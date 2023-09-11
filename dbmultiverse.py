import time
import lxml.html
import os
from urllib.parse import urljoin, urlparse, parse_qs
from pypdf import PdfMerger, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from PIL import Image
import sys
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import re

# LIMIT number of pixels can be processed with PILLOW
Image.MAX_IMAGE_PIXELS = 900000000
ROOT_DIRECTORY = os.path.dirname(__file__)
PDF_PATH = os.path.join(ROOT_DIRECTORY, 'pdf')
IMG_TEMP = os.path.join(ROOT_DIRECTORY, 'images')
PARENT_URL = 'http://www.dragonball-multiverse.com/es/'
DOUBLE_WIDTH = 1000
BLACK_LIST = []


def prepare_dirs(collection="dbmultiverse"):
    """Prepare directories for images and PDFs"""
    # Use collection name as subdirectory
    pdf_collection_path = os.path.join(PDF_PATH, collection)
    img_collection_path = os.path.join(IMG_TEMP, collection)
    
    for path in [pdf_collection_path, img_collection_path]:
        if not os.path.exists(path):
            os.makedirs(path)

def get_full_path(fname, number, extension, folder=IMG_TEMP, collection="dbmultiverse"):
    """Generate full path for a given file"""
    return os.path.join(folder, collection, f"{fname}{number}.{extension}")


def get_link(number, collection="dbmultiverse"):
    """Generate the appropriate link based on the page number."""

    if collection == "dbmultiverse":
        return f'https://www.dragonball-multiverse.com/es/page-{number}.html'
    elif collection == "namekseijin":
        return f'https://www.dragonball-multiverse.com/es/namekseijin-{number}.html'
    elif collection == "dbm-colors":
        return f'https://www.dragonball-multiverse.com/es/dbm-colors-{number}.html'
    elif collection == "strip":
        return f'https://www.dragonball-multiverse.com/es/strip-{number}.html'
    elif collection == "chibi-son-bra":
        return f'https://www.dragonball-multiverse.com/es/chibi-son-bra-{number}.html'

def get_img_url_from_element(element, collection):
    """Get the image URL based on the collection type and element."""
    
    # Define the extraction methods for each collection
    extraction_methods = {
        "dbmultiverse": {"attribute": "src", "regex": None},
        "strip": {"attribute": "src", "regex": None},
        "namekseijin": {"attribute": "style", "regex": r'background-image:url\((.*?)\)'},
        "dbm-colors": {"attribute": "style", "regex": r'background-image:url\((.*?)\)'},
        "chibi-son-bra": {"attribute": "style", "regex": r'background-image:url\((.*?)\)'}
    }

    # If the collection is unknown, return None
    if collection not in extraction_methods:
        return None

    # Extract the method for the given collection
    method = extraction_methods[collection]

    # If the attribute exists in the element
    if method["attribute"] in element.attrib:
        # If we need to extract using a regex
        if method["regex"]:
            match = re.search(method["regex"], element.attrib[method["attribute"]])
            if match:
                return match.group(1)
        # If we can directly return the attribute value
        else:
            return element.attrib[method["attribute"]]

    return None


def download_image(number, collection="dbmultiverse"):
    """Download a single image given its number"""
    jpg_path = get_full_path('DBM_', number, 'jpg', collection=collection)
    png_path = get_full_path('DBM_', number, 'png', collection=collection)
    
    if not os.path.isfile(jpg_path) and not os.path.isfile(png_path):
        link = get_link(number, collection)
        try:
            source = requests.get(link).content
            html = lxml.html.fromstring(source)
            element =  html.xpath("//*[@id='balloonsimg']")[0]
            img_url = get_img_url_from_element(element, collection)

            if img_url:
                full_url = urljoin(PARENT_URL, img_url)
                img_format = parse_qs(urlparse(full_url).query).get('ext', [None])[0]
                with open(get_full_path('DBM_', number, img_format, collection=collection), 'wb') as img_file:
                    img_file.write(requests.get(full_url).content)
                    
        except Exception as e:
            print(f"Error downloading page {number}: {e}")
            BLACK_LIST.append(number)
        time.sleep(0.1)

def download_images(max_books, collection="dbmultiverse"):
    """Download images from the web using a thread pool"""
    with ThreadPoolExecutor() as executor:
        list(tqdm(executor.map(lambda number: download_image(number, collection), range(int(max_books))), total=int(max_books), desc="Downloading"))
