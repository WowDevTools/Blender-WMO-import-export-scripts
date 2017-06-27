import bpy
import os
from . import m2 as m2_
from . import skin as skin_


def m2_to_blender_mesh(dir, filepath, filedata):
    """Import World of Warcraft M2 model to scene."""

    print("\nImporting model: <<" + filepath + ">>")

    active_obj = bpy.context.scene.objects.active
    is_select = bpy.context.scene.objects.active.select if active_obj else False

    m2_path = os.path.splitext(filepath)[0] + ".m2"
    skin_path = os.path.splitext(filepath)[0] + "00.skin"

    m2_file = filedata.read_file(m2_path)
    skin_file = filedata.read_file(skin_path)

    m2 = m2_.M2File((m2_file, os.path.basename(m2_path)))
    skin = skin_.SkinFile((skin_file, os.path.basename(skin_path)))

    if not m2 or not skin:
        print("Failed to import: <<" + filepath + ">> Model import seems to have failed.")

    name = m2.name.decode("utf-8")

    vertices = []
    polygons = []
    normals = []
    tex_coords = []

    for vertex in m2.vertices:
        vertices.append((vertex.pos.x, vertex.pos.y, vertex.pos.z))
        tex_coords.append(vertex.uv)
        normals.append(vertex.normal)

    for polygon in skin.tri:
        face = []
        for index in polygon.indices:
            face.append(skin.indices[index].Id)

        polygons.append(face)

    # create mesh
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], polygons)

    for poly in mesh.polygons:
        poly.use_smooth = True

    # set normals
    for index, vertex in enumerate(mesh.vertices):
        vertex.normal = normals[index]

    # set uv
    uv1 = mesh.uv_textures.new("UVMap")
    uv_layer1 = mesh.uv_layers[0]
    for i in range(len(uv_layer1.data)):
        uv = tex_coords[mesh.loops[i].vertex_index]
        uv_layer1.data[i].uv = (uv[0], 1 - uv[1])

    # unpack and convert textures
    texture_paths = []
    for texture in m2.textures:
        texture_paths.append(texture.name.decode("utf-8").rstrip('\0'))

    filedata.extract_textures_as_png(dir, texture_paths)

    # set textures
    for batch in skin.texunit:
        m2_mesh = skin.mesh[batch.submesh]

        # check if forced decompression is required here !!!
        path = os.path.splitext(
            m2.textures[m2.tex_lookup[batch.texture].Id].name.decode("utf-8").rstrip('\0')
        )[0] + ".png"

        img = None

        try:
            img = bpy.data.images.load(os.path.join(dir, path), check_existing=True)
        except:
            print("\nFailed to load texture: " + path + " File is missing or invalid.")

        if img:
            for i in range(m2_mesh.tri_offset // 3, (m2_mesh.tri_offset + m2_mesh.num_tris) // 3):
                uv1.data[i].image = img

    # create object
    scn = bpy.context.scene

    for o in scn.objects:
        o.select = False

    nobj = bpy.data.objects.new(name, mesh)
    scn.objects.link(nobj)

    if active_obj:
        bpy.context.scene.objects.active = active_obj
        active_obj.select = is_select

    return nobj


def wmv_get_last_m2():
    """Get the path of last M2 model from WoWModelViewer or similar log."""

    preferences = bpy.context.user_preferences.addons.get("io_scene_wmo").preferences

    if preferences.wmv_path:

        lines = open(preferences.wmv_path).readlines()

        for line in reversed(lines):
            if 'Loading model:' in line:
                return line[25:].split(",", 1)[0].rstrip("\n")


class WoW_WMO_Import_Doodad_WMV(bpy.types.Operator):
    bl_idname = 'scene.wow_wmo_import_doodad_from_wmv'
    bl_label = 'Import last M2 from WMV'
    bl_description = 'Import last M2 from WoW Model Viewer'
    bl_options = {'REGISTER'}

    def execute(self, context):

        game_data = getattr(bpy, "wow_game_data", None)

        if not game_data or not game_data.files:
            self.report({'ERROR'}, "Failed to import model. Connect to game client first.")
            return {'CANCELLED'}

        dir = bpy.path.abspath("//") if bpy.data.is_saved else None
        m2_path = wmv_get_last_m2()

        if not m2_path:
            self.report({'ERROR'}, """WoW Model Viewer log contains no model entries.
            Make sure to use compatible WMV version or open an .m2 there.""")
            return {'CANCELLED'}

        obj = None

        if dir:
            try:
                obj = m2_to_blender_mesh(dir, m2_path, game_data)
            except NotImplementedError:
                bpy.ops.mesh.primitive_cube_add()
                obj = bpy.context.scene.objects.active
                self.report({'WARNING'}, "Model is encrypted. Placeholder is imported instead.")
            except:
                bpy.ops.mesh.primitive_cube_add()
                obj = bpy.context.scene.objects.active
                self.report({'WARNING'}, "Failed to import model. Placeholder is imported instead.")
            else:
                self.report({'INFO'}, "Imported model: {}".format(m2_path))

            if bpy.context.scene.objects.active and bpy.context.scene.objects.active.select:
                obj.location = bpy.context.scene.objects.active.location
            else:
                obj.location = bpy.context.scene.cursor_location

            obj.WoWDoodad.Enabled = True
            obj.WoWDoodad.Path = m2_path

            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.objects.active = obj
            obj.select = True

        else:
            self.report({'ERROR'}, "Failed to import model. "
                                   "Save your blendfile first.")
            return {'CANCELLED'}

        return {'FINISHED'}
