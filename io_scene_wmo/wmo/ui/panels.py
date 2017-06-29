from .enums import *
from ...idproperty import idproperty

import bpy


###############################
## Root properties
###############################

class WoWRootPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_label = "WoW Root"

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(context.scene.WoWRoot, "Flags")
        col.separator()

        if "2" in context.scene.WoWRoot.Flags:
            col.prop(context.scene.WoWRoot, "AmbientColor")

        col.separator()

        col.prop(context.scene.WoWRoot, "SkyboxPath")
        col.prop(context.scene.WoWRoot, "WMOid")

    @classmethod
    def poll(cls, context):
        return (context.scene is not None)


class MODS_Set(bpy.types.PropertyGroup):
    Name = bpy.props.StringProperty()
    StartDoodad = bpy.props.IntProperty()
    nDoodads = bpy.props.IntProperty()
    Padding = bpy.props.IntProperty()


class MODN_String(bpy.types.PropertyGroup):
    Ofs = bpy.props.IntProperty()
    String = bpy.props.StringProperty()


class MODD_Definition(bpy.types.PropertyGroup):
    NameOfs = bpy.props.IntProperty()
    Flags = bpy.props.IntProperty()
    Position = bpy.props.FloatVectorProperty()
    Rotation = bpy.props.FloatVectorProperty()
    Tilt = bpy.props.FloatProperty()
    Scale = bpy.props.FloatProperty()
    Color = bpy.props.FloatVectorProperty()
    ColorAlpha = bpy.props.FloatProperty()


class WowRootPropertyGroup(bpy.types.PropertyGroup):

    MODS_Sets = bpy.props.CollectionProperty(type=MODS_Set)
    MODN_StringTable = bpy.props.CollectionProperty(type=MODN_String)
    MODD_Definitions = bpy.props.CollectionProperty(type=MODD_Definition)

    Flags = bpy.props.EnumProperty(
        name="Root flags",
        description="WoW WMO root flags",
        items=root_flags_enum,
        options={"ENUM_FLAG"}
        )

    AmbientColor = bpy.props.FloatVectorProperty(
        name="Ambient Color",
        subtype='COLOR',
        default=(1, 1, 1, 1),
        size=4,
        min=0.0,
        max=1.0
        )

    SkyboxPath =  bpy.props.StringProperty(
        name="SkyboxPath",
        description="Skybox for WMO (.MDX)",
        default='',
        )

    WMOid = bpy.props.IntProperty(
        name="WMO DBC ID",
        description="Used in WMOAreaTable (optional)",
        default=0,
        )


def RegisterWowRootProperties():
    bpy.types.Scene.WoWRoot = bpy.props.PointerProperty(type=WowRootPropertyGroup)


def UnregisterWowRootProperties():
    bpy.types.Scene.WoWRoot = None


###############################
## Doodads
###############################

class WoWDoodadPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_label = "WoW Doodad"

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        layout.prop(context.object.WoWDoodad, "Path")
        layout.prop(context.object.WoWDoodad, "Color")

        col = layout.column()
        col.label("Flags:")
        col.prop(context.object.WoWDoodad, "Flags")
        layout.enabled = context.object.WoWDoodad.Enabled

    @classmethod
    def poll(cls, context):
        return (context.object is not None
                and context.object.WoWDoodad.Enabled
                and isinstance(context.object.data, bpy.types.Mesh))


class WoWDoodadPropertyGroup(bpy.types.PropertyGroup):

    Path = bpy.props.StringProperty()

    Color = bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=4,
        default=(1,1,1,1),
        min=0.0,
        max=1.0
        )

    Flags = bpy.props.EnumProperty(
        name ="Doodad flags",
        description ="WoW doodad instance flags",
        items =[
                ("1" , "Accept Projected Tex.", ""),
                ("2", "Adjust lighting", ""),
                ("4", "Unknown", ""),
                ("8", "Unknown", "")],
        options={"ENUM_FLAG"}
        )

    Enabled = bpy.props.BoolProperty(
        name="",
        description="Enable WoW Doodad properties"
        )


def RegisterWoWDoodadProperties():
    bpy.types.Object.WoWDoodad = bpy.props.PointerProperty(type=WoWDoodadPropertyGroup)


def UnregisterWoWDoodadProperties():
    bpy.types.Object.WoWDoodad = None


###############################
## Material
###############################

class WowMaterialPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_label = "WoW Material"

    def draw_header(self, context):
        layout = self.layout
        self.layout.prop(context.material.WowMaterial, "Enabled")

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(context.material.WowMaterial, "Shader")
        col.prop(context.material.WowMaterial, "TerrainType")
        col.prop(context.material.WowMaterial, "BlendingMode")

        col.separator()
        col.prop(context.material.WowMaterial, "Texture1")
        col.prop(context.material.WowMaterial, "Texture2")

        col.separator()
        col.label("Flags:")
        col.prop(context.material.WowMaterial, "Flags")

        layout.prop(context.material.WowMaterial, "EmissiveColor")
        layout.prop(context.material.WowMaterial, "DiffColor")
        layout.enabled = context.material.WowMaterial.Enabled

    @classmethod
    def poll(cls, context):
        return context.material is not None


class WowMaterialPropertyGroup(bpy.types.PropertyGroup):

    Enabled = bpy.props.BoolProperty(
        name="",
        description="Enable WoW material properties"
        )

    Flags = bpy.props.EnumProperty(
        name="Material flags",
        description="WoW material flags",
        items=material_flag_enum,
        options={"ENUM_FLAG"}
        )

    Shader = bpy.props.EnumProperty(
        items=shader_enum,
        name="Shader",
        description="WoW shader assigned to this material"
        )

    BlendingMode = bpy.props.EnumProperty(
        items=blending_enum,
        name="Blending",
        description="WoW material blending mode"
        )

    Texture1 = bpy.props.StringProperty(
        name="Texture 1",
        description="Diffuse texture"
        )

    EmissiveColor = bpy.props.FloatVectorProperty(
        name="Emissive Color",
        subtype='COLOR',
        default=(1,1,1,1),
        size=4,
        min=0.0,
        max=1.0
        )

    Texture2 = bpy.props.StringProperty(
        name="Texture 2",
        description="Environment texture"
        )

    DiffColor = bpy.props.FloatVectorProperty(
        name="Diffuse Color",
        subtype='COLOR',
        default=(1,1,1,1),
        size=4,
        min=0.0,
        max=1.0
        )

    TerrainType = bpy.props.EnumProperty(
        items=terrain_type_enum,
        name="Terrain Type",
        description="Terrain type assigned to this material. Used for producing correct footstep sounds."
        )


def RegisterWowMaterialProperties():
    bpy.types.Material.WowMaterial = bpy.props.PointerProperty(type=WowMaterialPropertyGroup)

def UnregisterWowMaterialProperties():
    bpy.types.Material.WowMaterial = None


###############################
## Light
###############################

class WowLightPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_label = "WoW light"

    def draw_header(self, context):
        self.layout.prop(context.object.data.WowLight, "Enabled")

    def draw(self, context):
        layout = self.layout
        self.layout.prop(context.object.data.WowLight, "LightType")
        self.layout.prop(context.object.data.WowLight, "UseAttenuation")
        self.layout.prop(context.object.data.WowLight, "Color")
        self.layout.prop(context.object.data.WowLight, "Intensity")
        self.layout.prop(context.object.data.WowLight, "AttenuationStart")
        self.layout.prop(context.object.data.WowLight, "AttenuationEnd")
        layout.enabled = context.object.data.WowLight.Enabled

    @classmethod
    def poll(cls, context):
        return (context.object is not None
                and context.object.data is not None
                and isinstance(context.object.data, bpy.types.Lamp)
                )


class WowLightPropertyGroup(bpy.types.PropertyGroup):

    Enabled = bpy.props.BoolProperty(
        name="",
        description="Enable wow light properties"
        )

    LightType = bpy.props.EnumProperty(
        items=light_type_enum,
        name="Type",
        description="Type of the lamp"
        )

    Type = bpy.props.BoolProperty(
        name="Type",
        description="Unknown"
        )

    UseAttenuation = bpy.props.BoolProperty(
        name="Use attenuation",
        description="True if lamp use attenuation"
        )

    Padding = bpy.props.BoolProperty(
        name="Padding",
        description="True if lamp use Padding"
        )

    Color = bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        default=(1,1,1),
        min=0.0,
        max=1.0
        )

    Intensity = bpy.props.FloatProperty(
        name="Intensity",
        description="Intensity of the lamp"
        )

    ColorAlpha = bpy.props.FloatProperty(
        name="ColorAlpha",
        description="Color alpha",
        default=1,
        min=0.0,
        max=1.0
        )

    AttenuationStart = bpy.props.FloatProperty(
        name="Attenuation start",
        description="Distance at which light intensity starts to decrease"
        )

    AttenuationEnd = bpy.props.FloatProperty(
        name="Attenuation end",
        description="Distance at which light intensity reach 0"
        )


