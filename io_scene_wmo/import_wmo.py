
from . import wmo_format
from .wmo_format import *
from . import wmo_root
from .wmo_root import *
from . import wmo_group
from .wmo_group import *
from . import debug_utils
from .debug_utils import *
from .mpq import wow as mpyq

import os
import time

def OpenAllWMOGroups(rootName):
    i = 0
    group_list = []
    while True:
        groupName = rootName + "_" + str(i).zfill(3) + ".wmo"
        if(os.path.isfile(groupName) == False):
            break
        group = WMO_group_file()
        group.Read(open(groupName, 'rb'))
        group_list.append(group)
        i += 1

    return group_list

def read(filename, file_format, load_textures, import_doodads):

    start_time = time.time()

    f = open(filename, "rb")
    
    # Check if file is WMO root or WMO group, or unknown
    f.seek(12)
    hdr = ChunkHeader()
    hdr.Read(f)
    f.seek(0)
    
    group_list = []
    
    if hdr.Magic == "DHOM":
        # root WMO
        root = WMO_root_file()
        root.Read(f)
        rootName = os.path.splitext(filename)[0]
        group_list.extend(OpenAllWMOGroups(rootName))

    elif hdr.Magic == "PGOM":
        # group WMO

        # load root WMO
        rootName = filename[:-8]
        root = WMO_root_file()
        root.Read(open(rootName + ".wmo", "rb"))
        #group_list.extend(OpenAllWMOGroups(rootName))
        group = WMO_group_file()
        group.Read(f)
        group_list.append(group)

    else:
        LogError(2, "File seems to be corrupted")

    Log(2, True, "Importing WMO components")

    game_data = None

    if load_textures or import_doodads:
        game_data = getattr(bpy, "wow_game_data", None)

        if not game_data:
            Log(2, True, "Loading game data")
            bpy.ops.scene.load_wow_filesystem()
            game_data = bpy.wow_game_data

        if game_data.files:
            if load_textures:
                Log(2, True, "Extracting textures")
                game_data.extract_textures_as_png(os.path.dirname(filename), root.motx.GetAllStrings())
        else:
            Log(1, False, "Failed to load textures because game data was not loaded.")

    display_name = bpy.path.display_name_from_filepath(rootName)
    
    # load all materials in root file
    root.LoadMaterials(display_name, os.path.dirname(filename) + "\\", file_format)

    # load all WMO components
    root.LoadLights(display_name)
    root.LoadProperties(display_name, os.path.dirname(filename) + "\\")
    root.LoadFogs(display_name)
    # root.LoadConvexVolumePlanes(display_name)

    Log(2, True, "Importing group files")
    # create meshes
    for i in range(len(group_list)):
        objName = bpy.path.display_name_from_filepath(group_list[i].filename)
        Log(1, False, "Importing group", objName)
        group_list[i].LoadObject(objName, i, display_name, root, import_doodads)

    root.LoadPortals(display_name, root)

    Log(2, True, "Importing doodad sets")

    if import_doodads and game_data.files:
        root.LoadDoodads(os.path.dirname(filename), game_data)
    else:
        root.LoadDoodads()

    Log(1, False, "Total import time: ", time.strftime("%M minutes %S seconds", time.gmtime(time.time() - start_time)))





