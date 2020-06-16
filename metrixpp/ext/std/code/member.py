#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

import mpp.api
import re

class Plugin(mpp.api.Plugin,
             mpp.api.IConfigurable,
             mpp.api.Child,
             mpp.api.MetricPluginMixin):
    
    def declare_configuration(self, parser):
        parser.add_option("--std.code.member.fields", "--scmf",
            action="store_true", default=False,
            help="Enables collection of number of data members / fields "
            "per classes, structs and interfaces [default: %default]")
        parser.add_option("--std.code.member.globals", "--scmg",
            action="store_true", default=False,
            help="Enables collection of number of global variables / fields "
            "per global regions and namespaces [default: %default]")
        parser.add_option("--std.code.member.classes", "--scmc",
            action="store_true", default=False,
            help="Enables collection of number of classes defined "
            "per any region [default: %default]")
        parser.add_option("--std.code.member.structs", "--scms",
            action="store_true", default=False,
            help="Enables collection of number of structs defined "
            "per any region [default: %default]")
        parser.add_option("--std.code.member.interfaces", "--scmi",
            action="store_true", default=False,
            help="Enables collection of number of interfaces defined "
            "per any region [default: %default]")
        parser.add_option("--std.code.member.types", "--scmt",
            action="store_true", default=False,
            help="Enables collection of number of types (classes, structs "
            "or interface) defined per any region [default: %default]")
        parser.add_option("--std.code.member.methods", "--scmm",
            action="store_true", default=False,
            help="Enables collection of number of methods (functions) defined "
            "per any region [default: %default]")
        parser.add_option("--std.code.member.namespaces", "--scmnss",
            action="store_true", default=False,
            help="Enables collection of number of namespaces defined "
            "globally and enclosed (sub-namespaces) [default: %default]")
    
    def configure(self, options):
        self.is_active_fields = options.__dict__['std.code.member.fields']
        self.is_active_globals = options.__dict__['std.code.member.globals']
        self.is_active_classes = options.__dict__['std.code.member.classes']
        self.is_active_structs = options.__dict__['std.code.member.structs']
        self.is_active_interfaces = options.__dict__['std.code.member.interfaces']
        self.is_active_types = options.__dict__['std.code.member.types']
        self.is_active_methods = options.__dict__['std.code.member.methods']
        self.is_active_namespaces = options.__dict__['std.code.member.namespaces']
    
    def initialize(self):
        # counts fields and properties with default getter/setter
        pattern_to_search_cs = re.compile(
            r'''([_a-zA-Z][_a-zA-Z0-9]*\s+[_a-zA-Z][_a-zA-Z0-9])\s*([=;]|'''
            r'''[{]\s*(public\s+|private\s+|protected\s+|internal\s+)?(get|set)\s*[;]\s*[a-z \t\r\n]*[}])''')
        pattern_to_search_cpp = re.compile(
            r'''([_a-zA-Z][_a-zA-Z0-9]*\s+[_a-zA-Z][_a-zA-Z0-9])\s*[=;]''')
        pattern_to_search_java = re.compile(
            r'''([_$a-zA-Z][_$a-zA-Z0-9]*\s+[_$a-zA-Z][_$a-zA-Z0-9])\s*[=;]''')
        self.declare_metric(self.is_active_fields,
                            self.Field('fields', int, non_zero=True),
                            {
                             'std.code.java': pattern_to_search_java,
                             'std.code.cpp': pattern_to_search_cpp,
                             'std.code.cs': pattern_to_search_cs,
                            },
                            marker_type_mask=mpp.api.Marker.T.CODE,
                            region_type_mask=mpp.api.Region.T.CLASS |
                            mpp.api.Region.T.STRUCT | mpp.api.Region.T.INTERFACE)
        self.declare_metric(self.is_active_globals,
                            self.Field('globals', int, non_zero=True),
                            {
                             'std.code.java': pattern_to_search_java,
                             'std.code.cpp': pattern_to_search_cpp,
                             'std.code.cs': pattern_to_search_cs,
                            },
                            marker_type_mask=mpp.api.Marker.T.CODE,
                            region_type_mask=mpp.api.Region.T.GLOBAL |
                            mpp.api.Region.T.NAMESPACE)
        self.declare_metric(self.is_active_classes,
                            self.Field('classes', int, non_zero=True),
                            (None, self.ClassesCounter),
                            exclude_subregions=False,
                            merge_markers=True)
        self.declare_metric(self.is_active_structs,
                            self.Field('structs', int, non_zero=True),
                            (None, self.StructCounter),
                            exclude_subregions=False,
                            merge_markers=True)
        self.declare_metric(self.is_active_interfaces,
                            self.Field('interfaces', int, non_zero=True),
                            (None, self.InterfaceCounter),
                            exclude_subregions=False,
                            merge_markers=True)
        self.declare_metric(self.is_active_types,
                            self.Field('types', int, non_zero=True),
                            (None, self.TypeCounter),
                            exclude_subregions=False,
                            merge_markers=True)
        self.declare_metric(self.is_active_methods,
                            self.Field('methods', int, non_zero=True),
                            (None, self.MethodCounter),
                            exclude_subregions=False,
                            merge_markers=True)
        self.declare_metric(self.is_active_namespaces,
                            self.Field('namespaces', int, non_zero=True),
                            (None, self.NamespaceCounter),
                            exclude_subregions=False,
                            merge_markers=True)
        
        super(Plugin, self).initialize(fields=self.get_fields())
        
        if self.is_active() == True:
            self.subscribe_by_parents_interface(mpp.api.ICode)

    class ClassesCounter(mpp.api.MetricPluginMixin.PlainCounter):
        def count(self, marker, pattern_to_search):
            self.result = sum(1 for unused in self.data.iterate_regions(
                filter_group=mpp.api.Region.T.CLASS, region_id=self.region.get_id()))

    class StructCounter(mpp.api.MetricPluginMixin.PlainCounter):
        def count(self, marker, pattern_to_search):
            self.result = sum(1 for unused in self.data.iterate_regions(
                filter_group=mpp.api.Region.T.STRUCT, region_id=self.region.get_id()))

    class InterfaceCounter(mpp.api.MetricPluginMixin.PlainCounter):
        def count(self, marker, pattern_to_search):
            self.result = sum(1 for unused in self.data.iterate_regions(
                filter_group=mpp.api.Region.T.INTERFACE, region_id=self.region.get_id()))

    class TypeCounter(mpp.api.MetricPluginMixin.PlainCounter):
        def count(self, marker, pattern_to_search):
            self.result = sum(1 for unused in self.data.iterate_regions(
                filter_group=mpp.api.Region.T.CLASS | mpp.api.Region.T.STRUCT |
                 mpp.api.Region.T.INTERFACE, region_id=self.region.get_id()))

    class MethodCounter(mpp.api.MetricPluginMixin.PlainCounter):
        def count(self, marker, pattern_to_search):
            self.result = sum(1 for unused in self.data.iterate_regions(
                filter_group=mpp.api.Region.T.FUNCTION, region_id=self.region.get_id()))

    class NamespaceCounter(mpp.api.MetricPluginMixin.PlainCounter):
        def count(self, marker, pattern_to_search):
            self.result = sum(1 for unused in self.data.iterate_regions(
                filter_group=mpp.api.Region.T.NAMESPACE, region_id=self.region.get_id()))
