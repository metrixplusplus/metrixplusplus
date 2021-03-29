---
id: 01-u-overview
title: Overview
sidebar_label: Overview
---

## Highlights
Metrix++ is a tool to collect and analyse code metrics. Any metric is useless if it is not used. Metrix++ offers ease of introduction and integration with a variety of application use cases.

* Monitoring trends (eg. on **daily** basis. In order to take actions or make right decisions earlier.)
* Enforcing trends (eg. on **hourly** basis, at every commit of code changes.)
* Automated asistance to review agains standards (eg. on **per minute** basis during code refactoring and code development.)
The workflow sections below demonstarate these basic application usecases.

## Languages supported
The tool can parse C/C++, C# and Java source code files. The parser identifies certain regions in the code, such as classes, functions, namespaces, interfaces, etc. It detects comments, strings and code for the preprocessor. The identified regions form a tree of nested source code blocks, which are subsequently refered to and scanned by metrics plugins. Thus the tool attributes metrics to regions, which provides fine grained data to analysis tools. The following example demonstrates the regions concept. The right side comments describe Metrix++ properties attributed to each source line: type of region, name of a region and type of a content of a region).

```cpp
// simple C++ code                         // file: __global__: comment
                                           // file: __global__: code
#include <myapi.h>                         // file: __global__: preprocessor
                                           // file: __global__: code
// I explain the following class           //     class: MyClass: comment
class MyClass {                            //     class: MyClass: code
public:                                    //     class: MyClass: code
    int m_var; // some member              //     class: MyClass: code, comment
                                           //     class: MyClass: code
    // I explain the following function    //         function: MyClass: comment
    MyClass(): m_var(0) {                  //         function: MyClass: code
        char str[] = "unused string"       //         function: MyClass: code, string
                                           //         function: MyClass: code, string
        // nested region for good measure  //         function: MyClass: code
        struct MyStruct {};                //             struct: MyStruct: comment
    }                                      //             struct: MyStruct: code
                                           //         function: MyClass: code
    // Do not judge ugly code below        //     class: MyClass: code
#define get_max(a,b) ((a)>(b)?(a):(b))     //         function: set_max: comment
    set_max(int b) {                       //         function: set_max: preprocessor
        m_var = get_max(m_var, b);         //         function: set_max: code
    }                                      //         function: set_max: code
};                                         //         function: set_max: code
// this is the last line                   // file: __global__: comment
```

## Metrics
The metrics highlighed in blue are **per file** metrics. The other metrics are **per region** metrics.


<table class="table table-bordered">
<thead>
    <tr>
    <th>Metric (enable option)</th>
    <th>Brief description</th>
    <th>Motivation / Potential use</th>
    </tr>
