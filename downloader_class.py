#! /usr/bin/python
# -*- coding: utf8 -*-
import requests
import time
import lxml.html
import os
from urlparse import urljoin
from PyPDF2 import PdfFileMerger, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from PIL import Image


class Downloader():
    BLACK_LIST = []
    EXTRA_IMAGES = []
    ROOT_DIRECTORY = os.path.dirname(__file__)
    # La ruta donde se van a guardar los PDF
    PDF_PATH = os.path.join(ROOT_DIRECTORY, 'pdf')
    # La ruta donde se guardaran las imagenes
    IMG_PATH = os.path.join(ROOT_DIRECTORY, 'images')
    PARENT_URL = 'http://www.dragonball-multiverse.com/es/'
    #Aqui colocar siempre el numero del ultimo libro publicado + 1
    MAX_BOOKS = 22

    def __init__(self, selection):
        options = {1: self.download, 2: self.img_to_pdf, 3: self.merge_pdf, 4: self.execute_all}
        try:
            self.prepare_dirs(self.IMG_PATH, self.PDF_PATH)
            options[selection]()
            if selection is not 1 and selection is not 2 and selection is not 3 and selection is not 4:
               print "No has introducido una opcion valida"

        except ValueError:
            print "Oops! No has introducido un numero valido"

    def get_url_from_pne(self, path, fname, number, fext):
        return os.path.join(path, fname+str(number)+'.'+fext)

    def download(self,):
        i = 0
        aux = 0
        for i in range(self.MAX_BOOKS):
            try:
                if not os.path.isfile(self.get_url_from_pne(self.IMG_PATH, 'DBM_', i, 'jpg')) \
                        and not os.path.isfile(self.get_url_from_pne(self.IMG_PATH, 'DBM_', i, 'png')):
                    link = 'http://www.dragonball-multiverse.com/es/page-'+str(i)+'.html'
                    source = requests.get(link).content
                    html = lxml.html.fromstring(source)
                    book_title = html.cssselect('div')[7].cssselect('img')[0].get('src')
                    print book_title
                    url=urljoin(self.PARENT_URL,book_title)
                    #cogemos la extension del fichero para que no importe si es ".png" o ".jpg"
                    img_format = book_title[-3:]
                    #abrimos el fichero donde guardaremos la imagen
                    img_file = open(self.get_url_from_pne(self.IMG_PATH, 'DBM_', i, img_format),'wb')
                    img_file.write(requests.get(url).content)
                    img_file.close() #cerramos el fichero
                    time.sleep(0.5)
                    print "Downloaded in: "+self.get_url_from_pne(self.IMG_PATH, 'DBM_', i, img_format)
                else:
                    print "Saltando libro numero %s\r" %i

            except Exception as e:
                print e
                print "No se ha podido descargar"
                self.BLACK_LIST.append(i)
                time.sleep(.5)

    """ merge all pdfs in one """
    def merge_pdf(self,):
        merger = PdfFileMerger()
        num = 0
        for num in range(self.MAX_BOOKS):
            if num not in self.BLACK_LIST:
                merger.append(PdfFileReader(file(self.get_url_from_pne(self.PDF_PATH, 'DBM_', num, 'pdf'), 'rb')))
                print 'uniendo pagina %i...' % num
            else:
                print 'El numero %i esta en la BLACK LIST' % num
        merger.write(os.path.join(self.ROOT_DIRECTORY, 'DragonBallMultiverse.pdf'))
        print 'Terminado de unir'

    """ this method copy all images in a PDF"""
    def img_to_pdf(self,):
        aux_X = 0
        aux_Y = 0
        num = 0
        print 'Checkenado ancho de imagenes...'
        for num in range(self.MAX_BOOKS):
            #Tratamos diferente la imagen si es .png o .jpg
            if os.path.isfile(self.get_url_from_pne(self.IMG_PATH, 'DBM_', num, 'jpg')):
                self.check_images_width(self.get_url_from_pne(self.IMG_PATH, 'DBM_', num, 'jpg'))
            elif os.path.isfile(self.get_url_from_pne(self.IMG_PATH, 'DBM_', num, 'png')):
                self.check_images_width(self.get_url_from_pne(self.IMG_PATH, 'DBM_', num, 'png'))
        for num in range(self.MAX_BOOKS+len(self.EXTRA_IMAGES)):
            try:
                if num not in self.BLACK_LIST:
                    c = canvas.Canvas(self.get_url_from_pne(self.PDF_PATH, 'DBM_', num, 'pdf'))
                    #Tratamos diferente la imagen si es .png o .jpg
                    if os.path.isfile(self.get_url_from_pne(self.IMG_PATH, 'DBM_', num, 'jpg')):
                        if self.get_url_from_pne(self.IMG_PATH, 'DBM_', num, 'jpg') in self.EXTRA_IMAGES:
                            #captura las imagenes cortadas muy anchas
                            for aux in range(1, 3):
                                c.drawImage(self.get_url_from_pne(self.IMG_PATH, 'DBM_'+str(num)+'_',aux,'jpg'),
                                            aux_X, aux_Y, 21*cm, 28*cm)
                                c.showPage()
                                c.save()
                        else:
                            # abrimos imagen y dibujamos en pdf. 21 y 28 son las medidas para las imagenes
                            c.drawImage(self.get_url_from_pne(self.IMG_PATH, 'DBM_', num, 'jpg'),
                                        aux_X, aux_Y, 21*cm, 28*cm)
                            c.showPage()
                            c.save()
                    elif os.path.isfile(self.get_url_from_pne(self.IMG_PATH, 'DBM_', num, 'png')):
                        if self.get_url_from_pne(self.IMG_PATH, 'DBM_', num, 'png') in self.EXTRA_IMAGES:
                            for aux in range(1, 3):
                                c.drawImage(self.get_url_from_pne(self.IMG_PATH, 'DBM_'+str(num)+'_', aux, 'png'),
                                            aux_X, aux_Y, 21*cm, 28*cm)
                                c.showPage()
                                c.save()
                        else:
                            #lo mismo que arriba pero para .png
                            c.drawImage(self.get_url_from_pne(self.IMG_PATH, 'DBM_', num, 'png'),
                                        aux_X, aux_Y, 21*cm, 28*cm)
                            c.showPage()
                            c.save()

                    print "libro numero "+str(num)
                else:
                    print 'El numero %i esta en la BLACK LIST' % num
            except Exception as e:
                print e
                print "numero no encontrado"

    def prepare_dirs(self, img_dir, pdf_dir):
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)

    def check_images_width(self, url):
        img = Image.open(url)
        fname, fext = url.split("/")[-1].split(".")[0], url.split("/")[-1].split(".")[1]
        width, height = img.size[0], img.size[1]
        if width > 1000:
            #left - top - right - bottom
            img_2, img_1 = img.crop((width/2, 0, width, height)), img.crop((0, 0, width/2, height))
            img_1.save(os.path.join(self.IMG_PATH, fname+'_1.'+fext))
            img_2.save(os.path.join(self.IMG_PATH, fname+'_2.'+fext))
            self.EXTRA_IMAGES.append(url)
        else:
            pass

    def execute_all(self,):
        self.download()
        self.img_to_pdf()
        self.merge_pdf()
        print 'FINISH'

a = Downloader(4)
