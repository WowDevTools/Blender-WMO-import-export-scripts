
from . import wmo_format
from .wmo_format import *
from . import wmo_root
from .wmo_root import *
from . import wmo_group
from .wmo_group import *
from . import debug_utils
from .debug_utils import *

import os
import time

def write(filepath, source_doodads, autofill_textures, export_selected):

    start_time = time.time()
    
    bpy.ops.scene.wow_wmo_validate_scene
    Log(1, True, "Scene successfuly validated")

    f = open(filepath, "wb")
    root_filename = filepath
    
    base_name = os.path.splitext(filepath)[0]

    group_counter = 0
    portal_counter = 0
    fog_counter = 0
    lamp_counter = 0

    reference_map = {}

    def link_object(object):
        bpy.context.scene.objects.link(object)
        object.use_fake_user = False

    safety_watcher = SceneSafetyWatcher(link_object)

    # ref: fogs, liquid, portals, lights

    for object in bpy.context.scene.objects:

        if object.type == "MESH" and object.WoWDoodad.Enabled:
                safety_watcher.objects.append(object)
                object.use_fake_user = True
                bpy.context.scene.objects.unlink(object)
                continue

        if object.hide:
            continue
        elif export_selected and not object.select:
            object.select = False
            continue
        else:
            object.select = False

        # find references
        if object.type == "MESH":

            if object.WowWMOGroup.Enabled:
                object.WowWMOGroup.GroupID = group_counter
                group_counter += 1

                fogs = (object.WowWMOGroup.Fog1, object.WowWMOGroup.Fog2,
                        object.WowWMOGroup.Fog3, object.WowWMOGroup.Fog4)

                ref = reference_map.setdefault(object.name, [None, None, [], []])
                ref[0] = fogs

            elif object.WowLiquid.Enabled:
                ref = reference_map.setdefault(object.WowLiquid.WMOGroup, [None, None, [], []])
                ref[1] = object.name

            elif object.WowPortalPlane.Enabled:
                object.WowPortalPlane.PortalID = portal_counter
                portal_counter += 1

                groups = (object.WowPortalPlane.First, object.WowPortalPlane.Second)

                for group in groups:
                    if group:
                        ref = reference_map.setdefault(group, [None, None, [], []])
                        ref[2].append(object.name)

            elif object.WowFog.Enabled:
                object.WowFog.FogID = fog_counter
                fog_counter += 1


        elif object.type == "LAMP" and object.data.WowLight.Enabled:
            if object.parent:
                ref = reference_map.setdefault(object.parent, [None, None, [], []])
                ref[3].append(lamp_counter)
            lamp_counter += 1

        # prepare object for export
        bpy.context.scene.objects.active = object
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.objects.active = None


    wmo_root = WMO_root_file()

    Log(2, True, "Saving group files")
    wmo_groups = []

    group_list = list(reference_map.keys())
    group_list.sort()

    for group in group_list:

        obj = bpy.context.scene.objects[group]
        group_id = obj.WowWMOGroup.GroupID

        group_filename = base_name + "_" + str(group_id).zfill(3) + ".wmo"

        wmo_group = WMO_group_file()
        wmo_group.Save(obj, wmo_root, group_id, source_doodads, 
                       autofill_textures, group_filename, reference_map.get(group))

        wmo_groups.append(wmo_group)

    # reveal temporary hidden objects
    del safety_watcher

    # write group files
    Log(1, True, "Writing group files")
    for group in wmo_groups:
        group.Write()
        
    # save root file
    Log(2, True, "Saving root file")
    wmo_root.Save(source_doodads, autofill_textures, portal_counter)
    
    # write root file
    Log(2, True, "Writing root file")
    wmo_root.Write(f)

    Log(1, False, "Total export time: ", time.strftime("%M minutes %S seconds", time.gmtime(time.time() - start_time)))
    
    return