
from . import wmo_format
from .wmo_format import *
from . import wmo_root
from .wmo_root import *
from . import wmo_group
from .wmo_group import *
from . import debug_utils
from .debug_utils import *

import os

def write(filepath, fill_water, source_doodads, autofill_textures, export_selected):
    f = open(filepath, "wb")
    root_filename = filepath
    
    base_name = os.path.splitext(filepath)[0]
    
    selectedMap = {}
    
    portal_count = 0
    for ob in bpy.context.scene.objects:
        if(ob.type == "MESH"):
            if(ob.WowPortalPlane.Enabled):
                ob.WowPortalPlane.PortalID = portal_count
                portal_count += 1
                
        bpy.context.scene.objects.active = ob
        
        if not ob.hide:
            bpy.ops.object.mode_set(mode='OBJECT')
        
        if export_selected:
            if ob.select == True:
                selectedMap[ob] = False
                ob.select = False
            
    
    
    wmo_root = WMO_root_file()
    wmo_groups = {}
    
    iObj = 0
    mohd_0x1 = True
    
    Log(2, True, "Saving group files")
    
    for i in range(len(bpy.context.scene.objects)):
        
        # check if object is mesh       
        if bpy.context.scene.objects[i].type != 'MESH':
            continue
        
        # check if object is hidden
        if bpy.context.scene.objects[i].hide == True:
            continue
        
        #check if selected (optional)
        if export_selected and selectedMap.get(bpy.context.scene.objects[i], True):
            continue
        
        # check if object is portal
        if(bpy.context.scene.objects[i].WowPortalPlane.Enabled):
            continue
        
        # check if object is root source
        if(bpy.context.scene.objects[i].data.WowWMORoot.IsRoot):
            continue
        
        # check if object is a fog
        if(bpy.context.scene.objects[i].WowFog.Enabled):
            continue

        # check if object is a liquid
        if(bpy.context.scene.objects[i].WowLiquid.Enabled):
            continue
        
        group_filename = base_name + "_" + str(iObj).zfill(3) + ".wmo"

        # prepare group files for writing
        wmo_group = WMO_group_file()
        
        wmo_root.groupMap[iObj] = bpy.context.scene.objects[i]
        
        bpy.context.scene.objects[i].select = False
        
        if mohd_0x1:
            mohd_0x1 = wmo_group.Save(bpy.context.scene.objects[i], wmo_root, iObj, source_doodads, autofill_textures, group_filename)
        else:
            wmo_group.Save(bpy.context.scene.objects[i], wmo_root, iObj, source_doodads, autofill_textures, group_filename)
        
        # enumerate the groups
        wmo_group.index = iObj
            
        # append groups files for writing
        wmo_groups[bpy.context.scene.objects[i].name] = wmo_group
        

        iObj+=1
        
    # write group files
    Log(2, True, "Writing group files")
    for name, group in wmo_groups.items():
        group.Write()
        
    # write root file
    Log(2, True, "Writing root file")
    wmo_root.Save(f, fill_water, source_doodads, autofill_textures, mohd_0x1, wmo_groups, portal_count)
    return
