from .panels import *
from ...m2 import import_m2 as m2

import bpy
import subprocess
import mathutils
import math
import os
import sys
import time
import struct


###############################
## WMO operators
###############################

class IMPORT_ADT_SCENE(bpy.types.Operator):
    bl_idname = "scene.wow_import_adt_scene"
    bl_label = "Import M2s and WMOs from ADT"
    bl_description = "Import M2s and WMOs from ADT"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, context):
        return True

    dir_path = bpy.props.StringProperty(
        name="",
        description="Choose a directory with ADTs:",
        default="",
        maxlen=1024,
        subtype='DIR_PATH')

    doodads_on = bpy.props.BoolProperty(
        name="As doodads",
        description="Import M2 models as doodads",
        default=True
    )

    group_objects = bpy.props.BoolProperty(
        name="Group objects",
        description="Add imported objects to a new group",
        default=True
    )

    def execute(self, context):

        game_data = getattr(bpy, "wow_game_data", None)

        if not game_data or not game_data.files:
            self.report({'ERROR'}, "Failed to import model. Connect to game client first.")
            return {'CANCELLED'}

        save_dir = bpy.path.abspath("//") if bpy.data.is_saved else None

        if not save_dir:
            self.report({'ERROR'}, """Failed to import WMO.
            Save your blendfile first.""")
            return {'CANCELLED'}

        preferences = bpy.context.user_preferences.addons.get("io_scene_wmo").preferences

        dir = self.dir_path
        if not dir:
            return {'FINISHED'}

        fileinfo_path = preferences.fileinfo_path

        m2_paths = []
        wmo_paths = []

        m2_instances = {}
        wmo_instances = {}

        group_name = None
        if self.group_objects:
            i = 0
            while True:
                name = "ADTImport_" + str(i)
                if name not in bpy.context.scene.objects:
                    group_name = name
                    break
                i += 1

            bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
            parent = bpy.context.scene.objects.active
            parent.name = group_name

        for filename in os.listdir(dir):

            if filename.endswith(".adt"):
                filepath = os.path.join(dir, filename)
                subprocess.call([fileinfo_path, filepath] )

                with open(os.path.splitext(filepath)[0] + ".txt", 'r') as f:

                    cur_chunk = ""
                    for line in f.readlines():
                        parsed_line = line.replace('\t', ' ')
                        data = parsed_line.split()

                        if not data:
                            continue

                        if data[0] in {'MMDX', 'MWMO', 'MDDF', 'MODF'}:
                            cur_chunk = data[0]
                        else:
                            if cur_chunk == 'MMDX':
                                m2_paths.append(data[1])
                            elif cur_chunk == 'MWMO':
                                wmo_paths.append(data[1])
                            elif cur_chunk == 'MDDF':
                                entry = data[2:]
                                entry.insert(0, data[0])
                                m2_instances[data[1]] = entry
                            elif cur_chunk == 'MODF':
                                entry = data[2:]
                                entry.insert(0, data[0])
                                wmo_instances[data[1]] = entry


        instance_cache = {}

        # import M2s
        for uid, instance in m2_instances.items():
            doodad_path = m2_paths[int(instance[0])]
            cached_obj = instance_cache.get(doodad_path)

            if cached_obj:
                obj = cached_obj.copy()
                obj.data = cached_obj.data.copy()
                bpy.context.scene.objects.link(obj)

            else:
                try:
                    obj = m2.m2_to_blender_mesh(save_dir, doodad_path, game_data)
                except:
                    bpy.ops.mesh.primitive_cube_add()
                    obj = bpy.context.scene.objects.active
                    print("\nFailed to import model: <<{}>>. Placeholder is imported instead.".format(doodad_path))

                instance_cache[doodad_path] = obj

            obj.name += ".m2"
            obj.location = ((-float(instance[1])), (float(instance[3])), float(instance[2]))
            obj.rotation_euler = (math.radians(float(instance[6])),
                                  math.radians(float(instance[4])),
                                  math.radians(float(instance[5]) + 90))
            obj.scale = tuple((float(instance[7]) / 1024.0 for _ in range(3)))

            if self.doodads_on:
                obj.WoWDoodad.Enabled = True
                obj.WoWDoodad.Path = doodad_path

            if self.group_objects:
                obj.parent = parent

        # import WMOs
        from .. import import_wmo
        for uid, instance in wmo_instances.items():

            wmo_path = wmo_paths[int(instance[0])]

            cached_obj = instance_cache.get(wmo_path)


            game_data.extract_files(save_dir, (wmo_path,))

            i = 0
            while True:
                result = game_data.extract_files(save_dir, (wmo_path[:-4] + "_" + str(i).zfill(3) + ".wmo",))
                if not result:
                    break
                i += 1

            try:
                obj = import_wmo.import_wmo_to_blender_scene(os.path.join(save_dir, wmo_path), True, True, True)
            except:
                bpy.ops.mesh.primitive_cube_add()
                obj = bpy.context.scene.objects.active
                print("\nFailed to import model: <<{}>>. Placeholder is imported instead.".format(wmo_path))


            obj.location = ((-float(instance[1])), (float(instance[3])), float(instance[2]))
            obj.rotation_euler = (math.radians(float(instance[6])),
                                  math.radians(float(instance[4])),
                                  math.radians(float(instance[5]) + 90))

            if self.group_objects:
                obj.parent = parent

        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class IMPORT_LAST_WMO_FROM_WMV(bpy.types.Operator):
    bl_idname = "scene.wow_import_last_wmo_from_wmv"
    bl_label = "Load last WMO from WMV"
    bl_description = "Load last WMO from WMV"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, context):
        return True

    def wmv_get_last_wmo(self):
        """Get the path of last M2 model from WoWModelViewer or similar log."""

        preferences = bpy.context.user_preferences.addons.get("io_scene_wmo").preferences

        if preferences.wmv_path:

            lines = open(preferences.wmv_path).readlines()

            for line in reversed(lines):
                if 'Loading WMO' in line:
                    return line[22:].rstrip("\n")

    def execute(self, context):

        game_data = getattr(bpy, "wow_game_data", None)

        if not game_data or not game_data.files:
            self.report({'ERROR'}, "Failed to import model. Connect to game client first.")
            return {'CANCELLED'}

        dir = bpy.path.abspath("//") if bpy.data.is_saved else None
        wmo_path = self.wmv_get_last_wmo()

        if not wmo_path:
            self.report({'ERROR'}, """WoW Model Viewer log contains no WMO entries.
            Make sure to use compatible WMV version or open a .wmo there.""")
            return {'CANCELLED'}

        if dir:

            game_data.extract_files(dir, (wmo_path,))

            i = 0
            while True:
                result = game_data.extract_files(dir, (wmo_path[:-4] + "_" + str(i).zfill(3) + ".wmo",))
                if not result:
                    break
                i += 1

            try:
                from .. import import_wmo
                import_wmo.import_wmo_to_blender_scene(os.path.join(dir, wmo_path), True, True, True)
            except:
                self.report({'ERROR'}, "Failed to import model.")
                return {'CANCELLED'}

            self.report({'INFO'}, "Done importing WMO object to scene.")
            return {'FINISHED'}

        else:
            self.report({'ERROR'}, """Failed to import WMO.
            Save your blendfile first.""")
            return {'CANCELLED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


###############################
## Doodad operators
###############################

def LoadDoodadsFromPreserved(dir, game_data):
    """ Load doodad sets to scene from preserved doodadset data"""

    def get_string(ofs):
        for string in bpy.context.scene.WoWRoot.MODN_StringTable:
            if string.Ofs == ofs:
                return string.String

    scene = bpy.context.scene
    obj_map = {}

    for doodad_set in scene.WoWRoot.MODS_Sets:

        bpy.ops.object.empty_add(type='SPHERE', location=(0, 0, 0))
        anchor = bpy.context.scene.objects.active
        anchor.name = doodad_set.Name
        anchor.hide = True
        anchor.hide_select = True

        for i in range(doodad_set.StartDoodad, doodad_set.StartDoodad + doodad_set.nDoodads):
            doodad = scene.WoWRoot.MODD_Definitions[i]
            doodad_path = os.path.splitext(get_string(doodad.NameOfs))[0] + ".m2"

            nobj = None
            obj = obj_map.get(doodad_path)

            if not obj:
                try:
                    obj = m2.m2_to_blender_mesh(dir, doodad_path, game_data)
                except:
                    bpy.ops.mesh.primitive_cube_add()
                    obj = bpy.context.scene.objects.active
                    print("#nFailed to import model: <<{}>>. Placeholder is imported instead.".format(doodad_path))

                obj.WoWDoodad.Enabled = True
                obj.WoWDoodad.Path = doodad_path

                obj_map[doodad_path] = obj
                nobj = obj
            else:
                nobj = obj.copy()

                nobj.WoWDoodad.Color = (doodad.Color[0] / 255,
                                        doodad.Color[1] / 255,
                                        doodad.Color[2] / 255,
                                        doodad.ColorAlpha / 255)

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
            nobj.rotation_quaternion = (doodad.Tilt,
                                        doodad.Rotation[0],
                                        doodad.Rotation[1],
                                        doodad.Rotation[2])
            nobj.parent = anchor
            nobj.hide = True
            nobj.lock_location = (True, True, True)
            nobj.lock_rotation = (True, True, True)
            nobj.lock_scale = (True, True, True)


class DOODADS_BAKE_COLOR(bpy.types.Operator):
    bl_idname = "scene.wow_doodads_bake_color"
    bl_label = "Bake doodads color"
    bl_description = "Bake doodads colors from nearby vertex color values"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, context):
        return True

    tree_map = {}

    def find_nearest_object(object, objects):
        """Get closest object to another object"""

        dist = 32767
        result = None
        for obj in objects:
            obj_location_relative = obj.matrix_world.inverted() * object.location
            hit = obj.closest_point_on_mesh(obj_location_relative)
            hit_dist = (obj_location_relative - hit[1]).length
            if hit_dist < dist:
                dist = hit_dist
                result = obj

        return result

    def get_object_radius(obj):
        corner_min = [32767, 32767, 32767]
        corner_max = [0, 0, 0]

        mesh = obj.data

        for vertex in mesh.vertices:
            for i in range(3):
                corner_min[i] = min(corner_min[i], vertex.co[i])
                corner_max[i] = max(corner_max[i], vertex.co[i])
        result = (mathutils.Vector(corner_min) - mathutils.Vector(corner_max))
        return (abs(result.x) + abs(result.y) + abs(result.z)) / 3

    def gen_doodad_color(self, obj, group):

        mesh = group.data

        if not mesh.vertex_colors:
            return 0.5, 0.5, 0.5, 1.0

        radius = DOODADS_BAKE_COLOR.get_object_radius(obj)
        colors = []

        kd_tree = self.tree_map.get(group.name)
        if not kd_tree:
            kd_tree = mathutils.kdtree.KDTree(len(mesh.polygons))

            for index, poly in enumerate(mesh.polygons):
                kd_tree.insert(group.matrix_world * poly.center, index)

            kd_tree.balance()
            self.tree_map[group.name] = kd_tree

        polygons = kd_tree.find_range(obj.location, radius)

        if not polygons:
            polygons.append(kd_tree.find(obj.location))

        for poly in polygons:
            for loop_index in mesh.polygons[poly[1]].loop_indices:
                colors.append(mesh.vertex_colors[mesh.vertex_colors.active_index].data[loop_index].color)

        if not colors:
            return 0.5, 0.5, 0.5, 1.0

        final_color = mathutils.Vector((0x00, 0x00, 0x00))
        for color in colors:
            final_color += mathutils.Vector(color)

        return tuple(final_color / len(colors)) + (1.0,)

    def execute(self, context):

        window_manager = context.window_manager
        doodad_counter = 0
        len_objects = len(bpy.context.selected_objects)

        groups = [obj for obj in bpy.context.scene.objects if obj.WowWMOGroup.Enabled]

        window_manager.progress_begin(0, 100)
        for index, obj in enumerate(bpy.context.selected_objects):
            if obj.WoWDoodad.Enabled:
                obj.WoWDoodad.Color = self.gen_doodad_color(obj, DOODADS_BAKE_COLOR.find_nearest_object(obj, groups))
                print("\nBaking color to doodad instance <<{}>>".format(obj.name))
                doodad_counter += 1
                window_manager.progress_update(int(index / len_objects * 100))

        window_manager.progress_end()

        if doodad_counter:
            self.report({'INFO'}, "Done baking colors to {} doodad instances.".format(doodad_counter))
        else:
            self.report({'ERROR'}, "No doodad instances found among selected objects.")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class DOODAD_SET_CLEAR_PRESERVED(bpy.types.Operator):
    bl_idname = 'scene.wow_clear_preserved_doodad_sets'
    bl_label = 'Clear preserved doodad sets'
    bl_description = 'Clear preserved doodad set data or optionally load real doodad sets'
    bl_options = {'REGISTER', 'INTERNAL'}

    Action = bpy.props.EnumProperty(
        items=[
            ('0', "Load doodad sets", "Load doodad sets from game data", 'LOAD_FACTORY', 0),
            ('1', "Clear preserved sets", "Clear preserved doodad set data to unlock editing", 'CANCEL', 1)],
        default='0'
    )

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        col = self.layout
        col.prop(self, "Action", expand=True)

    def execute(self, context):
        if self.Action == '0':
            if not hasattr(bpy, "wow_game_data"):
                print("\n\n### Loading game data ###")
                bpy.ops.scene.load_wow_filesystem()

            dir = bpy.path.abspath("//") if bpy.data.is_saved else None

            if dir:
                try:
                    LoadDoodadsFromPreserved(dir, bpy.wow_game_data)
                except:
                    self.report({'ERROR'}, "An error occured while importing doodads.")
                    return {'CANCELLED'}
            else:
                self.report({'ERROR'}, """Failed to import model. Save your blendfile first.""")
                return {'CANCELLED'}

            bpy.context.scene.WoWRoot.MODS_Sets.clear()
            bpy.context.scene.WoWRoot.MODN_StringTable.clear()
            bpy.context.scene.WoWRoot.MODD_Definitions.clear()

            update_wow_visibility(bpy.context.scene, None)
            self.report({'INFO'}, "Successfully imported doodad sets")
            return {'FINISHED'}

        else:
            bpy.context.scene.WoWRoot.MODS_Sets.clear()
            bpy.context.scene.WoWRoot.MODN_StringTable.clear()
            bpy.context.scene.WoWRoot.MODD_Definitions.clear()
            self.report({'INFO'}, "Successfully cleared preserved doodad sets. Editing is now available")
            return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class DOODAD_SET_ADD(bpy.types.Operator):
    bl_idname = 'scene.wow_doodad_set_add'
    bl_label = 'Add doodad set'
    bl_description = 'Add models to doodadset'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    Action = bpy.props.EnumProperty(
        name="Operator action",
        description="Choose operator action",
        items=[
            ("ADD", "Add to existing set", "", 'PLUGIN', 0),
            ("CUSTOM", "Create new set", "", 'ZOOMIN', 1),
            ("GLOBAL", "Create new global set", "", 'WORLD', 2),
        ]
    )

    Set = bpy.props.EnumProperty(
        name="",
        description="Select doodad set",
        items=get_doodad_sets,
        update=switch_doodad_set
    )

    Name = bpy.props.StringProperty(
        name=""
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col.label(text="Action")
        col.prop(self, "Action", expand=True)

        if self.Action == "ADD":
            text = "Select set:"
            col.label(text=text)
            col.prop(self, "Set")
        elif self.Action == "CUSTOM":
            text = "Enter set name:"
            col.label(text=text)
            col.prop(self, "Name")

    def execute(self, context):

        selected_objs = []
        for obj in bpy.context.scene.objects:
            if obj.select and obj.WoWDoodad.Enabled:
                selected_objs.append(obj)

        if self.Action == "ADD":
            if self.Set != "None":
                for obj in selected_objs:
                    obj.parent = bpy.context.scene.objects[self.Set]

                self.report({'INFO'}, "Successfully added doodads to doodad set")

            else:
                self.report({'WARNING'}, "Select a doodad set to link objects to first")


        elif self.Action == "CUSTOM":
            if self.Name:
                bpy.ops.object.empty_add(type='SPHERE', location=(0, 0, 0))
                obj = bpy.context.scene.objects.active
                obj.name = self.Name
                obj.hide = True
                obj.hide_select = True
                obj.lock_location = (True, True, True)
                obj.lock_rotation = (True, True, True)
                obj.lock_scale = (True, True, True)

                for object in selected_objs:
                    object.parent = obj

                self.report({'INFO'}, "Successfully created new doodadset and added doodads to it")

            else:
                self.report({'WARNING'}, "Enter name of the doodadset")

        elif self.Action == "GLOBAL":
            if not bpy.context.scene.objects.get("Set_$DefaultGlobal"):
                bpy.ops.object.empty_add(type='SPHERE', location=(0, 0, 0))
                obj = bpy.context.scene.objects.active
                obj.name = "Set_$DefaultGlobal"
                obj.hide = True
                obj.hide_select = True
                obj.lock_location = (True, True, True)
                obj.lock_rotation = (True, True, True)
                obj.lock_scale = (True, True, True)

                for object in selected_objs:
                    object.parent = obj

                self.report({'INFO'}, "Successfully created global doodadset and added doodads to it")

            else:
                self.report({'WARNING'}, "There can only be one global doodadset")

        switch_doodad_set(bpy.context.scene, None)

        return {'FINISHED'}

class DOODAD_SET_COLOR(bpy.types.Operator):
    bl_idname = 'scene.wow_doodad_set_color'
    bl_label = 'Set Doodad Color'
    bl_description = "Set color to selected doodads"
    bl_options = {'REGISTER', 'UNDO'}

    Color = bpy.props.FloatVectorProperty(
        name='Color',
        description='Color applied to doodads',
        subtype='COLOR',
        size=4
    )

    def draw(self, context):
        self.layout.column().prop(self, "Color")

    def execute(self, context):

        if not bpy.context.selected_objects:
            self.report({'ERROR'}, "No objects selected.")
            return {'FINISHED'}

        success = False
        for obj in bpy.context.selected_objects:
            if obj.WoWDoodad.Enabled:
                obj.WoWDoodad.Color = self.Color
                success = True

        if success:
            self.report({'INFO'}, "Successfully assigned color to selected doodads.")
        else:
            self.report({'ERROR'}, "No doodads found among selected objects.")

        return {'FINISHED'}


class DOODAD_SET_TEMPLATE_ACTION(bpy.types.Operator):
    bl_idname = 'scene.wow_doodad_set_template_action'
    bl_label = 'Template action'
    bl_description = 'Apply an action to all instances of selected object on the scene'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    Action = bpy.props.EnumProperty(
        items=[
            ('SELECT', "Select", "Rotate all instances of selected doodads", 'PMARKER_ACT', 0),
            ('REPLACE', "Replace", "Replace all instances of selected doodads with last M2 from WMV", 'FILE_REFRESH', 1),
            ('RESIZE', "Resize", "Resize all instances of selected doodads", 'FULLSCREEN_ENTER', 2),
            ('DELETE', "Delete", "Delete all instances of selected doodads", 'CANCEL', 3),
            ('ROTATE', "Rotate", "Rotate all instances of selected doodads", 'LOOP_FORWARDS', 4)],
        default='SELECT'
    )

    Scale = bpy.props.FloatProperty(
        name="Scale",
        description="Scale applied to doodads",
        min=0.01,
        max=20,
        default=1
    )

    Rotation = bpy.props.FloatVectorProperty(
        name="Rotation",
        default=(0, 0, 0, 0),
        size=4
    )

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        col = self.layout.column()

        col.prop(self, "Action", expand=True)

        if self.Action == 'RESIZE':
            col.prop(self, "Scale")
        elif self.Action == 'ROTATE':
            col.prop(self, "Rotation")

    def execute(self, context):

        target = None
        active = bpy.context.scene.objects.active

        if active and active.WoWDoodad:
            target = active.WoWDoodad.Path
        else:
            self.report({'ERROR'}, "Template functions require an active object.")
            return {'CANCELLED'}

        selected_only = False
        if len(bpy.context.selected_objects) > 1:
            selected_only = True

        selected_objects = bpy.context.selected_objects.copy()
        objects_to_select = []

        success = False

        if target:

            new_obj = None

            if self.Action == 'REPLACE':
                if not bpy.data.is_saved:
                    self.report({'ERROR'}, "Saved your blendfile first.")
                    return {'FINISHED'}

                if not hasattr(bpy, "wow_game_data"):
                    self.report({'ERROR'}, "Connect to game data first.")
                    return {'FINISHED'}

                bpy.ops.scene.wow_wmo_import_doodad_from_wmv()
                new_obj = bpy.context.scene.objects.active

            for obj in bpy.context.scene.objects:
                is_selected = obj in selected_objects if selected_only else True

                if obj.WoWDoodad.Path == target and is_selected:

                    if self.Action == 'REPLACE':

                        location = obj.location
                        rotation = obj.rotation_quaternion
                        scale = obj.scale
                        parent = obj.parent
                        color = obj.WoWDoodad.Color
                        flags = obj.WoWDoodad.Flags

                        bpy.data.objects.remove(obj, do_unlink=True)

                        obj = new_obj.copy()
                        bpy.context.scene.objects.link(obj)
                        bpy.context.scene.objects.active = obj

                        obj.location = location
                        obj.rotation_mode = 'QUATERNION'
                        obj.rotation_quaternion = rotation
                        obj.scale = scale
                        obj.parent = parent
                        obj.WoWDoodad.Color = color
                        obj.WoWDoodad.Flags = flags
                        objects_to_select.append(obj)

                    elif self.Action == 'RESIZE':

                        obj.scale *= self.Scale
                        obj.select = True

                    elif self.Action == 'DELETE':

                        bpy.data.objects.remove(obj, do_unlink=True)

                    elif self.Action == 'ROTATE':
                        obj.rotation_mode = 'QUATERNION'
                        for i, _ in enumerate(self.Rotation):
                            obj.rotation_quaternion[i] += self.Rotation[i]

                    elif self.Action == 'SELECT':
                        obj.select = True

                    success = True

                for ob in objects_to_select:
                    ob.select = True

            if new_obj:
                bpy.data.objects.remove(new_obj, do_unlink=True)

            if success:
                self.report({'INFO'}, "Template action applied.")

            return {'FINISHED'}

        else:
            self.report({'ERROR'}, "No doodad is selected.")
            return {'FINISHED'}


###############################
## Water operators
###############################

class OBJECT_OP_ADD_FLAG(bpy.types.Operator):
    bl_idname = 'scene.wow_mliq_change_flags'
    bl_label = 'Change liquid flags'
    bl_description = 'Change WoW liquid flags'

    Action = bpy.props.EnumProperty(
        name="",
        description="Select flag action",
        items=[("ADD", "", ""),
               ("ADD_ALL", "", ""),
               ("CLEAR", "", ""),
               ("CLEAR_ALL", "", "")
               ]
    )

    def execute(self, context):
        water = bpy.context.scene.objects.active
        if water.WowLiquid.Enabled:
            mesh = water.data

            if self.Action == "ADD":
                for polygon in mesh.polygons:
                    if polygon.select:
                        for loop_index in polygon.loop_indices:
                            mesh.vertex_colors[mesh.vertex_colors.active_index].data[loop_index].color = (0, 0, 255)
            elif self.Action == "ADD_ALL":
                for polygon in mesh.polygons:
                    for loop_index in polygon.loop_indices:
                        mesh.vertex_colors[mesh.vertex_colors.active_index].data[loop_index].color = (0, 0, 255)
            elif self.Action == "CLEAR":
                for polygon in mesh.polygons:
                    if polygon.select:
                        for loop_index in polygon.loop_indices:
                            mesh.vertex_colors[mesh.vertex_colors.active_index].data[loop_index].color = (255, 255, 255)
            elif self.Action == "CLEAR_ALL":
                for polygon in mesh.polygons:
                    for loop_index in polygon.loop_indices:
                        mesh.vertex_colors[mesh.vertex_colors.active_index].data[loop_index].color = (255, 255, 255)

        else:
            self.report({'ERROR'}, "Selected object is not World of Warcraft liquid")

        return {'FINISHED'}


###############################
## Object operators
###############################

class OBJECT_OP_Bake_Portal_Relations(bpy.types.Operator):
    bl_idname = 'scene.wow_bake_portal_relations'
    bl_label = 'Bake portal relations'
    bl_description = 'Bake portal relations'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        def find_nearest_objects_pair(object, objects):

            pairs = []

            for obj in objects:
                hit = obj.closest_point_on_mesh(
                    obj.matrix_world.inverted() * (object.matrix_world * object.data.polygons[0].center))
                hit_dist = (
                obj.matrix_world.inverted() * (object.matrix_world * object.data.polygons[0].center) - hit[1]).length

                pairs.append((obj.name, hit_dist))

            pairs.sort(key=lambda x: x[1])

            return pairs[0][0], pairs[1][0]

        if not  bpy.context.selected_objects:
            self.report({'ERROR'}, "No objects selected.")
            return {'FINISHED'}

        success = False

        groups = tuple(x for x in bpy.context.scene.objects if x.WowWMOGroup.Enabled)

        for obj in bpy.context.selected_objects:
            if obj.WowPortalPlane.Enabled:
                direction = find_nearest_objects_pair(obj, groups)
                obj.WowPortalPlane.First = direction[0] if direction[0] else ""
                obj.WowPortalPlane.Second = direction[1] if direction[1] else ""
                success = True

        if success:
            self.report({'INFO'}, "Done baking portal relations.")
        else:
            self.report({'ERROR'}, "No portal objects found among selected objects.")

        return {'FINISHED'}


class OBJECT_OP_Add_Scale(bpy.types.Operator):
    bl_idname = 'scene.wow_add_scale_reference'
    bl_label = 'Add scale'
    bl_description = 'Add a WoW scale prop'
    bl_options = {'REGISTER', 'UNDO'}

    ScaleType = bpy.props.EnumProperty(
        name="Scale Type",
        description="Select scale reference type",
        items=[('HUMAN', "Human Scale (average)", ""),
               ('TAUREN', "Tauren Scale (thickest)", ""),
               ('TROLL', "Troll Scale (tallest)", ""),
               ('GNOME', "Gnome Scale (smallest)", "")
               ],
        default='HUMAN'
    )

    def execute(self, context):
        if self.ScaleType == 'HUMAN':
            bpy.ops.object.add(type='LATTICE')
            scale_obj = bpy.context.object
            scale_obj.name = "Human Scale"
            scale_obj.dimensions = (0.582, 0.892, 1.989)

        elif self.ScaleType == 'TAUREN':
            bpy.ops.object.add(type='LATTICE')
            scale_obj = bpy.context.object
            scale_obj.name = "Tauren Scale"
            scale_obj.dimensions = (1.663, 1.539, 2.246)

        elif self.ScaleType == 'TROLL':
            bpy.ops.object.add(type='LATTICE')
            scale_obj = bpy.context.object
            scale_obj.name = "Troll Scale"
            scale_obj.dimensions = (1.116, 1.291, 2.367)

        elif self.ScaleType == 'GNOME':
            bpy.ops.object.add(type='LATTICE')
            scale_obj = bpy.context.object
            scale_obj.name = "Gnome Scale"
            scale_obj.dimensions = (0.362, 0.758, 0.991)

        self.report({'INFO'}, "Successfully added " + self.ScaleType + " scale")
        return {'FINISHED'}


class OBJECT_OP_Add_Water(bpy.types.Operator):
    bl_idname = 'scene.wow_add_water'
    bl_label = 'Add water'
    bl_description = 'Add a WoW water plane'
    bl_options = {'REGISTER', 'UNDO'}

    xPlanes = bpy.props.IntProperty(
        name="X subdivisions:",
        description="Amount of WoW liquid planes in a row. One plane is 4.1666625 in its radius.",
        default=10,
        min=1
    )

    yPlanes = bpy.props.IntProperty(
        name="Y subdivisions:",
        description="Amount of WoW liquid planes in a column. One plane is 4.1666625 in its radius.",
        default=10,
        min=1
    )

    def execute(self, context):
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=self.xPlanes + 1,
                                        y_subdivisions=self.yPlanes + 1,
                                        radius=4.1666625 / 2
                                        )
        water = bpy.context.scene.objects.active
        bpy.ops.transform.resize(value=(self.xPlanes, self.yPlanes, 1.0))

        water.name += "_Liquid"

        mesh = water.data

        bit = 1
        while bit <= 0x80:
            mesh.vertex_colors.new("flag_" + hex(bit))
            bit <<= 1

        water.WowLiquid.Enabled = True

        water.hide = False if "4" in bpy.context.scene.WoWVisibility else True

        self.report({'INFO'}, "Successfully сreated WoW liquid: " + water.name)
        return {'FINISHED'}


