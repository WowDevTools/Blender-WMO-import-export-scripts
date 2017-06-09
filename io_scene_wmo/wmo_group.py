
from . import wmo_format
from .wmo_format import *

from . import BSP_Tree
from .BSP_Tree import *

from . import Collision
from .Collision import *

import math
from math import *

from . import debug_utils
from .debug_utils import *

import os
import sys
import mathutils


class WMO_group_file:
    def __init__(self):
        pass


    def Read(self, f):
        """ Read WoW WMO group file """
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
        if self.mogp.Flags & MOGP_FLAG.HasLight:
            self.molr = MOLR_chunk()
            self.molr.Read(f)

        # read doodads
        if self.mogp.Flags & MOGP_FLAG.HasDoodads:
            self.modr = MODR_chunk()
            self.modr.Read(f)

        # read collision faces
        if self.mogp.Flags & MOGP_FLAG.HasCollision:
            self.mobn = MOBN_chunk()
            self.mobn.Read(f)
            self.mobr = MOBR_chunk()
            self.mobr.Read(f)

        # read vertex colors
        if self.mogp.Flags & MOGP_FLAG.HasVertexColor:
            self.mocv = MOCV_chunk()
            self.mocv.Read(f)

        # read liquids
        if self.mogp.Flags & MOGP_FLAG.HasWater:
            if self.mogp.LiquidType in {3, 4, 7, 8, 11, 12}:
                self.mliq = MLIQ_chunk(False)
            else:
                self.mliq = MLIQ_chunk()
            self.mliq.Read(f)

        # read second MOTV and mocv
        if self.mogp.Flags & MOGP_FLAG.HasTwoMOTV:
            self.motv2 = MOTV_chunk()
            self.motv2.Read(f)

        if self.mogp.Flags & MOGP_FLAG.HasTwoMOCV:
            self.mocv2 = MOCV_chunk()
            self.mocv2.Read(f)

    @staticmethod
    def GetAvg(list):
        """ Get single average normal vector from a split normal """
        normal = [0.0, 0.0, 0.0]

        for n in list:
            for i in range(0, 3):
                normal[i] += n[i]

        for i in range(0, 3):
            normal[i] /= len(list)

        return normal

    @staticmethod
    def CompColors(color1, color2):
        """ Compare two colors """

        for i in range(0, 3):
            if color1[i] != color2[i]:
                return False
        return True

    @staticmethod
    def ret_min(a, b):
        return a if a < b else b

    @staticmethod
    def ret_max(a, b):
        return a if a > b else b

    @staticmethod
    def GetBatchType(polygon, mesh, vg_index_a, vg_index_b):
        """ Find which MOBA batch type a passed polygon belongs two """
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

    def GetMaterialViewportImage(self, material):
        """ Get viewport image assigned to a material """
        for i in range(3):
            try:
                img = material.texture_slots[3 - i].texture.image
                return img
            except:
                pass
        return None

    def FromWMOLiquidType(self, basic_liquid_type):
        """ Convert simplified WMO liquid type IDs to real LiquidType.dbc IDs """
        real_liquid_type = 0

        if basic_liquid_type < 20:
            if basic_liquid_type == 0:
                real_liquid_type = 14 if self.mogp.Flags & 0x80000 else 13
            elif basic_liquid_type == 1:
                real_liquid_type = 14
            elif basic_liquid_type == 2:
                real_liquid_type = 19
            elif(basic_liquid_type == 15):
                real_liquid_type = 17
            elif basic_liquid_type == 3:
                real_liquid_type = 20
        else:
            real_liquid_type = basic_liquid_type + 1

        return real_liquid_type

    # return array of vertice and array of faces in a tuple
    def LoadLiquids(self, objName, pos, root):
        """ Load liquid plane of the WMO group. Should only be called if MLIQ is present. """

        # load vertices
        vertices = []
        for y in range(0, self.mliq.yVerts):
            y_pos = self.mliq.Position[1] + y * 4.1666625
            for x in range(0 , self.mliq.xVerts):
                x_pos = self.mliq.Position[0] + x * 4.1666625
                vertices.append((x_pos, y_pos, self.mliq.VertexMap[y * self.mliq.xVerts + x].height[0]))

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

        # create mesh and object
        name = objName + "_Liquid"
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)

        #create mesh from python data
        mesh.from_pydata(vertices,[],faces)
        mesh.update(calc_edges=True)
        mesh.validate()

        #create uv map if liquid is lava
        if self.mogp.LiquidType in {3, 4, 7, 8, 11, 12}:
            uvMap = {}

            for vertex in mesh.vertices:
                uvMap[vertex.index] = (self.mliq.VertexMap[vertex.index].u,
                                       self.mliq.VertexMap[vertex.index].v)

            uv1 = mesh.uv_textures.new("UVMap")
            uv_layer1 = mesh.uv_layers[0]

            for poly in mesh.polygons:
                for loop_index in poly.loop_indices:
                        uv_layer1.data[loop_index].uv = (uvMap.get(mesh.loops[loop_index].vertex_index)[0],
                                                         - uvMap.get(mesh.loops[loop_index].vertex_index)[1])

        # setting flags in a hacky way using vertex colors
        bit = 1
        while bit <= 0x80:
            vc_layer = mesh.vertex_colors.new("flag_" + hex(bit))
            for poly in mesh.polygons:
                tileFlag = self.mliq.TileFlags[poly.index]
                for loop in poly.loop_indices:
                    if tileFlag & bit:
                        vc_layer.data[loop].color = (0, 0, 255)
            bit <<= 1

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
        real_liquid_type = 0

        if root.mohd.Flags & 0x4:
            real_liquid_type = self.mogp.LiquidType
        else:
            real_liquid_type = self.FromWMOLiquidType(self.mogp.LiquidType)

        obj.WowLiquid.Color = root.materials[self.mliq.LiquidMaterial].WowMaterial.DiffColor
        obj.WowLiquid.LiquidType = str(real_liquid_type)
        obj.WowLiquid.WMOGroup = objName

    # Return faces indices
    def GetBSPNodeIndices(self, iNode, nodes, faces, indices):
        """ Get indices of a WMO BSP tree nodes """
        # last node in branch
        nodeIndices = []
        if nodes[iNode].PlaneType & BSP_PLANE_TYPE.Leaf:
            for i in range(nodes[iNode].FirstFace, nodes[iNode].FirstFace + nodes[iNode].NumFaces):
                nodeIndices.append(faces[i])

        if nodes[iNode].Childrens[0] != -1:
            nodeIndices.extend(self.GetBSPNodeIndices(nodes[iNode].Childrens[0], nodes, faces, indices))

        if nodes[iNode].Childrens[1] != -1:
            nodeIndices.extend(self.GetBSPNodeIndices(nodes[iNode].Childrens[1], nodes, faces, indices))

        return nodeIndices

    def GetCollisionIndices(self):
        """ Get indices of a WMO BSP tree nodes that have collision """
        nodeIndices = self.GetBSPNodeIndices(0, self.mobn.Nodes, self.mobr.Faces, self.movi.Indices)
        indices = []
        for i in nodeIndices:
            if not self.mopy.TriangleMaterials[i].Flags & 0x04:
                indices.append(self.movi.Indices[i * 3])
                indices.append(self.movi.Indices[i * 3 + 1])
                indices.append(self.movi.Indices[i * 3 + 2])

        return indices

    # Create mesh from file data
    def LoadObject(self, objName, objId, base_name, root, editable_doodads):
        """ Load WoW WMO group as an object to the Blender scene """
        vertices = []
        normals = []
        custom_normals = []
        faces = []

        texCoords = []
        vertColors = []

        vertices = self.movt.Vertices
        normals = self.monr.Normals
        texCoords = self.motv.TexCoords


        for i in range(0, len(self.movi.Indices), 3):
            faces.append(self.movi.Indices[i:i+3 ])

        # create mesh
        mesh = bpy.data.meshes.new(objName)
        mesh.from_pydata(vertices, [], faces)

        # create object
        scn = bpy.context.scene

        for o in scn.objects:
            o.select = False

        nobj = bpy.data.objects.new(objName, mesh)
        scn.objects.link(nobj)

        for poly in mesh.polygons:
            poly.use_smooth = True

        # set normals
        for i in range(len(normals)):
            mesh.vertices[i].normal = normals[i]

        mesh.use_auto_smooth = True
        for loop in mesh.loops:
            mesh.vertices[loop.vertex_index].normal = normals[loop.vertex_index]
            custom_normals.append(normals[loop.vertex_index])

        mesh.normals_split_custom_set(custom_normals)

        # set vertex color
        if self.mogp.Flags & MOGP_FLAG.HasVertexColor:
            flag_set = nobj.WowWMOGroup.Flags
            flag_set.add('0')
            nobj.WowWMOGroup.Flags = flag_set
            vertColor_layer1 = mesh.vertex_colors.new("Col")

            lightmap = nobj.vertex_groups.new("Lightmap")
            nobj.WowVertexInfo.Lightmap = lightmap.name
            lightmap.add(self.movi.Indices, 1.0, 'ADD')

            # loops and vertex_color are in the same order, so we use it to find vertex index
            for i in range(len(mesh.loops)):

                vertColor_layer1.data[i].color = (self.mocv.vertColors[mesh.loops[i].vertex_index][2] / 255,
                                                  self.mocv.vertColors[mesh.loops[i].vertex_index][1] / 255,
                                                  self.mocv.vertColors[mesh.loops[i].vertex_index][0] / 255)

                mesh.vertices[mesh.loops[i].vertex_index].groups[lightmap.index].weight \
                = self.mocv.vertColors[mesh.loops[i].vertex_index][3] / 255

        if self.mogp.Flags & MOGP_FLAG.HasTwoMOCV:
            blendmap = nobj.vertex_groups.new("Blendmap")
            nobj.WowVertexInfo.Blendmap = blendmap.name
            blendmap.add(self.movi.Indices, 1.0, 'ADD')

            for vertex in mesh.vertices:
                vertex.groups[blendmap.index].weight = self.mocv2.vertColors[vertex.index][3] / 255


        # set uv
        uv1 = mesh.uv_textures.new("UVMap")
        uv_layer1 = mesh.uv_layers[0]
        for i in range(len(uv_layer1.data)):
            uv = texCoords[mesh.loops[i].vertex_index]
            uv_layer1.data[i].uv = (uv[0], 1 - uv[1])

        if self.mogp.Flags & MOGP_FLAG.HasTwoMOTV:
            uv2 = mesh.uv_textures.new("UVMap_2")
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

        if self.mogp.nBatchesA != 0:
            batchMapA = nobj.vertex_groups.new("BatchMapA")
            nobj.WowVertexInfo.BatchTypeA = batchMapA.name
        if self.mogp.nBatchesB != 0:
            batchMapB = nobj.vertex_groups.new("BatchMapB")
            nobj.WowVertexInfo.BatchTypeB = batchMapB.name

        batch_material_map = {}

        # add materials
        for i in range(len(self.moba.Batches)):

            material = mesh.materials.get(root.materials[self.moba.Batches[i].MaterialID].name)

            if not material:
                mat_id = len(mesh.materials)
                material_indices[self.moba.Batches[i].MaterialID] = mat_id
                material = root.materials[self.moba.Batches[i].MaterialID]

                image = self.GetMaterialViewportImage(material)
                material_viewport_textures[mat_id] = image

                if not len(material.texture_slots) and image:
                    texture = bpy.data.textures.new(os.path.split(image.filepath)[1], 'IMAGE')
                    texture.image = image
                    texture_slot = material.texture_slots.add()
                    texture_slot.texture = texture

                mesh.materials.append(root.materials[self.moba.Batches[i].MaterialID])

                material.WowMaterial.Enabled = True


            if i < self.mogp.nBatchesA:
                batchMapA.add(self.movi.Indices[self.moba.Batches[i].StartTriangle : self.moba.Batches[i].StartTriangle + self.moba.Batches[i].nTriangle], 1.0, 'ADD')

            elif i < self.mogp.nBatchesA + self.mogp.nBatchesB:
                batchMapB.add(self.movi.Indices[self.moba.Batches[i].StartTriangle : self.moba.Batches[i].StartTriangle + self.moba.Batches[i].nTriangle], 1.0, 'ADD')

            batch_material_map[(self.moba.Batches[i].StartTriangle // 3, (self.moba.Batches[i].StartTriangle + self.moba.Batches[i].nTriangle) // 3)] = self.moba.Batches[i].MaterialID

        # add ghost material
        for i in self.mopy.TriangleMaterials:
            if i.MaterialID == 0xFF:
                mat_ghost_ID = len(mesh.materials)
                mesh.materials.append(root.materials[0xFF])
                material_viewport_textures[mat_ghost_ID] = None
                material_indices[0xFF] = mat_ghost_ID
                break

        # set faces material
        for i in range(len(mesh.polygons)):
            matID = self.mopy.TriangleMaterials[i].MaterialID

            mesh.polygons[i].material_index = material_indices[matID]

            # set texture displayed in viewport
            img = material_viewport_textures[material_indices[matID]]
            if img != None:
                uv1.data[i].image = img

        # set textured solid in all 3D views and switch to textured mode
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].show_textured_solid = True
                area.spaces[0].viewport_shade = 'TEXTURED'

        #DEBUG BSP
        """for iNode in range(len(self.mobn.Nodes)):
            bsp_node_indices = self.GetBSPNodeIndices(iNode, self.mobn.Nodes, self.mobr.Faces, self.movi.Indices)
            bsp_node_vg = nobj.vertex_groups.new("debug_bsp")

            #for i in bsp_n1_indices:
            #    bsp_n1_GroupIndices.append(i)

            bsp_node_vg.add(bsp_node_indices, 1.0, 'ADD')"""
        #DEBUG BSP

        # add collision vertex group
        collision_indices = self.GetCollisionIndices()

        if collision_indices:
            collision_vg = nobj.vertex_groups.new("Collision")
            collision_vg.add(collision_indices, 1.0, 'ADD')
            nobj.WowVertexInfo.VertexGroup = collision_vg.name

        # add WMO group properties
        nobj.WowWMOGroup.Enabled = True
        nobj.WowWMOGroup.GroupName = root.mogn.GetString(self.mogp.GroupNameOfs)
        nobj.WowWMOGroup.GroupDesc = root.mogn.GetString(self.mogp.DescGroupNameOfs)
        nobj.WowWMOGroup.GroupDBCid = int(self.mogp.GroupID)

        nobj.WowWMOGroup.Fog1 = base_name + "_Fog_" + str(self.mogp.FogIndices[0]).zfill(2)
        nobj.WowWMOGroup.Fog2 = base_name + "_Fog_" + str(self.mogp.FogIndices[1]).zfill(2)
        nobj.WowWMOGroup.Fog3 = base_name + "_Fog_" + str(self.mogp.FogIndices[2]).zfill(2)
        nobj.WowWMOGroup.Fog4 = base_name + "_Fog_" + str(self.mogp.FogIndices[3]).zfill(2)


        if self.mogp.Flags & MOGP_FLAG.HasWater:
            self.LoadLiquids(objName, nobj.location, root)

        else:
            # getting Liquid Type ID
            real_liquid_type = 0

            if root.mohd.Flags & 0x4:
                real_liquid_type = self.mogp.LiquidType
            else:
                real_liquid_type = self.FromWMOLiquidType(self.mogp.LiquidType)
                real_liquid_type = 0 if real_liquid_type == 17 else real_liquid_type

            nobj.WowWMOGroup.LiquidType = str(real_liquid_type)

        if not editable_doodads and self.mogp.Flags & MOGP_FLAG.HasDoodads:
            if self.modr.DoodadRefs:
                for i in range(len(self.modr.DoodadRefs)):
                    doodad = nobj.WowWMOGroup.MODR.add()
                    doodad.value = self.modr.DoodadRefs[i]

        if self.mogp.Flags & MOGP_FLAG.Indoor:
            nobj.WowWMOGroup.PlaceType = str(0x2000)
        else:
            nobj.WowWMOGroup.PlaceType = str(0x8)

        flag_set = nobj.WowWMOGroup.Flags

        if self.mogp.Flags & MOGP_FLAG.DoNotUseLocalLighting:
            flag_set.add('1')

        if self.mogp.Flags & MOGP_FLAG.AlwaysDraw:
            flag_set.add('2')

        if self.mogp.Flags & MOGP_FLAG.IsMountAllowed:
            flag_set.add('3')

        if self.mogp.Flags & MOGP_FLAG.HasSkybox:
            flag_set.add('4')

        nobj.WowWMOGroup.Flags = flag_set

        mesh.validate(clean_customdata=False)
        mesh.update()

        nobj.select = True

        if scn.objects.active is None or scn.objects.active.mode == 'OBJECT':
            scn.objects.active = nobj

        root.groupMap[objId] = nobj.name

    def GetPortalDirection(self, portal_obj, group, result_map, portal_relations):
        """ Get the direction of MOPR portal relation given a portal object and a target group """

        cur_relation = result_map.get(portal_obj)

        # check if this portal was already processed
        if not cur_relation:

            if portal_obj.WowPortalPlane.Algorithm == "0":

                # store the previous active object
                active_obj = bpy.context.scene.objects.active

                # create a portal proxy object to apply transformations
                proxy_obj = portal_obj.copy()
                proxy_obj.data = portal_obj.data.copy()
                bpy.context.scene.objects.link(proxy_obj)
                bpy.context.scene.objects.active = proxy_obj

                # reveal hidden geometry
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.reveal()
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')

                proxy_obj.select = True
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                proxy_obj.select = False

                # triangulate the proxy portal
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.quads_convert_to_tris()
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')

                mesh = group.data
                portal_mesh = proxy_obj.data
                normal  = proxy_obj.data.polygons[0].normal

                for poly in mesh.polygons:

                    poly_normal = mathutils.Vector(poly.normal)
                    g_center = poly.center + poly_normal * sys.float_info.epsilon


                    dist = normal[0] * g_center[0] + normal[1] * g_center[1]
                    + normal[2] * g_center[2] - portal_mesh.polygons[0].normal[0] \
                    * portal_mesh.vertices[portal_mesh.polygons[0].vertices[0]].co[0]
                    - portal_mesh.polygons[0].normal[1] * portal_mesh.vertices[portal_mesh.polygons[0].vertices[0]].co[1]
                    - portal_mesh.polygons[0].normal[2] * portal_mesh.vertices[portal_mesh.polygons[0].vertices[0]].co[2]

                    if dist == 0:
                        continue

                    for portal_poly in portal_mesh.polygons:

                        direction = portal_poly.center - g_center
                        length = mathutils.Vector(direction).length
                        direction.normalize()

                        angle = mathutils.Vector(direction).angle(poly.normal, None)

                        if angle is None or angle >= pi * 0.5:
                            continue

                        ray_cast_result = bpy.context.scene.ray_cast(g_center, direction)

                        if not ray_cast_result[0] \
                        or ray_cast_result[4].name == portal_obj.name \
                        or ray_cast_result[4].name == proxy_obj.name \
                        or mathutils.Vector((ray_cast_result[1][0] - g_center[0], ray_cast_result[1][1] - g_center[1], ray_cast_result[1][2] - g_center[2])).length > \
                        length:
                            result = 1 if dist > 0 else -1

                            for portalRef in portal_relations:
                                if portalRef[0] == portal_obj.WowPortalPlane.PortalID:
                                    portalRef[2] = -result
                                    break

                            result_map[portal_obj] = result

                            bpy.data.objects.remove(proxy_obj, do_unlink = True)
                            bpy.context.scene.objects.active = active_obj
                            return result

                bpy.data.objects.remove(proxy_obj, do_unlink = True)
                bpy.context.scene.objects.active = active_obj
                result_map[portal_obj] = 0
                LogDebug(0,
                         False,
                         "WARNING: Failed to calculate portal direction. Calculation from another side may be attempted."
                         )
                return 0

            else:
                result = 1 if portal_obj.WowPortalPlane.Algorithm == "1" else -1
                result_map[portal_obj] = result
                return result

        else:
            return -cur_relation

    def SaveLiquid(self, ob, root):

        Log(1, False, "Exporting liquid: <<" + ob.name + ">>")

        mesh = ob.data

        # apply mesh transformations
        active = bpy.context.scene.objects.active
        bpy.context.scene.objects.active = ob
        ob.select = True
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        ob.select = False
        bpy.context.scene.objects.active = active

        StartVertex = 0
        sum = 0
        for vertex in mesh.vertices:
            curSum = vertex.co[0] + vertex.co[1]

            if (curSum < sum):
                StartVertex = vertex.index
                sum = curSum

        self.mliq.xTiles = round(ob.dimensions[0] / 4.1666625)
        self.mliq.yTiles = round(ob.dimensions[1] / 4.1666625)
        self.mliq.xVerts = self.mliq.xTiles + 1
        self.mliq.yVerts = self.mliq.yTiles + 1
        self.mliq.Position = mesh.vertices[StartVertex].co

        self.mogp.Flags |= 0x1000 # do we really need that?
        self.mogp.LiquidType = int(ob.WowLiquid.LiquidType)

        # creating liquid material

        material = bpy.data.materials.new(ob.name)
        material.WowMaterial.Enabled = True
        material.WowMaterial.Color2 = ob.WowLiquid.Color

        types_1 = {3, 7, 11}
        types_2 = {4, 8, 12}

        material.WowMaterial.Texture1 = "DUNGEONS\TEXTURES\STORMWIND\GRAY12.BLP"

        if self.mogp.LiquidType in types_1:
            material.WowMaterial.Texture1 = "DUNGEONS\TEXTURES\METAL\BM_BRSPIRE_CATWALK01.BLP"

        elif self.mogp.LiquidType in types_2:
            material.WowMaterial.Texture1 = "DUNGEONS\TEXTURES\FLOOR\JLO_UNDEADZIGG_SLIMEFLOOR.BLP"

        self.mliq.materialID = root.AddMaterial(material)


        if self.mogp.LiquidType in types_1 or self.mogp.LiquidType in types_2:

            if mesh.uv_layers.active:

                uvMap = {}

                for poly in mesh.polygons:
                    for loop_index in poly.loop_indices:
                        if mesh.loops[loop_index].vertex_index not in uvMap:
                            uvMap[mesh.loops[loop_index].vertex_index] = mesh.uv_layers.active.data[loop_index].uv

                for i in range(self.mliq.xVerts * self.mliq.yVerts):
                    vertex = MagmaVertex()

                    vertex.u = int( uvMap.get(mesh.vertices[i].index)[0])
                    vertex.v = int( uvMap.get(mesh.vertices[i].index)[1])

                    vertex.height = mesh.vertices[i].co[2]
                    self.mliq.VertexMap.append(vertex)
            else:

                LogError(2, "Slime and magma (lava) liquids require a UV map to be created.")

        else:

            for j in range(self.mliq.xVerts * self.mliq.yVerts):
                vertex = WaterVertex()

                vertex.height = mesh.vertices[j].co[2]
                self.mliq.VertexMap.append(vertex)

        for poly in mesh.polygons:
                tile_flag = 0
                blue = [0.0, 0.0, 1.0]

                bit = 1
                while bit <= 0x80:
                    vc_layer = mesh.vertex_colors["flag_" + hex(bit)]

                    if self.CompColors(vc_layer.data[poly.loop_indices[0]].color, blue):
                        tile_flag |= bit
                    bit <<= 1

                self.mliq.TileFlags.append(tile_flag)

        Log(0, False, "Done exporting liquid: <<" + ob.name + ">>")
        return True

    def SavePortalRelations(self, new_obj, obj, ob, root):
        obj_mesh = ob.data

        # save portal relations and MOGP indexing data
        if ob.WowPortalPlane.Enabled \
        and (ob.WowPortalPlane.First == obj.name \
        or ob.WowPortalPlane.Second == obj.name):
            Log(1,
                False,
                "Building portal relation between: <<" + ob.name + ">> (portal) and <<"
                + obj.name + ">> (group)"
                )

            objects = bpy.context.scene.objects

            first = ob.WowPortalPlane.First
            second = ob.WowPortalPlane.Second

            first_id = objects[first].WowWMOGroup.GroupID if first else None
            second_id =  objects[second].WowWMOGroup.GroupID if second else None

            portalRef = [0, 0, 1]

            portalRef[0] = ob.WowPortalPlane.PortalID

            if first == obj.name:
                portalRef[1] = second_id if second else first_id
            else:
                portalRef[1] = first_id if first else second_id

            portalRef[2] = self.GetPortalDirection(ob, new_obj, root.portalDirectionMap, root.PortalR)

            root.PortalR.append(portalRef)
            self.mogp.PortalCount += 1

            Log(0,
                False,
                "Done building portal relation between: <<" + ob.name + ">> (portal) and <<"
                + obj.name + ">> (group)"
                )

    def Save(self, obj, root, objNumber, autofill_textures, group_filename):
        """ Save WoW WMO group data for future export """
        Log(1, False, "Saving group: <<" + obj.name + ">>")
        self.filename = group_filename

        bpy.context.scene.objects.active = obj

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        try:

            new_obj = obj.copy()
            new_obj.data = obj.data.copy()
            bpy.context.scene.objects.link(new_obj)
            bpy.context.scene.objects.active = new_obj

            mesh = new_obj.data
            original_mesh = obj.data

            # apply all modifiers. Needs to optional.
            if len(new_obj.modifiers):
                for modifier in new_obj.modifiers:
                    bpy.ops.object.modifier_apply(modifier=modifier.name)

            # triangualate mesh
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.quads_convert_to_tris()
            bpy.ops.mesh.delete_loose()
            bpy.ops.mesh.select_all(action='DESELECT')

            # perform edge split.
            bpy.ops.uv.select_all(action='SELECT')
            bpy.ops.uv.seams_from_islands(mark_seams=False, mark_sharp=True)
            bpy.ops.object.mode_set(mode='OBJECT')

            bpy.ops.object.modifier_add(type='EDGE_SPLIT')
            bpy.context.object.modifiers["EdgeSplit"].use_edge_angle = False
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="EdgeSplit")

            # apply object transformation to geometry. Needs to be optional.
            new_obj.select = True
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            new_obj.select = False

            # perform vertex group split to keep batches accurate.
            bpy.ops.object.mode_set(mode='EDIT')
            if new_obj.WowVertexInfo.BatchTypeA != "":
                bpy.ops.object.vertex_group_set_active(group=new_obj.WowVertexInfo.BatchTypeA)
                bpy.ops.object.vertex_group_select()
                bpy.ops.mesh.split()
                bpy.ops.mesh.select_all(action='DESELECT')

            if new_obj.WowVertexInfo.BatchTypeB != "":
                bpy.ops.object.vertex_group_set_active(group=new_obj.WowVertexInfo.BatchTypeB)
                bpy.ops.object.vertex_group_select()
                bpy.ops.mesh.split()
                bpy.ops.mesh.select_all(action='DESELECT')

            bpy.ops.object.mode_set(mode='OBJECT')

            if not original_mesh.has_custom_normals:

                # perform custom normal data calculation if not yet calculated by the user
                bpy.context.scene.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')

                original_mesh.use_auto_smooth = True
                bpy.ops.mesh.customdata_custom_splitnormals_add()
                original_mesh.calc_normals_split()

                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')

                # perform custom normal data transfer to a temporary object
                obj.select = True
                new_obj.select = True
                bpy.context.scene.objects.active = new_obj
                bpy.ops.object.data_transfer(use_reverse_transfer=True, data_type='CUSTOM_NORMAL')
                new_obj.select = False
                obj.select = False

                # clear auto-generated custom normal data on original scene object to avoid changes of original scene on export. If normals are user defined, we do not touch them.
                bpy.context.scene.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.customdata_custom_splitnormals_clear()
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.context.scene.objects.active = new_obj

            else:
                mesh.calc_normals_split()

            # doing safety checks
            if len(mesh.vertices) > 65535:
                LogError(2,
                        "Object "
                        + str(obj.name)
                        + " contains more vertices ("
                        + str(len(mesh.vertices))
                        + ") than it is supported.  Maximum amount of vertices you can use per one object is 65535."
                        )

            if len(root.momt.Materials) > 256:
                LogError(2,
                        "Scene has excceeded the maximum allowed number of WoW materials (255). Your scene now has <<",
                        len(root.momt.Materials),
                        ">> materials. So, <<",
                        (len(root.momt.Materials) - 256),
                        ">> extra ones."
                        )

            self.mver = MVER_chunk()
            self.mver.Version = 17

            self.mogp = MOGP_chunk()

            material_indices = {}

            if autofill_textures:
                new_obj.select = True
                bpy.ops.scene.wow_fill_textures()
                new_obj.select = False

            for i in range(len(mesh.materials)):
                material_indices[i] = root.AddMaterial(mesh.materials[i]) # adding materials to root object. Returns the index of material if the passed one already exists.

            polyBatchMap = {}

            vg_batch_a = None
            vg_batch_b = None
            vg_collision = None
            vg_lightmap = None
            vg_blendmap = None
            uv_second_uv = None
            vg_attenuation = None


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

            if new_obj.WowVertexInfo.Blendmap != "":
                vg_blendmap = new_obj.vertex_groups.get(new_obj.WowVertexInfo.Blendmap)
                self.mogp.Flags |= MOGP_FLAG.HasTwoMOCV

            if new_obj.WowVertexInfo.SecondUV != "":
                uv_second_uv = new_obj.data.uv_textures.get(new_obj.WowVertexInfo.SecondUV)
                self.mogp.Flags |= MOGP_FLAG.HasTwoMOTV

            for poly in mesh.polygons:
                polyBatchMap.setdefault( (material_indices.get(poly.material_index), self.GetBatchType(poly, mesh, vg_batch_a.index, vg_batch_b.index)), [] ).append(poly.index)

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

            self.movi = MOVI_chunk()
            self.mopy = MOPY_chunk()
            self.moba = MOBA_chunk(nBatchesA + nBatchesB + nBatchesC)

            self.movt = MOVT_chunk(vertex_size)
            self.monr = MONR_chunk(vertex_size)
            self.motv = MOTV_chunk(vertex_size)
            self.motv2 = MOTV_chunk(vertex_size)
            self.mocv = MOCV_chunk(vertex_size)
            self.mocv2 = MOCV_chunk(vertex_size)


            vertexMap = {}
            normalMap = {}
            batchMap = {}

            new_index_last = 0

            # write geometry data and batches
            batch_counter_a = 0
            batch_counter_b = 0
            batch_counter_c = 0

            for batchKey, polyBatch in polyBatchMap.items():

                firstIndex = len(self.movi.Indices)

                sentryIndices = [0xFFFF, 0x00]

                for poly in polyBatch:
                    collision_counter = 0

                    for vertex_index in mesh.polygons[poly].vertices:

                        new_index_current = vertexMap.get(vertex_index)

                        if new_index_current == None:
                            vertexMap[vertex_index] = new_index_last
                            new_index_current = new_index_last
                            new_index_last += 1
                            self.movt.Vertices[new_index_current] = mesh.vertices[vertex_index].co

                        sentryIndices[0] = self.ret_min(sentryIndices[0], new_index_current)
                        sentryIndices[1] = self.ret_max(sentryIndices[1], new_index_current)

                        self.movi.Indices.append(new_index_current)


                        if vg_collision != None:
                            for group_info in mesh.vertices[vertex_index].groups:
                                if group_info.group == vg_collision.index:
                                    collision_counter += 1

                    tri_mat = TriangleMaterial()
                    tri_mat.MaterialID = batchKey[0]
                    tri_mat.Flags = 0x0 if tri_mat.MaterialID == 0xFF else 0x20
                    tri_mat.Flags |= 0x40 if collision_counter == len(mesh.polygons[poly].vertices) else 0x4 | 0x8

                    for loop_index in mesh.polygons[poly].loop_indices:

                        new_index = vertexMap.get(mesh.loops[loop_index].vertex_index)
                        vertex = mesh.vertices[mesh.loops[loop_index].vertex_index]

                        if len(mesh.uv_layers) > 0:
                            self.motv.TexCoords[new_index] = (mesh.uv_layers.active.data[loop_index].uv[0],
                                                                1.0 - mesh.uv_layers.active.data[loop_index].uv[1])

                        if uv_second_uv:
                            self.motv2.TexCoords[new_index] = (mesh.uv_layers[uv_second_uv.name].data[loop_index].uv[0],
                                                                1.0 - mesh.uv_layers[uv_second_uv.name].data[loop_index].uv[1])


                        if '0' in new_obj.WowWMOGroup.Flags \
                        or (new_obj.WowWMOGroup.PlaceType == '8192' and not '1' in new_obj.WowWMOGroup.Flags):
                            if len(mesh.vertex_colors):
                                vertex_color = [0x7F, 0x7F, 0x7F, 0x00]

                                for i in range(0, 3):
                                    vertex_color[i] = round(mesh.vertex_colors.active.data[loop_index].color[3 - i - 1] * 255)

                                if vg_lightmap:
                                    for vertex_group_element in vertex.groups:
                                        if vertex_group_element.group == vg_lightmap.index:
                                            weight = round(vertex_group_element.weight * 255)
                                            vertex_color[3] = weight if weight > 0 else 0x00
                                            if weight > 0:
                                                tri_mat.Flags |= 0x1

                                self.mocv.vertColors[new_index] = vertex_color

                            else:
                                if batchKey == 2:
                                    self.mocv.vertColors[new_index] = [0x7F, 0x7F, 0x7F, 0x00]
                                else:
                                    self.mocv.vertColors[new_index] = [0x7F, 0x7F, 0x7F, 0xFF]

                        if vg_blendmap != None:
                            for vertex_group_element in vertex.groups:
                                        if vertex_group_element.group == vg_blendmap.index:
                                            weight = round(vertex.groups[vg_blendmap.index].weight * 255)
                                            self.mocv2.vertColors[new_index] = (0,
                                                                                0,
                                                                                0,
                                                                                weight if weight > 0 else 0x00)

                        normalMap.setdefault(new_index, []).append(mesh.loops[loop_index].normal)

                    self.mopy.TriangleMaterials.append(tri_mat)

                nIndices = len(self.movi.Indices) - firstIndex

                BoundingBox = [32767, 32767, 32767, -32768, -32768, -32768]

                for poly in polyBatch:
                    for vertex_index in mesh.polygons[poly].vertices:
                        new_index = vertexMap.get(vertex_index)
                        self.monr.Normals[new_index] = self.GetAvg(normalMap.get(new_index))

                        for i in range(0, 2):
                            for j in range(0, 3):
                                idx = i * 3 + j
                                BoundingBox[idx] = self.ret_min(BoundingBox[idx], floor(self.movt.Vertices[new_index][j])) if i == 0 \
                                else self.ret_max(BoundingBox[idx], ceil(self.movt.Vertices[new_index][j]))

                # skip batch writing if processed polyBatch is collision
                if batchKey[0] == 0xFF:
                    continue

                # write current batch
                batch = Batch()

                batch.BoundingBox = BoundingBox

                batch.StartTriangle = firstIndex
                batch.nTriangle = nIndices

                batch.StartVertex = sentryIndices[0]
                batch.LastVertex = sentryIndices[1]

                batch.MaterialID = batchKey[0]

                # sort and write batches
                if batchKey[1] == 0:
                    self.moba.Batches[batch_counter_a] = batch
                    batch_counter_a += 1
                elif batchKey[1] == 1:
                    self.moba.Batches[nBatchesA + batch_counter_b] = batch
                    batch_counter_b += 1
                else:
                    self.moba.Batches[nBatchesA + nBatchesB + batch_counter_c] = batch
                    batch_counter_c += 1


            # write BSP nodes
            self.mobn = MOBN_chunk()

            # write BSP faces
            self.mobr = MOBR_chunk()

            # write header
            self.mogp.BoundingBoxCorner1 = [32767, 32767, 32767]
            self.mogp.BoundingBoxCorner2 = [-32768, -32768, -32768]

            for vtx in self.movt.Vertices:
                for i in range(0, 3):
                    self.mogp.BoundingBoxCorner1[i] = self.ret_min(self.mogp.BoundingBoxCorner1[i], floor(vtx[i]))
                    self.mogp.BoundingBoxCorner2[i] = self.ret_max(self.mogp.BoundingBoxCorner2[i], ceil(vtx[i]))


            self.mogp.Flags |= MOGP_FLAG.HasCollision # /!\ MUST HAVE 0x1 FLAG ELSE THE GAME CRASH !
            if '0' in new_obj.WowWMOGroup.Flags:
                self.mogp.Flags |= MOGP_FLAG.HasVertexColor
            if '4' in new_obj.WowWMOGroup.Flags:
                self.mogp.Flags |= MOGP_FLAG.HasSkybox
            if '1' in new_obj.WowWMOGroup.Flags:
                self.mogp.Flags |= MOGP_FLAG.DoNotUseLocalLighting
            if '2' in new_obj.WowWMOGroup.Flags:
                self.mogp.Flags |= MOGP_FLAG.AlwaysDraw
            if '3' in new_obj.WowWMOGroup.Flags:
                self.mogp.Flags |= MOGP_FLAG.IsMountAllowed

            self.mogp.Flags |= int(new_obj.WowWMOGroup.PlaceType)
            root.mohd.Flags |= 0x4

            self.mogp.PortalStart = root.PortalRCount
            self.mogp.PortalCount = 0

            hasWater = False
            hasLights = False
            light_counter = 0

            self.molr = MOLR_chunk()
            self.mliq = MLIQ_chunk()

            fogs = (obj.WowWMOGroup.Fog1,
                    obj.WowWMOGroup.Fog2,
                    obj.WowWMOGroup.Fog3,
                    obj.WowWMOGroup.Fog4)

            liquid = obj.WowWMOGroup.Relations.Liquid
            portal_relations = obj.WowWMOGroup.Relations.Portals
            lamps = obj.WowWMOGroup.Relations.Lights

            objects = bpy.context.scene.objects

            # set fog references
            self.mogp.FogIndices = (objects[fogs[0]].WowFog.FogID if fogs[0] else 0,
                                    objects[fogs[1]].WowFog.FogID if fogs[0] else 0,
                                    objects[fogs[2]].WowFog.FogID if fogs[0] else 0,
                                    objects[fogs[3]].WowFog.FogID if fogs[0] else 0,
                                    )

            # save liquid
            if liquid:
                hasWater = self.SaveLiquid(objects[liquid], root)

            # save lamps
            if lamps:
                hasLights = True
                for lamp in lamps:
                    self.molr.LightRefs.append(lamp.id)

            # save portal relations
            for relation in portal_relations:
                self.SavePortalRelations(new_obj, obj, objects[relation.id], root)

            root.PortalRCount += self.mogp.PortalCount
            self.mogp.nBatchesA = nBatchesA
            self.mogp.nBatchesB = nBatchesB
            self.mogp.nBatchesC = nBatchesC
            self.mogp.nBatchesD = 0
            self.mogp.GroupID = int(new_obj.WowWMOGroup.GroupDBCid)
            self.mogp.Unknown1 = 0
            self.mogp.Unknown2 = 0

            groupInfo = root.AddGroupInfo(self.mogp.Flags,
                                            [self.mogp.BoundingBoxCorner1,
                                            self.mogp.BoundingBoxCorner2],
                                            new_obj.WowWMOGroup.GroupName,
                                            new_obj.WowWMOGroup.GroupDesc)

            self.mogp.GroupNameOfs = groupInfo[0]
            self.mogp.DescGroupNameOfs = groupInfo[1]

            if len(new_obj.WowWMOGroup.MODR):
                self.modr = MODR_chunk()
                for doodad in new_obj.WowWMOGroup.MODR:
                    self.modr.DoodadRefs.append(doodad.value)
                self.mogp.Flags |= MOGP_FLAG.HasDoodads
            elif new_obj.WowWMOGroup.Relations.Doodads:
                self.modr = MODR_chunk()
                for doodad in new_obj.WowWMOGroup.Relations.Doodads:
                    self.modr.DoodadRefs.append(doodad.id)
                self.mogp.Flags |= MOGP_FLAG.HasDoodads
            else:
                self.modr = None

            bsp_tree = BSP_Tree()
            bsp_tree.GenerateBSP(self.movt.Vertices, self.movi.Indices, new_obj.WowVertexInfo.NodeSize)

            self.mobn.Nodes = bsp_tree.Nodes
            self.mobr.Faces = bsp_tree.Faces

            if '0' not in new_obj.WowWMOGroup.Flags:
                if new_obj.WowWMOGroup.PlaceType == '8192':
                    if '1' in new_obj.WowWMOGroup.Flags \
                    and not len(mesh.vertex_colors):
                        self.mocv = None
                    else:
                        self.mogp.Flags |= MOGP_FLAG.HasVertexColor
                else:
                    self.mocv = None

            if not hasWater:
                self.mliq = None
                self.mogp.Flags |= MOGP_FLAG.IsNotOcean # check if this is necessary
                root.mohd.Flags |= 0x4
                self.mogp.LiquidType = int(obj.WowWMOGroup.LiquidType)

            if not hasLights:
                self.molr = None
            else:
                self.mogp.Flags |= MOGP_FLAG.HasLight

            # write second MOTV and MOCV
            if uv_second_uv == None:
                self.motv2 = None

            if vg_blendmap == None:
                self.mocv2 = None

        except Exception as e:

            Log(0, False, "Failed saving group: <<" + str(obj.name) + ">>")
            raise e

        else:

            Log(0, False, "Done saving group: <<" + str(obj.name) + ">>")

        finally:

            bpy.data.objects.remove(new_obj, do_unlink = True)

            bpy.context.scene.objects.active = obj


    def Write(self):
        """ Write a saved WoW WMO group to a file """
        Log(1, False, "Writing file: <<" +  os.path.basename(self.filename) + ">>")

        f = open(self.filename, "wb")

        self.mver.Write(f)

        f.seek(0x58)
        self.mopy.Write(f)
        self.movi.Write(f)
        self.movt.Write(f)
        self.monr.Write(f)
        self.motv.Write(f)
        self.moba.Write(f)

        if self.molr:
            self.molr.Write(f)

        if self.modr:
            self.modr.Write(f)

        self.mobn.Write(f)
        self.mobr.Write(f)

        if self.mocv:
            self.mocv.Write(f)

        if self.mliq:
            self.mliq.Write(f)

        if self.motv2:
            self.motv2.Write(f)

        if self.mocv2:
            self.mocv2.Write(f)

        # get file size
        f.seek(0, 2)
        self.mogp.Header.Size = f.tell() - 20

        # write header
        f.seek(0xC)
        self.mogp.Write(f)


        Log(0, False, "Done writing file: <<" + os.path.basename(self.filename) + ">>")