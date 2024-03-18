---
id: 05-u-extending-tool
title: Extending the tool
sidebar_label: Extending the tool
---

Want to enable a new metric or a language, need advanced post-analysis tool? Please, check the plugin development tutorial.
## Create plugin
There are 3 types of plugins considered in this chapter:

* Metric plugin
* Language parser
* Post-processing / Analysis tool

Tutorial for metric plugin is generic at the beginning and large portion of this is applied to all other plugins. You need to know python and python regular expressions library to write Metrix++ extensions.

## Metric plugin
The tutorial will explain how to create a plugin to count magic numbers in source code. It will be relatively simple at first and will be extended with additional configuration options and smarter counting logic.

### Create placeholder for new plugin
1. All plugins are loaded by Metrix++ from standard places within the tool installation directory and from custom places specified in the METRIXPLUSPLUS_PATH environment variable. METRIXPLUSPLUS_PATH has got the same format as system PATH environment variable. So, the first step in plugin development is to set the METRIXPLUSPLUS_PATH to point out to the directory (or directories) where plugin is located.
2. Create new python package 'myext', python lib 'magic.py' and 'magic.ini' file.
```
+ working_directory (set in METRIXPLUSPLUS_PATH variable)
\--+ myext
   \--- __init__.py
   \--- magic.py
   \--- magic.ini
```
3. \__init\__.py is empty file to make myext considered by python as a package.

4. Edit magic.py to have the following content:
```py
import mpp.api
 
class Plugin(mpp.api.Plugin):
    
    def initialize(self):
        print "Hello world"
```
mpp.api package include Metrix++ API classes. mpp.api.Plugin is the base class, which can be loaded by Metrix++ engine and does nothing by default. In the code sample above it is extended to print "Hello world" on initialization.

5. Edit magic.ini to have the following content:
```
[Plugin]
version: 1.0
package: myext
module:  magic
class:   Plugin
depends: None
actions: collect
enabled: True
```

This file is a manifest for Metrix++ plugin loader. The fields in Plugin section are:
* **version** - 
a string representing the version, step up it every time when behaviour of a plugin or backward compatibility in api or data scope is changed
* **package** -
python package name where to load from
* **module** -
python module name (filename of *.py file) to load
* **class** -
name of a plugin class to instanciate
* **depends** -
list of plugin names to load, if it this plugin is loaded
* **actions** -
list of Metrix++ actions affected by this plugin
* **enabled** -
True or False, working status of a plugin

6. Now run Metrix++ to see how this new plugin works:
```bash
> python "/path/to/metrix++.py" collect
```
```
Hello world
```
### Toogle option for the plugin
1. It is recommended to follow the convention for all plugins: 'run only if enabled'. So, let's extend the magic.py file to make it configurable.
```py
import mpp.api
 
class Plugin(mpp.api.Plugin,
             # make this instance configurable...
             mpp.api.IConfigurable):
    # ... and implement 2 interfaces
    
    def declare_configuration(self, parser):
        parser.add_option("--myext.magic.numbers", "--mmn",
            action="store_true", default=False,
            help="Enables collection of magic numbers metric [default: %default]")
        
    def configure(self, options):
        self.is_active_numbers = options.__dict__['myext.magic.numbers']
    
    def initialize(self):
        # use configuration option here
        if self.is_active_numbers == True:
            print "Hello world"
```
parser argument is an instance of optparse.OptionParser class. It has got an extension to accept multiple options of the same argument. Check std.tools.limit to see how to declare multiopt options, if you need.

2. Now run Metrix++ to see how this works:
```bash
> python "/path/to/metrix++.py" collect --myext.magic.numbers
```
```
Hello world
```
### Subscribe to notifications from parent plugins (or code parsers)
1. Every plugin works in a callback functions called by parent plugins. Callback receives a reference to parent plugin, data object where to store metrics data, and a flag indicating if there are changes in file or parent's settings since the previous collection.
```py
import mpp.api
 
class Plugin(mpp.api.Plugin,
             mpp.api.IConfigurable,
             # declare that it can subscribe on notifications
             mpp.api.Child):
    
    def declare_configuration(self, parser):
        parser.add_option("--myext.magic.numbers", "--mmn",
            action="store_true", default=False,
            help="Enables collection of magic numbers metric [default: %default]")
    
    def configure(self, options):
        self.is_active_numbers = options.__dict__['myext.magic.numbers']
    
    def initialize(self):
        if self.is_active_numbers == True:
            # subscribe to notifications from all code parsers
            self.subscribe_by_parents_interface(mpp.api.ICode, 'callback')
 
    # parents (code parsers) will call the callback declared
    def callback(self, parent, data, is_updated):
        print parent.get_name(), data.get_path(), is_updated
```
2. Now run Metrix++ to see how this works. Try to do iterative scans (--db-file-prev option) to see how the state of arguments is changed
```bash
> python "/path/to/metrix++.py" collect --myext.magic.numbers
```
```bash
std.code.cpp ./test.cpp True
```

