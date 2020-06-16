#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

from metrixpp.mpp import api

class Plugin(api.Plugin,
             api.IConfigurable,
             api.Child,
             api.MetricPluginMixin):
    
    def declare_configuration(self, parser):
        self.parser = parser
        parser.add_option("--std.code.maintindex.simple", "--scmis",
            action="store_true", default=False,
            help="Enables collection of simple maintainability index metric."
             " It uses std.code.line:code, std.code.complexity:cyclomatic"
             " metrics to rank level of maintainability."
             " Lower value of this metric indicates better maintainability."
             " [default: %default]")

    def configure(self, options):
        self.is_active_simple = options.__dict__['std.code.maintindex.simple']
        if self.is_active_simple == True:
            required_opts = ['std.code.complexity.cyclomatic', 'std.code.lines.code']
            for each in required_opts:
                if options.__dict__[each] == False:
                    self.parser.error('option --std.code.maintindex.simple: requires --{0} option'.
                                      format(each))
    
    def initialize(self):
        self.declare_metric(self.is_active_simple,
                            self.Field('simple', int),
                            {
                             'std.code.complexity':(None, self.RankedComplexityCounter),
                             'std.code.lines':(None, self.RankedLinesCounter),
                            },
                            # set none, because this plugin is not interested in parsing the code
                            marker_type_mask=api.Marker.T.NONE)
        
        super(Plugin, self).initialize(fields=self.get_fields())

        if self.is_active() == True:
            self.subscribe_by_parents_name('std.code.complexity')
            self.subscribe_by_parents_name('std.code.lines')

    class RankedComplexityCounter(api.MetricPluginMixin.RankedCounter):
        rank_source = ('std.code.complexity', 'cyclomatic')
        rank_ranges = [(None, 7), (8, 11), (12, 19), (20, 49), (50, None)]
    
    class RankedLinesCounter(api.MetricPluginMixin.RankedCounter):
        rank_source = ('std.code.lines', 'code')
        rank_ranges = [(None, 124), (125, 249), (250, 499), (500, 999), (1000, None)]
