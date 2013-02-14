

import core.export.utils.py2xml
import core.export.utils.py2txt

def to_xml(data, root_name = None):
    serializer = core.export.utils.py2xml.Py2XML()
    return serializer.parse(data, objName=root_name)

def to_python(data, root_name = None):
    prefix = ""
    postfix = ""
    if root_name != None:
        prefix = "{'" + root_name + ": " 
        postfix = "}"
    return prefix + data.__repr__() + postfix

def to_txt(data, root_name = None):
    serializer = core.export.utils.py2txt.Py2TXT()
    return serializer.parse(data, objName=root_name, indent = -1)
