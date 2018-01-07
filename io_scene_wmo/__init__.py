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
    "version": (2, 0),
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

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper

from .wmo.ui import enums
from .wmo.ui import operators
from .wmo.ui import panels
from . import addon_updater_ops
from .idproperty import idproperty
from .mpq import wow as mpq
from .wmo import export_wmo
from .wmo import import_wmo
from .wmo import wmo_file
from .wmo import wmo_group

importlib.reload(wmo_file)
importlib.reload(wmo_group)
importlib.reload(import_wmo)
importlib.reload(export_wmo)
importlib.reload(enums)
importlib.reload(operators)
importlib.reload(panels)
importlib.reload(mpq)

class WMOPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    wow_path = StringProperty(
        name="WoW Client Path",
        subtype='DIR_PATH'
    )

    fileinfo_path = StringProperty(
        name="Path to fileinfo.exe",
        subtype='FILE_PATH'
    )

    wmv_path = StringProperty(
        name="WoW Model Viewer Log Path",
        subtype='FILE_PATH'
    )

    blp_path = StringProperty(
        name="BLP Converter Path",
        subtype='FILE_PATH'
    )

    # addon updater preferences

    auto_check_update = bpy.props.BoolProperty(
        name = "Auto-check for Update",
        description = "If enabled, auto-check for updates using an interval",
        default = True,
        )

    updater_intrval_months = bpy.props.IntProperty(
        name='Months',
        description = "Number of months between checking for updates",
        default=0,
        min=0
        )
    updater_intrval_days = bpy.props.IntProperty(
        name='Days',
        description = "Number of days between checking for updates",
        default=7,
        min=0,
        )
    updater_intrval_hours = bpy.props.IntProperty(
        name='Hours',
        description = "Number of hours between checking for updates",
        default=0,
        min=0,
        max=23
        )
    updater_intrval_minutes = bpy.props.IntProperty(
        name='Minutes',
        description = "Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
        )

    def draw(self, context):
        self.layout.prop(self, "wow_path")
        self.layout.prop(self, "wmv_path")
        self.layout.prop(self, "blp_path")
        self.layout.prop(self, "fileinfo_path")
        addon_updater_ops.update_settings_ui(self, context)

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

    group_objects = BoolProperty(
        name="Group objects",
        description="Group all objects of this WMO on import",
        default=False,
        )

    def execute(self, context):
        import_wmo.import_wmo_to_blender_scene(self.filepath, self.load_textures, self.import_doodads, self.group_objects)
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

    filter_glob = StringProperty(
        default="*.wmo",
        options={'HIDDEN'}
    )

    export_selected = BoolProperty(
        name="Export selected objects",
        description="Makes the exporter export only selected objects on the scene",
        default=False,
        )

    autofill_textures = BoolProperty(
        name="Fill texture paths",
        description="Automatically fills WoW Material texture paths based on texture filenames",
        default=True,
        )


    def execute(self, context):
        export_wmo.export_wmo_from_blender_scene(self.filepath, self.autofill_textures, self.export_selected)

        return {'FINISHED'}


def menu_import(self, context):
    self.layout.operator(WMOImporter.bl_idname, text="Wow WMO (.wmo)")


def menu_export(self, context):
    self.layout.operator(WMOExporter.bl_idname, text="Wow WMO (.wmo)")


def register():
    addon_updater_ops.register(bl_info)
    idproperty.register()
    bpy.utils.register_module(__name__)
    panels.register()
    bpy.types.INFO_MT_file_import.append(menu_import)
    bpy.types.INFO_MT_file_export.append(menu_export)


def unregister():
    bpy.utils.unregister_module(__name__)
    panels.unregister()
    bpy.types.INFO_MT_file_import.remove(menu_import)
    bpy.types.INFO_MT_file_export.remove(menu_export)
    idproperty.unregister()

if __name__ == "__main__":
    register()