class OBJECT_OP_Add_Fog(bpy.types.Operator):
    bl_idname = 'scene.wow_add_fog'
    bl_label = 'Add fog'
    bl_description = 'Add a WoW fog object to the scene'

    def execute(self, context):

        bpy.ops.mesh.primitive_uv_sphere_add()
        fog = bpy.context.scene.objects.active
        fog.name += "_Fog"

        # applying real object transformation
        bpy.ops.object.shade_smooth()
        fog.draw_type = 'SOLID'
        fog.show_transparent = True
        fog.show_name = True

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

        fog.WowFog.Enabled = True

        fog.hide = False if "3" in bpy.context.scene.WoWVisibility else True

        self.report({'INFO'}, "Successfully сreated WoW fog: " + fog.name)
        return {'FINISHED'}


class OBJECT_OP_Invert_Portals(bpy.types.Operator):
    bl_idname = 'scene.wow_set_portal_dir_alg'
    bl_label = 'Set portal direction algorithm'
    bl_description = 'Set portal direction calculation algorithm.'
    bl_options = {'REGISTER', 'UNDO'}

    Algorithm = bpy.props.EnumProperty(
        items=portal_dir_alg_enum,
        default="0"
    )

    def execute(self, context):
        success = False
        for ob in bpy.context.selected_objects:
            if ob.WowPortalPlane.Enabled:
                ob.WowPortalPlane.Algorithm = self.Algorithm
                success = True

        if success:
            self.report({'INFO'}, "Successfully inverted selected portals")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No portals found among selected objects")
            return {'CANCELLED'}