def RegisterWowLightProperties():
    bpy.types.Lamp.WowLight = bpy.props.PointerProperty(type=WowLightPropertyGroup)


def UnregisterWowLightProperties():
    bpy.types.Lamp.WowLight = None


###############################
## Vertex Info
###############################

class WowVertexInfoPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_label = "WoW Vertex Info"

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        self.layout.prop_search(context.object.WowVertexInfo, "VertexGroup",
                                context.object, "vertex_groups", text="Collision vertex group"
                                )

        self.layout.prop(context.object.WowVertexInfo, "NodeSize", slider=True)

        self.layout.prop_search(context.object.WowVertexInfo, "BatchTypeA", context.object,
                                "vertex_groups", text="Batch type A vertex group"
                                )

        self.layout.prop_search(context.object.WowVertexInfo, "BatchTypeB",
                                context.object, "vertex_groups", text="Batch type B vertex group"
                                )

        self.layout.prop_search(context.object.WowVertexInfo, "Lightmap",
                                context.object, "vertex_groups", text="Lightmap"
                                )

        self.layout.prop_search(context.object.WowVertexInfo, "Blendmap", context.object,
                                "vertex_groups", text="Blendmap"
                                )

        self.layout.prop_search(context.object.WowVertexInfo, "SecondUV", context.object.data,
                                "uv_textures", text="Second UV"
                                )

    @classmethod
    def poll(cls, context):
        return (context.object is not None
                and context.object.data is not None
                and isinstance(context.object.data,bpy.types.Mesh)
                and context.object.WowWMOGroup.Enabled
                )

class WowVertexInfoPropertyGroup(bpy.types.PropertyGroup):
    VertexGroup = bpy.props.StringProperty()

    NodeSize = bpy.props.IntProperty(
        name="Node max size",
        description="Max count of faces for a node in bsp tree",
        default=2500, min=1,
        soft_max=5000
        )

    BatchTypeA = bpy.props.StringProperty()
    BatchTypeB = bpy.props.StringProperty()
    Lightmap = bpy.props.StringProperty()
    Blendmap = bpy.props.StringProperty()
    SecondUV = bpy.props.StringProperty()

def RegisterWowVertexInfoProperties():
    bpy.types.Object.WowVertexInfo = bpy.props.PointerProperty(type=WowVertexInfoPropertyGroup)

def UnregisterWowVertexInfoProperties():
    bpy.types.Object.WowVertexInfo = None


###############################
## WMO Group
###############################
class WowWMOGroupPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_label = "WoW WMO Group"

    def draw_header(self, context):
        layout = self.layout
        self.layout.prop(context.object.WowWMOGroup, "Enabled")

    def draw(self, context):
        col = self.layout.column()
        col.prop(context.object.WowWMOGroup, "GroupDesc")

        col.separator()
        col.label("Flags:")
        col.prop(context.object.WowWMOGroup, "PlaceType")
        col.prop(context.object.WowWMOGroup, "Flags")

        col.separator()
        col.label("Fogs:")
        idproperty.layout_id_prop(col, context.object.WowWMOGroup, "Fog1")
        idproperty.layout_id_prop(col, context.object.WowWMOGroup, "Fog2")
        idproperty.layout_id_prop(col, context.object.WowWMOGroup, "Fog3")
        idproperty.layout_id_prop(col, context.object.WowWMOGroup, "Fog4")

        col.separator()
        col.prop(context.object.WowWMOGroup, "GroupDBCid")
        col.prop(context.object.WowWMOGroup, "LiquidType")

        idproperty.enabled = context.object.WowLiquid.Enabled
        self.layout.enabled = context.object.WowWMOGroup.Enabled

    @classmethod
    def poll(cls, context):
        return (context.object is not None
                and context.object.data is not None
                and isinstance(context.object.data,bpy.types.Mesh)
                and not context.object.WowPortalPlane.Enabled
                and not context.object.WowLiquid.Enabled
                and not context.object.WowFog.Enabled
                and not context.object.WoWDoodad.Enabled
                )

def fog_validator(ob):
    return ob.WowFog.Enabled

class WowWMOMODRStore(bpy.types.PropertyGroup):
    value = bpy.props.IntProperty(name="Doodads Ref")

class WowWMOPortalRel(bpy.types.PropertyGroup):
    id = bpy.props.StringProperty()