### Implement simple metric based on regular expression pattern

1. Callback may execute counting, searcing and additional parsing and store results, using data argument. 'data' argument is an instance of mpp.api.FileData class. However, most metrics can be implemented simplier, if mpp.api.MetricPluginMixin routines are used. MetricPluginMixin implements declarative style for metrics based on searches by regular expression. It cares about initialisation of database fields and properties. It implements default callback which counts number of matches by regular expression for all active declared metrics. So, let's utilise that:
```py
import mpp.api
import re
 
class Plugin(mpp.api.Plugin,
             mpp.api.IConfigurable,
             mpp.api.Child,
             # reuse by inheriting standard metric facilities
             mpp.api.MetricPluginMixin):
    
    def declare_configuration(self, parser):
        parser.add_option("--myext.magic.numbers", "--mmn",
            action="store_true", default=False,
            help="Enables collection of magic numbers metric [default: %default]")
    
    def configure(self, options):
        self.is_active_numbers = options.__dict__['myext.magic.numbers']
    
    def initialize(self):
        # declare metric rules
        self.declare_metric(
            self.is_active_numbers, # to count if active in callback
            self.Field('numbers', int), # field name and type in the database
            re.compile(r'''\b[0-9]+\b'''), # pattern to search
            marker_type_mask=mpp.api.Marker.T.CODE, # search in code
            region_type_mask=mpp.api.Region.T.ANY) # search in all types of regions
        
        # use superclass facilities to initialize everything from declared fields
        super(Plugin, self).initialize(fields=self.get_fields())
        
        # subscribe to all code parsers if at least one metric is active
        if self.is_active() == True:
            self.subscribe_by_parents_interface(mpp.api.ICode)
```
2. Now run Metrix++ to count numbers in code files.
```bash
> python "/path/to/metrix++.py" collect --myext.magic.numbers
```
3. Now view the results. At this stage it is fully working simple metric.
```bash
> python "/path/to/metrix++.py" view
```
```
:: info: Overall metrics for 'myext.magic:numbers' metric
	Average        : 2.75
	Minimum        : 0
	Maximum        : 7
	Total          : 11.0
	Distribution   : 4 regions in total (including 0 suppressed)
	  Metric value : Ratio : R-sum : Number of regions
	             0 : 0.250 : 0.250 : 1	|||||||||||||||||||||||||
	             1 : 0.250 : 0.500 : 1	|||||||||||||||||||||||||
	             3 : 0.250 : 0.750 : 1	|||||||||||||||||||||||||
	             7 : 0.250 : 1.000 : 1	|||||||||||||||||||||||||

:: info: Directory content:
	Directory      : .
```
### Extend regular expression incremental counting by smarter logic
1. At this stage the metric counts every number in source code. However, we indent to spot only 'magic' numbers. Declared constant is not a magic number, so it is better to exclude constants from counting. It is easy to change default counter behaviour by implementing a function with name '_<metric_name>_count'.
```py
import mpp.api
import re
 
class Plugin(mpp.api.Plugin,
             mpp.api.IConfigurable,
             mpp.api.Child,
             mpp.api.MetricPluginMixin):
    
    def declare_configuration(self, parser):
        parser.add_option("--myext.magic.numbers", "--mmn",
            action="store_true", default=False,
            help="Enables collection of magic numbers metric [default: %default]")
    
    def configure(self, options):
        self.is_active_numbers = options.__dict__['myext.magic.numbers']
    
    def initialize(self):
        # improve pattern to find declarations of constants
        pattern_to_search = re.compile(
            r'''((const(\s+[_a-zA-Z][_a-zA-Z0-9]*)+\s*[=]\s*)[-+]?[0-9]+\b)|(\b[0-9]+\b)''')
        self.declare_metric(self.is_active_numbers,
                            self.Field('numbers', int),
                            # give a pair of pattern + custom counter logic class
                            (pattern_to_search, self.NumbersCounter),
                            marker_type_mask=mpp.api.Marker.T.CODE,
                            region_type_mask=mpp.api.Region.T.ANY)
        
        super(Plugin, self).initialize(fields=self.get_fields())
        
        if self.is_active() == True:
            self.subscribe_by_parents_interface(mpp.api.ICode)
    
    # implement custom counter behavior:
    # increments counter by 1 only if single number spotted,
    # but not declaration of a constant
    class NumbersCounter(mpp.api.MetricPluginMixin.IterIncrementCounter):
        def increment(self, match):
            if match.group(0).startswith('const'):
                return 0
            return 1
```
2. Initialy counter is initialized by zero, but it is possible to change it as well by implementing a function with name '_<metric_name>_count_initialize'. 
3. Plugin we are implementing does not require this.
Now run Metrix++ to collect and view the results.
```bash
> python "/path/to/metrix++.py" collect --myext.magic.numbers
```
```bash
> python "/path/to/metrix++.py" view
```

