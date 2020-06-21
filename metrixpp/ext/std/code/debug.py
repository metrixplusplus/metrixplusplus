#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

import logging
import cgi

from metrixpp.mpp import api
from metrixpp.mpp import utils

class Plugin(api.Plugin, api.IConfigurable, api.IRunable):
    
    def declare_configuration(self, parser):
        parser.add_option("-m", "--mode", default='dumphtml', choices=['dumphtml'],
                             help="'dumphtml' - prints html code with code highlights for each given path [default: %default]")
    
    def configure(self, options):
        self.mode = options.__dict__['mode']

    def run(self, args):
        loader = self.get_plugin('metrixpp.mpp.dbf').get_loader()
    
        if self.mode == 'dumphtml':
            return dumphtml(args, loader)
        assert(False)

def dumphtml(args, loader):
    exit_code = 0
    result = ""
    result += '<html><body>'
    for path in args:
        path = utils.preprocess_path(path)
        
        data = loader.load_file_data(path)
        if data == None:
            utils.report_bad_path(path)
            exit_code += 1
            continue
        
        file_name = data.get_path()
        fh = open(file_name, 'r')
        if fh == None:
            logging.error("can not open file '" + path + "' for reading")
            exit_code += 1
            continue
        text = fh.read()
        fh.close()
        
        # TODO fix highlightning of markers
#        result += '<table><tr><td><pre>'
#        last_pos = 0
#        for marker in data.iterate_markers(filter_group= api.Marker.T.COMMENT |
#                                           api.Marker.T.STRING |
#                                           api.Marker.T.PREPROCESSOR):
#            result += (cgi.escape(text[last_pos:marker.begin]))
#            if marker.get_type() == api.Marker.T.STRING:
#                result += ('<span style="color:#0000FF">')
#            elif marker.get_type() == api.Marker.T.COMMENT:
#                result += ('<span style="color:#009900">')
#            elif marker.get_type() == api.Marker.T.PREPROCESSOR:
#                result += ('<span style="color:#990000">')
#            else:
#                assert False, "Uknown marker type"
#            result += (cgi.escape(text[marker.begin:marker.end]))
#            result += ('</span>')
#            last_pos = marker.end
#        result += (cgi.escape(text[last_pos:]))
#        result += ('</pre></td><td><pre>')
        result += '<table><tr><td><pre>'
        styles = [('<span style="background-color:#F0F010">',
                  '<span style="background-color:#F010F0">'),
                  ('<span style="background-color:#F0F030">',
                  '<span style="background-color:#F030F0">'),
                  ('<span style="background-color:#F0F050">',
                  '<span style="background-color:#F050F0">'),
                  ('<span style="background-color:#F0F070">',
                  '<span style="background-color:#F070F0">'),
                  ('<span style="background-color:#F0F090">',
                  '<span style="background-color:#F090F0">'),
                  ('<span style="background-color:#F0F0B0">',
                  '<span style="background-color:#F0B0F0">'),
                  ('<span style="background-color:#F0F0D0">',
                  '<span style="background-color:#F0D0F0">'),
                  ('<span style="background-color:#F0F0E0">',
                  '<span style="background-color:#F0E0F0">')]
        
        def proc_rec(region_id, file_data, styles, indent, pos):
            result = (styles[indent % len(styles)][pos % 2])
            region = file_data.get_region(region_id)
            result += ('<a href="#line' + str(region.get_cursor()) + '" id=line"' + str(region.get_cursor()) + '"></a>')
            last_pos = region.get_offset_begin() 
            for (ind, sub_id) in enumerate(file_data.get_region(region_id).iterate_subregion_ids()):
                subregion = file_data.get_region(sub_id)
                result += (cgi.escape(text[last_pos:subregion.get_offset_begin()]))
                result += proc_rec(sub_id, file_data, styles, indent + 3, ind)
                last_pos = subregion.get_offset_end()
            result += (cgi.escape(text[last_pos:region.get_offset_end()]))
            result += ('</span>')
            return result
        result += proc_rec(1, data, styles, 0, 0)
        result += ('</pre></td></tr></table>')
    result += ('</body></html>')
    print(result)
    return exit_code
            