class OBJECT_OP_Fill_Textures(bpy.types.Operator):
    bl_idname = 'scene.wow_fill_textures'
    bl_label = 'Fill textures'
    bl_description = """Fill Texture 1 field of WoW materials with paths from applied image. """
    bl_options = {'REGISTER'}

    def execute(self, context):

        if not hasattr(bpy, "wow_game_data"):
            print("\n\n### Loading game data ###")
            bpy.ops.scene.load_wow_filesystem()

        game_data = bpy.wow_game_data

        for ob in bpy.context.selected_objects:
            mesh = ob.data
            for i in range(len(mesh.materials)):
                if mesh.materials[i].active_texture is not None \
                        and not mesh.materials[i].WowMaterial.Texture1 \
                        and mesh.materials[i].active_texture.type == 'IMAGE' \
                        and mesh.materials[i].active_texture.image is not None:
                    path = (os.path.splitext(bpy.path.abspath(mesh.materials[i].active_texture.image.filepath))[0] + ".blp", "")
                    rest_path = ""

                    while True:
                        path = os.path.split(path[0])
                        if not path[1]:
                            print("\nTexture <<{}>> not found.".format(mesh.materials[i].active_texture.image.filepath))
                            break

                        rest_path = os.path.join(path[1], rest_path)
                        rest_path = rest_path[:-1] if rest_path.endswith("\\") else rest_path

                        sys.stdout = open(os.devnull, 'w')

                        if game_data.read_file(rest_path):
                            mesh.materials[i].WowMaterial.Texture1 = rest_path
                            break

                        sys.stdout = sys.__stdout__

            self.report({'INFO'}, "Done filling texture paths")

        return {'FINISHED'}


