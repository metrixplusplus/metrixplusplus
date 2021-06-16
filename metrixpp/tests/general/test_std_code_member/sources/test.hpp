#include <iostream>

extern int g_global;

extern int Foo();
extern void Bar(int x);

template <class FooBar>
class TestClass : public FooIf
{
  public:
    TestClass();
    virtual ~TestClass() = default;

    virtual void pure_virtual_method(int a) = 0 ;
    void virtual_override(int a) override;
    void override_as_pure_virtual(int a) override = 0;

    template <typename T>
    void function_declaration(T a, int b, int c);

    void function_definition()
    {


    }

    int a;
    long int b;
    char const* c;
    const int& d;
    int e = 0;
    const int f = 42;
    int gg;
    char const* const h;

    std::string m_string;
    static ::std::vector<std::function<int(void)>> const& m_vect;
    Foo::Bar::bla m_gar;

    static std::string& ref;
    const std::string* ptr;

    std::string const& blaa77h;

    ::std::gar::function<void()> fptr;

    int field[100];
};

// bit fields
struct sTest
{
    int x;
    unsigned char y;
    int32_t z;

    unsigned char b1 : 7 = 42;
    unsigned char : 1;
    unsigned char b2 : 8;
};


