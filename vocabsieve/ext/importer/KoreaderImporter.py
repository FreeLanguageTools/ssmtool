from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from io import BytesIO
import os
import re
import glob
import json
from pathlib import Path
from difflib import SequenceMatcher
from sentence_splitter import split_text_into_sentences
from vocabsieve.tools import addNotes
from vocabsieve.dictionary import getAudio
from datetime import datetime
from itertools import compress
from slpp import slpp
from lxml import etree
from ebooklib import epub, ITEM_DOCUMENT

from .GenericImporter import GenericImporter
from .utils import *


def fb2_xpathconvert(s):
    s = "/".join(s.split("/")[2:-1])
    s = ("/" + s).replace("/", "/f:")
    return "." + s

def epub_xpathconvert(s):
    index = int(re.findall('DocFragment\[(\d+)\]', s)[0])
    s = "/body" + s.split("body")[-1]
    s = "/".join(s.split("/")[:-1])
    s = s.replace("/", "/f:")
    return (index, "." + s)

def removesuffix(self: str, suffix: str, /) -> str:
    # suffix='' should not call self[:-0].
    if suffix and self.endswith(suffix):
        return self[:-len(suffix)]
    else:
        return self[:]

def koreader_parse_fb2(file, lang):
    result = []
    notepath = os.path.join(
        os.path.dirname(file), removesuffix(os.path.basename(file), "fb2") + "sdr", "metadata.fb2.lua"
    )
    with open(notepath) as f:
        notes = slpp.decode(" ".join("\n".join(f.readlines()[1:]).split(" ")[1:]))['bookmarks'].items()
    print(notepath)
    root = etree.parse(file).getroot()
    ns = {'f': "http://www.gribuser.ru/xml/fictionbook/2.0"}
    for _, item in notes:
        try:
            xpath = fb2_xpathconvert(item['page'])
            word_start = int(item['pos0'].split(".")[-1])
            word_end = int(item['pos1'].split(".")[-1])
            if root.xpath(xpath, namespaces=ns):
                ctx = root.xpath(xpath, namespaces=ns)[0].text
                for sentence in split_text_into_sentences(ctx, language=lang):
                    if item['notes'] in sentence:
                        if ctx.find(sentence) < word_start \
                            and ctx.find(sentence) + len(sentence) > word_end: 
                            result.append((item['notes'], sentence, item['datetime'], removesuffix(os.path.basename(file), ".fb2")))
        except KeyError:
            continue
    return result



def koreader_parse_epub(file, lang):
    result = []
    notepath = os.path.join(
        os.path.dirname(file), removesuffix(os.path.basename(file), "epub") + "sdr", "metadata.epub.lua"
    )
    with open(notepath) as f:
        notes = slpp.decode(" ".join("\n".join(f.readlines()[1:]).split(" ")[1:]))['bookmarks'].items()
    docs = []
    for doc in epub.read_epub(file).get_items_of_type(ITEM_DOCUMENT):
        docs.append(
            etree.parse(BytesIO(doc.get_content())).getroot()
        )
    ns = {'f': 'http://www.w3.org/1999/xhtml'}
    for _, item in notes:
        try:
            index, xpath = epub_xpathconvert(item['page'])
            word_start = int(item['pos0'].split(".")[-1])
            word_end = int(item['pos1'].split(".")[-1])
            if docs[index].xpath(xpath, namespaces=ns):
                ctx = docs[index].xpath(xpath, namespaces=ns)[0].text
                for sentence in split_text_into_sentences(ctx, language=lang):
                    if item['notes'] in sentence:
                        if ctx.find(sentence) < word_start \
                            and ctx.find(sentence) + len(sentence) > word_end: 
                            result.append((item['notes'], sentence, item['datetime'], removesuffix(os.path.basename(file), ".epub")))
                            break
        except KeyError:
            continue
    return result

def koreader_scandir(path):
    filelist = []
    epubs = glob.glob(os.path.join(path, "**/*.epub"), recursive=True)
    for filename in epubs:
        if os.path.exists(os.path.join(os.path.dirname(filename), 
                            removesuffix(filename, "epub") + "sdr", 
                            "metadata.epub.lua")):
            filelist.append(filename)
    fb2s = glob.glob(os.path.join(path, "**/*.fb2"), recursive=True)
    for filename in fb2s:
        if os.path.exists(os.path.join(os.path.dirname(filename), 
                          removesuffix(filename, "fb2") + "sdr", 
                          "metadata.fb2.lua")):
            filelist.append(filename)
    return filelist


class KoreaderImporter(GenericImporter):
    def __init__(self, parent, path):
        self.path = path
        super().__init__(parent, "KOReader")

    def getNotes(self):
        self.bookfiles = koreader_scandir(self.path)
        # This applies book_selected as mask
        items = []
        for bookfile in self.bookfiles:
            if bookfile.endswith("fb2"):
                items.extend(
                    koreader_parse_fb2(bookfile, self.lang)
                )
            elif bookfile.endswith("epub"):
                items.extend(
                    koreader_parse_epub(bookfile, self.lang)
                )
        return zip(*items)


    