class WowWMOLightRel(bpy.types.PropertyGroup):
    id = bpy.props.IntProperty()

class WowWMODoodadRel(bpy.types.PropertyGroup):
    id = bpy.props.IntProperty()

class WowWMOGroupRelations(bpy.types.PropertyGroup):
    """Used for export internally"""
    Portals = bpy.props.CollectionProperty(type=WowWMOPortalRel)
    Lights = bpy.props.CollectionProperty(type=WowWMOLightRel)
    Liquid = bpy.props.StringProperty()
    Doodads = bpy.props.CollectionProperty(type=WowWMODoodadRel)


class WowWMOGroupPropertyGroup(bpy.types.PropertyGroup):

    GroupDesc = bpy.props.StringProperty(name="Description")

    Enabled = bpy.props.BoolProperty(
        name="",
        description="Enable wow WMO group properties"
        )

    Flags = bpy.props.EnumProperty(
        items=group_flag_enum,
        options={'ENUM_FLAG'}
        )

    PlaceType = bpy.props.EnumProperty(
        items=place_type_enum,
        name="Place Type",
        description="Group is indoor or outdoor"
        )

    GroupID = bpy.props.IntProperty(
        name="",
        description="Group identifier used for export"
        )

    GroupDBCid = bpy.props.IntProperty(
        name="DBC Group ID",
        description="WMO Group ID in DBC file"
        )

    LiquidType = bpy.props.EnumProperty(
        items=liquid_type_enum,
        name="LiquidType",
        description="Fill this WMO group with selected liquid."
        )

    Fog1 = idproperty.ObjectIDProperty(name="Fog #1", validator=fog_validator)

    Fog2 = idproperty.ObjectIDProperty(name="Fog #2", validator=fog_validator)

    Fog3 = idproperty.ObjectIDProperty(name="Fog #3", validator=fog_validator)

    Fog4 = idproperty.ObjectIDProperty(name="Fog #4", validator=fog_validator)


    MODR = bpy.props.CollectionProperty(type=WowWMOMODRStore)

    Relations = bpy.props.PointerProperty(type=WowWMOGroupRelations)

def RegisterWowWMOGroupProperties():
    bpy.types.Object.WowWMOGroup = bpy.props.PointerProperty(type=WowWMOGroupPropertyGroup)

def UnregisterWowWMOGroupProperties():
    bpy.types.Object.WowWMOGroup = None


###############################
## Portal plane
###############################

class WowPortalPlanePanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_label = "WoW Portal Plane"

    def draw_header(self, context):
        layout = self.layout
        self.layout.prop(context.object.WowPortalPlane, "Enabled")

    def draw(self, context):
        layout = self.layout
        row = layout.row()

        column = layout.column()
        idproperty.layout_id_prop(column, context.object.WowPortalPlane, "First")
        idproperty.layout_id_prop(column, context.object.WowPortalPlane, "Second")

        col = layout.column()

        col.separator()
        col.label("Relation direction:")
        col.prop(context.object.WowPortalPlane, "Algorithm", expand=True)

        idproperty.enabled = context.object.WowLiquid.Enabled
        layout.enabled = context.object.WowPortalPlane.Enabled

    @classmethod
    def poll(cls, context):
        return (context.object is not None
                and context.object.data is not None
                and isinstance(context.object.data,bpy.types.Mesh)
                and not context.object.WowWMOGroup.Enabled
                and not context.object.WowLiquid.Enabled
                and not context.object.WowFog.Enabled
                and not context.object.WoWDoodad.Enabled
                )

def portal_validator(ob):
    return ob.type == 'MESH' and ob.WowWMOGroup.Enabled

class WowPortalPlanePropertyGroup(bpy.types.PropertyGroup):

    Enabled = bpy.props.BoolProperty(
        name="",
        description="Enable wow WMO group properties"
        )

    First = idproperty.ObjectIDProperty(
        name="First group",
        validator=portal_validator
        )

    Second = idproperty.ObjectIDProperty(
        name="Second group",
        validator=portal_validator
        )

    PortalID = bpy.props.IntProperty(
        name="Portal's ID",
        description="Portal ID"
        )

    Algorithm = bpy.props.EnumProperty(
        items=portal_dir_alg_enum,
        default="0"
        )


def RegisterWowPortalPlaneProperties():
    bpy.types.Object.WowPortalPlane = bpy.props.PointerProperty(type=WowPortalPlanePropertyGroup)

