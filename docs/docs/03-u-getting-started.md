---
id: 03-u-getting-started
title: Getting started
sidebar_label: Getting started
---

The tool is relatively simple to use. There are 3 fundamental steps:

* Collect the data, for example:
```bash
> python "/path/to/metrix++.py" collect --std.code.lines.code --std.code.complexity.cyclomatic
```


* View the data, for example:
```bash
> python "/path/to/metrix++.py" view
```


* Apply thresholds, for example:
```bash
> python "/path/to/metrix++.py" limit --max-limit=std.code.complexity:cyclomatic:7
```

Please, check the advanced [description of the workflow](04-u-workflow.md) with real examples.