
@attribute_should_not_be_a_function("word")
class A
{
	@nested_attribute_should_not_be_a_function("word")
	int function(int parameter)
	{
		switch(parameter)
		{
			case 1:
				break;
			case 2:
				break;
			case 3:
				break;
			case 4:
				break;
			default:
				break;
		}
	}
}