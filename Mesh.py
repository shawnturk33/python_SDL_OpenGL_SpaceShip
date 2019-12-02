from Buffer import *
import array
from Material import *
from Program import *
from math3d import *
from Texture import *

class Mesh:
    def __init__(self, fname):
        self.M =0
        self.pos = (0,0,0)
        self.materials = []
        with open(fname, "rb") as fp:
            line = fp.readline()
            if line != b"mesh 1\n":
                raise RuntimeError("bad mesh: " + fname)
            line = fp.readline().decode()
            lst = line.split()
            assert lst[0]=="materials"
            nm = int(lst[1])
            for i in range(nm):
                self.readMtl(fp)
            vdata = self.getBlob(fp, "positions")
            tdata = self.getBlob(fp, "texcoords")
            idata = self.getBlob(fp, "indices")
            ndata = self.getBlob(fp, "normals")
            line = fp.readline()
            assert line==b"end\n"
            self.setup(vdata,tdata,idata,ndata)

    def getBlob(self, fp, tag):
        line = fp.readline().decode()
        lst = line.split()
        assert lst[0] == tag
        numbytes = int(lst[1])
        B = fp.read(numbytes)
        buf = Buffer(B)
        fp.readline()  # discard empty line
        return buf

    def readMtl(self, fp):
        fp.readline()#mtlname
        line = fp.readline().decode()
        lst = line.split()
        assert lst[0] == "Kd"
        Kd = [float(q) for q in lst[1:4]]
        line = fp.readline().decode().strip()
        lst = line.split()
        assert lst[0] == "shininess"
        shininess = lst[1]
        line = fp.readline().decode().strip()
        lst = line.split()
        assert lst[0] == "specular"
        specular = [float(q) for q in lst[1:4]]
        line = fp.readline().decode().strip()
        if line.startswith("map_Kd"):
            lst=line.split(" ", 1)
            tex = ImageTexture2DArray(os.path.join("assets", lst[1].strip()))
            line=fp.readline().decode()
        else:
            tex = ImageTexture2DArray(os.path.join("assets", "white.png"))
        #range
        assert line.startswith("range")
        lst = line.split()
        start = int(lst[1])*4
        count = int(lst[2])
        m = Material()
        m.diffuse = vec3(*Kd)
        m.tex=tex
        m.start=start
        m.count=count
        m.shininess = float(shininess)
        m.specular = vec3(*specular)
        self.materials.append(m)
        return

    def setup(self, vdata, tdata, idata, ndata):
        tmp = array.array("I", [0])
        glGenVertexArrays(1, tmp)
        self.vao = tmp[0]
        glBindVertexArray(self.vao)
        idata.bind(GL_ELEMENT_ARRAY_BUFFER)
        vdata.bind(GL_ARRAY_BUFFER)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, 3*4, 0)
        tdata.bind(GL_ARRAY_BUFFER)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1,2,GL_FLOAT,False, 2*4, 0)
        ndata.bind(GL_ARRAY_BUFFER)
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, False, 3*4, 0)
        glBindVertexArray(0)

    def draw(self):
        glBindVertexArray(self.vao)
        for M in self.materials:
            M.tex.bind(0)
            Program.setUniform("diffuse", M.diffuse)
            Program.setUniform("shininess", M.shininess)
            Program.setUniform("specular", M.specular)
            Program.updateUniforms()
            glDrawElements(GL_TRIANGLES, M.count, GL_UNSIGNED_INT, M.start)

    def drawWithPos(self):
        glBindVertexArray(self.vao)
        for M in self.materials:
            M.tex.bind(0)
            Program.setUniform("diffuse", M.diffuse)
            Program.setUniform("shininess", M.shininess)
            Program.setUniform("specular", M.specular)
            self.M = translation3(self.pos)
            Program.setUniform("worldMatrix", self.M)
            Program.updateUniforms()
            glDrawElements(GL_TRIANGLES, M.count, GL_UNSIGNED_INT, M.start)
