
import bpy
import bpy.utils
import bpy.types
import os
from . import wmo_format
from .wmo_format import *
from . import debug_utils
from .debug_utils import *

from bpy.app.handlers import persistent

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


class WowRootPropertyGroup(bpy.types.PropertyGroup):
    Enabled = bpy.props.BoolProperty(name="", description="Enable WoW root properties", default = True)

    UseAmbient = bpy.props.BoolProperty(
        name="Use Ambient",
        description="Use ambient lighting inside indoor groups",
        default= True,
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
    shaderEnum = [('0', "Diffuse", ""), ('1', "Specular", ""), ('2', "Metal", ""), \
                  ('3', "Env", ""), ('4', "Opaque", ""), ('5', "EnvMetal", ""), \
                  ('6', "TwoLayerDiffuse", ""), ('7', "TwoLayerEnvMetal", ""), ('8', "TwoLayerTerrain", ""), \
                  ('9', "DiffuseEmissive", ""), ('10', "Tangent", ""), ('11', "MaskedEnvMetal", ""), ('12', "EnvMetalEmissive", ""), \
                  ('13', "TwoLayerDiffuseOpaque", ""), ('14', "TwoLayerDiffuseEmissive", "")]#, ('16', "Diffuse", "")]
    terrainEnum = [('0', "Dirt", ""), ('1', "Metallic", ""), ('2', "Stone", ""), \
                   ('3', "Snow", ""), ('4', "Wood", ""), ('5', "Grass", ""), \
                   ('6', "Leaves", ""), ('7', "Sand", ""), ('8', "Soggy", ""), \
                   ('9', "Dusty Grass", ""), ('10', "None", ""), ('11', "Water", "")]
    blendingEnum = [('0', "Blend_Opaque", ""), ('1', "Blend_AlphaKey", ""), \
                    ('2', "Blend_Alpha", ""), ('3', "Blend_Add", ""), ('4', "Blend_Mod", ""), \
                    ('5', "Blend_Mod2x", ""), ('6', "Blend_ModAdd", ""), ('7', "Blend_InvSrcAlphaAdd", ""), \
                    ('8', "Blend_InvSrcAlphaOpaque", ""), ('9', "Blend_SrcAlphaOpaque", ""), ('10', "Blend_NoAlphaAdd", ""), ('11', "Blend_ConstantAlpha", "")]
    
    Enabled = bpy.props.BoolProperty(name="", description="Enable WoW material properties")
    Shader = bpy.props.EnumProperty(items=shaderEnum, name="Shader", description="WoW shader assigned to this material")
    BlendingMode = bpy.props.EnumProperty(items=blendingEnum, name="Blending Mode", description="WoW material blending mode")
    Texture1 = bpy.props.StringProperty(name="Texture 1", description="Texture assigned to first slot in shader")
    Color1 = bpy.props.FloatVectorProperty(name="Emissive Color", subtype='COLOR', default=(1,1,1), min=0.0, max=1.0)
    Flags1 = bpy.props.EnumProperty(items=[('0', "Clamp", ""), ('1', "Repeat", "")], name="Extension 2", description="Extension mode for texture 1")
    Texture2 = bpy.props.StringProperty(name="Texture 2", description="Texture assigned to second slot in shader")
    Color2 = bpy.props.FloatVectorProperty(name="Emissive Color 2", subtype='COLOR', default=(1,1,1), min=0.0, max=1.0)
    TerrainType = bpy.props.EnumProperty(items=terrainEnum, name="Terrain Type", description="Terrain type assigned to this material. Used for footstep sounds and similar things.")
    Texture3 = bpy.props.StringProperty(name="Texture 3", description="Texture assigned to third slot in shader")
    Color3 = bpy.props.FloatVectorProperty(name="Emissive Color 3", subtype='COLOR', default=(1,1,1), min=0.0, max=1.0)
    Flags3 = bpy.props.EnumProperty(items=[('0', "Clamp", ""), ('1', "Repeat", "")], name="Extension 3", description="Extension mode for texture 3")
    TwoSided = bpy.props.BoolProperty(name="TwoSided", description="Enable TwoSided")
    Darkened = bpy.props.BoolProperty(name="Darkened", description="Enable Darkened")
    NightGlow = bpy.props.BoolProperty(name="Unshaded", description="Enable NightGlow")

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
        return (context.object is not None and context.object.data is not None and isinstance(context.object.data, bpy.types.Lamp))

class WowLightPropertyGroup(bpy.types.PropertyGroup):
    lightTypeEnum = [('0', "Omni", ""), ('1', "Spot", ""), ('2', "Direct", ""), ('3', "Ambient", "")]
    Enabled = bpy.props.BoolProperty(name="", description="Enable wow light properties")
    LightType = bpy.props.EnumProperty(items=lightTypeEnum, name="Type", description="Type of the lamp")
    Type = bpy.props.BoolProperty(name="Type", description="True if i dunno")
    UseAttenuation = bpy.props.BoolProperty(name="Use attenuation", description="True if lamp use attenuation")
    Padding = bpy.props.BoolProperty(name="Padding", description="True if lamp use Padding")
    Color = bpy.props.FloatVectorProperty(name="Color", subtype='COLOR', default=(1,1,1), min=0.0, max=1.0)
    Intensity = bpy.props.FloatProperty(name="Intensity", description="Intensity of the lamp")
    ColorAlpha = bpy.props.FloatProperty(name="ColorAlpha", description="Color alpha", default=1, min=0.0, max=1.0)
    AttenuationStart = bpy.props.FloatProperty(name="Attenuation start", description="Distance at which light intensity starts to decrease")
    AttenuationEnd = bpy.props.FloatProperty(name="Attenuation end", description="Distance at which light intensity reach 0")

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
        self.layout.prop_search(context.object.WowVertexInfo, "VertexGroup", context.object, "vertex_groups", text="Collision vertex group")
        self.layout.prop(context.object.WowVertexInfo, "NodeSize", slider=True)
        self.layout.prop_search(context.object.WowVertexInfo, "BatchTypeA", context.object, "vertex_groups", text="Batch type A vertex group")
        self.layout.prop_search(context.object.WowVertexInfo, "BatchTypeB", context.object, "vertex_groups", text="Batch type B vertex group")
        self.layout.prop_search(context.object.WowVertexInfo, "Lightmap", context.object, "vertex_groups", text="Lightmap")
        self.layout.prop_search(context.object.WowVertexInfo, "Blendmap", context.object, "vertex_groups", text="Blendmap")
        self.layout.prop_search(context.object.WowVertexInfo, "SecondUV", context.object.data, "uv_textures", text="Second UV")

    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.object.data is not None and isinstance(context.object.data,bpy.types.Mesh) and context.object.WowWMOGroup.Enabled)

