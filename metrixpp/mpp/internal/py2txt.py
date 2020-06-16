#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

# Copied from http://code.activestate.com/recipes/577268-python-data-structure-to-TXT-serialization/ and modified

'''
Py2TXT - Python to TXT serialization

This code transforms a Python data structures into an TXT document

Usage:
    serializer = Py2TXT()
    txt_string = serializer.parse( python_object )
    print python_object
    print txt_string
'''

INDENT_SPACE_SYMBOL = ".   " 

class Py2TXT():

    def __init__( self ):

        self.data = "" # where we store the processed TXT string

    def parse( self, pythonObj, objName=None, indent = 0 ):
        '''
        processes Python data structure into TXT string
        needs objName if pythonObj is a List
        '''
        if pythonObj == None:
            return "\n" + (INDENT_SPACE_SYMBOL * indent) + ""

        if isinstance( pythonObj, dict ):
            self.data = self._PyDict2TXT( pythonObj, objName, indent = indent + 1 )
            
        elif isinstance( pythonObj, list ):
            # we need name for List object
            self.data = self._PyList2TXT( pythonObj, objName, indent = indent + 1 )
            
        else:
            self.data = "\n" + (INDENT_SPACE_SYMBOL * indent) + "%(n)s: %(o)s" % { 'n':objName, 'o':str( pythonObj ) }
            
        self.data = (INDENT_SPACE_SYMBOL * (indent + 1)) + "-" * 80 + self.data + "\n" + (INDENT_SPACE_SYMBOL * (indent + 1)) + "=" * 80 
        return self.data

    def _PyDict2TXT( self, pyDictObj, objName=None, indent = 0 ):
        '''
        process Python Dict objects
        They can store TXT attributes and/or children
        '''
        tagStr = ""     # TXT string for this level
        attributes = {} # attribute key/value pairs
        attrStr = ""    # attribute string of this level
        childStr = ""   # TXT string of this level's children

        for k, v in list(pyDictObj.items()):

            if isinstance( v, dict ):
                # child tags, with attributes
                childStr += self._PyDict2TXT( v, k, indent = indent + 1 )

            elif isinstance( v, list ):
                # child tags, list of children
                childStr += self._PyList2TXT( v, k, indent = indent + 1 )

            else:
                # tag could have many attributes, let's save until later
                attributes.update( { k:v } )

        if objName == None:
            return childStr

        # create TXT string for attributes
        attrStr += ""
        for k, v in list(attributes.items()):
            attrStr += "\n" + (INDENT_SPACE_SYMBOL * (indent + 1)) + "%s=\"%s\"" % ( k, v )

        # let's assemble our tag string
        if childStr == "":
            tagStr += "\n" + (INDENT_SPACE_SYMBOL * indent) + "%(n)s: %(a)s" % { 'n':objName, 'a':attrStr }
        else:
            tagStr += "\n" + (INDENT_SPACE_SYMBOL * indent) + "%(n)s: %(a)s %(c)s" % { 'n':objName, 'a':attrStr, 'c':childStr }

        return tagStr

    def _PyList2TXT( self, pyListObj, objName=None, indent = 0 ):
        '''
        process Python List objects
        They have no attributes, just children
        Lists only hold Dicts or Strings
        '''
        tagStr = ""    # TXT string for this level
        childStr = ""  # TXT string of children

        for childObj in pyListObj:
            
            if isinstance( childObj, dict ):
                # here's some Magic
                # we're assuming that List parent has a plural name of child:
                # eg, persons > person, so cut off last char
                # name-wise, only really works for one level, however
                # in practice, this is probably ok
                childStr += "\n" + (INDENT_SPACE_SYMBOL * indent) + self._PyDict2TXT( childObj, objName[:-1], indent = indent + 1 )
            elif isinstance( childObj, list ):
                # here's some Magic
                # we're assuming that List parent has a plural name of child:
                # eg, persons > person, so cut off last char
                # name-wise, only really works for one level, however
                # in practice, this is probably ok
                childStr += self._PyList2TXT( childObj, objName[:-1], indent = indent + 1 )
            else:
                childStr += "\n" + (INDENT_SPACE_SYMBOL * (indent + 1))
                for string in childObj:
                    childStr += str(string);

        if objName == None:
            return childStr

        tagStr += "\n" + (INDENT_SPACE_SYMBOL * indent) + "%(n)s:%(c)s" % { 'n':objName, 'c':childStr }

        return tagStr
