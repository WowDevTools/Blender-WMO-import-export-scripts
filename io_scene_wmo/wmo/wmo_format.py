import bpy
import struct


###########################
# WMO ROOT
###########################

class ChunkHeader:
    def __init__(self, magic='', size=0):
        self.Magic = magic
        self.Size = size

    def read(self, f):
        self.Magic = f.read(4)[0:4].decode('ascii')
        self.Size = struct.unpack("I", f.read(4))[0]

    def write(self, f):
        f.write(self.Magic[:4].encode('ascii'))
        f.write(struct.pack('I', self.Size))

# contain version of file
class MVER_chunk:
    def __init__(self, header=ChunkHeader(), version=0):
        self.Header = header
        self.Version = version

    def read(self, f):
        # read header
        self.Header.read(f)
        self.Version = struct.unpack("I", f.read(4))[0]

    def write(self, f):
        self.Header.Magic = 'REVM'
        self.Header.Size = 4
        self.Header.write(f)
        f.write(struct.pack('I', self.Version))

# WMO Root header
class MOHD_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.nMaterials = 0
        self.nGroups = 0
        self.nPortals = 0
        self.nLights = 0
        self.nModels = 0
        self.nDoodads = 0
        self.nSets = 0
        self.AmbientColor = (0, 0, 0, 0)
        self.ID = 0
        self.BoundingBoxCorner1 = (0.0, 0.0, 0.0)
        self.BoundingBoxCorner2 = (0.0, 0.0, 0.0)
        self.Flags = 0

    def read(self, f):
        # read header
        self.Header.read(f)

        self.nMaterials = struct.unpack("I", f.read(4))[0]
        self.nGroups = struct.unpack("I", f.read(4))[0]
        self.nPortals = struct.unpack("I", f.read(4))[0]
        self.nLights = struct.unpack("I", f.read(4))[0]
        self.nModels = struct.unpack("I", f.read(4))[0]
        self.nDoodads = struct.unpack("I", f.read(4))[0]
        self.nSets = struct.unpack("I", f.read(4))[0]
        self.AmbientColor = struct.unpack("BBBB", f.read(4))
        self.ID = struct.unpack("I", f.read(4))[0]
        self.BoundingBoxCorner1 = struct.unpack("fff", f.read(12))
        self.BoundingBoxCorner2 = struct.unpack("fff", f.read(12))
        self.Flags = struct.unpack("I", f.read(4))[0]

    def write(self, f):
        self.Header.Magic = 'DHOM'
        self.Header.Size = 64

        self.Header.write(f)
        f.write(struct.pack('I', self.nMaterials))
        f.write(struct.pack('I', self.nGroups))
        f.write(struct.pack('I', self.nPortals))
        f.write(struct.pack('I', self.nLights))
        f.write(struct.pack('I', self.nModels))
        f.write(struct.pack('I', self.nDoodads))
        f.write(struct.pack('I', self.nSets))
        f.write(struct.pack('BBBB', *self.AmbientColor))
        f.write(struct.pack('I', self.ID))
        f.write(struct.pack('fff', *self.BoundingBoxCorner1))
        f.write(struct.pack('fff', *self.BoundingBoxCorner2))
        f.write(struct.pack('I', self.Flags))


# Texture names
class MOTX_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.StringTable = bytearray()

    def read(self, f):
        # read header
        self.Header.read(f)
        self.StringTable = f.read(self.Header.Size)

    def write(self, f):
        self.Header.Magic = 'XTOM'
        self.Header.Size = len(self.StringTable)

        self.Header.write(f)
        f.write(self.StringTable)

    def add_string(self, s):
        padding = len(self.StringTable) % 4
        if padding > 0:
            for iPad in range(4 - padding):
                self.StringTable.append(0)

        ofs = len(self.StringTable)
        self.StringTable.extend(s.encode('ascii'))
        self.StringTable.append(0)
        return ofs

    def get_string(self, ofs):
        if ofs >= len(self.StringTable):
            return ''
        start = ofs
        i = ofs
        while self.StringTable[i] != 0:
            i += 1
        return self.StringTable[start:i].decode('ascii')

    def get_all_strings(self):
        strings = []
        cur_str = ""

        for byte in self.StringTable:
            if byte:
                cur_str += chr(byte)
            elif cur_str:
                strings.append(cur_str)
                cur_str = ""

        return strings