class OBJECT_OP_Quick_Collision(bpy.types.Operator):
    bl_idname = 'scene.wow_quick_collision'
    bl_label = 'Generate basic collision for selected objects'
    bl_description = 'Generate WoW collision equal to geometry of the selected objects'
    bl_options = {'REGISTER', 'UNDO'}

    NodeSize = bpy.props.IntProperty(
        name="Node max size",
        description="Max count of faces for a node in bsp tree",
        default=2500,
        min=1,
        soft_max=5000
    )

    CleanUp = bpy.props.BoolProperty(
        name="Clean up",
        description="Remove unreferenced vertex groups",
        default=False
    )

    def execute(self, context):

        success = False
        for ob in bpy.context.selected_objects:
            if ob.WowWMOGroup.Enabled:
                bpy.context.scene.objects.active = ob

                if self.CleanUp:
                    for vertex_group in ob.vertex_groups:
                        if vertex_group.name != ob.WowVertexInfo.VertexGroup \
                                and vertex_group.name != ob.WowVertexInfo.BatchTypeA \
                                and vertex_group.name != ob.WowVertexInfo.BatchTypeB \
                                and vertex_group.name != ob.WowVertexInfo.Lightmap \
                                and vertex_group.name != ob.WowVertexInfo.Blendmap \
                                and vertex_group.name != ob.WowVertexInfo.SecondUV:
                            ob.vertex_groups.remove(vertex_group)

                if ob.vertex_groups.get(ob.WowVertexInfo.VertexGroup):
                    bpy.ops.object.vertex_group_set_active(group=ob.WowVertexInfo.VertexGroup)
                else:
                    new_vertex_group = ob.vertex_groups.new(name="Collision")
                    bpy.ops.object.vertex_group_set_active(group=new_vertex_group.name)
                    ob.WowVertexInfo.VertexGroup = new_vertex_group.name

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.object.vertex_group_assign()
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
                ob.WowVertexInfo.NodeSize = self.NodeSize

                success = True

        if success:
            self.report({'INFO'}, "Successfully generated automatic collision for selected WMO groups")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No WMO group objects found among selected objects")
            return {'CANCELLED'}


