def func(x):
    print('x is',x)
    x=2
    print('changed local x to',x)

x=50 #'50'
func(x)
print('x is still',x)


def func_global():
    global x
    print('x is',x)
    x=2
    print('changed global x to',x)

func_global()
print('x is still',x)