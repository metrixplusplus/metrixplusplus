# -*- coding: utf-8 -*-
#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#
#    This file is a part of Metrix++ Tool.
#
"""
Implements Halstead basic metrics:
- determines basic n1,n2,N1,N2 values
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
# operators: inc n1
OPERATORS = r"""#|!=|!|~|\+\+|\+=|\+|--|-=|->|-|\*|\*=|\*|/=|/|%=|%|==|=|>>=|>>|>=|>|<<=|<<|<=|<|\|\||\|=|\||\^\^|\^=|\^|&&|&=|&|::|:|\?|\.\.\.|\.|\,|;"""
# parentheses: inc n1 for each pair of "()","[]", "{}"
PARENS    = r"""\(|\)|\[|\]|\{|\}"""
# storage class specifiers: inc n1
SCSPEC    = r"""auto|extern|inline|register|static|typedef|virtual|mutable"""
# type qualifiers: inc n1
TYPE_QUAL = r"""const|friend|volatile"""
# reserved words: inc n1, note that an other inc n1 occurs by subsequent "()" or "{}" pair!
RESERVED  = r"""asm|class|delete|do|else|enum|goto|new|operator|sizeof|struct|this|union|namespace|using|try|throw|const_cast|static_cast|dynamic_cast|reinterpret_cast|typeid|template|explicit|true|false|typename|break|continue|return|private|protected|public"""
# reserved words: inc n1, but ignore following "()" pairs, i.e. don't inc n1!
RESPAREN  = r"""for|if|switch|while|catch"""
# reserved words: inc n1, but ignore following ":"
RESCOLN   = r"""case|default"""

# reserved operators requiring special handling in the OperatorCounter_XX classes:
RES_ALL   = SCSPEC+"|"+TYPE_QUAL+"|"+RESERVED+"|"+RESPAREN+"|"+RESCOLN

OPERANDS  = r"""\b\w+\b|\".*\"|\'.+\'"""
# ------------------------------------------------------------------------------
# todo: regex strings for C# and Java
# ------------------------------------------------------------------------------