class OBJECT_OP_Texface_to_material(bpy.types.Operator):
    bl_idname = 'scene.wow_texface_to_material'
    bl_label = 'Texface to material'
    bl_description = 'Generate materials out of texfaces in selected objects'

    def execute(self, context):
        if bpy.context.selected_objects[0]:
            bpy.context.scene.objects.active = bpy.context.selected_objects[0]
        bpy.ops.view3d.material_remove()
        bpy.ops.view3d.texface_to_material()

        self.report({'INFO'}, "Successfully generated materials from face textures")
        return {'FINISHED'}


class OBJECT_OP_To_WMOPortal(bpy.types.Operator):
    bl_idname = 'scene.wow_selected_objects_to_portals'
    bl_label = 'Selected objects to WMO portals'
    bl_description = 'Transfer all selected objects to WoW WMO portals'
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        row = layout.row()

        column = layout.column()
        idproperty.layout_id_prop(column, context.object.WowPortalPlane, "First")
        idproperty.layout_id_prop(column, context.object.WowPortalPlane, "Second")

    First = idproperty.ObjectIDProperty(
        name="First group",
        validator=portal_validator
    )

    Second = idproperty.ObjectIDProperty(
        name="Second group",
        validator=portal_validator
    )

    def portal_validator(ob):
        return ob.type == 'MESH' and ob.WowWMOGroup.Enabled

    def execute(self, context):

        success = False
        for ob in bpy.context.selected_objects:
            if ob.type == 'MESH':
                ob.WowWMOGroup.Enabled = False
                ob.WowLiquid.Enabled = False
                ob.WowFog.Enabled = False
                ob.WowPortalPlane.Enabled = True
                ob.WowPortalPlane.First = self.First
                ob.WowPortalPlane.Second = self.Second

                ob.hide = False if "2" in bpy.context.scene.WoWVisibility else True
                success = True

        if success:
            self.report({'INFO'}, "Successfully converted select objects to portals")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No mesh objects found among selected objects")
            return {'CANCELLED'}


