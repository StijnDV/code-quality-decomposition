def lots_of_nesting(a, b, c):
    def iner_func(a, b, c):
        print a, b, c
    if a:
        print a
        if b:
            print a
            if c:
                print a
                for x in b:
                    print x
    else:
        if c:
            print "No"
        else:
            print "Yes"
        if b:
            print c
            for z in c:
                iner_func(z, z, c)