class Plugin(api.Plugin,
             api.IConfigurable,
             api.Child,
             api.MetricPluginMixin):

    def declare_configuration(self, parser):
        parser.add_option("--ext.halstead.all", "--ehall", action="store_true", default=False,
            help="Halstead metrics plugin: all metrics are calculated [default: %default]")
        parser.add_option("--ext.halstead.base", "--ehbase", action="store_true", default=False,
            help="Halstead metrics plugin: base metrics n1,n2,N1,N2 [default: %default]")

    def configure(self, options):
        self.is_active_eha = options.__dict__['ext.halstead.all']
        self.is_active_ehb = options.__dict__['ext.halstead.base'] or self.is_active_eha

    def initialize(self):
        # ----------------------------------------------------------------------
        # Basic halstead metrics - n1,N1,n2,N2:
        # ----------------------------------------------------------------------
        operator_pattern_cpp = re.compile(
            r"(\b("+SCSPEC+"|"+TYPE_QUAL+"|"+RESERVED+
#               "|"+RESPAREN+"|"+RESCOLN+       for convenience: don't count the identifiers itself but subsequent "()" or ":"
            r")\b|"+OPERATORS+"|"+PARENS+")")
        operator_pattern_cs   = operator_pattern_cpp
        operator_pattern_java = operator_pattern_cpp
        operator_pattern_search = re.compile(r'''[\+\-\*\/\=]''')    # common operators
        self.declare_metric(self.is_active_ehb,
                            self.Field('N1', int,
                                non_zero=True),
                            {
                             'std.code.java': (operator_pattern_java, self.OperatorCounter_N1),
                             'std.code.cpp':  (operator_pattern_cpp, self.OperatorCounter_N1),
                             'std.code.cs':   (operator_pattern_cs, self.OperatorCounter_N1),
                             '*': operator_pattern_search
                            },
                            marker_type_mask=api.Marker.T.CODE,
                            region_type_mask=api.Region.T.ANY)

        operator_pattern_cpp = re.compile(
            r"(\b("+SCSPEC+"|"+TYPE_QUAL+"|"+RESERVED+
                "|"+RESPAREN+"|"+RESCOLN+
            r")\b|"+OPERATORS+"|"+PARENS+")")
        operator_pattern_cs   = operator_pattern_cpp
        operator_pattern_java = operator_pattern_cpp
        self.declare_metric(self.is_active_ehb,
                            self.Field('_n1', int,
                                non_zero=True),
                            {
                             'std.code.java': (operator_pattern_java, self.OperatorCounter_n1),
                             'std.code.cpp':  (operator_pattern_cpp,  self.OperatorCounter_n1),
                             'std.code.cs':   (operator_pattern_cs,   self.OperatorCounter_n1),
                             '*': operator_pattern_search
                            },
                            marker_type_mask=api.Marker.T.CODE,
                            region_type_mask=api.Region.T.ANY)

        operand_pattern_search = re.compile(r"("+OPERANDS+")")
        operand_pattern_java   = operand_pattern_search
        operand_pattern_cpp    = operand_pattern_search
        operand_pattern_cs     = operand_pattern_search
        self.declare_metric(self.is_active_ehb,
                            self.Field('N2', int,
                                non_zero=True),
                            {
                             'std.code.java': (operand_pattern_java, self.OperandCounter_N2),
                             'std.code.cpp':  (operand_pattern_cpp,  self.OperandCounter_N2),
                             'std.code.cs':   (operand_pattern_cs,   self.OperandCounter_N2),
                             '*': operand_pattern_search
                            },
                            marker_type_mask=api.Marker.T.CODE+api.Marker.T.STRING,
                            region_type_mask=api.Region.T.ANY)

        self.declare_metric(self.is_active_ehb,
                            self.Field('_n2', int,
                                non_zero=True),
                            {
                             'std.code.java': (operand_pattern_java, self.OperandCounter_n2),
                             'std.code.cpp':  (operand_pattern_cpp,  self.OperandCounter_n2),
                             'std.code.cs':   (operand_pattern_cs,   self.OperandCounter_n2),
                             '*': operand_pattern_search
                            },
                            marker_type_mask=api.Marker.T.CODE+api.Marker.T.STRING,
                            region_type_mask=api.Region.T.ANY)

        super(Plugin, self).initialize(fields=self.get_fields())

        if self.is_active() == True:
            self.subscribe_by_parents_interface(api.ICode)
            #print("Hello world")

    # --------------------------------------------------------------------------
    # classes to calculate basic halstead metrics n1,N1,n2,N2:
    # --------------------------------------------------------------------------
    class OperatorCounter_N1(api.MetricPluginMixin.IterIncrementCounter):
        """ Number of Operators """
        def __init__(self, *args, **kwargs):
            super(Plugin.OperatorCounter_N1, self).__init__(*args, **kwargs)

        def increment(self, match):
            if match.group(0) in ['}',']',')']:
                result = 0
            else:
                result = 1
#            print("Increment: >"+match.group(0)+"< - "+str(result))
            return result

    class OperatorCounter_n1(api.MetricPluginMixin.IterIncrementCounter):
        """ Number of unique Operators """
        def __init__(self, *args, **kwargs):
            super(Plugin.OperatorCounter_n1, self).__init__(*args, **kwargs)
            self.operator_list = []
            self.ignore = ""

        def increment(self, match):
            if match.group(0) in self.operator_list or match.group(0) in ['}',']',')'] or match.group(0) == self.ignore:
                self.ignore = "";
                result = 0
            else:
                self.operator_list.append(match.group(0))
                result = 1

            if re.match("("+RESPAREN+")",match.group(0)):
                self.ignore = "(";
            elif re.match("("+RESCOLN+")",match.group(0)):
                self.ignore = ":";

#            if result == 1:
#                print("Increment: >"+match.group(0)+"< - "+str(result))
            return result

    class OperandCounter_N2(api.MetricPluginMixin.IterIncrementCounter):
        """ Number of Operands """
        def __init__(self, *args, **kwargs):
            super(Plugin.OperandCounter_N2, self).__init__(*args, **kwargs)

        def increment(self, match):
            if re.match("("+RES_ALL+")",match.group(0)):
                result = 0
            else:
                result = 1
#                print("Increment: >"+match.group(0)+"<"+" - "+str(result
            return result

    class OperandCounter_n2(api.MetricPluginMixin.IterIncrementCounter):
        """ Number of unique Operands """
        def __init__(self, *args, **kwargs):
            super(Plugin.OperandCounter_n2, self).__init__(*args, **kwargs)
            self.operand_list = []

        def increment(self, match):
            if match.group(0) in self.operand_list or re.match("("+RES_ALL+")",match.group(0)):
                result = 0
            else:
                self.operand_list.append(match.group(0))
                result = 1
#                print("Increment: >"+match.group(0)+"<"+" - "+str(result))
            return result
