bl_info = {
    "name" : "Exr 2 Nuke",
    "author" : "Lucas ROUGE, Adrien BLANCHARD", 
    "description" : "A simple way to export Exrs to Nuke.",
    "blender" : (3, 3, 1),
    "version" : (1, 0, 0),
    "location" : "View layer Properties",
    "warning" : "",
    "doc_url": "", 
    "tracker_url": "", 
    "category" : "Render" 
}

import bpy
import sys,os
import json
from pathlib import Path
from importlib import reload

addon_directory=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
module_directory=addon_directory+'\Modules'
libraries_directory=addon_directory+'\Libraries'

#Permet de rajouter le dossier spécifié dans la liste des dossier dans lequelle blender va chercher les modules avec import
sys.path.append(module_directory)


    

#Addon import
from .modules import One_output, Two_outputs, Three_outputs, Fast_selection

#script_directory = bpy.utils.script_path_user()


#import One_output, Two_outputs, Three_outputs, Fast_selection
reload(One_output)
reload(Two_outputs)
reload(Three_outputs)
#reload(Fast_selection)




#OPERATORS

#Fast_selection
class EXR2NUKE_OP_APPLY_FASTSELECT(bpy.types.Operator):
    bl_idname = "op.apply_fast_select"
    bl_label = "op.apply_fast_select"
    bl_description = "Use the fast selection button to select favorite passes"
    bl_options = {"REGISTER", "UNDO"}
    

    def execute(self, context):
        
        Fast_selection.apply()

        return {"FINISHED"}

class EXR2NUKE_OP_SAVE_FASTSELECT(bpy.types.Operator):
    bl_idname = "op.save_fast_select"
    bl_label = "op.save_fast_select"
    bl_description = "Save the actual selected passes as Fast Selection"
    bl_options = {"REGISTER", "UNDO"}


    def execute(self, context):
        
        Fast_selection.save()

        return {"FINISHED"}

#Generate
class EXR2NUKE_OP_ONE_OUTPUT(bpy.types.Operator):
    bl_label = '1. Light + Data + Cryptommates'
    bl_idname = 'op.generate_1'
    bl_description = ("Generate only one multilayer Exr for output")
    
    def execute(self, context):
        
        One_output.create_setup()
        
        return {'FINISHED'}
    
class EXR2NUKE_OP_TWO_OUTPUT(bpy.types.Operator):
    bl_label = '2. Light + Data / Cryptommates'
    bl_idname = 'op.generate_2'
    bl_description = ("Generate two multilayer Exrs one for the beauty(light and data passes included) and one for Cryptommates")
    
    def execute(self, context):
        
        Two_outputs.create_setup()
        
        return {'FINISHED'}

class EXR2NUKE_OP_THREE_OUTPUT(bpy.types.Operator):
    bl_label = '3. Light / Data / Cryptommates'
    bl_idname = 'op.generate_3'
    bl_description = ("Generate three Exrs one for Light, one for Data and one for Cryptommates")
    
    def execute(self, context):
        
        Three_outputs.create_setup()
        
        return {'FINISHED'}

#PANELS

class EXR2NUKE_MAINPANEL(bpy.types.Panel):
    bl_label = "Exr 2 nuke Panel"
    bl_idname = "EXR2NUKE_PT_MAINPANEL"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'view_layer'
    bl_order = 0
     
    def draw(self, context):
        layout = self.layout

