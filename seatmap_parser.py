import argparse
import json
import xml.etree.ElementTree as ET
import re

alphanumeric = r'[A-Za-z1-9]\w+'

filetree = ET.parse('seatmap1.xml')
root = filetree.getroot()

def xmltag2json(xmltag) -> str:
    return xmltag.replace('{','').replace('}', ':')

def recurse(root, parent):
    tag = xmltag2json(root.tag)
    content = {}
    if root.attrib:
        content = {"@" + key : value for key, value in root.attrib.items()}
    if root.text:
        if re.search(alphanumeric, root.text):
            if content:
                content["#text"] = root.text
            else:
                content = root.text
    parent[tag] = content
    iterabletype = {}
    if len(root) > 0:
        # A look-ahead to see if we want to use a list or a dict to store the values 
        for child in root:
            ctag = xmltag2json(child.tag)
            if ctag in iterabletype:
                parent[tag][ctag] = []
                iterabletype[ctag] = []
            else:
                parent[tag][ctag] = {}
                iterabletype[ctag] = {}
    
    for child in root:
        ctag = xmltag2json(child.tag)
        value = recurse(child, {})
        if isinstance(iterabletype[ctag], list):
            parent[tag][ctag].append(value)
        else:
            parent[tag][ctag] = value
    if len(content) == 0:
        return None
    return content

with open('xmlout.json', 'w') as f:
    json.dump({xmltag2json(root.tag): recurse(root, {})}, fp=f, indent=4)



