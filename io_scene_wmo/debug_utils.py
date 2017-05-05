import bpy

###############################
## Debug output system
###############################

def report_message(message, type=True):
    for window in bpy.context.window_manager.windows:
        screen = window.screen
    
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                override = {'window': window, 'screen': screen, 'area': area}
                bpy.ops.render.report_message(override,'INVOKE_DEFAULT', message=message, type=type)
    
class TECH_OP_REPORT(bpy.types.Operator):
    bl_idname = 'render.report_message'
    bl_label = 'Report'
    bl_description = 'Reports passed message as error or warning'
    bl_options = {'REGISTER', 'UNDO'}
    
    message = bpy.props.StringProperty()
    type = bpy.props.BoolProperty(name="Report type", description="Type of message displayed", default = True)

    def execute(self, context):
        if self.type:
            self.report({'INFO'}, self.message)
        else:
            self.report({'INFO'}, self.message)
            
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

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




    

