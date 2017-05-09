# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>


bl_info = {
    "name": "Wow WMO format (.wmo)",
    "author": "Happyhack, Skarn",
    "version": (1, 1),
    "blender": (2, 78, 0),
    "location": "File > Import-Export > WoW WMO (.wmo) ",
    "description": "Import-Export WoW WMO",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"
        "Scripts/Import-Export/Wow_WMO_IO",
    "tracker_url": "https://developer.blender.org/T25692",
    "category": "Import-Export"}
    
# load and reload submodules
##################################

import importlib
from . import developer_utils
importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())


if "bpy" in locals():
    import imp
    #if "wow_custom_ui" in locals():
    #    imp.reload(wow_custom_ui)
    if "import_wmo" in locals():
        imp.reload(import_wmo)
    if "export_wmo" in locals():
        imp.reload(export_wmo)
else:
    import bpy
    
from bpy.props import IntProperty, StringProperty, BoolProperty, FloatVectorProperty
from bpy_extras.io_utils import ExportHelper

from . import wow_custom_ui
from . import debug_utils
from .idproperty import idproperty
#from . import Utility

class WMOPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    wow_path = StringProperty(name="WoW Client Path")
    wmv_path = StringProperty(name="WoW Model Viewer Log Path")
    blp_path = StringProperty(name="BLP Converter Path")

    def draw(self, context):
        self.layout.prop(self, "wow_path")
        self.layout.prop(self, "wmv_path")
        self.layout.prop(self, "blp_path")

class WMOImporter(bpy.types.Operator):
    """Load WMO mesh data"""
    bl_idname = "import_mesh.wmo"
    bl_label = "Import WMO"
    bl_options = {'UNDO'}
    
    filepath = StringProperty(
        subtype='FILE_PATH',
        )

    filter_glob = StringProperty(
        default="*.wmo", 
        options={'HIDDEN'}
        )
    
    formatEnum = [('.png', "PNG", ""), ('.bmp', "BMP", ""), ('.dds', "DDS", ""), 
                  ('.jpg', "JPG", ""), ('.tga', "TGA", ""), ('.tiff', "TIFF", "")]
        
    texture_format = bpy.props.EnumProperty(
        items=formatEnum, 
        name="Texture format", 
        description="Choose your texture file format"
        )

    load_textures = BoolProperty(
        name="Fetch textures",
        description="Automatically fetch textures from game data",
        default=True,
        )

    import_doodads = BoolProperty(
        name="Import doodad sets",
        description="Import WMO doodad set to scene",
        default=True,
        )

    def execute(self, context):
        from . import import_wmo
        import_wmo.read(self.filepath, self.texture_format, self.load_textures, self.import_doodads)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


class WMOExporter(bpy.types.Operator, ExportHelper):
    """Save WMO mesh data"""
    bl_idname = "export_mesh.wmo"
    bl_label = "Export WMO"
    bl_options = {'PRESET'}

    filename_ext = ".wmo"
    filter_glob = StringProperty(default="*.wmo", options={'HIDDEN'})
    
    export_selected = BoolProperty(
        name="Export selected objects",
        description="Makes the exporter export only selected objects on the scene",
        default=False,
        )
        
    source_doodads = BoolProperty(
        name="Save source doodads",
        description="Save source doodads",
        default=True,
        )
    
    autofill_textures = BoolProperty(
        name="Fill texture paths",
        description="Automatically fills WoW Material texture paths based on texture filenames",
        default=True,
        )           

    """apply_modifiers = BoolProperty(
            name="Apply Modifiers",
            description="Use transformed mesh data from each object",
            default=True,
            )
    """
    
    def execute(self, context):
        from . import export_wmo
        export_wmo.write(self.filepath, self.source_doodads, self.autofill_textures, self.export_selected)

        return {'FINISHED'}


def menu_import(self, context):
    self.layout.operator(WMOImporter.bl_idname, text="Wow WMO (.wmo)")


def menu_export(self, context):
    self.layout.operator(WMOExporter.bl_idname, text="Wow WMO (.wmo)")


def register():
    idproperty.register()
    bpy.utils.register_module(__name__)
    wow_custom_ui.register()

    bpy.types.INFO_MT_file_import.append(menu_import)
    bpy.types.INFO_MT_file_export.append(menu_export)


def unregister():
    bpy.utils.unregister_module(__name__)
    wow_custom_ui.unregister()

    bpy.types.INFO_MT_file_import.remove(menu_import)
    bpy.types.INFO_MT_file_export.remove(menu_export)
    
    idproperty.unregister()

if __name__ == "__main__":
    register()
