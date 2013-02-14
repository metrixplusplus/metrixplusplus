'''
Created on 26/06/2012

@author: konstaa
'''

import core.api

import re

class Plugin(core.api.Plugin, core.api.Child, core.api.IConfigurable):
    
    POST_NAME = '.ss.std.code.dumper.html'
    
    def declare_configuration(self, parser):
        parser.add_option("--std.code.dumper.on", action="store_true", default=False,
                         help="If the option is set (True), HTML files are generated for every parsed file containing code (for troubleshooting purposes only) [default: %default]")
    
    def configure(self, options):
        self.dump_html = options.__dict__['std.code.dumper.on']
        
    def initialize(self):
        if self.dump_html == True:
            core.api.subscribe_by_parents_interface(core.api.ICode, self)
        
        # do not process files dumped by previous run of this module    
        self.get_plugin_loader().get_plugin('core.dir').add_exclude_rule(re.compile(r'.*' + Plugin.POST_NAME + r'$'))
        
    def callback(self, parent, data):
        file_name = data.get_path()
        text = data.get_content()
        
        import cgi
        f = open(file_name + Plugin.POST_NAME, 'w')
        f.write('<html><body><table><tr><td><pre>')
        last_pos = 0
        for marker in data.iterate_markers():
            f.write(cgi.escape(text[last_pos:marker.begin]))
            if marker.get_type() == data.get_marker_types().STRING:
                f.write('<span style="color:#0000FF">')
            elif marker.get_type() == data.get_marker_types().COMMENT:
                f.write('<span style="color:#009900">')
            elif marker.get_type() == data.get_marker_types().PREPROCESSOR:
                f.write('<span style="color:#990000">')
            f.write(cgi.escape(text[marker.begin:marker.end]))
            f.write('</span>')
            last_pos = marker.end
        f.write(cgi.escape(text[last_pos:]))
        last_pos = 0
        f.write('</pre></td><td><pre>')
        styles = ['<span style="background-color:#ffff80">', '<span style="background-color:#ff80ff">']
        for item in enumerate(data.iterate_regions(filter_group=data.get_region_types().FUNCTION)):
            reg = item[1]
            f.write(cgi.escape(text[last_pos:reg.get_offset_begin()]))
            f.write(styles[item[0] % 2])
            f.write('<a href="#line' + str(reg.get_cursor()) + '" id=line"' + str(reg.get_cursor()) + '"></a>')
            f.write(cgi.escape(text[reg.get_offset_begin():reg.get_offset_end()]))
            f.write('</span>')
            last_pos = reg.get_offset_end()
        f.write(cgi.escape(text[last_pos:]))
        f.write('</pre></td></tr></table></body></html>')
        f.close()