def UnregisterWowPortalPlaneProperties():
    bpy.types.Object.WowPortalPlane = None

###############################
## Liquid
###############################

class WowLiquidPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_label = "WoW Liquid"

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        self.layout.prop(context.object.WowLiquid, "LiquidType")
        self.layout.prop(context.object.WowLiquid, "Color")

        column = layout.column()
        idproperty.layout_id_prop(column, context.object.WowLiquid, "WMOGroup")

        idproperty.enabled = context.object.WowLiquid.Enabled
        layout.enabled = context.object.WowLiquid.Enabled

    @classmethod
    def poll(cls, context):
        return (context.object is not None
                and context.object.data is not None
                and isinstance(context.object.data,bpy.types.Mesh)
                and context.object.WowLiquid.Enabled
                )

def liquid_validator(ob):
    for object in bpy.context.scene.objects:
        if object.type == 'MESH' and object.WowLiquid.WMOGroup == ob.name:
            bpy.ops.render.report_message(message="Test", type=False )
            return False
    return ob.WowWMOGroup.Enabled

class WowLiquidPropertyGroup(bpy.types.PropertyGroup):

    Enabled = bpy.props.BoolProperty(
        name="",
        description="Enable wow liquid properties",
        default=False
        )

    Color = bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        default=(0.08, 0.08, 0.08, 1),
        size=4,
        min=0.0,
        max=1.0
        )

    LiquidType = bpy.props.EnumProperty(
        items=liquid_type_enum,
        name="Liquid Type",
        description="Type of the liquid present in this WMO group"
        )

    WMOGroup = idproperty.ObjectIDProperty(
        name="WMO Group",
        validator=liquid_validator
        )

def RegisterWowLiquidProperties():
    bpy.types.Object.WowLiquid = bpy.props.PointerProperty(type=WowLiquidPropertyGroup)

def UnregisterWowLiquidProperties():
    bpy.types.Object.WowLiquid = None


###############################
## Fog
###############################
class WowFogPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_label = "WoW Fog"

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        layout.enabled = context.object.WowFog.Enabled
        self.layout.prop(context.object.WowFog, "IgnoreRadius")
        self.layout.prop(context.object.WowFog, "Unknown")
        self.layout.prop(context.object.WowFog, "InnerRadius")
        self.layout.prop(context.object.WowFog, "EndDist")
        self.layout.prop(context.object.WowFog, "StartFactor")
        self.layout.prop(context.object.WowFog, "Color1")
        self.layout.prop(context.object.WowFog, "EndDist2")
        self.layout.prop(context.object.WowFog, "StartFactor2")
        self.layout.prop(context.object.WowFog, "Color2")

    @classmethod
    def poll(cls, context):
        return (context.object is not None
                and context.object.data is not None
                and isinstance(context.object.data,bpy.types.Mesh)
                and context.object.WowFog.Enabled
                )

def UpdateFogColor(self, context):
    bpy.context.scene.objects.active.color = (self.Color1[0], self.Color1[1], self.Color1[2], 0.5)


class WowFogPropertyGroup(bpy.types.PropertyGroup):

    Enabled = bpy.props.BoolProperty(
        name="",
        description="Enable WoW WMO fog properties"
        )

    FogID = bpy.props.IntProperty(
        name="WMO Group ID",
        description="Used internally for exporting",
        default= 0,
        )

    IgnoreRadius = bpy.props.BoolProperty(
        name="Ignore Radius",
        description="Ignore radius in CWorldView::QueryCameraFog",
        default = False
        )

    Unknown = bpy.props.BoolProperty(
        name="Unknown Flag",
        description="Check that in if you know what it is",
        default = False
        )

    InnerRadius = bpy.props.FloatProperty(
        name="Inner Radius (%)",
        description="A radius of fog starting to fade",
        default=100.0,
        min=0.0,
        max=100.0
        )

    EndDist = bpy.props.FloatProperty(
        name="Farclip",
        description="Fog farclip",
        default=70.0,
        min=0.0,
        max=2048.0
        )

    StartFactor = bpy.props.FloatProperty(
        name="Nearclip",
        description="Fog nearclip",
        default=0.1,
        min=0.0,
        max=1.0
        )

    Color1 = bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        default=(1,1,1),
        min=0.0,
        max=1.0,
        update=UpdateFogColor
        )

    EndDist2 = bpy.props.FloatProperty(
        name="Underwater farclip",
        description="Underwater fog farclip",
        default=70.0,
        min=0.0,
        max=250.0
        )

    StartFactor2 = bpy.props.FloatProperty(
        name="Underwater nearclip",
        description="Underwater fog nearclip",
        default=0.1,
        min=0.0,
        max=1.0
        )

    Color2 = bpy.props.FloatVectorProperty(
        name="Underwater Color",
        subtype='COLOR',
        default=(1,1,1),
        min=0.0,
        max=1.0
        )

