import tkinter as tk
from tkinter import filedialog
from PIL import Image
import numpy as np

pixels = 0  
width = 0
height = 0
bitsPerPixel = 0
scaleFactor = 1
brightnessFactor = 1

# function to get the color table
def colorTable (colorTableBytes):
    colorTablePallete = []
    for i in range(0, len(colorTableBytes), 4):
        b = colorTableBytes[i]
        g = colorTableBytes[i + 1]
        r = colorTableBytes[i + 2]
        colorTablePallete.append((r,g,b))
    return colorTablePallete

def twentyFourBitExtraction(pixelData, width):
    allPixels = []
    bytes = 3

    #calculate how many bytes are actually in a row so you don't include padding 
    actualRowsize = bytes * width

    #go through each scanline and 
    for scanLine in pixelData:
        rowOfPixels = []

        #go through each set of 3 bytes and create a pixel and add it to the row array
        for i in range(0, actualRowsize, 3):
            b = scanLine[i]
            g = scanLine[i + 1]
            r = scanLine[i + 2]

            rowOfPixels.append((r,g,b))
        allPixels.append(rowOfPixels)
    return allPixels

# go through each line an use the byte as index to 
def eightBitExtraction(pixelData, width, pallete):

    pixels  = []
    for scanLine in pixelData:

        rowOfPixels  = []
        for i in range(width):
            colorIdx = scanLine[i]
            rowOfPixels.append(pallete[colorIdx])
        pixels.append(rowOfPixels)
    return pixels

# go through each scnaline and look at the bytes and add the first 4 bits and then the last 4 bits 
def fourBitExtraction(pixelData, width, pallete):
    pixels = []
    for scanLine in pixelData:

        pixelCounter = 0 
        rowOfPixels  = []

        for byte in scanLine:
            if pixelCounter >= width:
                break
            palleteIdx = (byte >> 4) & 0x0F
            rowOfPixels.append(pallete[palleteIdx])
            pixelCounter += 1
            if pixelCounter >= width:
                break
            palleteIdx = byte & 0x0F
            rowOfPixels.append(pallete[palleteIdx])
            pixelCounter += 1

        pixels.append(rowOfPixels)
    return pixels

def oneBitExtraction(pixelData, width, pallete):
    pixels = []
    for scanLine in pixelData:

        pixelCounter = 0 
        rowOfPixels  = []

        for byte in scanLine:
            bits = [(byte >> i) & 1 for i in range(7, -1, -1)]
            for palleteIdx in bits:
                if(pixelCounter >= width):
                    break
                rowOfPixels.append(pallete[palleteIdx])
                pixelCounter +=1
        pixels.append(rowOfPixels)
    return pixels

