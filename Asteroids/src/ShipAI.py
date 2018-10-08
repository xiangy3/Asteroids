from panda3d.core import Vec2, Point2
from MovingObject import MovingObject, normalizeDegrees
import math

from panda3d import bullet
from matplotlib.cbook import Null

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
		
		self.hittedAst = []
		self.count = 0
		self.dieFrame = 0
	# Called when a new game of asteroids is started.
	def newGame(self):
		self.pts = 0
		self.hittedAst = []
	
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
	

		


	# This AI will simply point the ship toward the first asteroid in the
	# list. Shots are never fired by this AI.
	def trackingAI(self, asteroids, heading, framesToFire):
		if len(asteroids) == 0: return (False, 0)
		dirToAsteroids = normalizeDegrees(math.degrees(math.atan2(asteroids[0].pos.getY(), asteroids[0].pos.getX())))
		if dirToAsteroids >= heading: 
			if abs(dirToAsteroids - heading)  > 180 :
				return (False, -1)
			elif abs(dirToAsteroids - heading)  < 180:
				return (False, +1)
		elif dirToAsteroids <= heading:
			if abs(dirToAsteroids - heading)  > 180 :
				return (False, 1)
			elif abs(dirToAsteroids - heading)  < 180:
				return (False, -1)
			
	
		
	 
	# This AI will never turn. It will simply fire a bullet if the bullet
	# will intersect with the first asteroid in the list. It is acceptable to shoot
	# and miss when the intersection falls off the window.
	def opportunisticAI(self, asteroids, heading, framesToFire):
		if len(asteroids) == 0: return (False, 0)
		bullet=MovingObject(1,Point2(0,0),90,self.bulletSpeed,self.bulletRad)
		if(asteroids[0].collideWithObject(bullet)):
			return (True, 0)
		return (False, 0)

	# This AI will shoot at the first asteroid in the list, when a shot will be successful.
	# If a shot is not possible, the ship will turn toward the first asteroid in the list.
	def aggressiveAI(self, asteroids, heading, framesToFire):
		if len(asteroids) == 0: return (False, 0)
		
		ship = MovingObject(1,origin,heading,0,8)
		if(asteroids[0].collideWithObject(ship)):
			return self.killAsteroid(asteroids[0],heading,framesToFire)
	
	def getAICommand(self, asteroids, heading, framesToFire):
		
		
		if len(asteroids) == 0: return (False, 0)
		
		ship = MovingObject(1,origin,heading,0,10)
		
		
		firstAttack = []
		
		secondAttack = []
		

		for asteroid in asteroids:
			nextDtPos = asteroid.pos+asteroid.vel*self.dt
			if (nextDtPos - ship.pos).length()< asteroid.rad+ship.rad:
				return None
				
			elif(asteroid.collideWithObject(ship)):
				asteroidInfo = (asteroid,asteroid.collideWithObject(ship))
				firstAttack.append(asteroidInfo)
			else:
				asteroidInfo = (asteroid,asteroid.speed/asteroid.rad)
				secondAttack.append(asteroidInfo)
		
		newFirstAttack = sorted(firstAttack, key=lambda astInfo: astInfo[1])
		newSecontAttack = sorted(secondAttack, key=lambda astInfo: astInfo[1],reverse = True)

		
		for asteroidInfo in newFirstAttack:
				if(asteroidInfo!=None):
					#newFirstAttack.pop()
					if not self.hittedAst.__contains__(asteroidInfo[0].id):
						return self.killAsteroid(asteroidInfo[0],heading,framesToFire,asteroids)
	
		for asteroidInfo in newSecontAttack:
				if(asteroidInfo!=None):
					#newSecontAttack.pop()
					if not self.hittedAst.__contains__(asteroidInfo[0].id):
						return self.killAsteroid(asteroidInfo[0],heading,framesToFire,asteroids)
		
			
		return (False, 0)
		
	def killAsteroid(self,asteroid,heading,framesToFire,asteroids):
		
		
		bullet=MovingObject(1,origin,heading,self.bulletSpeed,self.bulletRad)
		buttleTime = asteroid.collideWithObject(bullet)
		if(buttleTime != None):
			newPos = asteroid.pos + asteroid.vel * buttleTime
			if newPos.getX() < -350 or newPos.getX() >= 350 or newPos.getY() <= -350 or newPos.getY() >= 350:
				return (False,0)
			else:
				self.bulletCollion(bullet,buttleTime,asteroids,asteroid,framesToFire)
				self.count +=1
				if self.count == 5:
					self.hittedAst=[]
					self.count = 0
				return (True,0)
				

		else :
			dirToAsteroids = normalizeDegrees(math.degrees(math.atan2(asteroid.pos.getY(), asteroid.pos.getX())))
			if dirToAsteroids > heading: 
				if abs(dirToAsteroids - heading) > 180 :
					return (False, -self.turnRate)
				elif abs(dirToAsteroids - heading)< 180:
					return (False, self.turnRate)
			else:
				if abs(dirToAsteroids - heading) > 180 :
					return (False, self.turnRate)
				elif abs(dirToAsteroids - heading) < 180:
					return (False, -self.turnRate)
				
	def bulletCollion(self,bullet,buttleTime,asteroids,asteroid,framesToFire):
		actualId = None
		newId = None
		smallestTime = buttleTime
		
		for closestAst in asteroids:
			newColTime = closestAst.collideWithObject(bullet)
			if(newColTime != None and newColTime < smallestTime and not self.hittedAst.__contains__(asteroid.id)):
				smallestTime = newColTime
				newId = closestAst.id
		if(newId != None):
			actualId = newId
		else:
			actualId = asteroid.id
			
		self.hittedAst.append(actualId)