### Language specific regular expressions
1. In the previous step we added matching of constants assuming that identifiers may have symbols '_', 'a-z', 'A-Z' and '0-9'. It is true for C++ but it is not complete for Java. Java identifier may have '$' symbol in the identifier. So, let's add language specific pattern in the declaration of the metric:
```py
import mpp.api
import re
 
class Plugin(mpp.api.Plugin,
             mpp.api.IConfigurable,
             mpp.api.Child,
             mpp.api.MetricPluginMixin):
    
    def declare_configuration(self, parser):
        parser.add_option("--myext.magic.numbers", "--mmn",
            action="store_true", default=False,
            help="Enables collection of magic numbers metric [default: %default]")
    
    def configure(self, options):
        self.is_active_numbers = options.__dict__['myext.magic.numbers']
    
    def initialize(self):
        # specialized pattern for java
        pattern_to_search_java = re.compile(
            r'''((const(\s+[_$a-zA-Z][_$a-zA-Z0-9]*)+\s*[=]\s*)[-+]?[0-9]+\b)|(\b[0-9]+\b)''')
        # pattern for C++ and C# languages
        pattern_to_search_cpp_cs = re.compile(
            r'''((const(\s+[_a-zA-Z][_a-zA-Z0-9]*)+\s*[=]\s*)[-+]?[0-9]+\b)|(\b[0-9]+\b)''')
        # pattern for all other languages
        pattern_to_search = re.compile(
            r'''\b[0-9]+\b''')
        self.declare_metric(self.is_active_numbers,
                            self.Field('numbers', int),
                            # dictionary of pairs instead of a single pair
                            {
                             'std.code.java': (pattern_to_search_java, self.NumbersCounter),
                             'std.code.cpp': (pattern_to_search_cpp_cs, self.NumbersCounter),
                             'std.code.cs': (pattern_to_search_cpp_cs, self.NumbersCounter),
                             '*': pattern_to_search
                            },
                            marker_type_mask=mpp.api.Marker.T.CODE,
                            region_type_mask=mpp.api.Region.T.ANY)
        
        super(Plugin, self).initialize(fields=self.get_fields())
        
        if self.is_active() == True:
            self.subscribe_by_parents_interface(mpp.api.ICode)
 
    class NumbersCounter(mpp.api.MetricPluginMixin.IterIncrementCounter):
        def increment(self, match):
            if match.group(0).startswith('const'):
                return 0
            return 1
```
2. Keys in the dictionary of patterns are names of parent plugins (references to code parsers). The key '*' refers to any parser.
3. Now run Metrix++ to collect and view the results.
```bash
> python "/path/to/metrix++.py" collect --myext.magic.numbers
```
```bash
> python "/path/to/metrix++.py" view
```
### Store only non-zero metric values
1. Most functions have the metric, which we are implemneting, equal to zero. However, we are interested in finding code blocks having this metric greater than zero. Zeros consumes the space in the data file. So, we can optimise the size of a data file, if we exclude zero metric values. Let's declare this behavior for the metric.
```py
import mpp.api
import re
 
class Plugin(mpp.api.Plugin,
             mpp.api.IConfigurable,
             mpp.api.Child,
             mpp.api.MetricPluginMixin):
    
    def declare_configuration(self, parser):
        parser.add_option("--myext.magic.numbers", "--mmn",
            action="store_true", default=False,
            help="Enables collection of magic numbers metric [default: %default]")
    
    def configure(self, options):
        self.is_active_numbers = options.__dict__['myext.magic.numbers']
    
    def initialize(self):
        pattern_to_search_java = re.compile(
            r'''((const(\s+[_$a-zA-Z][_$a-zA-Z0-9]*)+\s*[=]\s*)[-+]?[0-9]+\b)|(\b[0-9]+\b)''')
        pattern_to_search_cpp_cs = re.compile(
            r'''((const(\s+[_a-zA-Z][_a-zA-Z0-9]*)+\s*[=]\s*)[-+]?[0-9]+\b)|(\b[0-9]+\b)''')
        pattern_to_search = re.compile(
            r'''\b[0-9]+\b''')
        self.declare_metric(self.is_active_numbers,
                            self.Field('numbers', int,
                                # optimize the size of datafile:
                                # store only non-zero results
                                non_zero=True),
                            {
                             'std.code.java': (pattern_to_search_java, self.NumbersCounter),
                             'std.code.cpp': (pattern_to_search_cpp_cs, self.NumbersCounter),
                             'std.code.cs': (pattern_to_search_cpp_cs, self.NumbersCounter),
                             '*': pattern_to_search
                            },
                            marker_type_mask=mpp.api.Marker.T.CODE,
                            region_type_mask=mpp.api.Region.T.ANY)
        
        super(Plugin, self).initialize(fields=self.get_fields())
        
        if self.is_active() == True:
            self.subscribe_by_parents_interface(mpp.api.ICode)
 
    class NumbersCounter(mpp.api.MetricPluginMixin.IterIncrementCounter):
        def increment(self, match):
            if match.group(0).startswith('const'):
                return 0
            return 1
```
2. Now run Metrix++ to collect and view the results.
```bash
> python "/path/to/metrix++.py" collect --myext.magic.numbers
```
```bash
> python "/path/to/metrix++.py" view
```
### Additional per metric configuration options
1. It is typical that most numbers counted by the metric are equal to 0, -1 or 1. They are not necessary magic numbers. 0 or 1 are typical variable initializers. -1 is a typical negative return code. So, let's implement simplified version of the metric, which does not count 0, -1 and 1, if the specific new option is set.
```py
import mpp.api
import re
 
class Plugin(mpp.api.Plugin,
             mpp.api.IConfigurable,
             mpp.api.Child,
             mpp.api.MetricPluginMixin):
    
    def declare_configuration(self, parser):
        parser.add_option("--myext.magic.numbers", "--mmn",
            action="store_true", default=False,
            help="Enables collection of magic numbers metric [default: %default]")
        # Add new option
        parser.add_option("--myext.magic.numbers.simplier", "--mmns",
            action="store_true", default=False,
            help="Is set, 0, -1 and 1 numbers are not counted [default: %default]")
    
    def configure(self, options):
        self.is_active_numbers = options.__dict__['myext.magic.numbers']
        # remember the option here
        self.is_active_numbers_simplier = options.__dict__['myext.magic.numbers.simplier']
    
    def initialize(self):
        pattern_to_search_java = re.compile(
            r'''((const(\s+[_$a-zA-Z][_$a-zA-Z0-9]*)+\s*[=]\s*)[-+]?[0-9]+\b)|(\b[0-9]+\b)''')
        pattern_to_search_cpp_cs = re.compile(
            r'''((const(\s+[_a-zA-Z][_a-zA-Z0-9]*)+\s*[=]\s*)[-+]?[0-9]+\b)|(\b[0-9]+\b)''')
        pattern_to_search = re.compile(
            r'''\b[0-9]+\b''')
        self.declare_metric(self.is_active_numbers,
                            self.Field('numbers', int,
                                non_zero=True),
                            {
                             'std.code.java': (pattern_to_search_java, self.NumbersCounter),
                             'std.code.cpp': (pattern_to_search_cpp_cs, self.NumbersCounter),
                             'std.code.cs': (pattern_to_search_cpp_cs, self.NumbersCounter),
                             '*': pattern_to_search
                            },
                            marker_type_mask=mpp.api.Marker.T.CODE,
                            region_type_mask=mpp.api.Region.T.ANY)
        
        super(Plugin, self).initialize(fields=self.get_fields(),
            # remember option settings in data file properties
            # in order to detect changes in settings on iterative re-run
            properties=[self.Property('number.simplier', self.is_active_numbers_simplier)])
        
        if self.is_active() == True:
            self.subscribe_by_parents_interface(mpp.api.ICode)
 
    class NumbersCounter(mpp.api.MetricPluginMixin.IterIncrementCounter):
        def increment(self, match):
            if (match.group(0).startswith('const') or
                (self.plugin.is_active_numbers_simplier == True and
                 match.group(0) in ['0', '1', '-1', '+1'])):
                return 0
            return 1
```
2. Now run Metrix++ to collect and view the results.
```bash
> python "/path/to/metrix++.py" collect --myext.magic.numbers
```
```bash
> python "/path/to/metrix++.py" view
```
```
:: info: Overall metrics for 'myext.magic:numbers' metric
	Average        : 2.5 (excluding zero metric values)
	Minimum        : 2
	Maximum        : 3
	Total          : 5.0
	Distribution   : 2 regions in total (including 0 suppressed)
	  Metric value : Ratio : R-sum : Number of regions
	             2 : 0.500 : 0.500 : 1	||||||||||||||||||||||||||||||||||||||||||||||||||
	             3 : 0.500 : 1.000 : 1	||||||||||||||||||||||||||||||||||||||||||||||||||

:: info: Directory content:
	Directory      : .
```
### Summary
We have finished with the tutorial. The tutorial explained how to implement simple and advanced metric plugins. We used built-in Metrix++ base classes. If you need to more advanced plugin capabilities, override in your plugin class functions inherited from mpp.api base classes. Check code of standard plugins to learn more techniques.

