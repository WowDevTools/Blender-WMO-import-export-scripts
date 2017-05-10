
import bpy
import bpy.utils
import bpy.types
import os
from . import wmo_format
from .wmo_format import *
from . import debug_utils
from .debug_utils import *
from bpy.utils import register_module, unregister_module
from .idproperty import idproperty
from .idproperty.idproperty import *

###############################
## Root properties
###############################

class WoWRootPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_label = "WoW Root"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        self.layout.prop(context.scene.WoWRoot, "PortalDistanceAttenuation")
        self.layout.prop(context.scene.WoWRoot, "LightenIndoor")
        self.layout.prop(context.scene.WoWRoot, "UseAmbient")
        self.layout.prop(context.scene.WoWRoot, "AmbientColor")
        self.layout.prop(context.scene.WoWRoot, "AmbientAlpha")
        self.layout.prop(context.scene.WoWRoot, "SkyboxPath")
        self.layout.prop(context.scene.WoWRoot, "WMOid")
        self.layout.prop(context.scene.WoWRoot, "UseTextureRelPath")
        self.layout.prop(context.scene.WoWRoot, "TextureRelPath")

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

    GroupID = bpy.props.IntProperty(
        name="WMO Group ID",
        description="Used internally for exporting",
        default= 0,
        )
    
    PortalDistanceAttenuation = bpy.props.BoolProperty(
        name="Auto Attenuation",
        description="Attenuate light on vertices based on distance from portal",
        default=True,
        )
    
    LightenIndoor = bpy.props.BoolProperty(
        name="Lighten Indoor",
        description="Lighten up all indoor groups automatically",
        default= False,
        )

    UseAmbient = bpy.props.BoolProperty(
        name="Use Ambient",
        description="Use ambient lighting inside indoor groups",
        default= False,
        )

    AmbientColor = bpy.props.FloatVectorProperty(
        name="Ambient Color",
        subtype='COLOR',
        default=(1,1,1),
        min=0.0,
        max=1.0
        )

    AmbientAlpha =  bpy.props.IntProperty(
        name="Ambient Intensity",
        description="Ambient. 255 = blizzlike",
        min=0, max=255,
        default= 127,
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

    UseTextureRelPath = bpy.props.BoolProperty(
        name="Use Texture Relative Path",
        description="Turn this setting off if you want texture auto-filling if your textures are already referenced through relative paths",
        default= True,
        )

    TextureRelPath =  bpy.props.StringProperty(
        name="TextureRelPath",
        description="A relative path to your texture folder. WARNING: changing that property is recommended only on brand new scenes. Do not change on scenes with imported WMOs.",
        default= '',
        
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
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        self.layout.prop(context.object.WoWDoodad, "Path")
        self.layout.prop(context.object.WoWDoodad, "Color")
        self.layout.prop(context.object.WoWDoodad, "Flags")
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
        name = "My enum",
        description = "My enum description",
        items = [
            ("1" , "Accept Projected Tex." , ""),
            ("2", "Adjust lighting", ""),
            ("4", "Unknown", ""),
            ("8", "Unknown", "")
        ],
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
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        self.layout.prop(context.material.WowMaterial, "Enabled")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        self.layout.prop(context.material.WowMaterial, "Shader")
        self.layout.prop(context.material.WowMaterial, "TerrainType")
        self.layout.prop(context.material.WowMaterial, "BlendingMode")
        self.layout.prop(context.material.WowMaterial, "TwoSided")
        self.layout.prop(context.material.WowMaterial, "Darkened")
        self.layout.prop(context.material.WowMaterial, "NightGlow")
        self.layout.prop(context.material.WowMaterial, "Texture1")
        self.layout.prop(context.material.WowMaterial, "Color1")
        self.layout.prop(context.material.WowMaterial, "Flags1")
        self.layout.prop(context.material.WowMaterial, "Texture2")
        self.layout.prop(context.material.WowMaterial, "Color2")
        self.layout.prop(context.material.WowMaterial, "Texture3")
        self.layout.prop(context.material.WowMaterial, "Color3")
        self.layout.prop(context.material.WowMaterial, "Flags3")
        layout.enabled = context.material.WowMaterial.Enabled
    @classmethod
    def poll(cls, context):
        return (context.material is not None)


class WowMaterialPropertyGroup(bpy.types.PropertyGroup):
    shaderEnum = [
        ('0', "Diffuse", ""), ('1', "Specular", ""), ('2', "Metal", ""),
        ('3', "Env", ""), ('4', "Opaque", ""), ('5', "EnvMetal", ""),
        ('6', "TwoLayerDiffuse", ""), ('7', "TwoLayerEnvMetal", ""), ('8', "TwoLayerTerrain", ""),
        ('9', "DiffuseEmissive", ""), ('10', "Tangent", ""), ('11', "MaskedEnvMetal", ""),
        ('12', "EnvMetalEmissive", ""), ('13', "TwoLayerDiffuseOpaque", ""), ('14', "TwoLayerDiffuseEmissive", "")
        ] #, ('16', "Diffuse", "")]
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
    
    Enabled = bpy.props.BoolProperty(
        name="", 
        description="Enable WoW material properties"
        )

    Shader = bpy.props.EnumProperty(
        items=shaderEnum, 
        name="Shader", 
        description="WoW shader assigned to this material"
        )

    BlendingMode = bpy.props.EnumProperty(
        items=blendingEnum, 
        name="Blending Mode", 
        description="WoW material blending mode"
        )

    Texture1 = bpy.props.StringProperty(
        name="Texture 1",
        description="Texture assigned to first slot in shader"
        )

    Color1 = bpy.props.FloatVectorProperty(
        name="Emissive Color", 
        subtype='COLOR', 
        default=(1,1,1), 
        min=0.0, 
        max=1.0
        )

    Flags1 = bpy.props.EnumProperty(
        items=[('0', "Clamp", ""), ('1', "Repeat", "")], 
        name="Extension 2", 
        description="Extension mode for texture 1"
        )

    Texture2 = bpy.props.StringProperty(
        name="Texture 2",
        description="Texture assigned to second slot in shader"
        )

    Color2 = bpy.props.FloatVectorProperty(
        name="Emissive Color 2",
        subtype='COLOR',
        default=(1,1,1),
        min=0.0,
        max=1.0
        )

    TerrainType = bpy.props.EnumProperty(
        items=terrainEnum,
        name="Terrain Type",
        description="Terrain type assigned to this material. Used for footstep sounds and similar things."
        )

    Texture3 = bpy.props.StringProperty(
        name="Texture 3",
        description="Texture assigned to third slot in shader"
        )

    Color3 = bpy.props.FloatVectorProperty(
        name="Emissive Color 3",
        subtype='COLOR',
        default=(1,1,1),
        min=0.0, 
        max=1.0
        )

    Flags3 = bpy.props.EnumProperty(
        items=[('0', "Clamp", ""), ('1', "Repeat", "")],
        name="Extension 3",
        description="Extension mode for texture 3"
        )

    TwoSided = bpy.props.BoolProperty(
        name="TwoSided",
        description="Enable TwoSided"
        )

    Darkened = bpy.props.BoolProperty(
        name="Darkened",
        description="Enable Darkened"
        )

    NightGlow = bpy.props.BoolProperty(
        name="Unshaded",
        description="Enable NightGlow"
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
    bl_options = {'DEFAULT_CLOSED'}

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
        description="True if i dunno"
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
    bl_options = {'DEFAULT_CLOSED'}

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
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        self.layout.prop(context.object.WowWMOGroup, "Enabled")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        self.layout.prop(context.object.WowWMOGroup, "GroupName")
        self.layout.prop(context.object.WowWMOGroup, "GroupDesc")
        self.layout.prop(context.object.WowWMOGroup, "PlaceType")
        self.layout.prop(context.object.WowWMOGroup, "GroupID")
        self.layout.prop(context.object.WowWMOGroup, "LiquidType")
        self.layout.prop(context.object.WowWMOGroup, "VertShad")
        self.layout.prop(context.object.WowWMOGroup, "NoLocalLighting")
        self.layout.prop(context.object.WowWMOGroup, "AlwaysDraw")
        self.layout.prop(context.object.WowWMOGroup, "IsMountAllowed")
        self.layout.prop(context.object.WowWMOGroup, "SkyBox")
        
        column = layout.column()
        idproperty.layout_id_prop(column, context.object.WowWMOGroup, "Fog1")
        idproperty.layout_id_prop(column, context.object.WowWMOGroup, "Fog2")
        idproperty.layout_id_prop(column, context.object.WowWMOGroup, "Fog3")
        idproperty.layout_id_prop(column, context.object.WowWMOGroup, "Fog4")
        
        idproperty.enabled = context.object.WowLiquid.Enabled
        layout.enabled = context.object.WowWMOGroup.Enabled

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
    
    
class WowWMOGroupPropertyGroup(bpy.types.PropertyGroup):
    placeTypeEnum = [('8', "Outdoor", ""), ('8192', "Indoor", "")]

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

    Enabled = bpy.props.BoolProperty(
        name="",
        description="Enable wow WMO group properties"
        )

    GroupName = bpy.props.StringProperty()
    GroupDesc = bpy.props.StringProperty()

    PlaceType = bpy.props.EnumProperty(
        items=placeTypeEnum,
        name="Place Type",
        description="Group is indoor or outdoor"
        )

    GroupID = bpy.props.IntProperty(
        name="DBC Group ID",
        description="WMO Group ID in DBC file"
        )

    VertShad = bpy.props.BoolProperty(
        name="Vertex color",
        description="Save group vertex shading",
        default = False
        )

    NoLocalLighting = bpy.props.BoolProperty(
        name="No local lighting",
        description="Do not use local diffuse lightning",
        default = False
        )

    AlwaysDraw = bpy.props.BoolProperty(
        name="Always draw",
        description="Always draw the group",
        default = False
        )

    IsMountAllowed = bpy.props.BoolProperty(
        name="Mounts allowed",
        description="Allows or prohibits mounts in the group. Works only with generated navmesh delivered to server.",
        default = False
        )

    SkyBox = bpy.props.BoolProperty(
        name="Use Skybox",
        description="Use skybox in group",
        default = False
        )

    Fog1 = idproperty.ObjectIDProperty(
        name="Fog 1",
        validator=fog_validator
        )

    Fog2 = idproperty.ObjectIDProperty(
        name="Fog 2",
        validator=fog_validator
        )

    Fog3 = idproperty.ObjectIDProperty(
        name="Fog 3",
        validator=fog_validator
        )

    Fog4 = idproperty.ObjectIDProperty(
        name="Fog 4",
        validator=fog_validator
        )

    LiquidType = bpy.props.EnumProperty(
        items=liquidTypeEnum,
        name="Fill with liquid",
        description="Fill this WMO group with selected liquid."
        )

    MODR = bpy.props.CollectionProperty(type=WowWMOMODRStore)

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
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        self.layout.prop(context.object.WowPortalPlane, "Enabled")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
         
        column = layout.column()
        idproperty.layout_id_prop(column, context.object.WowPortalPlane, "First")
        idproperty.layout_id_prop(column, context.object.WowPortalPlane, "Second")
        
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
    bl_options = {'DEFAULT_CLOSED'}

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

    liquidTypeEnum = [
        ('0', "Unsupported", ""), ('1', "Water", ""), ('2', "Ocean", ""),
        ('3', "Magma", ""), ('4', "Slime", ""), ('5', "Slow Water", ""),
        ('6', "Slow Ocean", ""), ('7', "Slow Magma", ""), ('8', "Slow Slime", ""),
        ('9', "Fast Water", ""), ('10', "Fast Ocean", ""), ('11', "Fast Magma", ""),
        ('12', "Fast Slime", ""), ('13', "WMO Water", ""), ('14', "WMO Ocean", ""),
        ('15', "Green Lava", ""), ('17', "WMO Water - Interior", ""), ('19', "WMO Magma", ""),
        ('20', "WMO Slime", ""), ('21', "Naxxramas - Slime", ""), ('41', "Coilfang Raid - Water", ""),
        ('61', "Hyjal Past - Water", ""), ('81', "Lake Wintergrasp - Water", ""), ('100', "Basic Procedural Water", ""),
        ('121', "CoA Black - Magma", ""), ('141', "Chamber Magma", ""), ('181', "Orange Slime", "")
        ]

    Enabled = bpy.props.BoolProperty(
        name="",
        description="Enable wow liquid properties",
        default=False
        )

    Color = bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        default=(0.08,0.08,0.08),
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
    bl_options = {'DEFAULT_CLOSED'}

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
        max=250.0
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

class WoWVisibilityPropertyGroup(bpy.types.PropertyGroup):

    Enabled = bpy.props.BoolProperty(
        name="",
        description="Enable WoW visibility properties",
        default = True
        )

    Outdoor = bpy.props.BoolProperty(
        name="Outdoor",
        description="Show/hide outdoor groups",
        default= True,
        )

    Indoor = bpy.props.BoolProperty(
        name="Indoor",
        description="Show/hide indoor groups",
        default= True,
        )
    
    Portals = bpy.props.BoolProperty(
        name="Portals",
        description="Show/hide portal objects",
        default= True,
        )
    
    Fog = bpy.props.BoolProperty(
        name="Fog",
        description="Show/hide fog objects",
        default= True,
        )
    
    Light = bpy.props.BoolProperty(
        name="Light",
        description="Show/hide light objects",
        default= True,
        ) 
    
    Water = bpy.props.BoolProperty(
        name="Water",
        description="Show/hide water planes",
        default= True,
        )     
    
    All = bpy.props.BoolProperty(
        name="All",
        description="Show/hide all WoW objects",
        default= True,
        )
def RegisterWoWVisibilityProperties():
    bpy.types.Scene.WoWVisibility = bpy.props.PointerProperty(type=WoWVisibilityPropertyGroup)

def UnregisterWoWVisibilityProperties():
    bpy.types.Scene.WoWVisibility = None

class WMOToolsPanelObjectMode(bpy.types.Panel):
    bl_label = 'Quick WMO'
    bl_idname = 'WMOQuickPanelObjMode'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_category = 'WoW'

    def draw(self, context):
        layout = self.layout.split()
        
        col = layout.column()
        
        col.label(text="Actions")
        col.operator("scene.wow_selected_objects_to_group", text = 'To WMO group', icon = 'OBJECT_DATA')
        col.operator("scene.wow_selected_objects_to_wow_material", text = 'To WMO material', icon = 'SMOOTH')
        col.operator("scene.wow_selected_objects_to_portals", text = 'To WMO portal', icon = 'MOD_MIRROR')
        col.operator("scene.wow_texface_to_material", text = 'Texface to mat.', icon = 'TEXTURE_DATA')
        col.operator("scene.wow_quick_collision", text = 'Quick collision', icon = 'STYLUS_PRESSURE')
        col.operator("scene.wow_fill_textures", text = 'Fill textures', icon = 'FILE_IMAGE')
        col.operator("scene.wow_fill_group_name", text = 'Fill group name', icon = 'FONTPREVIEW')
        col.operator("scene.wow_invert_portals", text = 'Invert portals', icon = 'FILE_REFRESH')
        col.operator("scene.wow_add_fog", text = 'Add fog', icon = 'GROUP_VERTEX')
        col.operator("scene.wow_add_water", text = 'Add water', icon = 'MOD_WAVE')
        col.operator("scene.wow_add_scale_reference", text = 'Add scale', icon = 'OUTLINER_OB_ARMATURE')
        col.operator("scene.wow_wmo_import_doodad_from_wmv", text = 'Last M2 from WMV', icon = 'LOAD_FACTORY')
        col.label(text="Display")
        col.operator("scene.wow_hide_show_outdoor", text = 'Outdoor', icon = 'BBOX')
        col.operator("scene.wow_hide_show_indoor", text = 'Indoor', icon = 'ROTATE')
        col.operator("scene.wow_hide_show_portals", text = 'Portals', icon = 'MOD_PARTICLES')
        col.operator("scene.wow_hide_show_fog", text = 'Fog', icon = 'FORCE_TURBULENCE')
        col.operator("scene.wow_hide_show_water", text = 'Water', icon = 'MOD_FLUIDSIM')
        col.operator("scene.wow_hide_show_light", text = 'Light', icon = 'LAMP_SPOT')
        col.operator("scene.wow_hide_show_all_objects", text = 'All', icon = 'VISIBLE_IPO_ON')

        col.label(text="Game data")
        state = hasattr(bpy, "wow_game_data") and bpy.wow_game_data.files
        icon = 'COLOR_GREEN' if state else 'COLOR_RED'
        text = "Unload game data" if state else "Load game data"
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
    bl_category = 'WoW'

    def draw(self, context):
        
        layout = self.layout.split()

        col = layout.column()
        
        col.label(text="Flags")
        flag_0x1 = col.operator("scene.wow_mliq_switch_flag", text = 'Flag 0x01', icon = 'MOD_SOFT')
        flag_0x1.Flag = '0x1'
        flag_0x2 = col.operator("scene.wow_mliq_switch_flag", text = 'Flag 0x02', icon = 'MOD_SOFT')
        flag_0x2.Flag = '0x2'
        flag_0x4 = col.operator("scene.wow_mliq_switch_flag", text = 'Flag 0x04', icon = 'MOD_SOFT')
        flag_0x4.Flag = '0x4'
        flag_0x8 = col.operator("scene.wow_mliq_switch_flag", text = 'Invisible', icon = 'VISIBLE_IPO_ON')
        flag_0x8.Flag = '0x8'
        flag_0x10 = col.operator("scene.wow_mliq_switch_flag", text = 'Flag 0x10', icon = 'MOD_SOFT')
        flag_0x10.Flag = '0x10'
        flag_0x20 = col.operator("scene.wow_mliq_switch_flag", text = 'Flag 0x20', icon = 'MOD_SOFT')
        flag_0x20.Flag = '0x20'
        flag_0x40 = col.operator("scene.wow_mliq_switch_flag", text = 'Flag 0x40', icon = 'MOD_SOFT')
        flag_0x40.Flag = '0x40'
        flag_0x80 = col.operator("scene.wow_mliq_switch_flag", text = 'Flag 0x80', icon = 'MOD_SOFT')
        flag_0x80.Flag = '0x80'
        col.label(text="Actions")
        col.operator("scene.wow_mliq_add_flag", text = 'Add flag', icon = 'MOD_SOFT')
        col.operator("scene.wow_mliq_add_all_flags", text = 'Fill all', icon = 'OUTLINER_OB_LATTICE')
        col.operator("scene.wow_mliq_clear_flag", text = 'Clear flag', icon = 'LATTICE_DATA')
        col.operator("scene.wow_mliq_clear_all_flags", text = 'Clear all', icon = 'MOD_LATTICE')

###############################
## Water operators
###############################  
    
class OBJECT_OP_FLAG_SWITCHER(bpy.types.Operator):
    bl_idname = 'scene.wow_mliq_switch_flag'
    bl_label = 'Flag 0x01'
    bl_description = 'Currently displayed flag layer'
    bl_options = {'REGISTER', 'UNDO'}
    
    Flag = bpy.props.EnumProperty(
    name = "Flag Layer",
    description = "Select scale reference type",
    items = [
            ('0x1', "flag_0x1", ""), 
            ('0x2', "flag_0x2", ""),
            ('0x4', "flag_0x4", ""),
            ('0x8', "flag_0x8", ""),
            ('0x10', "flag_0x10", ""),
            ('0x20', "flag_0x20", ""),
            ('0x40', "flag_0x40", ""),
            ('0x80', "flag_0x80", ""),
            ]
    )

    def SwitchFlag(self, Flag):
        water = bpy.context.scene.objects.active
        mesh = water.data
        if water.WowLiquid.Enabled:
            layer = mesh.vertex_colors.get("flag_" + Flag)

            if layer:
                layer.active = True
                mesh.use_paint_mask = True
            else:
                layer = mesh.vertex_colors.new("flag_" + Flag)
                layer.active = True
                # todo: display warning
        
    def execute(self, context):
        self.SwitchFlag(self.Flag)
        return {'FINISHED'}

class OBJECT_OP_ADD_FLAG(bpy.types.Operator):
    bl_idname = 'scene.wow_mliq_add_flag'
    bl_label = 'Add flag'
    bl_description = 'Add flag to currently selected faces'
    
    def AddFlag(self):
        water = bpy.context.scene.objects.active
        mesh = water.data
        if(water.WowLiquid.Enabled):
            for polygon in mesh.polygons:
                if polygon.select:
                    for loop_index in polygon.loop_indices:
                            mesh.vertex_colors[mesh.vertex_colors.active_index].data[loop_index].color = (0, 0, 255)
        
    def execute(self, context):
        self.AddFlag()
        return {'FINISHED'}
    

class OBJECT_OP_CLEAR_FLAG(bpy.types.Operator):
    bl_idname = 'scene.wow_mliq_clear_flag'
    bl_label = 'Clear flag'
    bl_description = 'Remove flag from currently selected faces'
    
    def ClearFlag(self):
        water = bpy.context.scene.objects.active
        mesh = water.data
        if(water.WowLiquid.Enabled):
            for polygon in mesh.polygons:
                if polygon.select:
                    for loop_index in polygon.loop_indices:
                            mesh.vertex_colors[mesh.vertex_colors.active_index].data[loop_index].color = (255, 255, 255)
        
    def execute(self, context):
        self.ClearFlag()
        return {'FINISHED'}
    
class OBJECT_OP_CLEAR_ALL_FLAGS(bpy.types.Operator):
    bl_idname = 'scene.wow_mliq_clear_all_flags'
    bl_label = 'Clear all flags'
    bl_description = 'Clear all flags on currently selected layer'
    
    def ClearAllFlags(self):
        water = bpy.context.scene.objects.active
        mesh = water.data
        if(water.WowLiquid.Enabled):
            for polygon in mesh.polygons:
                    for loop_index in polygon.loop_indices:
                            mesh.vertex_colors[mesh.vertex_colors.active_index].data[loop_index].color = (255, 255, 255)
        
    def execute(self, context):
        self.ClearAllFlags()
        return {'FINISHED'}
    
class OBJECT_OP_ADD_ALL_FLAGS(bpy.types.Operator):
    bl_idname = 'scene.wow_mliq_add_all_flags'
    bl_label = 'Fill all flags'
    bl_description = 'Fill all with flags on currently selected layer'
    
    def AddAllFlags(self):
        water = bpy.context.scene.objects.active
        mesh = water.data
        if(water.WowLiquid.Enabled):
            for polygon in mesh.polygons:
                    for loop_index in polygon.loop_indices:
                            mesh.vertex_colors[mesh.vertex_colors.active_index].data[loop_index].color = (0, 0, 255)
        
    def execute(self, context):
        self.AddAllFlags()
        return {'FINISHED'}
    
###############################
## Object operators
############################### 

class OBJECT_OP_Add_Scale(bpy.types.Operator):
    bl_idname = 'scene.wow_add_scale_reference'
    bl_label = 'Add scale'
    bl_description = 'Adds a WoW scale prop'
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

    def AddScale(self, ScaleType):
        
        if ScaleType == 'HUMAN':
            bpy.ops.object.add(type='LATTICE')
            scale_obj = bpy.context.object
            scale_obj.name = "Human Scale"
            scale_obj.dimensions = (0.582, 0.892, 1.989)

        elif ScaleType == 'TAUREN':
            bpy.ops.object.add(type='LATTICE')
            scale_obj = bpy.context.object
            scale_obj.name = "Tauren Scale"
            scale_obj.dimensions = (1.663, 1.539, 2.246)

        elif ScaleType == 'TROLL':
            bpy.ops.object.add(type='LATTICE')
            scale_obj = bpy.context.object
            scale_obj.name = "Troll Scale"
            scale_obj.dimensions = (1.116, 1.291, 2.367)

        elif ScaleType == 'GNOME':
            bpy.ops.object.add(type='LATTICE')
            scale_obj = bpy.context.object
            scale_obj.name = "Gnome Scale"
            scale_obj.dimensions = (0.362, 0.758, 0.991)

        self.report({'INFO'}, "Added " + ScaleType + " scale")
        
    def execute(self, context):
        self.AddScale(self.ScaleType)
        return {'FINISHED'} 
    
    
class OBJECT_OP_Add_Water(bpy.types.Operator):
    bl_idname = 'scene.wow_add_water'
    bl_label = 'Add water'
    bl_description = 'Adds a WoW water plane'
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
    
    def AddWater(self, xPlanes, yPlanes):
        bpy.ops.mesh.primitive_grid_add(x_subdivisions = xPlanes + 1,
                                        y_subdivisions = yPlanes + 1,
                                        radius=4.1666625 / 2
                                        )
        water = bpy.context.scene.objects.active
        bpy.ops.transform.resize( value=(xPlanes, yPlanes, 1.0) )
        
        water.name = water.name + "_Liquid"
        
        mesh = water.data

        bit = 1
        while bit <= 0x80:
            mesh.vertex_colors.new("flag_" + hex(bit))
            bit <<= 1
                                     
        water.WowLiquid.Enabled = True

        
    def execute(self, context):
        self.AddWater(self.xPlanes, self.yPlanes)
        return {'FINISHED'}
    
class OBJECT_OP_Add_Fog(bpy.types.Operator):
    bl_idname = 'scene.wow_add_fog'
    bl_label = 'Add fog'
    bl_description = 'Adds a WoW fog object to the scene'
                        
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
        return {'FINISHED'}
    
        
class OBJECT_OP_Invert_Portals(bpy.types.Operator):
    bl_idname = 'scene.wow_invert_portals'
    bl_label = 'Inevert portals'
    bl_description = 'Invert direction of all selected WoW portals'
    
    
    def InvertPortal(self):
        for ob in bpy.context.selected_objects:
            if(ob.WowPortalPlane.Enabled == True):
                
                first = ob.WowPortalPlane.First
                second = ob.WowPortalPlane.Second
                
                ob.WowPortalPlane.First = second
                ob.WowPortalPlane.Second = first
                    
    def execute(self, context):
        
        self.InvertPortal()
        return {'FINISHED'}
        
class OBJECT_OP_Fill_Group_Name(bpy.types.Operator):
    bl_idname = 'scene.wow_fill_group_name'
    bl_label = 'Fill group name'
    bl_description = 'Fills the specified group name for selected objects'
    bl_options = {'REGISTER', 'UNDO'}
    
    name = bpy.props.StringProperty()
    
    def FillGroupName(self, name):
        for ob in bpy.context.selected_objects:
            if(ob.WowWMOGroup.Enabled == True):
                ob.WowWMOGroup.GroupName = name        

    def execute(self, context):
        self.FillGroupName(self.name)
        return {'FINISHED'}           
        
class OBJECT_OP_Fill_Textures(bpy.types.Operator):
    bl_idname = 'scene.wow_fill_textures'
    bl_label = 'Fill textures'
    bl_description = 'Fills Texture 1 field of WoW materials with paths from applied image. \
                      Is able to account or not account relative texture path.'
    bl_options = {'REGISTER', 'UNDO'}
               
    
    def FillTextures(self):
        for ob in bpy.context.selected_objects:
            mesh = ob.data
            for i in range(len(mesh.materials)):
                if mesh.materials[i].active_texture is not None \
                and not mesh.materials[i].WowMaterial.Texture1 \
                and mesh.materials[i].active_texture.type == 'IMAGE' \
                and mesh.materials[i].active_texture.image is not None:

                    if(bpy.context.scene.WoWRoot.UseTextureRelPath):
                        mesh.materials[i].WowMaterial.Texture1 = os.path.splitext(
                            os.path.relpath(
                                mesh.materials[i].active_texture.image.filepath,
                                bpy.context.scene.WoWRoot.TextureRelPath 
                                )
                            )[0] + ".blp"
                    else:
                        mesh.materials[i].WowMaterial.Texture1 = os.path.splitext(
                            mesh.materials[i].active_texture.image.filepath
                            )[0] + ".blp"            

    def execute(self, context):
        
        self.FillTextures()
        return {'FINISHED'}               

class OBJECT_OP_Quick_Collision(bpy.types.Operator):
    bl_idname = 'scene.wow_quick_collision'
    bl_label = 'Generate basic collision for selected objects'
    bl_description = 'Generates WoW collision equal to geometry of the selected objects'
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
    
    def QuickCollision(self, NodeSize, CleanUp):
        for ob in bpy.context.selected_objects:
            ob.WowVertexInfo.Enabled = True
            bpy.context.scene.objects.active = ob
            
            if CleanUp:
                for vertex_group in ob.vertex_groups:
                    if (vertex_group.name != ob.WowVertexInfo.VertexGroup) \
                    and (vertex_group.name != ob.WowVertexInfo.BatchTypeA) \
                    and (vertex_group.name != ob.WowVertexInfo.BatchTypeB) \
                    and (vertex_group.name != ob.WowVertexInfo.Lightmap) \
                    and (vertex_group.name != ob.WowVertexInfo.Blendmap) \
                    and (vertex_group.name != ob.WowVertexInfo.SecondUV):
                        ob.vertex_groups.remove(vertex_group)
                        
            if ob.vertex_groups.get(ob.WowVertexInfo.VertexGroup) != None:
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
            ob.WowVertexInfo.NodeSize = NodeSize

    def execute(self, context):
        
        self.QuickCollision(self.NodeSize, self.CleanUp)
        return {'FINISHED'}        
        
class OBJECT_OP_Texface_to_material(bpy.types.Operator):
    bl_idname = 'scene.wow_texface_to_material'
    bl_label = 'Texface to material'
    bl_description = 'Generate materials out of texfaces in selected objects'

    def execute(self, context):
        if bpy.context.selected_objects[0] != None:
            bpy.context.scene.objects.active = bpy.context.selected_objects[0]
        bpy.ops.view3d.material_remove()
        bpy.ops.view3d.texface_to_material()
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
    
    def ToPortal(self, First, Second):
        for ob in bpy.context.selected_objects:
            if ob.type == 'MESH':
                ob.WowWMOGroup.Enabled = False
                ob.WowLiquid.Enabled = False
                ob.WowFog.Enabled = False
                ob.WowPortalPlane.Enabled = True
                ob.WowPortalPlane.First = First
                ob.WowPortalPlane.Second = Second


    def execute(self, context):
        
        self.ToPortal(self.First, self.Second)
        return {'FINISHED'}
        
class OBJECT_OP_To_Group(bpy.types.Operator):
    bl_idname = 'scene.wow_selected_objects_to_group'
    bl_label = 'Selected objects to WMO group'
    bl_description = 'Transfer all selected objects to WoW WMO groups'
    bl_options = {'REGISTER', 'UNDO'}
        
    GroupName = bpy.props.StringProperty()
    GroupDesc = bpy.props.StringProperty()

    PlaceType = bpy.props.EnumProperty(
        name = "Place Type",
        description = "Set WMO group place type",
        items = [('8', "Outdoor", ""), ('8192', "Indoor", "")],
        default = '8'
        )

    GroupID = bpy.props.IntProperty(
        name="DBC Group ID",
        description="WMO Group ID in DBC file"
        )

    VertShad = bpy.props.BoolProperty(
        name="Vertex shading",
        description="Save gropu vertex shading",
        default = False
        )

    SkyBox = bpy.props.BoolProperty(
        name="Use Skybox",
        description="Use skybox in group",
        default = False
        )        
    
    def ToGroup(self, PlaceType, GroupName, GroupDesc, GroupID, VertShad, SkyBox):
        for ob in bpy.context.selected_objects:
            
            if ob.type == 'MESH':
                ob.WowLiquid.Enabled = False
                ob.WowFog.Enabled = False
                ob.WowPortalPlane.Enabled = False  
                ob.WowWMOGroup.Enabled = True
                ob.WowWMOGroup.PlaceType = PlaceType
                ob.WowWMOGroup.GroupName = GroupName
                ob.WowWMOGroup.GroupDesc = GroupDesc
                ob.WowWMOGroup.GroupID = GroupID
                ob.WowWMOGroup.VertShad = VertShad
                ob.WowWMOGroup.SkyBox = SkyBox

    def execute(self, context):
        
        self.ToGroup(self.PlaceType, self.GroupName, self.GroupDesc, self.GroupID, self.VertShad, self.SkyBox)
        return {'FINISHED'}
    
class OBJECT_OP_To_WoWMaterial(bpy.types.Operator):
    bl_idname = 'scene.wow_selected_objects_to_wow_material'
    bl_label = 'Materials of selected objects to WoW Material'
    bl_description = 'Transfer all materials of selected objects to WoW material'
    bl_options = {'REGISTER', 'UNDO'}

    shaderEnum = [
        ('0', "Diffuse", ""), ('1', "Specular", ""), ('2', "Metal", ""), 
        ('3', "Env", ""), ('4', "Opaque", ""), ('5', "EnvMetal", ""), 
        ('6', "TwoLayerDiffuse", ""), ('7', "TwoLayerEnvMetal", ""), ('8', "TwoLayerTerrain", ""), 
        ('9', "DiffuseEmissive", ""), ('10', "Tangent", ""), ('11', "MaskedEnvMetal", ""), 
        ('12', "EnvMetalEmissive", ""), ('13', "TwoLayerDiffuseOpaque", ""), ('14', "TwoLayerDiffuseEmissive", "")
        ] #, ('16', "Diffuse", "")]
    terrainEnum = [
        ('0', "Dirt", ""), ('1', "Metallic", ""), ('2', "Stone", ""), 
        ('3', "Snow", ""), ('4', "Wood", ""), ('5', "Grass", ""), 
        ('6', "Leaves", ""), ('7', "Sand", ""), ('8', "Soggy", ""), 
        ('9', "Dusty Grass", ""), ('10', "None", ""), ('11', "Water", "")]
    blendingEnum = [
        ('0', "Blend_Opaque", ""), ('1', "Blend_AlphaKey", ""), 
        ('2', "Blend_Alpha", ""), ('3', "Blend_Add", ""), ('4', "Blend_Mod", ""), 
        ('5', "Blend_Mod2x", ""), ('6', "Blend_ModAdd", ""), ('7', "Blend_InvSrcAlphaAdd", ""), 
        ('8', "Blend_InvSrcAlphaOpaque", ""), ('9', "Blend_SrcAlphaOpaque", ""), ('10', "Blend_NoAlphaAdd", ""),
        ('11', "Blend_ConstantAlpha", "")
        ]
    
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

    TerrainType = bpy.props.EnumProperty(
        items=terrainEnum,
        name="Terrain Type",
        description="Terrain type assigned to that material"
        )

    TwoSided = bpy.props.BoolProperty(
        name="TwoSided",
        description="Enable TwoSided"
        )

    Darkened = bpy.props.BoolProperty(
        name="Darkened",
        description="Enable Darkened"
        )

    NightGlow = bpy.props.BoolProperty(
        name="Unshaded",
        description="Enable NightGlow"
        )    
    
    def ToWoWMaterial(self, Shader, BlendingMode, TerrainType, TwoSided, Darkened, NightGlow):
        for ob in bpy.context.selected_objects:
            if(ob.WowWMOGroup.Enabled == True):
                for i in range(len(ob.data.materials)):
                    material = ob.data.materials[i].WowMaterial
                    material.Enabled = True
                    material.Shader = Shader
                    material.BlendingMode = BlendingMode
                    material.TerrainType = TerrainType
                    material.TwoSided = TwoSided
                    material.Darkend = Darkened
                    material.NightGlow = NightGlow
                    

    def execute(self, context):
        
        self.ToWoWMaterial(self.Shader, self.BlendingMode, self.TerrainType, self.TwoSided, self.Darkened, self.NightGlow)
        return {'FINISHED'}
    
###############################
## Visibility operators
###############################  
    
class OBJECT_OP_Hide_Show_All(bpy.types.Operator):
    bl_idname = 'scene.wow_hide_show_all_objects'
    bl_label = 'Hide/Show all'
    bl_description = 'Hide/Show all WoW WMO objects'

    def execute(self, context):
        state = True
        for ob in bpy.context.scene.objects:
            if ob.WowWMOGroup.Enabled \
            or ob.WowPortalPlane.Enabled \
            or ob.WowFog.Enabled \
            or ob.WowLiquid.Enabled \
            or ob.data.WowLight.Enabled:
                if bpy.context.scene.WoWVisibility.All:
                    ob.hide = True
                    state = False
                else:
                    ob.hide = False
                    state = True
        bpy.context.scene.WoWVisibility.All = state
        return {'FINISHED'}
    

class OBJECT_OP_Hide_Show_Water(bpy.types.Operator):
    bl_idname = 'scene.wow_hide_show_water'
    bl_label = 'Hide/Show all water planes'
    bl_description = 'Hide/Show all WoW WMO water planes'

    def execute(self, context):
        state = True
        for ob in bpy.context.scene.objects:
            if(ob.WowLiquid.Enabled == True):
                if(bpy.context.scene.WoWVisibility.Water == True):
                    ob.hide = True
                    state = False
                else:
                    ob.hide = False
                    state = True
        bpy.context.scene.WoWVisibility.Water = state
        return {'FINISHED'}   

class OBJECT_OP_Hide_Show_Portals(bpy.types.Operator):
    bl_idname = 'scene.wow_hide_show_portals'
    bl_label = 'Hide/Show all portals'
    bl_description = 'Hide/Show all WoW WMO portal objects'

    def execute(self, context):
        state = True
        for ob in bpy.context.scene.objects:
            if(ob.WowPortalPlane.Enabled == True):
                if(bpy.context.scene.WoWVisibility.Portals == True):
                    ob.hide = True
                    state = False
                else:
                    ob.hide = False
                    state = True
        bpy.context.scene.WoWVisibility.Portals = state
        return {'FINISHED'}   
    
class OBJECT_OP_Hide_Show_Indoor(bpy.types.Operator):
    bl_idname = 'scene.wow_hide_show_indoor'
    bl_label = 'Hide/Show all indoor groups'
    bl_description = 'Hide/Show all WoW WMO indoor groups'

    def execute(self, context):
        state = True
        for ob in bpy.context.scene.objects:
            if((ob.WowWMOGroup.Enabled == True) & (ob.WowWMOGroup.PlaceType == '8192')):
                if(bpy.context.scene.WoWVisibility.Indoor == True):
                    ob.hide = True
                    state = False
                else:
                    ob.hide = False
                    state = True
        bpy.context.scene.WoWVisibility.Indoor = state
        return {'FINISHED'}   
    
class OBJECT_OP_Hide_Show_Outdoor(bpy.types.Operator):
    bl_idname = 'scene.wow_hide_show_outdoor'
    bl_label = 'Hide/Show all outdoor groups'
    bl_description = 'Hide/Show all WoW WMO outdoor groups'

    def execute(self, context):
        state = True
        for ob in bpy.context.scene.objects:
            if((ob.WowWMOGroup.Enabled == True) & (ob.WowWMOGroup.PlaceType == '8')):
                if(bpy.context.scene.WoWVisibility.Outdoor == True):
                    ob.hide = True
                    state = False
                else:
                    ob.hide = False
                    state = True
        bpy.context.scene.WoWVisibility.Outdoor = state
        return {'FINISHED'}
    
class OBJECT_OP_Hide_Show_Fog(bpy.types.Operator):
    bl_idname = 'scene.wow_hide_show_fog'
    bl_label = 'Hide/Show all WoW fog objects'
    bl_description = 'Hide/Show all WoW WMO fog objects'

    def execute(self, context):
        state = True
        for ob in bpy.context.scene.objects:
            if(ob.WowFog.Enabled == True):
                if(bpy.context.scene.WoWVisibility.Fog == True):
                    ob.hide = True
                    state = False
                else:
                    ob.hide = False
                    state = True
        bpy.context.scene.WoWVisibility.Fog = state
        return {'FINISHED'}
    
    
class OBJECT_OP_Hide_Show_Light(bpy.types.Operator):
    bl_idname = "scene.wow_hide_show_light"
    bl_label = "Hide/Show all WoW light objects"
    bl_description = "Hide/Show all WoW WMO light objects"
    
    def execute(self, context):
        state = True
        for ob in bpy.context.scene.objects:
            if(ob.type == 'LAMP' and ob.data.WowLight.Enabled):
                if(bpy.context.scene.WoWVisibility.Light == True):
                    ob.hide = True
                    state = False
                else:
                    ob.hide = False
                    state = True
        bpy.context.scene.WoWVisibility.Light = state    
        return {"FINISHED"}
        

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
    # RegisterWMOToolsPanelObjectMode()
    # registered in __init__
    #bpy.utils.register_class(WowMaterialPanel)

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
    # UnregisterWMOToolsPanelObjectMode()
    # unregistered in __init__
    #bpy.utils.unregister_class(WowMaterialPanel)

 


