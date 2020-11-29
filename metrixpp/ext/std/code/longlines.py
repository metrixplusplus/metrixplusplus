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
        parser.add_option("--std.code.longlines", "--scll",
            action="store_true", default=False,
            help="Enables collection of long lines metric [default: %default]")
        parser.add_option("--std.code.longlines.limit", "--sclll",
            default=80,
            help="Modifies the limit for maximum line-length [default: %default]")

    def configure(self, options):
        self.is_active_ll = options.__dict__['std.code.longlines']
        self.threshold = int(options.__dict__['std.code.longlines.limit'])

    def initialize(self):
        pattern_to_search = r'''.{%s,}''' % (self.threshold + 1)
        self.declare_metric(
                self.is_active_ll,
                self.Field('numbers', int, non_zero=True),
                re.compile(pattern_to_search),
                marker_type_mask=api.Marker.T.CODE,
                region_type_mask=api.Region.T.ANY,
                exclude_subregions=True)

        super(Plugin, self).initialize(fields=self.get_fields())

        if self.is_active_ll == True:
            self.subscribe_by_parents_interface(api.ICode)

