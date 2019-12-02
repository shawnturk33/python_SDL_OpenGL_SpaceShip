from ctypes import *
from sdl2 import *
from sdl2.keycode import *
from sdl2.sdlmixer import *
from gl import *
from glconstants import *
import globs
from Program import *
from Buffer import *
import random
import traceback
import os.path
from Bullet import *
from math3d import *
from Ship import *
from Background import *
from Texture import *
from Text import *
from Constants import *

class Camera:

    def __init__(self, eye, coi, up, vangle, hither, yon):
        self.vangle = vangle
        self.hither = hither
        self.yon = yon
        self.lookAt(eye, coi, up)

    def lookAt(self, eye, coi, up):
        self.eye = eye.xyz
        self.coi = coi.xyz
        self.look = normalize(self.coi.xyz - self.eye.xyz)
        self.right = normalize(cross(self.look, up))
        self.up = cross(self.right, self.look)
        self.updateViewMatrix()
        self.updateProjMatrix()

    def updateViewMatrix(self):
        self.viewMatrix = mat4(
            self.right.x, self.up.x, -self.look.x, 0,
            self.right.y, self.up.y, -self.look.y, 0,
            self.right.z, self.up.z, -self.look.z, 0,
            -dot(self.eye, self.right), -dot(self.eye,self.up), dot(self.eye, self.look), 1)

    def updateProjMatrix(self):
        self.hangle = (globs.screenSize.x/globs.screenSize.y)*self.vangle
        self.projMatrix = mat4(
            1/tan(self.hangle), 0, 0, 0,
            0, 1/tan(self.vangle), 0, 0,
            0, 0, 1+(2*self.yon)/(self.hither - self.yon), -1,
            0, 0, 2*self.hither*self.yon/(self.hither - self.yon), 0
        )

    def setUniforms(self):
        Program.setUniform("viewMatrix", self.viewMatrix)
        Program.setUniform("projMatrix", self.projMatrix)
        Program.setUniform("eyePos", self.eye)

    def strafe(self, dx, dy, dz):
        self.coi.x += dx
        self.coi.y += dy
        self.coi.z += dz
        self.eye.x += dx
        self.eye.y += dy
        self.eye.z += dz
        self.updateViewMatrix()

    def tilt(self, amt):
        M = rotation2(amt)
        self.right = self.right * M
        self.up = self.up * M
        self.updateViewMatrix()