## Analysis tool plugin

This tutorial will explain how to build custom Metrix++ command, which is bound to custom post-analysis tool. We will implement the tool, which identifies all new and changed regions and counts number of added lines. We skip calculating number of deleted lines, but it is easy to extend from what we get finally in the tutorial.

### New Metrix++ command / action

1. As in the tutorial for metric plugin, set the environment and create new python package 'myext', python lib 'compare.py' and 'compare.ini' file.
```
+ working_directory (set in METRIXPLUSPLUS_PATH variable)
\--+ myext
   \--- __init__.py
   \--- compare.py
   \--- compare.ini
```

2. __init__.py is empty file to make myext considered by python as a package.

3. Edit compare.py to have the following content:
```py
import mpp.api
 
class Plugin(mpp.api.Plugin, mpp.api.IRunable):
    
    def run(self, args):
        print args
        return 0
```
Inheritance from mpp.api.IRunable declares that the plugin is runable and requires implementation of 'run' interface.

4. Edit compare.ini to have the following content:
```
[Plugin]
version: 1.0
package: myext
module:  compare
class:   Plugin
depends: None
actions: compare
enabled: True
```
This file is a manifest for Metrix++ plugin loader. Actions field has got new value 'compare'. Metrix++ engine will automatically pick this action and will add it to the list of available commands. This plugin will be loaded on 'compare' action.