def convert_img_to_pdf(max_books, collection="dbmultiverse"):
    """Convert images to PDF using ThreadPool."""
    
    # Create a list of tasks (here, the task is a page number)
    tasks = [num for num in range(max_books) if num not in BLACK_LIST]
    
    # Use ThreadPoolExecutor to process images in parallel
    with ThreadPoolExecutor() as executor:
        list(tqdm(executor.map(lambda num: process_image(num, collection), tasks), total=len(tasks), desc="Converting to PDF"))

def process_image(num, collection="dbmultiverse"):
    """Process individual image and convert to PDF."""
    
    formats = ['jpg', 'png']
    for fmt in formats:
        img_path = get_full_path('DBM_', num, fmt, collection=collection)
        if os.path.isfile(img_path):
            img = Image.open(img_path)
            width, height = img.size
            if width > height and width > DOUBLE_WIDTH:
                # 2 pages images
                page_width, page_height = 42*cm, 28*cm
            elif width > height and width < DOUBLE_WIDTH:
                # strip first images are small
                page_width, page_height = width, height
            else:
                # MAYBE THIS CAN BE REFACTORED
                page_width, page_height = width, height
            
            c = canvas.Canvas(get_full_path('DBM_', num, 'pdf', folder=PDF_PATH, collection=collection), pagesize=(page_width, page_height))
            c.drawImage(img_path, 0, 0, page_width, page_height)
            c.showPage()
            c.save()


def check_images_width(img_path, collection):
    """Resize image if its width exceeds the threshold"""
    img = Image.open(img_path)
    fname, fext = os.path.basename(img_path).split('.')
    width, height = img.size

    if width > DOUBLE_WIDTH:
        new_width = width * 2
        new_height = int(height * (new_width / width)) 

        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        resized_img.save(get_full_path(fname, "", fext, collection=collection))



def merge_pdfs(max_books, collection):
    """Merge all individual PDFs into one"""
    merger = PdfMerger()

    for num in tqdm(range(max_books), desc="Merging PDFs"):
        pdf_path = get_full_path('DBM_', num, 'pdf', folder=PDF_PATH, collection=collection)
        if os.path.exists(pdf_path) and num not in BLACK_LIST:
            merger.append(PdfReader(open(pdf_path, 'rb')))
            #print(f'Joining page number {num}')
        else:
            pass
            #print(f'PDF number {num} does not exist or is in BLACK LIST')
    
    merger.write(os.path.join(ROOT_DIRECTORY, f'DragonBallMultiverse-{collection}.pdf'))
    print('Join finished')

def get_latest_chapter(collection):
    """Return the latest chapter number for a given collection."""
    base_url = "https://www.dragonball-multiverse.com/es/chapters.html"
    parameters = {"dbmultiverse": "page",
                "strip": "strip",
                "namekseijin": "namekseijin",
                "chibi-son-bra": "chibi-son-bra",
                "dbm-colors": "dbm-colors"}
    params = {'comic': parameters[collection]}
    response = requests.get(base_url, params=params)
    response.raise_for_status()  # Raise an exception for HTTP errors
    
    # Parse the HTML content
    tree = lxml.html.fromstring(response.content)
    
    # XPath to find all anchor elements containing chapter numbers
    chapter_links = tree.xpath('//a[text() and @href]')
    
    # Extract chapter numbers from the anchor text and find the maximum
    chapter_numbers = [int(link.text_content().strip()) for link in chapter_links if link.text_content().strip().isdigit()]
    
    return max(chapter_numbers, default=None)


def main():
    """
    DB Multiverse: dbmultiverse
    Namekseijin Densetsu: namekseijin
    DBMultiverse Colors: dbm-colors
    Minicomic: strip
    Chibi Son Bra did her best!: chibi-son-bra
    """
    valid_collections = ["dbmultiverse", "namekseijin", "dbm-colors", "strip", "chibi-son-bra"]
    collection = sys.argv[1]  # Read the collection from the command line arguments

    # Check for valid collection values to prevent potential security risks
    if collection not in valid_collections:
        print(f"Invalid collection: {collection}. Please use one of the following: {', '.join(valid_collections)}")
        return
    
    max_books = get_latest_chapter(collection)
    print(f"Downloading {max_books} chapters... for {collection}")

    prepare_dirs(collection=collection)
    download_images(max_books, collection=collection)
    
    for num in range(max_books):
        for fmt in ['jpg', 'png']:
            img_path = get_full_path('DBM_', num, fmt, collection=collection)
            if os.path.isfile(img_path):
                check_images_width(img_path)

    convert_img_to_pdf(max_books, collection=collection)
    merge_pdfs(max_books, collection)
    print('FINISH')


if __name__ == '__main__':
    main()