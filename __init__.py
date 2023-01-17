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



if "bpy" in locals():
    import imp
    imp.reload(create_1_node)
    print("Reloaded multifiles")
else:
    from . import create_1_node
    print("Imported multifiles")

import bpy   
    
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

        
        
        

    
#BUTTON 1
class ONE_OUTPUT(bpy.types.Operator):
    bl_label = 'Generate 1 output node system'
    bl_idname = 'node.1_operator'
    
    def execute(self, context):
        

        create_1_node.create_setup()
       # my_group = create_1_node_system(self, context, custom_node_name)
        
        return {'FINISHED'}



#REGISTER
def register():
    bpy.utils.register_class(B2N_MAINPANEL)
    bpy.utils.register_class(ONE_OUTPUT)



def unregister():
    bpy.utils.unregister_class(B2N_MAINPANEL)
    bpy.utils.unregister_class(ONE_OUTPUT)


if __name__ == "__main__":
    register()
