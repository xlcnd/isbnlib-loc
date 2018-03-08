# -*- coding: utf-8 -*-
"""Query the LoC (Library of Congress) service for metadata."""

import logging
from xml.dom.minidom import parseString

from isbnlib.dev import stdmeta
from isbnlib.dev._bouth23 import u
from isbnlib.dev.webquery import query as wquery

LOGGER = logging.getLogger(__name__)
UA = 'isbnlib (gzip)'
SERVICE_URL = 'http://lx2.loc.gov:210/lcdb?version=2.0'\
    '&operation=searchRetrieve&query=bath.isbn={isbn}'\
    '&maximumRecords=1&recordSchema=dc'


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
        .replace(' :', ':').split('/')[0]
    return title.strip(':.,; ')


def _clean_author(author):
    """Clean the Author field of some unnecessary annotations."""
    author = author.replace('author', '').replace(' :', ':')\
        .split('/')[0].split(';')[0]
    if '(' in author:
        author = author.split(')')[0] + ')'
    return author.strip(':.,; ')


def parser_loc(xml):
    """Parse the response from the LoC (Library of Congress) service (US)."""
    # handle special case
    if 'numberOfRecords>0<' in xml:
        return {}
    # parse xml and extract canonical fields (Dublin Core)
    dom = parseString(xml)
    keys = ('Title', 'Authors', 'Publisher', 'Year', 'Language')
    fields = ('title', 'creator', 'publisher', 'date', 'language')
    recs = {}
    try:
        for key, field in zip(keys, fields):
            nodes = dom.getElementsByTagName("srw_dc:dc")[0]\
                .getElementsByTagName(field)
            txt = '|'.join([_get_text(node) for node in nodes])
            recs[key] = u(txt)
        # cleanning
        recs['Publisher'] = recs['Publisher'].split('|')[0]
        authors = recs['Authors'].split('|')
        recs['Authors'] = [_clean_author(author) for author in authors]
        recs['Year'] = ''.join(c for c in recs['Year'] if c.isdigit())[:4]
        recs['Title'] = _clean_title(recs['Title'])
        recs['Language'] = recs['Language'].split('|')[0]
    except IndexError:
        LOGGER.debug('Check the parsing for LoC (possible error!)')
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
    """Query the LoC Library of Congress service for metadata."""
    data = wquery(
        SERVICE_URL.format(isbn=isbn), user_agent=UA, parser=parser_loc)
    if not data:  # pragma: no cover
        LOGGER.debug('No data from LoC for isbn %s', isbn)
        return {}
    return _mapper(isbn, data)
