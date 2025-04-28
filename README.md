BMP File Viewer and Editor
This is a simple Tkinter GUI tool written in Python that allows you to:

Open and display BMP files (1-bit, 4-bit, 8-bit, and 24-bit BMPs)
(using parser coded by hand)

Toggle color channels (Red, Green, Blue) on and off
(adjusted by directly changing pixel values)

Adjust image brightness
(adjusted by directly changing pixel values)

Scale (resize) the image
(adjusted direcly by estimating nearest value to orignal with scale porportions)

Save the modified image back as a BMP file
(using pillow library)

Features
✅ Open BMP Files: Supports 1-bit, 4-bit, 8-bit, and 24-bit BMP formats.

✅ Color Channel Control: Turn Red, Green, and Blue channels on or off individually.

✅ Brightness Adjustment: Increase or decrease the image brightness dynamically.

✅ Image Scaling: Zoom in or out by adjusting the scale percentage.

✅ Save Edited Image: Save the edited version as a BMP file while preserving compatible bit depths.

Requirements
Python 3.8+

Libraries:

tkinter (usually included with Python)

Pillow (pip install Pillow)

