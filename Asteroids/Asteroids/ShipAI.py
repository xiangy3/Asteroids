from panda3d.core import Vec2, Point2
from MovingObject import MovingObject, normalizeDegrees
import math

origin = Vec2(0, 0)

# this function can be used to display all the asteroid's values to the screen
def dumpAsteroids(rocks):
	print("Asteroids:")
	for rock in rocks:
		print(rock)
	print("------------------")
		
class ShipAI:
	# Called to create a new player
	def __init__(self, fieldSz, dt, turnRate, bulletSpeed, bulletRepeat, bulletRad, astSpeeds, astDiams,
					totalFrames, points):
		self.fieldSz = fieldSz
		self.dt = dt
		self.turnRate = turnRate
		self.bulletSpeed = bulletSpeed
		self.bulletRepeat = bulletRepeat
		self.bulletRad = bulletRad
		self.astSpeeds = astSpeeds
		
		self.astRads = []
		for diam  in astDiams:
			self.astRads.append(diam/2)
			
		self.totalFrames = totalFrames
		self.points = points
	
	# Called when a new game of asteroids is started.
	def newGame(self):
		self.pts = 0
	
	# Called to get the player's next command.
	#
	# The return value must be a 2-tuple
	# of the form (fire, dir). Where dir = {negative, 0, positive} to indicate turn CCW, don't
	# turn, or turn CW. fire is a boolean value to indicate whether to fire a
	# bullet. If this is True, a bullet will be fire, but only if the bullet repeat
	# rate is not exceeded. To execute the "shield", return None
	#
	# The inputs are:
	# asteroids -- array of MovingObjects, one for each asteroid on screen
	# heading -- the ship's heading (0 degrees is down +x), degrees.
	# framesToFire -- num non-firing frames needed before next bullet.
	
	def getAICommand(self, asteroids, heading, framesToFire):
		# dumpAsteroids(asteroids)
		# Fill this in for homework assignment
		return (True, 0)

	# This AI will simply point the ship toward the first asteroid in the
	# list. Shots are never fired by this AI.
	def trackingAI(self, asteroids, heading, framesToFire):
		if len(asteroids) == 0: return (False, 0)
		
		directionToAsteroid = normalizeDegrees(math.degrees(math.atan2(asteroids[0].pos.getY()
																	, asteroids[0].pos.getX())))
		
		if directionToAsteroid > heading:
			if directionToAsteroid - heading > 180:
				return (False, -1)
			else:
				return(False, +1)
		else:
			if heading - directionToAsteroid > 180:
				return (False, +1)
			else:
				return (False, -1)
	
	# This AI will never turn. It will simply fire a bullet if the bullet
	# will intersect with the first asteroid in the list. It is acceptable to shoot
	# and miss when the intersection falls off the window.
	def opportunisticAI(self, asteroids, heading, framesToFire):
		if len(asteroids) == 0: return (False, 0);
		
		bullet = MovingObject(1, Point2(0, 0), heading, self.bulletSpeed, self.bulletRad);
		
		if asteroids[0].collideWithObject(bullet):
			return (True, 0)
		return (False, 0)

	# This AI will shoot at the first asteroid in the list, when a shot will be successful.
	# If a shot is not possible, the ship will turn toward the first asteroid in the list.
	def aggressiveAI(self, asteroids, heading, framesToFire):
		if len(asteroids) == 0: return (False, 0)
		
		bullet = MovingObject(1, Point2(0, 0), heading, self.bulletSpeed, self.bulletRad);
		
		if asteroids[0].collideWithObject(bullet):
			return (True, 0)
		else:
			directionToAsteroid = normalizeDegrees(math.degrees(math.atan2(asteroids[0].pos.getY()
																	, asteroids[0].pos.getX())))
			if directionToAsteroid > heading:
				if directionToAsteroid - heading > 180:
					return (False, -1)
				else:
					return(False, +1)
			else:
				if heading - directionToAsteroid > 180:
					return (False, +1)
				else:
					return (False, -1)








