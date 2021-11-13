# -*- coding: utf-8 -*-
# flake8: noqa
# pylint: skip-file
"""tests for metadata."""

from isbnlib import meta
from .._loc import query


def test_query():
    """Test the query of metadata (LoC Library of Congress) with 'low level' queries."""
    assert (len(repr(query('9780321534965'))) > 100) == True
    assert (len(repr(query('9781118241257'))) > 100) == True
    assert (len(repr(query('9780425284629'))) > 100) == True


def test_query_missing():
    """Test LoC with 'low level' queries (missing data)."""
    assert (len(repr(query('9781849692341'))) <= 2) == True
    assert (len(repr(query('9781849692343'))) <= 2) == True


def test_query_wrong():
    """Test LoC with 'low level' queries (wrong data)."""
    assert (len(repr(query('9780000000'))) <= 2) == True
