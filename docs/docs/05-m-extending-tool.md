---
id: 05-m-extending-tool
title: Extending the tool
sidebar_label: Extending the tool
---

Want to enable a new metric or a language, need advanced post-analysis tool? Please, check the plugin development tutorial.
# Create plugin
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
```cpp
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
```
> python "/path/to/metrix++.py" collect
```
```
Hello world
```
