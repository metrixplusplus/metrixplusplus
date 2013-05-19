#
#    Metrix++, Copyright 2009-2013, Metrix++ Project
#    Link: http://metrixplusplus.sourceforge.net
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

# Copied from http://code.activestate.com/recipes/577268-python-data-structure-to-xml-serialization/
# - indent feature and better formatting added
# - fixed handling of lists in lists
# - fixed root object name for dictionaries

INDENT_SPACE_SYMBOL = "    " 

'''
Py2XML - Python to XML serialization

This code transforms a Python data structures into an XML document

Usage:
    serializer = Py2XML()
    xml_string = serializer.parse( python_object )
    print python_object
    print xml_string
'''

class Py2XML():

    def __init__( self ):

        self.data = "" # where we store the processed XML string

    def parse( self, pythonObj, objName=None, indent = 0 ):
        '''
        processes Python data structure into XML string
        needs objName if pythonObj is a List
        '''
        if pythonObj == None:
            return "\n" + (INDENT_SPACE_SYMBOL * indent) + ""

        if isinstance( pythonObj, dict ):
            self.data = self._PyDict2XML( pythonObj, objName, indent=indent+1 )
            
        elif isinstance( pythonObj, list ):
            # we need name for List object
            self.data = self._PyList2XML( pythonObj, objName, indent=indent+1 )
            
        else:
            self.data = "\n" + (INDENT_SPACE_SYMBOL * indent) + "<%(n)s>%(o)s</%(n)s>" % { 'n':objName, 'o':str( pythonObj ) }
            
        return self.data

    def _PyDict2XML( self, pyDictObj, objName=None, indent = 0 ):
        '''
        process Python Dict objects
        They can store XML attributes and/or children
        '''
        tagStr = ""     # XML string for this level
        attributes = {} # attribute key/value pairs
        attrStr = ""    # attribute string of this level
        childStr = ""   # XML string of this level's children

        for k, v in pyDictObj.items():

            if isinstance( v, dict ):
                # child tags, with attributes
                childStr += self._PyDict2XML( v, k, indent=indent+1 )

            elif isinstance( v, list ):
                # child tags, list of children
                childStr += self._PyList2XML( v, k, indent=indent+1 )

            else:
                # tag could have many attributes, let's save until later
                attributes.update( { k:v } )

        if objName == None:
            return childStr

        # create XML string for attributes
        for k, v in attributes.items():
            attrStr += " %s=\"%s\"" % ( k, v )

        # let's assemble our tag string
        if childStr == "":
            tagStr += "\n" + (INDENT_SPACE_SYMBOL * indent) + "<%(n)s%(a)s />" % { 'n':objName, 'a':attrStr }
        else:
            tagStr += ("\n" + (INDENT_SPACE_SYMBOL * indent) + "<%(n)s%(a)s>%(c)s" + "\n" + (INDENT_SPACE_SYMBOL * indent) + "</%(n)s>") % { 'n':objName, 'a':attrStr, 'c':childStr }

        return tagStr

    def _PyList2XML( self, pyListObj, objName=None, indent = 0 ):
        '''
        process Python List objects
        They have no attributes, just children
        Lists only hold Dicts or Strings
        '''
        tagStr = ""    # XML string for this level
        childStr = ""  # XML string of children

        for childObj in pyListObj:
            
            if isinstance( childObj, dict ):
                # here's some Magic
                # we're assuming that List parent has a plural name of child:
                # eg, persons > person, so cut off last char
                # name-wise, only really works for one level, however
                # in practice, this is probably ok
                childStr += self._PyDict2XML( childObj, objName[:-1], indent=indent+1 )
            elif isinstance( childObj, list ):
                # here's some Magic
                # we're assuming that List parent has a plural name of child:
                # eg, persons > person, so cut off last char
                # name-wise, only really works for one level, however
                # in practice, this is probably ok
                childStr += self._PyList2XML( childObj, objName[:-1], indent=indent+1 )
                pass
            else:
                childStr += "\n" + (INDENT_SPACE_SYMBOL * (indent + 1)) + "<" + objName[:-1] + ">"
                for string in childObj:
                    childStr += str(string);
                childStr += "</" + objName[:-1] + ">"
                
        if objName == None:
            return childStr

        tagStr += ("\n" + (INDENT_SPACE_SYMBOL * indent) + "<%(n)s>%(c)s" + "\n" + (INDENT_SPACE_SYMBOL * indent) + "</%(n)s>") % { 'n':objName, 'c':childStr }

        return tagStr