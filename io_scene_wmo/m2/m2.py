#!/usr/bin/python
import struct
import array
import os
import io

# customs
from .wowfile import *
from . import wowfile

# Tilting Values
TILT_X = 1
TILT_Y = 2
TILT_XY = 3

# AnimBlock Data Types
DATA_QUAT = 0
DATA_VEC3 = 1
DATA_INT = 2
DATA_SHORT = 3
DATA_VEC2 = 4
DATA_FLOAT = 5
DATA_VEC9 = 6

# Interpolation Types
INTER_NONE = 0
INTER_LINEAR = 1
INTER_HERMITE = 2


# Classes for the different structs
class M2Header:
    def __init__(self):
        self.magic = 808600653
        self.version = 264
        self.name = Chunk()
        self.modeltype = 0
        self.global_sequences = Chunk()
        self.animations = Chunk()
        self.anim_lookup = Chunk()
        self.bones = Chunk()
        self.key_bones = Chunk()
        self.vertices = Chunk()
        self.nviews = 1
        self.colors = Chunk()
        self.textures = Chunk()
        self.transparency = Chunk()
        self.uv_anim = Chunk()
        self.tex_replace = Chunk()
        self.renderflags = Chunk()
        self.bone_lookup = Chunk()
        self.tex_lookup = Chunk()
        self.tex_units = Chunk()
        self.trans_lookup = Chunk()
        self.uv_anim_lookup = Chunk()
        self.bound = Bounds()
        self.vbox = Bounds()
        self.bounding_triangles = Chunk()
        self.bounding_vertices = Chunk()
        self.bounding_normals = Chunk()
        self.attachments = Chunk()
        self.attach_lookup = Chunk()
        self.events = Chunk()
        self.lights = Chunk()
        self.cameras = Chunk()
        self.camera_lookup = Chunk()
        self.ribbon_emitters = Chunk()
        self.particle_emitters = Chunk()
        self.unknown = Chunk()

    def unpack(self, f):
        self.magic, = struct.unpack("i", f.read(4))
        self.version, = struct.unpack("i", f.read(4))
        self.name.unpack(f)
        self.modeltype, = struct.unpack("i", f.read(4))
        self.global_sequences.unpack(f)
        self.animations.unpack(f)
        self.anim_lookup.unpack(f)
        self.bones.unpack(f)
        self.key_bones.unpack(f)
        self.vertices.unpack(f)
        self.nviews, = struct.unpack("i", f.read(4))
        ##HACK!!!###
        self.nviews = 1
        self.colors.unpack(f)
        self.textures.unpack(f)
        self.transparency.unpack(f)
        self.uv_anim.unpack(f)
        self.tex_replace.unpack(f)
        self.renderflags.unpack(f)
        self.bone_lookup.unpack(f)
        self.tex_lookup.unpack(f)
        self.tex_units.unpack(f)
        self.trans_lookup.unpack(f)
        self.uv_anim_lookup.unpack(f)
        self.bound.unpack(f)
        self.vbox.unpack(f)
        self.bounding_triangles.unpack(f)
        self.bounding_vertices.unpack(f)
        self.bounding_normals.unpack(f)
        self.attachments.unpack(f)
        self.attach_lookup.unpack(f)
        self.events.unpack(f)
        self.lights.unpack(f)
        self.cameras.unpack(f)
        self.camera_lookup.unpack(f)
        self.ribbon_emitters.unpack(f)
        self.particle_emitters.unpack(f)
        if (self.modeltype & 8):
            self.unknown.unpack(f)

    def pack(self):
        ret = struct.pack("i", self.magic)
        ret += struct.pack("i", self.version)
        ret += self.name.pack()
        ret += struct.pack("i", self.modeltype)
        ret += self.global_sequences.pack()
        ret += self.animations.pack()
        ret += self.anim_lookup.pack()
        ret += self.bones.pack()
        ret += self.key_bones.pack()
        ret += self.vertices.pack()
        ret += struct.pack("i", self.nviews)
        ret += self.colors.pack()
        ret += self.textures.pack()
        ret += self.transparency.pack()
        ret += self.uv_anim.pack()
        ret += self.tex_replace.pack()
        ret += self.renderflags.pack()
        ret += self.bone_lookup.pack()
        ret += self.tex_lookup.pack()
        ret += self.tex_units.pack()
        ret += self.trans_lookup.pack()
        ret += self.uv_anim_lookup.pack()
        ret += self.bound.pack()
        ret += self.vbox.pack()
        ret += self.bounding_triangles.pack()
        ret += self.bounding_vertices.pack()
        ret += self.bounding_normals.pack()
        ret += self.attachments.pack()
        ret += self.attach_lookup.pack()
        ret += self.events.pack()
        ret += self.lights.pack()
        ret += self.cameras.pack()
        ret += self.camera_lookup.pack()
        ret += self.ribbon_emitters.pack()
        ret += self.particle_emitters.pack()
        if (self.modeltype & 8):
            ret += self.unknown.pack()
        return ret


class Vertex:
    def __init__(self):
        self.pos = Vec3()
        self.bweights = (0, 0, 0, 0)
        self.bindices = (0, 0, 0, 0)
        self.normal = (0, 0, 0)
        self.uv = (0, 0)
        self.unk = (0, 0)

    def unpack(self, f):
        self.pos = Vec3().unpack(f)
        self.bweights = struct.unpack("4B", f.read(4))
        self.bindices = struct.unpack("4B", f.read(4))
        self.normal = struct.unpack("3f", f.read(12))
        self.uv = struct.unpack("2f", f.read(8))
        self.unk = struct.unpack("2f", f.read(8))
        return self

    def pack(self):
        ret = self.pos.pack()
        ret += struct.pack("4B", self.bweights[0], self.bweights[1], self.bweights[2], self.bweights[3])
        ret += struct.pack("4B", self.bindices[0], self.bindices[1], self.bindices[2], self.bindices[3])
        ret += struct.pack("3f", self.normal[0], self.normal[1], self.normal[2])
        ret += struct.pack("2f", self.uv[0], self.uv[1])
        ret += struct.pack("2f", self.unk[0], self.unk[1])
        return ret


