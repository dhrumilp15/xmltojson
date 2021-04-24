import xml.etree.ElementTree as ET
from seatmap_parser import root_to_dict


def package(s):
    return ET.fromstring(s)


def test_minimal():
    assert root_to_dict(package('<a></a>')) == {'a': None}


def test_simple():
    assert root_to_dict(package('<a>data</a>')) == {'a': 'data'}


def test_list():
    assert root_to_dict(package('<a><b>1</b><b>2</b><b>3</b></a>')
                        ) == {'a': {'b': [1, 2, 3]}}


def test_attrib():
    assert root_to_dict(package('<a href="xyz"/>')
                        ) == {'a': {'@href': 'xyz'}}


def test_attrib_and_cdata():
    assert root_to_dict(package('<a href="xyz">123</a>')
                        ) == {'a': {'@href': 'xyz', '#text': 123}}


def test_skip_whitespace():
    xml = """
        <root>
          <emptya>           </emptya>
          <emptyb attr="attrvalue">
          </emptyb>
          <value>hello</value>
        </root>
    """
    assert root_to_dict(
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
    res = root_to_dict(package(xml))
    assert res == {
        'http://defaultns.com/:root': {
            'http://defaultns.com/:x': {
                '@http://a.com/:attr': 'val',
                '#text': 1,
            },
            'http://a.com/:y': 2,
            'http://b.com/:z': 3,
        }
    }
