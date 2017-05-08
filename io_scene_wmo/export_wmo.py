
from . import wmo_format
from .wmo_format import *
from . import wmo_root
from .wmo_root import *
from . import wmo_group
from .wmo_group import *
from . import debug_utils
from .debug_utils import *

import os

def write(filepath, source_doodads, autofill_textures, export_selected):
    
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

    # ref: fogs, liquid, portals, lights

    for object in bpy.context.scene.objects:

        if object.hide and (export_selected and not object.select):
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
                ref = reference_map.setdefault(group.name, [None, None, [], []])
                ref[1] = object.WoWLiquid.WMOGroup

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
            ref = reference_map.setdefault(group.parent, [None, None, [], []])
            ref[3].append(lamp_counter)
            lamp_counter += 1

        # prepare object for export
        bpy.context.scene.objects.active = object
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.objects.active = None

    wmo_root = WMO_root_file()

    Log(2, True, "Saving group files")
    wmo_groups = []

    for group in reversed(reference_map.keys()):

        obj = bpy.context.scene.objects[group]
        group_id = obj.WowWMOGroup.GroupID

        group_filename = base_name + "_" + str(group_id).zfill(3) + ".wmo"

        wmo_group = WMO_group_file()
        wmo_group.Save(obj, wmo_root, group_id, source_doodads, autofill_textures, group_filename)
        wmo_groups.append(wmo_group)

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
    
    return

'''           
def write(filepath, source_doodads, autofill_textures, export_selected):
    bpy.ops.scene.wow_wmo_validate_scene
    Log(1, True, "Scene successfuly validated")

    f = open(filepath, "wb")
    root_filename = filepath
    
    base_name = os.path.splitext(filepath)[0]
    
    selectedMap = {}
    
    portal_count = 0
    for ob in bpy.context.scene.objects:
        if ob.type == "MESH":
            if ob.WowPortalPlane.Enabled:
                ob.WowPortalPlane.PortalID = portal_count
                portal_count += 1
                
        bpy.context.scene.objects.active = ob
        
        if not ob.hide:
            bpy.ops.object.mode_set(mode='OBJECT')
        
        if ob.select == True:
            if(ob.type == 'MESH' and ob.WowWMOGroup.Enabled):
                selectedMap[ob] = False
            ob.select = False
                
        bpy.context.scene.objects.active = None
            
    wmo_root = WMO_root_file()
    wmo_groups = {}
    
    iObj = 0
    
    Log(2, True, "Saving group files")

    nObjects = len(bpy.context.scene.objects)
    
    for i in range(nObjects):
        index = nObjects - i - 1

        # check if object is mesh       
        if bpy.context.scene.objects[index].type != 'MESH':
            continue
        
        # check if object is hidden
        if bpy.context.scene.objects[index].hide == True:
            continue
        
        # check if selected (optional)
        if export_selected and selectedMap.get(bpy.context.scene.objects[index], True):
            continue
        
        # check if object is portal
        if bpy.context.scene.objects[index].WowPortalPlane.Enabled:
            continue
        
        # check if object is a fog
        if bpy.context.scene.objects[index].WowFog.Enabled:
            continue

        # check if object is a liquid
        if bpy.context.scene.objects[index].WowLiquid.Enabled:
            continue

        # check if WoW WMO group is turned off
        if not bpy.context.scene.objects[index].WowWMOGroup.Enabled:
            continue
        
        group_filename = base_name + "_" + str(iObj).zfill(3) + ".wmo"

        # prepare group files for writing
        wmo_group = WMO_group_file()
        
        wmo_root.groupMap[iObj] = bpy.context.scene.objects[index]
        
        bpy.context.scene.objects[index].select = False
        
        wmo_group.Save(bpy.context.scene.objects[index], 
                       wmo_root, 
                       iObj, 
                       source_doodads, 
                       autofill_textures, 
                       group_filename)
        
        # enumerate the groups
        wmo_group.index = iObj
            
        # append groups files for writing
        wmo_groups[bpy.context.scene.objects[index].name] = wmo_group
        

        iObj+=1
        
    # write group files
    Log(1, True, "Writing group files")
    for name, group in wmo_groups.items():
        group.Write()
        
    # save root file
    Log(2, True, "Saving root file")
    wmo_root.Save(source_doodads, 
                  autofill_textures,
                  wmo_groups, 
                  portal_count)
    
    # write root file
    Log(2, True, "Writing root file")
    wmo_root.Write(f)
    
    return

'''