class Sequ:
    def __init__(self):
        self.animId = 0
        self.subId = 0
        self.len = 0
        self.moveSpeed = 0
        self.flags = 0
        self.prob = 0
        self.pad = 0
        self.unk = (0, 0)
        self.playSpeed = 0
        self.bound = Bounds()
        self.next = 0
        self.index = 0

    def unpack(self, f):
        self.animId, = struct.unpack("H", f.read(2))
        self.subId, = struct.unpack("H", f.read(2))
        self.len, = struct.unpack("i", f.read(4))
        self.moveSpeed, = struct.unpack("f", f.read(4))
        self.flags, = struct.unpack("i", f.read(4))
        self.prob, = struct.unpack("h", f.read(2))
        self.pad, = struct.unpack("h", f.read(2))
        self.unk = struct.unpack("2i", f.read(8))
        self.playSpeed, = struct.unpack("i", f.read(4))
        self.bound.unpack(f)
        self.next, = struct.unpack("h", f.read(2))
        self.index, = struct.unpack("H", f.read(2))
        return self

    def pack(self):
        ret = struct.pack("H", self.animId)
        ret += struct.pack("H", self.subId)
        ret += struct.pack("i", self.len)
        ret += struct.pack("f", self.moveSpeed)
        ret += struct.pack("i", self.flags)
        ret += struct.pack("h", self.prob)
        ret += struct.pack("h", self.pad)
        ret += struct.pack("2i", self.unk[0], self.unk[1])
        ret += struct.pack("i", self.playSpeed)
        ret += self.bound.pack()
        ret += struct.pack("h", self.next)
        ret += struct.pack("H", self.index)
        return ret


class AnimSub:
    def __init__(self):
        self.type = 0
        self.nEntries = 0
        self.ofsEntries = 0
        self.values = []

    def unpack(self, f, type, animfile=None):
        self.type = type
        self.nEntries, = struct.unpack("i", f.read(4))
        self.ofsEntries, = struct.unpack("i", f.read(4))
        if (animfile is None):
            oldpos = f.tell()
            f.seek(self.ofsEntries)
            self.values = []
            for i in xrange(self.nEntries):
                if (type == DATA_QUAT):
                    temp = Quat().unpack(f)
                    self.values.append(temp)
                elif (type == DATA_VEC3):
                    temp = Vec3().unpack(f)
                    self.values.append(temp)
                elif (type == DATA_INT):
                    temp, = struct.unpack("i", f.read(4))
                    self.values.append(temp)
                elif (type == DATA_SHORT):
                    temp, = struct.unpack("h", f.read(2))
                    self.values.append(temp)
                elif (type == DATA_VEC2):
                    temp = Vec2().unpack(f)
                    self.values.append(temp)
                elif (type == DATA_VEC9):
                    temp = Vec9().unpack(f)
                    self.values.append(temp)
                elif (type == DATA_FLOAT):
                    temp, = struct.unpack("f", f.read(4))
                    self.values.append(temp)
                else:
                    pass
            f.seek(oldpos)
        else:
            file = open(animfile[1], "r+b")
            file.seek(self.ofsEntries)
            self.values = []
            for i in xrange(self.nEntries):
                if (type == DATA_QUAT):
                    temp = Quat().unpack(file)
                    self.values.append(temp)
                elif (type == DATA_VEC3):
                    temp = Vec3().unpack(file)
                    self.values.append(temp)
                elif (type == DATA_INT):
                    temp, = struct.unpack("i", file.read(4))
                    self.values.append(temp)
                elif (type == DATA_SHORT):
                    temp, = struct.unpack("h", file.read(2))
                    self.values.append(temp)
                elif (type == DATA_VEC2):
                    temp = Vec2().unpack(file)
                    self.values.append(temp)
                elif (type == DATA_VEC9):
                    temp = Vec9().unpack(file)
                    self.values.append(temp)
                elif (type == DATA_FLOAT):
                    temp, = struct.unpack("f", file.read(4))
                    self.values.append(temp)
                else:
                    pass
        return self

    def pack(self):
        ret = struct.pack("i", self.nEntries)
        ret += struct.pack("i", self.ofsEntries)
        return ret


class AnimBlock:
    def __init__(self):
        self.interpolation = 0
        self.gsequ = -1
        self.nTimes = 0
        self.ofsTimes = 0
        self.TimeSubs = []
        self.nKeys = 0
        self.ofsKeys = 0
        self.KeySubs = []
        self.type = DATA_INT

    def unpack(self, f, type, animfiles):
        self.interpolation, = struct.unpack("h", f.read(2))
        self.gsequ, = struct.unpack("h", f.read(2))
        self.nTimes, = struct.unpack("i", f.read(4))
        self.ofsTimes, = struct.unpack("i", f.read(4))
        self.type = type

        oldpos = f.tell()
        f.seek(self.ofsTimes)
        self.TimeSubs = []
        for i in xrange(self.nTimes):
            if (animfiles[i][0] == True):
                temp = AnimSub().unpack(f, DATA_INT, animfiles[i])
            else:
                temp = AnimSub().unpack(f, DATA_INT)
            self.TimeSubs.append(temp)
        f.seek(oldpos)

        self.nKeys, = struct.unpack("i", f.read(4))
        self.ofsKeys, = struct.unpack("i", f.read(4))

        oldpos = f.tell()
        f.seek(self.ofsKeys)
        self.KeySubs = []
        for i in xrange(self.nKeys):
            if (animfiles[i][0] == True):
                temp = AnimSub().unpack(f, type, animfiles[i])
            else:
                temp = AnimSub().unpack(f, type)
            self.KeySubs.append(temp)
        f.seek(oldpos)
        return self

    def pack(self):
        ret = struct.pack("h", self.interpolation)
        ret += struct.pack("h", self.gsequ)
        ret += struct.pack("i", self.nTimes)
        ret += struct.pack("i", self.ofsTimes)
        ret += struct.pack("i", self.nKeys)
        ret += struct.pack("i", self.ofsKeys)
        return ret


class Bone:
    def __init__(self):
        self.KeyBoneId = 0
        self.flags = 0
        self.parent = 0
        self.unk = (0, 0, 0)
        self.translation = AnimBlock()
        self.rotation = AnimBlock()
        self.scaling = AnimBlock()
        self.pivot = Vec3()

    def __str__(self):
        return (
            "(" + str(self.KeyBoneId) + "," + str(self.flags) + "," + str(self.parent) + "," + str(self.pivot) + ")")

    def unpack(self, f, animfiles):
        self.KeyBoneId, = struct.unpack("i", f.read(4))
        self.flags, = struct.unpack("i", f.read(4))
        self.parent, = struct.unpack("h", f.read(2))
        self.unk = struct.unpack("3h", f.read(6))
        self.translation = AnimBlock().unpack(f, DATA_VEC3, animfiles)
        self.rotation = AnimBlock().unpack(f, DATA_QUAT, animfiles)
        self.scaling = AnimBlock().unpack(f, DATA_VEC3, animfiles)
        self.pivot = Vec3().unpack(f)
        return self

    def pack(self):
        ret = struct.pack("i", self.KeyBoneId)
        ret += struct.pack("i", self.flags)
        ret += struct.pack("h", self.parent)
        ret += struct.pack("3h", self.unk[0], self.unk[1], self.unk[2])
        ret += self.translation.pack()
        ret += self.rotation.pack()
        ret += self.scaling.pack()
        ret += self.pivot.pack()
        return ret