class WowVertexInfoPropertyGroup(bpy.types.PropertyGroup):
    VertexGroup = bpy.props.StringProperty()
    NodeSize = bpy.props.IntProperty(name="Node max size", description="Max count of faces for a node in bsp tree", default=150, min=1, soft_max=500)
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
        #self.layout.prop(context.object.WowWMOGroup, "PortalGroupID")
        self.layout.prop(context.object.WowWMOGroup, "PlaceType")
        self.layout.prop(context.object.WowWMOGroup, "GroupID")
        self.layout.prop(context.object.WowWMOGroup, "VertShad")
        self.layout.prop(context.object.WowWMOGroup, "NoLocalLighting")
        self.layout.prop(context.object.WowWMOGroup, "AlwaysDraw")
        self.layout.prop(context.object.WowWMOGroup, "IsMountAllowed")
        self.layout.prop(context.object.WowWMOGroup, "SkyBox")
#        self.layout.prop(context.object.WowWMOGroup, "Fog1")
#        self.layout.prop(context.object.WowWMOGroup, "Fog2")
#        self.layout.prop(context.object.WowWMOGroup, "Fog3")
#        self.layout.prop(context.object.WowWMOGroup, "Fog4")
        self.layout.prop_search(context.object.WowWMOGroup, "Fog1", bpy.context.scene, "objects", text="Fog1")
        self.layout.prop_search(context.object.WowWMOGroup, "Fog2", bpy.context.scene, "objects", text="Fog2")
        self.layout.prop_search(context.object.WowWMOGroup, "Fog3", bpy.context.scene, "objects", text="Fog3")
        self.layout.prop_search(context.object.WowWMOGroup, "Fog4", bpy.context.scene, "objects", text="Fog4")
        
        layout.enabled = context.object.WowWMOGroup.Enabled

    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.object.data is not None and isinstance(context.object.data,bpy.types.Mesh) and \
        not context.object.WowPortalPlane.Enabled and not context.object.WowLiquid.Enabled and not context.object.WowFog.Enabled )

class WowWMOMODRStore(bpy.types.PropertyGroup):
    value = bpy.props.IntProperty(name="Doodads Ref")
    
