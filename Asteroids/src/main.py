#!/usr/bin/env python
# Based largely on the code from:
#
# Author: Shao Zhang, Phil Saltzman, and Greg Lindley
# Last Updated: 2015-03-13
#
# This tutorial demonstrates the use of tasks. A task is a function that
# gets called once every frame. They are good for things that need to be
# updated very often. In the case of asteroids, we use tasks to update
# the positions of all the objects, and to check if the bullets or the
# ship have hit the asteroids.
#
# Note: This definitely a complicated example. Tasks are the cores of
# most games so it seemed appropriate to show what a full game in Panda
# could look like.

from direct.showbase.ShowBase import ShowBase
from pandac.PandaModules import LPoint3, LVector3, OrthographicLens, Point2, \
								TextNode, Vec3, TransparencyAttrib, loadPrcFileData
import random
from direct.task import Task
from math import sin, cos, pi, degrees, atan2, radians
import sys
from ShipAI import ShipAI
from MovingObject import MovingObject, normalizeDegrees
from direct.interval.IntervalGlobal import Func, Wait, Sequence

def find(lst, val):
	for i in range(len(lst)):
		if lst[i] == val:
			return i
	return i

def touching(obj1, obj2):
	rad1 = obj1.getScale().getX() / 2
	rad2 = obj2.getScale().getX() / 2
	dist = (obj1.getPos() - obj2.getPos()).length()
	return dist <= rad1 + rad2
	
SEEDS = [12513,2234,23,3,4342,          # 20 random seeds, to ensure 20 repeatable
         954,233,786,4545423,1121,      # games.
         3426,976443,20452,503,2237,
         67121,36767,743,212,7524]

NUM_GAMES = len(SEEDS)

FIELD_SZ = 700					# dimensions of square window
NUM_FRAMES = 2000				# number of frames in a game
DT = 0.05						# seconds [virtual] for each frame
AI_TIME = 0.05					# time allowed for AI

INIT_NUM_ASTEROIDS = 10			# number of asteroids to start game

TURN_RATE = 4					# degrees in one turn

BULLET_REPEAT = 8				# frames to wait between firings
BULLET_SPEED = 200				# speed of fired bullet
BULLET_RAD = 2					# radius of bullet

INIT_AST_SPEED = 100
AST_SPEED_FACTOR = 1.5

INIT_AST_RAD = 80
AST_SZ_FACTOR = 0.5

SHIP_RAD = 8					# radius of ship
SHIELD_LIFE = 200				# frames of immunity
PTS = [2, 4, 10, -1]			# points for L, M, S, shots

# Computed constant quantities, don't change
AST_DIAMS = [2*INIT_AST_RAD, 2*int(INIT_AST_RAD*AST_SZ_FACTOR), 2*int(INIT_AST_RAD*AST_SZ_FACTOR*AST_SZ_FACTOR)]
AST_SPEEDS = [INIT_AST_SPEED, int(INIT_AST_SPEED*AST_SPEED_FACTOR), int(INIT_AST_SPEED*AST_SPEED_FACTOR*AST_SPEED_FACTOR)]

loadPrcFileData("", "win-size %d %d" % (FIELD_SZ, FIELD_SZ))

# This helps reduce the amount of code used by loading objects, since all of
# the objects are pretty much the same.
def loadObject(tex=None, pos=LPoint3(0, 0), scale=1, transparency=True):
	global loader, camera, render
	# Every object uses the plane model and is parented to the camera
	# so that it faces the screen.
	obj = loader.loadModel("models/plane")
	obj.reparentTo(render)
	obj.setP(-90)
	# Set the initial position and scale.
	obj.setPos(pos.getX(), pos.getY(), 0)
	obj.setScale(scale)
	
	# This tells Panda not to worry about the order that things are drawn in
	# (ie. disable Z-testing).  This prevents an effect known as Z-fighting.
	obj.setBin("unsorted", 0)
	obj.setDepthTest(False)
	
	if transparency or True:
		# Enable transparency blending.
		obj.setTransparency(TransparencyAttrib.MAlpha)
	
	if tex:
		# Load and set the requested texture.
		tex = loader.loadTexture('textures/' + tex)
		obj.setTexture(tex, 1)
	
	return obj

def genTextNode(T):
	global aspect2d
	txt = TextNode(T)
	txt.setText(T)
	txtNode = aspect2d.attachNewNode(txt)
	txtNode.setScale(0.1)
	txtNode.setPos(Vec3(-1.0, 0, 0.92))
	txt.setTextColor(1,0,0,1)
	return txt