class Attachment:
    def __init__(self):
        self.Id = 0
        self.bone = 0
        self.pos = Vec3()
        self.Enabled = AnimBlock()

    def unpack(self, f, animfiles):
        self.Id, = struct.unpack("i", f.read(4))
        self.bone, = struct.unpack("i", f.read(4))
        self.pos = Vec3().unpack(f)
        self.Enabled = AnimBlock().unpack(f, DATA_INT, animfiles)
        return self

    def pack(self):
        ret = struct.pack("i", self.Id)
        ret += struct.pack("i", self.bone)
        ret += self.pos.pack()
        ret += self.Enabled.pack()
        return ret


class Texture:
    def __init__(self):
        self.type = 0
        self.flags = 0
        self.len_name = 0
        self.ofs_name = 0
        self.name = ""

    def unpack(self, f):
        self.type, = struct.unpack("i", f.read(4))
        self.flags, = struct.unpack("i", f.read(4))
        self.len_name, = struct.unpack("i", f.read(4))
        self.ofs_name, = struct.unpack("i", f.read(4))
        oldpos = f.tell()
        f.seek(self.ofs_name)
        self.name = f.read(self.len_name)
        f.seek(oldpos)
        return self

    def pack(self):
        ret = struct.pack("i", self.type)
        ret += struct.pack("i", self.flags)
        ret += struct.pack("i", self.len_name)
        ret += struct.pack("i", self.ofs_name)
        return ret


class Renderflags:
    def __init__(self):
        self.flags = 0
        self.blend = 0

    def unpack(self, f):
        self.flags, = struct.unpack("h", f.read(2))
        self.blend, = struct.unpack("h", f.read(2))
        return self

    def pack(self):
        ret = struct.pack("h", self.flags)
        ret += struct.pack("h", self.blend)
        return ret


class UVAnimation:
    def __init__(self):
        self.translation = AnimBlock()
        self.rotation = AnimBlock()
        self.scaling = AnimBlock()

    def unpack(self, f, animfiles):
        self.translation = AnimBlock().unpack(f, DATA_VEC3, animfiles)
        self.rotation = AnimBlock().unpack(f, DATA_QUAT, animfiles)
        self.scaling = AnimBlock().unpack(f, DATA_VEC3, animfiles)
        return self

    def pack(self):
        ret = self.translation.pack()
        ret += self.rotation.pack()
        ret += self.scaling.pack()
        return ret


class Color:
    def __init__(self):
        self.color = AnimBlock()
        self.alpha = AnimBlock()

    def unpack(self, f, animfiles):
        self.color = AnimBlock().unpack(f, DATA_VEC3, animfiles)
        self.alpha = AnimBlock().unpack(f, DATA_SHORT, animfiles)
        return self

    def pack(self):
        ret = self.color.pack()
        ret += self.alpha.pack()
        return ret


class Transparency:
    def __init__(self):
        self.alpha = AnimBlock()

    def unpack(self, f, animfiles):
        self.alpha = AnimBlock().unpack(f, DATA_SHORT, animfiles)
        return self

    def pack(self):
        return self.alpha.pack()


class Event:
    def __init__(self):
        self.Id = 0
        self.Data = 0
        self.Bone = 0
        self.Pos = Vec3()
        self.interpolation = 0
        self.gsequ = 0
        self.nTimes = 0
        self.ofsTimes = 0

        self.TimeSubs = []

    def unpack(self, f):
        self.Id, = struct.unpack("i", f.read(4))
        self.Data, = struct.unpack("i", f.read(4))
        self.Bone, = struct.unpack("i", f.read(4))
        self.Pos = Vec3().unpack(f)
        self.interpolation, = struct.unpack("h", f.read(2))
        self.gsequ, = struct.unpack("h", f.read(2))
        self.nTimes, = struct.unpack("i", f.read(4))
        self.ofsTimes, = struct.unpack("i", f.read(4))

        oldpos = f.tell()
        f.seek(self.ofsTimes)
        self.TimeSubs = []
        for i in xrange(self.nTimes):
            temp = AnimSub().unpack(f, DATA_INT)
            self.TimeSubs.append(temp)
        f.seek(oldpos)
        return self

    def pack(self):
        ret = struct.pack("i", self.Id)
        ret += struct.pack("i", self.Data)
        ret += struct.pack("i", self.Bone)
        ret += self.Pos.pack()
        ret += struct.pack("h", self.interpolation)
        ret += struct.pack("h", self.gsequ)
        ret += struct.pack("i", self.nTimes)
        ret += struct.pack("i", self.ofsTimes)
        return ret


class Light:
    def __init__(self):
        self.Type = 0
        self.Bone = 0
        self.Pos = Vec3()
        self.AmbientCol = AnimBlock()
        self.AmbientInt = AnimBlock()
        self.DiffuseCol = AnimBlock()
        self.DiffuseInt = AnimBlock()
        self.AttStart = AnimBlock()
        self.AttEnd = AnimBlock()
        self.Enabled = AnimBlock()

    def unpack(self, f, animfiles):
        self.Type, = struct.unpack("h", f.read(2))
        self.Bone, = struct.unpack("h", f.read(2))
        self.Pos = Vec3().unpack(f)
        self.AmbientCol = AnimBlock().unpack(f, DATA_VEC3, animfiles)
        self.AmbientInt = AnimBlock().unpack(f, DATA_FLOAT, animfiles)
        self.DiffuseCol = AnimBlock().unpack(f, DATA_VEC3, animfiles)
        self.DiffuseInt = AnimBlock().unpack(f, DATA_FLOAT, animfiles)
        self.AttStart = AnimBlock().unpack(f, DATA_FLOAT, animfiles)
        self.AttEnd = AnimBlock().unpack(f, DATA_FLOAT, animfiles)
        self.Enabled = AnimBlock().unpack(f, DATA_INT, animfiles)
        return self

    def pack(self):
        ret = struct.pack("h", self.Type)
        ret += struct.pack("h", self.Bone)
        ret += self.Pos.pack()
        ret += self.AmbientCol.pack()
        ret += self.AmbientInt.pack()
        ret += self.DiffuseCol.pack()
        ret += self.DiffuseInt.pack()
        ret += self.AttStart.pack()
        ret += self.AttEnd.pack()
        ret += self.Enabled.pack()
        return ret


