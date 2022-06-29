# -*- coding: utf-8 -*-
#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#
#    This file is a part of Metrix++ Tool.
#
"""
Implements Halstead metrics:
- uses basic n1,n2,N1,N2 values from halstead_base
- calculates advanced metrics:
  - program length N
  - vocabulary n
  - program volume V
  - difficulty level D
  - program level L
  - implementation effort E
  - implementation time T
  - delivered bugs B

Note that we can assume the file to be analyzed is syntactically correct;
this should be true especially for correct parentheses' pairing!

An overview is found on https://www.verifysoft.com/en_halstead_metrics.html

A discussion of software metrics (esp. Halstead and Oman): https://core.ac.uk/download/pdf/216048382.pdf

A detailed explanation with example is found on http://www.verifysoft.com/de_cmtpp_mscoder.pdf (german)
"""

from metrixpp.mpp import api
import math

class Plugin(api.Plugin,
             api.IConfigurable,
             api.Child,
             api.MetricPluginMixin):

    def declare_configuration(self, parser):
        parser.add_option("--ext.halstead.vocabulary", "--ehvoc", action="store_true", default=False,
            help="Halstead metrics plugin: vocabulary 'n' [default: %default]")
        parser.add_option("--ext.halstead.length", "--ehlen", action="store_true", default=False,
            help="Halstead metrics plugin: program length 'N' [default: %default]")
        parser.add_option("--ext.halstead.volume", "--ehv", action="store_true", default=False,
            help="Halstead metrics plugin: program volume [default: %default]")
        parser.add_option("--ext.halstead.difficulty", "--ehd", action="store_true", default=False,
            help="Halstead metrics plugin: program difficulty [default: %default]")
        parser.add_option("--ext.halstead.level", "--ehl", action="store_true", default=False,
            help="Halstead metrics plugin: program level [default: %default]")
        parser.add_option("--ext.halstead.effort", "--ehe", action="store_true", default=False,
            help="Halstead metrics plugin: program effort [default: %default]")
        parser.add_option("--ext.halstead.time", "--eht", action="store_true", default=False,
            help="Halstead metrics plugin: estimated time [default: %default]")
        parser.add_option("--ext.halstead.bugs", "--ehb", action="store_true", default=False,
            help="Halstead metrics plugin: delivered bugs [default: %default]")

    def configure(self, options):
        self.is_active_eha = options.__dict__['ext.halstead.all']
        self.is_active_ehn = options.__dict__['ext.halstead.vocabulary']        \
            or self.is_active_eha
        self.is_active_ehN = options.__dict__['ext.halstead.length']        \
            or self.is_active_eha
        self.is_active_ehV = options.__dict__['ext.halstead.volume']        \
            or self.is_active_eha
        self.is_active_ehD = options.__dict__['ext.halstead.difficulty']    \
            or self.is_active_eha
        self.is_active_ehL = options.__dict__['ext.halstead.level']         \
            or self.is_active_eha
        self.is_active_ehE = options.__dict__['ext.halstead.effort']        \
            or self.is_active_eha
        self.is_active_ehT = options.__dict__['ext.halstead.time']          \
            or self.is_active_eha
        self.is_active_ehB = options.__dict__['ext.halstead.bugs']          \
            or self.is_active_eha
        self.is_active_ehb = options.__dict__['ext.halstead.base']          \
            or self.is_active_ehn \
            or self.is_active_ehN \
            or self.is_active_ehV \
            or self.is_active_ehD \
            or self.is_active_ehL \
            or self.is_active_ehE \
            or self.is_active_ehT \
            or self.is_active_ehB \

        if self.is_active_ehb:
            req_or = False
            required_opts = ['ext.halstead.all',
                             'ext.halstead.base']
            for each in required_opts:
                if options.__dict__[each] == True:
                    req_or = True
                    break
            if ( req_or == False ):
                self.parser.error('option --ext.halstead.*: requires --ext.halstead.all or --ext.halstead.base option')

    def initialize(self):
        # ----------------------------------------------------------------------
        # Advanced halstead metrics:
        # ----------------------------------------------------------------------
        self.declare_metric(self.is_active_ehN,
                            self.Field('H_Length', int),
                            {
                             '*':(None, self.HalsteadProgramLength)
                            },
                            marker_type_mask=api.Marker.T.NONE)
        self.declare_metric(self.is_active_ehn,
                            self.Field('H_Vocabulary', int),
                            {
                             '*':(None, self.HalsteadVocabulary)
                            },
                            marker_type_mask=api.Marker.T.NONE)
        self.declare_metric(self.is_active_ehV,
                            self.Field('H_Volume', float),
                            {
                             '*':(None, self.HalsteadVolume)
                            },
                            marker_type_mask=api.Marker.T.NONE)
        self.declare_metric(self.is_active_ehD,
                            self.Field('H_Difficulty', float),
                            {
                             '*':(None, self.HalsteadDifficulty)
                            },
                            marker_type_mask=api.Marker.T.NONE)
        self.declare_metric(self.is_active_ehL,
                            self.Field('H_Level', float),
                            {
                             '*':(None, self.HalsteadProgramLevel)
                            },
                            marker_type_mask=api.Marker.T.NONE)
        self.declare_metric(self.is_active_ehE,
                            self.Field('H_Effort', float),
                            {
                             '*':(None, self.HalsteadImplementationEffort)
                            },
                            marker_type_mask=api.Marker.T.NONE)
        self.declare_metric(self.is_active_ehT,
                            self.Field('H_Time', float),
                            {
                             '*':(None, self.HalsteadImplementationTime)
                            },
                            marker_type_mask=api.Marker.T.NONE)
        self.declare_metric(self.is_active_ehB,
                            self.Field('H_Bugs', float),
                            {
                             '*':(None, self.HalsteadDeliveredBugs)
                            },
                            marker_type_mask=api.Marker.T.NONE)

        super(Plugin, self).initialize(fields=self.get_fields())

        if self.is_active() == True:
            self.subscribe_by_parents_interface(api.ICode)
