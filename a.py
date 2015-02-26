import json

def a():
    print '1'
    yield 2
    print '3'
    yield 4
    print '5'
    yield 6
    print '7'

def b():
    print 'a'
    try:
        result = a()
        for x in result:
            yield x
        print 'b'
    except:
        print 'c'
    finally:
        print 'd'

result = b()
for x in result:
    print x