class FakeAnim:
    def __init__(self):
        self.nTimes = 0
        self.ofsTimes = 0
        self.type = 0
        self.Times = []
        self.nKeys = 0
        self.ofsKeys = 0
        self.Keys = []

    def unpack(self, f, type):
        self.nTimes, = struct.unpack("i", f.read(4))
        self.ofsTimes, = struct.unpack("i", f.read(4))
        self.type = type

        oldpos = f.tell()
        f.seek(self.ofsTimes)
        self.Times = []
        for i in xrange(self.nTimes):
            temp, = struct.unpack("h", f.read(2))
            self.Times.append(temp)
        f.seek(oldpos)

        self.nKeys, = struct.unpack("i", f.read(4))
        self.ofsKeys, = struct.unpack("i", f.read(4))

        oldpos = f.tell()
        f.seek(self.ofsKeys)
        self.Keys = []
        for i in xrange(self.nKeys):
            if (type == DATA_SHORT):
                temp, = struct.unpack("h", f.read(2))
                self.Keys.append(temp)
            elif (type == DATA_VEC3):
                temp = Vec3().unpack(f)
                self.Keys.append(temp)
            elif (type == DATA_VEC2):
                temp = Vec2().unpack(f)
                self.Keys.append(temp)
            else:
                pass
        f.seek(oldpos)
        return self

    def pack(self):
        ret = struct.pack("i", self.nTimes)
        ret += struct.pack("i", self.ofsTimes)
        ret += struct.pack("i", self.nKeys)
        ret += struct.pack("i", self.ofsKeys)
        return ret


class Particle:
    def __init__(self):
        self.Id = 0
        self.flags1 = 0
        self.flags2 = 0
        self.Pos = Vec3()
        self.bone = 0
        self.texture = 0

        self.lenModel = 0
        self.ofsModel = 0
        self.ModelName = ""

        self.lenParticle = 0
        self.ofsParticle = 0
        self.ParticleName = ""

        self.blend = 0
        self.emitter = 0
        self.color_dbc = 0
        self.particletype = 0
        self.head_or_tail = 0
        self.tex_tile_rot = 0
        self.tex_rows = 0
        self.tex_cols = 0
        self.emission_speed = AnimBlock()
        self.speed_var = AnimBlock()
        self.vert_range = AnimBlock()
        self.hor_range = AnimBlock()
        self.gravity = AnimBlock()
        self.lifespan = AnimBlock()
        self.pad1 = 0
        self.emission_rate = AnimBlock()
        self.pad2 = 0
        self.emission_area_len = AnimBlock()
        self.emission_area_width = AnimBlock()
        self.gravity2 = AnimBlock()
        self.color = FakeAnim()
        self.opacity = FakeAnim()
        self.size = FakeAnim()
        self.pad3 = (0, 0)
        self.intensity = FakeAnim()
        self.unkfake = FakeAnim()
        self.unk1 = Vec3()
        self.scale = Vec3()
        self.slowdown = 0
        self.unk2 = (0, 0, 0, 0, 0)
        self.rot1 = Vec3()
        self.rot2 = Vec3()
        self.translation = Vec3()
        self.unk3 = (0, 0, 0, 0)

        self.nUnk = 0
        self.ofsUnk = 0
        self.UnkRef = []

        self.Enabled = AnimBlock()

    def unpack(self, f, animfiles):
        self.Id, = struct.unpack("i", f.read(4))
        self.flags1, = struct.unpack("h", f.read(2))
        self.flags2, = struct.unpack("h", f.read(2))
        self.Pos = Vec3().unpack(f)
        self.bone, = struct.unpack("h", f.read(2))
        self.texture, = struct.unpack("h", f.read(2))

        self.lenModel, = struct.unpack("i", f.read(4))
        self.ofsModel, = struct.unpack("i", f.read(4))
        oldpos = f.tell()
        f.seek(self.ofsModel)
        self.ModelName = f.read(self.lenModel)
        f.seek(oldpos)

        self.lenParticle, = struct.unpack("i", f.read(4))
        self.ofsParticle, = struct.unpack("i", f.read(4))
        oldpos = f.tell()
        f.seek(self.ofsParticle)
        self.ParticleName = f.read(self.lenParticle)
        f.seek(oldpos)

        self.blend, = struct.unpack("b", f.read(1))
        self.emitter, = struct.unpack("b", f.read(1))
        self.color_dbc, = struct.unpack("h", f.read(2))
        self.particletype, = struct.unpack("b", f.read(1))
        self.head_or_tail, = struct.unpack("b", f.read(1))
        self.tex_tile_rot, = struct.unpack("h", f.read(2))
        self.tex_rows, = struct.unpack("h", f.read(2))
        self.tex_cols, = struct.unpack("h", f.read(2))

        self.emission_speed = AnimBlock().unpack(f, DATA_FLOAT, animfiles)
        self.speed_var = AnimBlock().unpack(f, DATA_FLOAT, animfiles)
        self.vert_range = AnimBlock().unpack(f, DATA_FLOAT, animfiles)
        self.hor_range = AnimBlock().unpack(f, DATA_FLOAT, animfiles)
        self.gravity = AnimBlock().unpack(f, DATA_FLOAT, animfiles)
        self.lifespan = AnimBlock().unpack(f, DATA_FLOAT, animfiles)

        self.pad1, = struct.unpack("i", f.read(4))
        self.emission_rate = AnimBlock().unpack(f, DATA_FLOAT, animfiles)
        self.pad2, = struct.unpack("i", f.read(4))

        self.emission_area_len = AnimBlock().unpack(f, DATA_FLOAT, animfiles)
        self.emission_area_width = AnimBlock().unpack(f, DATA_FLOAT, animfiles)
        self.gravity2 = AnimBlock().unpack(f, DATA_FLOAT, animfiles)

        self.color = FakeAnim().unpack(f, DATA_VEC3)
        self.opacity = FakeAnim().unpack(f, DATA_SHORT)
        self.size = FakeAnim().unpack(f, DATA_VEC2)
        self.pad3 = struct.unpack("2i", f.read(8))
        self.intensity = FakeAnim().unpack(f, DATA_SHORT)
        self.unkfake = FakeAnim().unpack(f, DATA_SHORT)
        self.unk1 = Vec3().unpack(f)
        self.scale = Vec3().unpack(f)
        self.slowdown, = struct.unpack("f", f.read(4))
        self.unk2 = struct.unpack("5f", f.read(20))
        self.rot1 = Vec3().unpack(f)
        self.rot2 = Vec3().unpack(f)
        self.translation = Vec3().unpack(f)
        self.unk3 = struct.unpack("4f", f.read(16))

        self.nUnk, = struct.unpack("i", f.read(4))
        self.ofsUnk, = struct.unpack("i", f.read(4))
        oldpos = f.tell()
        self.UnkRef = []
        f.seek(self.ofsUnk)
        for i in xrange(self.nUnk):
            temp = Vec3().unpack(f)
            self.UnkRef.append(temp)
        f.seek(oldpos)

        self.Enabled = AnimBlock().unpack(f, DATA_INT, animfiles)
        return self

    def pack(self):
        ret = struct.pack("i", self.Id)
        ret += struct.pack("h", self.flags1)
        ret += struct.pack("h", self.flags2)
        ret += self.Pos.pack()
        ret += struct.pack("h", self.bone)
        ret += struct.pack("h", self.texture)

        ret += struct.pack("i", self.lenModel)
        ret += struct.pack("i", self.ofsModel)
        ret += struct.pack("i", self.lenParticle)
        ret += struct.pack("i", self.ofsParticle)

        ret += struct.pack("b", self.blend)
        ret += struct.pack("b", self.emitter)
        ret += struct.pack("h", self.color_dbc)
        ret += struct.pack("b", self.particletype)
        ret += struct.pack("b", self.head_or_tail)
        ret += struct.pack("h", self.tex_tile_rot)
        ret += struct.pack("h", self.tex_rows)
        ret += struct.pack("h", self.tex_cols)

        ret += self.emission_speed.pack()
        ret += self.speed_var.pack()
        ret += self.vert_range.pack()
        ret += self.hor_range.pack()
        ret += self.gravity.pack()
        ret += self.lifespan.pack()
        ret += struct.pack("i", self.pad1)
        ret += self.emission_rate.pack()
        ret += struct.pack("i", self.pad2)
        ret += self.emission_area_len.pack()
        ret += self.emission_area_width.pack()
        ret += self.gravity2.pack()
        ret += self.color.pack()
        ret += self.opacity.pack()
        ret += self.size.pack()
        ret += struct.pack("2i", self.pad3[0], self.pad3[1])
        ret += self.intensity.pack()
        ret += self.unkfake.pack()
        ret += self.unk1.pack()
        ret += self.scale.pack()
        ret += struct.pack("f", self.slowdown)
        ret += struct.pack("5f", self.unk2[0], self.unk2[1], self.unk2[2], self.unk2[3], self.unk2[4])
        ret += self.rot1.pack()
        ret += self.rot2.pack()
        ret += self.translation.pack()
        ret += struct.pack("4f", self.unk3[0], self.unk3[1], self.unk3[2], self.unk3[3])
        ret += struct.pack("i", self.nUnk)
        ret += struct.pack("i", self.ofsUnk)
        ret += self.Enabled.pack()
        return ret


