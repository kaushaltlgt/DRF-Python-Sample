#define functions to be dealt with XML data
import xmltodict
import xml.etree.ElementTree as ET

def get_xml_node(xmlstring, nodeelement):
    "to get text from an xml node by parsing an xml string"
    try:
        root = xmltodict.parse(xmlstring)
        return root[nodeelement]
    except:
        return None    

def get_xml_node_count(xmlstring, nodeelement):
    "to get count of an xml node by parsing an xml string"
    root = xmltodict.parse(xmlstring)
    try:
        res = root[nodeelement]
        res = 1
    except:    
        getvalue = [val[nodeelement] for key, val in root.items() if nodeelement in val] #list comprehension to get key value from nested dictionary object
        res = 0
        for x in getvalue:
            res += len(x)
    return res


def get_xml_childnodes(xmlstring):
    "to return a list of child nodes in a XML document" 
    try:
        tree = ET.fromstring(xmlstring)
        root = tree.getchildren()
        ditresult = []
        for child in root:
            for child1 in child:         
                ditresult.append(child1.tag)
        return ditresult
    except:
        return []


def get_xml_selectnodes(xmlstring, node):
    "to return a list of child nodes in a parent node" 
    try:
        tree = ET.fromstring(xmlstring)
        root = tree.getiterator(node)
        ditresult = []
        for child in root:
            for child1 in child:         
                ditresult.append(child1.tag)
        return ditresult
    except:
        return []                


      


  