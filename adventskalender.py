#! /usr/bin/env python3
# -*- coding: utf-8 -*-

""".

# Script Name:      adventskalender.py
# CreationDate:     04.12.2018
# Last Modified:    08.12.2019 01:17:32
# Copyright:        Michael N. (c)2018
# Purpose:
#
## https://www.pyimagesearch.com/2017/07/10/using-tesseract-ocr-python/
# pip3 install boto3
#
"""

from bs4 import BeautifulSoup
import requests
import socket
import sys
import time
import math
import re
import os.path
import os
import time
from PIL import Image
import pytesseract
import boto3

ZEITDATUM = time.strftime("%d.%m.%Y %H:%M:%S")
KALENDERURL = "https://www.lc-ellerbekrellingen.de/weihnachtskalender-2018"
SEL = '1984307661'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko)'}
TEST = False


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


def trenner(laenge, trennerzeichen):
    textlaenge = int(len(laenge))
    trennzeile = trennerzeichen * textlaenge
    return str(trennzeile)


def create_dir(dirname):
    os.makedirs(dirname, exist_ok=True)


def init_html_content():
    htmlcontent = htmlbody
    htmlcontent += "\t<h3 align=center>Letze Änderung: " + ZEITDATUM + "</h3>\n"
    return htmlcontent


def set_file_name(imguri):
    extension = re.findall(r'\.[a-z][a-z][a-z]$',imguri)
    return extension[0]

def read_text_from_image(imagelocalfile):
    LOS = []
    textract = boto3.client('textract')
    with open(imagelocalfile, "rb") as f:
        # Call Amazon Textract
        response = textract.detect_document_text(
        Document={
            'Bytes': f.read()
            }
        )
        for item in response["Blocks"]:
            if item["BlockType"] == "LINE":
                if re.match(r'^\d{4}$', item['Text']):
                    #print(item['Text'])
                    LOS.append(item['Text'])
    return LOS

def read_text_from_image_local(imagelocalfile):
    LOS = []
    item = (pytesseract.image_to_string(imagelocalfile))
    for m in re.finditer(r'(\d{4})', item):
        LOS.append(m.group(1))

    print(LOS)
    return LOS

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
  <body>
    <div class="d-flex flex-column flex-md-row align-items-center p-3 px-md-4 mb-3 bg-white border-bottom shadow-sm"></div>""" + "\n"
htmlfooter = '</div><footer class="pt-4 my-md-5 pt-md-5 border-top">'
htmlfooter += "\t<h5 align=center>Letze Änderung: " + ZEITDATUM + "</h5>\n"
htmlfooter += "\t<h5 align=center>(c) 2019 Michael Neumann | emetriq GmbH | IT-Likedeeler</h5>\n"
htmlfooter += "</footer>"
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
    htmlcode = get_html_code2(KALENDERURL, HEADERS)
    contentbereich = htmlcode.find('div', {'id': SEL})
    NAME = 1
    htmlsortierung = ""
    htmlsort = None
    #htmlcontent = init_html_content()
    imgs = contentbereich.find_all('img')
    #print(imgs)
    htmlcontent = ""
    for imguri in imgs:
        print(imguri['src'])
        fileextension = set_file_name(imguri['src'])
        imagelocalfile = "bilder/" + str(NAME) + fileextension
        print(imagelocalfile)
        r = requests.get(imguri['src'], allow_redirects=True)
        with open(imagelocalfile, 'wb') as f:
            f.write(r.content)

        LOSE = read_text_from_image(imagelocalfile)
        if re.findall('^\d{1}$', str(NAME)):
            Tag = "0" + str(NAME) + ".Dezember"
        else:
            Tag = str(NAME) + ".Dezember"
        if htmlsort is None:
            htmlsort = [[Tag, imguri['src'], LOSE, imagelocalfile]]
        else:
            htmlsort.append([Tag, imguri['src'], LOSE, imagelocalfile])

        #os.remove(imagelocalfile)
        
        NAME += 1

    htmlsort.reverse()
    for i in htmlsort:
        htmlcontent += "<h2>" + i[0] + "</h2>" + "\n<br />"
        htmlcontent += '<table class="table"><tr>' + "\n"
        htmlcontent += '<th scope="col"><img src="' + i[1] + '"></th>'
        htmlcontent += '<th scope="col">'
        for LOS in i[2]:
            htmlcontent += "<h6>" + LOS + "</h6>" + "\n<br />"
        htmlcontent += '</th></tr></table>'
    html = init_html_content()
    html += '<div class="container">'
    html += htmlcontent
    html += htmlfooter
    with open("html/index.html", "w") as f:
        f.write(html)

    # zeitmessung stop
    stop = time.time()

    # zeitmessung auswertung
    timepost(start, stop)

