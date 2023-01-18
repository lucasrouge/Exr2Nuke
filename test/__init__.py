#----------------------------------------------------------
# File __init__.py
#----------------------------------------------------------

#    Addon info
bl_info = {
    'name': 'Multifile',
    'author': 'Thomas Larsson',
    'location': 'View3D > UI panel > Add meshes',
    'category': '3D View'
    }

# To support reload properly, try to access a package var, 
# if it's there, reload everything
if "bpy" in locals():
    import imp
    imp.reload(mycube)
    imp.reload(mysphere)
    imp.reload(mycylinder)
    print("Reloaded multifiles")
else:
    from . import mycube, mysphere, mycylinder
    print("Imported multifiles")

import bpy
from bpy.props import *

#
#   class AddMeshPanel(bpy.types.Panel):
#
class AddMeshPanel(bpy.types.Panel):
    bl_label = "Add meshes"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        self.layout.operator("multifile.add", 
            text="Add cube").mesh = "cube"
        self.layout.operator("multifile.add", 
            text="Add cylinder").mesh = "cylinder"
        self.layout.operator("multifile.add", 
            text="Add sphere").mesh = "sphere"

#
#   class OBJECT_OT_AddButton(bpy.types.Operator):
#
class OBJECT_OT_AddButton(bpy.types.Operator):
    bl_idname = "multifile.add"
    bl_label = "Add"
    mesh = bpy.props.StringProperty()

    def execute(self, context):
        if self.mesh == "cube":
            mycube.makeMesh(-8)
        elif self.mesh == "cylinder":
            mycylinder.makeMesh(-5)
        elif self.mesh == "sphere":
            mysphere.makeMesh(-2)
        return{'FINISHED'}    

#
#    Registration
#

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()