# -*- coding: utf-8 -*-
#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#
#    This file is a part of Metrix++ Tool.
#
""" @file
Implements Halstead advanced metrics
@package HalsteadAdvancedMetrics
Halstead advanced metrics:
- uses basic N1,n1,N2,n2 values from halstead_base
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

## @brief Work around for Python 2.7: math.log2 not available
def log2(x): return math.log2(x) if hasattr(math,"log2") else math.log(x,2)

class Plugin(api.Plugin,
             api.IConfigurable,
             api.Child,
             api.MetricPluginMixin):

    opt_prefix = 'std.code.halstead.'   # same as defined in halstead_base.py!

    def declare_configuration(self, parser):
        def add_option(opt1,opt2,action,default,help):
            parser.add_option("--"+self.opt_prefix+opt1, "--sch"+opt2, action=action, default=default,
                help=help)

        add_option("vocabulary", "voc", action="store_true", default=False,
            help="Halstead metrics plugin: vocabulary 'n' [default: %default]")
        add_option("length", "len", action="store_true", default=False,
            help="Halstead metrics plugin: program length 'N' [default: %default]")
        add_option("estimatedlength", "elen", action="store_true", default=False,
            help="Halstead metrics plugin: estimated program length [default: %default]")
        add_option("purityratio", "pr", action="store_true", default=False,
            help="Halstead metrics plugin: purity ratio [default: %default]")
        add_option("volume", "v", action="store_true", default=False,
            help="Halstead metrics plugin: program volume [default: %default]")
        add_option("difficulty", "d", action="store_true", default=False,
            help="Halstead metrics plugin: program difficulty [default: %default]")
        add_option("level", "l", action="store_true", default=False,
            help="Halstead metrics plugin: program level [default: %default]")
        add_option("effort", "e", action="store_true", default=False,
            help="Halstead metrics plugin: program effort [default: %default]")
        add_option("time", "t", action="store_true", default=False,
            help="Halstead metrics plugin: estimated time [default: %default]")
        add_option("bugs", "b", action="store_true", default=False,
            help="Halstead metrics plugin: delivered bugs [default: %default]")

    def configure(self, options):
        self.is_active_aha = options.__dict__[self.opt_prefix+'all']
        self.is_active_ahn = options.__dict__[self.opt_prefix+'vocabulary']    \
            or self.is_active_aha
        self.is_active_ahN = options.__dict__[self.opt_prefix+'length']        \
            or self.is_active_aha
        self.is_active_ah_N = options.__dict__[self.opt_prefix+'estimatedlength']   \
            or self.is_active_aha
        self.is_active_ahpr = options.__dict__[self.opt_prefix+'purityratio']   \
            or self.is_active_aha
        self.is_active_ahV = options.__dict__[self.opt_prefix+'volume']        \
            or self.is_active_aha
        self.is_active_ahD = options.__dict__[self.opt_prefix+'difficulty']    \
            or self.is_active_aha
        self.is_active_ahL = options.__dict__[self.opt_prefix+'level']         \
            or self.is_active_aha
        self.is_active_ahE = options.__dict__[self.opt_prefix+'effort']        \
            or self.is_active_aha
        self.is_active_ahT = options.__dict__[self.opt_prefix+'time']          \
            or self.is_active_aha
        self.is_active_ahB = options.__dict__[self.opt_prefix+'bugs']          \
            or self.is_active_aha
        self.is_active_ahb = options.__dict__[self.opt_prefix+'base']          \
            or self.is_active_ahn   \
            or self.is_active_ahN   \
            or self.is_active_ah_N  \
            or self.is_active_ahpr  \
            or self.is_active_ahV   \
            or self.is_active_ahD   \
            or self.is_active_ahL   \
            or self.is_active_ahE   \
            or self.is_active_ahT   \
            or self.is_active_ahB   \

        if self.is_active_ahb:
            req_or = False
            required_opts = [self.opt_prefix+'all',
                             self.opt_prefix+'base']
            for each in required_opts:
                if options.__dict__[each] == True:
                    req_or = True
                    break
            if ( req_or == False ):
                self.parser.error('option --'+self.opt_prefix+'*: requires --'+self.opt_prefix+'all or --'+self.opt_prefix+'base option')

    def initialize(self):
        # ----------------------------------------------------------------------
        # Advanced halstead metrics:
        # ----------------------------------------------------------------------
        self.declare_metric(self.is_active_ahN,
                            self.Field('H_Length', int),
                            {
                             '*':(None, self.HalsteadProgramLength)
                            },
                            marker_type_mask=api.Marker.T.NONE)
        self.declare_metric(self.is_active_ah_N,
                            self.Field('H_EstLength', float),
                            {
                             '*':(None, self.HalsteadEstimatedLength)
                            },
                            marker_type_mask=api.Marker.T.NONE)
        self.declare_metric(self.is_active_ahpr,
                            self.Field('H_PurityRatio', float),
                            {
                             '*':(None, self.HalsteadPurityRatio)
                            },
                            marker_type_mask=api.Marker.T.NONE)
        self.declare_metric(self.is_active_ahn,
                            self.Field('H_Vocabulary', int),
                            {
                             '*':(None, self.HalsteadVocabulary)
                            },
                            marker_type_mask=api.Marker.T.NONE)
        self.declare_metric(self.is_active_ahV,
                            self.Field('H_Volume', float),
                            {
                             '*':(None, self.HalsteadVolume)
                            },
                            marker_type_mask=api.Marker.T.NONE)
        self.declare_metric(self.is_active_ahD,
                            self.Field('H_Difficulty', float),
                            {
                             '*':(None, self.HalsteadDifficulty)
                            },
                            marker_type_mask=api.Marker.T.NONE)
        self.declare_metric(self.is_active_ahL,
                            self.Field('H_Level', float),
                            {
                             '*':(None, self.HalsteadProgramLevel)
                            },
                            marker_type_mask=api.Marker.T.NONE)
        self.declare_metric(self.is_active_ahE,
                            self.Field('H_Effort', float),
                            {
                             '*':(None, self.HalsteadImplementationEffort)
                            },
                            marker_type_mask=api.Marker.T.NONE)
        self.declare_metric(self.is_active_ahT,
                            self.Field('H_Time', float),
                            {
                             '*':(None, self.HalsteadImplementationTime)
                            },
                            marker_type_mask=api.Marker.T.NONE)
        self.declare_metric(self.is_active_ahB,
                            self.Field('H_Bugs', float),
                            {
                             '*':(None, self.HalsteadDeliveredBugs)
                            },
                            marker_type_mask=api.Marker.T.NONE)

        super(Plugin, self).initialize(fields=self.get_fields(), support_regions=True)

        if self.is_active():
            self.subscribe_by_parents_interface(api.ICode)

    # --------------------------------------------------------------------------
    # classes to calculate advanced halstead metrics:
    # --------------------------------------------------------------------------
    class HalsteadCalculator(api.MetricPluginMixin.PlainCounter):
        """ Base class to obtain basic metrics N1,n1,N2,n2.
            Additionally provides calculation for all Hallstead values
        """
        def __init__(self, *args, **kwargs):
            super(Plugin.HalsteadCalculator, self).__init__(*args, **kwargs)
            self.result = self.region.get_data(self.namespace, self.field)
            if self.result == None:
                self.result = 0

        def get_HalsteadFields(self):
            """ Helper function to obtain basic metrics N1,n1,N2,n2.
                Additionally obtains N = N1+N2 and n = n1+n2.
            """
            self.N1 = self.region.get_data('std.code.halstead_base', 'N1')
            self.n1 = self.region.get_data('std.code.halstead_base', '_n1')
            self.N2 = self.region.get_data('std.code.halstead_base', 'N2')
            self.n2 = self.region.get_data('std.code.halstead_base', '_n2')
            if ( (self.n1 == None) or (self.n2 == None) or (self.N1 == None) or (self.N2 == None) ):
                self.N = 0
                self.n = 0
                #print("HalsteadFields: none")
                return False
            else:
                self.N = self.N1+self.N2
                self.n = self.n1+self.n2
                #print("HalsteadFields: "+str(self.N1)+" / "+str(self.n1)+" / "+str(self.N2)+" / "+str(self.n2))
                return True

        ## @name Helper functions:
        # It's up to the caller to first call @ref self.get_HalsteadFields() to obtain
        # valid N1,n1,N2,n2, N and n values!
        # @{
        def get_EstimatedProgramLength(self):
            """ Estimated program length eLen = n1*log2(n1) + n2*log2(n2) """
            if (self.n1 > 0) and (self.n2 > 0):
                return self.n1*log2(self.n1)+self.n2*log2(self.n2)
            else:
                return 0.0

        def get_PurityRatio(self):
            """ Purity ratio PR = eLen/N """
            if self.N != 0:
                return self.get_EstimatedProgramLength()/self.N
            else:
                return 0.0

        def get_ProgramVolume(self):
            """ Program volume V = N * log2(n) """
            if self.n > 0:
                return self.N * log2(self.n) # Python 2.7: log2 not available
            else:
                return 0.0

            return self.result

        def get_ProgramDifficulty(self):
            """ Program difficulty D = n1*N2 / (2*n2) """
            if self.n2 != 0:
                return (self.n1*self.N2) / (2.0*self.n2)
            else:
                return 0.0

        def get_ProgramLevel(self):
            """ Program level L = 1/D = 2*n2 / (n1*N2) """
            if (self.n1*self.N2) != 0:
                return (2.0*self.n2) / (self.n1*self.N2)
            else:
                return 0.0

        def get_ImplementationEffort(self):
            """ Implementation effort E = V*D = N*log2(n) * n1*N2 / (2*n2) """
            return self.get_ProgramVolume()*self.get_ProgramDifficulty()

        def get_ImplementationTime(self):
            """ Implementation time T[sec] = E / 18
                The implementation effort "E" is interpreted as the program's
                information content in bit which may be interpreted as elementary
                YES/NO-decisions. "18" is the so called "Stroud number" which
                determines the number of elementary decisions / sec a human brain
                can make. The psychologist John M. Stroud has figured out that
                this is between 5 and 25. Halstead chooses 18 as a good value
                for software engineers...
            """
            return self.get_ImplementationEffort() / 18.0

        def get_EstimatedDeliveredBugs(self):
            """ Estimated delivered bugs B = E^(2/3) / 3000 """
            return self.get_ImplementationEffort()**(2.0/3.0) / 3000.0
        # @}

    # --------------------------------------------------------------------------
    class HalsteadProgramLength(HalsteadCalculator):
        """ Program length N = N1+N2 """
        def get_result(self):
            if self.get_HalsteadFields():
                self.result = self.N
            else:
                self.result = 0

            return self.result

    class HalsteadEstimatedLength(HalsteadCalculator):
        """ Estimated program length eLen = n1*log2(n1) + n2*log2(n2) """
        def get_result(self):
            if self.get_HalsteadFields():
                self.result = self.get_EstimatedProgramLength()
            else:
                self.result = 0.0

            return self.result

    class HalsteadPurityRatio(HalsteadCalculator):
        """ Purity ratio PR = eLen/N """
        def get_result(self):
            if self.get_HalsteadFields():
                self.result = self.get_PurityRatio()
            else:
                self.result = 0.0

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
            if self.get_HalsteadFields():
                self.result = self.get_ProgramVolume()
            else:
                self.result = 0.0

            return self.result

    class HalsteadDifficulty(HalsteadCalculator):
        """ Program difficulty D = n1*N2 / (2*n2) """
        def get_result(self):
            if self.get_HalsteadFields():
                self.result = self.get_ProgramDifficulty()
            else:
                self.result = 0.0

            return self.result

    class HalsteadProgramLevel(HalsteadCalculator):
        """ Program level L = 1/D = 2*n2 / (n1*N2) """
        def get_result(self):
            if self.get_HalsteadFields():
                self.result = self.get_ProgramLevel()
            else:
                self.result = 0.0

            return self.result

    class HalsteadImplementationEffort(HalsteadCalculator):
        """ Implementation effort E = V*D = N*log2(n) * n1*N2 / (2*n2) """
        def get_result(self):
            if self.get_HalsteadFields():
                self.result = self.get_ImplementationEffort()
            else:
                self.result = 0.0

            return self.result

    # --------------------------------------------------------------------------
    # some more advanced halstead metrics based on implementation effort E:
    # --------------------------------------------------------------------------
    class HalsteadImplementationTime(HalsteadCalculator):
        """ Implementation time T[sec] = E / 18 """
        def get_result(self):
            """ Note that originally T is given in seconds; but this seems not very
                handy esp. for large projects; so here it's calculated in hours.
            """
            if self.get_HalsteadFields():
                self.result = self.get_ImplementationTime() / 3600.0
            else:
                self.result = 0.0

            return self.result

    class HalsteadDeliveredBugs(HalsteadCalculator):
        """ Delivered bugs B = E^(2/3) / 3000 """
        def get_result(self):
            if self.get_HalsteadFields():
                self.result = self.get_EstimatedDeliveredBugs()
            else:
                self.result = 0.0

            return self.result