def GetFogObjects(self, context):
    fogs = []
    
    fogs.append(('0', "None", "")) # setting a default entry as a first element of our enum
    
    for object in bpy.context.scene.objects:
        if object.WowFog.Enabled:
                fogs.append((object.name, object.name, ""))
        
    return fogs
    
    
    
class WowWMOGroupPropertyGroup(bpy.types.PropertyGroup):
    Enabled = bpy.props.BoolProperty(name="", description="Enable wow WMO group properties")
    GroupName = bpy.props.StringProperty()
    GroupDesc = bpy.props.StringProperty()
    #PortalGroupID = bpy.props.IntProperty(name="Group ID for root", description="Group ID for root and portal")
    placeTypeEnum = [('8', "Outdoor", ""), ('8192', "Indoor", "")]
    PlaceType = bpy.props.EnumProperty(items=placeTypeEnum, name="Place Type", description="Group is indoor or outdoor")
    GroupID = bpy.props.IntProperty(name="DBC Group ID", description="WMO Group ID in DBC file")
    VertShad = bpy.props.BoolProperty(name="Vertex color", description="Save group vertex shading", default = False)
    NoLocalLighting = bpy.props.BoolProperty(name="No local lighting", description="Do not use local diffuse lightning", default = False)
    AlwaysDraw = bpy.props.BoolProperty(name="Always draw", description="Always draw the group", default = False)
    IsMountAllowed = bpy.props.BoolProperty(name="Mounts allowed", description="Allows or prohibits mounts in the group. Works only with generated navmesh delivered to server.", default = False)
    SkyBox = bpy.props.BoolProperty(name="Use Skybox", description="Use skybox in group", default = False)
#    Fog1 = bpy.props.EnumProperty(items=GetFogObjects, name="Fog 1", description="Fog of an object")
#    Fog2 = bpy.props.EnumProperty(items=GetFogObjects, name="Fog 2", description="Fog of an object")
#    Fog3 = bpy.props.EnumProperty(items=GetFogObjects, name="Fog 3", description="Fog of an object")
#    Fog4 = bpy.props.EnumProperty(items=GetFogObjects, name="Fog 4", description="Fog of an object")
    Fog1 = bpy.props.StringProperty()
    Fog2 = bpy.props.StringProperty()
    Fog3 = bpy.props.StringProperty()
    Fog4 = bpy.props.StringProperty()
    MODR = bpy.props.CollectionProperty(type=WowWMOMODRStore)

def RegisterWowWMOGroupProperties():
    bpy.types.Object.WowWMOGroup = bpy.props.PointerProperty(type=WowWMOGroupPropertyGroup)

def UnregisterWowWMOGroupProperties():
    bpy.types.Object.WowWMOGroup = None


###############################
## Portal plane
###############################
''' 

def GetGroupObjectsReferences(self, context):
    
    groups = []
    groups.append(('0', "None", "")) # setting a default entry as a first element of our enum

    for obj in bpy.context.scene.objects:
        if obj.WowWMOGroup.Enabled:
            groups.append((obj.name, obj.name, ""))
           
    return groups


def UpdateFirstGroupObjectReference(self, context):

    if context.object.WowPortalPlane.First == context.object.WowPortalPlane.Second and context.object.WowPortalPlane.First != '0':
        context.object.WowPortalPlane.Second = '0'          
            
def UpdateSecondGroupObjectReference(self, context):
        
    if context.object.WowPortalPlane.Second == context.object.WowPortalPlane.First and context.object.WowPortalPlane.Second != '0':
        context.object.WowPortalPlane.First = '0'
'''
   

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
        layout.enabled = context.object.WowPortalPlane.Enabled
        self.layout.prop_search(context.object.WowPortalPlane, "First", bpy.context.scene, "objects", text="First group")
        self.layout.prop_search(context.object.WowPortalPlane, "Second", bpy.context.scene, "objects", text="Second group")

    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.object.data is not None and isinstance(context.object.data,bpy.types.Mesh) and \
        not context.object.WowWMOGroup.Enabled and not context.object.WowLiquid.Enabled and not context.object.WowFog.Enabled)

class WowPortalPlanePropertyGroup(bpy.types.PropertyGroup):
    Enabled = bpy.props.BoolProperty(name="", description="Enable wow WMO group properties")
#    First = bpy.props.EnumProperty(items=GetGroupObjectsReferences, name="First group", description="First group")
#    Second = bpy.props.EnumProperty(items=GetGroupObjectsReferences, name="Second group", description="Second group")

    First = bpy.props.StringProperty()
    Second = bpy.props.StringProperty()
    PortalID = bpy.props.IntProperty(name="Portal's ID", description="Portal ID")

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