class WMO_Material:
    def __init__(self):
        self.Flags = 0
        self.Shader = 0
        self.BlendMode = 0
        self.Texture1Ofs = 0
        self.EmissiveColor = (0, 0, 0, 0)
        self.SidnEmissiveColor = (0, 0, 0, 0)
        self.Texture2Ofs = 0
        self.DiffColor = (0, 0, 0, 0)
        self.TerrainType = 0
        self.Texture3Ofs = 0
        self.Color3 = (0, 0, 0, 0)
        self.Tex3Flags = 0
        self.RunTimeData = (0, 0, 0, 0)

    def read(self, f):
        self.Flags = struct.unpack("I", f.read(4))[0]
        self.Shader = struct.unpack("I", f.read(4))[0]
        self.BlendMode = struct.unpack("I", f.read(4))[0]
        self.Texture1Ofs = struct.unpack("I", f.read(4))[0]
        self.EmissiveColor = struct.unpack("BBBB", f.read(4))
        self.SidnEmissiveColor = struct.unpack("BBBB", f.read(4))
        self.Texture2Ofs = struct.unpack("I", f.read(4))[0]
        self.DiffColor = struct.unpack("BBBB", f.read(4))
        self.TerrainType = struct.unpack("I", f.read(4))[0]
        self.Texture3Ofs = struct.unpack("I", f.read(4))[0]
        self.Color3 = struct.unpack("BBBB", f.read(4))
        self.Tex3Flags = struct.unpack("I", f.read(4))[0]
        self.RunTimeData = struct.unpack("IIII", f.read(16))[0]

    def write(self, f):
        f.write(struct.pack('I', self.Flags))
        f.write(struct.pack('I', self.Shader))
        f.write(struct.pack('I', self.BlendMode))
        f.write(struct.pack('I', self.Texture1Ofs))
        f.write(struct.pack('BBBB', *self.EmissiveColor))
        f.write(struct.pack('BBBB', *self.SidnEmissiveColor))
        f.write(struct.pack('I', self.Texture2Ofs))
        f.write(struct.pack('BBBB', *self.DiffColor))
        f.write(struct.pack('I', self.TerrainType))
        f.write(struct.pack('I', self.Texture3Ofs))
        f.write(struct.pack('BBBB', *self.Color3))
        f.write(struct.pack('I', self.Tex3Flags))
        f.write(struct.pack('IIII', *self.RunTimeData))

