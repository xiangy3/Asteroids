from panda3d.core import Vec2, Point2
from MovingObject import MovingObject, normalizeDegrees
from math import*
from heapq import*

origin = Vec2(0, 0)

# this function can be used to display all the asteroid's values to the screen
def dumpAsteroids(rocks):
    print("Asteroids:")
    for rock in rocks:
        print(rock)
    print("------------------")
        
class myShipAI:
    
    # Called to create a new player
    def __init__(self, fieldSz, dt, turnRate, bulletSpeed, bulletRepeat, bulletRad, astSpeeds, astDiams,
                    totalFrames, points, shipRad):
        self.fieldSz = fieldSz
        self.dt = dt
        self.turnRate = turnRate
        self.bulletSpeed = bulletSpeed
        self.bulletRepeat = bulletRepeat
        self.bulletRad = bulletRad
        self.astSpeeds = astSpeeds
        self.destoried = []
        self.ship_rad = shipRad
        
        self.astRads = []
        for diam  in astDiams:
            self.astRads.append(diam/2)
            
        self.totalFrames = totalFrames
        self.points = points
    
    # Called when a new game of asteroids is started.
    def newGame(self):
        self.pts = 0
        self.destoried = []
        
    def tryDestory(self, asteroid, heading, framesToFire):
        bullet = MovingObject(1, origin, heading, self.bulletSpeed, self.bulletRad);
        
        t = asteroid.collideWithObject(bullet)
        
        if t != None:
                nx = asteroid.pos.x * t
                ny = asteroid.pos.y * t
                if nx > -350 and nx < 350 and ny > -350 and ny < 350 :
                    
                    
                    self.destoried.append(asteroid.id)
                    return (True, 0)
                    
        else:
            directionToAsteroid = normalizeDegrees(degrees(atan2(asteroid.pos.getY(), 
                                                                     asteroid.pos.getX())))
            if directionToAsteroid > heading:
                if directionToAsteroid - heading > 180:
                    return (False, -self.turnRate)
                else:
                    return(False, +self.turnRate)
            else:
                if heading - directionToAsteroid > 180:
                    return (False, +self.turnRate)
                else:
                    return (False, -self.turnRate)
    
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
        if len(asteroids) == 0: return (False, 0)
        
        threats = [];
        mostThreats = [];
        
        tship = MovingObject(1, origin, heading, 0, self.ship_rad);
        for a in asteroids:
            if a.distance(tship) <= a.rad + tship.rad:
                return None
            if a.collideWithObject(tship):
                heappush(mostThreats, (a.distance(tship) / a.speed, a))
            else:
                heappush(threats, (a.distance(tship) / a.speed * a.rad, a))
         
        while mostThreats: 
            next_asteroid = heappop(mostThreats)
            
            if next_asteroid[1].id not in self.destoried:
                move = self.tryDestory(next_asteroid[1], heading, framesToFire)
                if move != None: 
                    return move
        
        while threats: 
            next_asteroid = heappop(threats)
            if next_asteroid[1].id not in self.destoried:
                move = self.tryDestory(next_asteroid[1], heading, framesToFire)
                if move != None:
                    return move
        return (False, self.turnRate)

                
            
            
        
        
        
        
        
        
        
        
        