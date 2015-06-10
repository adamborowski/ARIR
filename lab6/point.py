class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __div__(self, other):
        return Point(self.x / other, self.y / other)

    def __str__(self):
        return "({:5.2f},{:5.2f})".format(self.x, self.y)
    def __repr__(self):
        return self.__str__()