/* comment here per global region
 *
 *	metrix++:	suppress std.code.length:total
 *	metrix++: suppress std.general:size
 *	metrix++: suppress std.general:size intentional duplicate
 */


/*metrix++: suppress	std.code.length:total*/
int func()
{
	/* comment here */
}

int func2()
{
	/*metrix++: suppress std.code.length:total*/
}

/* metrix++: suppress std.code.length:total */
int func3()
{
	/* metrix++: suppress std.code.length:total*/
}


/* bla-bla */
       /* metrix++: suppress std.code.length:total */
/* bla-bla */
int func4()
{
	/* metrix++: suppress std.code.length:total*/
}

/* metrix++: suppress std.code.length:total */
struct cl1
{

};

struct cl2
{
	/* metrix++: suppress std.code.length:total*/

};

// bla-bla
//metrix++: suppress std.code.length:total
// bla-bla
struct cl3
{

};

/* bla-bla-bla */
struct no_suppress_cl
{

};

/* bla-bla-bla */
int nu_suppress_func()
{
	/* bla-bla-bla */
}

struct cl2
{
	/* metrix++: suppress std.code.length:total per class */

	/* metrix++: suppress std.code.length:total per function */
	int func4()
	{

	}

	int func_no_suppress_within_struct()
	{

	}
};

/* metrix++: suppress invalid:metric */
struct suppresed_for_invalid_metric
{

};

/* metrix++: suppress std.code.length:invlaid_metric */
struct suppresed_for_invalid_metric
{

};

/* metrix++: suppress invalid:metric */
/* metrix++: suppress std.code.length:total */
struct suppressed_for_size_and_invalid_metric
{

};

/* metrix++: suppress invalid:metric */
/* metrix++: suppress std.code.length:total */
/* metrix++: suppress std.code.complexity:cyclomatic */
int suppressed_for_size_and_complexity_and_invalid_metric()
{
	if (1) return;
}

// metrix++: suppress std.code.length:total asdas
// metrix++: suppress std.code.complexity:cyclomatic adsad
int func7()
{
	if (1) return;
}

// metrix++: suppress std.code.complexity:cyclomatic adsad
int nu_suppress_for_size()
{
	if (1) return;
}

// metrix++: suppress std.code.length:total adsad
int no_suppress_for_cyclomatic_complexity()
{
	if (1) return;
}

// metrix++: suppress std.code.length:total long-long
// description why it was suppressed
// metrix++: suppress std.code.complexity:cyclomatic
int func8()
{
	if (1) return;
}

/* metrix++: suppress std.code.length:total long-long */
/* description why it was suppressed */
/* metrix++: suppress std.code.complexity:cyclomatic */
int func9()
{
	if (1) return;
}

// metrix++: suppress std.code.complexity:cyclomatic adsad
int bad_suppress_for_size()
{
	// metrix++: suppress std.code.length:total

	if (1) return;
}

/* metrix++: suppress std.code.length:total long-long
 * description why it was suppressed
 * metrix++: suppress std.code.complexity:cyclomatic */
int func10()
{
	if (1) return;
}

/* metrix++: suppress std.code.length:total
 * metrix++: suppress std.code.length:total */
int duplicate_suppression_of_size()
{
}

/* metrix++: suppress std.general:size intentional suppression per file metric
 * metrix++: suppress std.code.length:total */
int bad_suppression_of_file_size()
{
}

