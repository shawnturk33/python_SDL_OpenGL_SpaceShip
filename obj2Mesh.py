import os.path
import array
from Material import *
import sys

def convert(fname):
    fpos=[]
    ftex=[]
    fnormals=[]
    ffaces={}
    materials={}
    with open(fname) as fp:
        for line in fp:
            line = line.strip()
            if len(line)==0:continue
            if line[0]=="#":continue
            lst = line.split()
            if lst[0]=="v":
                fpos.append([float(q) for q in lst[1:]])
            elif lst[0]=="vt":
                ftex.append([float(q) for q in lst[1:]])
            elif lst[0]=="vn":
                fnormals.append([float(q) for q in lst[1:]])
            elif lst[0]=="f":
                if len(lst)!=4:
                    raise RuntimeError("non triangles")
                for tmp in lst[1:]:
                    tmp=tmp.split("/")
                    if len(tmp)!=3 or tmp[1]=="":
                        raise RuntimeError("Not good")
                    if currmtl not in ffaces:
                        ffaces[currmtl] = []
                    vi,ti,ni = [int(q) -1 for q in tmp]
                    ffaces[currmtl].append((vi,ti,ni))
            elif lst[0]=="usemtl":
                currmtl=lst[1]
            elif lst[0]=="mtllib":
                parseMtl(lst[1],materials,os.path.dirname(fname))
    with open(fname + ".mesh","wb") as fp:
        fp.write(b"mesh 1\n")
        vdata = []
        tdata = []
        idata = []
        ndata = []
        vmap = {}
        numv = 0
        for mtl in ffaces:
            materials[mtl].start = len(idata)
            for key in ffaces[mtl]:
                vi,ti,ni = key
                if key not in vmap:
                    vmap[key] = numv
                    numv += 1
                    vdata += fpos[vi]
                    tdata += ftex[ti]
                    ndata += fnormals[ni]
                idata.append(vmap[key])
                materials[mtl].count+=1
        fp.write(b"materials %d\n" %len(ffaces))
        for m in ffaces:
            fp.write(b"material %s\n" %m.encode())
            fp.write(b"Kd %s\n" %materials[m].Kd.encode())
            fp.write(b"shininess %s\n" %materials[m].shininess.encode())
            fp.write(b"specular %s\n" %materials[m].specular.encode())
            if materials[m].map_Kd:
                fp.write(b"map_Kd %s\n" %materials[m].map_Kd.encode())
            fp.write(b"range %d %d\n" %(materials[m].start, materials[m].count))
        writeBlob(vdata, "positions",fp,"f")
        writeBlob(tdata, "texcoords", fp, "f")
        writeBlob(idata, "indices", fp, "I")
        writeBlob(ndata, "normals", fp, "f")
        fp.write(b"end\n")

def writeBlob(L, name, fp, fmt):
    A = array.array(fmt, L)
    B = A.tobytes()
    fp.write(b"%s %d\n"%(name.encode(), len(B)))
    fp.write(B)
    fp.write(b"\n")#debugging


def parseMtl(fname,mtls,pfx):
    with open(os.path.join(pfx,fname)) as fp:
        for line in fp:
            line = line.strip()
            lst = line.split(" ", 1)
            if lst[0]=="newmtl":
                curr = lst[1]
                mtls[curr] = Material()
            elif lst[0]=="Kd":
                mtls[curr].Kd = lst[1]
            elif lst[0]=="Ns":
                mtls[curr].shininess = lst[1]
            elif lst[0]=="Ks":
                mtls[curr].specular = lst[1]
            elif lst[0]=="map_Kd":
                mtls[curr].map_Kd=lst[1]

import tkinter.filedialog
infiles = tkinter.filedialog.askopenfilenames( initialdir=".", filetypes=( ("OBJ files","*.obj"), ("All files","*.*")))
for x in infiles:
    convert(x)
sys.exit(0)


