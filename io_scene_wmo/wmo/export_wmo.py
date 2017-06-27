from .wmo_file import WMOFile
from .wmo_group import WMOGroupFile

import bpy
import time


def export_wmo_from_blender_scene(filepath, autofill_textures, export_selected):
    """ Export WoW WMO object from Blender scene to files """

    start_time = time.time()

    # bpy.ops.scene.wow_wmo_validate_scene()
    # print("\nScene successfully validated")

    wmo = WMOFile(filepath)

    wmo.bl_scene_objects.build_references(export_selected)

    wmo.groups = list([WMOGroupFile(wmo) for _ in wmo.bl_scene_objects.groups])

    wmo.save_doodad_sets()

    # temporary unlink doodad sets to increase performance
    for set in wmo.bl_scene_objects.doodad_sets:
        for doodad in set[1]:
            doodad.use_fake_user = True
            bpy.context.scene.objects.unlink(doodad)

    wmo.save_lights()
    wmo.save_liquids()
    wmo.save_fogs()

    def restore_doodads():
        for set in wmo.bl_scene_objects.doodad_sets:
            for doodad in set[1]:
                bpy.context.scene.objects.link(doodad)
                doodad.use_fake_user = False

    try:
        wmo.save_portals()

        print("\n\n### Saving WMO groups ###")
        g_start_time = time.time()

        for index, group in enumerate(wmo.groups):
            obj = wmo.bl_scene_objects.groups[index]
            proxy_obj = obj.copy()
            proxy_obj.data = obj.data.copy()
            bpy.context.scene.objects.link(proxy_obj)
            try:
                group.save(obj, proxy_obj, autofill_textures)
            except Exception as exception:
                bpy.data.objects.remove(proxy_obj, do_unlink=True)
                raise exception
            else:
                bpy.data.objects.remove(proxy_obj, do_unlink=True)

        print("\nDone saving groups. "
              "\nTotal saving time: ", time.strftime("%M minutes %S seconds", time.gmtime(time.time() - g_start_time)))

        wmo.save_root_header()

    except Exception as exception:
        restore_doodads()
        wmo.bl_scene_objects.clear_references()
        raise exception
    else:
        restore_doodads()
        wmo.bl_scene_objects.clear_references()

    wmo.write()

    print("\nExport finished successfully. "
          "\nTotal export time: ", time.strftime("%M minutes %S seconds\a", time.gmtime(time.time() - start_time)))
