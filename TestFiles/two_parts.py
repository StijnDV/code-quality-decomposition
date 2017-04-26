def two_clear_parts(args1, args2):
    global a
    global b
    a = a + 1
    b = 25
    test = args1
    result1 = args1 * 5
    for res in test:
        if res:
            result1 += res
        else:
            result1 = result1 - res
    result2 = args2 + 25
    result2 = result2 * 5
    print(test)
    return (result1, result2)

def two_not_so_clear_parts(args1, args2):
    test = args1
    result1 = args1 * 5
    for res in test:
        if res:
            result1 += res
        else:
            result1 = result1 - res

    result2 = args2 + 25
    result2 = result2 * 5 + result1

    return result2