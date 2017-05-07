import bpy
import os
import time
from . import m2 as m2_
from . import skin as skin_


def M2ToBlenderMesh(dir, filepath, filedata):

    print("\nImporting model: <<" + filepath + ">>")

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

    return nobj


   