var = 5
factor = 20
result = var * factor
result = 24
result = 50
if result < 200:
    a = result
    print var

def test_func_bad(arg1, arg2, arg3):
    x = 30
    global var
    var = 5
    print arg2
    print arg3
    if arg1 == 2:
        return arg2
        def local_fun(arg1, arg2, arg3):
            print arg1, arg3
    return arg1 + arg2 + arg3

def test_func_maybe_bad(arg1, arg2, arg3):
    global result
    result = arg1 + arg2 + arg3
    print result

def test_func_good_print(arg1, arg2, arg3):
    print arg1, arg2, arg3

def test_func_good_return(arg1, arg2, arg3):
    output = arg1 + arg2 + arg3
    return output

def test_helper():
    global a
    print a