class OBJECT_OP_To_Group(bpy.types.Operator):
    bl_idname = 'scene.wow_selected_objects_to_group'
    bl_label = 'Selected objects to WMO group'
    bl_description = 'Transfer all selected objects to WoW WMO groups'
    bl_options = {'REGISTER', 'UNDO'}

    GroupName = bpy.props.StringProperty(name="Name")
    GroupDesc = bpy.props.StringProperty(name="Description")

    PlaceType = bpy.props.EnumProperty(
        items=place_type_enum,
        name="Place Type",
        description="Group is indoor or outdoor"
    )

    Flags = bpy.props.EnumProperty(
        items=group_flag_enum,
        options={'ENUM_FLAG'}
    )

    GroupDBCid = bpy.props.IntProperty(
        name="DBC Group ID",
        description="WMO Group ID in DBC file"
    )

    LiquidType = bpy.props.EnumProperty(
        items=liquid_type_enum,
        name="LiquidType",
        description="Fill this WMO group with selected liquid."
    )

    def execute(self, context):

        scene = bpy.context.scene

        success = False
        for ob in bpy.context.selected_objects:
            if ob.type == 'MESH':
                ob.WowLiquid.Enabled = False
                ob.WowFog.Enabled = False
                ob.WowPortalPlane.Enabled = False
                ob.WowWMOGroup.Enabled = True
                ob.WowWMOGroup.PlaceType = self.PlaceType
                ob.WowWMOGroup.GroupName = self.GroupName
                ob.WowWMOGroup.GroupDesc = self.GroupDesc
                ob.WowWMOGroup.Flags = self.Flags
                ob.WowWMOGroup.GroupDBCid = self.GroupDBCid
                ob.WowWMOGroup.LiquidType = self.LiquidType

                if self.PlaceType == "8" and "0" in scene.WoWVisibility \
                        or self.PlaceType == "8192" and "1" in scene.WoWVisibility:
                    ob.hide = False
                else:
                    ob.hide = True
                success = True

        if success:
            self.report({'INFO'}, "Successfully converted select objects to WMO groups")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No mesh objects found among selected objects")
            return {'CANCELLED'}


