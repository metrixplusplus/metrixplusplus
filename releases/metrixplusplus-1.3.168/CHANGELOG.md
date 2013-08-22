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

