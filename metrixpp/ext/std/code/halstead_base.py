# -*- coding: utf-8 -*-
#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#
#    This file is a part of Metrix++ Tool.
#

""" @file
Implements Halstead basic metrics
@package HalstadBaseMetrics
Halstead basic metrics:
- determines basic N1,n1,N2,n2 values
- s. module halstead.py for calculating advanced metrics

Note that we can assume the file to be analyzed is syntactically correct;
this should be true especially for correct parentheses' pairing!

An overview is found on https://www.verifysoft.com/en_halstead_metrics.html

A discussion of software metrics (esp. Halstead and Oman): https://core.ac.uk/download/pdf/216048382.pdf

A detailed explanation with example is found on http://www.verifysoft.com/de_cmtpp_mscoder.pdf (german)
"""

from metrixpp.mpp import api
import re

# ------------------------------------------------------------------------------
# regex strings for C/C++:
# from https://www.verifysoft.com/en_halstead_metrics.html
# ------------------------------------------------------------------------------
# parentheses: inc n1 for each pair of "()","[]", "{}"
#PARENS_CPP    = r"""\(|\)|\[|\]|\{|\}"""
# since we assume parentheses are properly paired, we only need to test the opening ones:
OPENPARENS_CPP = r"""\(|\[|\{"""
# operators: inc n1
OPERATORS_CPP = r"""#|!=|!|~=|~|\+\+|\+=|\+|--|-=|->|-|\*=|\*|/=|/|%=|%|==|=|>>=|>>|>=|>|<<=|<<|<=|<|\|\||\|=|\||\^\^|\^=|\^|&&|&=|&|::|:|\?|\.\.\.|\.|\,|;"""
# storage class specifiers: inc n1
SCSPEC_CPP = r"""auto|extern|inline|register|static|typedef|virtual|mutable"""
# type qualifiers: inc n1
TYPEQUAL_CPP = r"""const|friend|volatile"""
# reserved words: inc n1, note that an other inc n1 occurs by subsequent "()" or "{}" pair!
RESERVED_CPP = r"""asm|class|delete|else|enum|goto|new|operator|sizeof|struct|this|union|namespace|using|try|throw|const_cast|static_cast|dynamic_cast|reinterpret_cast|typeid|template|explicit|true|false|typename|break|continue|return|private|protected|public|transient"""
# reserved words: inc n1, but ignore subsequent "()" pair, i.e. don't inc n1!
RESPAREN_CPP = r"""for|if|switch|while|catch"""
# reserved words: inc n1, but ignore subsequent ":"
RESCOLN_CPP  = r"""case|default"""

# reserved operators requiring special handling in the OperandCounter_XX classes:
RESWORD_CPP = SCSPEC_CPP+"|"+TYPEQUAL_CPP+"|"+RESERVED_CPP+"|"+RESPAREN_CPP+"|"+RESCOLN_CPP
RESWORDALL_CPP = r"(\b"+RESWORD_CPP+"|do"+r")\b"

# ------------------------------------------------------------------------------
# An attempt for JAVA - not fairly tested!
# regex strings for JAVA, empirically derived from C++ strings above
# parentheses: inc n1 for each pair of "()","[]", "{}"
#PARENS_JAVA    = r"""\(|\)|\[|\]|\{|\}"""
# since we assume parentheses are properly paired, we only need to test the opening ones:
OPENPARENS_JAVA = r"""\(|\[|\{"""
# inc n1:
OPERATORS_JAVA = r"""#|!=|!|~|\+\+|\+=|\+|--|-=|->|-|\*=|\*|/=|/|%=|%|==|=|>>>=|>>>|>>=|>>|>=|>|<<=|<<|<=|<|\|\||\|=|\||\^\^|\^=|\^|&&|&=|&|::|:|\?|\.\.\.|\.|\,|;"""
SCSPEC_JAVA    = r"""static|abstract|native|import|final|implements|extends|throws"""
TYPEQUAL_JAVA  = r"""const|volatile"""
# reserved words: inc n1, note that an other inc n1 occurs by subsequent "()" or "{}" pair!
RESERVED_JAVA  = r"""assert|class|else|enum|goto|new|this|try|throw|break|continue|return|private|protected|public|true|false|package|instanceof|interface|synchronized"""
# reserved words: inc n1, but ignore subsequent "()" pair, i.e. don't inc n1!
RESPAREN_JAVA  = r"""for|if|switch|while|catch|finally|super"""
# reserved words: inc n1, but ignore subsequent ":"
RESCOLN_JAVA   = r"""case|default"""

