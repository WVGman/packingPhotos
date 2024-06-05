# packingPictures
Have you ever had a bunch of pictures/photos that you want to print out, but you want to minimize the wasted space on the page? This Python script (sub-optimally) packs pictures (PNGs, JPGs, and JPEGs) into letter-sized pages with 0.25 inch margins for easy cutting!

*Note: This code was written with assistance from ChatGPT's GPT-4o model.* 

# Usage
To run this code, you must have the PIL and img2pdf (if you want a PDF) libraries available. In the directory of the file, put all of your pictures into a folder called 'input'. Make sure all of your photos are formatted as PDFs, JPGs, or JPEGs. 

## Non-obvious Features
- Photos will be a maximum of 3.5 inches across to allow for at least 6 images per page.
- Photos will rotate for better fit if necessary.
- Code will make individual PNGs in an 'output' folder, as well as create an 'output.pdf'.

## Example
![Packed Page Example](https://i.imgur.com/8bsdQcW.jpeg)
