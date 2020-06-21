#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
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
    
    digitCount = 0

    def __init__( self, digitCount = None ):

        self.data = "" # where we store the processed XML string
        if digitCount != None:
            self.digitCount = digitCount
        else:
            self.digitCount = 8

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

        for k, v in sorted(list(pyDictObj.items())):

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
        for k, v in sorted(attributes.items()):
            if isinstance(v, float):
                attrStr += " %s=\"%s\"" % ( k, round(v, self.digitCount) )
            else:
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
