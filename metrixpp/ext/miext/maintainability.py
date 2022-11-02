# -*- coding: utf-8 -*-
#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#
#    This file is a part of Metrix++ Tool.
#

"""
Implements Oman's maintainability metrics:

An overview is found on https://www.verifysoft.com/en_maintainability.html

A discussion of software metrics (esp. Halstead and Oman): https://core.ac.uk/download/pdf/216048382.pdf
and http://web.archive.org/web/20021120101304/http://www.stsc.hill.af.mil/crosstalk/2001/08/welker.html

A detailed explanation with example is found on http://www.verifysoft.com/de_cmtpp_mscoder.pdf (german)
"""

from metrixpp.mpp import api
import math

class Plugin(api.Plugin,
             api.IConfigurable,
             api.Child,
             api.MetricPluginMixin):

    def declare_configuration(self, parser):
        self.parser = parser
        parser.add_option("--ext.mi_oman.all", "--emoa", action="store_true", default=False,
            help="Maintainability metrics plugin; the following modules are required: "
                 "--std.code.lines.comments, "
                 "--std.code.lines.total, "
                 "--std.code.complexity.cyclomatic, "
                 "and either --ext.halstead.all or --ext.halstead.volume "
                 "[default: %default]")

    def configure(self, options):
        self.is_active_oman = options.__dict__['ext.mi_oman.all']
        if self.is_active_oman == True:
            required_opts = ['std.code.complexity.cyclomatic',
                             'std.code.lines.comments',
                             'std.code.lines.total']
            for each in required_opts:
                if options.__dict__[each] == False:
                    self.parser.error('option --ext.mi_oman.all: requires --{0} option'.
                                      format(each))
            req_or = False
            required_opts = ['ext.halstead.all',
                             'ext.halstead.volume']
            for each in required_opts:
                if options.__dict__[each] == True:
                    req_or = True
                    break
            if ( req_or == False ):
                self.parser.error('option --ext.mi_oman.all: requires --ext.halstead.all or --ext.halstead.volume option')

    def initialize(self):

        self.declare_metric(self.is_active_oman,
                            self.Field('perCM', float),
                            {
                             '*':(None, self.Oman_perCM)
                            },
                            marker_type_mask=api.Marker.T.NONE)
        self.declare_metric(self.is_active_oman,
                            self.Field('MIwoc', float),
                            {
                             '*':(None, self.Oman_MIwoc)
                            },
                            marker_type_mask=api.Marker.T.NONE)
        self.declare_metric(self.is_active_oman,
                            self.Field('MIcw', float),
                            {
                             '*':(None, self.Oman_MIcw)
                            },
                            marker_type_mask=api.Marker.T.NONE)
        self.declare_metric(self.is_active_oman,
                            self.Field('MIsum', float),
                            {
                             '*':(None, self.Oman_MIsum)
                            },
                            marker_type_mask=api.Marker.T.NONE)

        super(Plugin, self).initialize(fields=self.get_fields())

        if self.is_active() == True:
            self.subscribe_by_parents_interface(api.ICode)
#            print("Hello world")

    class OmanCalculator(api.MetricPluginMixin.PlainCounter):
        def __init__(self, *args, **kwargs):
            super(Plugin.OmanCalculator, self).__init__(*args, **kwargs)
            self.result = self.region.get_data(self.namespace, self.field)
            if self.result == None:
                self.result = 0

        """ Helper functions to obtain metrics """
        def get_OmanFields(self):
            """ get database fields """
            self.LOCcom  = self.region.get_data('std.code.lines', 'comments')
            self.LOCphy  = self.region.get_data('std.code.lines', 'total')
            # average values: since we are on a per module basis these are the
            # module based values:
            self.aveG = self.region.get_data('std.code.complexity', 'cyclomatic')
            self.aveV = self.region.get_data('miext.halstead', 'H_Volume')
            self.aveLOC = self.LOCphy

            return ( (self.LOCcom != None) and (self.LOCphy != None)
                 and (self.aveG != None)and (self.aveV != None) )

        def get_perCM(self):
            """ average percent of lines of comments per Module perCM = LOCcom/aveLOC
                where aveLOC = total physical number of lines
            """
            if self.get_OmanFields():
                if self.aveLOC != 0:
                    return float(self.LOCcom)/float(self.aveLOC)   # explicit float due to Python 2.7 restrictions
            return 0.0

        def get_MIwoc(self):
            """ Maintainability Index without comments
                MIwoc = 171 - 5.2 * ln(aveV) - 0.23 * aveG -16.2 * ln(aveLOC)
            """
            if self.get_OmanFields():
                ln_aveV = 0.0
                if ( self.aveV > 0.0 ):
                    ln_aveV = math.log(self.aveV)
                ln_aveLOC = 0.0
                if ( self.aveLOC > 0.0 ):
                    ln_aveLOC = math.log(self.aveLOC)
                return 171.0            \
                     - 5.2 * ln_aveV    \
                     - 0.23 * self.aveG \
                     - 16.2 * ln_aveLOC
            return 0.0

        def get_MIcw(self):
            """ Maintainability Index comment weight MIcw = 50 * sin(Pi/2*sqrt(perCM))
                Note that this often is given as MIcw = 50 * sin(sqrt(2.46 * perCM))
                which in fact is the same since 2.46 = (Pi/2)²
            """
            return 50.0 * math.sin((math.pi/2.0) * math.sqrt(self.get_perCM()))


    class Oman_perCM(OmanCalculator):
        """ average percent of lines of comments per Module
            Not that this metric is saved as percentage
        """
        def get_result(self):
            self.result = self.get_perCM()*100.0
            return self.result

    class Oman_MIwoc(OmanCalculator):
        """ Maintainability Index without comments """
        def get_result(self):
            self.result = self.get_MIwoc()
            return self.result

    class Oman_MIcw(OmanCalculator):
        """ Maintainability Index comment weight """
        def get_result(self):
            self.result = self.get_MIcw()
            return self.result

    class Oman_MIsum(OmanCalculator):
        """ Maintainability Index = MIwoc + MIcw """
        def get_result(self):
            self.result = self.get_MIwoc() + self.get_MIcw()
            return self.result
