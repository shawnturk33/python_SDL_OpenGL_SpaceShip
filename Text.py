from Program import *
from sdl2 import *
from Buffer import *
from Texture import *
from sdl2.sdlttf import *
from gl import *
from glconstants import *
import globs
from Texture import *
from ctypes import *
import os.path
from math3d import *


class Text:
    prog = None
    def __init__(self, fontname, size):
        if Text.prog == None:
            Text.prog = Program("textvs.txt","textfs.txt");
            TTF_Init()
        self.font = TTF_OpenFont(os.path.join("assets", fontname).encode(), size)
        vbuff = Buffer(array.array("f",[0,0, 1,0, 1,1, 0,1]))
        ibuff = Buffer(array.array("I",[0,1,2, 0,2,3]))
        tmp = array.array("I",[0])
        glGenVertexArrays(1,tmp)
        self.vao = tmp[0]
        glBindVertexArray(self.vao)
        ibuff.bind(GL_ELEMENT_ARRAY_BUFFER)
        vbuff.bind(GL_ARRAY_BUFFER)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0,2,GL_FLOAT, False, 2*4, 0)
        glBindVertexArray(0)
        self.tex = DataTexture2DArray(1,1,1,array.array("B",[0,0,0,0]))
        self.textQuadSize=vec2(0,0)
        self.pos=vec2(0,0)
        self.dirty= False

    def setText(self, pos, st):
        self.pos = pos
        self.txt = st
        self.dirty = True
        surf1p = TTF_RenderUTF8_Blended(self.font, self.txt.encode(), SDL_Color(255,255,255,255))
        surf2p = SDL_ConvertSurfaceFormat(surf1p, SDL_PIXELFORMAT_ABGR8888, 0)
        w=surf2p.contents.w
        h=surf2p.contents.h
        pitch=surf2p.contents.pitch
        if pitch != w*4:
            print("Uh Oh! pitch!=w*4", pitch, w)
        pix = surf2p.contents.pixels
        B = string_at(pix, pitch*h)
        self.tex.setData(w,h,1,B)
        SDL_FreeSurface(surf2p)
        SDL_FreeSurface(surf1p)
        self.textQuadSize=vec2(w,h)
        self.dirty = False

    def draw(self):
        if self.dirty:
            self.renderTexture()
        oldprog = Program.current
        Text.prog.use()
        glBindVertexArray(self.vao)
        Program.setUniform("textQuadSizeInPixels", self.textQuadSize)
        Program.setUniform("textPosInPixels", self.pos)
        Program.updateUniforms()
        self.tex.bind(0)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, 0)
        glBindVertexArray(0)
        if oldprog:
            oldprog.use()