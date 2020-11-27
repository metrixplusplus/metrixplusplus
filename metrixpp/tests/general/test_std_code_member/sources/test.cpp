#include "test.hpp"
#include <iostream>

// false positive: the parser cannot identify these 3 lines as a single statement
   typedef typename boost::intrusive::
      pointer_traits<void_pointer>::template
         rebind_pointer<block_ctrl>::type                         block_ctrl_ptr;

using namespace std;
using std::cout;

int g_global = 0;

const int RC_SUCCESS = 0;

const std::array<int, 5> values;

void FuncWithPrototype(int b);

int Foo()
{
    int b = 3;
    return ++b;
}

void Bar(int x)
{

}

TestClass::TestClass()
{

}

void TestClass::virtual_override(int a)
{

}

template <class T>
void TestClass::function_declaration(T a, int b, int c)
{
    T var;
}

int main()
{
    int a = 43;

    Foo();

    return RC_SUCCESS;
}

void FuncWithPrototype(int b)
{

}
