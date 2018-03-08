# -*- coding: utf-8 -*-
"""Query the BnF Catalogue Général service for metadata."""

import logging
from xml.dom.minidom import parseString

from isbnlib.dev import stdmeta
from isbnlib.dev._bouth23 import u
from isbnlib.dev.webquery import query as wquery

LOGGER = logging.getLogger(__name__)
UA = 'isbnlib (gzip)'
SERVICE_URL = 'http://catalogue.bnf.fr/api/SRU?version=1.2'\
    '&operation=searchRetrieve&query=bib.isbn%20all%20%22{isbn}'\
    '%22&maximumRecords=1&recordSchema=dublincore'


def _get_text(topnode):
    """Get the text values in the child nodes."""
    text = ""
    for node in topnode.childNodes:
        if node.nodeType == node.TEXT_NODE:  # pragma: no cover
            text = text + node.data
    return text


def _clean_title(title):
    """Clean the Title field of some unnecessary annotations."""
    title = title.replace('<', '').replace('>', '')\
        .replace(': roman', '').split('/')[0]
    return title.strip(':.,; ')


def _clean_author(author):
    """Clean the Author field of some unnecessary annotations."""
    author = author.replace('Auteur du texte', '')\
        .split('/')[0].split(';')[0]
    if '(' in author:
        author = author.split(')')[0] + ')'
    return author.strip(':.,; ')


def parser_bnf(xml):
    """Parse the response from the BnF Catalogue Général service (France)."""
    # handle special case
    if 'numberOfRecords>0<' in xml:
        return {}
    # parse xml and extract canonical fields
    dom = parseString(xml)
    keys = ('Title', 'Authors', 'Publisher', 'Year', 'Language')
    fields = ('dc:title', 'dc:creator', 'dc:publisher', 'dc:date',
              'dc:language')
    recs = {}
    try:
        for key, field in zip(keys, fields):
            nodes = dom.getElementsByTagName("oai_dc:dc")[0]\
                .getElementsByTagName(field)
            txt = '|'.join([_get_text(node) for node in nodes])
            recs[key] = u(txt)
        # cleanning
        recs['Publisher'] = recs['Publisher'].split('|')[0]
        authors = recs['Authors'].split('|')
        recs['Authors'] = [_clean_author(author) for author in authors]
        recs['Year'] = ''.join(c for c in recs['Year'] if c.isdigit())
        recs['Title'] = _clean_title(recs['Title'])
        recs['Language'] = recs['Language'].split('|')[0]
    except IndexError:
        LOGGER.debug('Check the parsing for BnF (possible error!)')
    return recs


def _mapper(isbn, records):
    """Make records canonical.

    canonical: ISBN-13, Title, Authors, Publisher, Year, Language
    """
    # handle special case
    if not records:  # pragma: no cover
        return {}
    # add ISBN-13
    records['ISBN-13'] = u(isbn)
    # call stdmeta for extra cleanning and validation
    return stdmeta(records)


def query(isbn):
    """Query the BnF Catalogue Général service for metadata."""
    data = wquery(
        SERVICE_URL.format(isbn=isbn), user_agent=UA, parser=parser_bnf)
    if not data:  # pragma: no cover
        LOGGER.debug('No data from BnF Catalogue Général for isbn %s', isbn)
        return {}
    return _mapper(isbn, data)
