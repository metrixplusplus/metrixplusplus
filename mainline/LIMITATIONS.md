# Known Limitations 

+ C/C++, C# and Java parsers do not recognise definition of functions or overloaded operators
in case of embeded comments after identifier name and before the list of arguments.

	- This function is not detected by Metrix++:
	
			int getMax /* undesarable comment */ (int* array, int length)
			{
				/* ... */
			}
	  
	- This function is detected:
	
			int getMax(int* array, int length) /* here is fine */
			{
				/* ... */
			}

+ C/C++ parser does not recognise comments within preprocessor statements.
These comments are considered to be parts of a define.

	- This comment is not recognized by Metrix++:
	
			#define GET_MAX(a, b)	   \
				/*					  \
				 * This macros returns  \
				 * maximum from a and b \
				 */					 \
				((a > b) ? a : b)
	
	- This comment is recognised:
	
			/*
			 * This macro returns maximum from a and b
			 */
			#define GET_MAX(a, b) \
				((a > b) ? a : b)

+ C# parser does not recognise getters/setters for properties, if there is a comment before a block.
  
	- This function is not detected by Metrix++: | :

			get /* undesarable comment */
			{
				/* ... */
			}

	- This function is detected:

			get
			{	/* here comment is fine */
				/* ... */
			}


+ Java parser does not recognise anonymous inner classes.

+ C/C++, C# and Java parsers do not recognise definition of classes/structs/namespaces/interface)
in case of embeded comments after keyword and identifier name.

	- This class is not detected by Metrix++

			class /* comment */ MyClass
			{
				/* ... */
			}

	- This class is detected:

			class MyClass /* here is fine */
			{
				/* ... */
			}

+ Java parser does not support parsing of identifiers which have got unicode symbols in name.
