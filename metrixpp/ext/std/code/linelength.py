#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#
#    This file is a part of Metrix++ Tool.
#

from metrixpp.mpp import api
import re

class Plugin(api.Plugin,
             api.IConfigurable,
             api.Child,
             api.MetricPluginMixin):

    def declare_configuration(self, parser):
        parser.add_option("--std.code.linelength", "--scll",
            action="store_true", default=False,
            help="Enables collection of maximum line-length overruns [default: %default]")
        parser.add_option("--std.code.linelength.limit", "--sclll",
            default=80,
            help="Modifies the limit for maximum line-length [default: %default]")

    def configure(self, options):
        self.is_active_ll = options.__dict__['std.code.linelength']
        self.threshold = int(options.__dict__['std.code.linelength.limit'])

    def initialize(self):
        pattern_to_search = r'''.{%s,}''' % (self.threshold + 1)
        self.declare_metric(
                self.is_active_ll,
                self.Field('numbers', int),
                re.compile(pattern_to_search),
                marker_type_mask=api.Marker.T.CODE,
                region_type_mask=api.Region.T.ANY,
                exclude_subregions=True)

        super(Plugin, self).initialize(fields=self.get_fields())

        if self.is_active_ll == True:
            self.subscribe_by_parents_interface(api.ICode)