def RegisterWowFogProperties():
    bpy.types.Object.WowFog = bpy.props.PointerProperty(type=WowFogPropertyGroup)

def UnregisterWowFogProperties():
    bpy.types.Object.WowFog = None


###############################
## WMO Toolbar
###############################

def update_wow_visibility(self, context):
    values = self.WoWVisibility
    for obj in self.objects:
        if obj.type == "MESH":
            if obj.WowWMOGroup.Enabled:
                if obj.WowWMOGroup.PlaceType == '8':
                    obj.hide = False if '0' in values else True
                else:
                    obj.hide = False if '1' in values else True
            elif obj.WowPortalPlane.Enabled:
                obj.hide = False if '2' in values else True
            elif obj.WowFog.Enabled:
                obj.hide = False if '3' in values else True
            elif obj.WowLiquid.Enabled:
                obj.hide = False if '4' in values else True
        elif obj.type == "LAMP" and obj.data.WowLight.Enabled:
            obj.hide = False if '5' in values else True


def update_liquid_flags(self, context):
    value = self.WoWLiquidFlags

    water = bpy.context.scene.objects.active
    mesh = water.data
    if water.WowLiquid.Enabled:
        layer = mesh.vertex_colors.get("flag_" + value)

        if layer:
            layer.active = True
            mesh.use_paint_mask = True
        else:
            layer = mesh.vertex_colors.new("flag_" + value)
            layer.active = True


def get_doodad_sets(self, context):
    has_global = False
    doodad_set_objects = set()
    doodad_sets = []

    for obj in bpy.context.scene.objects:
        if obj.WoWDoodad.Enabled and obj.parent:
            if obj.parent.name != "Set_$DefaultGlobal":
                doodad_set_objects.add(obj.parent)
            else:
                has_global = True

    for index, obj in enumerate(sorted(doodad_set_objects, key=lambda x:x.name), 1 + has_global):
        doodad_sets.append((obj.name, obj.name, "", 'SCENE_DATA', index))

    doodad_sets.insert(0, ("None", "No set", "", 'X', 0))
    if has_global:
        doodad_sets.insert(1, ("Set_$DefaultGlobal", "Set_$DefaultGlobal", "", 'WORLD', 1))

    return doodad_sets


def switch_doodad_set(self, context):
    set = self.WoWDoodadVisibility

    for obj in bpy.context.scene.objects:
        if obj.WoWDoodad.Enabled:
            if obj.parent:
                name = obj.parent.name
                obj.hide = set == "None" or name != set and name != "Set_$DefaultGlobal"
            else:
                obj.hide = True


def RegisterWoWVisibilityProperties():
    bpy.types.Scene.WoWVisibility = bpy.props.EnumProperty(
        items=[
            ('0', "Outdoor", "Display outdoor groups", 'BBOX', 0x1),
            ('1', "Indoor", "Display indoor groups", 'ROTATE', 0x2),
            ('2', "Portals", "Display portals", 'MOD_PARTICLES', 0x4),
            ('3', "Fogs", "Display fogs", 'FORCE_TURBULENCE', 0x8),
            ('4', "Liquids", "Display liquids", 'MOD_FLUIDSIM', 0x10),
            ('5', "Lights", "Display lights", 'LAMP_SPOT', 0x20)],
        options={'ENUM_FLAG'},
        default={'0', '1', '2', '3', '4', '5'},
        update=update_wow_visibility
        )

    bpy.types.Scene.WoWLiquidFlags = bpy.props.EnumProperty(
        items=[
            ('0x1', "Flag 0x01", "Switch to this flag", 'MOD_SOFT', 0),
            ('0x2', "Flag 0x02", "Switch to this flag", 'MOD_SOFT', 1),
            ('0x4', "Flag 0x04", "Switch to this flag", 'MOD_SOFT', 2),
            ('0x8', "Invisible", "Switch to this flag", 'RESTRICT_VIEW_OFF', 3),
            ('0x10', "Flag 0x10", "Switch to this flag", 'MOD_SOFT', 4),
            ('0x20', "Flag 0x20", "Switch to this flag", 'MOD_SOFT', 5),
            ('0x40', "Flag 0x40", "Switch to this flag", 'MOD_SOFT', 6),
            ('0x80', "Flag 0x80", "Switch to this flag", 'MOD_SOFT', 7)],
        default='0x1',
        update=update_liquid_flags
        )

    bpy.types.Scene.WoWDoodadVisibility = bpy.props.EnumProperty(
        name="",
        description="Switch doodad sets",
        items=get_doodad_sets,
        update=switch_doodad_set
        )

