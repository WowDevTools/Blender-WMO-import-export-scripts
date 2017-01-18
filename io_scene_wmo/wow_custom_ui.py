
import bpy
import bpy.utils
import bpy.types
from . import wmo_format
from .wmo_format import *
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
        self.layout.prop(context.scene.WoWRoot, "Enabled")

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
        layout.enabled = context.scene.WoWRoot.Enabled

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
    bl_label = "WoW material"
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
        self.layout.prop(context.material.WowMaterial, "BatchType")
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
    batchEnum = [('0', "A (Special)", "Both vertex shader and global lighting are used. (Mixing is done based on MOCV alpha or automatically depending on a flag)"), \
                 ('1', "B (Indoor)", "Global lighting is ignored. Vertex shader modulates the texture and works as lighting."), \
                 ('2', "C (Outdoor)", "Only global lighting is used. Vertex shader is just a color modulating the texture.")]
    
    Enabled = bpy.props.BoolProperty(name="", description="Enable WoW material properties")
    Shader = bpy.props.EnumProperty(items=shaderEnum, name="Shader", description="WoW shader assigned to this material")
    BlendingMode = bpy.props.EnumProperty(items=blendingEnum, name="Blending Mode", description="WoW material blending mode")
    BatchType = bpy.props.EnumProperty(items=batchEnum, name="Batch Type", description="WoW batch type. See tutorial to learn what that is for.", default='2')
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
    bl_label = "Wow light"
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
    AttenuationStart = bpy.props.FloatProperty(name="Attenuation start", description="Distance at which light intensity start to decrease")
    AttenuationEnd = bpy.props.FloatProperty(name="Attenuation end", description="Distance at which light intensity reach 0")

def RegisterWowLightProperties():
    bpy.types.Lamp.WowLight = bpy.props.PointerProperty(type=WowLightPropertyGroup)

def UnregisterWowLightProperties():
    bpy.types.Lamp.WowLight = None


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
    bl_context = "data"
    bl_label = "Wow liquid"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        self.layout.prop(context.object.WowLiquid, "LiquidType")
        self.layout.prop_search(context.object.WowLiquid, "VertexGroup", context.object, "vertex_groups", text="Liquid vertex group")
        layout.enabled = context.object.WowLiquid.Enabled

    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.object.data is not None and isinstance(context.object.data,bpy.types.Mesh))

class WowLiquidPropertyGroup(bpy.types.PropertyGroup):
    liquidTypeEnum = [('81', "Lake Wintergrasp - Water", ""), ('41', "Coilfang Raid - Water", ""), ('1', "Water", ""), \
        ('2', "Ocean", ""), ('3', "Magma", ""), ('4', "Slime", ""), \
        ('21', "Naxxramas - Slime", ""), ('61', "Hyjal Past - Water", ""), ('100', "Basic Procedural Water", ""), \
        ('13', "WMO Water", ""), ('5', "Slow Water", ""), ('9', "Fast Water", ""), \
        ('6', "Slow Ocean", ""), ('10', "Fast Ocean", ""), ('7', "Slow Magma", ""), \
        ('11', "Fast Magma", ""), ('8', "Slow Slime", ""), ('12', "Fast Slime", ""), \
        ('14', "WMO Ocean", ""), ('15', "Green Lava", "")]
    Enabled = bpy.props.BoolProperty(name="", description="Enable wow liquid properties", default=False)
    LiquidType = bpy.props.EnumProperty(items=liquidTypeEnum, name="Liquid Type", description="Type of the liquid present in this WMO group")
    VertexGroup = bpy.props.StringProperty()

def RegisterWowLiquidProperties():
    bpy.types.Object.WowLiquid = bpy.props.PointerProperty(type=WowLiquidPropertyGroup)

def UnregisterWowLiquidProperties():
    bpy.types.Object.WowLiquid = None

###############################
## Collision
###############################

class WowCollisionPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_label = "Wow collision"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        self.layout.prop(context.object.WowCollision, "Enabled")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        self.layout.prop_search(context.object.WowCollision, "VertexGroup", context.object, "vertex_groups", text="Collision vertex group")
        self.layout.prop(context.object.WowCollision, "NodeSize", slider=True)
        layout.enabled = context.object.WowCollision.Enabled

    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.object.data is not None and isinstance(context.object.data,bpy.types.Mesh))

class WowCollisionPropertyGroup(bpy.types.PropertyGroup):
    Enabled = bpy.props.BoolProperty(name="", description="Enable wow collision properties")
    VertexGroup = bpy.props.StringProperty()
    NodeSize = bpy.props.IntProperty(name="Node max size", description="Max count of faces for a node in bsp tree", default=150, min=1, soft_max=500)

def RegisterWowCollisionProperties():
    bpy.types.Object.WowCollision = bpy.props.PointerProperty(type=WowCollisionPropertyGroup)

def UnregisterWowCollisionProperties():
    bpy.types.Object.WowCollision = None


###############################
## WMO Group
###############################
class WowWMOGroupPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_label = "Wow WMO group"
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
        self.layout.prop(context.object.WowWMOGroup, "SkyBox")
        self.layout.prop(context.object.WowWMOGroup, "Fog1")
        self.layout.prop(context.object.WowWMOGroup, "Fog2")
        self.layout.prop(context.object.WowWMOGroup, "Fog3")
        self.layout.prop(context.object.WowWMOGroup, "Fog4")
        layout.enabled = context.object.WowWMOGroup.Enabled

    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.object.data is not None and isinstance(context.object.data,bpy.types.Mesh))

class WowWMOMODRStore(bpy.types.PropertyGroup):
    value = bpy.props.IntProperty(name="Doodads Ref")
    
def GetFogObjects(self, context):
    fogs = []
    
    fogs.append(('0', "None", "")) # setting a default entry as a first element of our enum
    
    for object in bpy.context.scene.objects:
        if object.type != 'LAMP' and object.data.WowFog.Enabled:
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
    VertShad = bpy.props.BoolProperty(name="Vertex shading", description="Save gropu vertex shading", default = False)
    SkyBox = bpy.props.BoolProperty(name="Use Skybox", description="Use skybox in group", default = False)
    Fog1 = bpy.props.EnumProperty(items=GetFogObjects, name="Fog 1", description="Fog of an object")
    Fog2 = bpy.props.EnumProperty(items=GetFogObjects, name="Fog 2", description="Fog of an object")
    Fog3 = bpy.props.EnumProperty(items=GetFogObjects, name="Fog 3", description="Fog of an object")
    Fog4 = bpy.props.EnumProperty(items=GetFogObjects, name="Fog 4", description="Fog of an object")
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
    bl_context = "data"
    bl_label = "Wow Portal Plane"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        self.layout.prop(context.object.data.WowPortalPlane, "Enabled")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        self.layout.prop(context.object.data.WowPortalPlane, "First")
        self.layout.prop(context.object.data.WowPortalPlane, "Second")
        #self.layout.prop(context.object.data.WowPortalPlane, "normalX")
        #self.layout.prop(context.object.data.WowPortalPlane, "normalY")
        #self.layout.prop(context.object.data.WowPortalPlane, "normalZ")
        layout.enabled = context.object.data.WowPortalPlane.Enabled
        self.layout.prop(context.object.data.WowPortalPlane, "Invert")

    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.object.data is not None and isinstance(context.object.data,bpy.types.Mesh))

