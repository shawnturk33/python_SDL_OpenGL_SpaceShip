from gl import *
from glconstants import *
import io
import zipfile
import png
import traceback

class Texture:
    def __init__(self, typ):
        self.type = typ
        self.tex = None
    def bind(self,unit):
        glActiveTexture(GL_TEXTURE0 + unit)
        glBindTexture(self.type, self.tex)
    def unbind(self,unit):
        glActiveTexture(GL_TEXTURE0 + unit)
        glBindTexture(self.type,0)
class Texture2DArray(Texture):
    def __init__(self,w,h,slices):
        Texture.__init__(self,GL_TEXTURE_2D_ARRAY)
        self.w=w
        self.h=h
        self.slices=slices
class DataTexture2DArray(Texture2DArray):
    def __init__(self,w,h,slices,pix):
        Texture2DArray.__init__(self,w,h,slices)
        tmp=array.array("I",[0])
        glGenTextures(1,tmp)
        self.tex=tmp[0]
        self.bind(0)
        glTexImage3D(GL_TEXTURE_2D_ARRAY,0,GL_RGBA,w,h,slices,0,GL_RGBA,GL_UNSIGNED_BYTE,pix)
        glGenerateMipmap(GL_TEXTURE_2D_ARRAY)
        self.unbind(0)
    def setData(self, w, h, slices, pix):
        self.bind(0)
        if w == self.w and h == self.h and slices == self.slices:
            glTexSubImage3D(GL_TEXTURE_2D_ARRAY, 0, 0, 0, 0, w, h, slices, GL_RGBA, GL_UNSIGNED_BYTE, pix)
        else:
            glTexImage3D(GL_TEXTURE_2D_ARRAY, 0, GL_RGBA, w, h, slices, 0, GL_RGBA, GL_UNSIGNED_BYTE, pix)
            self.w=w; self.h=h; self.slices=slices
        glGenerateMipmap(GL_TEXTURE_2D_ARRAY)
        self.unbind(0)
class ImageTexture2DArray(DataTexture2DArray):
    def __init__(self,*files):
        #for x in traceback.format_stack():
           #print(x,end="")
        #print("Loading Image")
        membuf = io.BytesIO()
        w=None
        h=None
        slices=0
        for fname in files:
            if fname.endswith(".png" or fname.endswith(".jpg")):
                tmp = open(fname,"rb").read()
                pw,ph,fmt,pix = png.decode(tmp)
                pix = png.flipY(pw, ph, pix)
                if w==None:
                    w=pw
                    h=ph
                else:
                    if w != pw or h != ph:
                        raise RuntimeError("Size mismatch")
                slices += 1
                membuf.write(pix)
            elif fname.endswith(".zip") or fname.endswith(".ora"):
                z = zipfile.ZipFile(fname)
                for n in sorted(z.namelist()):
                    if n.endswith(".png") or n.endswith(".jpg"):
                        ze = z.open(n)
                        tmp = ze.read()
                        pw,ph,fmt,pix = png.decode(tmp)
                        if w==None:
                            w=pw
                            h=ph
                        else:
                            if w != pw or h != ph:
                                raise RuntimeError("Size mismatch")
                        slices+=1
                        membuf.write(pix)
            else:
                raise RuntimeError("Cannot read file " +fname)
        DataTexture2DArray.__init__(self,w,h,slices,membuf.getbuffer())
class Sampler:
    def __init__(self):
        tmp = array.array("I",[0])
        glGenSamplers(1,tmp)
        self.samp = tmp[0]
        glSamplerParameteri(self.samp,GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glSamplerParameteri(self.samp, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glSamplerParameteri(self.samp, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glSamplerParameteri(self.samp, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glSamplerParameteri(self.samp, GL_TEXTURE_MAX_ANISOTROPY_EXT, 1)
    def bind(self, unit):
        glBindSampler(unit, self.samp)