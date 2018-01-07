from .wmo_group import *
from .wmo_format import *
from ..m2 import import_m2 as m2
from mathutils.kdtree import KDTree

import bpy
import operator
import os
import time


class WMOFile:
    """ World of Warcraft WMO """

    def __init__(self, filepath):
        self.filepath = filepath
        self.groups = []
        self.bl_scene_objects = BlenderSceneObjects()
        self.material_lookup = {}
        self.texture_lookup = {}
        self.display_name = os.path.basename(os.path.splitext(filepath)[0])
        self.parent = None

        self.mver = MVER_chunk()
        self.mohd = MOHD_chunk()
        self.motx = MOTX_chunk()
        self.momt = MOMT_chunk()
        self.mogn = MOGN_chunk()
        self.mogi = MOGI_chunk()
        self.mosb = MOSB_chunk()
        self.mopv = MOPV_chunk()
        self.mopt = MOPT_chunk()
        self.mopr = MOPR_chunk()
        self.movv = MOVV_chunk()
        self.movb = MOVB_chunk()
        self.molt = MOLT_chunk()
        self.mods = MODS_chunk()
        self.modn = MODN_chunk()
        self.modd = MODD_chunk()
        self.mfog = MFOG_chunk()
        self.mcvp = MCVP_chunk()

    def read(self):
        """ Read WMO data from files into memory """

        start_time = time.time()

        with open(self.filepath, "rb") as f:

            # check if file is a WMO root or a WMO group, or unknown
            f.seek(12)
            hdr = ChunkHeader()
            hdr.read(f)
            f.seek(0)

            if hdr.Magic == "DHOM":
                self.mver.read(f)
                self.mohd.read(f)
                self.motx.read(f)
                self.momt.read(f)
                self.mogn.read(f)
                self.mogi.read(f)
                self.mosb.read(f)
                self.mopv.read(f)
                self.mopt.read(f)
                self.mopr.read(f)
                self.movv.read(f)
                self.movb.read(f)
                self.molt.read(f)
                self.mods.read(f)
                self.modn.read(f)
                self.modd.read(f)
                self.mfog.read(f)

                if f.tell() != os.fstat(f.fileno()).st_size:
                    self.mcvp.read(f)

                print("\nDone reading root file: <<" + os.path.basename(f.name) + ">>")
                root_name = os.path.splitext(self.filepath)[0]


                for i in range(self.mohd.nGroups):
                    group_name = root_name + "_" + str(i).zfill(3) + ".wmo"

                    if not os.path.isfile(group_name):
                        raise FileNotFoundError("\nNot all referenced WMO groups are present in the directory.\a")

                    group = WMOGroupFile(self)
                    group.read(open(group_name, 'rb'))
                    self.groups.append(group)

            elif hdr.Magic == "PGOM":
                raise NotImplementedError("\nImport of separate WMO group files is not supported. "
                                          "Please import the root file.\a")

            else:
                raise Exception("\nFile is not a WMO file or corrupted.\a")

            print("\nDone reading WMO. \nTotal reading time: ",
                  time.strftime("%M minutes %S seconds.", time.gmtime(time.time() - start_time)))

    def write(self):
        """ Write WMO data from memory into files """

        start_time = time.time()

        with open(self.filepath, 'wb') as f:
            print("\n\n=== Writing root file ===")

            self.mver.write(f)
            self.mohd.write(f)
            self.motx.write(f)
            self.momt.write(f)
            self.mogn.write(f)
            self.mogi.write(f)
            self.mosb.write(f)
            self.mopv.write(f)
            self.mopt.write(f)
            self.mopr.write(f)
            self.movv.write(f)
            self.movb.write(f)
            self.molt.write(f)
            self.mods.write(f)
            self.modn.write(f)
            self.modd.write(f)
            self.mfog.write(f)

            print("\nDone writing root file: <<" + os.path.basename(f.name) + ">>")

        print("\n\n=== Writing group files ===")
        for index, group in enumerate(self.groups):
            with open(os.path.splitext(self.filepath)[0] + "_" + str(index).zfill(3) + ".wmo", 'wb') as f:
                group.write(f)

        print("\nDone writing WMO. \nTotal writing time: ",
              time.strftime("%M minutes %S seconds.\a", time.gmtime(time.time() - start_time)))

    def compare_materials(self, material):
        """ Compare two WoW material properties """

        get_attributes = operator.attrgetter(
            'Shader', 'TerrainType', 'BlendingMode',
            'Texture1', 'EmissiveColor', 'Flags',
            'Texture2', 'DiffColor')

        mat1 = get_attributes(material.WowMaterial)

        for material2, index in self.material_lookup.items():

            if mat1 == get_attributes(material2.WowMaterial):
                return index

        return None

    def add_material(self, mat):
        """ Add material if not already added, then return index in root file """

        mat_index = self.compare_materials(mat)

        if mat_index is not None:
            return mat_index

        else:
            # else add it then return index
            if not mat.WowMaterial.Enabled:
                self.material_lookup[mat] = 0xFF
                return 0xFF
            else:
                self.material_lookup[mat] = len(self.momt.Materials)

                WowMat = WMO_Material()

                WowMat.Shader = int(mat.WowMaterial.Shader)
                WowMat.BlendMode = int(mat.WowMaterial.BlendingMode)
                WowMat.TerrainType = int(mat.WowMaterial.TerrainType)

                if mat.WowMaterial.Texture1 in self.texture_lookup:
                    WowMat.Texture1Ofs = self.texture_lookup[mat.WowMaterial.Texture1]
                else:
                    self.texture_lookup[mat.WowMaterial.Texture1] = self.motx.add_string(mat.WowMaterial.Texture1)
                    WowMat.Texture1Ofs = self.texture_lookup[mat.WowMaterial.Texture1]

                WowMat.EmissiveColor = (int(mat.WowMaterial.EmissiveColor[0] * 255),
                                        int(mat.WowMaterial.EmissiveColor[1] * 255),
                                        int(mat.WowMaterial.EmissiveColor[2] * 255),
                                        int(mat.WowMaterial.EmissiveColor[3] * 255))

                WowMat.TextureFlags1 = 0

                if mat.WowMaterial.Texture2 in self.texture_lookup:
                    WowMat.Texture2Ofs = self.texture_lookup[mat.WowMaterial.Texture2]
                else:
                    self.texture_lookup[mat.WowMaterial.Texture2] = self.motx.add_string(mat.WowMaterial.Texture2)
                    WowMat.Texture2Ofs = self.texture_lookup[mat.WowMaterial.Texture2]

                WowMat.DiffColor = (int(mat.WowMaterial.DiffColor[0] * 255),
                                    int(mat.WowMaterial.DiffColor[1] * 255),
                                    int(mat.WowMaterial.DiffColor[2] * 255),
                                    int(mat.WowMaterial.DiffColor[3] * 255))

                for flag in mat.WowMaterial.Flags:
                    WowMat.Flags |= int(flag)

                self.momt.Materials.append(WowMat)

                return self.material_lookup[mat]

    def add_group_info(self, flags, bounding_box, name, desc):
        """ Add group info, then return offset of name and desc in a tuple """
        group_info = GroupInfo()

        group_info.Flags = flags  # 8
        group_info.BoundingBoxCorner1 = bounding_box[0].copy()
        group_info.BoundingBoxCorner2 = bounding_box[1].copy()
        group_info.NameOfs = self.mogn.add_string(name)  # 0xFFFFFFFF

        desc_ofs = self.mogn.add_string(desc)

        self.mogi.Infos.append(group_info)

        return group_info.NameOfs, desc_ofs

    def load_materials(self):
        """ Load materials from WoW WMO root file """
        self.material_lookup = {}
        texture_path = os.path.dirname(self.filepath) + "\\"

        images = []
        image_names = []

        # Add ghost material
        mat = bpy.data.materials.get("WowMaterial_ghost")
        if not mat:
            mat = bpy.data.materials.new("WowMaterial_ghost")
            mat.diffuse_color = (0.2, 0.5, 1.0)
            mat.diffuse_intensity = 1.0
            mat.alpha = 0.15
            mat.transparency_method = 'Z_TRANSPARENCY'
            mat.use_transparency = True

        self.material_lookup[0xFF] = mat

        for index, wmo_material in enumerate(self.momt.Materials):
            texture1 = self.motx.get_string(wmo_material.Texture1Ofs)
            material_name = os.path.basename(texture1)[:-4] + '.png'

            mat = bpy.data.materials.new(material_name)
            self.material_lookup[index] = mat

            mat.WowMaterial.Enabled = True
            mat.WowMaterial.Shader = str(wmo_material.Shader)
            mat.WowMaterial.BlendingMode = str(wmo_material.BlendMode)
            mat.WowMaterial.Texture1 = texture1
            mat.WowMaterial.EmissiveColor = [x / 255 for x in wmo_material.EmissiveColor[0:4]]
            mat.WowMaterial.Texture2 = self.motx.get_string(wmo_material.Texture2Ofs)
            mat.WowMaterial.DiffColor = [x / 255 for x in wmo_material.DiffColor[0:4]]
            mat.WowMaterial.TerrainType = str(wmo_material.TerrainType)

            mat_flags = set()
            bit = 1
            while bit <= 0x80:
                if wmo_material.Flags & bit:
                    mat_flags.add(str(bit))
                bit <<= 1
            mat.WowMaterial.Flags = mat_flags

            # set texture slot and load texture

            if mat.WowMaterial.Texture1:
                tex1_slot = mat.texture_slots.create(2)
                tex1_slot.uv_layer = "UVMap"
                tex1_slot.texture_coords = 'UV'

                tex1_name = material_name + "_Tex_01"
                tex1 = bpy.data.textures.new(tex1_name, 'IMAGE')
                tex1_slot.texture = tex1

                try:
                    tex1_img_filename = os.path.splitext(mat.WowMaterial.Texture1)[0] + '.png'

                    img1_loaded = False

                    # check if image already loaded
                    for iImg in range(len(images)):
                        if image_names[iImg] == tex1_img_filename:
                            tex1.image = images[iImg]
                            img1_loaded = True
                            break

                    # if image is not loaded, do it
                    if not img1_loaded:
                        tex1_img = bpy.data.images.load(texture_path + tex1_img_filename)
                        tex1.image = tex1_img
                        images.append(tex1_img)
                        image_names.append(tex1_img_filename)

                except:
                    pass

            # set texture slot and load texture
            if mat.WowMaterial.Texture2:
                tex2_slot = mat.texture_slots.create(1)
                tex2_slot.uv_layer = "UVMap"
                tex2_slot.texture_coords = 'UV'

                tex2_name = material_name + "_Tex_02"
                tex2 = bpy.data.textures.new(tex2_name, 'IMAGE')
                tex2_slot.texture = tex2

                try:
                    tex2_img_filename = os.path.splitext(mat.WowMaterial.Texture2)[0] + '.png'

                    img2_loaded = False

                    # check if image already loaded
                    for iImg in range(len(images)):
                        if image_names[iImg] == tex2_img_filename:
                            tex2.image = images[iImg]
                            img2_loaded = True
                            break

                    # if image is not loaded, do it
                    if not img2_loaded:
                        tex2_img = bpy.data.images.load(texture_path + tex2_img_filename)
                        tex2.image = tex2_img
                        images.append(tex2_img)
                        image_names.append(tex2_img_filename)
                except:
                    pass

    def load_lights(self):
        """ Load WoW WMO MOLT lights """
        for i in range(len(self.molt.Lights)):
            l = self.molt.Lights[i]

            bl_light_types = ['POINT', 'SPOT', 'SUN', 'POINT']

            try:
                l_type = bl_light_types[l.LightType]
            except IndexError:
                raise Exception("Light type unknown : {} (light nbr : {})".format(str(l.LightType), str(i)))

            light_name = self.display_name + "_Light_" + str(i).zfill(2)
            light = bpy.data.lamps.new(light_name, l_type)
            light.color = (l.Color[2] / 255, l.Color[1] / 255, l.Color[0] / 255)
            light.energy = l.Intensity

            if l.LightType in {0, 1}:
                light.falloff_type = 'INVERSE_LINEAR'
                light.distance = l.Unknown4 / 2
                light.use_sphere = True

            light.WowLight.Enabled = True
            light.WowLight.LightType = str(l.LightType)
            light.WowLight.Type = bool(l.Type)
            light.WowLight.UseAttenuation = bool(l.UseAttenuation)
            light.WowLight.Padding = bool(l.Padding)
            light.WowLight.Type = bool(l.Type)
            light.WowLight.Color = light.color
            light.WowLight.ColorAlpha = l.Color[3] / 255
            light.WowLight.Intensity = l.Intensity
            light.WowLight.AttenuationStart = l.AttenuationStart
            light.WowLight.AttenuationEnd = l.AttenuationEnd

            obj = bpy.data.objects.new(light_name, light)
            obj.location = self.molt.Lights[i].Position

            bpy.context.scene.objects.link(obj)

            if self.parent:
                obj.parent = self.parent


    def load_fogs(self):
        """ Load WoW WMO fog objects """
        for i in range(len(self.mfog.Fogs)):

            f = self.mfog.Fogs[i]

            bpy.ops.mesh.primitive_uv_sphere_add()
            fog = bpy.context.scene.objects.active

            if not f.BigRadius:
                fog.hide = False

            fog.name = self.display_name + "_Fog_" + str(i).zfill(2)

            # applying real object transformation
            fog.location = f.Position
            bpy.ops.transform.resize(value=(f.BigRadius, f.BigRadius, f.BigRadius)) # 0.5 is the default sphere radius

            bpy.ops.object.shade_smooth()
            fog.draw_type = 'SOLID'
            fog.show_transparent = True
            fog.show_name = True
            fog.color = (f.Color1[2] / 255, f.Color1[1] / 255, f.Color1[0] / 255, 0.0)

            mesh = fog.data

            material = bpy.data.materials.new(name=fog.name)

            if mesh.materials:
                mesh.materials[0] = material
            else:
                mesh.materials.append(material)

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.object.material_slot_assign()
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')

            mesh.materials[0].use_object_color = True
            mesh.materials[0].use_transparency = True
            mesh.materials[0].alpha = 0.35

            # applying object properties

            fog.WowFog.Enabled = True
            if f.Flags & 0x01:
                fog.WowFog.IgnoreRadius = True
            if f.Flags & 0x10:
                fog.WowFog.Unknown = True

            if f.SmallRadius != 0:
                fog.WowFog.InnerRadius = int(f.SmallRadius / f.BigRadius * 100)
            else:
                fog.WowFog.InnerRadius = 0

            fog.WowFog.EndDist = f.EndDist
            fog.WowFog.StartFactor = f.StartFactor
            fog.WowFog.Color1 = (f.Color1[2] / 255, f.Color1[1] / 255, f.Color1[0] / 255)
            fog.WowFog.EndDist2 = f.EndDist2
            fog.WowFog.StartFactor2 = f.StartFactor2
            fog.WowFog.Color2 = (f.Color2[2] / 255, f.Color2[1] / 255, f.Color2[0] / 255)

            if self.parent:
                fog.parent = self.parent

    def load_doodads(self, dir=None, game_data=None):
        """ Load doodad sets to scene. Two modes are supported: data storing and actual import."""
        scene = bpy.context.scene
        if game_data and dir:
            obj_map = {}

            for doodad_set in self.mods.Sets:

                bpy.ops.object.empty_add(type='SPHERE', location=(0, 0, 0))
                anchor = bpy.context.scene.objects.active
                anchor.name = doodad_set.Name
                anchor.hide = True
                anchor.hide_select = True
                anchor.lock_location = (True, True, True)
                anchor.lock_rotation = (True, True, True)
                anchor.lock_scale = (True, True, True)

                if self.parent:
                    anchor.parent = self.parent

                for i in range(doodad_set.StartDoodad, doodad_set.StartDoodad + doodad_set.nDoodads):
                    doodad = self.modd.Definitions[i]
                    doodad_path = os.path.splitext(self.modn.get_string(doodad.NameOfs))[0] + ".m2"

                    nobj = None
                    obj = obj_map.get(doodad_path)

                    if not obj:
                        try:
                            obj = m2.m2_to_blender_mesh(dir, doodad_path, game_data)
                        except:
                            bpy.ops.mesh.primitive_cube_add()
                            obj = bpy.context.scene.objects.active
                            print("\nFailed to import model: <<{}>>. Placeholder is imported instead.".format(doodad_path))

                        obj.WoWDoodad.Enabled = True
                        obj.WoWDoodad.Path = doodad_path

                        obj_map[doodad_path] = obj
                        nobj = obj
                    else:
                        nobj = obj.copy()
                        scene.objects.link(nobj)

                    nobj.WoWDoodad.Color = (doodad.Color[2] / 255,
                                            doodad.Color[1] / 255,
                                            doodad.Color[0] / 255,
                                            doodad.Color[3] / 255)

                    flags = []
                    bit = 1
                    while bit <= 0x8:
                        if doodad.Flags & bit:
                            flags.append(str(bit))
                        bit <<= 1

                    nobj.WoWDoodad.Flags = set(flags)

                    # place the object correctly on the scene
                    nobj.location = doodad.Position
                    nobj.scale = (doodad.Scale, doodad.Scale, doodad.Scale)

                    nobj.rotation_mode = 'QUATERNION'
                    nobj.rotation_quaternion = (doodad.Rotation[3],
                                                doodad.Rotation[0],
                                                doodad.Rotation[1],
                                                doodad.Rotation[2])
                    nobj.parent = anchor
                    nobj.hide = True

        else:
            string_filter = []

            scene.WoWRoot.MODS_Sets.clear()
            scene.WoWRoot.MODN_StringTable.clear()
            scene.WoWRoot.MODD_Definitions.clear()

            for doodad_set in self.mods.Sets:
                property_set = scene.WoWRoot.MODS_Sets.add()
                property_set.Name = doodad_set.Name
                property_set.StartDoodad = doodad_set.StartDoodad
                property_set.nDoodads = doodad_set.nDoodads
                property_set.Padding = doodad_set.Padding

            for doodad_definition in self.modd.Definitions:
                property_definition = scene.WoWRoot.MODD_Definitions.add()
                property_definition.NameOfs = doodad_definition.NameOfs
                property_definition.Flags = doodad_definition.Flags
                property_definition.Position = doodad_definition.Position

                property_definition.Rotation = (doodad_definition.Rotation[0],
                                                doodad_definition.Rotation[1],
                                                doodad_definition.Rotation[2])

                property_definition.Tilt = doodad_definition.Rotation[3]
                property_definition.Scale = doodad_definition.Scale

                property_definition.Color = (doodad_definition.Color[0],
                                             doodad_definition.Color[1],
                                             doodad_definition.Color[2])

                property_definition.ColorAlpha = doodad_definition.Color[3]

                if property_definition.NameOfs not in string_filter:
                    path = scene.WoWRoot.MODN_StringTable.add()
                    path.Ofs = property_definition.NameOfs
                    path.String = self.modn.get_string(property_definition.NameOfs)
                    string_filter.append(property_definition.NameOfs)

    def load_portals(self):
        """ Load WoW WMO portal planes """
        vert_count = 0
        for index, portal in enumerate(self.mopt.Infos):
            portal_name = self.display_name + "_Portal_" + str(index).zfill(3)

            verts = []
            face = []
            faces = []

            for j in range(portal.nVertices):
                if (len(face) < 4):
                    verts.append(self.mopv.PortalVertices[vert_count])
                    face.append(j)
                vert_count += 1

            faces.append(face)

            mesh = bpy.data.meshes.new(portal_name)

            obj = bpy.data.objects.new(portal_name, mesh)

            obj.WowPortalPlane.Enabled = True
            first_relationship = True

            for relation in self.mopr.Relationships:
                if relation.PortalIndex == index:
                    group_name = self.mogn.get_string(self.groups[relation.GroupIndex].mogp.GroupNameOfs)
                    if first_relationship:
                        obj.WowPortalPlane.First = group_name
                        first_relationship = False
                    else:
                        obj.WowPortalPlane.Second = group_name
                        break

            mesh.from_pydata(verts, [], faces)
            bpy.context.scene.objects.link(obj)

            if self.parent:
                obj.parent = self.parent

    def load_properties(self):
        """ Load global WoW WMO properties """
        properties = bpy.context.scene.WoWRoot
        properties.AmbientColor = [float(self.mohd.AmbientColor[2] / 255),
                                   float(self.mohd.AmbientColor[1] / 255),
                                   float(self.mohd.AmbientColor[0]) / 255,
                                   float(self.mohd.AmbientColor[3]) / 255]

        flags = set()
        if self.mohd.Flags & 0x1:
            flags.add("0")
        if self.mohd.Flags & 0x2:
            flags.add("2")
        if self.mohd.Flags & 0x8:
            flags.add("1")

        properties.Flags = flags
        properties.SkyboxPath = self.mosb.Skybox
        properties.WMOid = self.mohd.ID

    def get_object_bounding_box(self, obj):
        """ Calculate bounding box of an object """
        corner1 = [0.0, 0.0, 0.0]
        corner2 = [0.0, 0.0, 0.0]

        for v in obj.bound_box:
            if v[0] < corner1[0]:
                corner1[0] = v[0]
            if v[1] < corner1[1]:
                corner1[1] = v[1]
            if v[2] < corner1[2]:
                corner1[2] = v[2]

            if v[0] > corner2[0]:
                corner2[0] = v[0]
            if v[1] > corner2[1]:
                corner2[1] = v[1]
            if v[2] > corner2[2]:
                corner2[2] = v[2]

        return (corner1, corner2)

    def get_global_bounding_box(self):
        """ Calculate bounding box of an entire scene """
        corner1 = self.mogi.Infos[0].BoundingBoxCorner1
        corner2 = self.mogi.Infos[0].BoundingBoxCorner2

        for gi in self.mogi.Infos:
            v = gi.BoundingBoxCorner1
            if v[0] < corner1[0]:
                corner1[0] = v[0]
            if v[1] < corner1[1]:
                corner1[1] = v[1]
            if v[2] < corner1[2]:
                corner1[2] = v[2]

            v = gi.BoundingBoxCorner2
            if v[0] > corner2[0]:
                corner2[0] = v[0]
            if v[1] > corner2[1]:
                corner2[1] = v[1]
            if v[2] > corner2[2]:
                corner2[2] = v[2]

        return corner1, corner2

    def save_doodad_sets(self):
        """ Save doodads data from Blender scene to WMO root """
        start_time = time.time()

        if len(self.bl_scene_objects.doodad_sets):
            doodad_paths = {}

            has_global = False

            for set_name, doodads in self.bl_scene_objects.doodad_sets:
                print("\nSaving doodadset: <<{}>>".format(set_name))

                doodad_set = DoodadSet()
                doodad_set.Name = set_name
                doodad_set.StartDoodad = len(self.modd.Definitions)

                for doodad in doodads:
                    doodad_def = DoodadDefinition()

                    path = os.path.splitext(doodad.WoWDoodad.Path)[0] + ".MDX"

                    doodad_def.NameOfs = doodad_paths.get(path)
                    if not doodad_def.NameOfs:
                        doodad_def.NameOfs = self.modn.AddString(path)
                        doodad_paths[path] = doodad_def.NameOfs

                    doodad_def.Position = doodad.matrix_world * mathutils.Vector((0,0,0))

                    doodad.rotation_mode = 'QUATERNION'

                    doodad_def.Rotation = (doodad.rotation_quaternion[1],
                                           doodad.rotation_quaternion[2],
                                           doodad.rotation_quaternion[3],
                                           doodad.rotation_quaternion[0])

                    doodad_def.Scale = doodad.scale[0]

                    doodad_def.Color = (int(doodad.WoWDoodad.Color[2] * 255),
                                        int(doodad.WoWDoodad.Color[1] * 255),
                                        int(doodad.WoWDoodad.Color[0] * 255),
                                        int(doodad.WoWDoodad.Color[3] * 255))

                    for flag in doodad.WoWDoodad.Flags:
                        doodad_def.Flags |= int(flag)

                    self.modd.Definitions.append(doodad_def)

                doodad_set.nDoodads = len(self.modd.Definitions) - doodad_set.StartDoodad

                if set_name == "Set_$DefaultGlobal":
                    self.mods.Sets.insert(0, doodad_set)
                    has_global = True
                else:
                    self.mods.Sets.append(doodad_set)

                    print("Done saving doodadset: <<{}>>".format(set_name))

            if not has_global:
                doodad_set = DoodadSet()
                doodad_set.Name = "Set_$DefaultGlobal"
                doodad_set.StartDoodad = 0
                doodad_set.nDoodads = 0
                self.mods.Sets.insert(0, doodad_set)

        elif len(bpy.context.scene.WoWRoot.MODS_Sets):
            print("\nSaving preserved doodadset data")
            scene = bpy.context.scene
            ofsMap = {}

            for property_set in scene.WoWRoot.MODS_Sets:
                doodad_set = DoodadSet()
                doodad_set.Name = property_set.Name
                doodad_set.StartDoodad = property_set.StartDoodad
                doodad_set.nDoodads = property_set.nDoodads
                doodad_set.Padding = property_set.Padding

                self.mods.Sets.append(doodad_set)

            for modn_string in scene.WoWRoot.MODN_StringTable:
                ofsMap[modn_string.Ofs] = self.modn.AddString(modn_string.String)

            for property_def in scene.WoWRoot.MODD_Definitions:
                doodad_def = DoodadDefinition()
                doodad_def.NameOfs = ofsMap.get(property_def.NameOfs)
                doodad_def.Flags = property_def.Flags
                doodad_def.Position = property_def.Position

                doodad_def.Rotation = [property_def.Rotation[0],
                                       property_def.Rotation[1],
                                       property_def.Rotation[2],
                                       0.0]

                doodad_def.Rotation[3] = property_def.Tilt
                doodad_def.Scale = property_def.Scale

                doodad_def.Color = [int(property_def.Color[0]),
                                    int(property_def.Color[1]),
                                    int(property_def.Color[2]),
                                    0]

                doodad_def.Color[3] = int(property_def.ColorAlpha)

                self.modd.Definitions.append(doodad_def)

        print("\nDone saving doodad sets. "
              "\nTotal saving time: ", time.strftime("%M minutes %S seconds", time.gmtime(time.time() - start_time)))

    def save_lights(self):
        start_time = time.time()
        print("\nSaving lights")

        for obj in self.bl_scene_objects.lights:
            mesh = obj.data

            light = Light()
            light.LightType = int(mesh.WowLight.LightType)

            if light.LightType in {0, 1}:
                light.Unknown4 = mesh.distance * 2

            light.Type = mesh.WowLight.Type
            light.UseAttenuation = mesh.WowLight.UseAttenuation
            light.Padding = mesh.WowLight.Padding

            light.Color = (int(mesh.WowLight.Color[2] * 255),
                           int(mesh.WowLight.Color[1] * 255),
                           int(mesh.WowLight.Color[0] * 255),
                           int(mesh.WowLight.ColorAlpha * 255))

            light.Position = obj.location
            light.Intensity = mesh.WowLight.Intensity
            light.AttenuationStart = mesh.WowLight.AttenuationStart
            light.AttenuationEnd = mesh.WowLight.AttenuationEnd
            self.molt.Lights.append(light)


        print("\nDone saving lights. "
              "\nTotal saving time: ", time.strftime("%M minutes %S seconds", time.gmtime(time.time() - start_time)))

    def save_liquids(self):
        start_time = time.time()

        for liquid_obj in self.bl_scene_objects.liquids:
            print("\nSaving liquid: <<{}>>".format(liquid_obj.name))

            if not liquid_obj.WowLiquid.WMOGroup:
                print("WARNING: Failed saving liquid: <<{}>>".format(liquid_obj.name))
                continue
            group_obj = bpy.context.scene.objects[liquid_obj.WowLiquid.WMOGroup]

            group_index = group_obj.WowWMOGroup.GroupID
            group = self.groups[group_index]

            group.save_liquid(liquid_obj)

            print("Done saving liquid: <<{}>>".format(liquid_obj.name))

        print("\nDone saving liquids. "
              "\nTotal saving time: ", time.strftime("%M minutes %S seconds", time.gmtime(time.time() - start_time)))

    def save_portals(self):
        start_time = time.time()
        print("\nSaving portals")

        saved_portals_ids = []

        self.mopt.Infos = len(self.bl_scene_objects.portals) * [None]

        for group_obj in self.bl_scene_objects.groups:

            portal_relations = group_obj.WowWMOGroup.Relations.Portals
            group_index = group_obj.WowWMOGroup.GroupID
            group = self.groups[group_index]
            group.mogp.PortalStart = len(self.mopr.Relationships)

            for relation in portal_relations:
                portal_obj = bpy.context.scene.objects[relation.id]
                portal_index = portal_obj.WowPortalPlane.PortalID

                if portal_index not in saved_portals_ids:
                    print("\nSaving portal: <<{}>>".format(portal_obj.name))

                    portal_mesh = portal_obj.data
                    portal_info = PortalInfo()
                    portal_info.StartVertex = len(self.mopv.PortalVertices)
                    v = []

                    for poly in portal_mesh.polygons:
                        for loop_index in poly.loop_indices:
                            vertex_pos = portal_mesh.vertices[portal_mesh.loops[loop_index].vertex_index].co \
                                         * portal_obj.matrix_world
                            self.mopv.PortalVertices.append(vertex_pos)
                            v.append(vertex_pos)

                    v_A = v[0][1] * v[1][2] - v[1][1] * v[0][2] - v[0][1] * v[2][2] + v[2][1] * v[0][2] + v[1][1] * v[2][2] - \
                          v[2][1] * v[1][2]
                    v_B = -v[0][0] * v[1][2] + v[2][0] * v[1][2] + v[1][0] * v[0][2] - v[2][0] * v[0][2] - v[1][0] * v[2][2] + \
                          v[0][0] * v[2][2]
                    v_C = v[2][0] * v[0][1] - v[1][0] * v[0][1] - v[0][0] * v[2][1] + v[1][0] * v[2][1] - v[2][0] * v[1][1] + \
                          v[0][0] * v[1][1]
                    v_D = -v[0][0] * v[1][1] * v[2][2] + v[0][0] * v[2][1] * v[1][2] + v[1][0] * v[0][1] * v[2][2] - v[1][0] * \
                          v[2][1] * v[0][2] - v[2][0] * v[0][1] * v[1][2] + v[2][0] * v[1][1] * v[0][2]

                    portal_info.Unknown = v_D / math.sqrt(v_A * v_A + v_B * v_B + v_C * v_C)
                    portal_info.nVertices = len(self.mopv.PortalVertices) - portal_info.StartVertex
                    portal_info.Normal = tuple(portal_mesh.polygons[0].normal)

                    self.mopt.Infos[portal_index] = portal_info
                    saved_portals_ids.append(portal_index)

                    print("Done saving portal: <<{}>>".format(portal_obj.name))

                first = bpy.context.scene.objects[self.bl_scene_objects.portals[portal_index].WowPortalPlane.First]
                second = bpy.context.scene.objects[self.bl_scene_objects.portals[portal_index].WowPortalPlane.Second]

                # calculating portal relation
                relation = PortalRelationship()
                relation.PortalIndex = portal_index
                relation.GroupIndex = second.WowWMOGroup.GroupID if first.name == group_obj.name else first.WowWMOGroup.GroupID
                relation.Side = group.get_portal_direction(portal_obj, group_obj)

                self.mopr.Relationships.append(relation)

            group.mogp.PortalCount = len(self.mopr.Relationships) - group.mogp.PortalStart

        print("\nDone saving portals. "
              "\nTotal saving time: ", time.strftime("%M minutes %S seconds", time.gmtime(time.time() - start_time)))

    def save_fogs(self):
        start_time = time.time()
        print("\nSaving fogs")

        for fog_obj in self.bl_scene_objects.fogs:
            print("\nSaving fog: <<{}>>".format(fog_obj.name))
            fog = Fog()

            fog.BigRadius = fog_obj.dimensions[2] / 2
            fog.SmallRadius = fog.BigRadius * (fog_obj.WowFog.InnerRadius / 100)

            fog.Color1 = (int(fog_obj.WowFog.Color1[2] * 255),
                          int(fog_obj.WowFog.Color1[1] * 255),
                          int(fog_obj.WowFog.Color1[0] * 255),
                          0xFF)

            fog.Color2 = (int(fog_obj.WowFog.Color2[2] * 255),
                          int(fog_obj.WowFog.Color2[1] * 255),
                          int(fog_obj.WowFog.Color2[0] * 255),
                          0xFF)

            fog.EndDist = fog_obj.WowFog.EndDist
            fog.EndDist2 = fog_obj.WowFog.EndDist2
            fog.Position = fog_obj.location
            fog.StartFactor = fog_obj.WowFog.StartFactor
            fog.StarFactor2 = fog_obj.WowFog.StartFactor2

            if fog_obj.WowFog.IgnoreRadius:
                fog.Flags |= 0x01
            if fog_obj.WowFog.Unknown:
                fog.Flags |= 0x10

            self.mfog.Fogs.append(fog)

            print("Done saving fog: <<{}>>".format(fog_obj.name))

        print("\nDone saving fogs. "
              "\nTotal saving time: ", time.strftime("%M minutes %S seconds", time.gmtime(time.time() - start_time)))

    def save_root_header(self):
        print("\nSaving root header")

        scene = bpy.context.scene

        self.mver.Version = 17

        # setting up default fog with default blizzlike values.
        if not len(self.mfog.Fogs):
            empty_fog = Fog()
            empty_fog.Color1 = (0xFF, 0xFF, 0xFF, 0xFF)
            empty_fog.Color2 = (0x00, 0x00, 0x00, 0xFF)
            empty_fog.EndDist = 444.4445
            empty_fog.EndDist2 = 222.2222
            empty_fog.StartFactor = 0.25
            empty_fog.StartFactor2 = -0.5
            self.mfog.Fogs.append(empty_fog)

        bb = self.get_global_bounding_box()
        self.mohd.BoundingBoxCorner1 = bb[0]
        self.mohd.BoundingBoxCorner2 = bb[1]

        # DBC foreign keys
        self.mohd.ID = scene.WoWRoot.WMOid
        self.mosb.Skybox = scene.WoWRoot.SkyboxPath

        self.mohd.AmbientColor = [int(scene.WoWRoot.AmbientColor[2] * 255),
                                  int(scene.WoWRoot.AmbientColor[1] * 255),
                                  int(scene.WoWRoot.AmbientColor[0] * 255),
                                  int(scene.WoWRoot.AmbientColor[3] * 255)]

        self.mohd.nMaterials = len(self.momt.Materials)
        self.mohd.nGroups = len(self.mogi.Infos)
        self.mohd.nPortals = len(self.mopt.Infos)
        self.mohd.nModels = self.modn.StringTable.decode("ascii").count('.MDX')
        self.mohd.nLights = len(self.molt.Lights)
        self.mohd.nDoodads = len(self.modd.Definitions)
        self.mohd.nSets = len(self.mods.Sets)

        flags = scene.WoWRoot.Flags
        if "0" in flags:
            self.mohd.Flags |= 0x01
        if "2" in flags:
            self.mohd.Flags |= 0x02
        if "1" in flags:
            self.mohd.Flags |= 0x08

        self.mohd.Flags |= 0x4

        print("Done saving root header")


