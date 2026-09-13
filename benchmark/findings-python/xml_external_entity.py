from xml.etree import ElementTree

def parse_uploaded_xml(xml_string):
    return ElementTree.fromstring(xml_string)