# Materials
class MOMT_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.Materials = []

    def read(self, f):
        # read header
        self.Header.read(f)

        self.Materials = []
        for i in range(self.Header.Size // 64):
            mat = WMO_Material()
            mat.read(f)
            self.Materials.append(mat)

    def write(self, f):
        self.Header.Magic = 'TMOM'
        self.Header.Size = len(self.Materials) * 64

        self.Header.write(f)
        for mat in self.Materials:
            mat.write(f)

# group names
class MOGN_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.StringTable = bytearray(b'\x00\x00')

    def read(self, f):
        # read header
        self.Header.read(f)
        self.StringTable = f.read(self.Header.Size)

    def write(self, f):
        self.Header.Magic = 'NGOM'

        # padd 4 bytes after
        padding = len(self.StringTable) % 4
        if(padding > 0):
            for iPad in range(4 - padding):
                self.StringTable.append(0)

        self.Header.Size = len(self.StringTable)

        self.Header.write(f)
        f.write(self.StringTable)

    def add_string(self, s):
        ofs = len(self.StringTable)
        self.StringTable.extend(s.encode('ascii'))
        self.StringTable.append(0)
        return ofs

    def get_string(self, ofs):
        if ofs >= len(self.StringTable):
            return ''
        start = ofs
        i = ofs
        while self.StringTable[i] != 0:
            i += 1
        return self.StringTable[start:i].decode('ascii')

class GroupInfo:
    def __init__(self):
        self.Flags = 0
        self.BoundingBoxCorner1 = (0, 0, 0)
        self.BoundingBoxCorner2 = (0, 0, 0)
        self.NameOfs = 0

    def read(self, f):
        self.Flags = struct.unpack("I", f.read(4))[0]
        self.BoundingBoxCorner1 = struct.unpack("fff", f.read(12))
        self.BoundingBoxCorner2 = struct.unpack("fff", f.read(12))
        self.NameOfs = struct.unpack("I", f.read(4))[0]

    def write(self, f):
        f.write(struct.pack('I', self.Flags))
        f.write(struct.pack('fff', *self.BoundingBoxCorner1))
        f.write(struct.pack('fff', *self.BoundingBoxCorner2))
        f.write(struct.pack('I', self.NameOfs))


# group informations
class MOGI_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.Infos = []

    def read(self, f):
        # read header
        self.Header.read(f)

        count = self.Header.Size // 32

        self.Infos = []
        for i in range(count):
            info = GroupInfo()
            info.read(f)
            self.Infos.append(info)

    def write(self, f):
        self.Header.Magic = 'IGOM'
        self.Header.Size = len(self.Infos) * 32

        self.Header.write(f)
        for info in self.Infos:
            info.write(f)

# skybox
class MOSB_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.Skybox = ''

    def read(self, f):
        # read header
        self.Header.read(f)
        self.Skybox = f.read(self.Header.Size).decode('ascii')

    def write(self, f):
        self.Header.Magic = 'BSOM'

        if not self.Skybox:
            self.Skybox = '\x00\x00\x00'

        self.Header.Size = len(self.Skybox) + 1

        self.Header.write(f)
        f.write(self.Skybox.encode('ascii') + b'\x00')

# portal vertices
class MOPV_chunk:
    def __init__(self):
        self.Header = ChunkHeader()

        self.PortalVertices = []
        #self.Portals = []

    def read(self, f):
        # read header
        self.Header.read(f)

        count = self.Header.Size // 12
        self.PortalVertices = []
        #self.Portals = []

        # 12 = sizeof(float) * 3
        for i in range(count):
            #self.PortalVertices = []
            #for j in range(4):
            self.PortalVertices.append(struct.unpack("fff", f.read(12)))
                #print(self.mopt.Infos[i].nVertices)
            #self.Portals.append(self.PortalVertices)

    def write(self, f):
        self.Header.Magic = 'VPOM'
        self.Header.Size = len(self.PortalVertices) * 12

        self.Header.write(f)
        for v in self.PortalVertices:
            f.write(struct.pack('fff', *v))

class PortalInfo:
    def __init__(self):
        self.StartVertex = 0
        self.nVertices = 0
        self.Normal = (0, 0, 0)
        self.Unknown = 0

    def read(self, f):
        self.StartVertex = struct.unpack("H", f.read(2))[0]
        self.nVertices = struct.unpack("H", f.read(2))[0]
        self.Normal = struct.unpack("fff", f.read(12))
        self.Unknown = struct.unpack("f", f.read(4))[0]

    def write(self, f):
        f.write(struct.pack('H', self.StartVertex))
        f.write(struct.pack('H', self.nVertices))
        f.write(struct.pack('fff', *self.Normal))
        f.write(struct.pack('f', self.Unknown))


# portal infos
class MOPT_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.Infos = []

    def read(self, f):
        # read header
        self.Header.read(f)

        self.Infos = []

        # 20 = sizeof(PortalInfo)
        for i in range(self.Header.Size // 20):
            info = PortalInfo()
            info.read(f)
            self.Infos.append(info)

    def write(self, f):
        self.Header.Magic = 'TPOM'
        self.Header.Size = len(self.Infos) * 20

        self.Header.write(f)
        for info in self.Infos:
            info.write(f)

class PortalRelationship:
    def __init__(self):
        self.PortalIndex = 0
        self.GroupIndex = 0
        self.Side = 0
        self.Padding = 0

    def read(self, f):
        self.PortalIndex = struct.unpack("H", f.read(2))[0]
        self.GroupIndex = struct.unpack("H", f.read(2))[0]
        self.Side = struct.unpack("h", f.read(2))[0]
        self.Padding = struct.unpack("H", f.read(2))[0]

    def write(self, f):
        f.write(struct.pack('H', self.PortalIndex))
        f.write(struct.pack('H', self.GroupIndex))
        f.write(struct.pack('h', self.Side))
        f.write(struct.pack('H', self.Padding))

# portal link 2 groups
class MOPR_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.Relationships = []

    def read(self, f):
        # read header
        self.Header.read(f)

        self.Relationships = []

        for i in range(self.Header.Size // 8):
            relationship = PortalRelationship()
            relationship.read(f)
            self.Relationships.append(relationship)

    def write(self, f):
        self.Header.Magic = 'RPOM'
        self.Header.Size = len(self.Relationships) * 8

        self.Header.write(f)

        for rel in self.Relationships:
            rel.write(f)


# visible vertices
class MOVV_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.VisibleVertices = []

    def read(self, f):
        # read header
        self.Header.read(f)

        self.VisibleVertices = []

        for i in range(self.Header.Size // 12):
            self.VisibleVertices.append(struct.unpack("fff", f.read(12)))

    def write(self, f):
        self.Header.Magic = 'VVOM'
        self.Header.Size = len(self.VisibleVertices) * 12

        self.Header.write(f)

        for v in self.VisibleVertices:
            f.write(struct.pack('fff', *v))

class VisibleBatch:
    def __init__(self):
        self.StartVertex = 0
        self.nVertices = 0

    def read(self, f):
        self.StartVertex = struct.unpack("H", f.read(2))[0]
        self.nVertices = struct.unpack("H", f.read(2))[0]

    def write(self, f):
        f.write(struct.pack('H', self.StartVertex))
        f.write(struct.pack('H', self.nVertices))

# visible batches
class MOVB_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.Batches = []

    def read(self, f):
        # read header
        self.Header.read(f)

        count = self.Header.Size // 4

        self.Batches = []

        for i in range(count):
            batch = VisibleBatch()
            batch.read(f)
            self.Batches.append(batch)

    def write(self, f):
        self.Header.Magic = 'BVOM'
        self.Header.Size = len(self.Batches) * 4

        self.Header.write(f)
        for batch in self.Batches:
            batch.write(f)

class Light:
    def __init__(self):
        self.LightType = 0
        self.Type = 1
        self.UseAttenuation = 1
        self.Padding = 1
        self.Color = (0, 0, 0, 0)
        self.Position = (0, 0, 0)
        self.Intensity = 0
        self.AttenuationStart = 0
        self.AttenuationEnd = 0
        self.Unknown1 = 0
        self.Unknown2 = 0
        self.Unknown3 = 0
        self.Unknown4 = 0

    def read(self, f):
        self.LightType = struct.unpack("B", f.read(1))[0]
        self.Type = struct.unpack("B", f.read(1))[0]
        self.UseAttenuation = struct.unpack("B", f.read(1))[0]
        self.Padding = struct.unpack("B", f.read(1))[0]
        self.Color = struct.unpack("BBBB", f.read(4))
        self.Position = struct.unpack("fff", f.read(12))
        self.Intensity = struct.unpack("f", f.read(4))[0]
        self.AttenuationStart = struct.unpack("f", f.read(4))[0]
        self.AttenuationEnd = struct.unpack("f", f.read(4))[0]
        self.Unknown1 = struct.unpack("f", f.read(4))[0]
        self.Unknown2 = struct.unpack("f", f.read(4))[0]
        self.Unknown3 = struct.unpack("f", f.read(4))[0]
        self.Unknown4 = struct.unpack("f", f.read(4))[0]

    def write(self, f):
        f.write(struct.pack('B', self.LightType))
        f.write(struct.pack('B', self.Type))
        f.write(struct.pack('B', self.UseAttenuation))
        f.write(struct.pack('B', self.Padding))
        f.write(struct.pack('BBBB', *self.Color))
        f.write(struct.pack('fff', *self.Position))
        f.write(struct.pack('f', self.Intensity))
        f.write(struct.pack('f', self.AttenuationStart))
        f.write(struct.pack('f', self.AttenuationEnd))
        f.write(struct.pack('f', self.Unknown1))
        f.write(struct.pack('f', self.Unknown2))
        f.write(struct.pack('f', self.Unknown3))
        f.write(struct.pack('f', self.Unknown4))


# lights
class MOLT_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.Lights = []

    def read(self, f):
        # read header
        self.Header.read(f)

        # 48 = sizeof(Light)
        count = self.Header.Size // 48

        self.Lights = []
        for i in range(count):
            light = Light()
            light.read(f)
            self.Lights.append(light)

    def write(self, f):
        self.Header.Magic = 'TLOM'
        self.Header.Size = len(self.Lights) * 48

        self.Header.write(f)
        for light in self.Lights:
            light.write(f)

class DoodadSet:
    def __init__(self):
        self.Name = ''
        self.StartDoodad = 0
        self.nDoodads = 0
        self.Padding = 0

    def read(self, f):
        self.Name = f.read(20).decode("ascii")
        self.StartDoodad = struct.unpack("I", f.read(4))[0]
        self.nDoodads = struct.unpack("I", f.read(4))[0]
        self.Padding = struct.unpack("I", f.read(4))[0]

    def write(self, f):
        f.write(self.Name.ljust(20, '\0').encode('ascii'))
        f.write(struct.pack('I', self.StartDoodad))
        f.write(struct.pack('I', self.nDoodads))
        f.write(struct.pack('I', self.Padding))

# doodad sets
class MODS_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.Sets = []

    def read(self, f):
        # read header
        self.Header.read(f)

        count = self.Header.Size // 32

        self.Sets = []

        for i in range(count):
            set = DoodadSet()
            set.read(f)
            self.Sets.append(set)

    def write(self, f):
        self.Header.Magic = 'SDOM'
        self.Header.Size = len(self.Sets) * 32

        self.Header.write(f)
        for set in self.Sets:
            set.write(f)


# doodad names
class MODN_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.StringTable = bytearray()

    def read(self, f):
        # read header
        self.Header.read(f)
        self.StringTable = f.read(self.Header.Size)

    def write(self, f):
        self.Header.Magic = 'NDOM'
        self.Header.Size = len(self.StringTable)

        self.Header.write(f)
        f.write(self.StringTable)

    def AddString(self, s):
        padding = len(self.StringTable) % 4
        if padding > 0:
            for iPad in range(4 - padding):
                self.StringTable.append(0)

        ofs = len(self.StringTable)
        self.StringTable.extend(s.encode('ascii'))
        self.StringTable.append(0)
        return ofs

    def get_string(self, ofs):
        if ofs >= len(self.StringTable):
            return ''
        start = ofs
        i = ofs
        while self.StringTable[i] != 0:
            i += 1
        return self.StringTable[start:i].decode('ascii')

class DoodadDefinition:
    def __init__(self):
        self.NameOfs = 0
        self.Flags = 0
        self.Position = (0, 0, 0)
        self.Rotation = [0, 0, 0, 0]
        self.Scale = 0
        self.Color = [0, 0, 0, 0]

    def read(self, f):
        weirdThing = struct.unpack("I", f.read(4))[0]
        self.NameOfs = weirdThing & 0xFFFFFF
        self.Flags = (weirdThing >> 24) & 0xFF
        self.Position = struct.unpack("fff", f.read(12))
        self.Rotation = struct.unpack("ffff", f.read(16))
        self.Scale = struct.unpack("f", f.read(4))[0]
        self.Color = struct.unpack("BBBB", f.read(4))

    def write(self, f):
        weirdThing = ((self.Flags & 0xFF) << 24) | (self.NameOfs & 0xFFFFFF)
        f.write(struct.pack('I', weirdThing))
        f.write(struct.pack('fff', *self.Position))
        f.write(struct.pack('ffff', *self.Rotation))
        f.write(struct.pack('f', self.Scale))
        f.write(struct.pack('BBBB', *self.Color))

# doodad definition
class MODD_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.Definitions = []

    def read(self, f):
        # read header
        self.Header.read(f)

        count = self.Header.Size // 40

        self.Definitions = []
        for i in range(count):
            defi = DoodadDefinition()
            defi.read(f)
            self.Definitions.append(defi)

    def write(self, f):
        self.Header.Magic = 'DDOM'
        self.Header.Size = len(self.Definitions) * 40

        self.Header.write(f)
        for defi in self.Definitions:
            defi.write(f)

# fog
class Fog:
    def __init__(self):
        self.Flags = 0
        self.Position = (0, 0, 0)
        self.SmallRadius = 0
        self.BigRadius = 0
        self.EndDist = 0
        self.StartFactor = 0
        self.Color1 = (0, 0, 0, 0)
        self.EndDist2 = 0
        self.StartFactor2 = 0
        self.Color2 = (0, 0, 0, 0)

    def read(self, f):
        self.Flags = struct.unpack("I", f.read(4))[0]
        self.Position = struct.unpack("fff", f.read(12))
        self.SmallRadius = struct.unpack("f", f.read(4))[0]
        self.BigRadius = struct.unpack("f", f.read(4))[0]
        self.EndDist = struct.unpack("f", f.read(4))[0]
        self.StartFactor = struct.unpack("f", f.read(4))[0]
        self.Color1 = struct.unpack("BBBB", f.read(4))
        self.EndDist2 = struct.unpack("f", f.read(4))[0]
        self.StartFactor2 = struct.unpack("f", f.read(4))[0]
        self.Color2 = struct.unpack("BBBB", f.read(4))

    def write(self, f):
        f.write(struct.pack('I', self.Flags))
        f.write(struct.pack('fff', *self.Position))
        f.write(struct.pack('f', self.SmallRadius))
        f.write(struct.pack('f', self.BigRadius))
        f.write(struct.pack('f', self.EndDist))
        f.write(struct.pack('f', self.StartFactor))
        f.write(struct.pack('BBBB', *self.Color1))
        f.write(struct.pack('f', self.EndDist2))
        f.write(struct.pack('f', self.StartFactor2))
        f.write(struct.pack('BBBB', *self.Color2))

class MFOG_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.Fogs = []

    def read(self, f):
        # read header
        self.Header.read(f)

        count = self.Header.Size // 48

        self.Fogs = []
        for i in range(count):
            fog = Fog()
            fog.read(f)
            self.Fogs.append(fog)

    def write(self, f):
        self.Header.Magic = 'GOFM'
        self.Header.Size = len(self.Fogs) * 48

        self.Header.write(f)
        for fog in self.Fogs:
            fog.write(f)

# Convex volume plane, used only for transport objects
class MCVP_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.convex_volume_planes = []

    def read(self, f):
        self.Header.read(f)

        count = self.Header.Size // 16

        for i in range(0, count):
            self.convex_volume_planes.append(struct.unpack('ffff', f.read(16)))

    def write(self, f):
        self.Header.Magic = 'PVCM'
        self.Header.Size = len(self.convex_volume_planes) * 16

        self.Header.write(f)
        for i in self.convex_volume_planes:
            f.write(struct.pack('ffff', self.convex_volume_planes[i]))

###########################
# WMO GROUP
###########################

class MOGP_FLAG:
    HasCollision = 0x1
    HasVertexColor = 0x4
    Outdoor = 0x8
    DoNotUseLocalLighting = 0x40
    HasLight = 0x200
    HasDoodads = 0x800
    HasWater = 0x1000
    Indoor = 0x2000
    AlwaysDraw = 0x10000
    HasSkybox = 0x40000
    IsNotOcean = 0x80000
    IsMountAllowed = 0x200000
    HasTwoMOCV = 0x1000000
    HasTwoMOTV = 0x2000000


# contain WMO group header
class MOGP_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.GroupNameOfs = 0
        self.DescGroupNameOfs = 0
        self.Flags = 0
        self.BoundingBoxCorner1 = (0, 0, 0)
        self.BoundingBoxCorner2 = (0, 0, 0)
        self.PortalStart = 0
        self.PortalCount = 0
        self.nBatchesA = 0
        self.nBatchesB = 0
        self.nBatchesC = 0
        self.nBatchesD = 0
        self.FogIndices = (0, 0, 0, 0)
        self.LiquidType = 0
        self.GroupID = 0
        self.Unknown1 = 0
        self.Unknown2 = 0

    def read(self, f):
        # read header
        self.Header.read(f)

        self.GroupNameOfs = struct.unpack("I", f.read(4))[0]
        self.DescGroupNameOfs = struct.unpack("I", f.read(4))[0]
        self.Flags = struct.unpack("I", f.read(4))[0]
        self.BoundingBoxCorner1 = struct.unpack("fff", f.read(12))
        self.BoundingBoxCorner2 = struct.unpack("fff", f.read(12))
        self.PortalStart = struct.unpack("H", f.read(2))[0]
        self.PortalCount = struct.unpack("H", f.read(2))[0]
        self.nBatchesA = struct.unpack("H", f.read(2))[0]
        self.nBatchesB = struct.unpack("H", f.read(2))[0]
        self.nBatchesC = struct.unpack("H", f.read(2))[0]
        self.nBatchesD = struct.unpack("H", f.read(2))[0]
        self.FogIndices = struct.unpack("BBBB", f.read(4))
        self.LiquidType = struct.unpack("I", f.read(4))[0]
        self.GroupID = struct.unpack("I", f.read(4))[0]
        self.Unknown1 = struct.unpack("I", f.read(4))[0]
        self.Unknown2 = struct.unpack("I", f.read(4))[0]

    def write(self, f):
        self.Header.Magic = 'PGOM'

        self.Header.write(f)
        f.write(struct.pack('I', self.GroupNameOfs))
        f.write(struct.pack('I', self.DescGroupNameOfs))
        f.write(struct.pack('I', self.Flags))
        f.write(struct.pack('fff', *self.BoundingBoxCorner1))
        f.write(struct.pack('fff', *self.BoundingBoxCorner2))
        f.write(struct.pack('H', self.PortalStart))
        f.write(struct.pack('H', self.PortalCount))
        f.write(struct.pack('H', self.nBatchesA))
        f.write(struct.pack('H', self.nBatchesB))
        f.write(struct.pack('H', self.nBatchesC))
        f.write(struct.pack('H', self.nBatchesD))
        f.write(struct.pack('BBBB', *self.FogIndices))
        f.write(struct.pack('I', self.LiquidType))
        f.write(struct.pack('I', self.GroupID))
        f.write(struct.pack('I', self.Unknown1))
        f.write(struct.pack('I', self.Unknown2))

# Material information
class TriangleMaterial:
    def __init__(self):
        self.Flags = 0
        self.MaterialID = 0

    def read(self, f):
        self.Flags = struct.unpack("B", f.read(1))[0]
        self.MaterialID = struct.unpack("B", f.read(1))[0]

    def write(self, f):
        f.write(struct.pack('B', self.Flags))
        f.write(struct.pack('B', self.MaterialID))

# contain list of triangle materials. One for each triangle
class MOPY_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.TriangleMaterials = []

    def read(self, f):
        # read header
        self.Header.read(f)

        count = self.Header.Size // 2

        self.TriangleMaterials = []

        for i in range(count):
            tri = TriangleMaterial()
            tri.read(f)
            self.TriangleMaterials.append(tri)

    def write(self, f):
        self.Header.Magic = 'YPOM'
        self.Header.Size = len(self.TriangleMaterials) * 2

        self.Header.write(f)
        for tri in self.TriangleMaterials:
            tri.write(f)

# Indices
class MOVI_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.Indices = []

    def read(self, f):
        # read header
        self.Header.read(f)

        # 2 = sizeof(unsigned short)
        count = self.Header.Size // 2

        self.Indices = []

        for i in range(count):
            self.Indices.append(struct.unpack("H", f.read(2))[0])

    def write(self, f):
        self.Header.Magic = 'IVOM'
        self.Header.Size = len(self.Indices) * 2

        self.Header.write(f)
        for i in self.Indices:
            f.write(struct.pack('H', i))

# Vertices
class MOVT_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.Vertices = []

    def read(self, f):
        # read header
        self.Header.read(f)

        # 4 * 3 = sizeof(float) * 3
        count = self.Header.Size // (4 * 3)

        self.Vertices = []

        for i in range(count):
            self.Vertices.append(struct.unpack("fff", f.read(12)))

    def write(self, f):
        self.Header.Magic = 'TVOM'
        self.Header.Size = len(self.Vertices) * 12

        self.Header.write(f)
        for v in self.Vertices:
            f.write(struct.pack('fff', *v))

# Normals
class MONR_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.Normals = []

    def read(self, f):
        # read header
        self.Header.read(f)

        # 4 * 3 = sizeof(float) * 3
        count = self.Header.Size // (4 * 3)

        self.Normals = []

        for i in range(count):
            self.Normals.append(struct.unpack("fff", f.read(12)))

    def write(self, f):
        self.Header.Magic = 'RNOM'
        self.Header.Size = len(self.Normals) * 12

        self.Header.write(f)
        for n in self.Normals:
            f.write(struct.pack('fff', *n))

# Texture coordinates
class MOTV_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.TexCoords = []

    def read(self, f):
        # read header
        self.Header.read(f)

        # 4 * 2 = sizeof(float) * 2
        count = self.Header.Size // (4 * 2)

        self.TexCoords = []

        for i in range(count):
            self.TexCoords.append(struct.unpack("ff", f.read(8)))

    def write(self, f):
        self.Header.Magic = 'VTOM'
        self.Header.Size = len(self.TexCoords) * 8

        self.Header.write(f)
        for tc in self.TexCoords:
            f.write(struct.pack('ff', *tc))

# batch
class Batch:
    def __init__(self):
        self.BoundingBox = (0, 0, 0, 0, 0, 0)
        self.StartTriangle = 0
        self.nTriangle = 0
        self.StartVertex = 0
        self.LastVertex = 0
        self.Unknown = 0
        self.MaterialID = 0

    def read(self, f):
        #not sure
        self.BoundingBox = struct.unpack("hhhhhh", f.read(12))
        self.StartTriangle = struct.unpack("I", f.read(4))[0]
        self.nTriangle = struct.unpack("H", f.read(2))[0]
        self.StartVertex = struct.unpack("H", f.read(2))[0]
        self.LastVertex = struct.unpack("H", f.read(2))[0]
        self.Unknown = struct.unpack("B", f.read(1))[0]
        self.MaterialID = struct.unpack("B", f.read(1))[0]

    def write(self, f):
        f.write(struct.pack('hhhhhh', *self.BoundingBox))
        f.write(struct.pack('I', self.StartTriangle))
        f.write(struct.pack('H', self.nTriangle))
        f.write(struct.pack('H', self.StartVertex))
        f.write(struct.pack('H', self.LastVertex))
        f.write(struct.pack('B', self.Unknown))
        f.write(struct.pack('B', self.MaterialID))

# batches
class MOBA_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.Batches = []

    def read(self, f):
        # read header
        self.Header.read(f)

        count = self.Header.Size // 24

        self.Batches = []

        for i in range(count):
            batch = Batch()
            batch.read(f)
            self.Batches.append(batch)

    def write(self, f):
        self.Header.Magic = 'ABOM'
        self.Header.Size = len(self.Batches) * 24

        self.Header.write(f)
        for b in self.Batches:
            b.write(f)

# lights
class MOLR_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.LightRefs = []

    def read(self, f):
        # read header
        self.Header.read(f)

        # 2 = sizeof(short)
        count = self.Header.Size // 2

        self.LightRefs = []

        for i in range(count):
            self.LightRefs.append(struct.unpack("h", f.read(2))[0])

    def write(self, f):
        self.Header.Magic = 'RLOM'
        self.Header.Size = len(self.LightRefs) * 2

        self.Header.write(f)
        for lr in self.LightRefs:
            f.write(struct.pack('h', lr))

# doodads
class MODR_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.DoodadRefs = []

    def read(self, f):
        # read header
        self.Header.read(f)

        # 2 = sizeof(short)
        count = self.Header.Size // 2

        self.DoodadRefs = []

        for i in range(count):
            self.DoodadRefs.append(struct.unpack("h", f.read(2))[0])

    def write(self, f):
        self.Header.Magic = 'RDOM'
        self.Header.Size = len(self.DoodadRefs) * 2

        self.Header.write(f)
        for dr in self.DoodadRefs:
            f.write(struct.pack('h', dr))

class BSP_PLANE_TYPE:
    YZ_plane = 0
    XZ_plane = 1
    XY_plane = 2
    Leaf = 4 # end node, contains polygons

class BSP_Node:
    def __init__(self):
        self.PlaneType = 0
        self.Children = (0, 0)
        self.NumFaces = 0
        self.FirstFace = 0
        self.Dist = 0

    def read(self, f):
        self.PlaneType = struct.unpack("h", f.read(2))[0]
        self.Children = struct.unpack("hh", f.read(4))
        self.NumFaces = struct.unpack("H", f.read(2))[0]
        self.FirstFace = struct.unpack("I", f.read(4))[0]
        self.Dist = struct.unpack("f", f.read(4))[0]

    def write(self, f):
        f.write(struct.pack('h', self.PlaneType))
        f.write(struct.pack('hh', *self.Children))
        f.write(struct.pack('H', self.NumFaces))
        f.write(struct.pack('I', self.FirstFace))
        f.write(struct.pack('f', self.Dist))

# collision geometry
class MOBN_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.Nodes = []

    def read(self, f):
        # read header
        self.Header.read(f)

        count = self.Header.Size // 0x10

        self.Nodes = []

        for i in range(count):
            node = BSP_Node()
            node.read(f)
            self.Nodes.append(node)

    def write(self, f):
        self.Header.Magic = 'NBOM'
        self.Header.Size = len(self.Nodes) * 0x10

        self.Header.write(f)
        for node in self.Nodes:
            node.write(f)

class MOBR_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.Faces = []

    def read(self, f):
        # read header
        self.Header.read(f)

        count = self.Header.Size // 2

        self.Faces = []

        for i in range(count):
            self.Faces.append(struct.unpack("H", f.read(2))[0])

    def write(self, f):
        self.Header.Magic = 'RBOM'
        self.Header.Size = len(self.Faces) * 2

        self.Header.write(f)
        for face in self.Faces:
            f.write(struct.pack('H', face))

# vertex colors
class MOCV_chunk:
    def __init__(self):
        self.Header = ChunkHeader()
        self.vertColors = []

    def read(self, f):
        # read header
        self.Header.read(f)

        # 4 = sizeof(unsigned char) * 4
        count = self.Header.Size // 4

        self.vertColors = []

        for i in range(count):
            self.vertColors.append(struct.unpack("BBBB", f.read(4)))

    def write(self, f):
        self.Header.Magic = 'VCOM'
        self.Header.Size = len(self.vertColors) * 4

        self.Header.write(f)
        for vc in self.vertColors:
            f.write(struct.pack('BBBB', *vc))

class LiquidVertex:
    def __init__(self):

        self.height = 0

    def read(self, f):
        self.height = struct.unpack("f", f.read(4))


    def write(self, f):
        f.write(struct.pack('f', self.height))

class WaterVertex(LiquidVertex):
    def __init__(self):
        self.flow1 = 0
        self.flow2 = 0
        self.flow1Pct = 0
        self.filler = 0

    def read(self, f):

        self.flow1 = struct.unpack("B", f.read(1))[0]
        self.flow2 = struct.unpack("B", f.read(1))[0]
        self.flow1Pct = struct.unpack("B", f.read(1))[0]
        self.filler = struct.unpack("B", f.read(1))[0]
        LiquidVertex.read(self, f) # Python, wtf?


    def write(self, f):

        f.write(struct.pack('B', self.flow1))
        f.write(struct.pack('B', self.flow2))
        f.write(struct.pack('B', self.flow1Pct))
        f.write(struct.pack('B', self.filler))
        LiquidVertex.write(self, f) # Python, wtf?


class MagmaVertex(LiquidVertex):
    def __init__(self):
        self.u = 0
        self.v = 0

    def read(self, f):
        self.u = struct.unpack("h", f.read(2))[0]
        self.v = struct.unpack("h", f.read(2))[0]
        LiquidVertex.read(self, f)

    def write(self, f):
        f.write(struct.pack('h', self.u))
        f.write(struct.pack('h', self.v))
        LiquidVertex.write(self, f)


class MLIQ_chunk:
    def __init__(self, mat = True):
        self.Header = ChunkHeader()
        self.xVerts = 0
        self.yVerts = 0
        self.xTiles = 0
        self.yTiles = 0
        self.Position = (0, 0, 0)
        self.materialID = 0
        self.VertexMap = []
        self.TileFlags = []
        self.LiquidMaterial = mat

    def read(self, f):
        # read header
        self.Header.read(f)

        self.xVerts = struct.unpack("I", f.read(4))[0]
        self.yVerts = struct.unpack("I", f.read(4))[0]
        self.xTiles = struct.unpack("I", f.read(4))[0]
        self.yTiles = struct.unpack("I", f.read(4))[0]
        self.Position = struct.unpack("fff", f.read(12))
        self.materialID = struct.unpack("H", f.read(2))[0]

        self.VertexMap = []

        for i in range(self.xVerts * self.yVerts):
            vtx = WaterVertex() if self.LiquidMaterial else MagmaVertex()
            vtx.read(f)
            self.VertexMap.append(vtx)

        self.TileFlags = []

        # 0x40 = visible
        # 0x0C = invisible
        # well some other strange things (e.g 0x7F = visible, etc...)

        for i in range(self.xTiles * self.yTiles):
            self.TileFlags.append(struct.unpack("B", f.read(1))[0])


    def write(self, f):
        self.Header.Magic = 'QILM'
        self.Header.Size = 30 + self.xVerts * self.yVerts * 8 + self.xTiles * self.yTiles

        self.Header.write(f)

        f.write(struct.pack('I', self.xVerts))
        f.write(struct.pack('I', self.yVerts))
        f.write(struct.pack('I', self.xTiles))
        f.write(struct.pack('I', self.yTiles))
        f.write(struct.pack('fff', *self.Position))
        f.write(struct.pack('H', self.materialID))

        for vtx in self.VertexMap:
            vtx.write(f)
        for tile_flag in self.TileFlags:
            f.write(struct.pack('B', tile_flag))

