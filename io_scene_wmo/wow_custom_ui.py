
import bpy
import bpy.utils
import bpy.types
import os
import sys
import re
from . import wmo_format
from .wmo_format import *
from . import debug_utils
from .debug_utils import *
from .m2 import import_m2 as m2
from bpy.utils import register_module, unregister_module
from .idproperty import idproperty
from .idproperty.idproperty import *

###############################
## Enums
###############################

shaderEnum = [
    ('0', "Diffuse", ""), ('1', "Specular", ""), ('2', "Metal", ""),
    ('3', "Env", ""), ('4', "Opaque", ""), ('5', "EnvMetal", ""),
    ('6', "TwoLayerDiffuse", ""), ('7', "TwoLayerEnvMetal", ""), ('8', "TwoLayerTerrain", ""),
    ('9', "DiffuseEmissive", ""), ('10', "Tangent", ""), ('11', "MaskedEnvMetal", ""),
    ('12', "EnvMetalEmissive", ""), ('13', "TwoLayerDiffuseOpaque", ""), ('14', "TwoLayerDiffuseEmissive", "")
    ]

terrainEnum = [
    ('0', "Dirt", ""), ('1', "Metallic", ""), ('2', "Stone", ""),
    ('3', "Snow", ""), ('4', "Wood", ""), ('5', "Grass", ""),
    ('6', "Leaves", ""), ('7', "Sand", ""), ('8', "Soggy", ""),
    ('9', "Dusty Grass", ""), ('10', "None", ""), ('11', "Water", "")
    ]

blendingEnum = [
    ('0', "Blend_Opaque", ""), ('1', "Blend_AlphaKey", ""), ('2', "Blend_Alpha", ""),
    ('3', "Blend_Add", ""), ('4', "Blend_Mod", ""),('5', "Blend_Mod2x", ""),
    ('6', "Blend_ModAdd", ""), ('7', "Blend_InvSrcAlphaAdd", ""),('8', "Blend_InvSrcAlphaOpaque", ""),
    ('9', "Blend_SrcAlphaOpaque", ""), ('10', "Blend_NoAlphaAdd", ""), ('11', "Blend_ConstantAlpha", "")
    ]

materialFlagEnum = [
    ("1" , "Unlit" , "Disable lighting", 'PMARKER', 0x1),
    ("2", "Unfogged", "Disable fog", 'FORCE_TURBULENCE', 0x2),
    ("4", "Two-sided", "Render from both sides", 'ARROW_LEFTRIGHT', 0x4),
    ("8", "Exterior light", "Ignore local WMO lighting, use world lighting instead", 'PMARKER_SEL', 0x8),
    ("16", "Night Glow", "Used for windows to glow at nighttime", 'PMARKER_ACT', 0x10),
    ("32", "Window", "Unknown, used for windows", 'MOD_WIREFRAME', 0x20),
    ("64", "Clamp_S", "Force texture to use clamp _s adressing", 'TRIA_RIGHT', 0x40),
    ("128", "Clamp_T", "Force texture to use clamp _t adressing", 'TRIA_RIGHT', 0x80)
    ]

groupFlagEnum = [
    ('0', "Vertex color", "Check if you need vertex color in this group", 'COLOR', 0x1),
    ('1', "No local lighting", "Use world-defined lighting in a group", 'PMARKER_SEL', 0x2),
    ('2', "Always draw", "Always draw the model. Disable portal-based geometry culling", 'MOD_PARTICLES', 0x4),
    ('3', "Mounts allowed", "Allow mounts in this indoor group", 'RESTRICT_VIEW_OFF', 0x8),
    ('4', "Use Skybox", "Display WMO skybox in this indoor group", 'WIRE', 0x10)
    ]

placeTypeEnum = [('8', "Outdoor", "", 'CURVE_NCIRCLE', 0), ('8192', "Indoor", "", 'FORCE_FORCE', 1)]


liquidTypeEnum = [
    ('0', "No liquid", ""), ('1', "Water", ""), ('2', "Ocean", ""),
    ('3', "Magma", ""), ('4', "Slime", ""), ('5', "Slow Water", ""),
    ('6', "Slow Ocean", ""), ('7', "Slow Magma", ""), ('8', "Slow Slime", ""),
    ('9', "Fast Water", ""), ('10', "Fast Ocean", ""), ('11', "Fast Magma", ""),
    ('12', "Fast Slime", ""), ('13', "WMO Water", ""), ('14', "WMO Ocean", ""),
    ('15', "Green Lava", ""), ('17', "WMO Water - Interior", ""), ('19', "WMO Magma", ""),
    ('20', "WMO Slime", ""), ('21', "Naxxramas - Slime", ""), ('41', "Coilfang Raid - Water", ""),
    ('61', "Hyjal Past - Water", ""), ('81', "Lake Wintergrasp - Water", ""), ('100', "Basic Procedural Water", ""),
    ('121', "CoA Black - Magma", ""), ('141', "Chamber Magma", ""), ('181', "Orange Slime", "")
    ]

portalDirAlgEnum = [
    ("0", "Auto", "", 'MONKEY', 0),
    ("1", "Positive", "", 'ZOOMIN', 1),
    ("2", "Negative", "", 'ZOOMOUT', 2)
    ]

