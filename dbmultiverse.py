
import time
import lxml.html
import os
from urllib.parse import urljoin
from PyPDF2 import PdfFileMerger, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from PIL import Image
import sys
import requests

def get_url_from_pne(path, fname, number, fext):
    return os.path.join(path, fname+str(number)+'.'+fext)

BLACK_LIST = []
EXTRA_IMAGES = []
ROOT_DIRECTORY = os.path.dirname(__file__)
# Next 3 vars have to be modified in order to change output folders
pdf_path = os.path.join(ROOT_DIRECTORY, 'pdf') # PDF folder
img_temp = os.path.join(ROOT_DIRECTORY, 'images') # Images folder

parent_url = 'http://www.dragonball-multiverse.com/es/'

""" download all images from html """
def download():
    i = 0
    aux = 0
    for i in range(int(MAX_BOOKS)):
        try:
            if not os.path.isfile(get_url_from_pne(img_temp, 'DBM_', i, 'jpg')) and not os.path.isfile(get_url_from_pne(img_temp, 'DBM_', i, 'png')):
                link = 'http://www.dragonball-multiverse.com/es/page-'+str(i)+'.html'
                source = requests.get(link).content
                html = lxml.html.fromstring(source)
                book_title = html.cssselect('div')[7].cssselect('img')[0].get('src')
                url=urljoin(parent_url,book_title)
                img_format = book_title[-3:] # file ext catched (.jpg or .png)
                img_file = open(get_url_from_pne(img_temp, 'DBM_', i, img_format),'wb') 
                img_file.write(requests.get(url).content)
                img_file.close()
                time.sleep(0.5)
                print("Downloaded in: "+get_url_from_pne(img_temp, 'DBM_', i, img_format))
            else:
                print("Skipping book number %s\r" %i)


        except Exception as e:
            print(e)
            print("It cannot be downloaded")
            BLACK_LIST.append(i)
            time.sleep(.5)


""" merge all pdfs in one """
def merge_pdf():
    merger = PdfFileMerger()
    num = 0
    for num in range(MAX_BOOKS):
        try:
            if num not in BLACK_LIST:
                merger.append(PdfFileReader(open(get_url_from_pne(pdf_path, 'DBM_', num, 'pdf'), 'rb')))
                print('Joining page number %i...'%num)
            else:
                print('The number %i is in BLACK LIST'%num)
        except Exception as e:
            print("PDF number %i is not exist"%num)
    merger.write(os.path.join(ROOT_DIRECTORY,'DragonBallMultiverse.pdf'))
    print('Join finished')


""" this method copy all images in a PDF"""
def img_to_pdf():
    aux_X = 0
    aux_Y = 0
    num = 0
    print('Checking images width...')
    for num in range(MAX_BOOKS):
        if (os.path.isfile(get_url_from_pne(img_temp, 'DBM_', num, 'jpg'))): # Different implementation if its jpg or png
            check_images_width(get_url_from_pne(img_temp, 'DBM_', num, 'jpg'))
        elif(os.path.isfile(get_url_from_pne(img_temp, 'DBM_', num, 'png'))):
            check_images_width(get_url_from_pne(img_temp, 'DBM_', num, 'png'))

    for num in range(MAX_BOOKS+len(EXTRA_IMAGES)):
        try:
            if num not in BLACK_LIST:
                c = canvas.Canvas(get_url_from_pne(pdf_path, 'DBM_', num, 'pdf'))
                if (os.path.isfile(get_url_from_pne(img_temp, 'DBM_', num, 'jpg'))): # Different implementation if its jpg or png
                    if get_url_from_pne(img_temp, 'DBM_', num, 'jpg') in EXTRA_IMAGES:
                        for aux in range(1, 3): # Catch images with more width than others
                            c.drawImage(get_url_from_pne(img_temp, 'DBM_'+str(num)+'_',aux,'jpg'), aux_X, aux_Y, 21*cm, 28*cm)
                            c.showPage()
                            c.save()
                    else:
                        c.drawImage(get_url_from_pne(img_temp, 'DBM_', num, 'jpg'), aux_X, aux_Y, 21*cm, 28*cm) # Draw in PDF. 21 and 28 are images sizes
                        c.showPage()
                        c.save()
                elif(os.path.isfile(get_url_from_pne(img_temp, 'DBM_', num, 'png'))):
                    if get_url_from_pne(img_temp, 'DBM_', num, 'png') in EXTRA_IMAGES:
                        for aux in range(1, 3):
                            c.drawImage(get_url_from_pne(img_temp, 'DBM_'+str(num)+'_',aux,'png'), aux_X, aux_Y, 21*cm, 28*cm)
                            c.showPage()
                            c.save()
                    else:
                        c.drawImage(get_url_from_pne(img_temp, 'DBM_', num, 'png'), aux_X, aux_Y, 21*cm, 28*cm) # The same as above but for png
                        c.showPage()
                        c.save()

                print("Book number "+str(num))
            else:
                print('Number %i is in BLACK LIST'%num)
        except Exception as e:
            print(e)
            print("Number not found")



def prepare_dirs(IMG_DIR, PDF_DIR):
    if not os.path.exists(IMG_DIR):
        os.makedirs(IMG_DIR)
    if not os.path.exists(PDF_DIR):
        os.makedirs(PDF_DIR)

def check_images_width(url = 'images/DBM_8.jpg'):
    img = Image.open(url)
    fname, fext = url.split("\\")[-1].split(".")[0], url.split("\\")[-1].split(".")[1]
    print("URL: %s"%url)
    print("%s - %s"%(fname, fext))
    width, height = img.size[0], img.size[1]
    if width > 1000:
        img_2, img_1 = img.crop((width//2, 0, width, height)), img.crop((0, 0, width//2, height)) #left - top - right - bottom
        print("2nd: a%s.%s"%(fname, fext))
        print(os.path.join(img_temp, fname+'_1.'+fext))
        filename = "%s_1.%s"%(fname, fext)
        img_1.save(os.path.join(img_temp, filename))
        filename = "%s_2.%s"%(fname, fext)
        img_2.save(os.path.join(img_temp, filename))
        EXTRA_IMAGES.append(url)
    else:
        print("NO EXTRA IMAGES")

def all():
    download()
    img_to_pdf()
    merge_pdf()
    print('FINISH')

""" interactive user mode """
print("=============================================")
print("---------Script realizado por BashRC---------")
print("--------Para mis amigos de forocarros--------")
print("---------------------------------------------")
print("=============================================\n")
MAX_BOOKS = 0
if __name__ == '__main__':
    MAX_BOOKS = int(sys.argv[1])
    try:
        all()
    except Exception as e:
        print(e)