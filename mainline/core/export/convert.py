#
#    Metrix++, Copyright 2009-2013, Metrix++ Project
#    Link: http://swi.sourceforge.net
#    
#    This file is a part of Metrix++ Tool.
#    
#    Metrix++ is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License.
#    
#    Metrix++ is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with Metrix++.  If not, see <http://www.gnu.org/licenses/>.
#


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
