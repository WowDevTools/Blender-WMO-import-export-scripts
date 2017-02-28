
import bpy
import math
from . import wmo_format
from .wmo_format import *

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
        self.PortalRCount = 0 #Portal references count
        self.PortalR = []
        self.WMOId = 0
        self.liquidReferences = {}
        self.groupMap = {}

    def Read(self, f):
        self.mver.Read(f)
        self.mohd.Read(f)
        self.WMOId = self.mohd.ID
        print("WMO DBC Id: " + str(self.WMOId))
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
        
        self.SaveSource()
    
    #def LoadDoodads(self):
        #for i in range(self.mods):

    def LoadReferences(self, refType):
        if refType == "LIQUID":
            for ob in bpy.context.scene.objects:
                if (ob.type == "MESH") and (ob.WowLiquid.Enabled):
                    ob.WowLiquid.WMOGroup = self.liquidReferences.get(ob.name)


    # mat is a bpy.types.Material
    def AddMaterial(self, mat):
        """ Add material if not already added, then return index in root file """

        if mat in self.materialLookup:
            # if material already added, return index
            return self.materialLookup[mat]
        else:
            # else add it then return index
            if(not mat.WowMaterial.Enabled):
                self.materialLookup[mat] = 0xFF
                return 0xFF
            else:
                self.materialLookup[mat] = len(self.momt.Materials)

                WowMat = WMO_Material()
                WowMat.Flags1 = 0
                
                if(mat.WowMaterial.TwoSided):
                    WowMat.Flags1 = WowMat.Flags1 | 4
                    
                if(mat.WowMaterial.Darkened):
                    WowMat.Flags1 = WowMat.Flags1 | 8              
                
                WowMat.Shader = int(mat.WowMaterial.Shader)
                WowMat.BlendMode = int(mat.WowMaterial.BlendingMode)
                WowMat.TerrainType = int(mat.WowMaterial.TerrainType)

                if mat.WowMaterial.Texture1 in self.textureLookup:
                    WowMat.Texture1Ofs = self.textureLookup[mat.WowMaterial.Texture1]
                else:
                    self.textureLookup[mat.WowMaterial.Texture1] = self.motx.AddString(mat.WowMaterial.Texture1)
                    WowMat.Texture1Ofs = self.textureLookup[mat.WowMaterial.Texture1]

                WowMat.Color1 = (mat.WowMaterial.Color1[0], mat.WowMaterial.Color1[1], mat.WowMaterial.Color1[2], 1)
                WowMat.TextureFlags1 = 0

                if mat.WowMaterial.Texture2 in self.textureLookup:
                    WowMat.Texture2Ofs = self.textureLookup[mat.WowMaterial.Texture2]
                else:
                    self.textureLookup[mat.WowMaterial.Texture2] = self.motx.AddString(mat.WowMaterial.Texture2)
                    WowMat.Texture2Ofs = self.textureLookup[mat.WowMaterial.Texture2]

                WowMat.Color2 = (mat.WowMaterial.Color2[0], mat.WowMaterial.Color2[1], mat.WowMaterial.Color2[2], 1)

                if mat.WowMaterial.Texture3 in self.textureLookup:
                    WowMat.Texture3Ofs = self.textureLookup[mat.WowMaterial.Texture3]
                else:
                    self.textureLookup[mat.WowMaterial.Texture3] = self.motx.AddString(mat.WowMaterial.Texture3)
                    WowMat.Texture3Ofs = self.textureLookup[mat.WowMaterial.Texture3]

                WowMat.Color3 = (mat.WowMaterial.Color3[0], mat.WowMaterial.Color3[1], mat.WowMaterial.Color3[2], 1)

                WowMat.DiffColor = (0, 0, 0)
                WowMat.RunTimeData = (0, 0)
                
                if(mat.WowMaterial.NightGlow):
                    WowMat.Flags1 = WowMat.Flags1 | 16
                    WowMat.Shader = 1
                    #WowMat.Color1 = (255, 255, 255, 255)
                    #WowMat.TextureFlags2 = WowMat.TextureFlags2 | 10

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
        self.materials = {}

        images = []
        imageNames = []

        # Add ghost material
        mat = bpy.data.materials.get("WowMaterial_ghost")
        if(not mat):
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
            mat.WowMaterial.Flags3 = '0'#1' if momt.Materials[i].TextureFlags1 & 0x80 else '0'

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
                    if(img2_loaded == False):
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
                        if(imageNames[iImg] == tex3_img_filename):
                            tex3.image = images[iImg]
                            img3_loaded = True
                            break

                    # if image is not loaded, do it
                    if(img3_loaded == False):
                        tex3_img = bpy.data.images.load(texturePath + tex3_img_filename)
                        tex3.image = tex3_img
                        images.append(tex3_img)
                        imageNames.append(tex3_img_filename)
                except:
                    pass

    def LoadLights(self, name):
        self.lights = []
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
            
    
    def LoadFogs(self, name):
        self.fogs = []
        for i in range(len(self.mfog.Fogs)):
            
            f = self.mfog.Fogs[i]
            
            bpy.ops.mesh.primitive_uv_sphere_add()
            fog = bpy.context.scene.objects.active
            
            if(i == 0 and f.Color1 == (0xFF, 0xFF, 0xFF, 0xFF) and  f.Color2 == (0x00, 0x00, 0x00, 0xFF) and f.EndDist == 444.4445 and \
            f.EndDist2 == 222.2222 and f.StartFactor == 0.25 and f.StartFactor2 == -0.5): # Checking if the fog is default
                fog.hide = True
                
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
            if(f.Flags & 0x01):
                fog.WowFog.IgnoreRadius = True
            if(f.Flags & 0x10):
                fog.WowFog.Unknown = True
            
            if(f.SmallRadius != 0):     
                fog.WowFog.InnerRadius = round(f.BigRadius / f.SmallRadius * 100, 2)
            else:
                fog.WowFog.InnerRadius = 0
            
            fog.WowFog.EndDist = f.EndDist
            fog.WowFog.StartFactor = f.StartFactor
            fog.WowFog.Color1 = (f.Color1[2] / 255, f.Color1[1] / 255, f.Color1[0] / 255)
            fog.WowFog.EndDist2 = f.EndDist2
            fog.WowFog.StartFactor2 = f.StartFactor2
            fog.WowFog.Color2 = (f.Color2[2] / 255, f.Color2[1] / 255, f.Color2[0] / 255)
        
            

    def SaveSource(self):
        name = "(TECH)Root_source"
        mesh = bpy.data.meshes.new(name)
        mesh.WowWMORoot.IsRoot = True
        mesh.WowWMORoot.MODS.Sets = self.mods.Sets
        #print(mesh.WowWMORoot.MODS.Sets[0].Name)
        mesh.WowWMORoot.MODN.StringTable = self.modn.StringTable
        mesh.WowWMORoot.MODD.Definitions = self.modd.Definitions
        mesh.WowWMORoot.MFOG.Fogs = self.mfog.Fogs
        obj = bpy.data.objects.new(name, mesh)
    
    def LoadPortals(self, name, root):
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
                if(self.mopr.Relationships[j].PortalIndex == i):
                    if(first_relationship):
                        obj.WowPortalPlane.First = root.groupMap.get(self.mopr.Relationships[j].GroupIndex)
                        first_relationship = False
                    else:
                        obj.WowPortalPlane.Second = root.groupMap.get(self.mopr.Relationships[j].GroupIndex)
                        break


            mesh.from_pydata(verts,[],faces)
            bpy.context.scene.objects.link(obj)
            
    def LoadConvexVolumePlanes(self, name):
        self.convex_volume_planes = []
        
        faces = []
        counter = 0
        
        for plane in self.mcvp.convex_volume_planes:
            if plane[2] != 0:
                self.convex_volume_planes.append( (1.0, 1.0, -(plane[0] + plane[1] + plane[3]) / plane[2]) )
            else:
                self.convex_volume_planes.append( (1.0, 1.0, -(plane[0] + plane[1] + plane[3]) / plane[2]) )
                
                
            self.convex_volume_planes.append( (1.0, -(plane[0] + plane[2] + plane[3]) / plane[1], 1.0) )
            self.convex_volume_planes.append( (-(plane[1] + plane[2] + plane[3]) / plane[0], 1.0, 1.0) )
            
            for i in range(0, 3):
                faces.append(counter * 3 + i)
            counter += 1
            
        mesh = bpy.data.meshes.new('Convex_Volume_Plane')
        
        obj = bpy.data.objects.new('Convex_Volume_Plane', mesh)
        
        mesh.from_pydata(self.convex_volume_planes, [], faces)
        bpy.context.scene.objects.link(obj)

            
    def LoadProperties(self, name, filepath):
        bpy.context.scene.WoWRoot.AmbientColor = [float(self.mohd.AmbientColor[0] / 255), float(self.mohd.AmbientColor[1] / 255), float(self.mohd.AmbientColor[2]) / 255]
        bpy.context.scene.WoWRoot.AmbientAlpha = self.mohd.AmbientColor[3]
        bpy.context.scene.WoWRoot.SkyboxPath =  self.mosb.Skybox
        bpy.context.scene.WoWRoot.UseAmbient = bool(self.mohd.Flags & 2)
        bpy.context.scene.WoWRoot.WMOid = self.mohd.ID
        bpy.context.scene.WoWRoot.TextureRelPath = filepath

    def GetObjectBoundingBox(self, obj):
        corner1 = [0, 0, 0]
        corner2 = [0, 0, 0]
        
        for v in obj.bound_box:
            if(v[0] < corner1[0]):
                corner1[0] = v[0]
            if(v[1] < corner1[1]):
                corner1[1] = v[1]
            if(v[2] < corner1[2]):
                corner1[2] = v[2]
                
            if(v[0] > corner2[0]):
                corner2[0] = v[0]
            if(v[1] > corner2[1]):
                corner2[1] = v[1]
            if(v[2] > corner2[2]):
                corner2[2] = v[2]

        return (corner1, corner2)

    def GetGlobalBoundingBox(self):
        corner1 = self.mogi.Infos[0].BoundingBoxCorner1
        corner2 = self.mogi.Infos[0].BoundingBoxCorner2
        
        for gi in self.mogi.Infos:
            v = gi.BoundingBoxCorner1
            if(v[0] < corner1[0]):
                corner1[0] = v[0]
            if(v[1] < corner1[1]):
                corner1[1] = v[1]
            if(v[2] < corner1[2]):
                corner1[2] = v[2]
                
            v = gi.BoundingBoxCorner2                
            if(v[0] > corner2[0]):
                corner2[0] = v[0]
            if(v[1] > corner2[1]):
                corner2[1] = v[1]
            if(v[2] > corner2[2]):
                corner2[2] = v[2]

        return (corner1, corner2)

    def Save(self, f, fill_water, source_doodads, autofill_textures, mohd_0x1, wmo_groups, nPortals):
    
        mver = MVER_chunk()                
        # set version header
        self.mver.Version = 17
        self.mver.Write(f)
        
        mohd = MOHD_chunk()
        motx = MOTX_chunk()
        momt = MOMT_chunk()
        mogn = MOGN_chunk()
        mogi = MOGI_chunk()
        mosb = MOSB_chunk()
        movv = MOVV_chunk()
        movb = MOVB_chunk()
        mods = MODS_chunk()
        modn = MODN_chunk()
        modd = MODD_chunk()
        mfog = MFOG_chunk()
        
        molt = MOLT_chunk()
        mopv = MOPV_chunk()
        mopt = MOPT_chunk(nPortals)

        global_vertices_count = 0
        global_portal_count = 0
        global_object_count = 0
        global_fog_count = 0
        global_outdoor_object_count = 0
        
        for ob in bpy.context.scene.objects:
            if(ob.type == "LAMP"):
                obj_light = ob.data
                if(obj_light.WowLight.Enabled):
                    light = Light()
                    light.LightType = int(obj_light.WowLight.LightType)
                    if(light.LightType == 0 or light.LightType == 1):
                        light.Unknown4 = obj_light.distance * 2
                    light.Type = obj_light.WowLight.Type
                    light.UseAttenuation = obj_light.WowLight.UseAttenuation
                    light.Padding = obj_light.WowLight.Padding
                    light.Color = (int(obj_light.WowLight.Color[2] * 255), int(obj_light.WowLight.Color[1] * 255), int(obj_light.WowLight.Color[0] * 255), int(obj_light.WowLight.ColorAlpha * 255))
                    light.Position = ob.location
                    light.Intensity = obj_light.WowLight.Intensity
                    light.AttenuationStart = obj_light.WowLight.AttenuationStart
                    light.AttenuationEnd = obj_light.WowLight.AttenuationEnd                
                    molt.Lights.append(light)
                    
            if(ob.type == "MESH"):
                obj_mesh = ob.data
                
                if(ob.WowWMOGroup.Enabled):
                    global_object_count += 1
                    if ob.WowWMOGroup.PlaceType == '8':
                        global_outdoor_object_count += 1
                    
                if(ob.WowPortalPlane.Enabled):
                    print("Exporting portal "+ob.name)
                    portal_info = PortalInfo()
                    portal_info.StartVertex = global_vertices_count
                    local_vertices_count = 0
                    v = []
                    ob.select = True
                    bpy.ops.object.transform_apply(location = True, rotation = True, scale = True)
                    ob.select = False
                    
                    for vert in obj_mesh.vertices:
                        mopv.PortalVertices.append(vert.co)
                        v.append(vert.co)
                        local_vertices_count+=1
                    
                    v_A = v[0][1]*v[1][2]-v[1][1]*v[0][2]-v[0][1]*v[2][2]+v[2][1]*v[0][2]+v[1][1]*v[2][2]-v[2][1]*v[1][2]
                    v_B = -v[0][0]*v[1][2]+v[2][0]*v[1][2]+v[1][0]*v[0][2]-v[2][0]*v[0][2]-v[1][0]*v[2][2]+v[0][0]*v[2][2]
                    v_C = v[2][0]*v[0][1]-v[1][0]*v[0][1]-v[0][0]*v[2][1]+v[1][0]*v[2][1]-v[2][0]*v[1][1]+v[0][0]*v[1][1]
                    
                    v_D = -v[0][0]*v[1][1]*v[2][2] + v[0][0]*v[2][1]*v[1][2] + v[1][0]*v[0][1]*v[2][2] - v[1][0]*v[2][1]*v[0][2] - v[2][0]*v[0][1]*v[1][2] + v[2][0]*v[1][1]*v[0][2]
                    portal_info.Unknown = v_D / math.sqrt(v_A*v_A+v_B*v_B+v_C*v_C) # i'm sorry
                    
                    #norm_x = v_A / math.sqrt(v_A*v_A+v_B*v_B+v_C*v_C)
                    #norm_y = v_B / math.sqrt(v_A*v_A+v_B*v_B+v_C*v_C)
                    #morm_z = v_C / math.sqrt(v_A*v_A+v_B*v_B+v_C*v_C)
                    portal_info.nVertices = local_vertices_count
                    portal_info.Normal = obj_mesh.polygons[0].normal
                    #portal_info.Normal = (norm_x, norm_y, morm_z)
                    
                    global_vertices_count+=local_vertices_count
                    mopt.Infos[ob.WowPortalPlane.PortalID] = portal_info
                    
                    
                if(ob.WowFog.Enabled):
                    print("Exporting fog "+ob.name)
                    fog = Fog()
                    
                    ob.select = True
                    bpy.ops.object.transform_apply(location = True, rotation = True, scale = True)
                    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
                    ob.select = False
                    
                    fog.BigRadius = ob.dimensions[2]
                    print(fog.BigRadius)
                    fog.SmallRadius = fog.BigRadius * (ob.WowFog.InnerRadius / 100)
                    fog.Color1 = (int(ob.WowFog.Color1[2] * 255), int(ob.WowFog.Color1[1] * 255), int(ob.WowFog.Color1[0] * 255), 0xFF)
                    fog.Color2 = (int(ob.WowFog.Color2[2] * 255), int(ob.WowFog.Color2[1] * 255), int(ob.WowFog.Color2[0] * 255), 0xFF)
                    fog.EndDist = ob.WowFog.EndDist
                    fog.EndDist2 = ob.WowFog.EndDist2
                    fog.Position = ob.location
                    fog.StartFactor = ob.WowFog.StartFactor
                    fog.StarFactor2 = ob.WowFog.StartFactor2
                    
                    if(ob.WowFog.IgnoreRadius):
                        fog.Flags |= 0x01
                    if(ob.WowFog.Unknown):
                        fog.Flags |= 0x10
                        
                    global_fog_count += 1
                        
                    mfog.Fogs.append(fog)
                    
                elif(obj_mesh.WowWMORoot.IsRoot):
                    if(source_doodads):
                        mods.Sets = obj_mesh.WowWMORoot.MODS.Sets
                        modn.StringTable = obj_mesh.WowWMORoot.MODN.StringTable
                        modd.Definitions = obj_mesh.WowWMORoot.MODD.Definitions
                        
        if(global_object_count > 512):
            raise Exception("Your scene contains more objects that it is supported by WMO file format " + str(global_object_count) + ". The hardcoded maximum is 512 for one root WMO file. Dividing your scene to a few separate WMO models is recommended.")
        
        if(global_fog_count == 0):
        
            empty_fog = Fog() # setting up default fog with default blizzlike values.
            empty_fog.Color1 = (0xFF, 0xFF, 0xFF, 0xFF)
            empty_fog.Color2 = (0x00, 0x00, 0x00, 0xFF)
            empty_fog.EndDist = 444.4445
            empty_fog.EndDist2 = 222.2222
            empty_fog.StartFactor = 0.25
            empty_fog.StartFactor2 = -0.5
            mfog.Fogs.append(empty_fog)
                    
        mopr = MOPR_chunk()
        mopr.Relationships = []
        # set portal relationship
        for i in range(len(self.PortalR)):
            relation = PortalRelationship()
            relation.PortalIndex = self.PortalR[i][0]
            relation.GroupIndex = wmo_groups.get(self.PortalR[i][1]).index
            relation.Side = self.PortalR[i][2]
            mopr.Relationships.append(relation)

        # set header
        bb = self.GetGlobalBoundingBox()

        self.mohd.nMaterials = len(self.momt.Materials)
        self.mohd.nGroups = len(self.mogi.Infos)
        self.mohd.nPortals = len(mopt.Infos)
        self.mohd.nLights = len(molt.Lights)
        self.mohd.nModels = modn.StringTable.decode("ascii").count('.MDX')
        self.mohd.nDoodads = len(modd.Definitions)
        self.mohd.nSets = len(mods.Sets)
        self.mohd.AmbientColor = [int(bpy.context.scene.WoWRoot.AmbientColor[2]*255), int(bpy.context.scene.WoWRoot.AmbientColor[1]*255), int(bpy.context.scene.WoWRoot.AmbientColor[0]*255), bpy.context.scene.WoWRoot.AmbientAlpha] 
        self.mohd.ID =  bpy.context.scene.WoWRoot.WMOid
        self.mohd.BoundingBoxCorner1 = bb[0]
        self.mohd.BoundingBoxCorner2 = bb[1]
        self.mohd.Flags = 0
        
        mosb.Skybox = bpy.context.scene.WoWRoot.SkyboxPath

        if mohd_0x1:
            self.mohd.Flags |= 0x01
        if bpy.context.scene.WoWRoot.UseAmbient:
            self.mohd.Flags |= 0x02
        if fill_water:
            self.mohd.Flags |= 0x04
        
#        if global_outdoor_object_count: -- makes mesh overbrightaa
#            self.mohd.Flags |= 0x08


        # write all chunks
        self.mohd.Write(f)
        self.motx.Write(f)
        self.momt.Write(f)
        self.mogn.Write(f)
        self.mogi.Write(f)
        mosb.Write(f)
        mopv.Write(f)
        mopt.Write(f)
        mopr.Write(f)
        self.movv.Write(f)
        self.movb.Write(f)
        molt.Write(f)
        mods.Write(f)
        modn.Write(f)
        modd.Write(f)
        mfog.Write(f)

        return
