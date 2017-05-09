import bpy

###############################
## Debug output system
###############################

class SceneSafetyWatcher():
    def __init__(self, func, objs=[]):
        self.objects = objs
        self.func = func
            
    def __del__(self):
        if self.objects:
            for object in self.objects:
                self.func(object)
        else:
            self.func()



class TECH_OP_VALIDATE_SCENE(bpy.types.Operator):
    bl_idname = 'scene.wow_wmo_validate_scene'
    bl_label = 'Validate Scene'
    bl_description = 'Validate WMO scene before export'
    bl_options = {'REGISTER'}

    def execute(self, context):
    
        for object in bpy.context.scene.objects:
            if object.type == 'MESH' and object.WowWMOGroup.Enabled:
                mesh = object.data

                # check if there is a uvmap layer
                if not len(mesh.uv_layers):
                    LogError(2, 
                            "WMO group" + object.name + "does not contains a UV map layer."
                            )

                # check material limit
                if len(mesh.materials) > 255:
                    LogError(2, 
                            "WMO group" + object.name + "contains more than 255 materials."
                            )

                # check polycount limit
                if len(mesh.vertices) > 65535:
                    LogError(2,
                             "Object " 
                             + str(obj.name) 
                             + " contains more vertices (" 
                             + str(len(mesh.vertices)) 
                             + ") than it is supported.  Maximum amount of vertices you can use per one object is 65535."
                             )
      
        return {'FINISHED'}

    
def Log(spacing, header, *message):
    
    string = ""
    
    for item in message:
        string += str(item) + " "
        
    if spacing:
        for i in range(0, spacing):
            print("")
    
    if header:
        print("###############################")
        print("##", string)
        print("###############################")
    
    else:
        print(string)
    
     
def LogDebug(spacing, header, *message):
    
    string = ""
    
    for item in message:
        string += str(item) + " "
    
    if spacing:
        for i in range(0, spacing):
            print("")
    
    if header:
        print("###############################")
        print("##", "DEBUG:", string)
        print("###############################")
    
    else:
        print(string)
    
def LogError(spacing, *message):
    
    string = ""
    
    for item in message:
        for char in str(item):
            string += char + " "
    
    if spacing:
        for i in range(0, spacing):
            print("")
    
    raise Exception(string)




    

