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
        parser.add_option("--std.code.ratio.comments", "--scrc", action="store_true", default=False,
                         help="Enables collection of comment ratio metric (per region detalization) - "
                         "ratio of non-empty lines of comments to non-empty lines of (code + comments)."
                         " It uses std.code.lines.code, std.code.lines.comments"
                         " metrics to calculate the ratio."
                         " [default: %default]")

    def configure(self, options):
        self.is_active_ratiocomments = options.__dict__['std.code.ratio.comments']
        if self.is_active_ratiocomments == True:
            required_opts = ['std.code.lines.comments', 'std.code.lines.code']
            for each in required_opts:
                if options.__dict__[each] == False:
                    self.parser.error('option --std.code.ratio.comments: requires --{0} option'.
                                      format(each))

    def initialize(self):
        self.declare_metric(self.is_active_ratiocomments,
                            self.Field('comments', float),
                            {
                             'std.code.lines':(None, self.RatioCalculatorCounter)
                            },
                            # set none, because this plugin is not interested in parsing the code
                            marker_type_mask=api.Marker.T.NONE)

        super(Plugin, self).initialize(fields=self.get_fields())

        if self.is_active() == True:
            self.subscribe_by_parents_name('std.code.lines')

    class RatioCalculatorCounter(api.MetricPluginMixin.RatioCalculator):
        ratio_comments = ('std.code.lines', 'comments')
        ratio_code = ('std.code.lines', 'code')
