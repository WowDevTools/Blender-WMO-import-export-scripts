
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
    normal = [0.0, 0.0, 0.0]
    
    for n in list:
        for i in range(0, 3):
            normal[i] += n[i]
    
    for i in range(0, 3):
        normal[i] /= len(list)
        
    return normal


def CompColors(color1, color2):

    for i in range(0, 3):
        if color1[i] != color2[i]:
            return False
    return True

def ret_min(a, b):
    return a if a < b else b

def ret_max(a, b):
    return a if a > b else b

def GetBatchType(polygon, mesh, vg_index_a, vg_index_b):
    counter_a = 0
    counter_b = 0

    for i in polygon.vertices:
        for group_info in mesh.vertices[i].groups:
            if group_info.group == vg_index_a:
                counter_a += 1
            elif group_info.group == vg_index_b:
                counter_b += 1

    if counter_a == len(polygon.vertices):
        return 0
    else:
        return 1 if counter_b == len(polygon.vertices) else 2

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
            if (self.mogp.LiquidType == 3) or (self.mogp.LiquidType == 4) or (self.mogp.LiquidType == 7) or \
            (self.mogp.LiquidType == 8) or (self.mogp.LiquidType == 11) or (self.mogp.LiquidType == 12):
                self.mliq = MLIQ_chunk(False)
            else:
                self.mliq = MLIQ_chunk()
            self.mliq.Read(f)
            
        # read second MOTV and mocv
        if(self.mogp.Flags & MOGP_FLAG.HasTwoMOTV):
            self.motv2 = MOTV_chunk()
            self.motv2.Read(f)
            
        if(self.mogp.Flags & MOGP_FLAG.HasTwoMOCV):
            self.mocv2 = MOCV_chunk()
            self.mocv2.Read(f)
        
            
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
    def LoadLiquids(self, objName, pos, root):
        
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
        obj = bpy.data.objects.new(name, mesh)
                    
        #create mesh from python data
        mesh.from_pydata(vertices,[],faces)
        mesh.update(calc_edges=True)
        mesh.validate()

        #create uv map if liquid is lava
        
        if (self.mogp.LiquidType == 3) or (self.mogp.LiquidType == 4) or (self.mogp.LiquidType == 7) or \
        (self.mogp.LiquidType == 8) or (self.mogp.LiquidType == 11) or (self.mogp.LiquidType == 12):
                
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
        obj.location = pos
        bpy.context.scene.objects.link(obj)
        
        bpy.context.scene.objects.active = obj
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=True)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        obj.lock_scale = [True, True, True]
        obj.lock_rotation[2] = True
        
        obj.WowLiquid.Enabled = True
        
        # getting Liquid Type ID
        
        basic_liquid_type = self.mogp.LiquidType
        real_liquid_type = 0
        
        if(root.mohd.Flags & 0x4): # defining real liquid type ID from DBC. to understand what is being done here see wiki (MLIQ)
                
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

        
        obj.WowLiquid.LiquidType = str(real_liquid_type)
        root.liquidReferences[name] = objName

               
    
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
    def LoadObject(self, objName, doodads, objId, base_name, root):

        vertices = []
        normals = []
        faces = []

        texCoords = []
        vertColors = []
        
        vertices = self.movt.Vertices
        normals = self.monr.Normals
        texCoords = self.motv.TexCoords


        for i in range(0, len(self.movi.Indices), 3):
            faces.append(self.movi.Indices[i:i+3])

        # create mesh
        mesh = bpy.data.meshes.new(objName)
        mesh.from_pydata(vertices, [], faces)

        # create object
        scn = bpy.context.scene
                    
        for o in scn.objects:
            o.select = False

        mesh.update()
        mesh.validate()

        nobj = bpy.data.objects.new(objName, mesh)
        scn.objects.link(nobj)

        # set normals
        for i in range(len(normals)):
            mesh.vertices[i].normal = normals[i]
            
        # set vertex color
        if self.mogp.Flags & MOGP_FLAG.HasVertexColor:
            nobj.WowWMOGroup.VertShad = True
            vertColor_layer1 = mesh.vertex_colors.new("Col")

            if not root.mohd.Flags & 0x01: 
                lightmap = nobj.vertex_groups.new("Lightmap")
                nobj.WowVertexInfo.Enabled = True
                nobj.WowVertexInfo.Lightmap = lightmap.name
                lightmap.add(self.movi.Indices, 1.0, 'ADD')

            # loops and vertex_color are in the same order, so we use it to find vertex index
            for i in range(len(mesh.loops)):

                vertColor_layer1.data[i].color = (self.mocv.vertColors[mesh.loops[i].vertex_index][2] / 255, \
                        self.mocv.vertColors[mesh.loops[i].vertex_index][1] / 255, \
                        self.mocv.vertColors[mesh.loops[i].vertex_index][0] / 255)

                if not root.mohd.Flags & 0x01: 
                    mesh.vertices[mesh.loops[i].vertex_index].groups[lightmap.index].weight = self.mocv.vertColors[mesh.loops[i].vertex_index][3] / 255

        if self.mogp.Flags & MOGP_FLAG.HasTwoMOCV:
            blendmap = nobj.vertex_groups.new("Blendmap")    
            nobj.WowVertexInfo.Enabled = True
            nobj.WowVertexInfo.Blendmap = blendmap.name
            blendmap.add(self.movi.Indices, 1.0, 'ADD')

            for vertex in mesh.vertices:
                vertex.groups[blendmap.index].weight = self.mocv2.vertColors[vertex.index][3] / 255

                
        # set uv
        uv1 = mesh.uv_textures.new("UVMap")
        uv_layer1 = mesh.uv_layers[0]
        for i in range(len(uv_layer1.data)):
            #if(mesh.loops[i].vertex_index < geometryVerticesCount):
            uv = texCoords[mesh.loops[i].vertex_index]
            uv_layer1.data[i].uv = (uv[0], 1 - uv[1])

        if self.mogp.Flags & MOGP_FLAG.HasTwoMOTV:
            uv2 = mesh.uv_textures.new("UVMap_2")
            nobj.WowVertexInfo.Enabled = True
            nobj.WowVertexInfo.SecondUV = uv2.name
            uv_layer2 = mesh.uv_layers[1]
        
            for j in range(len(uv_layer2.data)):
                uv = self.motv2.TexCoords[mesh.loops[j].vertex_index]
                uv_layer2.data[j].uv = (uv[0], 1 - uv[1])
            
        # map root material ID to index in mesh materials
        material_indices = {}
        material_viewport_textures = {}

        # create batch vertex groups

        batchMapA = None
        batchMapB = None

        if(self.mogp.nBatchesA != 0):
            batchMapA = nobj.vertex_groups.new("BatchMapA")    
            nobj.WowVertexInfo.Enabled = True
            nobj.WowVertexInfo.BatchTypeA = batchMapA.name
        if(self.mogp.nBatchesB != 0):
            batchMapB = nobj.vertex_groups.new("BatchMapB")
            nobj.WowVertexInfo.Enabled = True
            nobj.WowVertexInfo.BatchTypeB = batchMapB.name

        # add materials
        for i in range(len(self.moba.Batches)):
            mesh.materials.append(root.materials[self.moba.Batches[i].MaterialID])
            
            material = mesh.materials[i]
            
            material.WowMaterial.Enabled = True
                
            
            material_viewport_textures[i] = self.GetMaterialViewportImage(mesh.materials[i])
            material_indices[self.moba.Batches[i].MaterialID] = i


            if(i < self.mogp.nBatchesA):
                batchMapA.add(self.movi.Indices[self.moba.Batches[i].StartTriangle : self.moba.Batches[i].StartTriangle + self.moba.Batches[i].nTriangle], 1.0, 'ADD')

            elif(i < self.mogp.nBatchesA +  self.mogp.nBatchesB):
                batchMapB.add(self.movi.Indices[self.moba.Batches[i].StartTriangle : self.moba.Batches[i].StartTriangle + self.moba.Batches[i].nTriangle], 1.0, 'ADD')


            
        # add ghost material
        for i in self.mopy.TriangleMaterials:
            if(i.MaterialID == 0xFF):
                mat_ghost_ID = len(mesh.materials)
                mesh.materials.append(root.materials[0xFF])
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
            nobj.WowVertexInfo.Enabled = True
            nobj.WowVertexInfo.VertexGroup = collision_vg.name

        # add WMO group properties
        nobj.WowWMOGroup.Enabled = True
        nobj.WowWMOGroup.GroupName = root.mogn.GetString(self.mogp.GroupNameOfs)
        #nobj.WowWMOGroup.PortalGroupID = objId
        nobj.WowWMOGroup.GroupDesc = root.mogn.GetString(self.mogp.DescGroupNameOfs)
        nobj.WowWMOGroup.GroupID = int(self.mogp.GroupID)
        
        nobj.WowWMOGroup.Fog1 = base_name + "_Fog_" + str(self.mogp.FogIndices[0]).zfill(2)
        nobj.WowWMOGroup.Fog2 = base_name + "_Fog_" + str(self.mogp.FogIndices[1]).zfill(2)
        nobj.WowWMOGroup.Fog3 = base_name + "_Fog_" + str(self.mogp.FogIndices[2]).zfill(2)
        nobj.WowWMOGroup.Fog4 = base_name + "_Fog_" + str(self.mogp.FogIndices[3]).zfill(2)    

        
        if(self.mogp.Flags & MOGP_FLAG.HasWater):
            self.LoadLiquids(objName, nobj.location, root) 
        
        if(self.mogp.Flags & MOGP_FLAG.HasDoodads):
            if(len(self.modr.DoodadRefs) > 0):
                for i in range(len(self.modr.DoodadRefs)):
                    doodad = nobj.WowWMOGroup.MODR.add()
                    doodad.value = self.modr.DoodadRefs[i]
            
        if(self.mogp.Flags & 0x2000):
            nobj.WowWMOGroup.PlaceType = str(0x2000)
        else:
            nobj.WowWMOGroup.PlaceType = str(0x8)

        nobj.select = True
        #nobj.show_transparent = True

        if scn.objects.active is None or scn.objects.active.mode == 'OBJECT':
            scn.objects.active = nobj

    def Save(self, f, obj, root, objNumber, source_doodads, autofill_textures): #, material_indices, group_name_ofs, group_desc_ofs):

        mohd_0x1 = True

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

        # perform vertex group split to keep batches accurate.
        bpy.ops.object.mode_set(mode='EDIT')
        if new_obj.WowVertexInfo.BatchTypeA != "" and new_obj.WowVertexInfo.Enabled:
            bpy.ops.object.vertex_group_set_active(group=new_obj.WowVertexInfo.BatchTypeA)
            bpy.ops.object.vertex_group_select()
            bpy.ops.mesh.split()
            bpy.ops.mesh.select_all(action='DESELECT')

        if new_obj.WowVertexInfo.BatchTypeB != "" and new_obj.WowVertexInfo.Enabled:
            bpy.ops.object.vertex_group_set_active(group=new_obj.WowVertexInfo.BatchTypeB)
            bpy.ops.object.vertex_group_select()
            bpy.ops.mesh.split()
            bpy.ops.mesh.select_all(action='DESELECT')

        bpy.ops.object.mode_set(mode='OBJECT')
        
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
        
        material_indices = {} 
        
        for i in range(len(mesh.materials)):
            material_indices[i] = root.AddMaterial(mesh.materials[i]) # adding materials to root object. Returns the index of material if the passed one already exists.
            
            if(autofill_textures):
                if( (mesh.materials[i].active_texture is not None) and not mesh.materials[i].WowMaterial.Texture1 and \
                    (mesh.materials[i].active_texture.type == 'IMAGE') and (mesh.materials[i].active_texture.image is not None) ):
                        if(bpy.context.scene.WoWRoot.UseTextureRelPath):
                            mesh.materials[i].WowMaterial.Texture1 = os.path.splitext( os.path.relpath( mesh.materials[i].active_texture.image.filepath, bpy.context.scene.WoWRoot.TextureRelPath ))[0] + ".blp"
                            print(os.path.splitext( os.path.relpath( mesh.materials[i].active_texture.image.filepath, bpy.context.scene.WoWRoot.TextureRelPath ))[0] + ".blp")
                        else:
                            mesh.materials[i].WowMaterial.Texture1 = os.path.splitext( mesh.materials[i].active_texture.image.filepath )[0] + ".blp"
                            print(os.path.splitext( os.path.relpath( mesh.materials[i].active_texture.image.filepath, bpy.context.scene.WoWRoot.TextureRelPath ))[0] + ".blp")

        polyBatchMap = {}

        vg_batch_a = None
        vg_batch_b = None
        vg_collision = None
        vg_lightmap = None
        vg_blendmap = None
        uv_second_uv = None

        if new_obj.WowVertexInfo.Enabled:

            if new_obj.WowVertexInfo.BatchTypeA != "":
                vg_batch_a = new_obj.vertex_groups.get(new_obj.WowVertexInfo.BatchTypeA)
            else:
                vg_batch_a = new_obj.vertex_groups.new("BatchMapA")

            if new_obj.WowVertexInfo.BatchTypeB != "":
                vg_batch_b = new_obj.vertex_groups.get(new_obj.WowVertexInfo.BatchTypeB)
            else:
                vg_batch_b = new_obj.vertex_groups.new("BatchMapB")

            if new_obj.WowVertexInfo.VertexGroup != "":
                vg_collision = new_obj.vertex_groups.get(new_obj.WowVertexInfo.VertexGroup)
            
            if new_obj.WowVertexInfo.Lightmap != "":
                vg_lightmap = new_obj.vertex_groups.get(new_obj.WowVertexInfo.Lightmap)
                mohd_0x1 = False

            if new_obj.WowVertexInfo.Blendmap != "":
                vg_blendmap = new_obj.vertex_groups.get(new_obj.WowVertexInfo.Blendmap)
                mogp.Flags |= MOGP_FLAG.HasTwoMOCV

            if new_obj.WowVertexInfo.SecondUV != "":
                uv_second_uv = new_obj.data.uv_textures.get(new_obj.WowVertexInfo.SecondUV)
                mogp.Flags |= MOGP_FLAG.HasTwoMOTV
        
        else:
            vg_batch_a = new_obj.vertex_groups.new("BatchMapA")
            vg_batch_b = new_obj.vertex_groups.new("BatchMapB")


        for poly in mesh.polygons:
            polyBatchMap.setdefault( (material_indices.get(poly.material_index), GetBatchType(poly, mesh, vg_batch_a.index, vg_batch_b.index)), [] ).append(poly.index)

        vertex_size = len(mesh.vertices)

        # count A and B batches amount

        nBatchesA = 0
        nBatchesB = 0
        nBatchesC = 0

        for batchKey, polyBatch in polyBatchMap.items():
            if batchKey[0] != 0xFF:
                if batchKey[1] == 0:
                    nBatchesA += 1
                elif batchKey[1] == 1:
                    nBatchesB += 1
                else:
                    nBatchesC += 1

        movi = MOVI_chunk()
        mopy = MOPY_chunk()
        moba = MOBA_chunk(nBatchesA + nBatchesB + nBatchesC)

        movt = MOVT_chunk()
        monr = MONR_chunk(vertex_size)
        motv = MOTV_chunk(vertex_size)
        motv2 = MOTV_chunk(vertex_size)
        mocv = MOCV_chunk(vertex_size)
        mocv2 = MOCV_chunk(vertex_size)

        for vertex in mesh.vertices:
            movt.Vertices.append(vertex.co)

        normalMap = {}
        batchMap = {}

        # write geometry data and batches

        batch_counter_a = 0
        batch_counter_b = 0
        batch_counter_c = 0

        for batchKey, polyBatch in polyBatchMap.items():

            firstIndex = len(movi.Indices)

            for poly in polyBatch:
                collision_counter = 0

                for vertex_index in mesh.polygons[poly].vertices:
                    movi.Indices.append(vertex_index)

                    if vg_collision != None:
                        for group_info in mesh.vertices[vertex_index].groups:
                            if group_info.group == vg_collision.index:
                                collision_counter += 1

                tri_mat = TriangleMaterial()
                tri_mat.MaterialID = batchKey[0]
                tri_mat.Flags = 0x0 if tri_mat.MaterialID == 0xFF else 0x20
                tri_mat.Flags |= 0x48 if collision_counter == len(mesh.polygons[poly].vertices) else 0x4
                mopy.TriangleMaterials.append(tri_mat)

                for loop_index in mesh.polygons[poly].loop_indices:

                    if len(mesh.uv_layers) > 0:
                        motv.TexCoords[mesh.loops[loop_index].vertex_index] = (mesh.uv_layers.active.data[loop_index].uv[0], 1.0 - mesh.uv_layers.active.data[loop_index].uv[1])

                    if uv_second_uv != None:
                        motv2.TexCoords[mesh.loops[loop_index].vertex_index] = (mesh.uv_layers[uv_second_uv.name].data[loop_index].uv[0], 1.0 - mesh.uv_layers[uv_second_uv.name].data[loop_index].uv[1])


                    if (new_obj.WowWMOGroup.VertShad or new_obj.WowWMOGroup.PlaceType == '8192') and len(mesh.vertex_colors) > 0:
                        vertex_color = [0x7F, 0x7F, 0x7F, 0x00]
                        vertex_color2 = [0x7F, 0x7F, 0x7F, 0x00]

                        for i in range(0, 3):
                            vertex_color[i] = round(mesh.vertex_colors.active.data[loop_index].color[3 - i - 1] * 255)
                        if vg_lightmap != None:
                            vertex_color[3] = round(mesh.vertices[mesh.loops[loop_index].vertex_index].groups[vg_lightmap.index].weight * 255)
                            
                        mocv.vertColors[mesh.loops[loop_index].vertex_index] = vertex_color

                    if vg_blendmap != None:
                        mocv2.vertColors[mesh.loops[loop_index].vertex_index][3] = round(mesh.vertices[mesh.loops[loop_index].vertex_index].groups[vg_blendmap.index].weight * 255)
                    
                    normalMap.setdefault(mesh.loops[loop_index].vertex_index, []).append(mesh.loops[loop_index].normal)

            nIndices = len(movi.Indices) - firstIndex

            BoundingBox = [32767, 32767, 32767, -32768, -32768, -32768]

            for poly in polyBatch:
                for vertex_index in mesh.polygons[poly].vertices:
                    monr.Normals[vertex_index] = GetAvg(normalMap.get(vertex_index))

                    for i in range(0, 2):
                        for j in range(0, 3):
                            idx = i * 3 + j
                            BoundingBox[idx] = ret_min(BoundingBox[idx], floor(movt.Vertices[vertex_index][j])) if i == 0 \
                            else ret_max(BoundingBox[idx], ceil(movt.Vertices[vertex_index][j]))

            # skip batch writing if processed polyBatch is collision

            if batchKey[0] == 0xFF:
                continue

            # write current batch

            batch = Batch()

            batch.BoundingBox = BoundingBox


            batch.StartTriangle = firstIndex
            batch.nTriangle = nIndices

            batch.StartVertex = mesh.polygons[polyBatch[0]].vertices[0]
            batch.LastVertex = mesh.polygons[polyBatch[len(polyBatch) - 1]].vertices[2]

            batch.MaterialID = batchKey[0]


            # sort and write batches

            if batchKey[1] == 0:
                moba.Batches[batch_counter_a] = batch
                batch_counter_a += 1
            elif batchKey[1] == 1:
                moba.Batches[nBatchesA + batch_counter_b] = batch
                batch_counter_b += 1
            else:
                moba.Batches[nBatchesA + nBatchesB + batch_counter_c] = batch
                batch_counter_c += 1
            
        
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
            

        mogp.Flags |= MOGP_FLAG.HasCollision # /!\ MUST HAVE 0x1 FLAG ELSE THE GAME CRASH !
        if new_obj.WowWMOGroup.VertShad:
            mogp.Flags |= MOGP_FLAG.HasVertexColor
        if new_obj.WowWMOGroup.SkyBox:
            mogp.Flags |= MOGP_FLAG.HasSkybox
            
        mogp.Flags |= int(new_obj.WowWMOGroup.PlaceType)
        
        mogp.LiquidType = 15 


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
                
                if(ob.WowLiquid.Enabled and (obj.name == ob.WowLiquid.WMOGroup)): # export liquids

                    hasWater = True

                    print("Export liquid:", ob.name )
                    mesh = ob.data
                    StartVertex = 0
                    sum = 0
                    for vertex in obj_mesh.vertices:
                        curSum = vertex.co[0] + vertex.co[1]
                        
                        if (curSum < sum):
                            StartVertex = vertex.index
                            sum = curSum
                            
                    mliq.xTiles = round(ob.dimensions[0] / 4.1666625)
                    mliq.yTiles = round(ob.dimensions[1] / 4.1666625)
                    mliq.xVerts = mliq.xTiles + 1
                    mliq.yVerts = mliq.yTiles + 1
                    mliq.Position = mesh.vertices[StartVertex].co

                    mogp.Flags |= 0x1000
                    mogp.LiquidType = self.FromWMOLiquid( int(ob.WowLiquid.LiquidType) )
                    root.mohd.Flags |= 0x4 # needs checking

                    material = bpy.data.materials.new(ob.name)
                    material.WowMaterial.Enabled = True
                    material.WowMaterial.Flags3 = '1'

                    material.WowMaterial.Texture1 = "DUNGEONS\TEXTURES\FLOOR\JLO_UNDEADZIGG_SLIMEFLOOR.BLP"


                    if mogp.LiquidType == 3:
                        material.WowMaterial.Texture1 = "DUNGEONS\TEXTURES\TRIM\BM_BRSPIRE_LAVAWALLTRANS.BLP"
                    elif mogp.LiquidType == 4:
                        material.WowMaterial.Texture1 = "DUNGEONS\TEXTURES\FLOOR\JLO_UNDEADZIGG_SLIMEFLOOR.BLP"

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

                        for j in range(mliq.xVerts * mliq.yVerts):
                            vertex = WaterVertex()

                            vertex.height = mesh.vertices[j].co[2]
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
                            tile_flag = 0
                            blue = [0.0, 0.0, 1.0]

                            if CompColors(flag_0x1.data[poly.loop_indices[0]].color, blue): 
                                tile_flag |= 0x1
                            if CompColors(flag_0x2.data[poly.loop_indices[0]].color, blue):
                                tile_flag |= 0x2
                            if CompColors(flag_0x4.data[poly.loop_indices[0]].color, blue):
                                tile_flag |= 0x4
                            if CompColors(flag_0x8.data[poly.loop_indices[0]].color, blue):
                                tile_flag |= 0x8
                            if CompColors(flag_0x10.data[poly.loop_indices[0]].color, blue):
                                tile_flag |= 0x10
                            if CompColors(flag_0x20.data[poly.loop_indices[0]].color, blue):
                                tile_flag |= 0x20
                            if CompColors(flag_0x40.data[poly.loop_indices[0]].color, blue):
                                tile_flag |= 0x40
                            if CompColors(flag_0x80.data[poly.loop_indices[0]].color, blue):
                                tile_flag |= 0x80

                            mliq.TileFlags.append(tile_flag)

         
        
        if(mogp.PortalStart == -1):
            mogp.PortalStart = root.PortalRCount
        root.PortalRCount += mogp.PortalCount
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
        bsp_tree.GenerateBSP(movt.Vertices, movi.Indices, new_obj.WowVertexInfo.NodeSize)

        mobn.Nodes = bsp_tree.Nodes
        mobr.Faces = bsp_tree.Faces

        mobn.Write(f)
        mobr.Write(f)
        mocv.Write(f)

        if hasWater:
            mliq.Write(f)
            
        # write second MOTV and MOCV
        if vg_blendmap != None:
            motv2.Write(f)
            
        if uv_second_uv != None:
            mocv2.Write(f)

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

        return mohd_0x1