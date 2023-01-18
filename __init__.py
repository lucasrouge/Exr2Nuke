bl_info = {
    "name" : "Blender to Nuke",
    "author" : "LA",
    "version" : (1, 0),
    "blender" : (3, 3, 0),
    "location": "Node editor",
    "warning": "",
    "wiki_url": "",
    "category": "Compositor Nodes",
}



import sys
from pathlib import Path

sys.path.append("D:\Git\Exr2Nuke")


#Addon import
#if "bpy" in locals():
#    import imp
#    imp.reload(create_1_node)
#    print("Reloaded multifiles")
#else:
#    from . import create_1_node
#    print("Imported multifiles")

import bpy
import One_output, Two_outputs, Three_outputs





#CREATE PANEL
class B2N_MAINPANEL(bpy.types.Panel):
    bl_label = "B2N Panel"
    bl_idname = "B2N_MAINPANEL"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "B2N"

    def draw(self, context):
        layout = self.layout

        #CREATE BUTTONS
        row = layout.row()
        row.operator('node.1_operator', icon='NODE')
        row = layout.row()
        row.operator('node.2_operator', icon='NODE')
        row = layout.row()
        row.operator('node.3_operator', icon='NODE')
            
#BUTTON 1
class ONE_OUTPUT(bpy.types.Operator):
    bl_label = 'Generate 1 output node system'
    bl_idname = 'node.1_operator'
    
    def execute(self, context):
        
        One_output.create_setup()
        
        return {'FINISHED'}
    
#BUTTON 2
class TWO_OUTPUTS(bpy.types.Operator):
    bl_label = 'Generate 2 outputs node system'
    bl_idname = 'node.2_operator'
    
    def execute(self, context):
        
        Two_outputs.create_setup()
        
        return {'FINISHED'}

#BUTTON 3
class THREE_OUTPUTS(bpy.types.Operator):
    bl_label = 'Generate 3 outputs node system'
    bl_idname = 'node.3_operator'
    
    def execute(self, context):
        
        Three_outputs.create_setup()
        
        return {'FINISHED'}

#REGISTER
def register():
    bpy.utils.register_class(B2N_MAINPANEL)
    bpy.utils.register_class(ONE_OUTPUT)
    bpy.utils.register_class(TWO_OUTPUTS)
    bpy.utils.register_class(THREE_OUTPUTS)



def unregister():
    bpy.utils.unregister_class(B2N_MAINPANEL)
    bpy.utils.unregister_class(ONE_OUTPUT)
    bpy.utils.unregister_class(TWO_OUTPUTS)
    bpy.utils.unregister_class(THREE_OUTPUTS)

if __name__ == "__main__":
    register()
