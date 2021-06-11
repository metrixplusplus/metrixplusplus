

// Just produce any code in order to test basic workflow
namespace hmm
{

#define old_prep

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
			}
		};
		if (a);
	}

	int func_to_be_removed_in_new_sources(int param = 5)
	{
		class embeded
		{
			embeded()
			{
				int a = 10;
				if ("text")
				{
					/* again crazy */
				}
			}
		};
		if (a && b);
	}

	int never(int how_long = 999)
	{
		while(true)
		{

		}
		return 1;
	}

    virtual int pure_virtual_method() = 0;
    int pure_virtual_overrider() override = 0;

	int m_me88er = 10;

    int hex_number = 0xaBc78;
    unsigned int binary_number = 0b00110u;
    unsigned long long int octal_number = 074uLL;
    unsigned long long int different_order = 123llU;
    long int just_l = 42l;
    int one_separator = 123'456;
    int two_separators = 123'456'789;

    constexpr int const_hex_number = 0xaBc78;
    const unsigned int const_binary_number = 0b00110u;
    const unsigned long long int const_octal_number = 074uLL;
    const unsigned long long int const_different_order = 123llU;
    const long int const_just_l = 42l;
    constexpr int one_separator = 123'456;
    const int two_separators = 123'456'789;
};

}
