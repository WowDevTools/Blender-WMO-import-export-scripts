from .wmo_format import *
from .bsp_tree import *
from .collision import *

import math
from math import *

import os
import sys
import mathutils


class WMOGroupFile:
    def __init__(self, root):

        self.root = root

        self.mver = MVER_chunk()
        self.mogp = MOGP_chunk()
        self.mopy = MOPY_chunk()
        self.movi = MOVI_chunk()
        self.movt = MOVT_chunk()
        self.monr = MONR_chunk()
        self.motv = MOTV_chunk()
        self.moba = MOBA_chunk()
        self.molr = MOLR_chunk()
        self.modr = MODR_chunk()
        self.mobn = MOBN_chunk()
        self.mobr = MOBR_chunk()
        self.mocv = MOCV_chunk()
        self.mliq = MLIQ_chunk()
        self.motv2 = MOTV_chunk()
        self.mocv2 = MOCV_chunk()

    def read(self, f):
        """ Read WoW WMO group file """

        self.mver.read(f)
        self.mogp.read(f)
        self.mopy.read(f)
        self.movi.read(f)
        self.movt.read(f)
        self.monr.read(f)
        self.motv.read(f)
        self.moba.read(f)

        if self.mogp.Flags & MOGP_FLAG.HasLight:
            self.molr.read(f)

        if self.mogp.Flags & MOGP_FLAG.HasDoodads:
            self.modr.read(f)

        if self.mogp.Flags & MOGP_FLAG.HasCollision:
            self.mobn.read(f)
            self.mobr.read(f)

        if self.mogp.Flags & MOGP_FLAG.HasVertexColor:
            self.mocv.read(f)

        if self.mogp.Flags & MOGP_FLAG.HasWater:
            if self.mogp.LiquidType in {3, 4, 7, 8, 11, 12}:
                self.mliq.LiquidMaterial = False
            self.mliq.read(f)

        if self.mogp.Flags & MOGP_FLAG.HasTwoMOTV:
            self.motv2.read(f)

        if self.mogp.Flags & MOGP_FLAG.HasTwoMOCV:
            self.mocv2.read(f)

    def write(self, f):
        """ Write a saved WoW WMO group to a file """
        print("\nWriting file: <<" +  os.path.basename(f.name) + ">>")

        self.mver.write(f)

        f.seek(0x58)
        self.mopy.write(f)
        self.movi.write(f)
        self.movt.write(f)
        self.monr.write(f)
        self.motv.write(f)
        self.moba.write(f)

        if self.molr:
            self.molr.write(f)

        if self.modr:
            self.modr.write(f)

        self.mobn.write(f)
        self.mobr.write(f)

        if self.mocv:
            self.mocv.write(f)

        if self.mliq:
            self.mliq.write(f)

        if self.motv2:
            self.motv2.write(f)

        if self.mocv2:
            self.mocv2.write(f)

        # get file size
        f.seek(0, 2)
        self.mogp.Header.Size = f.tell() - 20

        # write header
        f.seek(0xC)
        self.mogp.write(f)

    @staticmethod
    def get_avg(list):
        """ Get single average normal vector from a split normal """
        normal = [0.0, 0.0, 0.0]

        for n in list:
            for i in range(0, 3):
                normal[i] += n[i]

        for i in range(0, 3):
            normal[i] /= len(list)

        return normal

    @staticmethod
    def comp_colors(color1, color2):
        """ Compare two colors """

        for i in range(0, 3):
            if color1[i] != color2[i]:
                return False
        return True

    @staticmethod
    def get_batch_type(polygon, mesh, vg_index_a, vg_index_b):
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

    def get_material_viewport_image(self, material):
        """ Get viewport image assigned to a material """
        for i in range(3):
            try:
                img = material.texture_slots[3 - i].texture.image
                return img
            except:
                pass
        return None

    def from_wmo_liquid_type(self, basic_liquid_type):
        """ Convert simplified WMO liquid type IDs to real LiquidType.dbc IDs """
        real_liquid_type = 0

        if basic_liquid_type < 20:
            if basic_liquid_type == 0:
                real_liquid_type = 14 if self.mogp.Flags & 0x80000 else 13
            elif basic_liquid_type == 1:
                real_liquid_type = 14
            elif basic_liquid_type == 2:
                real_liquid_type = 19
            elif basic_liquid_type == 15:
                real_liquid_type = 17
            elif basic_liquid_type == 3:
                real_liquid_type = 20
        else:
            real_liquid_type = basic_liquid_type + 1

        return real_liquid_type

    # return array of vertice and array of faces in a tuple
    def load_liquids(self, group_name, pos):
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
        name = group_name + "_Liquid"
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

        if self.root.mohd.Flags & 0x4:
            real_liquid_type = self.mogp.LiquidType
        else:
            real_liquid_type = self.from_wmo_liquid_type(self.mogp.LiquidType)

        obj.WowLiquid.Color = self.root.material_lookup[self.mliq.materialID].WowMaterial.DiffColor
        obj.WowLiquid.LiquidType = str(real_liquid_type)
        obj.WowLiquid.WMOGroup = group_name

        if self.root.parent:
            obj.parent = self.root.parent

    # Return faces indices
    def get_bsp_node_indices(self, i_node, nodes, faces, indices):
        """ Get indices of a WMO BSP tree nodes """
        # last node in branch
        node_indices = []
        if nodes[i_node].PlaneType & BSP_PLANE_TYPE.Leaf:
            for i in range(nodes[i_node].FirstFace, nodes[i_node].FirstFace + nodes[i_node].NumFaces):
                node_indices.append(faces[i])

        if nodes[i_node].Children[0] != -1:
            node_indices.extend(self.get_bsp_node_indices(nodes[i_node].Children[0], nodes, faces, indices))

        if nodes[i_node].Children[1] != -1:
            node_indices.extend(self.get_bsp_node_indices(nodes[i_node].Children[1], nodes, faces, indices))

        return node_indices

    def get_collision_indices(self):
        """ Get indices of a WMO BSP tree nodes that have collision """
        node_indices = self.get_bsp_node_indices(0, self.mobn.Nodes, self.mobr.Faces, self.movi.Indices)
        indices = []
        for i in node_indices:
            if not self.mopy.TriangleMaterials[i].Flags & 0x04:
                indices.append(self.movi.Indices[i * 3])
                indices.append(self.movi.Indices[i * 3 + 1])
                indices.append(self.movi.Indices[i * 3 + 2])

        return indices

    # Create mesh from file data
    def load_object(self, obj_name, editable_doodads):
        """ Load WoW WMO group as an object to the Blender scene """
        custom_normals = []
        faces = []

        vertices = self.movt.Vertices
        normals = self.monr.Normals
        tex_coords = self.motv.TexCoords

        for i in range(0, len(self.movi.Indices), 3):
            faces.append(self.movi.Indices[i:i+3])

        # create mesh
        mesh = bpy.data.meshes.new(obj_name)
        mesh.from_pydata(vertices, [], faces)

        # create object
        scn = bpy.context.scene

        for o in scn.objects:
            o.select = False

        nobj = bpy.data.objects.new(obj_name, mesh)
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
            vert_color_layer1 = mesh.vertex_colors.new("Col")

            lightmap = nobj.vertex_groups.new("Lightmap")
            nobj.WowVertexInfo.Lightmap = lightmap.name
            lightmap.add(self.movi.Indices, 1.0, 'ADD')

            # loops and vertex_color are in the same order, so we use it to find vertex index
            for i in range(len(mesh.loops)):

                vert_color_layer1.data[i].color = (self.mocv.vertColors[mesh.loops[i].vertex_index][2] / 255,
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
            uv = tex_coords[mesh.loops[i].vertex_index]
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

        batch_map_a = None
        batch_map_b = None

        if self.mogp.nBatchesA != 0:
            batch_map_a = nobj.vertex_groups.new("BatchMapA")
            nobj.WowVertexInfo.BatchTypeA = batch_map_a.name
        if self.mogp.nBatchesB != 0:
            batch_map_b = nobj.vertex_groups.new("BatchMapB")
            nobj.WowVertexInfo.BatchTypeB = batch_map_b.name

        batch_material_map = {}

        # add materials
        for i in range(len(self.moba.Batches)):

            material = mesh.materials.get(self.root.material_lookup[self.moba.Batches[i].MaterialID].name)

            if not material:
                mat_id = len(mesh.materials)
                material_indices[self.moba.Batches[i].MaterialID] = mat_id
                material = self.root.material_lookup[self.moba.Batches[i].MaterialID]

                image = self.get_material_viewport_image(material)
                material_viewport_textures[mat_id] = image

                if not len(material.texture_slots) and image:
                    texture = bpy.data.textures.new(os.path.split(image.filepath)[1], 'IMAGE')
                    texture.image = image
                    texture_slot = material.texture_slots.add()
                    texture_slot.texture = texture

                mesh.materials.append(self.root.material_lookup[self.moba.Batches[i].MaterialID])

                material.WowMaterial.Enabled = True

            if i < self.mogp.nBatchesA:
                batch_map_a.add(self.movi.Indices[self.moba.Batches[i].StartTriangle
                              : self.moba.Batches[i].StartTriangle + self.moba.Batches[i].nTriangle], 1.0, 'ADD')

            elif i < self.mogp.nBatchesA + self.mogp.nBatchesB:
                batch_map_b.add(self.movi.Indices[self.moba.Batches[i].StartTriangle
                              : self.moba.Batches[i].StartTriangle + self.moba.Batches[i].nTriangle], 1.0, 'ADD')

            batch_material_map[(self.moba.Batches[i].StartTriangle // 3, (self.moba.Batches[i].StartTriangle + self.moba.Batches[i].nTriangle) // 3)] = self.moba.Batches[i].MaterialID

        # add ghost material
        for i in self.mopy.TriangleMaterials:
            if i.MaterialID == 0xFF:
                mat_ghost__id = len(mesh.materials)
                mesh.materials.append(self.root.material_lookup[0xFF])
                material_viewport_textures[mat_ghost__id] = None
                material_indices[0xFF] = mat_ghost__id
                break

        # set faces material
        for i in range(len(mesh.polygons)):
            mat_id = self.mopy.TriangleMaterials[i].MaterialID

            mesh.polygons[i].material_index = material_indices[mat_id]

            # set texture displayed in viewport
            img = material_viewport_textures[material_indices[mat_id]]
            if img is not None:
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
        collision_indices = self.get_collision_indices()

        if collision_indices:
            collision_vg = nobj.vertex_groups.new("Collision")
            collision_vg.add(collision_indices, 1.0, 'ADD')
            nobj.WowVertexInfo.VertexGroup = collision_vg.name

        # add WMO group properties
        nobj.WowWMOGroup.Enabled = True
        nobj.WowWMOGroup.GroupDesc = self.root.mogn.get_string(self.mogp.DescGroupNameOfs)
        nobj.WowWMOGroup.GroupDBCid = int(self.mogp.GroupID)

        nobj.WowWMOGroup.Fog1 = self.root.display_name + "_Fog_" + str(self.mogp.FogIndices[0]).zfill(2)
        nobj.WowWMOGroup.Fog2 = self.root.display_name + "_Fog_" + str(self.mogp.FogIndices[1]).zfill(2)
        nobj.WowWMOGroup.Fog3 = self.root.display_name + "_Fog_" + str(self.mogp.FogIndices[2]).zfill(2)
        nobj.WowWMOGroup.Fog4 = self.root.display_name + "_Fog_" + str(self.mogp.FogIndices[3]).zfill(2)

        if self.mogp.Flags & MOGP_FLAG.HasWater:
            self.load_liquids(obj_name, nobj.location)

        else:
            # getting Liquid Type ID
            real_liquid_type = 0

            if self.root.mohd.Flags & 0x4:
                real_liquid_type = self.mogp.LiquidType
            else:
                real_liquid_type = self.from_wmo_liquid_type(self.mogp.LiquidType)
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

        if self.root.parent:
            nobj.parent = self.root.parent

    def get_portal_direction(self, portal_obj, group_obj):
        """ Get the direction of MOPR portal relation given a portal object and a target group """

        def try_calculate_direction():

            mesh = group_obj.data
            portal_mesh = portal_obj.data
            normal = portal_obj.data.polygons[0].normal

            for poly in mesh.polygons:
                poly_normal = mathutils.Vector(poly.normal)
                g_center = group_obj.matrix_world * poly.center + poly_normal * sys.float_info.epsilon

                dist = normal[0] * g_center[0] + normal[1] * g_center[1] \
                     + normal[2] * g_center[2] - portal_mesh.polygons[0].normal[0] \
                     * portal_mesh.vertices[portal_mesh.polygons[0].vertices[0]].co[0] \
                     - portal_mesh.polygons[0].normal[1] \
                     * portal_mesh.vertices[portal_mesh.polygons[0].vertices[0]].co[1] \
                     - portal_mesh.polygons[0].normal[2] \
                     * portal_mesh.vertices[portal_mesh.polygons[0].vertices[0]].co[2]

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
                    or mathutils.Vector(
                        (ray_cast_result[1][0] - g_center[0], ray_cast_result[1][1] - g_center[1],
                         ray_cast_result[1][2] - g_center[2])).length > length:
                        result = 1 if dist > 0 else -1

                        if bound_relation_side == 0:
                            bound_relation.Side = -result

                        return result

            return 0

        bpy.context.scene.objects.active = portal_obj

        # check if this portal was already processed
        bound_relation_side = None
        bound_relation = None
        for relation in self.root.mopr.Relationships:
            if relation.PortalIndex == portal_obj.WowPortalPlane.PortalID:
                bound_relation_side = relation.Side
                bound_relation = relation

        if bound_relation_side:
            return -bound_relation_side

        if portal_obj.WowPortalPlane.Algorithm != '0':
            return 1 if portal_obj.WowPortalPlane.Algorithm == '1' else -1

        # reveal hidden geometry
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        portal_obj.select = True
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        portal_obj.select = False

        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

        result = try_calculate_direction()

        if result:
            return result

        # triangulate the proxy portal
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.quads_convert_to_tris()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        result = try_calculate_direction()

        if result:
            return result

        if bound_relation_side is None:
            print("\nFailed to calculate direction for portal <<{}>>. "
                  "Calculation from another side will be attempted.".format(portal_obj.name))
        else:
            print("\nFailed to calculate direction from the opposite side for portal <<{}>> "
                  "You may consider setting up the direction manually.".format(portal_obj.name))

        return 0

    def save_liquid(self, ob):
        mesh = ob.data

        # apply mesh transformations
        active = bpy.context.scene.objects.active
        bpy.context.scene.objects.active = ob
        ob.select = True
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        ob.select = False
        bpy.context.scene.objects.active = active

        start_vertex = 0
        sum = 0
        for vertex in mesh.vertices:
            cur_sum = vertex.co[0] + vertex.co[1]

            if cur_sum < sum:
                start_vertex = vertex.index
                sum = cur_sum

        self.mliq.xTiles = round(ob.dimensions[0] / 4.1666625)
        self.mliq.yTiles = round(ob.dimensions[1] / 4.1666625)
        self.mliq.xVerts = self.mliq.xTiles + 1
        self.mliq.yVerts = self.mliq.yTiles + 1
        self.mliq.Position = mesh.vertices[start_vertex].co

        self.mogp.Flags |= 0x1000 # do we really need that?
        self.mogp.LiquidType = int(ob.WowLiquid.LiquidType)

        # creating liquid material

        material = bpy.data.materials.new(ob.name)
        material.WowMaterial.Enabled = True
        material.WowMaterial.DiffColor = ob.WowLiquid.Color

        types_1 = {3, 7, 11}
        types_2 = {4, 8, 12}

        material.WowMaterial.Texture1 = "DUNGEONS\\TEXTURES\\STORMWIND\\GRAY12.BLP"

        if self.mogp.LiquidType in types_1:
            material.WowMaterial.Texture1 = "DUNGEONS\\TEXTURES\\METAL\\BM_BRSPIRE_CATWALK01.BLP"

        elif self.mogp.LiquidType in types_2:
            material.WowMaterial.Texture1 = "DUNGEONS\\TEXTURES\\FLOOR\\JLO_UNDEADZIGG_SLIMEFLOOR.BLP"

        self.mliq.materialID = self.root.add_material(material)

        if self.mogp.LiquidType in types_1 or self.mogp.LiquidType in types_2:

            if mesh.uv_layers.active:

                uv_map = {}

                for poly in mesh.polygons:
                    for loop_index in poly.loop_indices:
                        if mesh.loops[loop_index].vertex_index not in uv_map:
                            uv_map[mesh.loops[loop_index].vertex_index] = mesh.uv_layers.active.data[loop_index].uv

                for i in range(self.mliq.xVerts * self.mliq.yVerts):
                    vertex = MagmaVertex()

                    vertex.u = int(uv_map.get(mesh.vertices[i].index)[0])
                    vertex.v = int(uv_map.get(mesh.vertices[i].index)[1])

                    vertex.height = mesh.vertices[i].co[2]
                    self.mliq.VertexMap.append(vertex)
            else:
                raise Exception("\nSlime and magma (lava) liquids require a UV map to be created.")

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

                    if self.comp_colors(vc_layer.data[poly.loop_indices[0]].color, blue):
                        tile_flag |= bit
                    bit <<= 1

                self.mliq.TileFlags.append(tile_flag)

    def save(self, original_obj, obj, autofill_textures):
        """ Save WoW WMO group data for future export """
        print("\nSaving group: <<{}>>".format(obj.name[:-4]))

        bpy.context.scene.objects.active = obj
        mesh = obj.data

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        if len(obj.modifiers):
            for modifier in obj.modifiers:
                bpy.ops.object.modifier_apply(modifier=modifier.name)

        bpy.ops.object.modifier_add(type='TRIANGULATE')
        bpy.context.object.modifiers["Triangulate"].quad_method = 'BEAUTY'
        bpy.ops.object.modifier_remove(modifier="Triangulate")

        # triangulate mesh
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
        obj.select = True
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        obj.select = False

        # perform vertex group split to keep batches accurate.
        bpy.ops.object.mode_set(mode='EDIT')
        if obj.WowVertexInfo.BatchTypeA != "":
            bpy.ops.object.vertex_group_set_active(group=obj.WowVertexInfo.BatchTypeA)
            bpy.ops.object.vertex_group_select()
            bpy.ops.mesh.split()
            bpy.ops.mesh.select_all(action='DESELECT')

        if obj.WowVertexInfo.BatchTypeB != "":
            bpy.ops.object.vertex_group_set_active(group=obj.WowVertexInfo.BatchTypeB)
            bpy.ops.object.vertex_group_select()
            bpy.ops.mesh.split()
            bpy.ops.mesh.select_all(action='DESELECT')

        bpy.ops.object.mode_set(mode='OBJECT')

        mesh.use_auto_smooth = True

        if mesh.has_custom_normals:
            mesh.calc_normals_split()
        else:
            bpy.ops.mesh.customdata_custom_splitnormals_add()
            original_obj.data.calc_normals_split()

            obj.select = True
            bpy.context.scene.objects.active = original_obj
            bpy.ops.object.data_transfer(data_type='CUSTOM_NORMAL')
            obj.select = False
            bpy.context.scene.objects.active = obj
            mesh.calc_normals_split()

        # doing safety checks
        if len(mesh.vertices) > 65535:
            print("\nObject <<{}>> contains more vertices ({}) than it is supported. "
                  "\nMaximum amount of vertices you can use per one object is 65535.".format(obj.name, len(mesh.vertices)))

        if len(self.root.momt.Materials) > 256:
            print("\nScene has exceeded the maximum allowed number of WoW materials (255). Your scene now has {} materials. "
                  "So, {} extra ones.".format(len(self.root.momt.Materials), (len(self.root.momt.Materials) - 256)))

        self.mver.Version = 17

        material_indices = {}

        if autofill_textures:
            obj.select = True
            bpy.ops.scene.wow_fill_textures()
            obj.select = False

        for i in range(len(mesh.materials)):
            material_indices[i] = self.root.add_material(mesh.materials[i])

        poly_batch_map = {}

        vg_batch_a = None
        vg_batch_b = None
        vg_collision = None
        vg_lightmap = None
        vg_blendmap = None
        uv_second_uv = None

        if obj.WowVertexInfo.BatchTypeA != "":
            vg_batch_a = obj.vertex_groups.get(obj.WowVertexInfo.BatchTypeA)
        else:
            vg_batch_a = obj.vertex_groups.new("BatchMapA")

        if obj.WowVertexInfo.BatchTypeB != "":
            vg_batch_b = obj.vertex_groups.get(obj.WowVertexInfo.BatchTypeB)
        else:
            vg_batch_b = obj.vertex_groups.new("BatchMapB")

        if obj.WowVertexInfo.VertexGroup != "":
            vg_collision = obj.vertex_groups.get(obj.WowVertexInfo.VertexGroup)

        if obj.WowVertexInfo.Lightmap != "":
            vg_lightmap = obj.vertex_groups.get(obj.WowVertexInfo.Lightmap)

        if obj.WowVertexInfo.Blendmap != "":
            vg_blendmap = obj.vertex_groups.get(obj.WowVertexInfo.Blendmap)
            self.mogp.Flags |= MOGP_FLAG.HasTwoMOCV
            self.root.mohd.Flags |= 0x1

        if obj.WowVertexInfo.SecondUV != "":
            uv_second_uv = obj.data.uv_textures.get(obj.WowVertexInfo.SecondUV)
            self.mogp.Flags |= MOGP_FLAG.HasTwoMOTV

        for poly in mesh.polygons:
            poly_batch_map.setdefault((material_indices.get(poly.material_index),
                                       self.get_batch_type(poly, mesh, vg_batch_a.index, vg_batch_b.index)), []).append(poly.index)

        vertex_size = len(mesh.vertices)

        # count A and B batches amount
        n_batches_a = 0
        n_batches_b = 0
        n_batches_c = 0

        for batch_key, poly_batch in poly_batch_map.items():
            if batch_key[0] != 0xFF:
                if batch_key[1] == 0:
                    n_batches_a += 1
                elif batch_key[1] == 1:
                    n_batches_b += 1
                else:
                    n_batches_c += 1

        # resize chunk containers
        self.moba.Batches = (n_batches_a + n_batches_b + n_batches_c) * [Batch()]
        self.movt.Vertices = vertex_size * [(0, 0, 0)]
        self.monr.Normals = vertex_size * [(0, 0, 0)]
        self.motv.TexCoords = vertex_size * [(0, 0)]
        self.motv2.TexCoords = vertex_size * [(0, 0)]
        self.mocv.vertColors = vertex_size * [(0x7F, 0x7F, 0x7F, 0x00)]
        self.mocv2.vertColors = vertex_size * [(0x7F, 0x7F, 0x7F, 0x00)]

        vertex_map = {}
        normal_map = {}

        new_index_last = 0

        # write geometry data and batches
        batch_counter_a = 0
        batch_counter_b = 0
        batch_counter_c = 0

        for batch_key, poly_batch in poly_batch_map.items():

            first_index = len(self.movi.Indices)

            sentry_indices = [0xFFFF, 0x00]

            for poly in poly_batch:
                collision_counter = 0

                for vertex_index in mesh.polygons[poly].vertices:

                    new_index_current = vertex_map.get(vertex_index)

                    if new_index_current is None:
                        vertex_map[vertex_index] = new_index_last
                        new_index_current = new_index_last
                        new_index_last += 1
                        self.movt.Vertices[new_index_current] = tuple(mesh.vertices[vertex_index].co)

                    sentry_indices[0] = min(sentry_indices[0], new_index_current)
                    sentry_indices[1] = max(sentry_indices[1], new_index_current)

                    self.movi.Indices.append(new_index_current)

                    if vg_collision is not None:
                        for group_info in mesh.vertices[vertex_index].groups:
                            if group_info.group == vg_collision.index:
                                collision_counter += 1

                tri_mat = TriangleMaterial()
                tri_mat.MaterialID = batch_key[0]
                tri_mat.Flags = 0x8 if tri_mat.MaterialID == 0xFF else 0x20
                tri_mat.Flags |= 0x40 if collision_counter == len(mesh.polygons[poly].vertices) else 0x4 | 0x8

                for loop_index in mesh.polygons[poly].loop_indices:

                    new_index = vertex_map.get(mesh.loops[loop_index].vertex_index)
                    vertex = mesh.vertices[mesh.loops[loop_index].vertex_index]

                    if len(mesh.uv_layers) > 0:
                        self.motv.TexCoords[new_index] = (mesh.uv_layers.active.data[loop_index].uv[0],
                                                            1.0 - mesh.uv_layers.active.data[loop_index].uv[1])

                    if uv_second_uv:
                        self.motv2.TexCoords[new_index] = (mesh.uv_layers[uv_second_uv.name].data[loop_index].uv[0],
                                                            1.0 - mesh.uv_layers[uv_second_uv.name].data[loop_index].uv[1])

                    if '0' in obj.WowWMOGroup.Flags \
                    or (obj.WowWMOGroup.PlaceType == '8192' and '1' not in obj.WowWMOGroup.Flags):
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
                            if batch_key == 2:
                                self.mocv.vertColors[new_index] = [0x7F, 0x7F, 0x7F, 0x00]
                            else:
                                self.mocv.vertColors[new_index] = [0x7F, 0x7F, 0x7F, 0xFF]

                    if vg_blendmap is not None:
                        for vertex_group_element in vertex.groups:
                                    if vertex_group_element.group == vg_blendmap.index:
                                        try:
                                            weight = round(vertex.groups[vg_blendmap.index].weight * 255)
                                        except:
                                            weight = 1
                                        self.mocv2.vertColors[new_index] = (0,
                                                                            0,
                                                                            0,
                                                                            weight if weight > 0 else 0x00)

                    normal_map.setdefault(new_index, []).append(tuple(mesh.loops[loop_index].normal))

                self.mopy.TriangleMaterials.append(tri_mat)

            n_indices = len(self.movi.Indices) - first_index

            bounding_box = [32767, 32767, 32767, -32768, -32768, -32768]

            for poly in poly_batch:
                for vertex_index in mesh.polygons[poly].vertices:
                    new_index = vertex_map.get(vertex_index)
                    self.monr.Normals[new_index] = self.get_avg(normal_map.get(new_index))

                    for i in range(0, 2):
                        for j in range(0, 3):
                            idx = i * 3 + j
                            bounding_box[idx] = min(bounding_box[idx], floor(self.movt.Vertices[new_index][j])) \
                                               if i == 0 else max(bounding_box[idx], ceil(self.movt.Vertices[new_index][j]))

            # skip batch writing if processed polyBatch is collision
            if batch_key[0] == 0xFF:
                continue

            # write current batch
            batch = Batch()

            batch.BoundingBox = bounding_box

            batch.StartTriangle = first_index
            batch.nTriangle = n_indices

            batch.StartVertex = sentry_indices[0]
            batch.LastVertex = sentry_indices[1]

            batch.MaterialID = batch_key[0]

            # sort and write batches
            if batch_key[1] == 0:
                self.moba.Batches[batch_counter_a] = batch
                batch_counter_a += 1
            elif batch_key[1] == 1:
                self.moba.Batches[n_batches_a + batch_counter_b] = batch
                batch_counter_b += 1
            else:
                self.moba.Batches[n_batches_a + n_batches_b + batch_counter_c] = batch
                batch_counter_c += 1

        # write header
        self.mogp.BoundingBoxCorner1 = [32767, 32767, 32767]
        self.mogp.BoundingBoxCorner2 = [-32768, -32768, -32768]

        for vtx in self.movt.Vertices:
            for i in range(0, 3):
                self.mogp.BoundingBoxCorner1[i] = min(self.mogp.BoundingBoxCorner1[i], floor(vtx[i]))
                self.mogp.BoundingBoxCorner2[i] = max(self.mogp.BoundingBoxCorner2[i], ceil(vtx[i]))

        self.mogp.Flags |= MOGP_FLAG.HasCollision # /!\ MUST HAVE 0x1 FLAG ELSE THE GAME CRASH !
        if '0' in obj.WowWMOGroup.Flags:
            self.mogp.Flags |= MOGP_FLAG.HasVertexColor
        if '4' in obj.WowWMOGroup.Flags:
            self.mogp.Flags |= MOGP_FLAG.HasSkybox
        if '1' in obj.WowWMOGroup.Flags:
            self.mogp.Flags |= MOGP_FLAG.DoNotUseLocalLighting
        if '2' in obj.WowWMOGroup.Flags:
            self.mogp.Flags |= MOGP_FLAG.AlwaysDraw
        if '3' in obj.WowWMOGroup.Flags:
            self.mogp.Flags |= MOGP_FLAG.IsMountAllowed

        self.mogp.Flags |= int(obj.WowWMOGroup.PlaceType)

        hasLights = False

        fogs = (obj.WowWMOGroup.Fog1,
                obj.WowWMOGroup.Fog2,
                obj.WowWMOGroup.Fog3,
                obj.WowWMOGroup.Fog4)

        lamps = obj.WowWMOGroup.Relations.Lights

        objects = bpy.context.scene.objects

        # set fog references
        self.mogp.FogIndices = (objects[fogs[0]].WowFog.FogID if fogs[0] else 0,
                                objects[fogs[1]].WowFog.FogID if fogs[0] else 0,
                                objects[fogs[2]].WowFog.FogID if fogs[0] else 0,
                                objects[fogs[3]].WowFog.FogID if fogs[0] else 0)
        # save lamps
        if lamps:
            hasLights = True
            for lamp in lamps:
                self.molr.LightRefs.append(lamp.id)

        self.mogp.nBatchesA = n_batches_a
        self.mogp.nBatchesB = n_batches_b
        self.mogp.nBatchesC = n_batches_c
        self.mogp.nBatchesD = 0
        self.mogp.GroupID = int(obj.WowWMOGroup.GroupDBCid)
        self.mogp.Unknown1 = 0
        self.mogp.Unknown2 = 0

        group_info = self.root.add_group_info(self.mogp.Flags,
                                             [self.mogp.BoundingBoxCorner1, self.mogp.BoundingBoxCorner2],
                                             original_obj.name,
                                             obj.WowWMOGroup.GroupDesc)

        self.mogp.GroupNameOfs = group_info[0]
        self.mogp.DescGroupNameOfs = group_info[1]

        if len(obj.WowWMOGroup.MODR):
            for doodad in obj.WowWMOGroup.MODR:
                self.modr.DoodadRefs.append(doodad.value)
            self.mogp.Flags |= MOGP_FLAG.HasDoodads
        elif obj.WowWMOGroup.Relations.Doodads:
            for doodad in obj.WowWMOGroup.Relations.Doodads:
                self.modr.DoodadRefs.append(doodad.id)
            self.mogp.Flags |= MOGP_FLAG.HasDoodads
        else:
            self.modr = None

        bsp_tree = BSPTree()
        bsp_tree.GenerateBSP(self.movt.Vertices, self.movi.Indices, obj.WowVertexInfo.NodeSize)

        self.mobn.Nodes = bsp_tree.Nodes
        self.mobr.Faces = bsp_tree.Faces

        if '0' not in obj.WowWMOGroup.Flags:
            if obj.WowWMOGroup.PlaceType == '8192':
                if '1' in obj.WowWMOGroup.Flags \
                and not len(mesh.vertex_colors):
                    self.mocv = None
                else:
                    self.mogp.Flags |= MOGP_FLAG.HasVertexColor
            else:
                self.mocv = None

        if not self.mogp.Flags & MOGP_FLAG.HasWater:
            self.mliq = None
            self.mogp.Flags |= MOGP_FLAG.IsNotOcean # check if this is necessary
            self.root.mohd.Flags |= 0x4
            self.mogp.LiquidType = int(obj.WowWMOGroup.LiquidType)

        if not hasLights:
            self.molr = None
        else:
            self.mogp.Flags |= MOGP_FLAG.HasLight

        # write second MOTV and MOCV
        if uv_second_uv is None:
            self.motv2 = None

        if vg_blendmap is None:
            self.mocv2 = None

        print("\nDone saving group: <<{}>>".format(obj.name[:-4]))



