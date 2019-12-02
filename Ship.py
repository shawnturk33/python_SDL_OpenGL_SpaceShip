from sdl2 import *
from sdl2.keycode import *
from gl import *
from glconstants import *
import globs
from ctypes import *
from math3d import *
from Texture import *
from Buffer import *
import random
from Program import *
from math import *
from Constants import *
from Mesh import *

class Ship:

    global radius
    radius = 0.1
    mesh = None

    def __init__(self):
        self.state = ALIVE
        self.deathwatch = 500
        self.radius = radius
        self.alphaFactor = 1
        self.M = 0
        self.rotation = 0
        self.spin = 0
        self.bank = 0
        self.scaling = 1
        self.diffuse = vec3(1,1,1)
        if Ship.mesh is None:
            Ship.mesh = Mesh(os.path.join("assets", "ship1b.obj.mesh"))
        self.pos = vec3(0, 0, 0)
        self.up = vec3(0, 1, 0)
        self.right = vec3(0, 0, 1)
        self.facing = cross(self.up, self.right)
        self.rotationMatrix = mat4(
            self.facing.x, self.facing.y, self.facing.z, 0,
            self.up.x, self.up.y, self.up.z, 0,
            self.right.x, self.right.y, self.right.z, 0,
            0, 0, 0, 1)

    def update(self, elapsed):
        self.bank = 0
        if SDLK_w in globs.keyset:
            self.tilt(0.007)
            self.bank = 3.14/8
        if SDLK_s in globs.keyset:
            self.tilt(-0.007)
            self.bank = -3.14/8
        if SDLK_a in globs.keyset:
            self.turn(0.007)
        if SDLK_d in globs.keyset:
            self.turn(-0.007)
        self.pos += self.facing * vec3(0.005, 0.005, 0.005)

    def tilt(self, amount):
        M = axisRotation(self.right, amount)
        self.facing = (vec4(*self.facing, 0) * M).xyz
        self.up = (vec4(*self.up, 0) * M).xyz
        self.updateRotationMatrix()

    def turn(self, amount):
        M = axisRotation(self.up, amount)
        self.facing = (vec4(*self.facing, 0) * M).xyz
        self.right = (vec4(*self.right, 0) * M).xyz
        self.updateRotationMatrix()

    def updateRotationMatrix(self):
        self.rotationMatrix = mat4(
            self.facing.x, self.facing.y, self.facing.z, 0,
            self.up.x, self.up.y, self.up.z, 0,
            self.right.x, self.right.y, self.right.z, 0,
            0, 0, 0, 1)


    def draw(self):
        Program.setUniform("alphaFactor",self.alphaFactor)
        Program.setUniform("diffuse", self.diffuse)
        self.M = self.rotationMatrix * rotation3(self.right, self.bank) * translation(self.pos)
        Program.setUniform("worldMatrix", self.M)
        Program.updateUniforms()
        self.mesh.draw()


class EnemyShip(Ship):
    mesh = None

    def __init__(self):
        Ship.__init__(self)
        self.pos = vec3(globs.camera.coi.x + 1, random.uniform(-1,1), 0)
        self.nextSpawnTime = random.randint(500,2000)
        if EnemyShip.mesh is None:
            EnemyShip.mesh = Mesh(os.path.join("assets", "ship2b.obj.mesh"))


    def update(self, elapsed):
        self.pos.x += -0.0005 * elapsed
        self.nextSpawnTime -= elapsed
        if self.state == DYING:
            self.rotation += 0.1
            self.pos.y -= 0.007
            self.scaling -= 0.01
            self.alphaFactor -= 1-(self.deathwatch - elapsed)/self.deathwatch
            self.deathwatch -= elapsed
            if self.deathwatch <= 0:
                self.state = DEAD
                self.alphaFactor = 0


    def draw(self):
        Program.setUniform("alphaFactor", self.alphaFactor)
        Program.setUniform("diffuse", self.diffuse)
        self.M = scaling3(vec3(self.scaling, self.scaling, self.scaling)) * rotation3((1,0,0), self.rotation) * translation3(self.pos)
        Program.setUniform("worldMatrix", self.M)
        Program.updateUniforms()
        EnemyShip.mesh.draw()


class EnemySin(EnemyShip):
    mesh = None

    def __init__(self):
        EnemyShip.__init__(self)
        if EnemySin.mesh is None:
            EnemySin.mesh = Mesh(os.path.join("assets", "jellyfish.obj.mesh"))

    def update(self, elapsed):
        EnemyShip.update(self, elapsed)
        self.pos.y += sin(3*self.pos.x*pi)*0.003
        self.spin += 0.01

    def draw(self):
        Program.setUniform("alphaFactor", self.alphaFactor)
        Program.setUniform("diffuse", self.diffuse)
        self.M = scaling3(vec3(self.scaling,self.scaling,self.scaling)) * rotation3(vec3(0, 1, 1), self.rotation) * rotation3(vec3(0,1,0), self.spin) * translation3(self.pos)
        Program.setUniform("worldMatrix", self.M)
        Program.updateUniforms()
        EnemySin.mesh.draw()