class Ribbon:
    def __init__(self):
        self.Id = 0
        self.Bone = 0
        self.Pos = Vec3()
        self.nTexRefs = 0
        self.ofsTexRefs = 0
        self.TexRefs = []

        self.nBlendRef = 0
        self.ofsBlendRef = 0
        self.BlendRef = []

        self.Color = AnimBlock()
        self.Opacity = AnimBlock()
        self.Above = AnimBlock()
        self.Below = AnimBlock()

        self.Resolution = 0
        self.Length = 0
        self.Angle = 0
        self.Flags = 0
        self.Blend = 0

        self.Unk1 = AnimBlock()
        self.Unk2 = AnimBlock()

        self.pad = 0

    def unpack(self, f, animfiles):
        self.Id, = struct.unpack("i", f.read(4))
        self.Bone, = struct.unpack("i", f.read(4))
        self.Pos = Vec3().unpack(f)
        self.nTexRefs, = struct.unpack("i", f.read(4))
        self.ofsTexRefs, = struct.unpack("i", f.read(4))
        oldpos = f.tell()
        f.seek(self.ofsTexRefs)
        self.TexRefs = []
        for i in xrange(self.nTexRefs):
            temp, = struct.unpack("i", f.read(4))
            self.TexRefs.append(temp)
        f.seek(oldpos)

        self.nBlendRef, = struct.unpack("i", f.read(4))
        self.ofsBlendRef, = struct.unpack("i", f.read(4))
        oldpos = f.tell()
        f.seek(self.ofsBlendRef)
        self.BlendRef = []
        for i in xrange(self.nBlendRef):
            temp, = struct.unpack("i", f.read(4))
            self.BlendRef.append(temp)
        f.seek(oldpos)

        self.Color = AnimBlock().unpack(f, DATA_VEC3, animfiles)
        self.Opacity = AnimBlock().unpack(f, DATA_SHORT, animfiles)
        self.Above = AnimBlock().unpack(f, DATA_FLOAT, animfiles)
        self.Below = AnimBlock().unpack(f, DATA_FLOAT, animfiles)

        self.Resolution, = struct.unpack("f", f.read(4))
        self.Length, = struct.unpack("f", f.read(4))
        self.Angle, = struct.unpack("f", f.read(4))
        self.Flags, = struct.unpack("h", f.read(2))
        self.Blend, = struct.unpack("h", f.read(2))

        self.Unk1 = AnimBlock().unpack(f, DATA_SHORT, animfiles)
        self.Unk2 = AnimBlock().unpack(f, DATA_INT, animfiles)

        self.pad, = struct.unpack("i", f.read(4))
        return self

    def pack(self):
        ret = struct.pack("i", self.Id)
        ret += struct.pack("i", self.Bone)
        ret += self.Pos.pack()
        ret += struct.pack("i", self.nTexRefs)
        ret += struct.pack("i", self.ofsTexRefs)
        ret += struct.pack("i", self.nBlendRef)
        ret += struct.pack("i", self.ofsBlendRef)
        ret += self.Color.pack()
        ret += self.Opacity.pack()
        ret += self.Above.pack()
        ret += self.Below.pack()
        ret += struct.pack("f", self.Resolution)
        ret += struct.pack("f", self.Length)
        ret += struct.pack("f", self.Angle)
        ret += struct.pack("h", self.Flags)
        ret += struct.pack("h", self.Blend)
        ret += self.Unk1.pack()
        ret += self.Unk2.pack()
        ret += struct.pack("i", self.pad)
        return ret


