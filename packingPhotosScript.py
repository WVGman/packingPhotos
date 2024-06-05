# Code written with assistance from ChatGPT's GPT-4o
# This code takes a bunch of images in a folder as an input, then outputs a series of png images and a PDF.
# The code originally uses letter pages (8.5 x 11) with a 0.25 inch margin between the pages,
# but you can configure to change that.

import os
from PIL import Image
import img2pdf


class Photo:
    def __init__(self, width, height, filename):
        self.width = width
        self.height = height
        self.filename = filename
        self.rotated = False

    def rotate(self):
        self.width, self.height = self.height, self.width
        self.rotated = not self.rotated

    def resize(self, max_side_length):
        if self.width > max_side_length or self.height > max_side_length:
            if self.width > self.height:
                scale_factor = max_side_length / self.width
            else:
                scale_factor = max_side_length / self.height
            self.width *= scale_factor
            self.height *= scale_factor


class Page:
    def __init__(self, width, height, margin):
        self.width = width
        self.height = height
        self.margin = margin
        self.remaining_areas = [(margin, margin, width - 2 * margin, height - 2 * margin)]  # List of available spaces
        self.photos = []

    def can_place_photo(self, photo):
        for i, (x, y, w, h) in enumerate(self.remaining_areas):
            if w >= photo.width and h >= photo.height:
                return i, x, y
        return None

    def place_photo(self, photo):
        result = self.can_place_photo(photo)
        if result:
            i, x, y = result
            self.photos.append((photo, x, y))

            # Update the remaining spaces
            _, _, w, h = self.remaining_areas.pop(i)
            new_remaining_areas = []

            # Right remaining space
            if w - photo.width - self.margin > 0:
                new_remaining_areas.append(
                    (x + photo.width + self.margin, y, w - photo.width - self.margin, photo.height))

            # Bottom remaining space
            if h - photo.height - self.margin > 0:
                new_remaining_areas.append((x, y + photo.height + self.margin, w, h - photo.height - self.margin))

            self.remaining_areas.extend(new_remaining_areas)

            # Sort remaining areas by size (largest first)
            self.remaining_areas = sorted(self.remaining_areas, key=lambda area: area[2] * area[3], reverse=True)

            return True
        return False


def best_fit_algorithm(photos, page_width, page_height, margin):
    pages = [Page(page_width, page_height, margin)]

    for photo in photos:
        placed = False
        for page in pages:
            if page.place_photo(photo):
                placed = True
                break
        if not placed:
            # Try rotating the photo and place again
            photo.rotate()
            for page in pages:
                if page.place_photo(photo):
                    placed = True
                    break
            if not placed:
                # If not placed even after rotation, add a new page
                photo.rotate()  # Rotate back to original orientation before adding to new page
                new_page = Page(page_width, page_height, margin)
                new_page.place_photo(photo)
                pages.append(new_page)

    return pages


def create_png(pages, page_width, page_height, output_folder):
    dpi = 300  # Dots per inch for the output image
    page_width_px = int(page_width * dpi)
    page_height_px = int(page_height * dpi)

    for page_index, page in enumerate(pages):
        image = Image.new('RGB', (page_width_px, page_height_px), 'white')

        for photo, x, y in page.photos:
            photo_width_px = int(photo.width * dpi)
            photo_height_px = int(photo.height * dpi)
            x_px = int(x * dpi)
            y_px = int(y * dpi)

            # Load the photo image
            photo_image = Image.open(photo.filename)
            if photo.rotated:
                photo_image = photo_image.rotate(90, expand=True)

            photo_image = photo_image.resize((photo_width_px, photo_height_px))

            # Paste the photo onto the page image
            image.paste(photo_image, (x_px, y_px))

        output_file = os.path.join(output_folder, f"page_{page_index + 1}.png")
        image.save(output_file, 'PNG')


def load_photos_from_folder(folder_path, max_side_length=3.5):
    photos = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('png', 'jpg', 'jpeg')):
            filepath = os.path.join(folder_path, filename)
            with Image.open(filepath) as img:
                dpi = img.info.get('dpi', (300, 300))  # Default to 300 DPI if not specified
                width, height = img.size
                width_inch = width / dpi[0]
                height_inch = height / dpi[1]
                photo = Photo(width_inch, height_inch, filepath)
                photo.resize(max_side_length)
                photos.append(photo)
    return photos


# Parameters
photo_folder = "input"
page_width = 8.5
page_height = 11
margin = 0.25
output_folder = "output"

# Load photos
photos = load_photos_from_folder(photo_folder)

# Apply best-fit algorithm
pages = best_fit_algorithm(photos, page_width, page_height, margin)

# Create PNG files
os.makedirs(output_folder, exist_ok=True)
create_png(pages, page_width, page_height, output_folder)

#################################################
# convert PNGs to PDF
output_pdf = "output.pdf"

# List all PNG files in the output folder
png_files = [file for file in os.listdir(output_folder) if file.endswith('.png')]

# Sort the PNG files based on their names (assuming the names are in the format "page_1.png", "page_2.png", etc.)
png_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))

# Create a list to store the paths of all PNG files
png_paths = [os.path.join(output_folder, file) for file in png_files]

# Convert PNG files to a single PDF
with open(output_pdf, "wb") as pdf_file:
    pdf_file.write(img2pdf.convert(png_paths))
