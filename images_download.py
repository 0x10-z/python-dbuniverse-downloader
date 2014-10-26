#! /usr/bin/python
# -*- coding: utf8 -*-
import requests, time, lxml.html, os
from urlparse import urljoin
from PyPDF2 import PdfFileMerger, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from PIL import Image

def get_url_from_pne(path, fname, number, fext):
    return os.path.join(path, fname+str(number)+'.'+fext)

BLACK_LIST = []
EXTRA_IMAGES = []
ROOT_DIRECTORY = os.path.dirname(__file__)
# Las 3 variables de acontinuacion se deben modificar para cada usuario. Colocar la ruta de donde se va a descargar cada cosa
pdf_path = os.path.join(ROOT_DIRECTORY, 'pdf') # La ruta donde se van a guardar los PDF
img_temp = os.path.join(ROOT_DIRECTORY, 'images') # La ruta donde se guardaran las imagenes

parent_url = 'http://www.dragonball-multiverse.com/es/'

MAX_BOOKS = 949 #Aqui colocar siempre el numero del ultimo libro publicado + 1
""" download all images from html """
def download():
    i = 0
    aux = 0
    for i in range(MAX_BOOKS):
    	try:
            if not os.path.isfile(get_url_from_pne(img_temp, 'DBM_', i, 'jpg')) and not os.path.isfile(get_url_from_pne(img_temp, 'DBM_', i, 'png')):
                link = 'http://www.dragonball-multiverse.com/es/page-'+str(i)+'.html'
                source = requests.get(link).content
                html = lxml.html.fromstring(source)
                book_title = html.cssselect('div')[7].cssselect('img')[0].get('src')
                url=urljoin(parent_url,book_title)
                img_format = book_title[-3:] #cogemos la extension del fichero para que no importe si es ".png" o ".jpg"
                img_file = open(get_url_from_pne(img_temp, 'DBM_', i, img_format),'wb') #abrimos el fichero donde guardaremos la imagen
                #img_file.write(urllib.urlopen(url).read()) #empezamos la descarga
                img_file.write(requests.get(url).content)
                img_file.close() #cerramos el fichero
                time.sleep(0.5)
                print "Downloaded in: "+get_url_from_pne(img_temp, 'DBM_', i, img_format)
            else:
                print "Saltando libro numero %s\r" %i

        except Exception as e:
            print e
            print "No se ha podido descargar"
            BLACK_LIST.append(i)
            time.sleep(.5)


""" merge all pdfs in one """
def merge_pdf():
    merger = PdfFileMerger()
    num = 0
    for num in range(MAX_BOOKS):
        if num not in BLACK_LIST:
            merger.append(PdfFileReader(file(get_url_from_pne(pdf_path, 'DBM_', num, 'pdf'), 'rb')))
            print 'uniendo pagina %i...'%num
        else:
            print 'El numero %i esta en la BLACK LIST'%num
    merger.write(os.path.join(ROOT_DIRECTORY,'DragonBallMultiverse.pdf'))
    print 'Terminado de unir'


""" this method copy all images in a PDF"""
def img_to_pdf():
    aux_X = 0
    aux_Y = 0
    num = 0
    print 'Checkenado ancho de imagenes...'
    for num in range(MAX_BOOKS):
        if (os.path.isfile(get_url_from_pne(img_temp, 'DBM_', num, 'jpg'))): #Tratamos diferente la imagen si es .png o .jpg
            check_images_width(get_url_from_pne(img_temp, 'DBM_', num, 'jpg'))
        elif(os.path.isfile(get_url_from_pne(img_temp, 'DBM_', num, 'png'))):
            check_images_width(get_url_from_pne(img_temp, 'DBM_', num, 'png'))
    for num in range(MAX_BOOKS+len(EXTRA_IMAGES)):
        try:
            if num not in BLACK_LIST:
                c = canvas.Canvas(get_url_from_pne(pdf_path, 'DBM_', num, 'pdf'))
                if (os.path.isfile(get_url_from_pne(img_temp, 'DBM_', num, 'jpg'))): #Tratamos diferente la imagen si es .png o .jpg
                    if get_url_from_pne(img_temp, 'DBM_', num, 'jpg') in EXTRA_IMAGES:
                        for aux in range(1, 3): #captura las imagenes cortadas muy anchas
                            c.drawImage(get_url_from_pne(img_temp, 'DBM_'+str(num)+'_',aux,'jpg'), aux_X, aux_Y, 21*cm, 28*cm)
                            c.showPage()
                            c.save()
                    else:
                        c.drawImage(get_url_from_pne(img_temp, 'DBM_', num, 'jpg'), aux_X, aux_Y, 21*cm, 28*cm) # abrimos imagen y dibujamos en pdf. 21 y 28 son las medidas para las imagenes
                        c.showPage()
                        c.save()
                elif(os.path.isfile(get_url_from_pne(img_temp, 'DBM_', num, 'png'))):
                    if get_url_from_pne(img_temp, 'DBM_', num, 'png') in EXTRA_IMAGES:
                        for aux in range(1, 3):
                            c.drawImage(get_url_from_pne(img_temp, 'DBM_'+str(num)+'_',aux,'png'), aux_X, aux_Y, 21*cm, 28*cm)
                            c.showPage()
                            c.save()
                    else:
                        c.drawImage(get_url_from_pne(img_temp, 'DBM_', num, 'png'), aux_X, aux_Y, 21*cm, 28*cm) #lo mismo que arriba pero para .png
                        c.showPage()
                        c.save()

                print "libro numero "+str(num)
            else:
                print 'El numero %i esta en la BLACK LIST'%num
        except Exception as e:
            print e
            print "numero no encontrado"



def prepare_dirs(IMG_DIR, PDF_DIR):
    if not os.path.exists(IMG_DIR):
        os.makedirs(IMG_DIR)
    if not os.path.exists(PDF_DIR):
        os.makedirs(PDF_DIR)

def check_images_width(url = 'images/DBM_8.jpg'):
    img = Image.open(url)
    fname, fext = url.split("/")[-1].split(".")[0], url.split("/")[-1].split(".")[1]
    width, height = img.size[0], img.size[1]
    if width > 1000:
        img_2, img_1 = img.crop((width/2, 0, width, height)), img.crop((0, 0, width/2, height)) #left - top - right - bottom
        img_1.save(os.path.join(img_temp, fname+'_1.'+fext))
        img_2.save(os.path.join(img_temp, fname+'_2.'+fext))
        EXTRA_IMAGES.append(url)
    else:
        pass

def all():
    download()
    img_to_pdf()
    merge_pdf()
    print 'FINISH'

""" interactive user mode """
print "============================================="
print "---------Script realizado por BashRC---------"
print "--------Para mis amigos de forocarros--------"
print "---------------------------------------------"
print "=============================================\n"

str_modal = "Introduce un numero de una opcion a ejecutar\n" \
            "1 -Descargar MAX_BOOKS DragonBallMultiverse\n" \
            "2 -Convertir imagenes en PDFs\n" \
            "3 -Unir todos los PDF en un unico PDF\n" \
            "4 -Todo el proceso\n" \
            "Introduce 0 para salir\n"
options = {1 : download, 2 : img_to_pdf, 3 : merge_pdf, 4 : all}
try:
    prepare_dirs(img_temp, pdf_path)
    selection = input(str_modal)
    while selection is not 0:    
        options[selection]()
        if selection is not 1 and selection is not 2 and selection is not 3 and selection is not 4:
            print "No has introducido una opcion valida"
        selection = input(str_modal)

except ValueError:
    print "Oops! No has introducido un numero valido"

