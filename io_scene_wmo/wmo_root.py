
import bpy
import math
import mathutils
import operator
from . import wmo_format
from .wmo_format import *
from . import debug_utils
from .debug_utils import *
from .m2 import import_m2 as m2

import os

class WMO_root_file:
    def __init__(self):
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

        self.materialLookup = {}
        self.textureLookup = {}
        self.lightsLookup = {}
        self.PortalRCount = 0
        self.PortalR = []
        self.portalDirectionMap = {}
        self.groupMap = {}

    def Read(self, f):
        """ Read WoW WMO root file """
        self.mver.Read(f)
        self.mohd.Read(f)
        self.motx.Read(f)
        self.momt.Read(f)
        self.mogn.Read(f)
        self.mogi.Read(f)
        self.mosb.Read(f)
        self.mopv.Read(f)
        self.mopt.Read(f)
        self.mopr.Read(f)
        self.movv.Read(f)
        self.movb.Read(f)
        self.molt.Read(f)
        self.mods.Read(f)
        self.modn.Read(f)
        self.modd.Read(f)
        self.mfog.Read(f)
        
        if f.tell() != os.fstat(f.fileno()).st_size:
            self.mcvp.Read(f)
                
    def CompareMaterials(self, material):
        """ Compare two WoW material properties """  

        get_attributes = operator.attrgetter(
        'Shader', 'TerrainType', 'BlendingMode',
        'TwoSided', 'Darkened', 'NightGlow',
        'Texture1', 'Color1', 'Flags1',
        'Texture2', 'Color2', 'Texture3',
        'Color3', 'Flags3' )

        mat1 = get_attributes(material.WowMaterial)


        for material2, index in self.materialLookup.items():

            if mat1 == get_attributes(material2.WowMaterial):
                return index

            """
            if material.WowMaterial.Shader == material2.WowMaterial.Shader \
            and material.WowMaterial.TerrainType == material2.WowMaterial.TerrainType \
            and material.WowMaterial.BlendingMode == material2.WowMaterial.BlendingMode \
            and material.WowMaterial.TwoSided == material2.WowMaterial.TwoSided \
            and material.WowMaterial.Darkened == material2.WowMaterial.Darkened \
            and material.WowMaterial.NightGlow == material2.WowMaterial.NightGlow \
            and material.WowMaterial.Texture1 == material2.WowMaterial.Texture1 \
            and material.WowMaterial.Color1 == material.WowMaterial.Color1 \
            and material.WowMaterial.Flags1 == material2.WowMaterial.Flags1 \
            and material.WowMaterial.Texture2 == material2.WowMaterial.Texture2 \
            and material.WowMaterial.Color2 == material.WowMaterial.Color2 \
            and material.WowMaterial.Texture3 == material2.WowMaterial.Texture3 \
            and material.WowMaterial.Color3 == material.WowMaterial.Color3 \
            and material.WowMaterial.Flags3 == material2.WowMaterial.Flags3:
                return index
            """
            
        return None     


    # mat is a bpy.types.Material
    def AddMaterial(self, mat):
        """ Add material if not already added, then return index in root file """

        mat_index = self.CompareMaterials(mat)
        
        if mat_index != None:
            return mat_index 
        
        else:
            # else add it then return index
            if not mat.WowMaterial.Enabled:
                self.materialLookup[mat] = 0xFF
                return 0xFF
            else:
                self.materialLookup[mat] = len(self.momt.Materials)

                WowMat = WMO_Material()
                
                WowMat.Shader = int(mat.WowMaterial.Shader)
                WowMat.BlendMode = int(mat.WowMaterial.BlendingMode)
                WowMat.TerrainType = int(mat.WowMaterial.TerrainType)

                if mat.WowMaterial.Texture1 in self.textureLookup:
                    WowMat.Texture1Ofs = self.textureLookup[mat.WowMaterial.Texture1]
                else:
                    self.textureLookup[mat.WowMaterial.Texture1] = self.motx.AddString(mat.WowMaterial.Texture1)
                    WowMat.Texture1Ofs = self.textureLookup[mat.WowMaterial.Texture1]

                WowMat.Color1 = (mat.WowMaterial.Color1[0],
                                 mat.WowMaterial.Color1[1], 
                                 mat.WowMaterial.Color1[2], 
                                 1)

                WowMat.TextureFlags1 = 0

                if mat.WowMaterial.Texture2 in self.textureLookup:
                    WowMat.Texture2Ofs = self.textureLookup[mat.WowMaterial.Texture2]
                else:
                    self.textureLookup[mat.WowMaterial.Texture2] = self.motx.AddString(mat.WowMaterial.Texture2)
                    WowMat.Texture2Ofs = self.textureLookup[mat.WowMaterial.Texture2]

                WowMat.Color2 = (mat.WowMaterial.Color2[0], 
                                 mat.WowMaterial.Color2[1], 
                                 mat.WowMaterial.Color2[2], 
                                 1)

                if mat.WowMaterial.Texture3 in self.textureLookup:
                    WowMat.Texture3Ofs = self.textureLookup[mat.WowMaterial.Texture3]
                else:
                    self.textureLookup[mat.WowMaterial.Texture3] = self.motx.AddString(mat.WowMaterial.Texture3)
                    WowMat.Texture3Ofs = self.textureLookup[mat.WowMaterial.Texture3]

                WowMat.Color3 = (mat.WowMaterial.Color3[0], 
                                 mat.WowMaterial.Color3[1],
                                 mat.WowMaterial.Color3[2], 
                                 1)

                WowMat.DiffColor = (0, 0, 0)
                WowMat.RunTimeData = (0, 0)

                if mat.WowMaterial.TwoSided:
                    WowMat.Flags1 |= 0x4
                    
                if mat.WowMaterial.Darkened:
                    WowMat.Flags1 |= 0x8          
                
                if mat.WowMaterial.NightGlow:
                    WowMat.Flags1 |= 0x10
                    WowMat.Shader = 1

                self.momt.Materials.append(WowMat)

                return self.materialLookup[mat]

    def AddGroupInfo(self, flags, boundingBox, name, desc):
        """ Add group info, then return offset of name and desc in a tuple """
        group_info = GroupInfo()

        group_info.Flags = flags # 8
        group_info.BoundingBoxCorner1 = boundingBox[0].copy()
        group_info.BoundingBoxCorner2 = boundingBox[1].copy()
        group_info.NameOfs = self.mogn.AddString(name) #0xFFFFFFFF

        descOfs = self.mogn.AddString(desc)

        self.mogi.Infos.append(group_info)

        return (group_info.NameOfs, descOfs)

    def LoadMaterials(self, name, texturePath, file_format):
        """ Load materials from WoW WMO root file """
        self.materials = {}

        images = []
        imageNames = []

        # Add ghost material
        mat = bpy.data.materials.get("WowMaterial_ghost")
        if not mat:
            mat = bpy.data.materials.new("WowMaterial_ghost")
            mat.diffuse_color = (0.2, 0.5, 1.0)
            mat.diffuse_intensity = 1.0
            mat.alpha = 0.15
            mat.transparency_method = 'Z_TRANSPARENCY'
            mat.use_transparency = True

        self.materials[0xFF] = mat

        for i in range(len(self.momt.Materials)):
            material_name = name + "_Mat_" + str(i).zfill(2)

            mat = bpy.data.materials.new(material_name)
            self.materials[i] = mat

            mat.WowMaterial.Enabled = True
            mat.WowMaterial.Shader = str(self.momt.Materials[i].Shader)
            mat.WowMaterial.BlendingMode = str(self.momt.Materials[i].BlendMode)
            mat.WowMaterial.Texture1 = self.motx.GetString(self.momt.Materials[i].Texture1Ofs)
            mat.WowMaterial.Color1 = [x / 255 for x in self.momt.Materials[i].Color1[0:3]]
            mat.WowMaterial.Flags1 = '1' if self.momt.Materials[i].TextureFlags1 & 0x80 else '0'
            mat.WowMaterial.Texture2 = self.motx.GetString(self.momt.Materials[i].Texture2Ofs)
            mat.WowMaterial.Color2 = [x / 255 for x in self.momt.Materials[i].Color2[0:3]]
            mat.WowMaterial.TerrainType = str(self.momt.Materials[i].TerrainType)
            mat.WowMaterial.Texture3 = self.motx.GetString(self.momt.Materials[i].Texture3Ofs)
            mat.WowMaterial.Color3 = [x / 255 for x in self.momt.Materials[i].Color3[0:3]]
            mat.WowMaterial.Flags3 = '0' #1' if momt.Materials[i].TextureFlags1 & 0x80 else '0'

            if self.momt.Materials[i].Flags1 & 0x4:
                mat.WowMaterial.TwoSided = True
            if self.momt.Materials[i].Flags1 & 0x8:
                mat.WowMaterial.Darkened = True
            if self.momt.Materials[i].Flags1 & 0x10:
                mat.WowMaterial.NightGlow = True

            # set texture slot and load texture
            
            if mat.WowMaterial.Texture1:
                tex1_slot = mat.texture_slots.create(2)
                tex1_slot.uv_layer = "UVMap"
                tex1_slot.texture_coords = 'UV'

                tex1_name = material_name + "_Tex_01"
                tex1 = bpy.data.textures.new(tex1_name, 'IMAGE')
                tex1_slot.texture = tex1

                try:
                    tex1_img_filename = os.path.splitext( mat.WowMaterial.Texture1 )[0] + file_format

                    img1_loaded = False

                    # check if image already loaded
                    for iImg in range(len(images)):
                        if(imageNames[iImg] == tex1_img_filename):
                            tex1.image = images[iImg]
                            img1_loaded = True
                            break

                    # if image is not loaded, do it
                    if(img1_loaded == False):
                        tex1_img = bpy.data.images.load(texturePath + tex1_img_filename)
                        tex1.image = tex1_img
                        images.append(tex1_img)
                        imageNames.append(tex1_img_filename)

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
                    tex2_img_filename = os.path.splitext( mat.WowMaterial.Texture2 )[0] + file_format
                    
                    img2_loaded = False

                    # check if image already loaded
                    for iImg in range(len(images)):
                        if(imageNames[iImg] == tex2_img_filename):
                            tex2.image = images[iImg]
                            img2_loaded = True
                            break

                    # if image is not loaded, do it
                    if img2_loaded == False:
                        tex2_img = bpy.data.images.load(texturePath + tex2_img_filename)
                        tex2.image = tex2_img
                        images.append(tex2_img)
                        imageNames.append(tex2_img_filename)
                except:
                    pass

            # set texture slot and load texture
            if mat.WowMaterial.Texture3:
                tex3_slot = mat.texture_slots.create(0)
                tex3_slot.uv_layer = "UVMap"
                tex3_slot.texture_coords = 'UV'
                
                tex3_name = material_name + "_Tex_03"
                tex3 = bpy.data.textures.new(tex3_name, 'IMAGE')
                tex3_slot.texture = tex3

                try:
                    tex3_img_filename = os.path.splitext( mat.WowMaterial.Texture2 )[0] + file_format
                    
                    img3_loaded = False

                    # check if image already loaded
                    for iImg in range(len(images)):
                        if imageNames[iImg] == tex3_img_filename:
                            tex3.image = images[iImg]
                            img3_loaded = True
                            break

                    # if image is not loaded, do it
                    if img3_loaded == False:
                        tex3_img = bpy.data.images.load(texturePath + tex3_img_filename)
                        tex3.image = tex3_img
                        images.append(tex3_img)
                        imageNames.append(tex3_img_filename)
                except:
                    pass

    def LoadLights(self, name):
        """ Load WoW WMO MOLT lights """
        for i in range(len(self.molt.Lights)):
            light_name = name + "_Light_" + str(i).zfill(2)

            l = self.molt.Lights[i]
         
            if(l.LightType == 0): # omni
                l_type = 'POINT'
            elif(l.LightType == 1): # spot
                l_type = 'SPOT'
            elif(l.LightType == 2): # direct
                l_type = 'SUN'
            elif(l.LightType == 3): # ambient
                l_type = 'POINT'    # use point with no attenuation
            else:
                raise Exception("Light type unknown :" + str(l.LightType) + "(light nbr : " + str(i) + ")")

            light_name = name + "_Light_" + str(i).zfill(2)
            light = bpy.data.lamps.new(light_name, l_type)
            light.color = (l.Color[2] / 255, l.Color[1] / 255, l.Color[0] / 255)
            light.energy = l.Intensity

            if(l.LightType == 0 or l.LightType == 1):
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

            self.lightsLookup[i] = obj
            
    
    def LoadFogs(self, name):
        """ Load WoW WMO fog objects """
        self.fogs = []
        for i in range(len(self.mfog.Fogs)):
            
            f = self.mfog.Fogs[i]
            
            bpy.ops.mesh.primitive_uv_sphere_add()
            fog = bpy.context.scene.objects.active
            
            if not f.BigRadius:
                fog.hide = False
                
            fog.name = name + "_Fog_" + str(i).zfill(2)
            
            # applying real object transformation
            fog.location = f.Position
            bpy.ops.transform.resize( value=(f.BigRadius, f.BigRadius, f.BigRadius) ) # 0.5 is the default radius of sphere primitive in Blender
            
            bpy.ops.object.shade_smooth()
            fog.draw_type = 'SOLID'
            fog.show_transparent = True
            fog.show_name = True
            fog.color = (f.Color1[2] / 255, f.Color1[1] / 255, f.Color1[0] / 255, 0.0)
            
            
            mesh = fog.data
            
            material = bpy.data.materials.new(name = fog.name)
            
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

    def LoadDoodads(self, dir=None, game_data=None):
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

                for i in range(doodad_set.StartDoodad, doodad_set.StartDoodad + doodad_set.nDoodads):
                    doodad = self.modd.Definitions[i]
                    doodad_path = os.path.splitext(self.modn.GetString(doodad.NameOfs))[0] + ".m2"

                    nobj = None
                    obj = obj_map.get(doodad_path)

                    if not obj:
                        try:
                            obj = m2.M2ToBlenderMesh(dir, doodad_path, game_data)
                        except:
                            bpy.ops.mesh.primitive_cube_add()
                            obj = bpy.context.scene.objects.active
                            LogDebug(1, False, "Failed to import model: <<" + doodad_path + ">>. Placeholder is imported instead.")

                        obj.WoWDoodad.Enabled = True
                        obj.WoWDoodad.Path = doodad_path

                        obj_map[doodad_path] = obj
                        nobj = obj
                    else:
                        nobj = obj.copy()

                        nobj.WoWDoodad.Color = (doodad.Color[0] / 255,
                                               doodad.Color[1] / 255,
                                               doodad.Color[2] / 255,
                                               doodad.Color[3] / 255)

                        flags = []
                        bit = 1
                        while bit <= 0x8:
                            if doodad.Flags & bit:
                                flags.append(str(bit))
                            bit <<= 1

                        nobj.WoWDoodad.Flags = set(flags)

                        scene.objects.link(nobj)

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
                    nobj.lock_location = (True, True, True)
                    nobj.lock_rotation = (True, True, True)
                    nobj.lock_scale = (True, True, True)


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
                    path.String = self.modn.GetString(property_definition.NameOfs)
                    string_filter.append(property_definition.NameOfs) 

    def LoadPortals(self, name, root):
        """ Load WoW WMO portal planes """
        self.portals = []
        self.vert_count = 0
        for i in range(len(self.mopt.Infos)):
            portal_name = name + "_Portal_" + str(i).zfill(3)

            verts = []            
            face = []
            faces = []
            for j in range(self.mopt.Infos[i].nVertices):
                if(len(face) < 4):
                    verts.append(self.mopv.PortalVertices[self.vert_count])
                    face.append(j)
                self.vert_count+=1
            
            faces.append(face)
            
            mesh = bpy.data.meshes.new(portal_name)

            obj = bpy.data.objects.new(portal_name, mesh)  

            obj.WowPortalPlane.Enabled = True
            first_relationship = True
            
            for j in range(len(self.mopr.Relationships)):
                if self.mopr.Relationships[j].PortalIndex == i:
                    if first_relationship:
                        obj.WowPortalPlane.First = root.groupMap.get(self.mopr.Relationships[j].GroupIndex)
                        first_relationship = False
                    else:
                        obj.WowPortalPlane.Second = root.groupMap.get(self.mopr.Relationships[j].GroupIndex)
                        break


            mesh.from_pydata(verts,[],faces)
            bpy.context.scene.objects.link(obj)
            
    def LoadConvexVolumePlanes(self, name):
        """ Load WoW WMO convex volume planes used for trasport objects """
        self.convex_volume_planes = []
        
        faces = []
        counter = 0
        
        for plane in self.mcvp.convex_volume_planes:
            if plane[2] != 0:
                self.convex_volume_planes.append((1.0, 1.0, -(plane[0] + plane[1] + plane[3]) / plane[2]))
            else:
                self.convex_volume_planes.append((1.0, 1.0, -(plane[0] + plane[1] + plane[3]) / plane[2]))
                
                
            self.convex_volume_planes.append((1.0, -(plane[0] + plane[2] + plane[3]) / plane[1], 1.0))
            self.convex_volume_planes.append((-(plane[1] + plane[2] + plane[3]) / plane[0], 1.0, 1.0))
            
            for i in range(0, 3):
                faces.append(counter * 3 + i)
            counter += 1
            
        mesh = bpy.data.meshes.new('Convex_Volume_Plane')
        
        obj = bpy.data.objects.new('Convex_Volume_Plane', mesh)
        
        mesh.from_pydata(self.convex_volume_planes, [], faces)
        bpy.context.scene.objects.link(obj)

            
    def LoadProperties(self, name, filepath):
        """ Load global WoW WMO properties """
        bpy.context.scene.WoWRoot.AmbientColor = [float(self.mohd.AmbientColor[0] / 255),
                                                  float(self.mohd.AmbientColor[1] / 255),
                                                  float(self.mohd.AmbientColor[2]) / 255]

        bpy.context.scene.WoWRoot.AmbientAlpha = self.mohd.AmbientColor[3]
        bpy.context.scene.WoWRoot.SkyboxPath = self.mosb.Skybox
        bpy.context.scene.WoWRoot.LightenIndoor = bool(self.mohd.Flags & 0x8)
        bpy.context.scene.WoWRoot.UseAmbient = bool(self.mohd.Flags & 0x2)
        bpy.context.scene.WoWRoot.WMOid = self.mohd.ID
        bpy.context.scene.WoWRoot.TextureRelPath = filepath
        bpy.context.scene.WoWRoot.PortalDistanceAttenuation = bool(self.mohd.Flags & 0x1)

    def GetObjectBoundingBox(self, obj):
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

    def GetGlobalBoundingBox(self):
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

        return (corner1, corner2)

    def Save(self, export_doodads, autofill_textures, nPortals):
        """ Save WoW WMO root file for future export """        
        # set version header
        self.mver.Version = 17
        self.mopt = MOPT_chunk(nPortals)

        global_vertices_count = 0
        global_portal_count = 0
        global_object_count = 0
        global_fog_count = 0
        global_outdoor_object_count = 0

        source_doodads = True
        doodad_map = {}

        scn = bpy.context.scene
                    
        for o in scn.objects:
            o.select = False
        
        for ob in bpy.context.scene.objects:
            if ob.type == "LAMP":
                obj_light = ob.data
                if obj_light.WowLight.Enabled:
                    light = Light()
                    light.LightType = int(obj_light.WowLight.LightType)

                    if light.LightType == 0 or light.LightType == 1:
                        light.Unknown4 = obj_light.distance * 2

                    light.Type = obj_light.WowLight.Type
                    light.UseAttenuation = obj_light.WowLight.UseAttenuation
                    light.Padding = obj_light.WowLight.Padding

                    light.Color = (int(obj_light.WowLight.Color[2] * 255), 
                                   int(obj_light.WowLight.Color[1] * 255), 
                                   int(obj_light.WowLight.Color[0] * 255), 
                                   int(obj_light.WowLight.ColorAlpha * 255))

                    light.Position = ob.location
                    light.Intensity = obj_light.WowLight.Intensity
                    light.AttenuationStart = obj_light.WowLight.AttenuationStart
                    light.AttenuationEnd = obj_light.WowLight.AttenuationEnd                
                    self.molt.Lights.append(light)
                    
            if ob.type == "MESH":
                obj_mesh = ob.data
                
                if ob.WowWMOGroup.Enabled:
                    global_object_count += 1
                    if ob.WowWMOGroup.PlaceType == '8':
                        global_outdoor_object_count += 1
                    
                if ob.WowPortalPlane.Enabled:
                    Log(1, False, "Exporting portal: <<" + ob.name + ">>")
                    portal_info = PortalInfo()
                    portal_info.StartVertex = global_vertices_count
                    local_vertices_count = 0
                    v = []
                    ob.select = True
                    bpy.ops.object.transform_apply(location = True, rotation = True, scale = True)
                    ob.select = False
                    
                    for poly in obj_mesh.polygons:
                        for loop_index in poly.loop_indices:
                            vertex = obj_mesh.vertices[obj_mesh.loops[loop_index].vertex_index]
                            self.mopv.PortalVertices.append(vertex.co)
                            v.append(vertex.co)
                            local_vertices_count+=1
                    
                    v_A = v[0][1]*v[1][2]-v[1][1]*v[0][2]-v[0][1]*v[2][2]+v[2][1]*v[0][2]+v[1][1]*v[2][2]-v[2][1]*v[1][2]
                    v_B = -v[0][0]*v[1][2]+v[2][0]*v[1][2]+v[1][0]*v[0][2]-v[2][0]*v[0][2]-v[1][0]*v[2][2]+v[0][0]*v[2][2]
                    v_C = v[2][0]*v[0][1]-v[1][0]*v[0][1]-v[0][0]*v[2][1]+v[1][0]*v[2][1]-v[2][0]*v[1][1]+v[0][0]*v[1][1]
                    
                    v_D = -v[0][0]*v[1][1]*v[2][2] + v[0][0]*v[2][1]*v[1][2] + v[1][0]*v[0][1]*v[2][2] - v[1][0]*v[2][1]*v[0][2] \
                    - v[2][0]*v[0][1]*v[1][2] + v[2][0]*v[1][1]*v[0][2]

                    portal_info.Unknown = v_D / math.sqrt(v_A*v_A+v_B*v_B+v_C*v_C) # i'm sorry
                    
                    #norm_x = v_A / math.sqrt(v_A*v_A+v_B*v_B+v_C*v_C)
                    #norm_y = v_B / math.sqrt(v_A*v_A+v_B*v_B+v_C*v_C)
                    #morm_z = v_C / math.sqrt(v_A*v_A+v_B*v_B+v_C*v_C)
                    portal_info.nVertices = local_vertices_count
                    portal_info.Normal = obj_mesh.polygons[0].normal
                    #portal_info.Normal = (norm_x, norm_y, morm_z)
                    
                    global_vertices_count+=local_vertices_count
                    self.mopt.Infos[ob.WowPortalPlane.PortalID] = portal_info
                    
                    Log(0, False, "Done exporting portal: <<" + ob.name + ">>")
                    
                    
                if ob.WowFog.Enabled:
                    Log(1, False, "Exporting fog: <<" + ob.name + ">>")
                    fog = Fog()
                    
                    ob.select = True
                    bpy.ops.object.transform_apply(location = True, rotation = True, scale = True)
                    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
                    ob.select = False
                    
                    fog.BigRadius = ob.dimensions[2] / 2
                    fog.SmallRadius = fog.BigRadius * (ob.WowFog.InnerRadius / 100)

                    fog.Color1 = (int(ob.WowFog.Color1[2] * 255), 
                                  int(ob.WowFog.Color1[1] * 255), 
                                  int(ob.WowFog.Color1[0] * 255), 
                                  0xFF)

                    fog.Color2 = (int(ob.WowFog.Color2[2] * 255), 
                                  int(ob.WowFog.Color2[1] * 255), 
                                  int(ob.WowFog.Color2[0] * 255), 
                                  0xFF)

                    fog.EndDist = ob.WowFog.EndDist
                    fog.EndDist2 = ob.WowFog.EndDist2
                    fog.Position = ob.location
                    fog.StartFactor = ob.WowFog.StartFactor
                    fog.StarFactor2 = ob.WowFog.StartFactor2
                    
                    if ob.WowFog.IgnoreRadius:
                        fog.Flags |= 0x01
                    if ob.WowFog.Unknown:
                        fog.Flags |= 0x10
                        
                    global_fog_count += 1
                        
                    self.mfog.Fogs.append(fog)
                    
                    Log(0, False, "Done exporting fog: <<" + ob.name + ">>")

                if ob.WoWDoodad.Enabled:
                    source_doodads = False
                    if ob.parent and ob.parent.type == "EMPTY":
                        doodad_map.setdefault(ob.parent.name, []).append(ob)

                    
        if source_doodads and len(bpy.context.scene.WoWRoot.MODS_Sets):
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

            for property_definition in scene.WoWRoot.MODD_Definitions:
                doodad_definition = DoodadDefinition()
                doodad_definition.NameOfs = ofsMap.get(property_definition.NameOfs)
                doodad_definition.Flags = property_definition.Flags
                doodad_definition.Position = property_definition.Position

                doodad_definition.Rotation = [property_definition.Rotation[0],
                                              property_definition.Rotation[1],
                                              property_definition.Rotation[2],
                                              0.0]

                doodad_definition.Rotation[3] = property_definition.Tilt
                doodad_definition.Scale = property_definition.Scale

                doodad_definition.Color = [int(property_definition.Color[0]),
                                           int(property_definition.Color[1]),
                                           int(property_definition.Color[2]),
                                           0]

                doodad_definition.Color[3] = int(property_definition.ColorAlpha)

                self.modd.Definitions.append(doodad_definition)

        elif len(doodad_map):

            doodad_sets = {}
            doodad_paths = {}

            for set_name, doodads in doodad_map.items():
                Log(1, False, "Exporting doodadset: <<" + set_name + ">>")

                doodad_set = DoodadSet()
                doodad_set.Name = set_name
                doodad_set.StartDoodad = len(self.modd.Definitions)

                for doodad in doodads:
                    doodad_definition = DoodadDefinition()
          
                    path = os.path.splitext(doodad.WoWDoodad.Path)[0] + ".MDX"

                    doodad_definition.NameOfs = doodad_paths.get(path)
                    if not doodad_definition.NameOfs:
                        doodad_definition.NameOfs = self.modn.AddString(path)
                        doodad_paths[path] = doodad_definition.NameOfs

                    doodad_definition.Position = doodad.location

                    doodad_definition.Rotation = (doodad.rotation_quaternion[1],
                                                  doodad.rotation_quaternion[2],
                                                  doodad.rotation_quaternion[3],
                                                  doodad.rotation_quaternion[0])

                    doodad_definition.Scale = doodad.scale[0]

                    doodad_definition.Color = (int(doodad.WoWDoodad.Color[0] * 255),
                                               int(doodad.WoWDoodad.Color[1] * 255),
                                               int(doodad.WoWDoodad.Color[2] * 255),
                                               int(doodad.WoWDoodad.Color[3] * 255))

                    for flag in doodad.WoWDoodad.Flags:
                        doodad_definition.Flags |= int(flag)

                    self.modd.Definitions.append(doodad_definition)

                doodad_set.nDoodads = len(self.modd.Definitions) - doodad_set.StartDoodad
                
                if set_name == "Set_$DefaultGlobal":
                    self.mods.Sets.insert(0, doodad_set)
                else:
                    self.mods.Sets.append(doodad_set)

                Log(0, False, "Done exporting doodadset: <<" + set_name + ">>")

              
        if global_object_count > 512:
            LogError(2, 
                     "Your scene contains more objects that it is supported by WMO file format " 
                     + str(global_object_count) 
                     + ". The hardcoded maximum is 512 for one root WMO file. Dividing your scene to a few separate WMO models is recommended.")

        # setting up default fog with default blizzlike values.       
        if global_fog_count == 0:
            empty_fog = Fog() 
            empty_fog.Color1 = (0xFF, 0xFF, 0xFF, 0xFF)
            empty_fog.Color2 = (0x00, 0x00, 0x00, 0xFF)
            empty_fog.EndDist = 444.4445
            empty_fog.EndDist2 = 222.2222
            empty_fog.StartFactor = 0.25
            empty_fog.StartFactor2 = -0.5
            self.mfog.Fogs.append(empty_fog)
                    
        # set portal relations
        self.mopr.Relationships = []
        for i in range(len(self.PortalR)):
            group_id = self.PortalR[i][1]
            relation = PortalRelationship()
            relation.PortalIndex = self.PortalR[i][0]
            relation.GroupIndex = group_id
            relation.Side = self.PortalR[i][2]
            self.mopr.Relationships.append(relation)

        # set header
        bb = self.GetGlobalBoundingBox()

        self.mohd.nMaterials = len(self.momt.Materials)
        self.mohd.nGroups = len(self.mogi.Infos)
        self.mohd.nPortals = len(self.mopt.Infos)
        self.mohd.nModels = self.modn.StringTable.decode("ascii").count('.MDX')
        self.mohd.nLights = len(self.molt.Lights)
        self.mohd.nDoodads = len(self.modd.Definitions)
        self.mohd.nSets = len(self.mods.Sets)

        self.mohd.AmbientColor = [int(bpy.context.scene.WoWRoot.AmbientColor[0]*255),
                                  int(bpy.context.scene.WoWRoot.AmbientColor[1]*255),
                                  int(bpy.context.scene.WoWRoot.AmbientColor[2]*255),
                                  bpy.context.scene.WoWRoot.AmbientAlpha] 

        self.mohd.ID =  bpy.context.scene.WoWRoot.WMOid
        self.mohd.BoundingBoxCorner1 = bb[0]
        self.mohd.BoundingBoxCorner2 = bb[1]
        
        self.mosb.Skybox = bpy.context.scene.WoWRoot.SkyboxPath

        if bpy.context.scene.WoWRoot.PortalDistanceAttenuation:
            self.mohd.Flags |= 0x01
        if bpy.context.scene.WoWRoot.UseAmbient:
            self.mohd.Flags |= 0x02 
        if bpy.context.scene.WoWRoot.LightenIndoor:
            self.mohd.Flags |= 0x08

        return

    def Write(self, f):
        """ Write a saved WoW WMO root to a file """
        
        self.mver.Write(f)
        self.mohd.Write(f)
        self.motx.Write(f)
        self.momt.Write(f)
        self.mogn.Write(f)
        self.mogi.Write(f)
        self.mosb.Write(f)
        self.mopv.Write(f)
        self.mopt.Write(f)
        self.mopr.Write(f)
        self.movv.Write(f)
        self.movb.Write(f)
        self.molt.Write(f)
        self.mods.Write(f)
        self.modn.Write(f)
        self.modd.Write(f)
        self.mfog.Write(f)
        
        Log(1, False, "Done writing root file: <<" + os.path.basename(f.name) +">>")
        Log(1, False, "Exporting process finished successfully")

        return