def UnregisterWoWVisibilityProperties():
    bpy.types.Scene.WoWVisibility = None
    bpy.types.Scene.WoWLiquidFlags = None
    bpy.types.Scene.WoWDoodadVisibility = None

class WMOToolsPanelObjectMode(bpy.types.Panel):
    bl_label = 'Quick WMO'
    bl_idname = 'WMOQuickPanelObjMode'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_category = 'WMO'

    def draw(self, context):
        layout = self.layout.split()

        has_sets = True if bpy.context.scene.WoWRoot.MODS_Sets else False
        game_data_loaded = hasattr(bpy, "wow_game_data") and bpy.wow_game_data.files

        col = layout.column(align=True)

        col.label(text="Display:")
        col_row = col.row()
        col_row.column(align=True).prop(context.scene, "WoWVisibility")
        col_col = col_row.column(align=True)
        col_col.operator("scene.wow_wmo_select_entity", text='', icon='VIEWZOOM').Entity = 'Outdoor'
        col_col.operator("scene.wow_wmo_select_entity", text='', icon='VIEWZOOM').Entity = 'Indoor'
        col_col.operator("scene.wow_wmo_select_entity", text='', icon='VIEWZOOM').Entity = 'WowPortalPlane'
        col_col.operator("scene.wow_wmo_select_entity", text='', icon='VIEWZOOM').Entity = 'WowFog'
        col_col.operator("scene.wow_wmo_select_entity", text='', icon='VIEWZOOM').Entity = 'WowLiquid'
        col_col.operator("scene.wow_wmo_select_entity", text='', icon='VIEWZOOM').Entity = 'WowLight'

        if not bpy.context.scene.WoWRoot.MODS_Sets:
            box2_row2 = col.row()
            box2_row2.prop(context.scene, "WoWDoodadVisibility", expand=False)
            box2_row2.operator("scene.wow_wmo_select_entity", text='', icon='VIEWZOOM').Entity = 'WoWDoodad'

        col.separator()
        col.label(text="Add to scene:")
        box1 = col.box().column(align=True)
        box1_col = box1.column(align=True)
        box1_row1 = box1_col.row(align=True)
        box1_row1.operator("scene.wow_add_fog", text = 'Fog', icon = 'GROUP_VERTEX')
        box1_row1.operator("scene.wow_add_water", text = 'Water', icon = 'MOD_WAVE')
        box1_row2 = box1_col.row(align=True)
        if game_data_loaded:
            if not has_sets:
                box1_row2.operator("scene.wow_wmo_import_doodad_from_wmv", text='M2', icon = 'LOAD_FACTORY')
                box1_row2.operator("scene.wow_import_last_wmo_from_wmv", text = 'WMO', icon = 'APPEND_BLEND')

        box1_col.operator("scene.wow_add_scale_reference", text = 'Scale', icon = 'OUTLINER_OB_ARMATURE')

        col.label(text="Game data:")
        icon = 'COLOR_GREEN' if game_data_loaded else 'COLOR_RED'
        text = "Unload game data" if game_data_loaded else "Load game data"
        col.operator("scene.load_wow_filesystem", text=text, icon = icon)

        if bpy.context.selected_objects:
            col.separator()
            col.label(text="Selected:")
            box = col.box().column(align=True)
            #box.label(text="Convert:")
            box.menu("view3D.convert_to_menu", text="Convert selected")
            box.label(text="Apply:")
            box_col = box.column(align=True)
            box_col.operator("scene.wow_quick_collision", text='Quick collision', icon='STYLUS_PRESSURE')
            box_col.operator("scene.wow_fill_textures", text='Fill texture paths', icon='FILE_IMAGE')
            box_col.operator("scene.wow_set_portal_dir_alg", text='Set portal dir.', icon='FILE_REFRESH')
            box_col.operator("scene.wow_bake_portal_relations", text='Bake portal rels.', icon='LINKED')
            box.label(text="Doodads:")
            box_col2 = box.column(align=True)
            if not has_sets:
                box_col2.operator("scene.wow_doodad_set_add", text='Add to doodadset', icon='ZOOMIN')
                box_col2.operator("scene.wow_doodads_bake_color", text='Bake color', icon='GROUP_VCOL')
                box_col2.operator("scene.wow_doodad_set_color", text='Set color', icon='COLOR')
                box_col2.operator("scene.wow_doodad_set_template_action", text='Template action', icon='FORCE_MAGNETIC')
            else:
                box_col2.operator("scene.wow_clear_preserved_doodad_sets", text='Clear doodad sets', icon='CANCEL')