5. Now run Metrix++ to see how this new plugin works:
```bash
> python "/path/to/metrix++.py" compare -- path1 path2 path3
```
```
["path1", "path2", "path3"]
```
### Access data file loader and its interfaces

1. By default, all post-analysis tools have got --db-file and --db-file-prev options. It is because 'mpp.dbf' plugin is loaded for any action, including our new one 'compare'. In order to continue the tutorial, we need to have 2 data files with 'std.code.lines:total' metric collected. So, write to files by running:

```bash
> cd my_project_version_1
> python "/path/to/metrix++.py" collect --std.code.lines.total
```
```bash
> cd my_project_version_2
> python "/path/to/metrix++.py" collect --std.code.lines.total
```

2. Edit compare.py file to get the loader and iterate collected file paths:
```py
import mpp.api
# load common utils for post processing tools
import mpp.utils
 
class Plugin(mpp.api.Plugin, mpp.api.IRunable):
    
    def run(self, args):
        # get data file reader using standard metrix++ plugin
        loader = self.get_plugin('mpp.dbf').get_loader()
        
        # iterate and print file length for every path in args
        exit_code = 0
        for path in (args if len(args) > 0 else [""]):
            file_iterator = loader.iterate_file_data(path)
            if file_iterator == None:
                mpp.utils.report_bad_path(path)
                exit_code += 1
                continue
            for file_data in file_iterator:
                print file_data.get_path()
        return exit_code
```

