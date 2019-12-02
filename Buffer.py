from gl import *
from glconstants import *
import array

class Buffer:
    def __init__(self, data, usage=GL_STATIC_DRAW, size=None ):
        tmp = array.array("I", [0] )
        glGenBuffers(1,tmp)
        self.buffID = tmp[0]
        glBindBuffer( GL_ARRAY_BUFFER, self.buffID )
        if data == None:
            glBufferData(GL_ARRAY_BUFFER, size, None, usage)
        else:
            if type(data)==bytes:
                tmp=data
            else:
                tmp = data.tobytes()
            glBufferData( GL_ARRAY_BUFFER, len(tmp), tmp, GL_STATIC_DRAW)
        glBindBuffer( GL_ARRAY_BUFFER, 0 )

    def bind(self, bindingPoint):
        glBindBuffer(bindingPoint, self.buffID)

    def bindBase(self,bindingPoint,index):
        glBindBufferBase(bindingPoint,index,self.buffID)
        