def GetGroupObjects(self, context):
    groups = []
    
    groups.append(('0', "None", "")) # setting a default entry as a first element of our enum
    
    for object in bpy.context.scene.objects:
        if object.type != 'LAMP' and object.WowWMOGroup.Enabled:
                groups.append((object.name, object.name, ""))
        
    return groups
    
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
        self.layout.prop_search(context.object.WowLiquid, "WMOGroup", bpy.context.scene, "objects", text="WMO Group")
        layout.enabled = context.object.WowLiquid.Enabled

    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.object.data is not None and isinstance(context.object.data,bpy.types.Mesh) and context.object.WowLiquid.Enabled)

class WowLiquidPropertyGroup(bpy.types.PropertyGroup):
    liquidTypeEnum = [('13', "WMO Water", ""), ('17', "WMO Water Interior", ""), \
        ('14', "WMO Ocean", ""), ('19', "WMO Lava", ""), ('20', "WMO Slime", ""), \
        ('5', "Slow Water", ""), ('6', "Slow Ocean", ""), ('7', "Slow Magma", ""), \
        ('8', "Slow Slime", ""), ('9', "Fast Water", ""), ('10', "Fast Ocean", ""), \
        ('11', "Fast Magma", ""), ('12', "Fast Slime", ""),('21', "Naxxramas - Slime", ""), \
        ('41', "Coilfang Raid - Water", ""), ('81', "Lake Wintergrasp - Water", ""), \
        ('61', "Hyjal Past - Water", ""), ('100', "Basic Procedural Water", ""), ('0', "Unsupported", "")]
    Enabled = bpy.props.BoolProperty(name="", description="Enable wow liquid properties", default=False)
    LiquidType = bpy.props.EnumProperty(items=liquidTypeEnum, name="Liquid Type", description="Type of the liquid present in this WMO group")
    WMOGroup = bpy.props.StringProperty()

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
        return (context.object is not None and context.object.data is not None and isinstance(context.object.data,bpy.types.Mesh) and context.object.WowFog.Enabled)

def UpdateFogColor(self, context):
    bpy.context.scene.objects.active.color = (self.Color1[0], self.Color1[1], self.Color1[2], 0.5)


class WowFogPropertyGroup(bpy.types.PropertyGroup):
    Enabled = bpy.props.BoolProperty(name="", description="Enable WoW WMO fog properties")
    IgnoreRadius = bpy.props.BoolProperty(name="Ignore Radius", description="Ignore radius in CWorldView::QueryCameraFog", default = False)
    Unknown = bpy.props.BoolProperty(name="Unknown Flag", description="Check that in if you know what it is", default = False)
    InnerRadius = bpy.props.FloatProperty(name="Inner Radius (%)", description="A radius of fog starting to fade", default=100.0, min=0.0, max=100.0)
    EndDist = bpy.props.FloatProperty(name="Farclip", description="Fog farclip", default=700.0, min=0.0, max=1500.0)
    StartFactor = bpy.props.FloatProperty(name="Nearclip", description="Fog nearclip", default=0.5, min=0.0, max=1.0)
    Color1 = bpy.props.FloatVectorProperty(name="Color", subtype='COLOR', default=(1,1,1), min=0.0, max=1.0, update=UpdateFogColor)
    EndDist2 = bpy.props.FloatProperty(name="Underwater farclip", description="Underwater fog farclip", default=700.0, min=0.0, max=1500.0)
    StartFactor2 = bpy.props.FloatProperty(name="Underwater nearclip", description="Underwater fog nearclip", default=0.5, min=0.0, max=1.0)
    Color2 = bpy.props.FloatVectorProperty(name="Underwater Color", subtype='COLOR', default=(1,1,1), min=0.0, max=1.0)        

def RegisterWowFogProperties():
    bpy.types.Object.WowFog = bpy.props.PointerProperty(type=WowFogPropertyGroup)

def UnregisterWowFogProperties():
    bpy.types.Object.WowFog = None


###############################
## WMO Toolbar
###############################    