class AsteroidsDemo(ShowBase):

	def __init__(self):
		global taskMgr, base
		# Initialize the ShowBase class from which we inherit, which will
		# create a window and set up everything we need for rendering into it.
		ShowBase.__init__(self)
		
		lens = OrthographicLens()
		lens.setFilmSize(FIELD_SZ, FIELD_SZ)
		base.cam.node().setLens(lens)

		# This code puts the standard title and instruction text on screen
	#	self.scoreBrd = genLabelText("Test", 0)
		self.scoreBrd = genTextNode("TEST")

		# Disable default mouse-based camera control.  This is a method on the
		# ShowBase class from which we inherit.
		self.disableMouse()
		
		# point camera down onto x-y plane
		camera.setPos(LVector3(0, 0, 1))
		camera.setP(-90)
		
		# Load the background starfield.
		self.setBackgroundColor((0, 0, 0, 1))
		self.bg = loadObject("stars.jpg", scale=FIELD_SZ, transparency=False)
		
		# Load the ship and set its initial velocity.
		self.ship = loadObject("ship.png", scale=2*SHIP_RAD)
		self.setTag("velocity", self.ship, LVector3.zero())
		
		self.accept("escape", sys.exit)  # Escape quits
		self.accept("space", self.endGame, [0])  # Escape quits
		
		# Now we create the task. taskMgr is the task manager that actually
		# calls the function each frame. The add method creates a new task.
		# The first argument is the function to be called, and the second
		# argument is the name for the task.  It returns a task object which
		# is passed to the function each frame.
		self.gameTask = taskMgr.add(self.gameLoop, "gameLoop")
		
		# Stores the time at which the next bullet may be fired.
		self.nextBullet = 0.0
		
		# This list will stored fired bullets.
		self.bullets = []
		
		self.shipAI = ShipAI(FIELD_SZ, AI_TIME, TURN_RATE,
							BULLET_SPEED, BULLET_REPEAT, BULLET_RAD,
							AST_SPEEDS, AST_DIAMS, NUM_FRAMES, PTS)
		self.currFrame = 0
		self.currGame = 0
		self.totalScore = 0
		self.bullets = []
		self.asteroids = []
		self.ship.setColor(1,1,1)
		self.newGame()
		self.shieldActive = False
		self.shieldFrames = 0
	
	def spawnAsteroids(self):
		# Control variable for if the ship is alive
		self.alive = True
		self.asteroids = []  # List that will contain our asteroids
		
		for i in range(INIT_NUM_ASTEROIDS):
			# This loads an asteroid. The texture chosen is random
			# from "asteroid1.png" to "asteroid3.png".
			asteroid = loadObject("circle.png", scale=AST_DIAMS[0])
			self.asteroids.append(asteroid)
			
			# This is kind of a hack, but it keeps the asteroids from spawning
			# near the player.  It creates the list (-20, -19 ... -5, 5, 6, 7,
			# ... 20) and chooses a value from it. Since the player starts at 0
			# and this list doesn't contain anything from -4 to 4, it won't be
			# close to the player.
			WC_SZ = FIELD_SZ/2
			asteroid.setX(random.choice(tuple(range(-WC_SZ, -WC_SZ/2)) + tuple(range(WC_SZ/2, WC_SZ))))
			# Same thing for Y
			asteroid.setY(random.choice(tuple(range(-WC_SZ, -WC_SZ/2)) + tuple(range(WC_SZ/2, WC_SZ))))
			
			# Heading is a random angle in radians
			heading = random.random() * 2 * pi
			
			# Converts the heading to a vector and multiplies it by speed to
			# get a velocity vector
			v = LVector3(cos(heading), sin(heading), 0) * AST_SPEEDS[0]
			self.setTag("velocity", self.asteroids[i], v)
			self.currID += 1
			self.setTag("ID", asteroid, self.currID)

	# This is our main task function, which does all of the per-frame
	# processing.  It takes in self like all functions in a class, and task,
	# the task object returned by taskMgr.
	def gameLoop(self, task):
		global globalClock
		
		# If the ship is not alive, do nothing.  Tasks return Task.cont to
		# signify that the task should continue running. If Task.done were
		# returned instead, the task would be removed and would no longer be
		# called every frame.
		if not self.alive:
			return Task.cont
	
		# 0. gather information about asteroids
		rocks = []
		for r in self.asteroids:
			v = self.getTag("velocity", r)
			idNum = self.getTag("ID", r)
			heading = degrees(atan2(v.getY(), v.getX()))
			obj = MovingObject(idNum, Point2(r.getX(), r.getY()), 
							   heading, v.length(), r.getScale()[0]/2)
			rocks.append(obj)
		
		# 1. Get ship's command
		startTime = globalClock.getLongTime()
		cmd = self.shipAI.getAICommand(rocks, normalizeDegrees(self.ship.getH()+90), self.framesToFire)
		#cmd = self.shipAI.opportunisticAI(rocks, normalizeDegrees(self.ship.getH()+90), self.framesToFire)
		#cmd = self.shipAI.trackingAI(rocks, normalizeDegrees(self.ship.getH()+90), self.framesToFire)
		#cmd = self.shipAI.aggressiveAI(rocks, normalizeDegrees(self.ship.getH()+90), self.framesToFire)
		
		if cmd == None:
			if not self.shieldUsed:
				self.ship.setColor(0,1,0)
				self.shieldUsed = True
				self.shieldFrames = SHIELD_LIFE
				self.shieldActive = True
			cmd = (False, 0)

		endTime = globalClock.getLongTime()
		if endTime - startTime > AI_TIME:
			print("Exceeded time limit")
		
		#2 Perform ship's command
		self.updateShip(cmd[0], cmd[1]);
			
		#3 Update asteroids-
		for obj in self.asteroids:
			self.updatePos(obj)
		
		#4 Update bullets
		newBulletArray = []
		for obj in self.bullets:
			self.updatePos(obj)  # Update the bullet
			maxCoord = FIELD_SZ / 2
			if obj.getX() == -maxCoord or obj.getX() == maxCoord or \
				obj.getY() == -maxCoord or obj.getY() == maxCoord: 
				obj.removeNode()  # Otherwise, remove it from the scene.
			else:
				newBulletArray.append(obj)
				
		self.bullets = newBulletArray

		#5 Check bullet collision with asteroids
		# In short, it checks every bullet against every asteroid. This is
		# quite slow.  A big optimization would be to sort the objects left to
		# right and check only if they overlap.  Framerate can go way down if
		# there are many bullets on screen, but for the most part it's okay.
		activeBullets = []
		for bullet in self.bullets:
			# This range statement makes it step though the asteroid list
			# backwards.  This is because if an asteroid is removed, the
			# elements after it will change position in the list.  If you go
			# backwards, the length stays constant.
			hit = False
			for i in range(len(self.asteroids)-1, -1, -1):
				asteroid = self.asteroids[i]
				# Panda's collision detection is more complicated than we need
				# here.  This is the basic sphere collision check. If the
				# distance between the object centers is less than sum of the
				# radii of the two objects, then we have a collision. We use
				# lengthSquared() since it is faster than length().
				if touching(bullet, asteroid):
					self.asteroidHit(i)      # Handle the hit
					hit = True
			if hit:
				bullet.removeNode()
			else:
				activeBullets.append(bullet)
		self.bullets = activeBullets

		#6 Update scoreboard
		gameScore =  self.hits[0] * PTS[0] + \
					self.hits[1] * PTS[1] + \
					self.hits[2] * PTS[2] - \
					self.hits[3] * PTS[3]
		scoreText = "#%d (%d) %d@%d %d@%d %d@%d %d@%d= %d" % (self.currGame, self.currFrame, self.hits[0], PTS[0], 
																self.hits[1], PTS[1],
																self.hits[2], PTS[2],
																self.hits[3], PTS[3],
																gameScore
																)
		self.scoreBrd.setText(scoreText)
		
		#7 Check if game is over: 
		#  A. maximum number of frames processed
		#  B. Check is ship collided with asteroid
		if self.currFrame == NUM_FRAMES:
			self.endGame(gameScore)
			return Task.cont

		if self.shieldActive:
			self.shieldFrames -= 1
			print(self.shieldFrames)
			if self.shieldFrames == 0:
				self.ship.setColor(1,1,1)
				self.shieldActive = False
		else:	
			for ast in self.asteroids:
				# Same sphere collision check for the ship vs. the asteroid
				if touching(ast, self.ship):
					print(self.ship.getPos())
					print(ast.getPos())
					print((ast.getPos()-self.ship.getPos()).length())
					self.endGame(gameScore)
					return Task.cont
		
		self.currFrame += 1
		
		return Task.cont    # Since every return is Task.cont, the task will

	def endGame(self, gameScore):
		self.alive = False 
		for i in self.asteroids + self.bullets:
			i.removeNode()
		self.bullets = []          # Clear the bullet list
		self.asteroids = []
		print("Game #%d: %d   %s" % (self.currGame, gameScore, self.scoreBrd.getText()))
		self.totalScore += gameScore
		if self.currGame == NUM_GAMES:
			print("Total " + str(self.totalScore))
			sys.exit()
		Sequence(Func(self.ship.hide),
				Wait(2),
				Func(self.ship.show),
			 	Func(self.newGame)).start()
		return Task.cont
		
	def newGame(self):
		self.hits = [0,0,0,0]
		self.currFrame = 0
		self.shieldUsed = False
		self.shieldActive = False
		self.ship.setColor(1,1,1)
		self.ship.setH(0)		# panda 0 degrees is 90 for us
		self.framesToFire = 0
		self.currID = 0
		random.seed(SEEDS[self.currGame])
		self.currGame += 1
		self.alive = True
		for i in self.asteroids + self.bullets:
			i.removeNode()
		self.bullets = []
		self.asteroids = []	
		self.spawnAsteroids()
		self.shipAI.newGame() 

	# Updates the positions of objects
	def updatePos(self, obj):
		vel = self.getTag("velocity", obj)
		newPos = obj.getPos() + vel * DT
		
		WC_SZ = FIELD_SZ / 2
		# Check if the object is out of bounds. If so, wrap it
		radius = .5 * obj.getScale().getX()
		if newPos.getX() - radius > WC_SZ:
			newPos.setX(-WC_SZ)
		elif newPos.getX() + radius < -WC_SZ:
			newPos.setX(WC_SZ)
		if newPos.getY() - radius > WC_SZ:
			newPos.setY(-WC_SZ)
		elif newPos.getY() + radius < -WC_SZ:
			newPos.setY(WC_SZ)
		
		obj.setPos(newPos)

	# The handler when an asteroid is hit by a bullet
	def asteroidHit(self, index):
		currDiam = self.asteroids[index].getScale().getX()
		# If the asteroid is small it is simply removed
		if currDiam == AST_DIAMS[2]:
			self.asteroids[index].removeNode()
			del self.asteroids[index]
			self.hits[2] += 1
		else:
			which = find(AST_DIAMS, currDiam)
			self.hits[which] += 1
			# If it is big enough, divide it up into little asteroids.
			# First we update the current asteroid.
			asteroid = self.asteroids[index]
			newScale = AST_DIAMS[which+1]
			asteroid.setScale(newScale)
			
			# The new direction is chosen as perpendicular to the old direction
			# This is determined using the cross product, which returns a
			# vector perpendicular to the two input vectors.  By crossing
			# velocity with a vector that goes into the screen, we get a vector
			# that is orthogonal to the original velocity in the screen plane.
			newSpeed = AST_SPEEDS[which+1]
			vel = self.getTag("velocity", asteroid)
			vel.normalize()
			vel = LVector3(0, 0, 1).cross(vel)
			vel *= newSpeed
			self.setTag("velocity", asteroid, vel)
			self.currID += 1
			self.setTag("ID", asteroid, self.currID)
			
			# Now we create a new asteroid identical to the current one
			newAst = loadObject(scale=newScale)
			self.setTag("velocity", newAst, -vel)
			newAst.setPos(asteroid.getPos())
			newAst.setTexture(asteroid.getTexture(), 1)
			self.asteroids.append(newAst)
			self.currID += 1
			self.setTag("ID", newAst, self.currID)

	# This updates the ship's position. This is similar to the general update
	# but takes into account turn and thrust
	def updateShip(self, fire, turnDir):
		if fire and self.framesToFire <= 0 and not self.shieldActive:
			self.fire()
			self.framesToFire = BULLET_REPEAT
			self.hits[3] += 1
		else:
			heading = self.ship.getH()
			heading += turnDir * TURN_RATE
			self.ship.setH(heading % 360)
			self.framesToFire -= 1

	# Creates a bullet and adds it to the bullet list
	def fire(self):
		print(self.shieldActive, self.shieldFrames)
		direction = radians(self.ship.getH() + 90)
		pos = self.ship.getPos()
		bullet = loadObject("bullet.png", scale=BULLET_RAD*2)  # Create the object
		bullet.setPos(pos)
		vel = LVector3(cos(direction), sin(direction), 0) * BULLET_SPEED
		self.setTag("velocity", bullet, vel)
		self.bullets.append(bullet)

	def setTag(self, tag, obj, val):
		obj.setPythonTag(tag, val)
	
	def getTag(self, tag, obj):
		return obj.getPythonTag(tag)
	


demo = AsteroidsDemo()
demo.run()
