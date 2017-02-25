
from . import wmo_format
from .wmo_format import *
from . import wmo_root
from .wmo_root import *
from . import wmo_group
from .wmo_group import *

import os

def write(filepath, fill_water, source_doodads, autofill_textures, export_selected):
    f = open(filepath, "wb")
    root_filename = filepath

    wmo_root = WMO_root_file()
    
    base_name = os.path.splitext(filepath)[0]
    
    portal_count = 0
    for ob in bpy.context.scene.objects:
        if(ob.type == "MESH"):
            if(ob.WowPortalPlane.Enabled):
                ob.WowPortalPlane.PortalID = portal_count
                portal_count+=1
    
    iObj = 0
    mohd_0x1 = True
    
    for i in range(len(bpy.context.scene.objects)):
        
        #check if selected (optional)
        if bpy.data.objects[i].select != True and export_selected:
            continue
    
        # check if object is mesh
        """"if (not isinstance(bpy.context.selected_objects[iObj].data, bpy.types.Mesh)):
            continue
        
        # check if object is portal
        if(bpy.context.selected_objects[iObj].data.WowPortalPlane.Enabled):
            continue"""
        
        if (not isinstance(bpy.context.scene.objects[i].data, bpy.types.Mesh)):
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
        
        print("Export group "+bpy.context.scene.objects[i].name)
        group_filename = base_name + "_" + str(iObj).zfill(3) + ".wmo"
        group_file = open(group_filename, "wb")

        # write group file
        wmo_group = WMO_group_file()
        
        wmo_root.groupMap[iObj] = bpy.context.scene.objects[i]
        
        if mohd_0x1:
            mohd_0x1 = wmo_group.Save(group_file, bpy.context.scene.objects[i], wmo_root, iObj, source_doodads, autofill_textures)
        else:
            wmo_group.Save(group_file, bpy.context.scene.objects[i], wmo_root, iObj, source_doodads, autofill_textures)
            

        iObj+=1
        
    # write root file
    print("Export root file") 
    wmo_root.Save(f, fill_water, source_doodads, autofill_textures, mohd_0x1)
    return