</thead>
<tbody>
    <tr class="info center-justified">
    <td>std.general.size</td>
    <td>Size of a file in bytes.</td>
    <td rowspan="6"><ul><li>Monitoring the growth of source code base.</li>
        <li>Normalizing other metrics.</li>
        <li>Preventing large files and regions (large things are difficult to maintain).</li>
        <li>Predicting delivery dates by comparing S-shaped code base growth / change curves.</li></ul>
    </td>
    </tr>
    <tr  class="td-regular center-justified">
    <td>std.code.length.total</td>
    <td>The same as 'std.general.size' metric, but attributed to code regions.</td>
    </tr>
    <tr class="info center-justified">
    <td>std.code.filelines.total</td>
    <td>Number of non-blank lines of code of any content type (exectuable, comments, etc.) per file</td>
    </tr>
    <tr  class="td-regular center-justified">
    <td>std.code.lines.total</td>
    <td>Number of non-blank lines of code of any content type (exectuable, comments, etc.) per region</td>
    </tr>
    <tr class="info center-justified">
    <td>std.code.filelines.code</td>
    <td>Number of non-blank lines of code excluding preprocessor and comments per file.</td>
    </tr>
    <tr  class="td-regular center-justified">
    <td>std.code.lines.code</td>
    <td>Number of non-blank lines of code excluding preprocessor and comments per region.</td>
    </tr>
    <tr class="info center-justified">
    <td>std.code.filelines.preprocessor</td>
    <td>Number of non-blank lines of preprocessor code per file.</td>
    <td rowspan="2"><ul><li>Enforcing localisation of preprocessor code in a single place.</li>
        <li>Encouraging usage of safer code structures instead of the preprocessor.</li></ul></td>
    </tr>
    <tr  class="td-regular center-justified">
    <td>std.code.lines.preprocessor</td>
    <td>Number of non-blank lines of preprocessor code per region.</td>
    </tr>
    <tr class="info center-justified">
    <td>std.code.filelines.comments</td>
    <td>Number of non-blank lines of comments per file.</td>
    <td rowspan="2"><ul><li>Low number of comments may indicate maintainability problems.</li></ul></td>
    </tr>
    <tr  class="td-regular center-justified">
    <td>std.code.lines.comments</td>
    <td>Number of non-blank lines of comments per region.</td>
    </tr>
    <tr class="td-regular center-justified">
    <td>std.code.complexity.cyclomatic</td>
    <td>McCabe cyclomatic complexity metric.</td>
    <td colspan="2"><ul><li>Identification of highly complex code for review and refactoring.</li>
        <li>Preventing complex functions (complexity is a reason of many defects and a reason of expensive maintaintenance).</li></ul></td>
    </tr>
    <tr class="td-regular center-justified">
    <td>std.code.complexity.maxindent</td>
    <td>Maximum level of indentation of blocks within a region.
        <pre class="prettyprint">
        </pre>
        </td>
    </tr>
    <tr class="td-regular center-justified">
    <td>std.code.magic.numbers</td>
    <td>Number of magic numbers. There is an option to exclude 0, -1 and 1 numbers from counting.</td>
    <td>Magic numbers are dangerous.
        The <a href="http://stackoverflow.com/questions/47882/what-is-a-magic-number-and-why-is-it-bad" target="blank">
            discussion on stackoverflow</a> explains why.</td>
    </tr>
    <tr class="td-regular center-justified">
    <td>std.code.todo.comments, std.code.todo.strings</td>
    <td>Number of TODO/FIXME/etc markers in comments and strings accordingly.
        There is an option to configure a list of markers.</td>
    <td>Manage potentially incomplete work. If project manager dispatches issues only in a tracker tool,
        todo markers are lost in the source code. The metric could make these 'lost' issues visible.</td>
    </tr>
    <tr class="info center-justified">
    <td>std.general.proctime</td>
    <td>Seconds spent on processing a file.</td>
    <td><ul><li>Monitor and profile Metrix++ tool's performance.</li></ul>
    </td>
    </tr>
    <tr class="td-regular center-justified">
    <td>std.suppress</td>
    <td>An option enables collection of Metrix++ suppressions and 2 metrics: 'std.suppress:count' and
        'std.suppress.file:count'. The first is number of suppressions per region.
        The second is the same but applies for file-scope metrics.</td>
    <td><ul><li>Suppressing false-positives.</li>
        <li>Managing the amount of suppressions. There should be no false-positives to suppress with the right metric,
            but there could be exceptions in specific cases. Managing suppressions is about managing exceptions.
            If there are many exceptional cases, maybe something is wrong with a metric or the application of a metric.</li></ul></td>
    </tr>
    <tr class="info center-justified">
    <td>std.general.procerrors</td>
    <td>Number of errors detected by Metrix++ code parser.</td>
    <td><ul><li>Cleaning up errors to ensure reliable code scanning.</li>
        <li>Errors, like mismatched brackets, may result in bad identification of regions.</li>
    </ul></td>
    </tr>
    <tr class="td-regular center-justified">
    <td>std.code.maintindex.simple</td>
    <td>Simple variant of maintainability index - a measure of maintainability.
        It uses std.code.lines:code and std.code.complexity:cyclomatic
        metrics to evaluate level of maintainability. Lower value of this index indicates
        better level maintainability</td>
    <td>Identify code, which may benefit the most from refactoring.</td>
    </tr>
</tbody>
</table>
