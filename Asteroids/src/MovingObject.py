from panda3d.core import Vec2
from math import sin, cos, radians, sqrt
from SecondOrderPoly import SecondOrderPoly
from pandac.PandaModules import Point2

def normalizeDegrees(H):
	return H % 360

class MovingObject:
	def __init__(self, idNum, pos, heading, speed, rad):
		self.id = idNum
		self.pos = pos
		self.speed = speed
		rads = radians(heading)
		self.vel = Vec2(cos(rads), sin(rads)) * speed
		self.rad = rad
	
	def distance(self, other):
		return (self.pos - other.pos).length()
	
	def update(self, dt):
		self.loc += self.vel * dt
	
	def __str__(self):
		return "ID=%d Pos=%s Vel=%s Speed=%f Radius=%f" % \
		        (self.id, self.pos.__str__(), self.vel.__str__(), self.speed, self.rad)
	
	def collideWithObject(self, other):
		collideDist = self.rad + other.rad
		if self.distance(other) <= collideDist:
			return (0,)
		(x1, y1) = (self.pos[0], self.pos[1])
		(x2, y2) = (other.pos[0], other.pos[1])
		(dx1, dy1) = (self.vel[0], self.vel[1])
		(dx2, dy2) = (other.vel[0], other.vel[1])
		(X, Y) = (x1 - x2, y1 - y2)
		(DX, DY) = (dx1 - dx2, dy1 - dy2)
		a = DX * DX + DY * DY
		b = 2 * (X * DX + Y * DY)
		c = X * X + Y * Y - collideDist * collideDist
		poly = SecondOrderPoly(a, b, c)
		result = poly.smallestPostiveRoot()
		return result
	
	def collideWithPointAtOrigin(self):
		x = self.pos[0]
		y = self.pos[1]
		dx = self.vel[0]
		dy = self.vel[1]
		A = dx * dx + dy * dy
		B = 2 * (x * dx + y * dy)
		C = x * x + y * y - self.rad
		poly = SecondOrderPoly(A, B, C)
		result = poly.realRoots()
		return result

if __name__ == "__main__":
	a1 = MovingObject(0, Point2(0,0), 45, sqrt(2), 1)
	a2 = MovingObject(0, Point2(3,0), 90, 1, 1)
	print(a1.collideWithObject(a2))
	
	a1 = MovingObject(0, Point2(0,0), 135, sqrt(2), 1)
	a2 = MovingObject(0, Point2(3,0), 45, sqrt(2), 1)
	print(a1.collideWithObject(a2))	
	
	a1 = MovingObject(0, Point2(-3, -3), 45, sqrt(8), 1)
	a2 = MovingObject(0, Point2(0,0), 45, sqrt(2), 1)
	print(a1.collideWithObject(a2))