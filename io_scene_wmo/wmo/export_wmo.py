from .wmo_file import WMOFile
from .wmo_group import WMOGroupFile

import bpy
import time


def fix_scene_references():
    """Horrible hack. To be removed with Blender 2.79"""

    def find_valid_object_name(name):
        obj = None
        for i in range(100):
            try:
                obj = bpy.context.scene.objects[name + "." + str(i).zfill(3)]
            except:
                continue
            break

        if obj is None:
            return ""
        else:
            return obj.name

    for obj in bpy.context.scene.objects:
        if obj.WowPortalPlane.Enabled:
            obj.WowPortalPlane.First = find_valid_object_name(obj.WowPortalPlane.First)
            obj.WowPortalPlane.Second = find_valid_object_name(obj.WowPortalPlane.Second)
        if obj.WowWMOGroup.Enabled:
            obj.WowWMOGroup.Fog1 = find_valid_object_name(obj.WowWMOGroup.Fog1)
            obj.WowWMOGroup.Fog2 = find_valid_object_name(obj.WowWMOGroup.Fog2)
            obj.WowWMOGroup.Fog3 = find_valid_object_name(obj.WowWMOGroup.Fog3)
            obj.WowWMOGroup.Fog4 = find_valid_object_name(obj.WowWMOGroup.Fog4)

            obj.WowWMOGroup.Relations.Portals.clear()
            obj.WowWMOGroup.Relations.Doodads.clear()
            obj.WowWMOGroup.Relations.Lights.clear()
            obj.WowWMOGroup.Relations.Liquid = ""

        if obj.WowLiquid.Enabled:
            obj.WowLiquid.WMOGroup = find_valid_object_name(obj.WowLiquid.WMOGroup)


def export_wmo_from_blender_scene(filepath, autofill_textures, export_selected):
    """ Export WoW WMO object from Blender scene to files """

    start_time = time.time()

    #bpy.ops.scene.wow_wmo_validate_scene()
    #print("\nScene successfully validated")

    wmo = WMOFile(filepath)

    print("\n\n### Building object references ###")

    bpy.ops.scene.new(type='FULL_COPY')
    fix_scene_references()  # I am sorry.

    wmo.bl_scene_objects.build_references(export_selected)

    wmo.groups = list([WMOGroupFile(wmo) for _ in wmo.bl_scene_objects.groups])

    try:
        wmo.save_doodad_sets()
        wmo.save_lights()
        wmo.save_liquids()
        wmo.save_fogs()
        wmo.save_portals()

        print("\n\n### Saving WMO groups ###")

        for index, group in enumerate(wmo.groups):
            group.save(wmo.bl_scene_objects.groups[index], autofill_textures)

        wmo.save_root_header()

        wmo.write()

    except Exception as exception:
        for obj in bpy.context.scene.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.ops.scene.delete()

        raise exception

    else:
        for obj in bpy.context.scene.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.ops.scene.delete()

    print("\nExport finished successfully. "
          "\nTotal export time: ", time.strftime("%M minutes %S seconds\a", time.gmtime(time.time() - start_time)))