class EXR2NUKE_FASTSELECT_SUBPANEL(bpy.types.Panel):
    bl_label = 'Options'
    bl_idname = 'EXR2NUKE_PT_FASTSELECT'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'view_layer'
    bl_parent_id = 'EXR2NUKE_PT_MAINPANEL'
    bl_order = 0

    
    def draw(self, context):
        layout = self.layout 
        row = layout.row(heading='', align=False)
        row.alignment = 'Center'.upper()
        op = row.operator('op.apply_fast_select', text='Apply Fast Selection', icon='PLUS', emboss=True) 
        op = row.operator('op.save_fast_select', text='Save Fast Selection Profile', icon='PASTEDOWN', emboss=True) 

        if bpy.context.scene.render.engine == 'CYCLES':

                    
                    row = layout.row(heading='', align=False)
                    row.alignment = 'Center'.upper()
                    row.label(text='You are using Cycles passes can be denoised')
                
                    row = layout.row(heading='', align=False)       
                    row.alert = False
                    row.active = True
                    row.alignment = 'Center'.upper()
                    row.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                    if bpy.data.scenes['Scene'].view_layers['ViewLayer'].cycles.denoising_store_passes:
                        row.prop(bpy.data.scenes['Scene'].view_layers['ViewLayer'].cycles, 'denoising_store_passes', text='Passes are denoised.', icon_value=0, emboss=True)
                    else:
                        row.prop(bpy.data.scenes['Scene'].view_layers['ViewLayer'].cycles, 'denoising_store_passes', text='Passes are not denoised.', icon_value=0, emboss=True) 
                    
                    row = layout.row(heading='', align=False)
                    row.alignment = 'Center'.upper()
                    row.label(text="Don't forget to regenerate the node tree after changing any option", icon_value=2)
        else :
            row = layout.row(heading='', align=False)
            row.alignment = 'Center'.upper()
            row.label(text="You are using Eevee passes can't be denoised")
            

             
        


class EXR2NUKE_GENERATE_SUBPANEL(bpy.types.Panel):
    bl_label = 'Generate and Output'
    bl_idname = 'EXR2NUKE_PT_GENERATE'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'view_layer'
    bl_parent_id = 'EXR2NUKE_PT_MAINPANEL'
    bl_order = 2
    
    def draw(self, context):
            layout = self.layout
            

            #Check box pour denoise ou non les passes

            
            #CREATE BUTTONS
            row = layout.row()
            row.alignment = 'Center'.upper()
            row.label(text="How many outputs do you want to generate?")
            
            row = layout.row()
            row.operator('op.generate_1', icon='NODE')
            row.alignment = 'Center'.upper()
                        
            row = layout.row()
            row.operator('op.generate_2', icon='NODE')
            row.alignment = 'Center'.upper()

            if bpy.context.scene.render.engine == 'CYCLES':          
                row = layout.row()
                row.operator('op.generate_3', icon='NODE')
                row.alignment = 'Center'.upper()

            liste_outputs = ['Light_exr','Data_exr','Light_Data_exr','Cryptomatte_exr' ,'File_Output_exr']
            try:
                for i in liste_outputs:
                    if i in bpy.data.scenes['Scene'].node_tree.nodes:
                        col = layout.column(heading='', align=False)
                        col.alignment = 'Expand'.upper()
                        col.label(text=i +':', icon_value=0)
                        col.prop(bpy.data.scenes['Scene'].node_tree.nodes[i], 'base_path', text='', icon_value=0, emboss=True)
            except:
                row = layout.row()
                row.alignment = 'Center'.upper()
                row.label(text='You have to select a method.', icon_value=2)
         

            
        


#REGISTER
def register():
    #OPERATORS
    bpy.utils.register_class(EXR2NUKE_OP_APPLY_FASTSELECT)
    bpy.utils.register_class(EXR2NUKE_OP_SAVE_FASTSELECT)
    bpy.utils.register_class(EXR2NUKE_OP_ONE_OUTPUT)
    bpy.utils.register_class(EXR2NUKE_OP_TWO_OUTPUT)
    bpy.utils.register_class(EXR2NUKE_OP_THREE_OUTPUT)
    #PANELS
    bpy.utils.register_class(EXR2NUKE_MAINPANEL)
    bpy.utils.register_class(EXR2NUKE_FASTSELECT_SUBPANEL)
    bpy.utils.register_class(EXR2NUKE_GENERATE_SUBPANEL)

def unregister():
    #OPERATORS
    bpy.utils.unregister_class(EXR2NUKE_OP_APPLY_FASTSELECT)
    bpy.utils.unregister_class(EXR2NUKE_OP_SAVE_FASTSELECT)
    bpy.utils.unregister_class(EXR2NUKE_OP_ONE_OUTPUT)
    bpy.utils.unregister_class(EXR2NUKE_OP_TWO_OUTPUT)
    bpy.utils.unregister_class(EXR2NUKE_OP_THREE_OUTPUT)
    #PANELS
    bpy.utils.unregister_class(EXR2NUKE_MAINPANEL)
    bpy.utils.unregister_class(EXR2NUKE_FASTSELECT_SUBPANEL)
    bpy.utils.unregister_class(EXR2NUKE_GENERATE_SUBPANEL)
        
if __name__ == "__main__":
    register()