3. Now run Metrix++ to see how it works:
```bash
> python "/path/to/metrix++.py" compare --db-file=my_project_version_2/metrixpp.db --db-file-prev=my_project_version_1/metrixpp.db
```
### Identify added, modified files/regions and read metric data

1. Let's extend the logic of the tool to compare files and regions, read 'std.code.lines:total' metric and calcuate the summary of number of added lines. mpp.utils.FileRegionsMatcher is helper class which does matching and comparison of regions for 2 given mpp.api.FileData objects.
```
import mpp.api
import mpp.utils
import mpp.cout
 
class Plugin(mpp.api.Plugin, mpp.api.IRunable):
    
    def run(self, args):
        loader = self.get_plugin('mpp.dbf').get_loader()
        # get previous db file loader
        loader_prev = self.get_plugin('mpp.dbf').get_loader_prev()
        
        exit_code = 0
        for path in (args if len(args) > 0 else [""]):
            added_lines = 0
            file_iterator = loader.iterate_file_data(path)
            if file_iterator == None:
                mpp.utils.report_bad_path(path)
                exit_code += 1
                continue
            for file_data in file_iterator:
                added_lines += self._compare_file(file_data, loader, loader_prev)
            mpp.cout.notify(path, '', mpp.cout.SEVERITY_INFO,
                            "Change trend report",
                            [('Added lines', added_lines)])
        return exit_code
 
    def _compare_file(self, file_data, loader, loader_prev):
        # compare file with previous and return number of new lines
        file_data_prev = loader_prev.load_file_data(file_data.get_path())
        if file_data_prev == None:
            return self._sum_file_regions_lines(file_data)
        elif file_data.get_checksum() != file_data_prev.get_checksum():
            return self._compare_file_regions(file_data, file_data_prev)
 
    def _sum_file_regions_lines(self, file_data):
        # just sum up the metric for all regions
        result = 0
        for region in file_data.iterate_regions():
            result += region.get_data('std.code.lines', 'total')
    
    def _compare_file_regions(self, file_data, file_data_prev):
        # compare every region with previous and return number of new lines
        matcher = mpp.utils.FileRegionsMatcher(file_data, file_data_prev)
        result = 0
        for region in file_data.iterate_regions():
            if matcher.is_matched(region.get_id()) == False:
                # if added region, just add the lines
                result += region.get_data('std.code.lines', 'total')
            elif matcher.is_modified(region.get_id()):
                # if modified, add the difference in lines
                region_prev = file_data_prev.get_region(
                    matcher.get_prev_id(region.get_id()))
                result += (region.get_data('std.code.lines', 'total') -
                           region_prev.get_data('std.code.lines', 'total'))
        return result
```

2. Now run Metrix++ to see how it works:
```bash
> python "/path/to/metrix++.py" compare --db-file=my_project_version_2/metrixpp.db --db-file-prev=my_project_version_1/metrixpp.db
```
```
:: info: Change trend report
	Added lines    : 7
```

### Summary

We have finished with the tutorial. The tutorial explained how to read Metrix++ data files and implement custom post-processing tools. Even if some existing Metrix++ code requires clean-up and refactoring, check code of standard tool plugins to learn more techniques.

## Language parser plugin

Unfortunately, there is no good documentation at this stage for this part. Briefly, if metric plugin counts and stores data into FileData object, tool plugin reads this data, language plugin construct the original structure of FileData object. The orginal structure includes regions (like functions, classes, etc.) and markers (like comments, strings, preprocessor, etc.). Check code of existing parsers:
* a language parser plugin is registered in the same way as a metric plugin
* it registers parser's callback in 'std.tools.collect' plugin
* parses a file in a callback, called by 'std.tools.collect'
* parser needs to identify markers and regions and tell about this to file data object passed as an argument for the callback.

There are useful options and tools avaialble for trobuleshooting purposes during development:
* metrix++.py debug generates html code showing parsed code structures and their boundaries
* --nest-regions for view tool forces the viewer to indent subregions.
* --log-level option is available for any command and is helpful to trace execution.

Finally, if there are any questions or enquires, please, feel free to [submit new question](https://github.com/metrixplusplus/metrixplusplus/issues/new).