class Camera:
    def __init__(self):
        self.Type = 0
        self.FOV = 0
        self.FarClip = 0
        self.NearClip = 0
        self.TransPos = AnimBlock()
        self.Pos = Vec3()
        self.TransTar = AnimBlock()
        self.Target = Vec3()
        self.Scaling = AnimBlock()

    def unpack(self, f, animfiles):
        self.Type, = struct.unpack("i", f.read(4))
        self.FOV, = struct.unpack("f", f.read(4))
        self.FarClip, = struct.unpack("f", f.read(4))
        self.NearClip, = struct.unpack("f", f.read(4))
        self.TransPos = AnimBlock().unpack(f, DATA_VEC9, animfiles)
        self.Pos = Vec3().unpack(f)
        self.TransTar = AnimBlock().unpack(f, DATA_VEC9, animfiles)
        self.Target = Vec3().unpack(f)
        self.Scaling = AnimBlock().unpack(f, DATA_VEC3, animfiles)
        return self

    def pack(self):
        ret = struct.pack("i", self.Type)
        ret += struct.pack("f", self.FOV)
        ret += struct.pack("f", self.FarClip)
        ret += struct.pack("f", self.NearClip)
        ret += self.TransPos.pack()
        ret += self.Pos.pack()
        ret += self.TransTar.pack()
        ret += self.Target.pack()
        ret += self.Scaling.pack()
        return ret


class GlobalSequence:
    def __init__(self):
        self.Timestamp = 0

    def unpack(self, f):
        self.Timestamp, = struct.unpack("i", f.read(4))
        return self

    def pack(self):
        return struct.pack("i", self.Timestamp)


def WriteAnimBlock(f, block, animfiles):
    if (block.nTimes != 0):
        block.ofsTimes = f.tell()
        for i in block.TimeSubs:
            f.write(i.pack())
        FillLine(f)

        for i in xrange(block.nTimes):
            if (animfiles[i][0] == False):
                block.TimeSubs[i].ofsEntries = f.tell()
                for j in block.TimeSubs[i].values:
                    if (block.TimeSubs[i].type == DATA_QUAT):
                        f.write(j.pack())
                    elif (block.TimeSubs[i].type == DATA_VEC3):
                        f.write(j.pack())
                    elif (block.TimeSubs[i].type == DATA_INT):
                        f.write(struct.pack("i", j))
                    elif (block.TimeSubs[i].type == DATA_SHORT):
                        f.write(struct.pack("h", j))
                    elif (block.TimeSubs[i].type == DATA_VEC2):
                        f.write(j.pack())
                    elif (block.TimeSubs[i].type == DATA_VEC9):
                        f.write(j.pack())
                    elif (block.TimeSubs[i].type == DATA_FLOAT):
                        f.write(struct.pack("f", j))
                    else:
                        pass
                FillLine(f)
            else:
                file = open(animfiles[i][1], "a+b")
                file.seek(0, SEEK_END)
                block.TimeSubs[i].ofsEntries = file.tell()
                for j in block.TimeSubs[i].values:
                    if (block.TimeSubs[i].type == DATA_QUAT):
                        file.write(j.pack())
                    elif (block.TimeSubs[i].type == DATA_VEC3):
                        file.write(j.pack())
                    elif (block.TimeSubs[i].type == DATA_INT):
                        file.write(struct.pack("i", j))
                    elif (block.TimeSubs[i].type == DATA_SHORT):
                        file.write(struct.pack("h", j))
                    elif (block.TimeSubs[i].type == DATA_VEC2):
                        file.write(j.pack())
                    elif (block.TimeSubs[i].type == DATA_VEC9):
                        file.write(j.pack())
                    elif (block.TimeSubs[i].type == DATA_FLOAT):
                        file.write(struct.pack("f", j))
                    else:
                        pass
                FillLine(file)

        block.ofsKeys = f.tell()
        for i in block.KeySubs:
            f.write(i.pack())
        FillLine(f)
        for i in xrange(block.nKeys):
            if (animfiles[i][0] == False):
                block.KeySubs[i].ofsEntries = f.tell()
                for j in block.KeySubs[i].values:
                    if (block.KeySubs[i].type == DATA_QUAT):
                        f.write(j.pack())
                    elif (block.KeySubs[i].type == DATA_VEC3):
                        f.write(j.pack())
                    elif (block.KeySubs[i].type == DATA_INT):
                        f.write(struct.pack("i", j))
                    elif (block.KeySubs[i].type == DATA_SHORT):
                        f.write(struct.pack("h", j))
                    elif (block.KeySubs[i].type == DATA_VEC2):
                        f.write(j.pack())
                    elif (block.KeySubs[i].type == DATA_VEC9):
                        f.write(j.pack())
                    elif (block.KeySubs[i].type == DATA_FLOAT):
                        f.write(struct.pack("f", j))
                    else:
                        pass
                FillLine(f)
            else:
                file = open(animfiles[i][1], "a+b")
                file.seek(0, SEEK_END)
                block.KeySubs[i].ofsEntries = file.tell()
                for j in block.KeySubs[i].values:
                    if (block.KeySubs[i].type == DATA_QUAT):
                        file.write(j.pack())
                    elif (block.KeySubs[i].type == DATA_VEC3):
                        file.write(j.pack())
                    elif (block.KeySubs[i].type == DATA_INT):
                        file.write(struct.pack("i", j))
                    elif (block.KeySubs[i].type == DATA_SHORT):
                        file.write(struct.pack("h", j))
                    elif (block.KeySubs[i].type == DATA_VEC2):
                        file.write(j.pack())
                    elif (block.KeySubs[i].type == DATA_VEC9):
                        file.write(j.pack())
                    elif (block.KeySubs[i].type == DATA_FLOAT):
                        file.write(struct.pack("f", j))
                    else:
                        pass
                FillLine(file)

        oldpos = f.tell()

        f.seek(block.ofsTimes)
        for i in block.TimeSubs:
            f.write(i.pack())

        f.seek(block.ofsKeys)
        for i in block.KeySubs:
            f.write(i.pack())

        f.seek(oldpos)
    else:
        block.ofsTimes = 0
        block.ofsKeys = 0