class ConvertOperators(bpy.types.Menu):
    bl_label = "Convert"
    bl_idname = "view3D.convert_to_menu"
    bl_options = {'REGISTER'}

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.operator("scene.wow_selected_objects_to_group", text='To WMO group', icon='OBJECT_DATA')
        col.operator("scene.wow_selected_objects_to_wow_material", text='To WMO material', icon='SMOOTH')
        col.operator("scene.wow_selected_objects_to_portals", text='To WMO portal', icon='MOD_MIRROR')
        col.operator("scene.wow_texface_to_material", text='Texface to material', icon='TEXTURE_DATA')

class INFO_MT_mesh_WoW_components_add(bpy.types.Menu):
    bl_label = "WoW"
    bl_idname = "view3D.add_wow_components_menu"
    bl_options = {'REGISTER'}

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.operator("scene.wow_add_fog", text = 'Fog', icon = 'GROUP_VERTEX')
        col.operator("scene.wow_add_water", text = 'Water', icon = 'MOD_WAVE')
        col.operator("scene.wow_add_scale_reference", text = 'Scale', icon = 'OUTLINER_OB_ARMATURE')

        if hasattr(bpy, "wow_game_data") and bpy.wow_game_data.files:
            col.operator("scene.wow_wmo_import_doodad_from_wmv", text='M2', icon='LOAD_FACTORY')
            col.operator("scene.wow_import_last_wmo_from_wmv", text='WMO', icon='APPEND_BLEND')

def wow_components_add_menu_item(self, context):
    self.layout.menu("view3D.add_wow_components_menu", icon = 'SOLO_ON')


class WoWToolsPanelLiquidFlags(bpy.types.Panel):
    bl_label = 'Liquid Flags'
    bl_idname = 'WMOQuickPanelVertexColorMode'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'vertexpaint'
    bl_category = 'WMO'

    def draw(self, context):

        layout = self.layout.split()

        col = layout.column()

        col.label(text="Flags")
        col.prop(context.scene, "WoWLiquidFlags", expand=True)

        col.label(text="Actions")
        col.operator("scene.wow_mliq_change_flags", text = 'Add flag', icon = 'MOD_SOFT').Action = "ADD"
        col.operator("scene.wow_mliq_change_flags", text = 'Fill all', icon = 'OUTLINER_OB_LATTICE').Action = "ADD_ALL"
        col.operator("scene.wow_mliq_change_flags", text = 'Clear flag', icon = 'LATTICE_DATA').Action = "CLEAR"
        col.operator("scene.wow_mliq_change_flags", text = 'Clear all', icon = 'MOD_LATTICE').Action = "CLEAR_ALL"

    @classmethod
    def poll(cls, context):
        return (context.object is not None
                and context.object.data is not None
                and isinstance(context.object.data,bpy.types.Mesh)
                and context.object.WowLiquid.Enabled
                )

def register():
    RegisterWowRootProperties()
    RegisterWoWDoodadProperties()
    RegisterWowMaterialProperties()
    RegisterWowLiquidProperties()
    RegisterWowLightProperties()
    RegisterWowVertexInfoProperties()
    RegisterWowWMOGroupProperties()
    RegisterWowPortalPlaneProperties()
    RegisterWoWVisibilityProperties()
    RegisterWowFogProperties()
    bpy.types.INFO_MT_add.prepend(wow_components_add_menu_item)

def unregister():
    UnregisterWowRootProperties()
    UnregisterWoWDoodadProperties()
    UnregisterWowMaterialProperties()
    UnregisterWowLiquidProperties()
    UnregisterWowLightProperties()
    UnregisterWowVertexInfoProperties()
    UnregisterWowWMOGroupProperties()
    UnregisterWowPortalPlaneProperties()
    UnregisterWoWVisibilityProperties()
    UnregisterWowFogProperties()
    bpy.types.INFO_MT_add.remove(wow_components_add_menu_item)



