
from . import wmo_format
from .wmo_format import *

from . import BSP_Tree
from .BSP_Tree import *

from . import Collision
from .Collision import *

import math
from math import *

import os
import sys

#from . import Utility
#from .Utility import *

def GetAvg(list):
    normal = [0, 0, 0]
    
    for n in list:
        for i in range(0, 3):
            normal[i] += n[i]
    
    for i in range(0, 3):
        normal[i] /= len(list)
        
    return normal
    

def ret_min(a, b):
    return a if a < b else b

def ret_max(a, b):
    return a if a > b else b

class WMO_group_file:
    def __init__(self):
        pass
        

    def Read(self, f):
        self.filename = f.name

        # read version header
        self.mver = MVER_chunk()
        self.mver.Read(f)

        # read file header
        self.mogp = MOGP_chunk()
        self.mogp.Read(f)
    
        # read materials
        self.mopy = MOPY_chunk()
        self.mopy.Read(f)

        # read indices
        self.movi = MOVI_chunk()
        self.movi.Read(f)

        # read vertices
        self.movt = MOVT_chunk()
        self.movt.Read(f)

        # read normals
        self.monr = MONR_chunk()
        self.monr.Read(f)

        # read texcoords
        self.motv = MOTV_chunk()
        self.motv.Read(f)

        # read batches
        self.moba = MOBA_chunk()
        self.moba.Read(f)
    
        # read lights
        if(self.mogp.Flags & MOGP_FLAG.HasLight):
            self.molr = MOLR_chunk()
            self.molr.Read(f)
    
        # read doodads
        if(self.mogp.Flags & MOGP_FLAG.HasDoodads):
            self.modr = MODR_chunk()
            self.modr.Read(f)
    
        # read collision faces
        if(self.mogp.Flags & MOGP_FLAG.HasCollision):
            self.mobn = MOBN_chunk()
            self.mobn.Read(f)
            self.mobr = MOBR_chunk()
            self.mobr.Read(f)
    
        # read vertex colors
        if(self.mogp.Flags & MOGP_FLAG.HasVertexColor):
            self.mocv = MOCV_chunk()
            self.mocv.Read(f)

        # read liquids
        if(self.mogp.Flags & MOGP_FLAG.HasWater):
            if self.mogp.LiquidType == 3:
                self.mliq = MLIQ_chunk(False)
            else:
                self.mliq = MLIQ_chunk()
            self.mliq.Read(f)
            
    def CreateMeshFromBatch(self, meshName, batch, materials):
        # create mesh vertices / faces
        vertices = self.movt.Vertices[batch.StartVertex : batch.LastVertex + 1]
        indices = []
        
        # triangles are indices actually trueNTriangle = nTriangle // 3
        for i in range(batch.StartTriangle, batch.StartTriangle + batch.nTriangle):
            indices.append(self.movi.Indices[i] - batch.StartVertex)
          
        faces = []
        for i in range(0, len(indices), 3):
            faces.append(indices[i : i + 3])

        mesh = bpy.data.meshes.new(meshName)
        mesh.from_pydata(vertices, [], faces)
        
        # set vertex normals
        for i in range(len(mesh.vertices)):
            mesh.vertices[i].normal = self.monr.Normals[i + batch.StartVertex]
            
        # set vertex color
        if(self.mogp.Flags & MOGP_FLAG.HasVertexColor):
            vertColor_layer1 = mesh.vertex_colors.new("vertCol_layer1")
            for i in range(len(mesh.loops)):
                vertColor_layer1.data[i].color = self.mocv.vertColors[mesh.loops[i].vertex_index + batch.StartVertex][:4]
                
        # set uv
        uv1 = mesh.uv_textures.new("UVMap")
        uv_layer1 = mesh.uv_layers[0]
        for i in range(len(uv_layer1.data)):
            uv = self.motv.TexCoords[mesh.loops[i].vertex_index + batch.StartVertex]
            uv_layer1.data[i].uv = (uv[0], 1 - uv[1])
            
        # set material
        mesh.materials.append(materials[batch.MaterialID])

        # set displayed texture
        uv1.active = True

        return mesh

    def GetMaterialViewportImage(self, material):
        for i in range(3):
            try:
                img = material.texture_slots[3 - i].texture.image
                return img
            except:
                pass
        return None
    
    def ToWMOLiquid(self, basic_liquid_type):
        real_liquid_type = 0
        if basic_liquid_type == 0:
            real_liquid_type = 14 if self.mogp.Flags & 0x80000 else 13
        elif basic_liquid_type == 1:
            real_liquid_type = 14
        elif basic_liquid_type == 2:
            real_liquid_type = 19
        elif basic_liquid_type == 3:
            real_liquid_type = 20
            
        return real_liquid_type

    def FromWMOLiquid(self, real_liquid_type):
        basic_liquid_type = real_liquid_type
        if real_liquid_type == 13:
            basic_liquid_type = 1
        if real_liquid_type == 14:
            basic_liquid_type = 2
        if real_liquid_type == 17:
            basic_liquid_type = 15
        if real_liquid_type == 19:
            basic_liquid_type = 3
        if real_liquid_type == 20:
            basic_liquid_type = 4

        return basic_liquid_type
                
    # return array of vertice and array of faces in a tuple
    def LoadLiquids(self, objName, pos, mohd_flags):
        
        # load vertices
        vertices = []
        for y in range(0, self.mliq.yVerts):
            y_pos = self.mliq.Position[1] + y * 4.1666625
            for x in range(0 , self.mliq.xVerts):
                x_pos = self.mliq.Position[0] + x * 4.1666625
                vertices.append((x_pos, y_pos, self.mliq.VertexMap[y * self.mliq.xVerts + x].height[0] + self.mliq.Position[2]))
                # print(x_pos, y_pos, self.mliq.VertexMap[y * self.mliq.xVerts + x].height[0] + self.mliq.Position[2])
                # second float seems to be VERY low (e.g -3.271161e+35), or NAN or whatever when vertice is shown (or maybe it indicate a volume?)
                #vertices.append((x_pos, y_pos, self.mliq.HeightMap[y * self.mliq.xVerts + x][1] + self.mliq.Position[2]))
        # calculate faces
        
        indices = []
        for y in range(self.mliq.yTiles):
            for x in range(self.mliq.xTiles):
                indices.append(y * self.mliq.xVerts + x)
                indices.append(y * self.mliq.xVerts + x + 1)
                indices.append((y + 1) * self.mliq.xVerts + x)
                indices.append((y + 1) * self.mliq.xVerts + x + 1)
                
        faces = []
        
        for i in range(0, len(indices), 4):
            faces.append((indices[i], indices[i + 1], indices[i + 3], indices[i + 2]))  

        #create mesh and object
        name = objName + "_Liquid"
        mesh = bpy.data.meshes.new(name)
        object = bpy.data.objects.new(name, mesh)
                    
        #create mesh from python data
        mesh.from_pydata(vertices,[],faces)
        mesh.update(calc_edges=True)
        mesh.validate()

        #create uv map if liquid is lava
        
        if self.mogp.LiquidType == 3:
            uvMap = {}

            for vertex in mesh.vertices:
                uvMap[vertex.index] = (self.mliq.VertexMap[vertex.index].u, self.mliq.VertexMap[vertex.index].v)

            uv1 = mesh.uv_textures.new("UVMap")
            uv_layer1 = mesh.uv_layers[0]

            for poly in mesh.polygons:
                for loop_index in poly.loop_indices:
                        uv_layer1.data[loop_index].uv = (uvMap.get(mesh.loops[loop_index].vertex_index)[0], 1 - uvMap.get(mesh.loops[loop_index].vertex_index)[1])
            

        flag_0x1 = mesh.vertex_colors.new("flag_0x1")
        flag_0x2 = mesh.vertex_colors.new("flag_0x2")
        flag_0x4 = mesh.vertex_colors.new("flag_0x4")
        flag_0x8 = mesh.vertex_colors.new("flag_0x8")
        flag_0x10 = mesh.vertex_colors.new("flag_0x10")
        flag_0x20 = mesh.vertex_colors.new("flag_0x20")
        flag_0x40 = mesh.vertex_colors.new("flag_0x40")
        flag_0x80 = mesh.vertex_colors.new("flag_0x80")
        
        for face in mesh.polygons:
            for loop in face.loop_indices:
                if(self.mliq.TileFlags[face.index] & 0x1):
                    flag_0x1.data[loop].color = (0, 0, 255)
                if(self.mliq.TileFlags[face.index] & 0x2):
                    flag_0x2.data[loop].color = (0, 0, 255)           
                if(self.mliq.TileFlags[face.index] & 0x4):
                    flag_0x4.data[loop].color = (0, 0, 255)
                if(self.mliq.TileFlags[face.index] & 0x8):
                    flag_0x8.data[loop].color = (0, 0, 255) 
                if(self.mliq.TileFlags[face.index] & 0x10):
                    flag_0x10.data[loop].color = (0, 0, 255)
                if(self.mliq.TileFlags[face.index] & 0x20):
                    flag_0x20.data[loop].color = (0, 0, 255)           
                if(self.mliq.TileFlags[face.index] & 0x20):
                    flag_0x40.data[loop].color = (0, 0, 255)
                if(self.mliq.TileFlags[face.index] & 0x80):
                    flag_0x80.data[loop].color = (0, 0, 255)
                    
        #set mesh location
        object.location = pos
        bpy.context.scene.objects.link(object)
        
        bpy.context.scene.objects.active = object
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=True)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        object.lock_scale = [True, True, True]
        object.lock_rotation[2] = True
        
        object.WowLiquid.Enabled = True
        
        # getting Liquid Type ID
        
        basic_liquid_type = self.mogp.LiquidType
        real_liquid_type = 0
        
        if(mohd_flags & 0x4): # defining real liquid type ID from DBC. to understand what is being done here see wiki (MLIQ)
                
            if basic_liquid_type < 21: 
                real_liquid_type = self.ToWMOLiquid(basic_liquid_type - 1)
            else:
                real_liquid_type = basic_liquid_type
        else:

            if(basic_liquid_type == 15):
                real_liquid_type = 17
            else:
                if(basic_liquid_type < 20):
                    real_liquid_type = self.ToWMOLiquid(basic_liquid_type)
                else:
                    real_liquid_type = basic_liquid_type + 1

        
        object.WowLiquid.LiquidType = str(real_liquid_type)

               
    
    # Return faces indices
    def GetBSPNodeIndices(self, iNode, nodes, faces, indices):
        # last node in branch
        nodeIndices = []
        if(nodes[iNode].PlaneType & BSP_PLANE_TYPE.Leaf):
            for i in range(nodes[iNode].FirstFace, nodes[iNode].FirstFace + nodes[iNode].NumFaces):
                nodeIndices.append(faces[i])

        if(nodes[iNode].Childrens[0] != -1):
            nodeIndices.extend(self.GetBSPNodeIndices(nodes[iNode].Childrens[0], nodes, faces, indices))

        if(nodes[iNode].Childrens[1] != -1):
            nodeIndices.extend(self.GetBSPNodeIndices(nodes[iNode].Childrens[1], nodes, faces, indices))

        return nodeIndices

    def GetCollisionIndices(self):
        nodeIndices = self.GetBSPNodeIndices(0, self.mobn.Nodes, self.mobr.Faces, self.movi.Indices)
        indices = []
        for i in nodeIndices:
            if(not (self.mopy.TriangleMaterials[i].Flags & 0x04)):
                indices.append(self.movi.Indices[i * 3])
                indices.append(self.movi.Indices[i * 3 + 1])
                indices.append(self.movi.Indices[i * 3 + 2])

        return indices

    # Create mesh from file data
    def LoadObject(self, objName, materials, doodads, mogn, objId, base_name, mohd):

        vertices = []
        normals = []
        faces = []

        texCoords = []
        vertColors = []
        
        vertices = self.movt.Vertices
        normals = self.monr.Normals
        texCoords = self.motv.TexCoords


        #for i in range(0, len(self.mobr.Faces)):
        #    faces.append((self.movi.Indices[self.mobr.Faces[i] * 3], self.movi.Indices[self.mobr.Faces[i] * 3 + 1], self.movi.Indices[self.mobr.Faces[i] * 3 + 2]))

        for i in range(0, len(self.movi.Indices), 3):
            faces.append(self.movi.Indices[i:i+3])
            
        """for i in range(len(self.moba.Batches)):

            batch = self.moba.Batches[i]

            # add vertices BAAAAAD 
            startVert = len(vertices)
            vertices.extend(self.movt.Vertices[batch.StartVertex : batch.LastVertex + 1])
            
            # add faces
            for iFace in range(batch.StartTriangle, batch.StartTriangle + batch.nTriangle, 3):
                faces.append((self.movi.Indices[iFace] - batch.StartVertex + startVert, \
                    self.movi.Indices[iFace + 1] - batch.StartVertex + startVert, \
                    self.movi.Indices[iFace + 2] - batch.StartVertex + startVert))

            # add vertex normals
            normals.extend(self.monr.Normals[batch.StartVertex : batch.LastVertex + 1])

            
            # add vertex color
            if(self.mogp.Flags & MOGP_FLAG.HasVertexColor):
                vertColors.extend(self.mocv.vertColors[batch.StartVertex : batch.LastVertex + 1])

            # add uv coords
            texCoords.extend(self.motv.TexCoords[batch.StartVertex : batch.LastVertex + 1])

            # add material
            objMats.append(materials[batch.MaterialID])

        
        geometryVerticesCount = len(vertices)

        # load liquids
        if(self.mogp.Flags & MOGP_FLAG.HasWater):
            liquids_data = self.LoadLiquids()
            liquidVerticesCount = len(liquids_data[0])

            startVert = len(vertices)
            vertices.extend(liquids_data[0])

            for i in range(0, len(liquids_data[1]), 3):
                faces.append((liquids_data[1][i] + startVert, liquids_data[1][i + 1] + startVert, liquids_data[1][i + 2] + startVert))"""

        # create mesh
        mesh = bpy.data.meshes.new(objName)
        mesh.from_pydata(vertices, [], faces)

        # set normals
        for i in range(len(normals)):
            mesh.vertices[i].normal = normals[i]
            
        # set vertex color
        if(self.mogp.Flags & MOGP_FLAG.HasVertexColor):
            vertColor_layer1 = mesh.vertex_colors.new("Col")
            # loops and vertex_color are in the same order, so we use it to find vertex index
            for i in range(len(mesh.loops)):
                #if(mesh.loops[i].vertex_index < geometryVerticesCount):
                vertColor_layer1.data[i].color = (self.mocv.vertColors[mesh.loops[i].vertex_index][2] / 255, \
                        self.mocv.vertColors[mesh.loops[i].vertex_index][1] / 255, \
                        self.mocv.vertColors[mesh.loops[i].vertex_index][0] / 255)
                
        # set uv
        uv1 = mesh.uv_textures.new("UVMap")
        uv_layer1 = mesh.uv_layers[0]
        for i in range(len(uv_layer1.data)):
            #if(mesh.loops[i].vertex_index < geometryVerticesCount):
            uv = texCoords[mesh.loops[i].vertex_index]
            uv_layer1.data[i].uv = (uv[0], 1 - uv[1])
            
        # set material
        """for i in range(len(objMats)):
            mesh.materials.append(objMats[i])

        # I guess mesh.polygons and faces are in the same order
        iFace = 0
        for i in range(len(self.moba.Batches)):
            img = self.GetMaterialViewportImage(objMats[i])
            iEndFace = iFace + (self.moba.Batches[i].nTriangle // 3)
            for iFace in range(iFace, iEndFace):
                mesh.polygons[iFace].material_index = i
                mesh.polygons[iFace].use_smooth = True
                if(img != None):
                    uv1.data[iFace].image = img
            iFace += 1"""
            
        # map root material ID to index in mesh materials
        material_indices = {}
        material_viewport_textures = {}

        # add materials
        for i in range(len(self.moba.Batches)):
            mesh.materials.append(materials[self.moba.Batches[i].MaterialID])
            
            material =  mesh.materials[i]
            
            material.WowMaterial.Enabled = True
            
            if(i < self.mogp.nBatchesA):
                material.WowMaterial.BatchType = '0'
            elif(i < self.mogp.nBatchesB):
                material.WowMaterial.BatchType = '1'
            else:
                material.WowMaterial.BatchType = '2'
                
            
            material_viewport_textures[i] = self.GetMaterialViewportImage(mesh.materials[i])
            material_indices[self.moba.Batches[i].MaterialID] = i
            
        # add ghost material
        for i in self.mopy.TriangleMaterials:
            if(i.MaterialID == 0xFF):
                mat_ghost_ID = len(mesh.materials)
                mesh.materials.append(materials[0xFF])
                material_viewport_textures[mat_ghost_ID] = None
                material_indices[0xFF] = mat_ghost_ID
                break

        # set faces material
        for i in range(len(mesh.polygons)):
            matID = self.mopy.TriangleMaterials[i].MaterialID
            mesh.polygons[i].material_index = material_indices[matID]
            mesh.polygons[i].use_smooth = True
            # set texture displayed in viewport
            img = material_viewport_textures[material_indices[matID]]
            if(img != None):
                uv1.data[i].image = img

        # set textured solid in all 3D views and switch to textured mode
        for area in bpy.context.screen.areas:
            if(area.type == 'VIEW_3D'):
                area.spaces[0].show_textured_solid = True
                area.spaces[0].viewport_shade = 'TEXTURED'                

        scn = bpy.context.scene
                    
        for o in scn.objects:
            o.select = False

        mesh.update()
        mesh.validate()
        

        nobj = bpy.data.objects.new(objName, mesh)
        
        if(self.mogp.Flags & MOGP_FLAG.HasWater):
            self.LoadLiquids(objName, nobj.location, mohd.Flags)
        
        # set liquid properties
        """if(self.mogp.Flags & MOGP_FLAG.HasWater):
            liquidGroup = nobj.vertex_groups.new("liquidGroup")

            liquidGroupIndices = []
            for i in range(liquidVerticesCount):
                liquidGroupIndices.append(i + geometryVerticesCount)
            
            liquidGroup.add(liquidGroupIndices, 1.0, 'ADD')
            nobj.WowLiquidEnabled = True
            nobj.WowLiquidVertGroup = "liquidGroup"
            nobj.WowLiquidType = str(self.mogp.LiquidType)"""
        
        #####DEBUG BSP
        """for iNode in range(len(self.mobn.Nodes)):
            bsp_node_indices = self.GetBSPNodeIndices(iNode, self.mobn.Nodes, self.mobr.Faces, self.movi.Indices)
            bsp_node_vg = nobj.vertex_groups.new("debug_bsp")

            #for i in bsp_n1_indices:
            #    bsp_n1_GroupIndices.append(i)
            
            bsp_node_vg.add(bsp_node_indices, 1.0, 'ADD')"""
        #####DEBUG BSP

        # add collision vertex group
        collision_indices = self.GetCollisionIndices()

        if(collision_indices):
            collision_vg = nobj.vertex_groups.new("collision")    
            collision_vg.add(collision_indices, 1.0, 'ADD')
            nobj.WowCollision.Enabled = True
            nobj.WowCollision.VertexGroup = collision_vg.name

        # add WMO group properties
        nobj.WowWMOGroup.Enabled = True
        nobj.WowWMOGroup.GroupName = mogn.GetString(self.mogp.GroupNameOfs)
        #nobj.WowWMOGroup.PortalGroupID = objId
        nobj.WowWMOGroup.GroupDesc = mogn.GetString(self.mogp.DescGroupNameOfs)
        nobj.WowWMOGroup.GroupID = int(self.mogp.GroupID)
        
        nobj.WowWMOGroup.Fog1 = base_name + "_Fog_" + str(self.mogp.FogIndices[0]).zfill(2)
        nobj.WowWMOGroup.Fog2 = base_name + "_Fog_" + str(self.mogp.FogIndices[1]).zfill(2)
        nobj.WowWMOGroup.Fog3 = base_name + "_Fog_" + str(self.mogp.FogIndices[2]).zfill(2)
        nobj.WowWMOGroup.Fog4 = base_name + "_Fog_" + str(self.mogp.FogIndices[3]).zfill(2)     
        
        if(self.mogp.Flags & MOGP_FLAG.HasDoodads):
            if(len(self.modr.DoodadRefs) > 0):
                for i in range(len(self.modr.DoodadRefs)):
                    doodad = nobj.WowWMOGroup.MODR.add()
                    doodad.value = self.modr.DoodadRefs[i]
            
        if(self.mogp.Flags & 0x2000):
            nobj.WowWMOGroup.PlaceType = str(0x2000)
        else:
            nobj.WowWMOGroup.PlaceType = str(0x8)

        scn.objects.link(nobj)

        nobj.select = True
        #nobj.show_transparent = True

        if scn.objects.active is None or scn.objects.active.mode == 'OBJECT':
            scn.objects.active = nobj

    def Save(self, f, obj, root, objNumber, source_doodads, autofill_textures):#, material_indices, group_name_ofs, group_desc_ofs):

        # check Wow WMO panel enabled
        if(not obj.WowWMOGroup.Enabled):
            #bpy.ops.error.message(message="Error: Trying to export " + obj.name + " but Wow WMO Group properties not enabled")
            raise Exception("Error: Trying to export " + obj.name + " but Wow WMO Group properties not enabled")

        bpy.context.scene.objects.active = obj
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        bpy.context.scene.objects.link(new_obj)
        bpy.context.scene.objects.active = new_obj
        
        mesh = new_obj.data
        original_mesh = obj.data
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.quads_convert_to_tris()
        bpy.ops.mesh.select_all(action='DESELECT')
        
        # perform edge split. Needs to be optional.
        bpy.ops.uv.select_all(action='TOGGLE')
        bpy.ops.uv.seams_from_islands(mark_seams=False, mark_sharp=True)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        bpy.ops.object.modifier_add(type='EDGE_SPLIT')
        bpy.context.object.modifiers["EdgeSplit"].use_edge_angle = False
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="EdgeSplit")
        
        # perform custom normal data calculation if not yet calculated by the user
        bpy.context.scene.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        
        auto_normal_smooth = False
        if (original_mesh.has_custom_normals == False):
            bpy.ops.mesh.customdata_custom_splitnormals_add()
            bpy.ops.mesh.masked_soften_normals()
            original_mesh.calc_normals_split()
            auto_normal_smooth = True
            
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # perform custom normal data transfer to a temporary object
        obj.select = True
        bpy.context.scene.objects.active = new_obj
        bpy.ops.object.data_transfer(use_reverse_transfer=True, data_type='CUSTOM_NORMAL')
        obj.select = False
        
        # clear auto-generated custom normal data on original scene object to avoid changes of original scene on export. If normals are user defined, we do not touch them.
        bpy.context.scene.objects.active = obj 
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        if (original_mesh.has_custom_normals == True) and (auto_normal_smooth == True):
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.objects.active = new_obj
        
        # apply object transformation to geometry. Needs to be optional.
        new_obj.select = True
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        new_obj.select = False

        #mesh.calc_normals_split() -- We seem to not need that after transfer
        
        # doing some safety checks to notify the user if the object is badly formed
        if(len(mesh.vertices) > 65535):
            raise Exception("Object " + str(obj.name) + " contains more vertices (" + str(len(mesh.vertices)) + ") than it is supported.  Maximum amount of vertices you can use per one object is 65535.")
        
        if len(mesh.materials) > 254 or len(root.momt.Materials) > 255:
            raise Exception("Scene has excceeded the maximum allowed number of WoW materials (255). Your scene now has " + len(root.momt.Materials) + " materials. So, " + (len(root.momt.Materials) - 255) + " extra ones." )
        
        
        mver = MVER_chunk()
        mver.Version = 17
        mver.Write(f)

        mogp = MOGP_chunk()
        
        map_batches = {} #												--map_batches:creation
        
        # initializing batches:
        new_index_last = 0 #												--new_index_last:creation
        nBatchesA = 0
        nBatchesB = 0
        nBatchesC = 0
        map_indices = {} #												--map_indices:creation
        vg_collision = None #												--vg_collision:creation
        material_indices = {} #                                                                                         --material_indices:creation
        batchTypeMap = {}
        
        for i in range(len(mesh.materials)):
            material_indices[i] = root.AddMaterial(mesh.materials[i]) # adding materials to root object. Returns the index of material if the passed one already exists.
            
            if(mesh.materials[i].WowMaterial.Enabled == True and mesh.materials[i].WowMaterial.BatchType == '0'):
                nBatchesA += 1
                batchTypeMap[material_indices.get(i)] = 0
            if(mesh.materials[i].WowMaterial.Enabled == True and mesh.materials[i].WowMaterial.BatchType == '1'):
                nBatchesB += 1
                batchTypeMap[material_indices.get(i)] = 1
            if(mesh.materials[i].WowMaterial.Enabled == True and mesh.materials[i].WowMaterial.BatchType == '2'):
                nBatchesC += 1
                batchTypeMap[material_indices.get(i)] = 2

            if(autofill_textures):
                if( (mesh.materials[i].active_texture is not None) and not mesh.materials[i].WowMaterial.Texture1 and \
                    (mesh.materials[i].active_texture.type == 'IMAGE') and (mesh.materials[i].active_texture.image is not None) ):
                        print ("test")
                        if(bpy.context.scene.WoWRoot.UseTextureRelPath):
                            mesh.materials[i].WowMaterial.Texture1 = os.path.splitext( os.path.relpath( mesh.materials[i].active_texture.image.filepath, bpy.context.scene.WoWRoot.TextureRelPath ))[0] + ".blp"
                            print(os.path.splitext( os.path.relpath( mesh.materials[i].active_texture.image.filepath, bpy.context.scene.WoWRoot.TextureRelPath ))[0] + ".blp")
                        else:
                            mesh.materials[i].WowMaterial.Texture1 = os.path.splitext( mesh.materials[i].active_texture.image.filepath )[0] + ".blp"
                            print(os.path.splitext( os.path.relpath( mesh.materials[i].active_texture.image.filepath, bpy.context.scene.WoWRoot.TextureRelPath ))[0] + ".blp")       

        
        if new_obj.WowCollision.Enabled:
            vg_collision = new_obj.vertex_groups.get(new_obj.WowCollision.VertexGroup)
        
        for poly in mesh.polygons:
            batch_current = map_batches.setdefault(material_indices.get(poly.material_index), RenderBatch())
        
            triangle_current = []
            for vert_index in poly.vertices:
                new_index_current = map_indices.get(vert_index)
                if new_index_current == None:
                    new_index_current = new_index_last
                    map_indices[vert_index] = new_index_current
                    new_index_last += 1
        
                triangle_current.append(new_index_current)
        
                if new_index_current not in batch_current.vertex_infos:
                    info_current = batch_current.vertex_infos.setdefault(new_index_current, VertexInfo())
                    info_current.pos = mesh.vertices[vert_index].co
        
                    if vg_collision != None:
                        for group_info in mesh.vertices[vert_index].groups:
                            if vg_collision.index == group_info.group:
                                info_current.collision = True
                                break
        
            batch_current.triangles.append(triangle_current)
        
            for loop_index in poly.loop_indices:
                info_current = batch_current.vertex_infos.get(map_indices.get(mesh.loops[loop_index].vertex_index))
                info_current.normals.append(mesh.loops[loop_index].normal)
        
                if len(mesh.uv_layers) > 0:
                    info_current.uv = (mesh.uv_layers.active.data[loop_index].uv[0], 1.0 - mesh.uv_layers.active.data[loop_index].uv[1])
        
                if len(mesh.vertex_colors) > 0:
                        info_current.color[2] = round(mesh.vertex_colors.active.data[loop_index].color[0] * 255) # B
                        info_current.color[1] = round(mesh.vertex_colors.active.data[loop_index].color[1] * 255) # G
                        info_current.color[0] = round(mesh.vertex_colors.active.data[loop_index].color[2] * 255) # R
        
        
        del vg_collision #													--vg_collision:deletion
        del map_indices #													--map_indices:deletion
        del new_index_last #												        --new_index_last:deletion                                                                                               
        # done: initializing batches
        
        # initializing chunks:
        total_size = 0 #                         --total_size:creation
        count = 0
        for material_index, batch in map_batches.items():
            total_size += len(batch.vertex_infos)
            count += 1
        
        movi = MOVI_chunk() #                    --movi:creation
        mopy = MOPY_chunk() #                    --mopy:creation
        moba = MOBA_chunk(count) #                    --moba:creation
        
        movt = MOVT_chunk(total_size) #          --movt:creation
        monr = MONR_chunk(total_size) #          --monr:creation
        motv = MOTV_chunk(total_size) #          --motv:creation
        mocv = MOCV_chunk(total_size) #          --mocv:creation
        
        del total_size #                         --total_size:deletion
        # done: initializing chunks
        
        iA = 0
        iB = nBatchesA
        iC = nBatchesB
        
        # filling chunks:
        for material_index, batch in map_batches.items():
            n_triangles = len(batch.triangles)
            sentry_indices = [0xFFFF, 0]
        
            for triangle in batch.triangles:
                tri_mat = TriangleMaterial()
                needs_collision = True
        
                for vert_index in triangle:
                    sentry_indices[0] = ret_min(sentry_indices[0], vert_index)
                    sentry_indices[1] = ret_max(sentry_indices[1], vert_index)
                    
                    movi.Indices.append(vert_index)
                    
                    if batch.vertex_infos.get(vert_index).collision == False:
                        needs_collision = False
        
                tri_mat.MaterialID = material_index
                tri_mat.Flags = 0x0 if tri_mat.MaterialID == 0xFF else 0x20
                tri_mat.Flags |= 0x48 if needs_collision else 0x4
        
                mopy.TriangleMaterials.append(tri_mat)
        
            
            if n_triangles == 0 or material_index == 0xFF:
                continue
        
        
            batch_current = Batch()
        
            batch_current.BoundingBox = [32767, 32767, 32767, -32768, -32768, -32768]
            for index, info in batch.vertex_infos.items():
                movt.Vertices[index] = info.pos
                monr.Normals[index] = GetAvg(info.normals)
                motv.TexCoords[index] = info.uv
                mocv.vertColors[index] = info.color
        
                for i in range(0, 2):
                    for j in range(0, 3):
                        idx = i * 3 + j
                        batch_current.BoundingBox[idx] = ret_min(batch_current.BoundingBox[idx], floor(info.pos[j])) if i == 0 else \
                            ret_max(batch_current.BoundingBox[idx], ceil(info.pos[j]))
        
            batch_current.StartTriangle = len(movi.Indices) - n_triangles * 3
            batch_current.nTriangle = n_triangles * 3
            batch_current.StartVertex = sentry_indices[0]
            batch_current.LastVertex = sentry_indices[1]
            batch_current.MaterialID = material_index
            
            if(batchTypeMap.get(material_index) == 0):
                moba.Batches[iA] = batch_current
                iA += 1
            if(batchTypeMap.get(material_index) == 1):
                moba.Batches[iB] = batch_current
                iB += 1
            if(batchTypeMap.get(material_index) == 2):
                moba.Batches[iC] = batch_current
                iC += 1                
        
              
        del material_indices #
        del batchTypeMap
        del iA
        del iB
        del iC
        # done: filling chunks
        
        map_batches = {} #													--map_batches:deletion        
        
        # write BSP nodes
        mobn = MOBN_chunk()

        # write BSP faces
        mobr = MOBR_chunk()

        # write header
        mogp.BoundingBoxCorner1 = [32767, 32767, 32767]
        mogp.BoundingBoxCorner2 = [-32768, -32768, -32768]        
        
        for vtx in movt.Vertices:
            for i in range(0, 3):
                mogp.BoundingBoxCorner1[i] = ret_min(mogp.BoundingBoxCorner1[i], floor(vtx[i]))
                mogp.BoundingBoxCorner2[i] = ret_max(mogp.BoundingBoxCorner2[i], ceil(vtx[i]))
            

        mogp.Flags = MOGP_FLAG.HasCollision # /!\ MUST HAVE 0x1 FLAG ELSE THE GAME CRASH !
        if(new_obj.WowWMOGroup.VertShad):
            mogp.Flags = mogp.Flags | MOGP_FLAG.HasVertexColor
        if(new_obj.WowWMOGroup.SkyBox):
            mogp.Flags = mogp.Flags | MOGP_FLAG.HasSkybox
            
        mogp.Flags = mogp.Flags | int(new_obj.WowWMOGroup.PlaceType)


        mogp.PortalStart = -1
        mogp.PortalCount = 0
        
        fog_id = 0
        fogMap = {}
    
        mliq = MLIQ_chunk()

        hasWater = False        
        
        for ob in bpy.context.scene.objects:
            if(ob.type == "MESH"):
                obj_mesh = ob.data
                if(ob.WowPortalPlane.Enabled and (ob.WowPortalPlane.First == objNumber or ob.WowPortalPlane.Second == objNumber)):
                    portalRef = [0,0,0]
                    if(mogp.PortalStart == -1):
                        mogp.PortalStart = root.PortalRCount
                    portalRef[0] = ob.WowPortalPlane.PortalID
                    modify = 1
                    if(ob.WowPortalPlane.First == objNumber):
                        portalRef[1] = ob.WowPortalPlane.Second
                        portalRef[2] = 1
                    else:
                        portalRef[1] = ob.WowPortalPlane.First
                        portalRef[2] = -1
                    if(ob.WowPortalPlane.Invert):
                        modify = -1
                    portalRef[2] = portalRef[2] * modify
                    root.PortalR.append(portalRef)
                    mogp.PortalCount+=1
                if(ob.WowFog.Enabled):
                    fogMap[ob.name] = fog_id
                    fog_id += 1
                
                if(ob.WowLiquid.Enabled and ob.WowLiquid.WMOGroup == obj.name): # export liquids

                    HasWater = True

                    print("Exporting liquid:", ob.name )
                    mesh = ob.data
                    StartVertex = 0
                    sum = 0
                    for vertex in obj_mesh.vertices:
                        curSum = vertex.co[0] + vertex.co[1]
                        
                        if (curSum < sum):
                            StartVertex = vertex.index
                            sum = curSum
                            
                    mliq.xVerts = round(ob.dimensions[0] / 4.1666625)
                    mliq.yVerts = round(ob.dimensions[1] / 4.1666625)
                    mliq.xTiles = mliq.xVerts - 1
                    mliq.yTiles = mliq.yTiles - 1
                    mliq.Position = mesh.vertices[StartVertex].co

                    mogp.LiquidType = self.FromWMOLiquid( int(ob.WowLiquid.LiquidType) )
                    root.mohd.Flags |= 0x4 # needs checking

                    material = bpy.data.materials.new(ob.name)
                    material.WowMaterial.Enabled = True
                    material.WowMaterial.Flags3 = '1'

                    material.WowMaterial.Texture1 = "DUNGEONS\TEXTURES\FLOOR\JLO_UNDEADZIGG_SLIMEFLOOR.BLP"


                    if mogp.LiquidType == 3:
                        material.WowMaterial.Texture1 = "DUNGEONS\TEXTURES\TRIM\BM_BRSPIRE_LAVAWALLTRANS.BLP"
                    elif mogp.LiquidType == 4:
                        material.WowMaterial.Texture1 = "DUNGEONS\TEXTURES\TRIM\BM_BRSPIRE_LAVAWALLTRANS.BLP"

                    mliq.materialID = root.AddMaterial(material) 

                    if mogp.LiquidType == 3:

                        uvMap = {}

                        for poly in mesh.polygons:
                            for loop_index in poly.loop_indices:
                                if mesh.loops[loop_index].vertex_index not in uvMap:
                                    uvMap[mesh.loops[loop_index].vertex_index] = mesh.uv_layers.active.data[loop_index].uv

                        for i in range(mliq.xVerts * mliq.yVerts):
                            vertex = MagmaVertex()

                            vertex.u = uvMap.get(mesh.vertices[i].index)[0]
                            vertex.v = uvMap.get(mesh.vertices[i].index)[1]

                            vertex.height = mesh.vertices[i].co[2]
                            mliq.VertexMap.append(vertex)

                    else:

                        for i in range(mliq.xVerts * mliq.yVerts):
                            vertex = WaterVertex()

                            vertex.height = mesh.vertices[i].co[2]
                            mliq.VertexMap.append(vertex)

                    flag_0x1 = mesh.vertex_colors["flag_0x1"]
                    flag_0x2 = mesh.vertex_colors["flag_0x2"]
                    flag_0x4 = mesh.vertex_colors["flag_0x4"]
                    flag_0x8 = mesh.vertex_colors["flag_0x8"]
                    flag_0x10 = mesh.vertex_colors["flag_0x10"]
                    flag_0x20 = mesh.vertex_colors["flag_0x20"]
                    flag_0x40 = mesh.vertex_colors["flag_0x40"]
                    flag_0x80 = mesh.vertex_colors["flag_0x80"]

                    for poly in mesh.polygons:

                        if flag_0x1.data[poly.loop_indices[0]].color == (0, 0, 255):
                            mliq.TileFlags[poly.index] |= 0x1
                        if flag_0x2.data[poly.loop_indices[0]].color == (0, 0, 255):
                            mliq.TileFlags[poly.index] |= 0x2
                        if flag_0x4.data[poly.loop_indices[0]].color == (0, 0, 255):
                            mliq.TileFlags[poly.index] |= 0x4
                        if flag_0x8.data[poly.loop_indices[0]].color == (0, 0, 255):
                            mliq.TileFlags[poly.index] |= 0x8
                        if flag_0x10.data[poly.loop_indices[0]].color == (0, 0, 255):
                            mliq.TileFlags[poly.index] |= 0x10
                        if flag_0x20.data[poly.loop_indices[0]].color == (0, 0, 255):
                            mliq.TileFlags[poly.index] |= 0x20
                        if flag_0x40.data[poly.loop_indices[0]].color == (0, 0, 255):
                            mliq.TileFlags[poly.index] |= 0x40
                        if flag_0x80.data[poly.loop_indices[0]].color == (0, 0, 255):
                            mliq.TileFlags[poly.index] |= 0x80
         
        
        if(mogp.PortalStart == -1):
            mogp.PortalStart = root.PortalRCount
        root.PortalRCount+=mogp.PortalCount
        mogp.nBatchesA = nBatchesA
        mogp.nBatchesB = nBatchesB
        mogp.nBatchesC = nBatchesC
        mogp.nBatchesD = 0
        mogp.FogIndices = (fogMap.get(new_obj.WowWMOGroup.Fog1, 0), fogMap.get(new_obj.WowWMOGroup.Fog2, 0), fogMap.get(new_obj.WowWMOGroup.Fog3, 0), fogMap.get(new_obj.WowWMOGroup.Fog4, 0), )
        mogp.LiquidType = 0
        mogp.GroupID = int(new_obj.WowWMOGroup.GroupID)
        mogp.Unknown1 = 0
        mogp.Unknown2 = 0
        
        groupInfo = root.AddGroupInfo(mogp.Flags, [mogp.BoundingBoxCorner1, mogp.BoundingBoxCorner2], new_obj.WowWMOGroup.GroupName, new_obj.WowWMOGroup.GroupDesc)
        mogp.GroupNameOfs = groupInfo[0]
        mogp.DescGroupNameOfs = groupInfo[1]
        
        f.seek(0x58)
        mopy.Write(f)
        movi.Write(f)
        movt.Write(f)
        monr.Write(f)
        motv.Write(f)
        moba.Write(f)
        
        if(source_doodads):
            modr = MODR_chunk()
            if(len(new_obj.WowWMOGroup.MODR) > 0):
                print("has doodads")
                for doodad in new_obj.WowWMOGroup.MODR:
                    modr.DoodadRefs.append(doodad.value)
                mogp.Flags = mogp.Flags | MOGP_FLAG.HasDoodads
            modr.Write(f)
        
        bsp_tree = BSP_Tree()
        bsp_tree.GenerateBSP(movt.Vertices, movi.Indices, new_obj.WowCollision.NodeSize)

        mobn.Nodes = bsp_tree.Nodes
        mobr.Faces = bsp_tree.Faces

        mobn.Write(f)
        mobr.Write(f)
        mocv.Write(f)

        if HasWater:
            mliq.Write(f)


        # get file size
        f.seek(0, 2)
        mogp.Header.Size = f.tell() - 20

        # write header
        f.seek(0xC)
        mogp.Write(f)
        
        # bpy.context.scene.objects.unlink(new_obj)
        bpy.data.objects.remove(new_obj, do_unlink = True)
        
    
        # obj.select = True
        bpy.context.scene.objects.active = obj

        return None