class A(object):
    def __init__(self, x,y):
		self.x = x
		self.y = y

    def hello(self):
        print "HellO"

    def test_func(self, inp):
        return self



l = A(1,2)
l2 = A (2,3)
print l
print l2
k = l.test_func(12)
k2 = l2.test_func(12)
print k
print k2