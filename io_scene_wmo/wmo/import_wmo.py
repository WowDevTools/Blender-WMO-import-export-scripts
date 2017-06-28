import bpy
import os
import time

from .wmo_file import WMOFile


def import_wmo_to_blender_scene(filepath, load_textures, import_doodads):
    """ Read and import WoW WMO object to Blender scene"""

    start_time = time.time()

    wmo = WMOFile(filepath)
    wmo.read()

    print("\n\n### Importing WMO components ###")

    game_data = None

    if load_textures or import_doodads:
        game_data = getattr(bpy, "wow_game_data", None)

        if not game_data:
            print("\n\n### Loading game data ###")
            bpy.ops.scene.load_wow_filesystem()
            game_data = bpy.wow_game_data

        if game_data.files:
            if load_textures:
                print("\n\n### Extracting textures ###")
                game_data.extract_textures_as_png(os.path.dirname(filepath), wmo.motx.get_all_strings())
        else:
            print("\nFailed to load textures because game data was not loaded.")

    display_name = os.path.basename(os.path.splitext(filepath)[0])

    # load all materials in root file
    wmo.load_materials(display_name, os.path.dirname(filepath) + "\\")

    # load all WMO components
    wmo.load_lights(display_name)
    wmo.load_properties(display_name)
    wmo.load_fogs(display_name)

    print("\n\n### Importing WMO groups ###")

    for group in wmo.groups:
        obj_name = wmo.mogn.get_string(group.mogp.GroupNameOfs)
        print("\nImporting group <<{}>>".format(obj_name))
        group.load_object(obj_name, display_name, import_doodads)

    wmo.load_portals(display_name, wmo)

    print("\n\n### Importing WMO doodad sets ###")

    if import_doodads and game_data.files:
        wmo.load_doodads(os.path.dirname(filepath), game_data)
    else:
        wmo.load_doodads()

    print("\nDone importing WMO. \nTotal import time: ",
          time.strftime("%M minutes %S seconds.\a", time.gmtime(time.time() - start_time)))
