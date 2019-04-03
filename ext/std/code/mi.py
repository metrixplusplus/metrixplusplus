#
#    Metrix++, Copyright 2009-2013, Metrix++ Project
#    Link: http://metrixplusplus.sourceforge.net
#    
#    This file is a part of Metrix++ Tool.
#    
#    Metrix++ is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3 of the License.
#    
#    Metrix++ is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with Metrix++.  If not, see <http://www.gnu.org/licenses/>.
#

import mpp.api

class Plugin(mpp.api.Plugin,
             mpp.api.IConfigurable,
             mpp.api.Child,
             mpp.api.MetricPluginMixin):
    
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
                            marker_type_mask=mpp.api.Marker.T.NONE)
        
        super(Plugin, self).initialize(fields=self.get_fields())

        if self.is_active() == True:
            self.subscribe_by_parents_name('std.code.complexity')
            self.subscribe_by_parents_name('std.code.lines')

    class RankedComplexityCounter(mpp.api.MetricPluginMixin.RankedCounter):
        rank_source = ('std.code.complexity', 'cyclomatic')
        rank_ranges = [(None, 7), (8, 11), (12, 19), (20, 49), (50, None)]
    
    class RankedLinesCounter(mpp.api.MetricPluginMixin.RankedCounter):
        rank_source = ('std.code.lines', 'code')
        rank_ranges = [(None, 124), (125, 249), (250, 499), (500, 999), (1000, None)]
