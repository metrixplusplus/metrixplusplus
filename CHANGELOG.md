## 1.8.0 (March, 2024)
- Improve C/C++ number parsing
- Added new metric, ratio of comment lines to code lines 2
- Detect correct file coding
- report plugin
- exclude directories option
- cyclomatic complexity metric without switch case

## 1.7.1 (June, 2021)
- improve C++ numbers parsing

## 1.7 (December, 2020)
- added Promehteous format for exporting/view
- added std.code.longlines plugin

## 1.6 (June, 2020)
- added python3 support
- added pypi package (metrixpp)
- changed implementation of collect --include-files to include all files matching any rule
- fix implementation of std.code.maintindex.simple

## 1.5 (April, 2019)
- project moved to github
- fixed processing of more than one directory #73
- improved limit tool to be able to apply different limits on different region types

## 1.4 (June, 2014)
- Fixed match of names of generic functions and classes 
- New metrics group: std.code.member.* - counting of classes, fields, globals, etc.
- New metric: std.code.maintindex:simple - simple implemetation of maintainability index.
- New configuration option for collect tool: --include-files (symetrical to --exclude-files)
- New metrics: lines of code metrics per file

## 1.3 (August, 2013)
- Deprecated and dropped support for callback based implementation of advanced counters
(use MetricPluginMixin.*Counter classes instead)
- New metric: std.code.todo:comments - number of todo markers in comments.
- New metric: std.code.todo:strings - number of todo markers in strings.
- Defect fixed: critical performance issue for iterative runs
- Defect fixed: fixed counting of magic numbers

## 1.2 (August, 2013)
- **Feature** suppressions capability for limit tool
- **Feature** distribution tables and graphs in viewer
- **Feature** export tool (exproting of data files to csv format)
- **Feature** unified stdout output format for all tools
- **New metric plugin** std.code.magic:numbers: Counts number of magic numbers per region.
- **New metric plugin** std.code.lines: Counts number of lines of code, comments, preprocessor,
etc.
- **New metric plugin** std.code.length: Counts number of symbols per region.
- **New metric plugin** std.code.complexity:maxindend: Measures maximum level of indented blocks per function.
- **New metric plugin** std.general:size: Measures file size in bytes.
- **New documentation**: Explains code regions concepts, available metrics, workflow,
plugin development.
- **Re-factoring**: better Metrix++ api for plugin development.
- **Major bug-fixing**: application to real commercial software and use cases.

## 1.1 (March, 2013)
- **Extension point for post analysis tools** added. All tools are merged
  to one 'metrix++.py' with plugable actions, like collect, limit, etc:
  run 'python metrix++.py' to get the list of actions supported.
- fixed Java parser (fixed false match of attributes as functions)