rootFlagsEnum = [
    ("0", "Auto Attenuation", "Attenuate light on vertices based on distance from portal", 'MOD_MIRROR', 0x1),
    ("1", "Lighten Indoor", "Lighten up all indoor groups automatically", 'LAMP_SUN', 0x2),
    ("2", "Use Ambient", "Use ambient lighting inside indoor groups", 'PMARKER_ACT', 0x4)
     ]

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
        name = "Root flags",
        description = "WoW WMO root flags",
        items=rootFlagsEnum,
        options = {"ENUM_FLAG"}
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
        default= '',
        )

    WMOid = bpy.props.IntProperty(
        name="WMO DBC ID",
        description="Used in WMOAreaTable (optional)",
        default= 0,
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
        name = "Doodad flags",
        description = "WoW doodad instance flags",
        items = [
                ("1" , "Accept Projected Tex." , ""),
                ("2", "Adjust lighting", ""),
                ("4", "Unknown", ""),
                ("8", "Unknown", "")],
        options = {"ENUM_FLAG"}
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
        return (context.material is not None)


class WowMaterialPropertyGroup(bpy.types.PropertyGroup):

    Enabled = bpy.props.BoolProperty(
        name="",
        description="Enable WoW material properties"
        )

    Flags = bpy.props.EnumProperty(
        name = "Material flags",
        description = "WoW material flags",
        items=materialFlagEnum,
        options = {"ENUM_FLAG"}
        )

    Shader = bpy.props.EnumProperty(
        items=shaderEnum,
        name="Shader",
        description="WoW shader assigned to this material"
        )

    BlendingMode = bpy.props.EnumProperty(
        items=blendingEnum,
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
        items=terrainEnum,
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
        layout = self.layout
        self.layout.prop(context.object.data.WowLight, "Enabled")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        self.layout.prop(context.object.data.WowLight, "LightType")
        #self.layout.prop(context.object.data.WowLight, "Type")
        self.layout.prop(context.object.data.WowLight, "UseAttenuation")
        #self.layout.prop(context.object.data.WowLight, "Padding")
        self.layout.prop(context.object.data.WowLight, "Color")
        self.layout.prop(context.object.data.WowLight, "Intensity")
        #self.layout.prop(context.object.data.WowLight, "ColorAlpha")
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
    lightTypeEnum = [
        ('0', "Omni", ""), ('1', "Spot", ""),
        ('2', "Direct", ""), ('3', "Ambient", "")
        ]

    Enabled = bpy.props.BoolProperty(
        name="",
        description="Enable wow light properties"
        )

    LightType = bpy.props.EnumProperty(
        items=lightTypeEnum,
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
        col.prop(context.object.WowWMOGroup, "GroupName")
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

    GroupName = bpy.props.StringProperty(name="Name")
    GroupDesc = bpy.props.StringProperty(name="Description")

    Enabled = bpy.props.BoolProperty(
        name="",
        description="Enable wow WMO group properties"
        )

    Flags = bpy.props.EnumProperty(
        items=groupFlagEnum,
        options={'ENUM_FLAG'}
        )

    PlaceType = bpy.props.EnumProperty(
        items=placeTypeEnum,
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
        items=liquidTypeEnum,
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
        items=portalDirAlgEnum,
        default="0"
        )


def RegisterWowPortalPlaneProperties():
    bpy.types.Object.WowPortalPlane = bpy.props.PointerProperty(type=WowPortalPlanePropertyGroup)

def UnregisterWowPortalPlaneProperties():
    bpy.types.Object.WowPortalPlane = None

###############################
## Liquid
###############################

#XTextures\river\lake_a.1.blp
#XTextures\river\lake_a.1.blp
#XTextures\river\lake_a.1.blp
#XTextures\ocean\ocean_h.1.blp
#XTextures\lava\lava.1.blp
#XTextures\slime\slime.1.blp
#XTextures\slime\slime.1.blp
#XTextures\river\lake_a.1.blp
#XTextures\procWater\basicReflectionMap.1.blp
#XTextures\river\lake_a.1.blp
#XTextures\river\lake_a.1.blp
#XTextures\river\fast_a.1.blp
#XTextures\ocean\ocean_h.1.blp
#XTextures\ocean\ocean_h.1.blp
#XTextures\lava\lava.1.blp
#XTextures\lava\lava.1.blp
#XTextures\slime\slime.1.blp
#XTextures\slime\slime.1.blp
#XTextures\ocean\ocean_h.1.blp
#XTextures\LavaGreen\lavagreen.1.blp

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
        items=liquidTypeEnum,
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

        col = layout.column()

        col.label(text="Actions:")

        if bpy.context.selected_objects:
            box = col.box()
            box.label(text="Convert:")
            box.operator("scene.wow_selected_objects_to_group", text = 'To WMO group', icon = 'OBJECT_DATA')
            box.operator("scene.wow_selected_objects_to_wow_material", text = 'To WMO material', icon = 'SMOOTH')
            box.operator("scene.wow_selected_objects_to_portals", text = 'To WMO portal', icon = 'MOD_MIRROR')
            box.operator("scene.wow_texface_to_material", text = 'Texface to mat.', icon = 'TEXTURE_DATA')
            box.label(text="Apply:")
            box.operator("scene.wow_quick_collision", text = 'Quick collision', icon = 'STYLUS_PRESSURE')
            box.operator("scene.wow_fill_textures", text = 'Fill textures', icon = 'FILE_IMAGE')
            box.operator("scene.wow_fill_group_name", text = 'Fill group name', icon = 'FONTPREVIEW')
            box.operator("scene.wow_invert_portals", text = 'Invert portals', icon = 'FILE_REFRESH')
            if not has_sets:
                box.label(text="Doodads:")
                box.operator("scene.wow_doodad_set_add", text = 'Add to doodadset', icon = 'ZOOMIN')
                box.operator("scene.wow_doodad_set_template_action", text = 'Template action', icon = 'FORCE_MAGNETIC')

        box1 = col.box()
        box1.label(text="Add to scene:")
        box1.operator("scene.wow_add_fog", text = 'Add fog', icon = 'GROUP_VERTEX')
        box1.operator("scene.wow_add_water", text = 'Add water', icon = 'MOD_WAVE')
        box1.operator("scene.wow_add_scale_reference", text = 'Add scale', icon = 'OUTLINER_OB_ARMATURE')

        if game_data_loaded:
            if not has_sets:
                box1.operator("scene.wow_wmo_import_doodad_from_wmv", text = 'Add M2 from WMV', icon = 'LOAD_FACTORY')

            box1.operator("scene.wow_import_last_wmo_from_wmv", text = 'Add WMO from WMV', icon = 'APPEND_BLEND')

        if has_sets:
            col.operator("scene.wow_clear_preserved_doodad_sets", text = 'Clear doodad sets', icon = 'CANCEL')

        col.label(text="Display:")
        box2 = col.box()
        box2.label(text="Unit Types:")
        box2.prop(context.scene, "WoWVisibility")

        if not bpy.context.scene.WoWRoot.MODS_Sets:
            box2.label(text="Doodad Sets:")
            box2.prop(context.scene, "WoWDoodadVisibility", expand=False)

        col.label(text="Game data:")
        icon = 'COLOR_GREEN' if game_data_loaded else 'COLOR_RED'
        text = "Unload game data" if game_data_loaded else "Load game data"
        load_data = col.operator("scene.load_wow_filesystem", text = text, icon = icon)

    def RegisterWMOToolsPanelObjectMode():
        bpy.utils.register_module(WMOToolsPanelObjectMode)
    def UnregisterWMOToolsPanelObjectMode():
        bpy.utils.register_module(WMOToolsPanelObjectMode)

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

###############################
## WMO operators
###############################

class IMPORT_LAST_WMO_FROM_WMV(bpy.types.Operator):
    bl_idname = "scene.wow_import_last_wmo_from_wmv"
    bl_label = "Load last WMO from WMV"
    bl_description = "Load last WMO from WMV"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, context):
        return True

    def wmv_get_last_wmo(self):
        """Get the path of last M2 model from WoWModelViewer or similar log."""

        preferences = bpy.context.user_preferences.addons.get("io_scene_wmo").preferences

        if preferences.wmv_path:

            lines = open(preferences.wmv_path).readlines()

            for line in reversed(lines):
                result = re.search("[^\d{2}:\d{2}:\d{2}: Loading WMO ].{1,}.wmo\n", line)
                if result:
                    return result.string[result.regs[0][0]:result.regs[0][1]]

    def execute(self, context):

        game_data = getattr(bpy, "wow_game_data", None)

        if not game_data or not game_data.files:
            self.report({'ERROR'}, "Failed to import model. Connect to game client first.")
            return {'CANCELLED'}

        dir = bpy.path.abspath("//") if bpy.data.is_saved else None
        wmo_path = self.wmv_get_last_wmo()

        if not wmo_path:
            self.report({'ERROR'}, """WoW Model Viewer log contains no WMO entries.
            Make sure to use compatible WMV version or open a .wmo there.""")
            return {'CANCELLED'}

        if dir:

            game_data.extract_files(dir, (wmo_path, ))

            i = 0
            while True:
                result = game_data.extract_files(dir, (wmo_path[:-4] + "_" + str(i).zfill(3) + ".wmo", ))
                if not result:
                    break
                i += 1

            try:
                from . import import_wmo
                import_wmo.read(os.path.join(dir, wmo_path), '.png' , True, True)
            except:
                self.report({'ERROR'}, "Failed to import model.")
                return {'CANCELLED'}

            self.report({'INFO'}, "Done importing WMO object to scene.")
            return {'FINISHED'}

        else:
            self.report({'ERROR'}, """Failed to import WMO.
            Save your blendfile first.""")
            return {'CANCELLED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

###############################
## Doodad operators
###############################

def LoadDoodadsFromPreserved(dir, game_data):
    """ Load doodad sets to scene from preserved doodadset data"""

    def get_string(ofs):
        for string in bpy.context.scene.WoWRoot.MODN_StringTable:
            if string.Ofs == ofs:
                return string.String

    scene = bpy.context.scene
    obj_map = {}

    for doodad_set in scene.WoWRoot.MODS_Sets:

        bpy.ops.object.empty_add(type='SPHERE', location=(0, 0, 0))
        anchor = bpy.context.scene.objects.active
        anchor.name = doodad_set.Name
        anchor.hide = True
        anchor.hide_select = True

        for i in range(doodad_set.StartDoodad, doodad_set.StartDoodad + doodad_set.nDoodads):
            doodad = scene.WoWRoot.MODD_Definitions[i]
            doodad_path = os.path.splitext(get_string(doodad.NameOfs))[0] + ".m2"

            nobj = None
            obj = obj_map.get(doodad_path)

            if not obj:
                try:
                    obj = m2.M2ToBlenderMesh(dir, doodad_path, game_data)
                except:
                    bpy.ops.mesh.primitive_cube_add()
                    obj = bpy.context.scene.objects.active
                    LogDebug(1, False, "Failed to import model: <<" + doodad_path + ">>. Placeholder is imported instead.")

                obj.WoWDoodad.Enabled = True
                obj.WoWDoodad.Path = doodad_path

                obj_map[doodad_path] = obj
                nobj = obj
            else:
                nobj = obj.copy()

                nobj.WoWDoodad.Color = (doodad.Color[0] / 255,
                                        doodad.Color[1] / 255,
                                        doodad.Color[2] / 255,
                                        doodad.ColorAlpha / 255)

                flags = []
                bit = 1
                while bit <= 0x8:
                    if doodad.Flags & bit:
                        flags.append(str(bit))
                    bit <<= 1

                nobj.WoWDoodad.Flags = set(flags)

                scene.objects.link(nobj)

            # place the object correctly on the scene
            nobj.location = doodad.Position
            nobj.scale = (doodad.Scale, doodad.Scale, doodad.Scale)

            nobj.rotation_mode = 'QUATERNION'
            nobj.rotation_quaternion = (doodad.Tilt,
                                        doodad.Rotation[0],
                                        doodad.Rotation[1],
                                        doodad.Rotation[2])
            nobj.parent = anchor
            nobj.hide = True
            nobj.lock_location = (True, True, True)
            nobj.lock_rotation = (True, True, True)
            nobj.lock_scale = (True, True, True)


class DOODAD_SET_CLEAR_PRESERVED(bpy.types.Operator):
    bl_idname = 'scene.wow_clear_preserved_doodad_sets'
    bl_label = 'Clear preserved doodad sets'
    bl_description = 'Clear preserved doodad set data or optionally load real doodad sets'
    bl_options = {'REGISTER', 'INTERNAL'}

    Action = bpy.props.EnumProperty(
        items=[
            ('0', "Load doodad sets", "Load doodad sets from game data", 'LOAD_FACTORY', 0),
            ('1', "Clear preserved sets", "Clear preserved doodad set data to unlock editing", 'CANCEL', 1)],
        default='0'
        )

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        col = self.layout
        col.prop(self, "Action", expand=True)

    def execute(self, context):
        if self.Action == '0':
            if not hasattr(bpy, "wow_game_data"):
                Log(2, True, "Loading game data")
                bpy.ops.scene.load_wow_filesystem()

            dir = bpy.path.abspath("//") if bpy.data.is_saved else None

            if dir:
                try:
                    LoadDoodadsFromPreserved(dir, bpy.wow_game_data)
                except:
                    self.report({'ERROR'}, "An error occured while importing doodads.")
                    return {'CANCELLED'}
            else:
                self.report({'ERROR'}, """Failed to import model. Save your blendfile first.""")
                return {'CANCELLED'}

            bpy.context.scene.WoWRoot.MODS_Sets.clear()
            bpy.context.scene.WoWRoot.MODN_StringTable.clear()
            bpy.context.scene.WoWRoot.MODD_Definitions.clear()

            update_wow_visibility(bpy.context.scene, None)
            self.report({'INFO'}, "Successfully imported doodad sets")
            return {'FINISHED'}

        else:
            bpy.context.scene.WoWRoot.MODS_Sets.clear()
            bpy.context.scene.WoWRoot.MODN_StringTable.clear()
            bpy.context.scene.WoWRoot.MODD_Definitions.clear()
            self.report({'INFO'}, "Successfully cleared preserved doodad sets. Editing is now available")
            return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)



class DOODAD_SET_ADD(bpy.types.Operator):
    bl_idname = 'scene.wow_doodad_set_add'
    bl_label = 'Add doodad set'
    bl_description = 'Add models to doodadset'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    Action = bpy.props.EnumProperty(
        name="Operator action",
        description="Choose operator action",
        items=[
            ("ADD", "Add to existing set", "", 'PLUGIN', 0),
            ("CUSTOM", "Create new set", "", 'ZOOMIN', 1),
            ("GLOBAL", "Create new global set", "", 'WORLD',2),
            ]
        )

    Set = bpy.props.EnumProperty(
        name="",
        description="Select doodad set",
        items=get_doodad_sets,
        update=switch_doodad_set
        )

    Name = bpy.props.StringProperty(
        name=""
        )

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col.label(text="Action")
        col.prop(self, "Action", expand=True)

        if self.Action == "ADD":
            text = "Select set:"
            col.label(text=text)
            col.prop(self, "Set")
        elif self.Action == "CUSTOM":
            text = "Enter set name:"
            col.label(text=text)
            col.prop(self, "Name")

    def execute(self, context):

        selected_objs = []
        for obj in bpy.context.scene.objects:
            if obj.select and obj.WoWDoodad.Enabled:
                selected_objs.append(obj)

        if self.Action == "ADD":
            if self.Set != "None":
                for obj in selected_objs:
                    obj.parent = bpy.context.scene.objects[self.Set]

                self.report({'INFO'}, "Successfully added doodads to doodad set")

            else:
                self.report({'WARNING'}, "Select a doodad set to link objects to first")


        elif self.Action == "CUSTOM":
            if self.Name:
                bpy.ops.object.empty_add(type='SPHERE', location=(0, 0, 0))
                obj = bpy.context.scene.objects.active
                obj.name = self.Name
                obj.hide = True
                obj.hide_select = True
                obj.lock_location = (True, True, True)
                obj.lock_rotation = (True, True, True)
                obj.lock_scale = (True, True, True)

                for object in selected_objs:
                    object.parent = obj

                self.report({'INFO'}, "Successfully created new doodadset and added doodads to it")

            else:
                self.report({'WARNING'}, "Enter name of the doodadset")

        elif self.Action == "GLOBAL":
            if not bpy.context.scene.objects.get("Set_$DefaultGlobal"):
                bpy.ops.object.empty_add(type='SPHERE', location=(0, 0, 0))
                obj = bpy.context.scene.objects.active
                obj.name = "Set_$DefaultGlobal"
                obj.hide = True
                obj.hide_select = True
                obj.lock_location = (True, True, True)
                obj.lock_rotation = (True, True, True)
                obj.lock_scale = (True, True, True)

                for object in selected_objs:
                    object.parent = obj

                self.report({'INFO'}, "Successfully created global doodadset and added doodads to it")

            else:
                self.report({'WARNING'}, "There can only be one global doodadset")

        switch_doodad_set(bpy.context.scene, None)

        return {'FINISHED'}


class DOODAD_SET_TEMPLATE_ACTION(bpy.types.Operator):
    bl_idname = 'scene.wow_doodad_set_template_action'
    bl_label = 'Template action'
    bl_description = 'Apply an action to all instances of selected object on the scene'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    Action = bpy.props.EnumProperty(
        items=[
            ('SELECT', "Select", "Rotate all instances of selected doodads", 'PMARKER_ACT', 0),
            ('REPLACE', "Replace", "Replace all instances of selected doodads with last M2 from WMV", 'FILE_REFRESH', 1),
            ('RESIZE', "Resize", "Resize all instances of selected doodads", 'FULLSCREEN_ENTER', 2),
            ('DELETE', "Delete", "Delete all instances of selected doodads", 'CANCEL', 3),
            ('ROTATE', "Rotate", "Rotate all instances of selected doodads", 'LOOP_FORWARDS', 4)],
        default='SELECT'
        )

    Scale = bpy.props.FloatProperty(
        name="Scale",
        description="Scale applied to doodads",
        min=0.01,
        max=20,
        default=1
        )

    Rotation = bpy.props.FloatVectorProperty(
        name="Rotation",
        default=(0, 0, 0, 0),
        size=4
        )

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        col = self.layout.column()

        col.prop(self, "Action", expand=True)

        if self.Action == 'RESIZE':
            col.prop(self, "Scale")
        elif self.Action == 'ROTATE':
            col.prop(self, "Rotation")

    def execute(self, context):

        target = None
        active = bpy.context.scene.objects.active

        if active and active.WoWDoodad:
           target = active.WoWDoodad.Path
        else:
            self.report({'ERROR'}, "Template functions require an active object.")
            return {'CANCELLED'}

        selected_only = False
        if len(bpy.context.selected_objects) > 1:
            selected_only = True

        selected_objects = bpy.context.selected_objects.copy()
        objects_to_select = []

        success = False

        if target:

            new_obj = None

            if self.Action == 'REPLACE':
                if not bpy.data.is_saved:
                    self.report({'ERROR'}, "Saved your blendfile first.")
                    return {'FINISHED'}

                if not hasattr(bpy, "wow_game_data"):
                    self.report({'ERROR'}, "Connect to game data first.")
                    return {'FINISHED'}

                bpy.ops.scene.wow_wmo_import_doodad_from_wmv()
                new_obj = bpy.context.scene.objects.active

            for obj in bpy.context.scene.objects:
                is_selected = obj in selected_objects if selected_only else True

                if obj.WoWDoodad.Path == target and is_selected:

                    if self.Action == 'REPLACE':

                        location = obj.location
                        rotation = obj.rotation_quaternion
                        scale = obj.scale

                        bpy.data.objects.remove(obj, do_unlink = True)

                        obj = new_obj.copy()
                        bpy.context.scene.objects.link(obj)
                        bpy.context.scene.objects.active = obj

                        obj.location = location
                        obj.rotation_mode = 'QUATERNION'
                        obj.rotation_quaternion = rotation
                        obj.scale = scale
                        objects_to_select.append(obj)

                    elif self.Action == 'RESIZE':

                        obj.scale *= self.Scale
                        obj.select = True

                    elif self.Action == 'DELETE':

                        bpy.data.objects.remove(obj, do_unlink = True)

                    elif self.Action == 'ROTATE':
                        obj.rotation_mode = 'QUATERNION'
                        for i, _ in enumerate(self.Rotation):
                            obj.rotation_quaternion[i] += self.Rotation[i]

                    elif self.Action == 'SELECT':
                        obj.select = True

                    success = True

                for ob in objects_to_select:
                    ob.select = True

            if new_obj:
                bpy.data.objects.remove(new_obj, do_unlink = True)

            if success:
                self.report({'INFO'}, "Template action applied.")

            return {'FINISHED'}

        else:
            self.report({'ERROR'}, "No doodad is selected.")
            return {'FINISHED'}


###############################
## Water operators
###############################

class OBJECT_OP_ADD_FLAG(bpy.types.Operator):
    bl_idname = 'scene.wow_mliq_change_flags'
    bl_label = 'Change liquid flags'
    bl_description = 'Change WoW liquid flags'

    Action = bpy.props.EnumProperty(
        name="",
        description="Select flag action",
        items=[("ADD", "", ""),
               ("ADD_ALL", "", ""),
               ("CLEAR", "", ""),
               ("CLEAR_ALL", "", "")
            ]
        )

    def execute(self, context):
        water = bpy.context.scene.objects.active
        if water.WowLiquid.Enabled:
            mesh = water.data

            if self.Action == "ADD":
                for polygon in mesh.polygons:
                    if polygon.select:
                        for loop_index in polygon.loop_indices:
                                mesh.vertex_colors[mesh.vertex_colors.active_index].data[loop_index].color = (0, 0, 255)
            elif self.Action == "ADD_ALL":
                for polygon in mesh.polygons:
                        for loop_index in polygon.loop_indices:
                                mesh.vertex_colors[mesh.vertex_colors.active_index].data[loop_index].color = (0, 0, 255)
            elif self.Action == "CLEAR":
                for polygon in mesh.polygons:
                    if polygon.select:
                        for loop_index in polygon.loop_indices:
                                mesh.vertex_colors[mesh.vertex_colors.active_index].data[loop_index].color = (255, 255, 255)
            elif self.Action == "CLEAR_ALL":
                for polygon in mesh.polygons:
                        for loop_index in polygon.loop_indices:
                                mesh.vertex_colors[mesh.vertex_colors.active_index].data[loop_index].color = (255, 255, 255)

        else:
            self.report({'ERROR'}, "Selected object is not World of Warcraft liquid")

        return {'FINISHED'}

###############################
## Object operators
###############################

class OBJECT_OP_Add_Scale(bpy.types.Operator):
    bl_idname = 'scene.wow_add_scale_reference'
    bl_label = 'Add scale'
    bl_description = 'Add a WoW scale prop'
    bl_options = {'REGISTER', 'UNDO'}

    ScaleType = bpy.props.EnumProperty(
        name = "Scale Type",
        description = "Select scale reference type",
        items = [('HUMAN', "Human Scale (average)", ""),
                 ('TAUREN', "Tauren Scale (thickest)", ""),
                 ('TROLL', "Troll Scale (tallest)", ""),
                 ('GNOME', "Gnome Scale (smallest)", "")
                 ],
        default = 'HUMAN'
        )

    def execute(self, context):
        if self.ScaleType == 'HUMAN':
            bpy.ops.object.add(type='LATTICE')
            scale_obj = bpy.context.object
            scale_obj.name = "Human Scale"
            scale_obj.dimensions = (0.582, 0.892, 1.989)

        elif self.ScaleType == 'TAUREN':
            bpy.ops.object.add(type='LATTICE')
            scale_obj = bpy.context.object
            scale_obj.name = "Tauren Scale"
            scale_obj.dimensions = (1.663, 1.539, 2.246)

        elif self.ScaleType == 'TROLL':
            bpy.ops.object.add(type='LATTICE')
            scale_obj = bpy.context.object
            scale_obj.name = "Troll Scale"
            scale_obj.dimensions = (1.116, 1.291, 2.367)

        elif self.ScaleType == 'GNOME':
            bpy.ops.object.add(type='LATTICE')
            scale_obj = bpy.context.object
            scale_obj.name = "Gnome Scale"
            scale_obj.dimensions = (0.362, 0.758, 0.991)

        self.report({'INFO'}, "Successfully added " + self.ScaleType + " scale")
        return {'FINISHED'}


class OBJECT_OP_Add_Water(bpy.types.Operator):
    bl_idname = 'scene.wow_add_water'
    bl_label = 'Add water'
    bl_description = 'Add a WoW water plane'
    bl_options = {'REGISTER', 'UNDO'}

    xPlanes = bpy.props.IntProperty(
        name="X subdivisions:",
        description="Amount of WoW liquid planes in a row. One plane is 4.1666625 in its radius.",
        default=10,
        min=1
        )

    yPlanes = bpy.props.IntProperty(
        name="Y subdivisions:",
        description="Amount of WoW liquid planes in a column. One plane is 4.1666625 in its radius.",
        default=10,
        min=1
        )

    def execute(self, context):
        bpy.ops.mesh.primitive_grid_add(x_subdivisions = self.xPlanes + 1,
                                        y_subdivisions = self.yPlanes + 1,
                                        radius=4.1666625 / 2
                                        )
        water = bpy.context.scene.objects.active
        bpy.ops.transform.resize( value=(self.xPlanes, self.yPlanes, 1.0) )

        water.name = water.name + "_Liquid"

        mesh = water.data

        bit = 1
        while bit <= 0x80:
            mesh.vertex_colors.new("flag_" + hex(bit))
            bit <<= 1

        water.WowLiquid.Enabled = True

        water.hide = False if "4" in bpy.context.scene.WoWVisibility else True

        self.report({'INFO'}, "Successfully сreated WoW liquid: " + water.name)
        return {'FINISHED'}


class OBJECT_OP_Add_Fog(bpy.types.Operator):
    bl_idname = 'scene.wow_add_fog'
    bl_label = 'Add fog'
    bl_description = 'Add a WoW fog object to the scene'

    def execute(self, context):

        bpy.ops.mesh.primitive_uv_sphere_add()
        fog = bpy.context.scene.objects.active
        fog.name = fog.name + "_Fog"

        # applying real object transformation
        bpy.ops.object.shade_smooth()
        fog.draw_type = 'SOLID'
        fog.show_transparent = True
        fog.show_name = True

        mesh = fog.data

        material = bpy.data.materials.new(name = fog.name)

        if mesh.materials:
            mesh.materials[0] = material
        else:
            mesh.materials.append(material)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.object.material_slot_assign()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        mesh.materials[0].use_object_color = True
        mesh.materials[0].use_transparency = True
        mesh.materials[0].alpha = 0.35

        fog.WowFog.Enabled = True

        fog.hide = False if "3" in bpy.context.scene.WoWVisibility else True

        self.report({'INFO'}, "Successfully сreated WoW fog: " + fog.name)
        return {'FINISHED'}


class OBJECT_OP_Invert_Portals(bpy.types.Operator):
    bl_idname = 'scene.wow_invert_portals'
    bl_label = 'Invert portals'
    bl_description = 'Invert predefined direction of all selected WoW portals.'
    bl_options = {'REGISTER', 'UNDO'}

    Algorithm = bpy.props.EnumProperty(
        items=portalDirAlgEnum,
        default="0"
        )

    def execute(self, context):
        success = False
        for ob in bpy.context.selected_objects:
            if ob.WowPortalPlane.Enabled:
                ob.WowPortalPlane.Algorithm = self.Algorithm
                success = True

        if success:
            self.report({'INFO'}, "Successfully inverted selected portals")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No portals found among selected objects")
            return {'CANCELLED'}


class OBJECT_OP_Fill_Group_Name(bpy.types.Operator):
    bl_idname = 'scene.wow_fill_group_name'
    bl_label = 'Fill group name'
    bl_description = 'Fill the specified group name for selected objects'
    bl_options = {'REGISTER', 'UNDO'}

    Name = bpy.props.StringProperty()

    def execute(self, context):
        success = False
        for ob in bpy.context.selected_objects:
            if ob.WowWMOGroup.Enabled:
                ob.WowWMOGroup.GroupName = self.Name
                success = True

        if success:
            self.report({'INFO'}, "Successfully set names for selected groups")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No WMO group objects found among selected objects")
            return {'CANCELLED'}


class OBJECT_OP_Fill_Textures(bpy.types.Operator):
    bl_idname = 'scene.wow_fill_textures'
    bl_label = 'Fill textures'
    bl_description = """Fill Texture 1 field of WoW materials with paths from applied image. """
    bl_options = {'REGISTER'}

    def execute(self, context):

        if not hasattr(bpy, "wow_game_data"):
                Log(2, True, "Loading game data")
                bpy.ops.scene.load_wow_filesystem()

        game_data = bpy.wow_game_data

        for ob in bpy.context.selected_objects:
            mesh = ob.data
            for i in range(len(mesh.materials)):
                if mesh.materials[i].active_texture is not None \
                and not mesh.materials[i].WowMaterial.Texture1 \
                and mesh.materials[i].active_texture.type == 'IMAGE' \
                and mesh.materials[i].active_texture.image is not None:
                    path = (os.path.splitext(mesh.materials[i].active_texture.image.filepath)[0] + ".blp", "")
                    rest_path = ""

                    while True:
                        path = os.path.split(path[0])
                        if not path[1]:
                            LogDebug(1, False, "Texture " + mesh.materials[i].active_texture.image.filepath + " not found.")
                            break

                        rest_path = os.path.join(path[1], rest_path)
                        rest_path = rest_path[:-1] if rest_path.endswith("\\") else rest_path

                        sys.stdout = open(os.devnull, 'w')

                        if game_data.read_file(rest_path):
                            mesh.materials[i].WowMaterial.Texture1 = rest_path
                            break

                        sys.stdout = sys.__stdout__

            self.report({'INFO'}, "Done filling texture paths")

        return {'FINISHED'}


class OBJECT_OP_Quick_Collision(bpy.types.Operator):
    bl_idname = 'scene.wow_quick_collision'
    bl_label = 'Generate basic collision for selected objects'
    bl_description = 'Generate WoW collision equal to geometry of the selected objects'
    bl_options = {'REGISTER', 'UNDO'}

    NodeSize = bpy.props.IntProperty(
        name="Node max size",
        description="Max count of faces for a node in bsp tree",
        default=2500,
        min=1,
        soft_max=5000
        )

    CleanUp = bpy.props.BoolProperty(
        name="Clean up",
        description="Remove unreferenced vertex groups",
        default = False
        )

    def execute(self, context):

        success = False
        for ob in bpy.context.selected_objects:
            if ob.WowWMOGroup.Enabled:
                bpy.context.scene.objects.active = ob

                if self.CleanUp:
                    for vertex_group in ob.vertex_groups:
                        if vertex_group.name != ob.WowVertexInfo.VertexGroup \
                        and vertex_group.name != ob.WowVertexInfo.BatchTypeA \
                        and vertex_group.name != ob.WowVertexInfo.BatchTypeB \
                        and vertex_group.name != ob.WowVertexInfo.Lightmap \
                        and vertex_group.name != ob.WowVertexInfo.Blendmap \
                        and vertex_group.name != ob.WowVertexInfo.SecondUV:
                            ob.vertex_groups.remove(vertex_group)

                if ob.vertex_groups.get(ob.WowVertexInfo.VertexGroup):
                    bpy.ops.object.vertex_group_set_active(group=ob.WowVertexInfo.VertexGroup)
                else:
                    new_vertex_group = ob.vertex_groups.new(name="Collision")
                    bpy.ops.object.vertex_group_set_active(group=new_vertex_group.name)
                    ob.WowVertexInfo.VertexGroup = new_vertex_group.name

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.object.vertex_group_assign()
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
                ob.WowVertexInfo.NodeSize = self.NodeSize

                success = True

        if success:
            self.report({'INFO'}, "Successfully generated automatic collision for selected WMO groups")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No WMO group objects found among selected objects")
            return {'CANCELLED'}


class OBJECT_OP_Texface_to_material(bpy.types.Operator):
    bl_idname = 'scene.wow_texface_to_material'
    bl_label = 'Texface to material'
    bl_description = 'Generate materials out of texfaces in selected objects'

    def execute(self, context):
        if bpy.context.selected_objects[0]:
            bpy.context.scene.objects.active = bpy.context.selected_objects[0]
        bpy.ops.view3d.material_remove()
        bpy.ops.view3d.texface_to_material()

        self.report({'INFO'}, "Successfully generated materials from face textures")
        return {'FINISHED'}


class OBJECT_OP_To_WMOPortal(bpy.types.Operator):
    bl_idname = 'scene.wow_selected_objects_to_portals'
    bl_label = 'Selected objects to WMO portals'
    bl_description = 'Transfer all selected objects to WoW WMO portals'
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        row = layout.row()

        column = layout.column()
        idproperty.layout_id_prop(column, context.object.WowPortalPlane, "First")
        idproperty.layout_id_prop(column, context.object.WowPortalPlane, "Second")


    First = idproperty.ObjectIDProperty(
            name="First group",
            validator=portal_validator
            )

    Second = idproperty.ObjectIDProperty(
        name="Second group",
        validator=portal_validator
        )

    def portal_validator(ob):
        return ob.type == 'MESH' and ob.WowWMOGroup.Enabled

    def execute(self, context):

        success = False
        for ob in bpy.context.selected_objects:
            if ob.type == 'MESH':
                ob.WowWMOGroup.Enabled = False
                ob.WowLiquid.Enabled = False
                ob.WowFog.Enabled = False
                ob.WowPortalPlane.Enabled = True
                ob.WowPortalPlane.First = self.First
                ob.WowPortalPlane.Second = self.Second

                ob.hide = False if "2" in bpy.context.scene.WoWVisibility else True
                success = True

        if success:
            self.report({'INFO'}, "Successfully converted select objects to portals")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No mesh objects found among selected objects")
            return {'CANCELLED'}


class OBJECT_OP_To_Group(bpy.types.Operator):
    bl_idname = 'scene.wow_selected_objects_to_group'
    bl_label = 'Selected objects to WMO group'
    bl_description = 'Transfer all selected objects to WoW WMO groups'
    bl_options = {'REGISTER', 'UNDO'}

    GroupName = bpy.props.StringProperty(name="Name")
    GroupDesc = bpy.props.StringProperty(name="Description")

    PlaceType = bpy.props.EnumProperty(
        items=placeTypeEnum,
        name="Place Type",
        description="Group is indoor or outdoor"
        )

    Flags = bpy.props.EnumProperty(
        items=groupFlagEnum,
        options={'ENUM_FLAG'}
        )

    GroupDBCid = bpy.props.IntProperty(
        name="DBC Group ID",
        description="WMO Group ID in DBC file"
        )

    LiquidType = bpy.props.EnumProperty(
        items=liquidTypeEnum,
        name="LiquidType",
        description="Fill this WMO group with selected liquid."
        )

    def execute(self, context):

        scene = bpy.context.scene

        success = False
        for ob in bpy.context.selected_objects:
            if ob.type == 'MESH':
                ob.WowLiquid.Enabled = False
                ob.WowFog.Enabled = False
                ob.WowPortalPlane.Enabled = False
                ob.WowWMOGroup.Enabled = True
                ob.WowWMOGroup.PlaceType = self.PlaceType
                ob.WowWMOGroup.GroupName = self.GroupName
                ob.WowWMOGroup.GroupDesc = self.GroupDesc
                ob.WowWMOGroup.Flags = self.Flags
                ob.WowWMOGroup.GroupDBCid = self.GroupDBCid
                ob.WowWMOGroup.LiquidType = self.LiquidType

                if self.PlaceType == "8" and "0" in scene.WoWVisibility \
                or self.PlaceType == "8192" and "1" in scene.WoWVisibility:
                    ob.hide = False
                else:
                    ob.hide = True
                success = True

        if success:
            self.report({'INFO'}, "Successfully converted select objects to WMO groups")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No mesh objects found among selected objects")
            return {'CANCELLED'}


class OBJECT_OP_To_WoWMaterial(bpy.types.Operator):
    bl_idname = 'scene.wow_selected_objects_to_wow_material'
    bl_label = 'Materials of selected objects to WoW Material'
    bl_description = 'Transfer all materials of selected objects to WoW material'
    bl_options = {'REGISTER', 'UNDO'}

    Flags = bpy.props.EnumProperty(
        name = "Material flags",
        description = "WoW material flags",
        items =materialFlagEnum,
        options = {"ENUM_FLAG"}
        )

    Shader = bpy.props.EnumProperty(
        items=shaderEnum,
        name="Shader",
        description="WoW shader assigned to this material"
        )

    BlendingMode = bpy.props.EnumProperty(
        items=blendingEnum,
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
        items=terrainEnum,
        name="Terrain Type",
        description="Terrain type assigned to this material. Used for producing correct footstep sounds."
        )

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "Shader")
        col.prop(self, "TerrainType")
        col.prop(self, "BlendingMode")

        col.separator()
        col.label("Flags:")
        col.prop(self, "Flags")

        col.separator()
        col.prop(self, "Texture1")
        col.prop(self, "Texture2")

        layout.prop(self, "EmissiveColor")
        layout.prop(self, "DiffColor")

    def execute(self, context):
        success = False
        for ob in bpy.context.selected_objects:
            if ob.WowWMOGroup.Enabled:
                for material in ob.data.materials:
                    material.WowMaterial.Enabled = True
                    material.WowMaterial.Shader = self.Shader
                    material.WowMaterial.BlendingMode = self.BlendingMode
                    material.WowMaterial.TerrainType = self.TerrainType
                    material.WowMaterial.Flags = self.Flags
                    material.WowMaterial.EmissiveColor = self.EmissiveColor
                    material.WowMaterial.DiffColor = self.DiffColor
                success = True

        if success:
            self.report({'INFO'}, "Successfully enabled all materials in the selected WMO groups as WMO materials")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No WMO group objects found among selected objects")
            return {'CANCELLED'}


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