class WowPortalPlanePropertyGroup(bpy.types.PropertyGroup):
    Enabled = bpy.props.BoolProperty(name="", description="Enable wow WMO group properties")
    First = bpy.props.IntProperty(name="First GroupID", description="Portal Reference")
    Second = bpy.props.IntProperty(name="Second GroupID", description="Portal Reference")
    normalX = bpy.props.FloatProperty(name="Normal X", description="Portal Normal")
    normalY = bpy.props.FloatProperty(name="Normal Y", description="Portal Normal")
    normalZ = bpy.props.FloatProperty(name="Normal Z", description="Portal Normal")
    Invert = bpy.props.BoolProperty(name="Invert direction", description="Invert portal direction", default = False)
    PortalID = bpy.props.IntProperty(name="Portal's ID", description="Portal ID")

def RegisterWowPortalPlaneProperties():
    bpy.types.Mesh.WowPortalPlane = bpy.props.PointerProperty(type=WowPortalPlanePropertyGroup)

def UnregisterWowPortalPlaneProperties():
    bpy.types.Mesh.WowPortalPlane = None
    
    
###############################
## Fog
###############################
class WowFogPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_label = "Wow Fog"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        self.layout.prop(context.object.data.WowFog, "Enabled")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        layout.enabled = context.object.data.WowFog.Enabled
        self.layout.prop(context.object.data.WowFog, "IgnoreRadius")
        self.layout.prop(context.object.data.WowFog, "Unknown")
        self.layout.prop(context.object.data.WowFog, "InnerRadius")
        self.layout.prop(context.object.data.WowFog, "EndDist")
        self.layout.prop(context.object.data.WowFog, "StartFactor")
        self.layout.prop(context.object.data.WowFog, "Color1")
        self.layout.prop(context.object.data.WowFog, "EndDist2")
        self.layout.prop(context.object.data.WowFog, "StartFactor2")
        self.layout.prop(context.object.data.WowFog, "Color2")

    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.object.data is not None and isinstance(context.object.data,bpy.types.Mesh))

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
    bpy.types.Mesh.WowFog = bpy.props.PointerProperty(type=WowFogPropertyGroup)

def UnregisterWowFogProperties():
    bpy.types.Mesh.WowFog = None


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
    
class WoWToolsPanelObjectMode(bpy.types.Panel):
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
        col.operator("scene.wow_hide_show_all_objects", text = 'All', icon = 'VISIBLE_IPO_ON') 

    def RegisterWMOToolsPanelObjectMode():
        bpy.utils.register_module(WMOToolsPanelObjectMode)
    def UnregisterWMOToolsPanelObjectMode():
        bpy.utils.register_module(WMOToolsPanelObjectMode)
        

class OBJECT_OP_Add_Water(bpy.types.Operator):
    bl_idname = 'scene.wow_add_water'
    bl_label = 'Add water'
    bl_description = 'Adds a WoW water plane'
    bl_options = {'REGISTER', 'UNDO'}
    
    xPlanes = bpy.props.IntProperty(name="X subdivisions:", description="Amount of WoW liquid planes in a row. One plane is 4.1666625 in its radius.", default=10, min=1)
    yPlanes = bpy.props.IntProperty(name="Y subdivisions:", description="Amount of WoW liquid planes in a column. One plane is 4.1666625 in its radius.", default=10, min=1)
    
    def AddWater(self, xPlanes, yPlanes):
        bpy.ops.mesh.primitive_grid_add(x_subdivisions =xPlanes + 1, y_subdivisions = Planes + 1, radius=4.1666625 / 2)
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
        
        mesh.WowFog.Enabled = True
        return {'FINISHED'}
    
        