class BlenderSceneObjects:

    def __init__(self):
        self.groups = []
        self.portals = []
        self.fogs = []
        self.lights = []
        self.liquids = []
        self.doodad_sets = []

    def find_nearest_object(object, objects):
        """Get closest object to another object"""

        dist = sys.float_info.max
        result = None
        for obj in objects:
            obj_location_relative = obj.matrix_world.inverted() * object.location
            hit = obj.closest_point_on_mesh(obj_location_relative)
            hit_dist = (obj_location_relative - hit[1]).length
            if hit_dist < dist:
                dist = hit_dist
                result = obj

        return result

    def build_references(self, export_selected):
        """ Build WMO references in Blender scene """

        start_time = time.time()

        empties = []

        for obj in bpy.context.scene.objects:
            if not obj.WoWDoodad.Enabled and not obj.type == 'EMPTY':
                if obj.hide or export_selected and not obj.select:
                    continue
                else:
                    bpy.context.scene.objects.active = obj
                    bpy.ops.object.mode_set(mode='OBJECT')

            obj.select = False

            if obj.type == 'MESH':

                if obj.WowWMOGroup.Enabled:
                    self.groups.append(obj)
                    obj.WowWMOGroup.GroupID = len(self.groups) - 1

                elif obj.WowPortalPlane.Enabled:
                    self.portals.append(obj)
                    obj.WowPortalPlane.PortalID = len(self.portals) - 1

                    group_objects = (obj.WowPortalPlane.First, obj.WowPortalPlane.Second)

                    for group_name in group_objects:
                        if group_name:
                            group_obj = None
                            try:
                                group_obj = bpy.context.scene.objects[group_name]
                            except KeyError:
                                print("\nWARNING: portal <<{}>> points to a non-existing object.".format(group_name))
                                continue
                            rel = group_obj.WowWMOGroup.Relations.Portals.add()
                            rel.id = obj.name

                elif obj.WowFog.Enabled:
                    self.fogs.append(obj)
                    obj.WowFog.FogID = len(self.fogs) - 1

                elif obj.WowLiquid.Enabled:
                    self.liquids.append(obj)
                    group = None
                    try:
                        group = bpy.context.scene.objects[obj.WowLiquid.WMOGroup]
                    except KeyError:
                        print("\nWARNING: liquid <<{}>> points to a non-existing object.".format(obj.WowLiquid.WMOGroup))
                        group.WowWMOGroup.Relations.Liquid = ""
                        continue
                    group.WowWMOGroup.Relations.Liquid = obj.name

            elif obj.type == 'LAMP' and obj.data.WowLight.Enabled:
                self.lights.append(obj)

            elif obj.type == 'EMPTY':
                empties.append(obj)

        print("\nDone building references. "
              "\nTotal building time: ",
              time.strftime("%M minutes %S seconds", time.gmtime(time.time() - start_time)))

        start_time = time.time()

        # sorting doodads into sets
        doodad_counter = 0
        for empty in empties:

            doodad_set = (empty.name, [])

            for doodad in empty.children:
                if doodad.WoWDoodad.Enabled:
                    group = BlenderSceneObjects.find_nearest_object(doodad, self.groups)

                    if group:
                        rel = group.WowWMOGroup.Relations.Doodads.add()
                        rel.id = doodad_counter
                        doodad_counter += 1

                        doodad_set[1].append(doodad)

            if doodad_set[1]:
                self.doodad_sets.append(doodad_set)

        # setting light references
        for index, light in enumerate(self.lights):
            group = BlenderSceneObjects.find_nearest_object(light, self.groups)
            if group:
                rel = group.WowWMOGroup.Relations.Lights.add()
                rel.id = index

        print("\nDone assigning doodads and lights to groups. "
              "\nTotal time: ",
              time.strftime("%M minutes %S seconds", time.gmtime(time.time() - start_time)))

    def clear_references(self):
        for group in self.groups:
            group.WowWMOGroup.Relations.Doodads.clear()
            group.WowWMOGroup.Relations.Lights.clear()
            group.WowWMOGroup.Relations.Portals.clear()
            group.WowWMOGroup.Relations.Lights.clear()
            group.WowWMOGroup.Relations.Liquid = ""