class WoWVisibilityPropertyGroup(bpy.types.PropertyGroup):
    Enabled = bpy.props.BoolProperty(name="", description="Enable WoW visibility properties", default = True)

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
        col.operator("scene.wow_quick_collision", text = 'Quick Collision', icon = 'STYLUS_PRESSURE')
        col.operator("scene.wow_fill_textures", text = 'Fill textures', icon = 'FILE_IMAGE')
        col.operator("scene.wow_fill_group_name", text = 'Fill group name', icon = 'FONTPREVIEW')
        col.operator("scene.wow_invert_portals", text = 'Invert portals', icon = 'FILE_REFRESH')
        col.operator("scene.wow_add_fog", text = 'Add fog', icon = 'GROUP_VERTEX')
        col.operator("scene.wow_add_water", text = 'Add water', icon = 'MOD_WAVE')
        col.label(text="Display")
        col.operator("scene.wow_hide_show_outdoor", text = 'Outdoor', icon = 'BBOX')
        col.operator("scene.wow_hide_show_indoor", text = 'Indoor', icon = 'ROTATE')
        col.operator("scene.wow_hide_show_portals", text = 'Portals', icon = 'MOD_PARTICLES')
        col.operator("scene.wow_hide_show_fog", text = 'Fog', icon = 'FORCE_TURBULENCE')
        col.operator("scene.wow_hide_show_water", text = 'Water', icon = 'MOD_FLUIDSIM')
        col.operator("scene.wow_hide_show_light", text = 'Light', icon = 'LAMP_SPOT')
        col.operator("scene.wow_hide_show_all_objects", text = 'All', icon = 'VISIBLE_IPO_ON') 

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
        col.operator("scene.wow_mliq_flag_0x01", text = 'Flag 0x01', icon = 'MOD_SOFT')
        col.operator("scene.wow_mliq_flag_0x02", text = 'Flag 0x02', icon = 'MOD_SOFT')
        col.operator("scene.wow_mliq_flag_0x04", text = 'Flag 0x04', icon = 'MOD_SOFT')
        col.operator("scene.wow_mliq_flag_0x08", text = 'Invisible', icon = 'VISIBLE_IPO_ON')
        col.operator("scene.wow_mliq_flag_0x10", text = 'Flag 0x10', icon = 'MOD_SOFT')
        col.operator("scene.wow_mliq_flag_0x20", text = 'Flag 0x20', icon = 'MOD_SOFT')
        col.operator("scene.wow_mliq_flag_0x40", text = 'Flag 0x40', icon = 'MOD_SOFT')
        col.operator("scene.wow_mliq_flag_0x80", text = 'Flag 0x80', icon = 'MOD_SOFT')
        col.label(text="Actions")
        col.operator("scene.wow_mliq_add_flag", text = 'Add flag', icon = 'MOD_SOFT')
        col.operator("scene.wow_mliq_add_all_flags", text = 'Fill all', icon = 'OUTLINER_OB_LATTICE')
        col.operator("scene.wow_mliq_clear_flag", text = 'Clear flag', icon = 'LATTICE_DATA')
        col.operator("scene.wow_mliq_clear_all_flags", text = 'Clear all', icon = 'MOD_LATTICE')

    
    
class OBJECT_OP_FLAG_0x01(bpy.types.Operator):
    bl_idname = 'scene.wow_mliq_flag_0x01'
    bl_label = 'Flag 0x01'
    bl_description = 'Currently displayed flag layer'
    
    def SwitchFlag(self):
        water = bpy.context.scene.objects.active
        mesh = water.data
        if(water.WowLiquid.Enabled):
            mesh.vertex_colors["flag_0x1"].active = True
            mesh.use_paint_mask = True
        
    def execute(self, context):
        self.SwitchFlag()
        return {'FINISHED'}
    
    
class OBJECT_OP_FLAG_0x02(bpy.types.Operator):
    bl_idname = 'scene.wow_mliq_flag_0x02'
    bl_label = 'Flag 0x02'
    bl_description = 'Currently displayed flag layer'
    
    def SwitchFlag(self):
        water = bpy.context.scene.objects.active
        mesh = water.data
        if(water.WowLiquid.Enabled):
            mesh.vertex_colors["flag_0x2"].active = True
            mesh.use_paint_mask = True
        
    def execute(self, context):
        self.SwitchFlag()
        return {'FINISHED'}

class OBJECT_OP_FLAG_0x04(bpy.types.Operator):
    bl_idname = 'scene.wow_mliq_flag_0x04'
    bl_label = 'Flag 0x04'
    bl_description = 'Currently displayed flag layer'
    
    def SwitchFlag(self):
        water = bpy.context.scene.objects.active
        mesh = water.data
        if(water.WowLiquid.Enabled):
            mesh.vertex_colors["flag_0x4"].active = True
            mesh.use_paint_mask = True
        
    def execute(self, context):
        self.SwitchFlag()
        return {'FINISHED'}
    