class OBJECT_OP_Invert_Portals(bpy.types.Operator):
    bl_idname = 'scene.wow_invert_portals'
    bl_label = 'Inevert portals'
    bl_description = 'Invert direction of all selected WoW portals'
    
    
    def InvertPortal(self):
        for ob in bpy.context.selected_objects:
            if(ob.data.WowPortalPlane.Enabled == True):
                if(ob.data.WowPortalPlane.Invert == True):
                    ob.data.WowPortalPlane.Invert = not ob.data.WowPortalPlane.Invert
                    
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
                if((mesh.materials[i].WowMaterial.Texture1 != "") & (mesh.materials[i].active_texture is not None) ):
                    if((mesh.materials[i].active_texture.type == 'IMAGE')):
                        if(bpy.context.scene.WoWRoot.UseTextureRelPath):
                            mesh.materials[i].WowMaterial.Texture1 = os.path.splitext( os.path.relpath( bpy.types.ImageTexture(mesh.materials[i].active_texture).image.filepath , bpy.context.scene.WoWRoot.TextureRelPath ))[0] + ".blp"
                        else:
                            mesh.materials[i].WowMaterial.Texture1 = os.path.splitext( bpy.types.ImageTexture(mesh.materials[i].active_texture).image.filepath )[0] + ".blp"                

    def execute(self, context):
        
        self.FillTextures()
        return {'FINISHED'}               

class OBJECT_OP_Quick_Collision(bpy.types.Operator):
    bl_idname = 'scene.wow_quick_collision'
    bl_label = 'Generate basic collision for selected objects'
    bl_description = 'Generates WoW collision equal to geometry of the selected objects'
    bl_options = {'REGISTER', 'UNDO'}
        
    NodeSize = bpy.props.IntProperty(name="Node max size", description="Max count of faces for a node in bsp tree", default=150, min=1, soft_max=500)        
    
    def QuickCollision(self, NodeSize):
        for ob in bpy.context.selected_objects:
            ob.WowCollision.Enabled = True
            bpy.context.scene.objects.active = ob
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            # bpy.ops.object.vertex_group_remove(all = True)
            bpy.ops.object.vertex_group_assign_new()
            ob.WowCollision.VertexGroup = ob.vertex_groups.active.name
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')
            ob.WowCollision.NodeSize = NodeSize

    def execute(self, context):
        
        self.QuickCollision(self.NodeSize)
        return {'FINISHED'}        
        
class OBJECT_OP_Texface_to_material(bpy.types.Operator):
    bl_idname = 'scene.wow_texface_to_material'
    bl_label = 'Texface to material'
    bl_description = 'Generate materials out of texfaces in selected objects'

    def execute(self, context):
        bpy.ops.view3d.material_remove()
        bpy.ops.view3d.texface_to_material()
        return {'FINISHED'}   
        
class OBJECT_OP_To_WMOPortal(bpy.types.Operator):
    bl_idname = 'scene.wow_selected_objects_to_portals'
    bl_label = 'Selected objects to WMO portals'
    bl_description = 'Transfer all selected objects to WoW WMO portals'
    
    
    def ToPortal(self):
        for ob in bpy.context.selected_objects:
            ob.data.WowPortalPlane.Enabled = True
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
            if((ob.WowWMOGroup.Enabled == True) or (ob.data.WowPortalPlane.Enabled == True)) or (ob.data.WowFog.Enabled == True) or (ob.WowLiquid.Enabled == True):
                if(bpy.context.scene.WoWVisibility.All == True):
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
            if(ob.data.WowPortalPlane.Enabled == True):
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
    bl_description = 'Hide/Show all WoW fog objects'

    def execute(self, context):
        state = True
        for ob in bpy.context.scene.objects:
            if(ob.data.WowFog.Enabled == True):
                if(bpy.context.scene.WoWVisibility.Fog == True):
                    ob.hide = True
                    state = False
                else:
                    ob.hide = False
                    state = True
        bpy.context.scene.WoWVisibility.Fog = state
        return {'FINISHED'}       
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
    RegisterWowCollisionProperties()
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
    UnregisterWowCollisionProperties()
    UnregisterWowWMOGroupProperties()
    UnregisterWowPortalPlaneProperties()
    UnregisterWowWMORootProperties()
    UnregisterWoWVisibilityProperties()
    UnregisterWowFogProperties()
    # UnregisterWMOToolsPanelObjectMode()
    # unregistered in __init__
    #bpy.utils.unregister_class(WowMaterialPanel)




