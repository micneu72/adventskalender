#!/usr/bin/python3
# -*- coding: utf-8 -*-

""".

# Script Name:      adventskalender.py
# CreationDate:     04.12.2018
# Last Modified:    28.11.2019 13:54:43
# Copyright:        Michael N. (c)2018
# Purpose:
#
## https://www.pyimagesearch.com/2017/07/10/using-tesseract-ocr-python/
# pip3 install pytesseract
# apt install python3-pyocr
# apt install python3-opencv
# pip3 install opencv-python
# pip3 install pillow
# brew install tesseract
"""

#from PIL import Image
#from requests_html import HTMLSession
import requests
import time
import math
import re
import os.path

import pytesseract
import cv2
import os


ZEITDATUM = time.strftime("%d.%m.%Y %H:%M:%S")
KALENDERURL = "https://www.lc-ellerbekrellingen.de/weihnachtskalender-2018"
SEL = '#1984307661'


def timepost(start, stop):
    """laufzeit auswerten."""
    zeit = stop - start
    zeit = math.ceil(zeit)

    if zeit >= 3600:
        int_h = zeit / 3600
        int_h = int(int_h)
        zeit = zeit - (int_h * 3600)
    else:
        int_h = 0

    if zeit >= 60:
        int_m = zeit / 60
        int_m = int(int_m)
        zeit = zeit - (int_m * 60)
    else:
        int_m = 0

    if zeit <= 59:
        int_s = int(zeit)

    if int_h > 0:
        print("%2d Stunde(n), %2d Minute(n), %2d Sekunde(n)" % (int_h, int_m, int_s))
    elif int_m > 0:
        print("%2d Minute(n), %2d Sekunde(n)" % (int_m, int_s))
    else:
        print("%2d Sekunde(n)" % (int_s))


def get_html_code3(uri, sel):
    """Crawl page."""
    session = HTMLSession()
    page = session.get(uri)
    r = page.html.find('#1984307661')
    return r


def trenner(laenge, trennerzeichen):
    textlaenge = int(len(laenge))
    trennzeile = trennerzeichen * textlaenge
    return str(trennzeile)


def create_dir(dirname):
    os.makedirs(dirname, exist_ok=True)


def convert_imgage_to_grey(datei):
    image = cv2.imread(datei)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


htmlbody = """<!doctype html>
<html lang="de">
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">

    <title>Adventskalender OCR für emetriq GmbH</title>
  </head>
  <body>""" + "\n"
htmlfooter = "<h3 align=center>Letze Änderung: " + ZEITDATUM + "</h3>\n"
htmlfooter += "<h3 align=center>(c) 2019 Michael Neumann | emetriq GmbH | Likedeeler</h3>"
htmlfooter +=  """ <!-- Optional JavaScript -->
    <!-- jQuery first, then Popper.js, then Bootstrap JS -->
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>
  </body>
</html> """

create_dir("bilder")
create_dir("html")

# zeitmessung start
start = time.time()

if __name__ == '__main__':
    NAME = 1
    bilder = []
    htmlcode = get_html_code3(KALENDERURL, SEL)
    try:
        urls = htmlcode.find('img')
        for url in urls:
            match = re.search( 'tablet', url['src'])
            if match:
                if not url['src'] == "https://cdn.website-editor.net/c52db4ba56694d33b1086a5b364f6c3a/dms3rep/multi/tablet/Screenshot+2018-08-28+10.19.47-165c58c4.png":
                    #print(url['src'])
                    bilder.append(url['src'])

        htmlcontent = htmlbody
        htmlcontent += "<h3 align=center>Letze Änderung: " + ZEITDATUM + "</h3>\n"
        for bildurl in bilder:
            datei = "bilder/" + str(NAME) + ".png"
            print(bildurl)
            r = requests.get(bildurl, allow_redirects=True)
            with open(datei, 'wb') as f:
                f.write(r.content)
            convert_imgage_to_grey(datei)

            filename = "{}.png".format(os.getpid())
            cv2.imwrite(filename, gray)

            text = pytesseract.image_to_string(Image.open(filename))
            os.remove(filename)
            #print(text)
            text2 = re.findall("\d{4}", text)
            print(text2)
            htmlcontent += '<img src="' + bildurl + '">' + "\n" + "<br />"
            htmlcontent += "<h2>" + str(text2) + "</h2>" + "\n" +"<br />"
            NAME += 1
    except:
        htmlcontent = htmlbody
        htmlcontent += "<h3 align=center>Letze Änderung: " + ZEITDATUM + "</h3>\n"
        htmlcontent += "<h3 align=center>ist noch nicht gestartet</h3>\n"

    htmlcontent += htmlfooter
    with open("html/index.html", "w") as f:
        f.write(htmlcontent)
    # zeitmessung stop
    stop = time.time()

    # zeitmessung auswertung
    timepost(start, stop)
