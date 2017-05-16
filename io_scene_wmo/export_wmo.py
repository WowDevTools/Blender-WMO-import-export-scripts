
from . import wmo_format
from .wmo_format import *
from . import wmo_root
from .wmo_root import *
from . import wmo_group
from .wmo_group import *
from . import debug_utils
from .debug_utils import *
from mathutils import Vector

import os
import time

def find_nearest_object(object, objects):
    """Get closest object to another object"""

    dist = 32767
    result = None
    for obj in objects:
        hit = obj.closest_point_on_mesh(object.location)
        hit_dist = (object.location - hit[1]).length 
        if hit_dist < dist:
            dist = hit_dist
            result = obj

    return result

def write(filepath, save_doodads, autofill_textures, export_selected):

    start_time = time.time()
    
    bpy.ops.scene.wow_wmo_validate_scene
    Log(1, True, "Scene successfuly validated")

    with open(filepath, "wb") as f:
        root_filename = filepath
    
        base_name = os.path.splitext(filepath)[0]

        group_counter = 0
        portal_counter = 0
        fog_counter = 0
        lamp_counter = 0
        doodad_counter = 0

        groups = []

        wmo_root = WMO_root_file()

        scene = bpy.context.scene

        # find all groups on the scene
        for object in scene.objects:
            if object.hide:
                continue
            elif export_selected and not object.select:
                object.select = False
                continue
            else:
                object.select = False

            if object.WowWMOGroup.Enabled:
                    object.WowWMOGroup.GroupID = group_counter
                    groups.append(object)

                    group_counter += 1

                    object.WowWMOGroup.Relations.Portals.clear()
                    object.WowWMOGroup.Relations.Doodads.clear()
                    object.WowWMOGroup.Relations.Lights.clear()

                    bpy.context.scene.objects.active = object
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.context.scene.objects.active = None

        # set references
        for object in scene.objects:

            if object.type == "EMPTY":
                doodad_set = (object.name, [])

                for obj in object.children:
                    if obj.WoWDoodad.Enabled:

                        group = find_nearest_object(obj, groups)
                        if group:
                            rel = group.WowWMOGroup.Relations.Doodads.add()
                            rel.id = doodad_counter  
                            doodad_set[1].append(obj)
                            doodad_counter += 1

                        obj.use_fake_user = True
                        scene.objects.unlink(obj)

                if doodad_set[1]:
                    wmo_root.doodad_sets.append(doodad_set)

            if object.type == "MESH":

                if not object.WoWDoodad.Enabled or not object.WowWMOGroup.Enabled:
                    # prepare object for export
                    bpy.context.scene.objects.active = object
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.context.scene.objects.active = None

                if object.WowLiquid.Enabled:
                    group = scene.objects[object.WowLiquid.WMOGroup]
                    group.WowWMOGroup.Relations.Liquid = object.name

                elif object.WowPortalPlane.Enabled:
                    object.WowPortalPlane.PortalID = portal_counter
                    portal_counter += 1

                    group_objs = (object.WowPortalPlane.First, object.WowPortalPlane.Second)

                    for group in group_objs:
                        if group:
                            rel = scene.objects[group].WowWMOGroup.Relations.Portals.add()
                            rel.id = object.name

                elif object.WowFog.Enabled:
                    object.WowFog.FogID = fog_counter

                    fog_counter += 1


            elif object.type == "LAMP" and object.data.WowLight.Enabled:
                group = find_nearest_object(object, groups)
                if group:
                    rel = group.WowWMOGroup.Relations.Lights.add()
                    rel.id = lamp_counter

                lamp_counter += 1

        wmo_groups = [None] * len(groups)

        try: 
            Log(2, True, "Saving group files")

            for group in groups:

                obj = bpy.context.scene.objects[group.name]
                group_id = obj.WowWMOGroup.GroupID

                group_filename = base_name + "_" + str(group_id).zfill(3) + ".wmo"

                wmo_group = WMO_group_file()
                wmo_group.Save(obj, wmo_root, group_id, save_doodads, 
                               autofill_textures, group_filename)

                wmo_groups[group_id] = wmo_group

        finally:
            for doodad_set in wmo_root.doodad_sets:
                for doodad in doodad_set[1]:
                    bpy.context.scene.objects.link(doodad)
                    object.use_fake_user = False

        # write group files
        Log(1, True, "Writing group files")
        for group in wmo_groups:
            group.Write()
        
        # save root file
        Log(2, True, "Saving root file")
        wmo_root.Save(save_doodads, autofill_textures, portal_counter)
    
        # write root file
        Log(2, True, "Writing root file")
        wmo_root.Write(f)

        Log(1, False, "Total export time: ", time.strftime("%M minutes %S seconds", time.gmtime(time.time() - start_time)))
    