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
                            marker_type_mask=api.Marker.T.CODE,
                            region_type_mask=api.Region.T.CLASS |
                            api.Region.T.STRUCT | api.Region.T.INTERFACE)
        self.declare_metric(self.is_active_globals,
                            self.Field('globals', int, non_zero=True),
                            {
                             'std.code.java': pattern_to_search_java,
                             'std.code.cpp': pattern_to_search_cpp,
                             'std.code.cs': pattern_to_search_cs,
                            },
                            marker_type_mask=api.Marker.T.CODE,
                            region_type_mask=api.Region.T.GLOBAL |
                            api.Region.T.NAMESPACE)
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
            self.subscribe_by_parents_interface(api.ICode)

    class ClassesCounter(api.MetricPluginMixin.PlainCounter):
        def count(self, marker, pattern_to_search):
            self.result = sum(1 for unused in self.data.iterate_regions(
                filter_group=api.Region.T.CLASS, region_id=self.region.get_id()))

    class StructCounter(api.MetricPluginMixin.PlainCounter):
        def count(self, marker, pattern_to_search):
            self.result = sum(1 for unused in self.data.iterate_regions(
                filter_group=api.Region.T.STRUCT, region_id=self.region.get_id()))

    class InterfaceCounter(api.MetricPluginMixin.PlainCounter):
        def count(self, marker, pattern_to_search):
            self.result = sum(1 for unused in self.data.iterate_regions(
                filter_group=api.Region.T.INTERFACE, region_id=self.region.get_id()))

    class TypeCounter(api.MetricPluginMixin.PlainCounter):
        def count(self, marker, pattern_to_search):
            self.result = sum(1 for unused in self.data.iterate_regions(
                filter_group=api.Region.T.CLASS | api.Region.T.STRUCT |
                 api.Region.T.INTERFACE, region_id=self.region.get_id()))

    class MethodCounter(api.MetricPluginMixin.PlainCounter):
        def count(self, marker, pattern_to_search):
            self.result = sum(1 for unused in self.data.iterate_regions(
                filter_group=api.Region.T.FUNCTION, region_id=self.region.get_id()))

    class NamespaceCounter(api.MetricPluginMixin.PlainCounter):
        def count(self, marker, pattern_to_search):
            self.result = sum(1 for unused in self.data.iterate_regions(
                filter_group=api.Region.T.NAMESPACE, region_id=self.region.get_id()))