class OBJECT_OP_FLAG_0x08(bpy.types.Operator):
    bl_idname = 'scene.wow_mliq_flag_0x08'
    bl_label = 'Invisible'
    bl_description = 'Currently displayed flag layer'
    
    def SwitchFlag(self):
        water = bpy.context.scene.objects.active
        mesh = water.data
        if(water.WowLiquid.Enabled):
            mesh.vertex_colors["flag_0x8"].active = True
            mesh.use_paint_mask = True
        
    def execute(self, context):
        self.SwitchFlag()
        return {'FINISHED'}
    
class OBJECT_OP_FLAG_0x10(bpy.types.Operator):
    bl_idname = 'scene.wow_mliq_flag_0x10'
    bl_label = 'Flag 0x10'
    bl_description = 'Currently displayed flag layer'
    
    def SwitchFlag(self):
        water = bpy.context.scene.objects.active
        mesh = water.data
        if(water.WowLiquid.Enabled):
            mesh.vertex_colors["flag_0x10"].active = True
            mesh.use_paint_mask = True
        
    def execute(self, context):
        self.SwitchFlag()
        return {'FINISHED'}
    
class OBJECT_OP_FLAG_0x20(bpy.types.Operator):
    bl_idname = 'scene.wow_mliq_flag_0x20'
    bl_label = 'Flag 0x20'
    bl_description = 'Currently displayed flag layer'
    
    def SwitchFlag(self):
        water = bpy.context.scene.objects.active
        mesh = water.data
        if(water.WowLiquid.Enabled):
            mesh.vertex_colors["flag_0x20"].active = True
            mesh.use_paint_mask = True
        
    def execute(self, context):
        self.SwitchFlag()
        return {'FINISHED'}
    
class OBJECT_OP_FLAG_0x40(bpy.types.Operator):
    bl_idname = 'scene.wow_mliq_flag_0x40'
    bl_label = 'Flag 0x40'
    bl_description = 'Currently displayed flag layer'
    
    def SwitchFlag(self):
        water = bpy.context.scene.objects.active
        mesh = water.data
        if(water.WowLiquid.Enabled):
            mesh.vertex_colors["flag_0x40"].active = True
            mesh.use_paint_mask = True
        
    def execute(self, context):
        self.SwitchFlag()
        return {'FINISHED'}
    
class OBJECT_OP_FLAG_0x80(bpy.types.Operator):
    bl_idname = 'scene.wow_mliq_flag_0x80'
    bl_label = 'Flag 0x80'
    bl_description = 'Currently displayed flag layer'
    
    def SwitchFlag(self):
        water = bpy.context.scene.objects.active
        mesh = water.data
        if(water.WowLiquid.Enabled):
            mesh.vertex_colors["flag_0x80"].active = True
            mesh.use_paint_mask = True
        
    def execute(self, context):
        self.SwitchFlag()
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



    
    
class OBJECT_OP_Add_Water(bpy.types.Operator):
    bl_idname = 'scene.wow_add_water'
    bl_label = 'Add water'
    bl_description = 'Adds a WoW water plane'
    bl_options = {'REGISTER', 'UNDO'}
    
    xPlanes = bpy.props.IntProperty(name="X subdivisions:", description="Amount of WoW liquid planes in a row. One plane is 4.1666625 in its radius.", default=10, min=1)
    yPlanes = bpy.props.IntProperty(name="Y subdivisions:", description="Amount of WoW liquid planes in a column. One plane is 4.1666625 in its radius.", default=10, min=1)
    
    def AddWater(self, xPlanes, yPlanes):
        bpy.ops.mesh.primitive_grid_add(x_subdivisions = xPlanes + 1, y_subdivisions = yPlanes + 1, radius=4.1666625 / 2)
        water = bpy.context.scene.objects.active
        bpy.ops.transform.resize( value=(xPlanes, yPlanes, 1.0) )
        
        water.name = water.name + "_Liquid"
        
        mesh = water.data
        
        mesh.vertex_colors.new("flag_0x1")
        mesh.vertex_colors.new("flag_0x2")
        mesh.vertex_colors.new("flag_0x4")
        mesh.vertex_colors.new("flag_0x8")
        mesh.vertex_colors.new("flag_0x10")
        mesh.vertex_colors.new("flag_0x20")
        mesh.vertex_colors.new("flag_0x40")
        mesh.vertex_colors.new("flag_0x80")                                 
        
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
    bl_description = 'Fills Texture 1 field of WoW materials with paths from applied image. Is able to account or not account relative texture path.'
    bl_options = {'REGISTER', 'UNDO'}
               
    
    def FillTextures(self):
        for ob in bpy.context.selected_objects:
            mesh = ob.data
            for i in range(len(mesh.materials)):
                if( (mesh.materials[i].active_texture is not None) and not mesh.materials[i].WowMaterial.Texture1 and \
                    (mesh.materials[i].active_texture.type == 'IMAGE') and (mesh.materials[i].active_texture.image is not None) ):
                        if(bpy.context.scene.WoWRoot.UseTextureRelPath):
                            mesh.materials[i].WowMaterial.Texture1 = os.path.splitext( os.path.relpath( mesh.materials[i].active_texture.image.filepath, bpy.context.scene.WoWRoot.TextureRelPath ))[0] + ".blp"
                            LogDebug(1, False, os.path.splitext( os.path.relpath( mesh.materials[i].active_texture.image.filepath, bpy.context.scene.WoWRoot.TextureRelPath ))[0] + ".blp")
                        else:
                            mesh.materials[i].WowMaterial.Texture1 = os.path.splitext( mesh.materials[i].active_texture.image.filepath )[0] + ".blp"
                            LogDebug(1, False, os.path.splitext( os.path.relpath( mesh.materials[i].active_texture.image.filepath, bpy.context.scene.WoWRoot.TextureRelPath ))[0] + ".blp")              

    def execute(self, context):
        
        self.FillTextures()
        return {'FINISHED'}               