class OBJECT_OP_To_WoWMaterial(bpy.types.Operator):
    bl_idname = 'scene.wow_selected_objects_to_wow_material'
    bl_label = 'Materials of selected objects to WoW Material'
    bl_description = 'Transfer all materials of selected objects to WoW material'
    bl_options = {'REGISTER', 'UNDO'}

    Flags = bpy.props.EnumProperty(
        name="Material flags",
        description="WoW material flags",
        items=material_flag_enum,
        options={"ENUM_FLAG"}
    )

    Shader = bpy.props.EnumProperty(
        items=shader_enum,
        name="Shader",
        description="WoW shader assigned to this material"
    )

    BlendingMode = bpy.props.EnumProperty(
        items=blending_enum,
        name="Blending",
        description="WoW material blending mode"
    )

    Texture1 = bpy.props.StringProperty(
        name="Texture 1",
        description="Diffuse texture"
    )

    EmissiveColor = bpy.props.FloatVectorProperty(
        name="Emissive Color",
        subtype='COLOR',
        default=(1, 1, 1, 1),
        size=4,
        min=0.0,
        max=1.0
    )

    Texture2 = bpy.props.StringProperty(
        name="Texture 2",
        description="Environment texture"
    )

    DiffColor = bpy.props.FloatVectorProperty(
        name="Diffuse Color",
        subtype='COLOR',
        default=(1, 1, 1, 1),
        size=4,
        min=0.0,
        max=1.0
    )

    TerrainType = bpy.props.EnumProperty(
        items=terrain_type_enum,
        name="Terrain Type",
        description="Terrain type assigned to this material. Used for producing correct footstep sounds."
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "Shader")
        col.prop(self, "TerrainType")
        col.prop(self, "BlendingMode")

        col.separator()
        col.label("Flags:")
        col.prop(self, "Flags")

        col.separator()
        col.prop(self, "Texture1")
        col.prop(self, "Texture2")

        layout.prop(self, "EmissiveColor")
        layout.prop(self, "DiffColor")

    def execute(self, context):
        success = False
        for ob in bpy.context.selected_objects:
            if ob.WowWMOGroup.Enabled:
                for material in ob.data.materials:
                    material.WowMaterial.Enabled = True
                    material.WowMaterial.Shader = self.Shader
                    material.WowMaterial.BlendingMode = self.BlendingMode
                    material.WowMaterial.TerrainType = self.TerrainType
                    material.WowMaterial.Flags = self.Flags
                    material.WowMaterial.EmissiveColor = self.EmissiveColor
                    material.WowMaterial.DiffColor = self.DiffColor
                success = True

        if success:
            self.report({'INFO'}, "Successfully enabled all materials in the selected WMO groups as WMO materials")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No WMO group objects found among selected objects")
            return {'FINISHED'}


