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


c1 = C(-15)
print(c1.x)
c2 = C(15)
print(c2.x)
