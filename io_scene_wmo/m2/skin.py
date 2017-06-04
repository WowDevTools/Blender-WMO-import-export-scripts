#!/usr/bin/python
import struct
import array
import io
from .wowfile import *
from . import wowfile

class SkinHeader:
    def __init__(self):
        self.magic          = 1313426259
        self.Indices        = Chunk()
        self.Triangles      = Chunk()
        self.Properties     = Chunk()
        self.Submeshes      = Chunk()
        self.TextureUnits   = Chunk()
        self.lod        = 0
    def unpack(self,f):
        self.magic,         = struct.unpack("i",f.read(4))
        self.Indices.unpack(f)
        self.Triangles.unpack(f)
        self.Properties.unpack(f)
        self.Submeshes.unpack(f)
        self.TextureUnits.unpack(f)
        self.lod,       = struct.unpack("i",f.read(4))
        return self
    def pack(self):
        ret = struct.pack("i",self.magic)
        ret +=  self.Indices.pack()
        ret +=  self.Triangles.pack()
        ret +=  self.Properties.pack()
        ret +=  self.Submeshes.pack()
        ret +=  self.TextureUnits.pack()
        ret += struct.pack("i", self.lod)
        return ret

class Mesh:
    def __init__(self):
        self.mesh_id        = 0
        self.vert_offset    = 0
        self.num_verts      = 0
        self.tri_offset     = 0
        self.num_tris       = 0
        self.num_bones      = 0
        self.start_bone     = 0
        self.unknown        = 0
        self.rootbone       = 0
        self.bound      = Bounds()

    def unpack(self,f):
        self.mesh_id,       = struct.unpack("i",f.read(4))
        self.vert_offset,   = struct.unpack("H",f.read(2))
        self.num_verts,     = struct.unpack("H",f.read(2))
        self.tri_offset,    = struct.unpack("H",f.read(2))
        self.num_tris,      = struct.unpack("H",f.read(2))
        self.num_bones,     = struct.unpack("H",f.read(2))
        self.start_bone,    = struct.unpack("H",f.read(2))
        self.unknown,       = struct.unpack("H",f.read(2))
        self.rootbone,      = struct.unpack("H",f.read(2))
        self.bound.unpack(f)
        return self
    def pack(self):
        ret = struct.pack("i",self.mesh_id)
        ret += struct.pack("H",self.vert_offset)
        ret += struct.pack("H", self.num_verts)
        ret += struct.pack("H", self.tri_offset)
        ret += struct.pack("H", self.num_tris)
        ret += struct.pack("H", self.num_bones)
        ret += struct.pack("H", self.start_bone)
        ret += struct.pack("H", self.unknown)
        ret += struct.pack("H", self.rootbone)
        ret += self.bound.pack()
        return ret


class Material:
    def __init__(self):
        self.flags         = 0
        self.shading        = 0
        self.submesh       = 0
        self.submesh2      = 0
        self.color         = -1
        self.renderflag    = 0
        self.texunit        = 0
        self.mode          = 0
        self.texture       = 0
        self.texunit2      = 0
        self.transparency  = 0
        self.animation      = 0
    def unpack(self,f):
        self.flags,         = struct.unpack("H",f.read(2))
        self.shading,       = struct.unpack("H",f.read(2))
        self.submesh,       = struct.unpack("H",f.read(2))
        self.submesh2,      = struct.unpack("H",f.read(2))
        self.color,         = struct.unpack("h",f.read(2))
        self.renderflag,    = struct.unpack("H",f.read(2))
        self.texunit,       = struct.unpack("H",f.read(2))
        self.mode,          = struct.unpack("H",f.read(2))
        self.texture,       = struct.unpack("H",f.read(2))
        self.texunit2,      = struct.unpack("H",f.read(2))
        self.transparency,  = struct.unpack("H",f.read(2))
        self.animation,      = struct.unpack("H",f.read(2))
        return self
    def pack(self):
        ret = struct.pack("H",self.flags)
        ret += struct.pack("H",self.shading)
        ret += struct.pack("H",self.submesh)
        ret += struct.pack("H",self.submesh2)
        ret += struct.pack("h",self.color)
        ret += struct.pack("H",self.renderflag)
        ret += struct.pack("H",self.texunit)
        ret += struct.pack("H",self.mode)
        ret += struct.pack("H",self.texture)
        ret += struct.pack("H",self.texunit2)
        ret += struct.pack("H",self.transparency)
        ret += struct.pack("H",self.animation)
        return ret

class Propertie:
    def __init__(self):
        self.Bones = (0,0,0,0)
    def unpack(self,f):
        self.Bones = struct.unpack("4B",f.read(4))
        return self
    def pack(self):
        return struct.pack("4B",self.Bones[0],self.Bones[1],self.Bones[2],self.Bones[3])

class SkinFile:
    def __init__(self, file):
        f = open(file,"r+b") if type(file) == type("") else io.BytesIO(file[0])

        self.header = SkinHeader()
        self.header.unpack(f)
        self.indices    = ReadBlock(f,self.header.Indices,Lookup)
        self.header.Triangles.count //= 3;
        self.tri    = ReadBlock(f,self.header.Triangles,Triangle)
        self.prop   = ReadBlock(f,self.header.Properties,Propertie)
        self.mesh   = ReadBlock(f,self.header.Submeshes,Mesh)
        self.texunit    = ReadBlock(f,self.header.TextureUnits,Material)


        f.close()

    def write(self,filename):
        f = open(filename,"wb")

        f.write(self.header.pack())

        WriteBlock(f,self.header.Indices,self.indices)
        WriteBlock(f,self.header.Triangles,self.tri)
        self.header.Triangles.count *= 3;
        WriteBlock(f,self.header.Properties,self.prop)
        WriteBlock(f,self.header.Submeshes,self.mesh)
        WriteBlock(f,self.header.TextureUnits,self.texunit)

        f.seek(0,SEEK_SET)
        f.write(self.header.pack())

        f.close()


