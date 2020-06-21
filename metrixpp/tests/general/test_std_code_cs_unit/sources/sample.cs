

public class example
{
    protected List<int> testfunction1(string text1)
    {
        List<int> numbers = new List<int>();
        return numbers;
    }

    protected List<T> testfunction2<T>(string text1)
    {
        List<int> numbers = new List<int>();
        return numbers;
    }

    protected int testfunction3<T>(string text1)
    {
        List<int> numbers = new List<int>();
        return numbers;
    }

    protected int testfunction4(string text1)
    {
        List<int> numbers = new List<int>();
        return numbers;
    }

    protected int testfunction5<T, S>(string text1)
    {
        List<int> numbers = new List<int>();
        return numbers;
    }

    protected IDictionary<T, S> testfunction6<T, S>(string text1)
    {
        List<int> numbers = new List<int>();
        return numbers;
    }

    protected IDictionary<T, S> testfunction7<T,
        S>(string text1)
    {
        List<int> numbers = new List<int>();
        return numbers;
    }

    protected IDictionary<T, IList<S>> testfunction8<T,
        S>(string text1)
    {
        List<int> numbers = new List<int>();
        return numbers;
    }

    protected IList<T> testfunction9<T,    S>(string text1)
    {
        List<int> numbers = new List<int>();
        return numbers;
    }

    protected IList<T> Interface.testfunction10<T, S>(string text1)
    {
        List<int> numbers = new List<int>();
        return numbers;
    }

    protected IList<T> Interface<T>.testfunction11<T, S>(string text1)
    {
        List<int> numbers = new List<int>();
        return numbers;
    }

    protected IList<T> Interface<T, S>.testfunction12(string text1)
    {
        List<int> numbers = new List<int>();
        return numbers;
    }

    protected IList<T> Interface<T, S>.testfunction13<T>(string text1)
    {
        List<int> numbers = new List<int>();
        return numbers;
    }

    protected IList<T> Interface<T>.testfunction14<T, S>(string text1)
    {
        List<int> numbers = new List<int>();
        return numbers;
    }

    protected IList<T> Interface<T,S>.testfunction15<T, S>(string text1)
    {
        List<int> numbers = new List<int>();
        return numbers;
    }

    protected IList<T> Interface<T, S>.testfunction16 <T>(string text1)
    {
        List<int> numbers = new List<int>();
        return numbers;
    }

    protected IList<T> Interface <T, S>. testfunction17<T>(string text1)
    {
        List<int> numbers = new List<int>();
        return numbers;
    }

    class testClass1
    {
    }

    class testClass2
    {
    }

    class testClass3<T>
    {
    }

    class testClass4 <T>
    {
    }

    class testClass5<T, S>
    {
    }

    class testClass6<T,
        S>
        where T: class
        where S: class
    {
    }

    class testClass7 < T>
        where T : class
    {
    }

    protected IList<T> Interface<T, S, A, B,   C>.testfunction18<T, S, A, V, F, G>(string text1)
    {
        List<int> numbers = new List<int>();
        return numbers;
    }

}
