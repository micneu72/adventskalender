#! /usr/bin/env python3
# -*- coding: utf-8 -*-

""".

# Script Name:      adventskalender.py
# CreationDate:     04.12.2018
# Last Modified:    30.11.2019 12:08:34
# Copyright:        Michael N. (c)2018
# Purpose:
#
## https://www.pyimagesearch.com/2017/07/10/using-tesseract-ocr-python/
# pip3 install pytesseract
# apt install python3-pyocr
# apt install python3-opencv
# pip3 install opencv-python
# pip3 install pillow
#
"""

from PIL import Image
from bs4 import BeautifulSoup
import requests
import socket
#import pytesseract
import cv2
import sys
import time
import math
import re
import os.path
import os
import time


ZEITDATUM = time.strftime("%d.%m.%Y %H:%M:%S")
KALENDERURL = "https://www.lc-ellerbekrellingen.de/weihnachtskalender-2018"
#KALENDERURL = "https://heise.de"
SEL = '1984307661'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko)'}
TEST = True


def timepost(start, stop):
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


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    filename = args.filename
    return filename    


def get_html_code2(uri, HEADERS):
    page = requests.get(uri, headers=HEADERS)
    bsObj = BeautifulSoup(page.content, 'html.parser')
    return bsObj


def get_website_title(bsObj):
    return bsObj.title.string


def get_url_list(bsObj):
    daten = [[]]
    for link in bsObj.find_all('a'):
        href = link.get('href')
        urltext = link.get_text('href')
        webtitle = get_website_title(bsObj)
        daten += [[webtitle, href, urltext]]
    return daten


def trenner(laenge, trennerzeichen):
    textlaenge = int(len(laenge))
    trennzeile = trennerzeichen * textlaenge
    return str(trennzeile)


def create_dir(dirname):
    os.makedirs(dirname, exist_ok=True)


def convert_image_to_gray(datei):
    print("Bilddatei: ", datei)
    try:
        img = Image.open(datei).convert('L')
    except:
        img = Image.open(datei).convert('LA')
    img.save(datei)

def create_image_list():
    bilder = []
    urls = htmlcode.find('img')
    for url in urls:
        match = re.search('tablet', url['src'])
        if match:
            if not url['src'] == "https://cdn.website-editor.net/c52db4ba56694d33b1086a5b364f6c3a/dms3rep/multi/tablet/Screenshot+2018-08-28+10.19.47-165c58c4.png":
                #print(url['src'])
                bilder.append(url['src'])
    return bilder


def init_html_content():
    htmlcontent = htmlbody
    htmlcontent += "\t<h3 align=center>Letze Änderung: " + ZEITDATUM + "</h3>\n"
    return htmlcontent


def set_file_name(imguri):
    extension = re.findall(r'\.[a-z][a-z][a-z]$',imguri)
    return extension[0]


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
htmlfooter = "\t<h3 align=center>Letze Änderung: " + ZEITDATUM + "</h3>\n"
htmlfooter += "\t<h3 align=center>(c) 2019 Michael Neumann | emetriq GmbH | Likedeeler</h3>"
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
    htmlcode = get_html_code2(KALENDERURL, HEADERS)
    contentbereich = htmlcode.findAll("div", {"id": SEL})
    if TEST:
        htmlcontent = init_html_content()
        imgs = htmlcode.findAll("img")
        #print(imgs)
        for imguri in imgs:
            print(imguri['src'])
            fileextension = set_file_name(imguri['src'])
            imagelocalfile = "bilder/" + str(NAME) + fileextension
            r = requests.get(imguri['src'], allow_redirects=True)
            with open(imagelocalfile, 'wb') as f:
                f.write(r.content)
            convert_image_to_gray(imagelocalfile)

            #text = pytesseract.image_to_string(Image.open(filename))
            #os.remove(filename)
            #print(text)
            #text2 = re.findall("\d{4}", text)
            #print(text2)
            #htmlcontent += '<img src="' + imguri + '">' + "\n" + "<br />"
            #htmlcontent += "<h2>" + str(text2) + "</h2>" + "\n" +"<br />"
            NAME += 1
    try:
        htmlcontent = init_html_content()
        imgs = contentbereich.findAll("img")
        print(imgs)
        for imguri in imgs:
            datei = "bilder/" + str(NAME) + ".png"
            print(imguri)
            r = requests.get(imguri, allow_redirects=True)
            with open(datei, 'wb') as f:
                f.write(r.content)
            convert_image_to_gray(datei) 

            text = pytesseract.image_to_string(Image.open(filename))
            os.remove(filename)
            #print(text)
            text2 = re.findall("\d{4}", text)
            print(text2)
            htmlcontent += '<img src="' + imguri + '">' + "\n" + "<br />"
            htmlcontent += "<h2>" + str(text2) + "</h2>" + "\n" +"<br />"
            NAME += 1

    except:
        print("keine bilder im bereich")
        htmlcontent = init_html_content()
        htmlcontent += "\t<h3 align=center>ist noch nicht gestartet</h3>\n"

    htmlcontent += htmlfooter
    with open("html/index.html", "w") as f:
        f.write(htmlcontent)

    # zeitmessung stop
    stop = time.time()

    # zeitmessung auswertung
    timepost(start, stop)