#            print("Hello world")

    # --------------------------------------------------------------------------
    # classes to calculate advanced halstead metrics:
    # --------------------------------------------------------------------------
    class HalsteadCalculator(api.MetricPluginMixin.PlainCounter):
        """ Helper class to obtain basic metrics n1,N1,n2,N2.
            Additionally obtains n = n1+n2 and N = N1+N2.
        """
        def __init__(self, *args, **kwargs):
            super(Plugin.HalsteadCalculator, self).__init__(*args, **kwargs)
            self.result = self.region.get_data(self.namespace, self.field)
            if self.result == None:
                self.result = 0

        def get_HalsteadFields(self):
            """ Helper function to obtain basic metrics n1,N1,n2,N2.
                Additionally obtains n = n1+n2 and N = N1+N2.
            """
            self.n1 = self.region.get_data('miext.halstead_base', '_n1')
            self.n2 = self.region.get_data('miext.halstead_base', '_n2')
            self.N1 = self.region.get_data('miext.halstead_base', 'N1')
            self.N2 = self.region.get_data('miext.halstead_base', 'N2')
            if ( (self.n1 == None) or (self.n2 == None) or (self.N1 == None) or (self.N2 == None) ):
                self.N = 0
                self.n = 0
                #print("HalsteadFields: none")
                return False
            else:
                self.N = self.N1+self.N2
                self.n = self.n1+self.n2
                #print("HalsteadFields: "+str(self.N1)+" / "+str(self.N2)+" / "+str(self.n1)+" / "+str(self.n2))
                return True

    class HalsteadProgramLength(HalsteadCalculator):
        """ Program length N = N1+N2 """
        def get_result(self):
            if self.get_HalsteadFields():
                self.result = self.N
            else:
                self.result = 0

            return self.result

    class HalsteadVocabulary(HalsteadCalculator):
        """ Program vocabulary n = n1+n2 """
        def get_result(self):
            if self.get_HalsteadFields():
                self.result = self.n
            else:
                self.result = 0

            return self.result

    class HalsteadVolume(HalsteadCalculator):
        """ Program volume V = N * log2(n) """
        def get_result(self):
            if self.get_HalsteadFields() and ( (self.n > 0) ):
                #self.result = self.N * math.log2(self.n) # Python 2.7: log2 not available
                self.result = self.N * math.log(self.n,2)
            else:
                self.result = 0.0

            return self.result

    class HalsteadDifficulty(HalsteadCalculator):
        """ Program difficulty D = n1*N2 / (2*n2) """
        def get_result(self):
            if self.get_HalsteadFields() and ( (self.n2 != 0) ):
                self.result = (self.n1*self.N2) / (2.0*self.n2)
            else:
                self.result = 0.0

            return self.result

    class HalsteadProgramLevel(HalsteadCalculator):
        """ Program level L = 1/D = 2*n2 / (n1*N2) """
        def get_result(self):
            if self.get_HalsteadFields() and ( ((self.n1*self.N2) != 0) ):
                self.result = (2.0*self.n2) / (self.n1*self.N2)
            else:
                self.result = 0.0

            return self.result

    class HalsteadImplementationEffort(HalsteadCalculator):
        """ Implementation effort E = V*D = N*log2(n) * n1*N2 / (2*n2) """
        def get_result(self):
            if self.get_HalsteadFields() and ( (self.n2 != 0) ):
                #self.result = self.N * math.log2(self.n) * (self.n1*self.N2) / (2*self.n2) # Python 2.7: log2 not available
                self.result = self.N * math.log(self.n,2) * (self.n1*self.N2) / (2.0*self.n2)
            else:
                self.result = 0.0

            return self.result

    # --------------------------------------------------------------------------
    # some more advanced halstead metrics based on implementation effort E:
    # --------------------------------------------------------------------------
    class HalsteadImplementationTime(HalsteadImplementationEffort):
        """ Implementation time T[sec] = E / 18
            The implementation effort "E" is interpreted as the program's
            information content in bit which may be interpreted as elementary
            YES/NO-decisions. "18" is the so called "Stroud number" which
            determines the number of elementary decisions / sec a human brain
            can make and Stroud has figured out that this is between 5 and 25.
            Halstead chooses 18 as a good value for software engineers...
        """
        def get_result(self):
            """ Note that originally T is given in seconds; but this seems not very
                handy esp. for large projects; so here it's calculated in hours.
            """
            self.result = super(Plugin.HalsteadImplementationTime, self).get_result() / (18.0 * 3600.0)

            return self.result

    class HalsteadDeliveredBugs(HalsteadImplementationEffort):
        """ Delivered bugs B = E^(2/3) / 3000 """
        def get_result(self):
            self.result = super(Plugin.HalsteadDeliveredBugs, self).get_result()**(2.0/3.0) / 3000.0

            return self.result