class WOW_WMO_SELECT_ENTITY(bpy.types.Operator):
    bl_idname = 'scene.wow_wmo_select_entity'
    bl_label = 'Select WMO entities'
    bl_description = 'Select all WMO entities of given type'
    bl_options = {'REGISTER', 'INTERNAL'}

    Entity = bpy.props.EnumProperty(
        name="Entity",
        description="Select WMO component entity objects",
        items=[
            ("Outdoor", "Outdoor", ""),
            ("Indoor", "Indoor", ""),
            ("WowPortalPlane", "Portals", ""),
            ("WowLiquid", "Liquids", ""),
            ("WowFog", "Fogs", ""),
            ("WowLight", "Lights", ""),
            ("WoWDoodad", "Doodads", "")
        ]
    )

    def execute(self, context):

        for obj in bpy.context.scene.objects:
            if obj.hide:
                continue

            if obj.type == 'MESH':
                if obj.WowWMOGroup.Enabled:
                    if self.Entity == "Outdoor" and obj.WowWMOGroup.PlaceType == '8':
                        obj.select = True
                    elif self.Entity == "Indoor" and obj.WowWMOGroup.PlaceType == '8192':
                        obj.select = True
                elif self.Entity not in ("WowLight", "Outdoor", "Indoor"):
                    if getattr(obj, self.Entity).Enabled:
                        obj.select = True

            elif obj.type == 'LAMP':
               if self.Entity == "WowLight":
                   obj.select = True

        return {'FINISHED'}