def WriteFakeBlock(f, block):
    block.ofsTimes = f.tell()
    for j in block.Times:
        f.write(struct.pack("h", j))
    FillLine(f)

    block.ofsKeys = f.tell()
    for j in block.Keys:
        if (block.type == DATA_SHORT):
            f.write(struct.pack("h", j))
        elif (block.type == DATA_VEC3):
            f.write(j.pack())
        elif (block.type == DATA_VEC2):
            f.write(j.pack())
        else:
            pass
    FillLine(f)


def InAnimFile(a_name, anim):
    first = str(anim.animId)
    while len(first) < 4:
        first = "0" + first
    scnd = str(anim.subId)
    while len(scnd) < 2:
        scnd = "0" + scnd
    fname = a_name + first + "-" + scnd + ".anim"
    return os.path.isfile(fname), fname


def CreateAnimFileName(a_name, anim, animfile):
    first = str(anim.animId)
    while len(first) < 4:
        first = "0" + first
    scnd = str(anim.subId)
    while len(scnd) < 2:
        scnd = "0" + scnd
    fname = a_name + first + "-" + scnd + ".anim"
    return animfile[0], fname


class M2File:
    def __init__(self, file):

        f = open(file, "r+b") if type(file) == type("") else io.BytesIO(file[0])
        filename = file[1]

        self.hdr = M2Header()
        self.hdr.unpack(f)
        hdr = self.hdr  # just spare some time in tipping

        f.seek(hdr.name.offset)  # Go to the name
        self.name = f.read(hdr.name.count)  # Read the name
        # Read Blocks
        self.gSequ = ReadBlock(f, hdr.global_sequences, GlobalSequence)
        self.animations = ReadBlock(f, hdr.animations, Sequ)
        self.anim_files = []
        tempname = filename[0:len(filename) - 3]
        for i in self.animations:
            self.anim_files.append(InAnimFile(tempname, i))
        self.anim_lookup = ReadBlock(f, hdr.anim_lookup, Lookup)
        self.bones = ReadBlock(f, hdr.bones, Bone, self.anim_files)
        self.key_bones = ReadBlock(f, hdr.key_bones, Lookup)
        self.vertices = ReadBlock(f, hdr.vertices, Vertex)
        self.colors = ReadBlock(f, hdr.colors, Color, self.anim_files)
        self.textures = ReadBlock(f, hdr.textures, Texture)
        self.transparency = ReadBlock(f, hdr.transparency, Transparency, self.anim_files)
        self.uv_anim = ReadBlock(f, hdr.uv_anim, UVAnimation, self.anim_files)
        self.tex_replace = ReadBlock(f, hdr.tex_replace, Lookup)
        self.renderflags = ReadBlock(f, hdr.renderflags, Renderflags)
        self.bone_lookup = ReadBlock(f, hdr.bone_lookup, Lookup)
        self.tex_lookup = ReadBlock(f, hdr.tex_lookup, Lookup)
        self.tex_units = ReadBlock(f, hdr.tex_units, Lookup)
        self.trans_lookup = ReadBlock(f, hdr.trans_lookup, Lookup)
        self.uv_anim_lookup = ReadBlock(f, hdr.uv_anim_lookup, Lookup)
        self.bounding_triangles = ReadBlock(f, hdr.bounding_triangles, Triangle)
        self.bounding_vertices = ReadBlock(f, hdr.bounding_vertices, Vec3)
        self.bounding_normals = ReadBlock(f, hdr.bounding_normals, Vec3)
        self.attachments = ReadBlock(f, hdr.attachments, Attachment, self.anim_files)
        self.attach_lookup = ReadBlock(f, hdr.attach_lookup, Lookup)
        self.events = ReadBlock(f, hdr.events, Event)
        self.lights = ReadBlock(f, hdr.lights, Light, self.anim_files)
        self.cameras = ReadBlock(f, hdr.cameras, Camera, self.anim_files)
        self.camera_lookup = ReadBlock(f, hdr.camera_lookup, Lookup)
        self.ribbon_emitters = ReadBlock(f, hdr.ribbon_emitters, Ribbon, self.anim_files)
        #self.particle_emitters = ReadBlock(f, hdr.particle_emitters, Particle, self.anim_files)

        f.close()

    def write(self, filename):
        f = open(filename, "w+b")

        tempname = filename[0:len(filename) - 3]
        counter = 0
        for i in self.animations:
            self.anim_files[counter] = CreateAnimFileName(tempname, i, self.anim_files[counter])
            counter += 1

        f.seek(0)
        f.write(self.hdr.pack())
        FillLine(f)

        self.hdr.name.offset = f.tell()
        f.write(self.name)
        FillLine(f)

        WriteBlock(f, self.hdr.global_sequences, self.gSequ)
        WriteBlock(f, self.hdr.animations, self.animations)
        WriteBlock(f, self.hdr.anim_lookup, self.anim_lookup)

        WriteBlock(f, self.hdr.bones, self.bones)
        for i in self.bones:
            WriteAnimBlock(f, i.translation, self.anim_files)
            WriteAnimBlock(f, i.rotation, self.anim_files)
            WriteAnimBlock(f, i.scaling, self.anim_files)
        oldpos = f.tell()
        f.seek(self.hdr.bones.offset)
        WriteBlock(f, self.hdr.bones, self.bones)
        f.seek(oldpos)

        WriteBlock(f, self.hdr.key_bones, self.key_bones)
        WriteBlock(f, self.hdr.vertices, self.vertices)

        WriteBlock(f, self.hdr.colors, self.colors)
        for i in self.colors:
            WriteAnimBlock(f, i.color, self.anim_files)
            WriteAnimBlock(f, i.alpha, self.anim_files)
        oldpos = f.tell()
        f.seek(self.hdr.colors.offset)
        WriteBlock(f, self.hdr.colors, self.colors)
        f.seek(oldpos)

        WriteBlock(f, self.hdr.textures, self.textures)
        for i in self.textures:
            i.ofs_name = f.tell()
            i.len_name = len(i.name)
            f.write(i.name)
            FillLine(f)
        oldpos = f.tell()
        f.seek(self.hdr.textures.offset)
        WriteBlock(f, self.hdr.textures, self.textures)
        f.seek(oldpos)

        WriteBlock(f, self.hdr.transparency, self.transparency)
        for i in self.transparency:
            WriteAnimBlock(f, i.alpha, self.anim_files)
        oldpos = f.tell()
        f.seek(self.hdr.transparency.offset)
        WriteBlock(f, self.hdr.transparency, self.transparency)
        f.seek(oldpos)

        WriteBlock(f, self.hdr.uv_anim, self.uv_anim)
        for i in self.uv_anim:
            WriteAnimBlock(f, i.translation, self.anim_files)
            WriteAnimBlock(f, i.rotation, self.anim_files)
            WriteAnimBlock(f, i.scaling, self.anim_files)
        oldpos = f.tell()
        f.seek(self.hdr.uv_anim.offset)
        WriteBlock(f, self.hdr.uv_anim, self.uv_anim)
        f.seek(oldpos)

        WriteBlock(f, self.hdr.tex_replace, self.tex_replace)
        WriteBlock(f, self.hdr.renderflags, self.renderflags)
        WriteBlock(f, self.hdr.bone_lookup, self.bone_lookup)
        WriteBlock(f, self.hdr.tex_lookup, self.tex_lookup)
        WriteBlock(f, self.hdr.tex_units, self.tex_units)
        WriteBlock(f, self.hdr.trans_lookup, self.trans_lookup)
        WriteBlock(f, self.hdr.uv_anim_lookup, self.uv_anim_lookup)
        WriteBlock(f, self.hdr.bounding_triangles, self.bounding_triangles)
        WriteBlock(f, self.hdr.bounding_vertices, self.bounding_vertices)
        WriteBlock(f, self.hdr.bounding_normals, self.bounding_normals)

        WriteBlock(f, self.hdr.attachments, self.attachments)
        for i in self.attachments:
            WriteAnimBlock(f, i.Enabled, self.anim_files)
        oldpos = f.tell()
        f.seek(self.hdr.attachments.offset)
        WriteBlock(f, self.hdr.attachments, self.attachments)
        f.seek(oldpos)

        WriteBlock(f, self.hdr.attach_lookup, self.attach_lookup)

        WriteBlock(f, self.hdr.events, self.events)
        for i in self.events:
            i.ofsTimes = f.tell()
            for n in i.TimeSubs:
                f.write(n.pack())
                FillLine(f)
            for n in xrange(i.nTimes):
                i.TimeSubs[n].ofsEntries = f.tell()
                for j in i.TimeSubs[n].values:
                    f.write(struct.pack("i", j))
            oldpos = f.tell()
            f.seek(i.ofsTimes)
            for n in i.TimeSubs:
                f.write(n.pack())
            f.seek(oldpos)
        FillLine(f)
        oldpos = f.tell()
        f.seek(self.hdr.events.offset)
        WriteBlock(f, self.hdr.events, self.events)
        f.seek(oldpos)

        WriteBlock(f, self.hdr.lights, self.lights)
        for i in self.lights:
            WriteAnimBlock(f, i.AmbientCol, self.anim_files)
            WriteAnimBlock(f, i.AmbientInt, self.anim_files)
            WriteAnimBlock(f, i.DiffuseCol, self.anim_files)
            WriteAnimBlock(f, i.DiffuseInt, self.anim_files)
            WriteAnimBlock(f, i.AttStart, self.anim_files)
            WriteAnimBlock(f, i.AttEnd, self.anim_files)
            WriteAnimBlock(f, i.Enabled, self.anim_files)
        oldpos = f.tell()
        f.seek(self.hdr.lights.offset)
        WriteBlock(f, self.hdr.lights, self.lights)
        f.seek(oldpos)

        WriteBlock(f, self.hdr.cameras, self.cameras)
        for i in self.cameras:
            WriteAnimBlock(f, i.TransPos, self.anim_files)
            WriteAnimBlock(f, i.TransTar, self.anim_files)
            WriteAnimBlock(f, i.Scaling, self.anim_files)
        oldpos = f.tell()
        f.seek(self.hdr.cameras.offset)
        WriteBlock(f, self.hdr.cameras, self.cameras)
        f.seek(oldpos)

        WriteBlock(f, self.hdr.camera_lookup, self.camera_lookup)

        WriteBlock(f, self.hdr.ribbon_emitters, self.ribbon_emitters)
        for i in self.ribbon_emitters:
            i.ofsTexRefs = f.tell()
            for j in i.TexRefs:
                f.write(struct.pack("i", j))
            FillLine(f)
            i.ofsBlendRef = f.tell()
            for j in i.BlendRef:
                f.write(struct.pack("i", j))
            FillLine(f)
            WriteAnimBlock(f, i.Color, self.anim_files)
            WriteAnimBlock(f, i.Opacity, self.anim_files)
            WriteAnimBlock(f, i.Above, self.anim_files)
            WriteAnimBlock(f, i.Below, self.anim_files)
            WriteAnimBlock(f, i.Unk1, self.anim_files)
            WriteAnimBlock(f, i.Unk2, self.anim_files)
        oldpos = f.tell()
        f.seek(self.hdr.ribbon_emitters.offset)
        WriteBlock(f, self.hdr.ribbon_emitters, self.ribbon_emitters)
        f.seek(oldpos)

        WriteBlock(f, self.hdr.particle_emitters, self.particle_emitters)
        for i in self.particle_emitters:
            i.ofsModel = f.tell()
            f.write(i.ModelName)
            FillLine(f)
            i.ofsParticle = f.tell()
            f.write(i.ParticleName)
            FillLine(f)

            WriteAnimBlock(f, i.emission_speed, self.anim_files)
            WriteAnimBlock(f, i.speed_var, self.anim_files)
            WriteAnimBlock(f, i.vert_range, self.anim_files)
            WriteAnimBlock(f, i.hor_range, self.anim_files)
            WriteAnimBlock(f, i.gravity, self.anim_files)
            WriteAnimBlock(f, i.lifespan, self.anim_files)
            WriteAnimBlock(f, i.emission_rate, self.anim_files)
            WriteAnimBlock(f, i.emission_area_len, self.anim_files)
            WriteAnimBlock(f, i.emission_area_width, self.anim_files)
            WriteAnimBlock(f, i.gravity2, self.anim_files)
            WriteAnimBlock(f, i.Enabled, self.anim_files)

            WriteFakeBlock(f, i.color)
            WriteFakeBlock(f, i.opacity)
            WriteFakeBlock(f, i.size)
            WriteFakeBlock(f, i.intensity)
            WriteFakeBlock(f, i.unkfake)

            i.ofsUnk = f.tell()
            for j in i.UnkRef:
                f.write(j.pack())
            FillLine(f)

        oldpos = f.tell()
        f.seek(self.hdr.particle_emitters.offset)
        WriteBlock(f, self.hdr.particle_emitters, self.particle_emitters)
        f.seek(oldpos)

        f.seek(0, SEEK_SET)
        f.write(self.hdr.pack())

        f.close()