def parse(filePath):
    global pixels, width, height, bitsPerPixel

    # open the file in binary 
    with open(filePath, "rb") as bmpFile:
        # read the header bytes 
        headerBytes  = bmpFile.read(54)
        bmpFile.seek(54)

        # get header info 
        bmpFileSize = int.from_bytes(headerBytes[2:6], 'little')
        offset = int.from_bytes(headerBytes[10:14], 'little')
        width = int.from_bytes(headerBytes[18:22], 'little')
        height = int.from_bytes(headerBytes[22:26], 'little')
        bitsPerPixel = int.from_bytes(headerBytes[28:30], 'little')
        compresssion  = int.from_bytes(headerBytes[30:34], 'little')

        # color table for 1, 4, 8 
        if bitsPerPixel == 1 or bitsPerPixel == 4 or bitsPerPixel == 8:
            numColortableBytes = 2** bitsPerPixel
            colorTableBytes = bmpFile.read(numColortableBytes * 4)
            colorTablePallete = colorTable(colorTableBytes)
        
        # go to the actual pixels 
        bmpFile.seek(offset)

        # number of bytes per row using formula 
        rowSize = ((width * bitsPerPixel + 31) // 32) * 4 
        rawData = []

        # add the rowsData as index in array and reverse the order 
        for _ in range(height):
            rawData.append(bmpFile.read(rowSize))
        rawData.reverse()

        if(bitsPerPixel == 24):     
            pixels = twentyFourBitExtraction(rawData, width)
        
        if(bitsPerPixel == 8):     
            pixels = eightBitExtraction(rawData, width, colorTablePallete)

        if(bitsPerPixel == 4):     
            pixels = fourBitExtraction(rawData, width, colorTablePallete)
        
        if(bitsPerPixel == 1):     
            pixels = oneBitExtraction(rawData, width, colorTablePallete)

        return pixels, width, height, bitsPerPixel, bmpFileSize

# toggles for the different colors 

def redToggle():
    if red.get() == 1:
        red.set(0)
        redbutton.config(text="Red off")

    else:
        red.set(1)
        redbutton.config(text="Red on")
    displayBMPFile(pixels, width, height)

def greenToggle():
    if green.get() == 1:
        green.set(0)
        greenbutton.config(text="Green off")

    else:
        green.set(1)
        greenbutton.config(text="Green on")
    displayBMPFile(pixels, width, height)

def blueToggle():
    if blue.get() == 1:
        blue.set(0)
        bluebutton.config(text="Blue off")

    else:
        blue.set(1)
        bluebutton.config(text="Blue on")
    displayBMPFile(pixels, width, height)

def brightnessToggle(value):
    displayBMPFile(pixels, width, height)

def scaleToggle(value):
    displayBMPFile(pixels, width, height)
        
def rgbtoyuv(r, g, b):
    y = 0.299 * r + 0.587 * g + 0.114 * b
    u = -0.14713 * r - 0.28886 * g + 0.436 * b
    v = 0.615 * r - 0.51499 * g - 0.10001 * b
    return (y, u, v)

def yuvtorgb(y, u, v):
    r = y + 1.13983 * v
    g = y - 0.39465 * u - 0.58060 * v
    b = y + 2.03211 * u
    return (min(255, max(0, int(r))), min(255, max(0, int(g))), min(255, max(0, int(b))))


def getImage(pixels, width, height):
    # get the factors from the sliders 
    global brightnessFactor
    brightnessFactor = brightnessSlider.get() /100
    global scaleFactor 
    scaleFactor = scaleSlider.get() /100

# scaling 
    # scale for the new dimensions
    scaledWidth = int(width * scaleFactor)
    scaledHeight = int(height * scaleFactor)

    # empty image 
    bmpimg = tk.PhotoImage(width=scaledWidth, height=scaledHeight)

    # iterate of over the pixels according to the new dimensions 
    for y in range(scaledHeight):
        for x in range(scaledWidth):

            # get pixel values of closest pixel to new pixel 
            scaledX= int(x / scaleFactor)
            scaledY = int(y / scaleFactor)

            # alter the brightness of the image 
            r, g, b = pixels[scaledY][scaledX] 
            yval, u, v = rgbtoyuv(r, g, b)
            yval *= brightnessFactor
            r,g,b = yuvtorgb(yval, u, v)

            # convert to hex while checking if the color is on or off 
            hc = "#{:02x}{:02x}{:02x}".format(r* red.get(), g* green.get(), b * blue.get())
            bmpimg.put(hc, (x, y)) 
    return bmpimg


# modidifed getImage fucntion so the data can easily used by pillow library 
def getImage2(pixels, width, height):
    # get the factors from the sliders 
    global brightnessFactor
    brightnessFactor = brightnessSlider.get() /100
    global scaleFactor 
    scaleFactor = scaleSlider.get() /100

# scaling 
    # scale for the new dimensions
    scaledWidth = int(width * scaleFactor)
    scaledHeight = int(height * scaleFactor)

    # empty image 
    img = Image.new("RGB", (scaledWidth, scaledHeight))

    # iterate of over the pixels according to the new dimensions 
    for y in range(scaledHeight):
        row  = []
        for x in range(scaledWidth):

            # get pixel values of closest pixel to new pixel 
            scaledX= int(x / scaleFactor)
            scaledY = int(y / scaleFactor)

            # alter the brightness of the image 
            r, g, b = pixels[scaledY][scaledX] 
            yval, u, v = rgbtoyuv(r, g, b)
            yval *= brightnessFactor
            r,g,b = yuvtorgb(yval, u, v)
            img.putpixel((x, y), (r, g, b))
    return img


def saveImage():

    # Ask where to save the file
    file_path = filedialog.asksaveasfilename(
        title="Save Image As",
        defaultextension=".bmp",
        filetypes=[("Bitmap Images", "*.bmp")]
    )

    if not file_path:
        return  # Cancelled

    global bitsPerPixel

    # Generate the RGB image using your logic
    img_rgb = getImage2(pixels, width, height)  # should return RGB Pillow image

    # Convert image mode based on bits per pixel
    if bitsPerPixel == 8 or bitsPerPixel == 4 or bitsPerPixel == 1:
        img_to_save = img_rgb.convert("P")  # 8-bit grayscale
    elif bitsPerPixel == 24:
        img_to_save = img_rgb.convert("RGB")  # 24-bit color
    else:
        print("Unsupported bit depth:", bitsPerPixel)
        return

    # Save as BMP
    img_to_save.save(file_path, format="BMP")
    print(f"Image saved as {bitsPerPixel}-bit BMP at:", file_path)

def displayBMPFile(pixels, width, height):

    bmpimg = getImage(pixels, width, height)

    # update the image 
    image.config(image=bmpimg)
    # stop trash collection 
    image.image = bmpimg 


def displayMetaData(bmpFileSize, width, height,bitsPerPixel):

    metaData = (
        f"File Size: {bmpFileSize} bytes\n"
        f"Width: {width} px\n"
        f"Height: {height} px\n"
        f"Bits per Pixel: {bitsPerPixel}"
    )


    metadata.config(text=metaData)
    print()

def getNewBitDepth():
    global bitsPerPixel
    if(bitsPerPixel == 1 or bitsPerPixel == 4 or bitsPerPixel == 8):
        return 8
    elif(bitsPerPixel == 24):
        return 24
    else:
        print("Unsupported bit depth")
        return

def openBMPFile():

    while True:

        filePath=tk.filedialog.askopenfilename(title="Choose a File", filetypes=[("Bitmap Images", "*.bmp")])
    
        # if no file was selected return 
        if not filePath:
            return 

        # check for the signature 
        with open(filePath, "rb") as bmpFile:
            signature = bmpFile.read(2) 
        
        # unlock all the features and display the image and metadata and any other datas
        if(signature == b'BM'):
            #reset the scaling
            global bitsPerPixel
            brightnessSlider.set(100)
            scaleSlider.set(100)
            statusLabel.config(text="File Accepted", fg="green")
            filePathO.set(filePath)
            # parse the file
            pixels, width, height, bitsPerPixel, bmpFileSize = parse(filePath)
            displayBMPFile(pixels, width, height)
            displayMetaData(bmpFileSize, width, height,bitsPerPixel)
            currentBitDepth.set("Current Bit Depth: " + str(bitsPerPixel))
            saveBitDepth.set("Saving with Bit Depth: " + str(getNewBitDepth()))
            redbutton.config(state="normal")
            greenbutton.config(state="normal")
            bluebutton.config(state="normal")
            brightnessSlider.config(state = "normal")
            scaleSlider.config(state = "normal")
            return
        else:
            # tell the user the file is unable to be opnened 
            statusLabel.config(text="Error: Could not open file", fg="red")
            break


def setCurrentBitDepthLabel(bpp):
    currentBitDepth.set(f"Current Bit Depth: {bpp}-bit")

def setSaveBitDepthLabel():
    saveBitDepth.set(f"Saving As: {bitsPerPixel.get()}-bit BMP")

root = tk.Tk()
root.title("BMP File Display/Editor")
root.geometry("1000x600")  

# create grid  
root.columnconfigure(1, weight=1)  
root.rowconfigure(1, weight=1)     

# create frame for buttons 
control_frame = tk.Frame(root)
control_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

# frame for image 
image_frame = tk.Frame(root, bg="gray")
image_frame.grid(row=0, column=1, rowspan=8, sticky="nsew", padx=10, pady=10)

# allow image to adjust
root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)

