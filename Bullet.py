from math3d import *
import math
from Buffer import *
from Program import *
from Texture import *
import array
import globs
import os.path
from Constants import *
from Mesh import *


class Bullet:
    mesh = None

    def __init__(self, spawn):
        self.pos=spawn
        self.life=750000
        self.state = ALIVE
        self.M = 0
        if Bullet.mesh is None:
            Bullet.mesh = Mesh(os.path.join("assets", "bullet.obj.mesh"))


    def update(self,elapsed):
        self.life -= elapsed
        self.pos.x += 0.0005*elapsed
        
    def draw(self):
        self.M = translation3(self.pos)
        Program.setUniform("worldMatrix", self.M)
        Program.updateUniforms()
        Bullet.mesh.draw()

    def collidesWith(self, en):
        if self.state != ALIVE:
            return False
        if en.state != ALIVE:
            return False
        v = self.pos - en.pos
        rs = en.radius + 0.1
        rs *= rs
        return (dot(v,v)<=rs)



