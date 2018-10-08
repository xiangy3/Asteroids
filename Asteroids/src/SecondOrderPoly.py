import math


def solveQuadraticEquation(a, b, c):
	discr = b * b - 4 * a * c
	if a == 0:
		if b == 0:
			return []
		else:
			return [-c / b]
	elif discr < 0:
		return []
	elif discr == 0:
		return [-b / (2 * a)]
	else:
		r1 = (-b - math.sqrt(discr)) / (2 * a)
		r2 = (-b + math.sqrt(discr)) / (2 * a)
		return [r1, r2]
	
class SecondOrderPoly:
	def __init__(self, a, b, c):
		self.a = float(a)
		self.b = float(b)
		self.c = float(c)
	
	def realRoots(self):
		return solveQuadraticEquation(self.a, self.b, self.c)

	def positiveRoots(self):
		roots = self.realRoots()
		result = []
		for root in roots:
			if root > 0:
				result.append(root)
		return result
				
	def smallestPostiveRoot(self):
		posRoots = self.positiveRoots()
		if len(posRoots) == 0:
			result = None
		else:
			result = posRoots[0]
		return result

	def __str__(self):
		return "%+dx^2%+dx%+d" % (self.a, self.b, self.c)
	
def test(A, B, C):
	poly = SecondOrderPoly(A, B, C)
	print(poly)
	print(poly.realRoots())
	print(poly.positiveRoots())
	print(poly.smallestPostiveRoot())

if __name__ == "__main__":
	test(1, 2, 3)
	test(0, 2, 1)
	test(3, 2, -1)
	test(1, 0, 0)
