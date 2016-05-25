import os


class Foo(object):
    """Some doc"""
    CLASS_ATTR = {"dict": 1,
                  "bla": "foobar"}

    def __init__(self, arg):
        """initializaion"""
        self.arg = arg

    def method(self, x, y):
        """very important method"""

        def inner_funtion(x, y):
            for i in y:
                x = x + i

            result = y[:]
            result.append(x)
            return result

        result = None
        result2 = """\
multiline
string
the
annoying
bastard"""

        if self.arg < 100:
            result = inner_funtion(x, y)

        return result if result else result2

def main():
    instance = Foo(10)
    print(os.path.curdir, instance.method(2, [1, 2, 3]))

if __name__ == "__main__":
    main()
