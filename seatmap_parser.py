#!/usr/bin/env python3
import argparse
import json
import xml.etree.ElementTree as ET
import re
import os
from typing import Any
from collections.abc import Iterable

ALPHANUMERIC = r"[A-Za-z1-9]+"


def xml_tag_to_json_tag(xml_tag: ET.Element.tag) -> str:
    """Converts an xml tag to a json tag.

    E.g.
        xml_tag_to_json_tag({http://www.opentravel.org/OTA/2003/05/common/}Fee)
        ->
        http://www.opentravel.org/OTA/2003/05/common/:Fee

    Args:
        xml_tag: The tag of an xml element.

    Returns:
        An equivalent string tag that's compatible with the JSON format.
    """
    return xml_tag.replace("{", "").replace("}", ":")


def text_to_value(text: str) -> Any:
    """Converts a given text to a more representative value.

    E.g.
        text_to_value("4.5") -> 4.5
        text_to_value("true") -> True
        text_to_value("27") -> 27
        text_to_value("0") -> 0

    Args:
        text: A string to be converted.

    Returns:
        A more representative value for `text`.
    """

    # Use casefold for string comparison
    txt = text.casefold()
    if txt == "true":
        return True
    if txt == "false":
        return False

    # We perform the digits check early
    if txt.isdigit():
        return int(txt)
    try:
        # float() also handles scientific notation
        return float(txt)
    except ValueError:
        search_for_alphanumeric = re.search(ALPHANUMERIC, txt)
        # If the text is many newline or tab characters
        if not search_for_alphanumeric:
            return None
        return text


def get_node_content(node: ET.Element) -> dict:
    '''Retrieves a node's attributes and text as a dict.

    Args:
        root: The current node in the XML structure.

    Returns:
        A dict of the node's attributes and text.
    '''
    # `content` holds attribute and text information of the current node.
    content = {}

    if node.attrib:
        # Prepend attributes' keys with "@".
        content = {
            "@" + xml_tag_to_json_tag(key): text_to_value(text) for key,
            text in node.attrib.items()}

    if node.text:
        converted_text = text_to_value(node.text)
        if converted_text:
            if content:
                # Prepend text key with "#" only if attributes exist.
                content["#text"] = converted_text
            else:
                # If there are no attributes, this node only holds text
                # information.
                content = converted_text
    return content


def parse_xml(root: ET.Element) -> dict:
    """Recursively converts the XML to a dict.

    Args:
        root: An ET.Element that represents the root of the xml.

    Returns:
        A dict of the xml's contents.
    """

    # Store the information at the current node in the parent
    content = get_node_content(root)
    if root:
        # Let's use a look-ahead to determine whether we want to use a list or a
        # dict to store a children.
        for child in root:
            child_tag = xml_tag_to_json_tag(child.tag)
            # Store this child as a list if there are duplicates. Otherwise,
            # we'll use a dict.
            if child_tag in content:
                content[child_tag] = []
            else:
                content[child_tag] = {}
        # Using the look-ahead, insert the values of children into
        # the appropriate root structure.
        for child in root:
            value = parse_xml(child)
            child_tag = xml_tag_to_json_tag(child.tag)
            if isinstance(content[child_tag], list):
                content[child_tag].append(value)
            else:
                content[child_tag] = value
    # If recursion returns an empty iterable, the current node has no
    # child information.
    if isinstance(content, Iterable) and not content:
        return None
    return content


def get_root_from_xml(file: str) -> ET.Element:
    """Returns the root of the XML file.

    Args:
        file: The XML's file location as a string.

    Returns:
        The root element of the XML file (xml.etree.ElementTree.Element)"""
    return ET.parse(file).getroot()


def root_to_dict(root: ET.Element) -> dict:
    '''Converts a root to its corresponding dict.

    Args:
        root: The root of the xml.

    Returns:
        A dict of the xml.
    '''
    return {xml_tag_to_json_tag(root.tag): parse_xml(root)}


def main(files: list) -> None:
    """A driver function to convert XMLs to JSONs

    Args:
        files: A list of filenames
    """

    for file in files:
        # We try to parse as many xmls as possible.
        if not os.path.exists(file):
            print("{} can't be found.".format(file))
            print("Usage: python seatmap_parser.py [FILENAMES.xml] ...")
            continue

        outfile = os.path.splitext(file)[0] + "_parsed.json"
        try:
            root = get_root_from_xml(file)
        except ET.ParseError:
            print("{} cannot be parsed." .format(file))
            print("Usage: python seatmap_parser.py [FILENAMES.xml] ...")
            continue

        xml_converted_to_dict = root_to_dict(root)

        with open(outfile, "w") as file_ptr:
            json.dump(xml_converted_to_dict, fp=file_ptr, indent=4)


def parse_args() -> list:
    """Parses a list of XML files passed as commandline arguments with
    ArgumentParser.

    Returns:
        A list of XML filenames to be converted to jsons.
    """
    argparser = argparse.ArgumentParser(
        description="Process a list of XML files.")
    argparser.add_argument(
        "xml_file", nargs="+", type=str, help="The locations of your XML files"
    )
    return argparser.parse_args().xml_file


if __name__ == "__main__":
    ARGS = parse_args()
    main(ARGS)
