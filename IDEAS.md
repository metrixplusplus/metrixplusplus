# Ideas

https://github.com/metrixplusplus/metrixplusplus/blob/master/IDEAS.md
This file captures all the ideas sparked in the past in relation to this project.

## New metrics
- Number of casts to void
- Count good stuff: const, pure, rodata, static
- Numver of dead symbols, files, functions, directories
- Detect and count source code within comments and #if 0
- Number of lines suppresed from static analysis, compiler warnings (useful when analysis is separated from new/modified code and untouched code)
- check presense of doxygen comments before a region
- Number of warnings by unused code detector
- number of breaks per case statement (motivation is to enforce break per case)
- Number of dead http links in strings and comments
- count not empty (pattern based) comments (to evaluate quality of comments to some extent.?)
- analysis of names, fucntions include english verbs, object under operation, etc., compliancy with naming conventions
- number of throwing exceptions or consider how it is linked with multiple returns and cyclomatic complexity
- number of violations to coding style (source from external tool?)
- Number of violations to coding standards (against external tool?)
- count declaration without initialisation
- count default:s per switches (to enforce default case)
- inheritance deepness, number of children, number of parent
- number of using 'using namespace' statements
- volume of changes in commit
- size of corresponding *.o file
- number of global variables (or extern symbols from binaries?)
- number of valgrind warnings
- count noname structs, namespaces, enums, classes
- Number of components per whole scanned system, size of a component
- number of logging statements
- number of asserts metric
- number of returns or span time between returns, code indent level in case of mutiple returns
- fan-in/fan-out (input/output asignments and flows) metric
- Number of basic blocks metric
- number of variable-members in public headers
- number of warnings by static analysis tool
- number of warnings by compiler
- Max line length metric
- radio of length of name of identifier to span time (more spanning variables should be named longer)
- Number of changes metric (frequently changing places may require attention to revision approaches)
- Number of magic strings metric
- Span time, life time metrics
- Number of delete, new (malloc/free) operators metric (to enforce none and use smart pointers)
- Arguments per function metric
- Preprocessor statements metric (differentiate conditional and non-conditional)
- Number of statements metric
- Simple Coupling metric (number of external identifiers used, number of times used by others)
- Code duplication metric (develop own code duplication detector?)
- Code coverage metric (integrate with other tools?)
- Add a way to collect usage data (Need some sort of feedback on usage trends. Datafile properties would be enough to feedback.)
- Exclude header files guards from std.code.lines:preprocessor metric. (To minimise number of false-positives for the metric.)
- Maximum number of pointer dereferencing per statement (Ref: Limit the use of pointers. Use no more than two levels of dereferencing per expression. http://spinroot.com/p10/rule9.html)
- Average number of assertions per function length (Ref: Use minimally two assertions per function on average. http://spinroot.com/p10/rule5.html)
- Metric for gotos, setjmp, longjmp (Inspired by: http://spinroot.com/p10/rule1.html)

## Other
- Add default useful views inside the db file. It turned out people browse DB file directly and want to have useful views available when DB file is opened.
- Web dashboard to browse trends.
- Support for other languages (Python, Matlabm Lua, sh, Ruby, etc..)
- Performance profile the tool (Need a way to enable cProfile module via configuration. Plus, need a measurement of time spent per plugin.)
- Handle kill signal and kill child process and release database file


