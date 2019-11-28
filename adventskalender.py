#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Script Name:      adventskalender.py
# CreationDate:     04.12.2018
# Last Modified:    25.11.2019 11:06:35
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
#
from PIL import Image
import sys
import time
import math
import socket
from bs4 import BeautifulSoup
import re
import os.path
import time
import requests
import configparser
import argparse
import pytesseract
import cv2
import os
import urllib.request
import urllib

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

    print("%2d Stunde(n), %2d Minute(n), %2d Sekunde(n)" % (int_h, int_m, int_s))

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    filename = args.filename
    return filename    

def get_html_code2(uri):
    page = requests.get(uri)
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


def getURLs(uri):
    bereich = ""
    htmlcode = get_html_code2(uri)
    urls = sort_data(htmlcode, urlRegEx)
    return urls

ZEITDATUM = time.strftime("%d.%m.%Y %H:%M:%S")

kalenderurl = "https://www.lc-ellerbekrellingen.de/weihnachtskalender-2018"

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

writehtml = open("html/index.html", "w")

# zeitmessung start
start = time.time()

if __name__ == '__main__':
    NAME = 1
    bilder = []
    htmlcode = get_html_code2(kalenderurl)
    try:
        imgs = htmlcode.img['src']
        urls = htmlcode.find_all('img')
        tage = htmlcode.findAll("div", {"class": "dmNewParagraph"})
        for url in urls:
            match = re.search( 'tablet', url['src'])
            if match:
                if not url['src'] == "https://cdn.website-editor.net/c52db4ba56694d33b1086a5b364f6c3a/dms3rep/multi/tablet/Screenshot+2018-08-28+10.19.47-165c58c4.png":
                    #print(url['src'])
                    bilder.append(url['src'])
                
        htmlcontent = htmlbody
        htmlcontent += "<h3 align=center>Letze Änderung: " + ZEITDATUM + "</h3>\n"
        for web in bilder:
            datei = "bilder/" + str(NAME) + ".png"
            url = web
            print(url)
            r = requests.get(url, allow_redirects=True)
            open(datei, 'wb').write(r.content)
            image = cv2.imread(datei)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            filename = "{}.png".format(os.getpid())
            cv2.imwrite(filename, gray)

            text = pytesseract.image_to_string(Image.open(filename))
            os.remove(filename)
            #print(text)
            text2 = re.findall("\d{4}", text)
            print(text2)
            htmlcontent += '<img src="' + web + '">' + "\n" + "<br />"
            htmlcontent += "<h2>" + str(text2) + "</h2>" + "\n" +"<br />"
            NAME += 1
    except:
        htmlcontent = htmlbody
        htmlcontent += "<h3 align=center>Letze Änderung: " + ZEITDATUM + "</h3>\n"
        htmlcontent += "<h3 align=center>ist noch nicht gestartet</h3>\n"

    htmlcontent += htmlfooter
    writehtml.write(htmlcontent)
    writehtml.close()
    # zeitmessung stop
    stop = time.time()

    # zeitmessung auswertung
    timepost(start, stop)