RESWORD_JAVA   = SCSPEC_JAVA+"|"+TYPEQUAL_JAVA+"|"+RESERVED_JAVA+"|"+RESPAREN_JAVA+"|"+RESCOLN_JAVA
RESWORDALL_JAVA = r"(\b"+RESWORD_JAVA+"|do"+r")\b"

# ------------------------------------------------------------------------------
# inc N2 for each match - regex identically for all languages?!:
OPERANDS  = r"\b\w+\b"
#OPERANDS  = r"\b\w+(?<!"+RESWORD_CPP+")\b" not functional: look-ahead only allows patterns with identical length

# ------------------------------------------------------------------------------
# todo: regex strings for C#
# ------------------------------------------------------------------------------

class Plugin(api.Plugin,
             api.IConfigurable,
             api.Child,
             api.MetricPluginMixin):
    """ @brief Halstad basic metrics class

    To prevent double scanning for N1/n1 and N2/n2 values we only scan once
    to obtaining N1/N2 and preserve the operands and operators in a dictionary
    @ref "halstead_dict"; so to obtain the n1/n2 values we only need the length
    of the respective dictionary entry. \n
    This requires to obtain the N-value before the respective n-value - s. @ref self.initialize

    Additionally the dictionary must also cover the regions because the api.py
    iterates thus:
    @code
        for field in self.get_fields():
            ...
            for region in data.iterate_regions():
                counter = counter_class()
                for marker in data.iterate_markers()
                    counter.count()
                    ...
    @endcode
    which instantiates a counter_class() for each region.

    @attention
    - It is assumed that metrics fields are calculated in the order they are
      declared i.e. declare_metric() is called - s. @ref self.initialize()
    - If iteration sequence is changed (s. above) this plugin probably may be
      updated accordingly.
    """
    halstead_dict = {}  # dictionary to preserve operands and operators for each region
    opt_prefix = 'std.code.halstead.'

    def declare_configuration(self, parser):
        def add_option(opt,action,default,help):
            parser.add_option("--"+self.opt_prefix+opt, "--sch"+opt, action=action, default=default,
                help=help)

        add_option("all", action="store_true", default=False,
            help="Halstead metrics plugin: all metrics are calculated [default: %default]")
        add_option("base", action="store_true", default=False,
            help="Halstead metrics plugin: base metrics n1,n2,N1,N2 [default: %default]")

    def configure(self, options):
        self.is_active_ehb = options.__dict__[self.opt_prefix+'base'] or options.__dict__[self.opt_prefix+'all']

    def initialize(self):
        """ @brief Basic halstead metrics - N1,n1,N2,n2
        @note
        - Ordering of declare_metric calls is important since calculation of nx
          depends on match counts of Nx (x = 1,2)! i.e. Nx has to be counted
          first and then nx is derived from these.
        - Since counter classes (i.e. here: DictCounter resp. its derived
          variants) are not persistent (i.e. they are instantiated and finally
          destroyed for each iteration over regions and the respective fields,
          s. api.MetricPluginMixin.callback()/count_if_active() )
          recognized operators and operands have to be preserved using dictionaries,
          s. operators_dict and operands_dict
          @note Another possibility would be to implement independent classes
                for N1,n1,N2,n2 but this seems very ineffective since matching
                for N1 and n1 resp. N2 and n2 would beeing exactly the same
                i.e. matching would be done twice decreasing performance
        """
        # Operator metrics N1,n1
        operator_pattern_search = re.compile(r"[\+\-\*\/\=]")    # common operators
        operator_pattern_cpp = re.compile(
            r"(\b("+RESWORD_CPP+r")\b|"+OPERATORS_CPP+"|"+OPENPARENS_CPP+")"
            )
        operator_pattern_java = re.compile(
            r"(\b("+RESWORD_JAVA+r")\b|"+OPERATORS_JAVA+"|"+OPENPARENS_JAVA+")"
            )
        operator_pattern_cs   = operator_pattern_search
        self.declare_metric(self.is_active_ehb,
                            self.Field('N1', int, non_zero=True),
                            {
                             'std.code.java': (operator_pattern_java, self.HalsteadCounter_N1_java),
                             'std.code.cpp':  (operator_pattern_cpp,  self.HalsteadCounter_N1_cpp),
                             #'std.code.cs':   (operator_pattern_cs,   self.HalsteadCounter_N1_cs),
                             '*': operator_pattern_search
                            },
                            marker_type_mask=api.Marker.T.CODE+api.Marker.T.PREPROCESSOR,
                            region_type_mask=api.Region.T.ANY)

        self.declare_metric(self.is_active_ehb,
                            self.Field('_n1', int, non_zero=True),
                            {
                             '*':(None, self.HalsteadCounter_n1) # nothing to do, but only to get previously counted operators = len(halstead_dict)
                            },
                            marker_type_mask=api.Marker.T.NONE)

        # Operand metrics N2,n2
        operand_pattern_search = re.compile(r"("+OPERANDS+")")
        operand_pattern_java   = operand_pattern_search
        operand_pattern_cpp    = operand_pattern_search
        operand_pattern_cs     = operand_pattern_search
        self.declare_metric(self.is_active_ehb,
                            self.Field('N2', int, non_zero=True),
                            {
                             'std.code.java': (operand_pattern_java, self.HalsteadCounter_N2_java),
                             'std.code.cpp':  (operand_pattern_cpp,  self.HalsteadCounter_N2_cpp),
                             #'std.code.cs':   (operand_pattern_cs,   self.HalsteadCounter_N2_cs),
                             '*': operand_pattern_search
                            },
                            marker_type_mask=api.Marker.T.CODE+api.Marker.T.STRING+api.Marker.T.PREPROCESSOR,
                            region_type_mask=api.Region.T.ANY)

        self.declare_metric(self.is_active_ehb,
                            self.Field('_n2', int, non_zero=True),
                            {
                             '*':(None, self.HalsteadCounter_n2) # nothing to do, but only to get previously counted operands = len(halstead_dict)
                            },
                            marker_type_mask=api.Marker.T.NONE)

        super(Plugin, self).initialize(fields=self.get_fields(), support_regions=True)

        if self.is_active():
            self.subscribe_by_parents_interface(api.ICode)

    #def callback(self, parent, data, is_updated):
    #    print('halstead_base');
    #    super(Plugin, self).callback(parent,data,is_updated)

    # --------------------------------------------------------------------------

    class DictCounter(api.MetricPluginMixin.IterIncrementCounter):
        """ Common dictionary counter class
        \n
        Counts every match as IterIncrementCounter does, but additionally puts
        each match as a key into a dictionary to
        - count every occurrence of this match: inc(dictcounter[match])
        - count the summary of distinct occurrences of each match: len(dictcounter)

        @note This class may be moved to api.MetricPluginMixin class for common use
        """
        def __init__(self, *args, **kwargs):
            super(Plugin.DictCounter, self).__init__(*args, **kwargs)
            self.dictcounter = {}

        def inc_DictCounter(self, key):
            # ensure key is present:
            if key not in self.dictcounter: self.dictcounter[key] = 0
            self.dictcounter[key] += 1

        def increment(self, match):
            self.inc_DictCounter(match.group(0))
            return 1

        """ Debug
        def get_result(self):
            N = 0;
            for op in self.dictcounter:
                N += self.dictcounter[op]
            #    print(op+" : "+str(self.dictcounter[op]));
            print("N = "+str(N)+" n = "+str(len(self.dictcounter))+"\n")
            return self.result  # = N
        #"""

    # --------------------------------------------------------------------------
    # classes to calculate basic halstead metrics N1,n1,N2,n2:
    # --------------------------------------------------------------------------

    class HalsteadCounter(DictCounter):

        def get_DictKey(self):
            if ( self.region.name == None ):
                return "__file__"
            else:
                return self.region.name

        def init_DictCounter(self):
            """ @brief Initializes the dictcounter
            """
            dictkey = self.get_DictKey()
            self.plugin.halstead_dict[dictkey] = {}
            self.dictcounter = self.plugin.halstead_dict[dictkey]
            #print(dictkey)

        def get_DictCounter(self):
            """ @brief Gets an existing dictcounter
            """
            dictkey = self.get_DictKey()
            self.dictcounter = self.plugin.halstead_dict[dictkey]
            #print(dictkey)

    class HalsteadCounter_N(HalsteadCounter):
        """ Number of Operators or Operands """
        def __init__(self, *args, **kwargs):
            super(Plugin.HalsteadCounter_N, self).__init__(*args, **kwargs)
            self.init_DictCounter()

        def get_result(self):
            """ Retrieves the totally counted matches
            @note
            Not really necessary since it does the same as the base class
            IterIncrementCounter - for clarity / debugging purposes only
            """
            #print("N = "+str(self.result)+" n = "+str(len(self.dictcounter))))
            return self.result  # = N

    class HalsteadCounter_n(HalsteadCounter):
        """ Number of unique Operators or Operands
        @note
        Must be called after HalsteadCounter_N and before any call of another
        HalsteadCounter_N!
        """
        def __init__(self, *args, **kwargs):
            super(Plugin.HalsteadCounter_n, self).__init__(*args, **kwargs)
            self.get_DictCounter()

        def get_result(self):
            """ Retrieves the distinct matches
            """
            #print(str(len(self.dictcounter)))
            return len(self.dictcounter)

    # --------------------------------------------------------------------------

    class HalsteadCounter_N1(HalsteadCounter_N):
        """ Number of Operators """
        def __init__(self, *args, **kwargs):
            super(Plugin.HalsteadCounter_N1, self).__init__(*args, **kwargs)
            self.ignore = ""

        def count(self, marker, pattern_to_search):
            """ @brief Count operators
            \n
            According to https://www.verifysoft.com/en_halstead_metrics.html
            preprocessor directives (marker == T.PREPROCESSOR) are treated as
            operators. Since they are collected separately we have to adjust the
            "pattern_to_search"; for all other markers the original
            "pattern_to_search" has to take place, i.e. the desired patterns
            must be matched.
            An other possibility would be to search for preprocessor and code
            independently as distinct metrics, i.e. to instantiate distinct
            counter classes counting N1code and N1pre as distinct database fields
            and finally aggregate them to the unique metric / database field N1.
            """

            # finditer(string,begin,end) doesn't copy the string slice but
            # starts matching at "begin" within "string" and thus prevents
            # matching the "\A" specifier (probably similar with "end" and "\Z"):
            # So first extract desired text!:
            text = self.data.get_content()[marker.get_offset_begin():marker.get_offset_end()]

            self.marker = marker
            if marker.group == api.Marker.T.PREPROCESSOR:
                # ignore spaces and tabs at line start upto "#" and after "#";
                # only search for preprocessor keyword:
                pattern_to_search = re.compile(r"\A[ \t]*\#[ \t]*[a-zA-Z]\w+")

            self.pattern_to_search = pattern_to_search
            for match in pattern_to_search.finditer(text):
                self.result += self.increment(match)


        def set_ignore(self,match,key):
            self.ignore = ''

        ## @brief increment
        def increment(self, match):
            result = 0
            key = match.group(0)

            if self.marker.group == api.Marker.T.PREPROCESSOR:  # preprocessor keyword:
                key = key.replace(" ", "")                      # remove all spaces
                key = key.replace("\t", "")                     # remove all tabs

            if key != self.ignore:
                self.inc_DictCounter(key)
                result = 1
                #print(key)

            self.set_ignore(match,key)

            return result

    class HalsteadCounter_N1_cpp(HalsteadCounter_N1):
        def set_ignore(self,match,key):
            if re.match("("+RESPAREN_CPP+")",key):
                self.ignore = "("   # ignore subsequent "("
            elif re.match("("+RESCOLN_CPP+")",key):
                self.ignore = ":"   # ignore subsequent ":"
            elif key == self.ignore:
                self.ignore = ""

    class HalsteadCounter_N1_java(HalsteadCounter_N1):
        def set_ignore(self,match,key):
            if re.match("("+RESPAREN_JAVA+")",key):
                self.ignore = "("   # ignore subsequent "("
            elif re.match("("+RESCOLN_JAVA+")",key):
                self.ignore = ":"   # ignore subsequent ":"
            elif key == self.ignore:
                self.ignore = ""

    class HalsteadCounter_n1(HalsteadCounter_n):
        """ Distinct number of Operators """
        pass
        #def __init__(self, *args, **kwargs):
        #    super(Plugin.HalsteadCounter_n1, self).__init__(*args, **kwargs)

    # --------------------------------------------------------------------------

    class HalsteadCounter_N2(HalsteadCounter_N):
        """ Number of Operands """
        #def __init__(self, *args, **kwargs):
        #    super(Plugin.HalsteadCounter_N2, self).__init__(*args, **kwargs)

        def count(self, marker, pattern_to_search):
            """ Count operands
            \n
            Since operands either may be whole strings or parts of code we have
            to modify "pattern_to_search" depending on "marker":
            Strings (marker == T.STRING) have to be taken as a whole. According
            to https://www.verifysoft.com/en_halstead_metrics.html preprocessor
            directives (marker == T.PREPROCESSOR) themselves are counted on their
            directive identifier and for all other markers the original
            "pattern_to_search" has to take place, i.e. the desired patterns
            must be matched.
            An other possibility would be to search for preprocessor, strings
            and code independently as distinct metrics, i.e. to instantiate
            distinct counter classes counting N2string, N2code and N2pre as
            distinct database fields and finally aggregate them to the unique
            metric / database field N2.
            """

            text = self.data.get_content()[marker.get_offset_begin():marker.get_offset_end()]
            #print("---> "+text)

            self.marker = marker
            if marker.group == api.Marker.T.PREPROCESSOR:
                # ignore spaces and tabs at line start upto "#" and after "#";
                # only search for preprocessor keyword:
                pattern_to_search = re.compile(r"\A[ \t]*\#[ \t]*[a-zA-Z]\w+")
            elif marker.group == api.Marker.T.STRING:
                pattern_to_search = re.compile(r".+")

            self.pattern_to_search = pattern_to_search
            for match in pattern_to_search.finditer(text):
                self.result += self.increment(match)

        def is_resword(self,match,key):
            return False

        def increment(self, match):
            result = 0
            key = match.group(0)
            if self.marker.group == api.Marker.T.PREPROCESSOR:  # preprocessor keyword:
                key = key.replace(" ", "")                      # remove all spaces
                key = key.replace("\t", "")                     # remove all tabs

            if ( (self.marker.group != api.Marker.T.CODE)   # "key" is not code
             or not self.is_resword(match,key)              # or not a reserved word
            ):
                self.inc_DictCounter(key)
                result = 1

            return result

    class HalsteadCounter_N2_cpp(HalsteadCounter_N2):
        def is_resword(self,match,key):
            return re.match(RESWORDALL_CPP,key)            # key is a reserved word
    class HalsteadCounter_N2_java(HalsteadCounter_N2):
        def is_resword(self,match,key):
            return re.match(RESWORDALL_JAVA,key)           # key is a reserved word

    class HalsteadCounter_n2(HalsteadCounter_n):
        """ Distinct number of Operands """
        pass
        #def __init__(self, *args, **kwargs):
        #    super(Plugin.HalsteadCounter_n2, self).__init__("2", *args, **kwargs)
