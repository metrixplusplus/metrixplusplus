#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

from metrixpp.mpp import api
import re

class Plugin(api.Plugin, api.MetricPluginMixin, api.Child, api.IConfigurable):
    
    def declare_configuration(self, parser):
        parser.add_option("--std.code.lines.code", "--sclc", action="store_true", default=False,
                         help="Enables collection of lines of code metric (per region detalization) - "
                         "number of non-empty lines of code, excluding comments "
                         "[default: %default]")
        parser.add_option("--std.code.lines.preprocessor", "--sclp", action="store_true", default=False,
                         help="Enables collection of lines of preprocessor code metric (per region detalization) - "
                         "number of non-empty lines of preprocessor code "
                         "[default: %default]")
        parser.add_option("--std.code.lines.comments", "--sclcom", action="store_true", default=False,
                         help="Enables collection of lines of comments metric (per region detalization) - "
                         "number of non-empty lines of comments "
                         "[default: %default]")
        parser.add_option("--std.code.lines.total", "--sclt", action="store_true", default=False,
                         help="Enables collection of total lines metric (per region detalization) - "
                         "number of any type of lines (blank, code, comments, etc.)"
                         "[default: %default]")
    
    def configure(self, options):
        self.is_active_code = options.__dict__['std.code.lines.code']
        self.is_active_preprocessor = options.__dict__['std.code.lines.preprocessor']
        self.is_active_comments = options.__dict__['std.code.lines.comments']
        self.is_active_total = options.__dict__['std.code.lines.total']
        
    pattern_line = re.compile(r'''[^\s].*''')

    def initialize(self):
        self.declare_metric(self.is_active_code,
                       self.Field('code', int),
                       self.pattern_line,
                       api.Marker.T.CODE | api.Marker.T.STRING,
                       merge_markers=True)
        self.declare_metric(self.is_active_preprocessor,
                       self.Field('preprocessor', int),
                       self.pattern_line,
                       api.Marker.T.PREPROCESSOR)
        self.declare_metric(self.is_active_comments,
                       self.Field('comments', int),
                       self.pattern_line,
                       api.Marker.T.COMMENT)
        self.declare_metric(self.is_active_total,
                       self.Field('total', int),
                       self.pattern_line,
                       api.Marker.T.ANY,
                       merge_markers=True)

        super(Plugin, self).initialize(fields=self.get_fields())

        if self.is_active() == True:
            self.subscribe_by_parents_interface(api.ICode)