red = tk.IntVar(value=1)
green = tk.IntVar(value=1)
blue = tk.IntVar(value=1)
filePathO = tk.StringVar()

# File Button
openFileButton = tk.Button(control_frame, text="Open File", command=openBMPFile)
openFileButton.grid(row=0, column=0, columnspan=2, pady=5, sticky="w")

# Status of file Label
statusLabel = tk.Label(control_frame, text="", font=("Arial", 14), bg="white", width=20)
statusLabel.grid(row=1, column=0, columnspan=2, pady=5, sticky="w")

# Metadata Label
metadata = tk.Label(control_frame, text="Metadata", font=("Arial", 15))
metadata.grid(row=7, column=0, columnspan=2, pady=10)

# Color Buttons
redbutton = tk.Button(control_frame, text="Red on", fg="red", width=10, command=redToggle, state="disabled")
redbutton.grid(row=2, column=0, padx=5, pady=2, sticky="w")

greenbutton = tk.Button(control_frame, text="Green on", fg="green", width=10, command=greenToggle, state="disabled")
greenbutton.grid(row=3, column=0, padx=5, pady=2, sticky="w")

bluebutton = tk.Button(control_frame, text="Blue on", fg="blue", width=10, command=blueToggle, state="disabled")
bluebutton.grid(row=4, column=0, padx=5, pady=2, sticky="w")

# Brightness Slider
brightnessSlider = tk.Scale(control_frame, from_=0, to=200, orient="horizontal", label="Brightness", command=brightnessToggle)
brightnessSlider.set(100)
brightnessSlider.config(state = "disabled")
brightnessSlider.grid(row=5, column=0, columnspan=2, pady=5, sticky="w")

# Scale Slider
scaleSlider = tk.Scale(control_frame, from_=1, to=200, orient="horizontal", label="Scale", command=scaleToggle)
scaleSlider.set(100)  # Default value is now 100
scaleSlider.config(state="disabled")  # Initially disabled
scaleSlider.grid(row=6, column=0, columnspan=2, pady=5, sticky="w")

# Image Label 
image = tk.Label(image_frame, bg="gray", width=40, height=20)
image.pack(expand=True, fill="both")  # Ensures the image frame grows but does NOT push buttons

#saveButton 
saveButton = tk.Button(control_frame, text="Save Image", width=15, command=saveImage)
saveButton.grid(row=8, column=0, columnspan=2, pady=10, sticky="w")

currentBitDepth = tk.StringVar(value="Current Bit Depth: N/A")
saveBitDepth = tk.StringVar(value="Saving with Bit Depth: N/A")

# Current Bit Depth Display
currentBitDepthLabel = tk.Label(control_frame, textvariable=currentBitDepth, font=("Arial", 14), fg="gray")
currentBitDepthLabel.grid(row=9, column=0, columnspan=2, sticky="w")

# Save Bit Depth Display
saveBitDepthLabel = tk.Label(control_frame, textvariable=saveBitDepth, font=("Arial", 14), fg="gray")
saveBitDepthLabel.grid(row=10, column=0, columnspan=2, sticky="w")

# Run Tkinter event loop
root.mainloop()
