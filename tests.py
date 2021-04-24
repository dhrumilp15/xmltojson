import xml.etree.ElementTree as ET
import pytest
from seatmap_parser import parse_xml, get_root_from_xml
from io import BytesIO


def encode(s):
    try:
        return bytes(s, 'ascii')
    except (NameError, TypeError):
        return s


def package(s):
    return ET.parse(s)


def test_minimal():
    assert parse_xml(package('</a>')) == {'a': None}


def test_simple():
    assert parse_xml(package('<a>data</a>')) == {'a': {'#text': 'data'}}


def test_list():
    assert parse_xml(package('<a><b>1</b><b>2</b><b>3</b></a>')
                     ) == {'a': {'b': [1, 2, 3]}}


def test_attrib():
    assert parse_xml(package('<a href="xyz"/>')
                     ) == {'a': {'@href': 'xyz'}}


def test_attrib_and_cdata():
    assert parse_xml(package('<a href="xyz">123</a>')
                     ) == {'a': {'@href': 'xyz', '#text': 123}}


def test_semi_structured():
    assert parse_xml(package('<a>abc<b/>def</a>')
                     ) == {'a': {'b': None, '#text': 'abcdef'}}


def test_nested_semi_structured():
    assert parse_xml(package('<a>abc<b>123<c/>456</b>def</a>')
                     ) == {'a': {'#text': 'abcdef', 'b': {
                         '#text': 123456, 'c': None}}}


def test_skip_whitespace():
    xml = """
        <root>
          <emptya>           </emptya>
          <emptyb attr="attrvalue">
          </emptyb>
          <value>hello</value>
        </root>
    """
    assert parse_xml(
        package(xml)) == {
        'root': {
            'emptya': None,
            'emptyb': {
                '@attr': 'attrvalue'},
            'value': 'hello'}}


def test_namespace_support():
    xml = """
        <root xmlns="http://defaultns.com/"
              xmlns:a="http://a.com/"
              xmlns:b="http://b.com/">
          <x a:attr="val">1</x>
          <a:y>2</a:y>
          <b:z>3</b:z>
        </root>
        """
    d = {
        'http://defaultns.com/:root': {
            'http://defaultns.com/:x': {
                '@http://a.com/:attr': 'val',
                '#text': 1,
            },
            'http://a.com/:y': 2,
            'http://b.com/:z': 3,
        }
    }
    res = parse_xml(package(xml))
    assert res == d
