class P:

    def __init__(self, x):
        self.x = x

    @property
    def x(self):
        print("getter method called")
        return self._x

    @x.setter
    def x(self, x):
        if x < 0:
            print("setter method called")
            self._x = -1 * x
        else:
            print("setter method called")
            self._x = x


p1 = P(-15)
print(p1.x)


class C:

    def __init__(self, x):
        self.x = x

    @property
    def x(self):
        print("getter method called")
        return self._x

    @x.setter
    def x(self, x):
        if x < 0:
            raise ValueError("x is not positive number")
        print("setter method called")
        self._x = x

    @x.deleter
    def x(self):
        print("deleter method called")
        del self._x


c2 = C(15)
print(c2.x)


# c1 = C(-15)
# print(c1.x)


class E:

    def __init__(self, x):
        self.x = x

    @property
    def x(self):
        print("getter method called")
        return self._x

    @x.setter
    def x(self, x):
        if x < 0:
            self._x = 0
        else:
            self._x = x

    @x.deleter
    def x(self):
        print("deleter method called")
        del self._x


e2 = E(22)
print(e2.x)
e1 = E(-15)
print(e1.x)
del e1.x
print(e1.x)
