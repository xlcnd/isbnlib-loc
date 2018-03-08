# -*- coding: utf-8 -*-
# flake8: noqa
# pylint: skip-file
"""nose tests for metadata."""

from nose.tools import assert_equals
from isbnlib import meta
from .._bnf import query


def test_query():
    """Test the query of metadata (BnF Catalogue Général) with 'low level' queries."""
    assert_equals(len(repr(query('9781849692341'))) == 2, True)
    assert_equals(len(repr(query('9781849692343'))) == 2, True)

    assert_equals(len(repr(query('9782072693144'))) > 100, True)
    assert_equals(len(repr(query('9782247169092'))) > 100, True)
    assert_equals(len(repr(query('9782210760851'))) > 100, True)

    assert_equals(len(repr(query('9780000000'))) == 2, True)
