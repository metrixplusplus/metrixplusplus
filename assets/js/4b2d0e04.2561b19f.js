"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[270],{5680:(e,t,n)=>{n.d(t,{xA:()=>d,yg:()=>m});var o=n(6540);function i(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function r(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(e);t&&(o=o.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,o)}return n}function s(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?r(Object(n),!0).forEach((function(t){i(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):r(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function l(e,t){if(null==e)return{};var n,o,i=function(e,t){if(null==e)return{};var n,o,i={},r=Object.keys(e);for(o=0;o<r.length;o++)n=r[o],t.indexOf(n)>=0||(i[n]=e[n]);return i}(e,t);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);for(o=0;o<r.length;o++)n=r[o],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(i[n]=e[n])}return i}var a=o.createContext({}),c=function(e){var t=o.useContext(a),n=t;return e&&(n="function"==typeof e?e(t):s(s({},t),e)),n},d=function(e){var t=c(e.components);return o.createElement(a.Provider,{value:t},e.children)},u="mdxType",g={inlineCode:"code",wrapper:function(e){var t=e.children;return o.createElement(o.Fragment,{},t)}},y=o.forwardRef((function(e,t){var n=e.components,i=e.mdxType,r=e.originalType,a=e.parentName,d=l(e,["components","mdxType","originalType","parentName"]),u=c(n),y=i,m=u["".concat(a,".").concat(y)]||u[y]||g[y]||r;return n?o.createElement(m,s(s({ref:t},d),{},{components:n})):o.createElement(m,s({ref:t},d))}));function m(e,t){var n=arguments,i=t&&t.mdxType;if("string"==typeof e||i){var r=n.length,s=new Array(r);s[0]=y;var l={};for(var a in t)hasOwnProperty.call(t,a)&&(l[a]=t[a]);l.originalType=e,l[u]="string"==typeof e?e:i,s[1]=l;for(var c=2;c<r;c++)s[c]=n[c];return o.createElement.apply(null,s)}return o.createElement.apply(null,n)}y.displayName="MDXCreateElement"},4401:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>a,contentTitle:()=>s,default:()=>g,frontMatter:()=>r,metadata:()=>l,toc:()=>c});var o=n(8168),i=(n(6540),n(5680));const r={id:"01-u-overview",title:"Overview",sidebar_label:"Overview"},s=void 0,l={unversionedId:"01-u-overview",id:"01-u-overview",title:"Overview",description:"Highlights",source:"@site/docs/01-u-overview.md",sourceDirName:".",slug:"/01-u-overview",permalink:"/metrixplusplus/docs/01-u-overview",draft:!1,editUrl:"https://metrixplusplus.github.io/docs/01-u-overview.md",tags:[],version:"current",sidebarPosition:1,frontMatter:{id:"01-u-overview",title:"Overview",sidebar_label:"Overview"},sidebar:"someSidebar",next:{title:"Download and install",permalink:"/metrixplusplus/docs/02-u-download-install"}},a={},c=[{value:"Highlights",id:"highlights",level:2},{value:"Languages supported",id:"languages-supported",level:2},{value:"Metrics",id:"metrics",level:2}],d={toc:c},u="wrapper";function g(e){let{components:t,...n}=e;return(0,i.yg)(u,(0,o.A)({},d,n,{components:t,mdxType:"MDXLayout"}),(0,i.yg)("h2",{id:"highlights"},"Highlights"),(0,i.yg)("p",null,"Metrix++ is a tool to collect and analyse code metrics. Any metric is useless if it is not used. Metrix++ offers ease of introduction and integration with a variety of application use cases."),(0,i.yg)("ul",null,(0,i.yg)("li",{parentName:"ul"},"Monitoring trends (eg. on ",(0,i.yg)("strong",{parentName:"li"},"daily")," basis. In order to take actions or make right decisions earlier.)"),(0,i.yg)("li",{parentName:"ul"},"Enforcing trends (eg. on ",(0,i.yg)("strong",{parentName:"li"},"hourly")," basis, at every commit of code changes.)"),(0,i.yg)("li",{parentName:"ul"},"Automated asistance to review agains standards (eg. on ",(0,i.yg)("strong",{parentName:"li"},"per minute")," basis during code refactoring and code development.)\nThe workflow sections below demonstarate these basic application usecases.")),(0,i.yg)("h2",{id:"languages-supported"},"Languages supported"),(0,i.yg)("p",null,"The tool can parse C/C++, C# and Java source code files. The parser identifies certain regions in the code, such as classes, functions, namespaces, interfaces, etc. It detects comments, strings and code for the preprocessor. The identified regions form a tree of nested source code blocks, which are subsequently refered to and scanned by metrics plugins. Thus the tool attributes metrics to regions, which provides fine grained data to analysis tools. The following example demonstrates the regions concept. The right side comments describe Metrix++ properties attributed to each source line: type of region, name of a region and type of a content of a region)."),(0,i.yg)("pre",null,(0,i.yg)("code",{parentName:"pre",className:"language-cpp"},'// simple C++ code                         // file: __global__: comment\n                                           // file: __global__: code\n#include <myapi.h>                         // file: __global__: preprocessor\n                                           // file: __global__: code\n// I explain the following class           //     class: MyClass: comment\nclass MyClass {                            //     class: MyClass: code\npublic:                                    //     class: MyClass: code\n    int m_var; // some member              //     class: MyClass: code, comment\n                                           //     class: MyClass: code\n    // I explain the following function    //         function: MyClass: comment\n    MyClass(): m_var(0) {                  //         function: MyClass: code\n        char str[] = "unused string"       //         function: MyClass: code, string\n                                           //         function: MyClass: code, string\n        // nested region for good measure  //         function: MyClass: code\n        struct MyStruct {};                //             struct: MyStruct: comment\n    }                                      //             struct: MyStruct: code\n                                           //         function: MyClass: code\n    // Do not judge ugly code below        //     class: MyClass: code\n#define get_max(a,b) ((a)>(b)?(a):(b))     //         function: set_max: comment\n    set_max(int b) {                       //         function: set_max: preprocessor\n        m_var = get_max(m_var, b);         //         function: set_max: code\n    }                                      //         function: set_max: code\n};                                         //         function: set_max: code\n// this is the last line                   // file: __global__: comment\n')),(0,i.yg)("h2",{id:"metrics"},"Metrics"),(0,i.yg)("p",null,"The metrics highlighed in blue are ",(0,i.yg)("strong",{parentName:"p"},"per file")," metrics. The other metrics are ",(0,i.yg)("strong",{parentName:"p"},"per region")," metrics."),(0,i.yg)("table",{class:"table table-bordered"},(0,i.yg)("thead",null,(0,i.yg)("tr",null,(0,i.yg)("th",null,"Metric (enable option)"),(0,i.yg)("th",null,"Brief description"),(0,i.yg)("th",null,"Motivation / Potential use"))),(0,i.yg)("tbody",null,(0,i.yg)("tr",{class:"info center-justified"},(0,i.yg)("td",null,"std.general.size"),(0,i.yg)("td",null,"Size of a file in bytes."),(0,i.yg)("td",{rowspan:"6"},(0,i.yg)("ul",null,(0,i.yg)("li",null,"Monitoring the growth of source code base."),(0,i.yg)("li",null,"Normalizing other metrics."),(0,i.yg)("li",null,"Preventing large files and regions (large things are difficult to maintain)."),(0,i.yg)("li",null,"Predicting delivery dates by comparing S-shaped code base growth / change curves.")))),(0,i.yg)("tr",{class:"td-regular center-justified"},(0,i.yg)("td",null,"std.code.length.total"),(0,i.yg)("td",null,"The same as 'std.general.size' metric, but attributed to code regions.")),(0,i.yg)("tr",{class:"info center-justified"},(0,i.yg)("td",null,"std.code.filelines.total"),(0,i.yg)("td",null,"Number of non-blank lines of code of any content type (exectuable, comments, etc.) per file")),(0,i.yg)("tr",{class:"td-regular center-justified"},(0,i.yg)("td",null,"std.code.lines.total"),(0,i.yg)("td",null,"Number of non-blank lines of code of any content type (exectuable, comments, etc.) per region")),(0,i.yg)("tr",{class:"info center-justified"},(0,i.yg)("td",null,"std.code.filelines.code"),(0,i.yg)("td",null,"Number of non-blank lines of code excluding preprocessor and comments per file.")),(0,i.yg)("tr",{class:"td-regular center-justified"},(0,i.yg)("td",null,"std.code.lines.code"),(0,i.yg)("td",null,"Number of non-blank lines of code excluding preprocessor and comments per region.")),(0,i.yg)("tr",{class:"info center-justified"},(0,i.yg)("td",null,"std.code.filelines.preprocessor"),(0,i.yg)("td",null,"Number of non-blank lines of preprocessor code per file."),(0,i.yg)("td",{rowspan:"2"},(0,i.yg)("ul",null,(0,i.yg)("li",null,"Enforcing localisation of preprocessor code in a single place."),(0,i.yg)("li",null,"Encouraging usage of safer code structures instead of the preprocessor.")))),(0,i.yg)("tr",{class:"td-regular center-justified"},(0,i.yg)("td",null,"std.code.lines.preprocessor"),(0,i.yg)("td",null,"Number of non-blank lines of preprocessor code per region.")),(0,i.yg)("tr",{class:"info center-justified"},(0,i.yg)("td",null,"std.code.filelines.comments"),(0,i.yg)("td",null,"Number of non-blank lines of comments per file."),(0,i.yg)("td",{rowspan:"3"},(0,i.yg)("ul",null,(0,i.yg)("li",null,"Low number of comments may indicate maintainability problems.")))),(0,i.yg)("tr",{class:"td-regular center-justified"},(0,i.yg)("td",null,"std.code.lines.comments"),(0,i.yg)("td",null,"Number of non-blank lines of comments per region.")),(0,i.yg)("tr",{class:"td-regular center-justified"},(0,i.yg)("td",null,"std.code.ratio.comments"),(0,i.yg)("td",null,"Ratio of non-empty lines of comments to non-empty lines of (code + comments) per region.")),(0,i.yg)("tr",{class:"td-regular center-justified"},(0,i.yg)("td",null,"std.code.complexity.cyclomatic"),(0,i.yg)("td",null,"McCabe cyclomatic complexity metric."),(0,i.yg)("td",{colspan:"2"},(0,i.yg)("ul",null,(0,i.yg)("li",null,"Identification of highly complex code for review and refactoring."),(0,i.yg)("li",null,"Preventing complex functions (complexity is a reason of many defects and a reason of expensive maintaintenance).")))),(0,i.yg)("tr",{class:"td-regular center-justified"},(0,i.yg)("td",null,"std.code.complexity.cyclomatic_switch_case_once"),(0,i.yg)("td",null,"Modified McCabe cyclomatic complexity metric which counts switch case constructs only once."),(0,i.yg)("td",{colspan:"2"},(0,i.yg)("ul",null,(0,i.yg)("li",null,"Identification of highly complex code for review and refactoring."),(0,i.yg)("li",null,"Preventing complex functions (complexity is a reason of many defects and a reason of expensive maintaintenance)."),(0,i.yg)("li",null,"Switch case statements might be considered to be easier to read than other constructs. This metric encourages developers to use switch case where applicable.")))),(0,i.yg)("tr",{class:"td-regular center-justified"},(0,i.yg)("td",null,"std.code.complexity.maxindent"),(0,i.yg)("td",null,"Maximum level of indentation of blocks within a region.",(0,i.yg)("pre",{class:"prettyprint"}))),(0,i.yg)("tr",{class:"td-regular center-justified"},(0,i.yg)("td",null,"std.code.magic.numbers"),(0,i.yg)("td",null,"Number of magic numbers. There is an option to exclude 0, -1 and 1 numbers from counting."),(0,i.yg)("td",null,"Magic numbers are dangerous. The ",(0,i.yg)("a",{href:"http://stackoverflow.com/questions/47882/what-is-a-magic-number-and-why-is-it-bad",target:"blank"},"discussion on stackoverflow")," explains why.")),(0,i.yg)("tr",{class:"td-regular center-justified"},(0,i.yg)("td",null,"std.code.todo.comments, std.code.todo.strings"),(0,i.yg)("td",null,"Number of TODO/FIXME/etc markers in comments and strings accordingly. There is an option to configure a list of markers."),(0,i.yg)("td",null,"Manage potentially incomplete work. If project manager dispatches issues only in a tracker tool, todo markers are lost in the source code. The metric could make these 'lost' issues visible.")),(0,i.yg)("tr",{class:"info center-justified"},(0,i.yg)("td",null,"std.general.proctime"),(0,i.yg)("td",null,"Seconds spent on processing a file."),(0,i.yg)("td",null,(0,i.yg)("ul",null,(0,i.yg)("li",null,"Monitor and profile Metrix++ tool's performance.")))),(0,i.yg)("tr",{class:"td-regular center-justified"},(0,i.yg)("td",null,"std.suppress"),(0,i.yg)("td",null,"An option enables collection of Metrix++ suppressions and 2 metrics: 'std.suppress:count' and 'std.suppress.file:count'. The first is number of suppressions per region. The second is the same but applies for file-scope metrics."),(0,i.yg)("td",null,(0,i.yg)("ul",null,(0,i.yg)("li",null,"Suppressing false-positives."),(0,i.yg)("li",null,"Managing the amount of suppressions. There should be no false-positives to suppress with the right metric, but there could be exceptions in specific cases. Managing suppressions is about managing exceptions. If there are many exceptional cases, maybe something is wrong with a metric or the application of a metric.")))),(0,i.yg)("tr",{class:"info center-justified"},(0,i.yg)("td",null,"std.general.procerrors"),(0,i.yg)("td",null,"Number of errors detected by Metrix++ code parser."),(0,i.yg)("td",null,(0,i.yg)("ul",null,(0,i.yg)("li",null,"Cleaning up errors to ensure reliable code scanning."),(0,i.yg)("li",null,"Errors, like mismatched brackets, may result in bad identification of regions.")))),(0,i.yg)("tr",{class:"td-regular center-justified"},(0,i.yg)("td",null,"std.code.maintindex.simple"),(0,i.yg)("td",null,"Simple variant of maintainability index - a measure of maintainability. It uses std.code.lines:code and std.code.complexity:cyclomatic metrics to evaluate level of maintainability. Lower value of this index indicates better level maintainability"),(0,i.yg)("td",null,"Identify code, which may benefit the most from refactoring.")))))}g.isMDXComponent=!0}}]);