class OBJECT_OP_Quick_Collision(bpy.types.Operator):
    bl_idname = 'scene.wow_quick_collision'
    bl_label = 'Generate basic collision for selected objects'
    bl_description = 'Generates WoW collision equal to geometry of the selected objects'
    bl_options = {'REGISTER', 'UNDO'}
        
    NodeSize = bpy.props.IntProperty(name="Node max size", description="Max count of faces for a node in bsp tree", default=150, min=1, soft_max=500)
    CleanUp = bpy.props.BoolProperty(name="Clean up", description="Remove unreferenced vertex groups", default = False)
    
    def QuickCollision(self, NodeSize, CleanUp):
        for ob in bpy.context.selected_objects:
            ob.WowVertexInfo.Enabled = True
            bpy.context.scene.objects.active = ob
            
            if CleanUp:
                for vertex_group in ob.vertex_groups:
                    if (vertex_group.name != ob.WowVertexInfo.VertexGroup) and (vertex_group.name != ob.WowVertexInfo.BatchTypeA) and (vertex_group.name != ob.WowVertexInfo.BatchTypeB) and \
                    (vertex_group.name != ob.WowVertexInfo.Lightmap) and (vertex_group.name != ob.WowVertexInfo.Blendmap) and (vertex_group.name != ob.WowVertexInfo.SecondUV):
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
    
    
    def ToPortal(self):
        for ob in bpy.context.selected_objects:
            ob.WowPortalPlane.Enabled = True
            ob.WowWMOGroup.Enabled = False

    def execute(self, context):
        
        self.ToPortal()
        return {'FINISHED'}
        
