import json
import urllib.request
import requests
import os
import re
import unicodedata
import time
from .vsnt import *
from bs4 import BeautifulSoup
from typing import List, Dict
from .db import *
from pystardict import Dictionary
from .dictionary import *
from .dictformats import *
from .xdxftransform import xdxf2html
from PyQt5.QtCore import QCoreApplication
import mobi
from itertools import islice
from lxml import etree
from charset_normalizer import from_bytes
from ebooklib import epub, ITEM_DOCUMENT

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}


def invoke(action, server, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(
        urllib.request.urlopen(
            urllib.request.Request(
                server, requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']


def getDeckList(server) -> list:
    result = invoke('deckNames', server)
    return list(result)


def getNoteTypes(server) -> list:
    result = invoke('modelNames', server)
    return list(result)


def getFields(server, name) -> list:
    result = invoke('modelFieldNames', server, modelName=name)
    return list(result)


def addNote(server, content) -> int:
    result = invoke('addNote', server, note=content)
    return int(result)


def addNotes(server, content) -> List[int]:
    result = invoke('addNotes', server, notes=content)
    return list(result)

def notesInfo(server, notes):
    return invoke('notesInfo', server, notes=notes)

def getVersion(server) -> str:
    result = invoke('version', server)
    return str(result)

def addDefaultModel(server):
    return invoke('createModel', 
        server, 
        modelName="vocabsieve-notes", 
        inOrderFields=FIELDS, 
        css=CSS, 
        cardTemplates=CARDS
        )

def findNotes(server, query):
    return invoke('findNotes', server, query=query)


def guiBrowse(server, query):
    return invoke('guiBrowse', server, query=query)

def is_json(myjson) -> bool:
    if not myjson.startswith("{"):
        return False
    try:
        json_object = json.loads(myjson)
        json_object['word']
        json_object['sentence']
    except ValueError as e:
        return False
    except Exception as e:
        print(e)
        return False
    return True


def failed_lookup(word, settings) -> str:
    return str("<b>Definition for \"" + str(word) + "\" not found.</b><br>Check the following:<br>" +
               "- Language setting (Current: " + settings.value("target_language", 'en') + ")<br>" +
               "- Is the correct word being looked up?<br>" +
               "- Are you connected to the Internet?<br>" +
               "Otherwise, then " + settings.value("dict_source", "Wiktionary (English)") +
               " probably just does not have this word listed.")


def is_oneword(s) -> bool:
    return len(s.split()) == 1

def freq_to_stars(freq_num, lemmatize):
    if lemmatize:
        if freq_num <= 1000:
            return "★★★★★"
        elif freq_num <= 3000:
            return "★★★★☆"
        elif freq_num <= 8000:
            return "★★★☆☆"
        elif freq_num <= 20000:
            return "★★☆☆☆"
        elif freq_num <= 40000:
            return "★☆☆☆☆"
        else:
            return "☆☆☆☆☆"
    else:
        if freq_num <= 1500:
            return "★★★★★"
        elif freq_num <= 5000:
            return "★★★★☆"
        elif freq_num <= 15000:
            return "★★★☆☆"
        elif freq_num <= 30000:
            return "★★☆☆☆"
        elif freq_num <= 60000:
            return "★☆☆☆☆"
        else:
            return "☆☆☆☆☆"

def dictimport(path, dicttype, lang, name) -> None:
    "Import dictionary from file to database"
    if dicttype == "stardict":
        stardict = Dictionary(os.path.splitext(path)[0], in_memory=True)
        d = {}
        if stardict.ifo.sametypesequence == 'x':
            for key in stardict.idx.keys():
                d[key] = xdxf2html(stardict.dict[key])
        else:
            for key in stardict.idx.keys():
                d[key] = stardict.dict[key]
        dictdb.importdict(d, lang, name)
    elif dicttype == "json":
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
            dictdb.importdict(d, lang, name)
    elif dicttype == "migaku":
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            d = {}
            for item in data:
                d[item['term']] = item['definition']
            dictdb.importdict(d, lang, name)
    elif dicttype == "freq":
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            d = {}
            for i, word in enumerate(data):
                d[word] = str(i + 1)
            dictdb.importdict(d, lang, name)
    elif dicttype == "audiolib":
        # Audios will be stored as a serialized json list
        filelist = []
        d = {}
        for root, dirs, files in os.walk(path):
            for item in files:
                filelist.append(
                    os.path.relpath(
                        os.path.join(
                            root, item), path))
        for item in filelist:
            headword = os.path.basename(os.path.splitext(item)[0]).lower()
            if not d.get(headword):
                d[headword] = [item]
            else:
                d[headword].append(item)
        for word in d.keys():
            d[word] = json.dumps(d[word])
        dictdb.importdict(d, lang, name)
    elif dicttype == 'mdx':
        d = parseMDX(path)
        dictdb.importdict(d, lang, name)
    elif dicttype == "dsl":
        d = parseDSL(path)
        dictdb.importdict(d, lang, name)
    elif dicttype == "csv":
        d = parseCSV(path)
        dictdb.importdict(d, lang, name)
    elif dicttype == "tsv":
        d = parseTSV(path)
        dictdb.importdict(d, lang, name)


def dictdelete(name) -> None:
    dictdb.deletedict(name)

def starts_with_cyrillic(s):
    if s:
        return unicodedata.name(s[0]).startswith("CYRILLIC")
    else:
        return s

def remove_ns(s: str) -> str: return str(s).split("}")[-1]

def tostr(s):
    return str(
        from_bytes(
            etree.tostring(
                s,
                encoding='utf8',
                method='text')).best()).strip()

def ebook2text(path):
    _, ext = os.path.splitext(path)
    if ext in {'.azw', '.azw3', '.kfx', '.mobi'}:
        _, newpath = mobi.extract(path)
        # newpath is either html or epub
        return ebook2text(newpath)
    if ext == '.epub':
        book = epub.read_epub(path)
        chapters = []
        for doc in book.get_items_of_type(ITEM_DOCUMENT):
            tree = etree.fromstring(doc.get_content())
            notags = etree.tostring(tree, encoding='utf8', method="text")
            data = str(from_bytes(notags).best()).strip()
            if len(data.splitlines()) < 2:
                continue
            content = "\n".join(data.splitlines())
            chapters.append(content)
    elif ext == '.fb2':
        with open(path, 'rb') as f:
            data = f.read()
            tree = etree.fromstring(data)
        chapters = []
        already_seen = False
        for el in tree:
            tag_nons = remove_ns(el.tag)
            if tag_nons == "body" and not already_seen:
                already_seen = True
                for section in el:
                    current_chapter = ""
                    for item in section:
                        if remove_ns(item.tag) == "title":
                            current_chapter = tostr(item) + "\n\n"
                        else:
                            current_chapter += tostr(item) + "\n"
                    chapters.append(current_chapter)
    elif ext == '.html':
        with open(path, 'r', encoding='utf-8') as f:
            c = f.read()
            return BeautifulSoup(c).getText()
    
    return "\n\n\n\n".join(chapters)

def window(seq, n=2):
    "Returns a sliding window (of width n) over data from the iterable"
    "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result