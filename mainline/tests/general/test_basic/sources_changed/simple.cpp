

// Just produce any code in order to test basic workflow
namespace hmm
{

#define old_prep
#define new_prep

class A
{

	A()
	{
		/* first funtion */
		this->m_me88er = 10;
		if (a & b)
		{
			for (int i = 0; i < 0 && i > 0; i++)
			{
				int a; // right?
			}
		}
	}

	int func(int param = 5)
	{
		class embeded
		{
			embeded()
			{
				int a = 10;
				if (true)
				{
					// again crazy
				}

				while (a == b); // regressed
			}
		};
		if (a);
	}

	int never(int how_long = 999)
	{
		while(true)
		{

		}
		return 2; // slightly modified
	}

	char new_func()
	{
		// simple
	}

	char new_func_complex()
	{
		if (true) {}
		return 'A';
	}

	/* metrix++: suppress std.code.complexity:cyclomatic */
	char new_func_complex_but_suppressed()
	{
		if (true && false)
		{
			return 'A';
		}
		return 'B';
	}

	int m_me88er = 10;
};

}