class OBJECT_OP_To_Group(bpy.types.Operator):
    bl_idname = 'scene.wow_selected_objects_to_group'
    bl_label = 'Selected objects to WMO group'
    bl_description = 'Transfer all selected objects to WoW WMO groups'
    bl_options = {'REGISTER', 'UNDO'}
        
    GroupName = bpy.props.StringProperty()
    GroupDesc = bpy.props.StringProperty()
    PlaceType = bpy.props.EnumProperty(name = "Place Type", description = "Set WMO group place type", items = [('8', "Outdoor", ""), ('8192', "Indoor", "")], default = '8')
    GroupID = bpy.props.IntProperty(name="DBC Group ID", description="WMO Group ID in DBC file")
    VertShad = bpy.props.BoolProperty(name="Vertex shading", description="Save gropu vertex shading", default = False)
    SkyBox = bpy.props.BoolProperty(name="Use Skybox", description="Use skybox in group", default = False)        
    
    def ToGroup(self, PlaceType, GroupName, GroupDesc, GroupID, VertShad, SkyBox):
        for ob in bpy.context.selected_objects:
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

    shaderEnum = [('0', "Diffuse", ""), ('1', "Specular", ""), ('2', "Metal", ""), \
                  ('3', "Env", ""), ('4', "Opaque", ""), ('5', "EnvMetal", ""), \
                  ('6', "TwoLayerDiffuse", ""), ('7', "TwoLayerEnvMetal", ""), ('8', "TwoLayerTerrain", ""), \
                  ('9', "DiffuseEmissive", ""), ('10', "Tangent", ""), ('11', "MaskedEnvMetal", ""), ('12', "EnvMetalEmissive", ""), \
                  ('13', "TwoLayerDiffuseOpaque", ""), ('14', "TwoLayerDiffuseEmissive", "")]#, ('16', "Diffuse", "")]
    terrainEnum = [('0', "Dirt", ""), ('1', "Metallic", ""), ('2', "Stone", ""), \
                   ('3', "Snow", ""), ('4', "Wood", ""), ('5', "Grass", ""), \
                   ('6', "Leaves", ""), ('7', "Sand", ""), ('8', "Soggy", ""), \
                   ('9', "Dusty Grass", ""), ('10', "None", ""), ('11', "Water", "")]
    blendingEnum = [('0', "Blend_Opaque", ""), ('1', "Blend_AlphaKey", ""), \
                    ('2', "Blend_Alpha", ""), ('3', "Blend_Add", ""), ('4', "Blend_Mod", ""), \
                    ('5', "Blend_Mod2x", ""), ('6', "Blend_ModAdd", ""), ('7', "Blend_InvSrcAlphaAdd", ""), \
                    ('8', "Blend_InvSrcAlphaOpaque", ""), ('9', "Blend_SrcAlphaOpaque", ""), ('10', "Blend_NoAlphaAdd", ""), ('11', "Blend_ConstantAlpha", "")]
    
    Shader = bpy.props.EnumProperty(items=shaderEnum, name="Shader", description="WoW shader assigned to this material")
    BlendingMode = bpy.props.EnumProperty(items=blendingEnum, name="Blending", description="WoW material blending mode")    
    TerrainType = bpy.props.EnumProperty(items=terrainEnum, name="Terrain Type", description="Terrain type assigned to that material")
    TwoSided = bpy.props.BoolProperty(name="TwoSided", description="Enable TwoSided")
    Darkened = bpy.props.BoolProperty(name="Darkened", description="Enable Darkened")
    NightGlow = bpy.props.BoolProperty(name="Unshaded", description="Enable NightGlow")    
    
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
    
class OBJECT_OP_Hide_Show_All(bpy.types.Operator):
    bl_idname = 'scene.wow_hide_show_all_objects'
    bl_label = 'Hide/Show all'
    bl_description = 'Hide/Show all WoW WMO objects'

    def execute(self, context):
        state = True
        for ob in bpy.context.scene.objects:
            if ob.WowWMOGroup.Enabled or ob.WowPortalPlane.Enabled or ob.WowFog.Enabled or ob.WowLiquid.Enabled or ob.data.WowLight.Enabled:
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
        
###############################
## Root source
###############################
class WowWMORootPropertyGroup(bpy.types.PropertyGroup):
    IsRoot = bpy.props.BoolProperty(name="", description="Enable wow WMO root source")
    MODS = MODS_chunk()
    MODN = MODN_chunk()
    MODD = MODD_chunk()
    MFOG = MFOG_chunk()

def RegisterWowWMORootProperties():
    bpy.types.Mesh.WowWMORoot = bpy.props.PointerProperty(type=WowWMORootPropertyGroup)

def UnregisterWowWMORootProperties():
    bpy.types.Mesh.WowWMORoot = None    

def register():
    RegisterWowRootProperties()
    RegisterWowMaterialProperties()
    RegisterWowLiquidProperties()
    RegisterWowLightProperties()
    RegisterWowVertexInfoProperties()
    RegisterWowWMOGroupProperties()
    RegisterWowPortalPlaneProperties()
    RegisterWowWMORootProperties()
    RegisterWoWVisibilityProperties()
    RegisterWowFogProperties()
    # RegisterWMOToolsPanelObjectMode()
    # registered in __init__
    #bpy.utils.register_class(WowMaterialPanel)

def unregister():
    UnregisterWowRootProperties()
    UnregisterWowMaterialProperties()
    UnregisterWowLiquidProperties()
    UnregisterWowLightProperties()
    UnregisterWowVertexInfoProperties()
    UnregisterWowWMOGroupProperties()
    UnregisterWowPortalPlaneProperties()
    UnregisterWowWMORootProperties()
    UnregisterWoWVisibilityProperties()
    UnregisterWowFogProperties()
    # UnregisterWMOToolsPanelObjectMode()
    # unregistered in __init__
    #bpy.utils.unregister_class(WowMaterialPanel)

 


