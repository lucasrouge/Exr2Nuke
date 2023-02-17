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
    "category" : "Compositing" 
}

import bpy
import sys,os
import json
from pathlib import Path
from importlib import reload

module_directory=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))+'\Modules'
sys.path.append(module_directory)

libraries_path=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))+'\Libraries'
    

#Addon import
#from .modules import One_output, Two_outputs, Three_outputs

script_directory = bpy.utils.script_path_user()
print(script_directory)


import One_output, Two_outputs, Three_outputs
reload(One_output)
reload(Two_outputs)
reload(Three_outputs)




#OPERATORS

#Fast_selection
class EXR2NUKE_OP_APPLY_FASTSELECT(bpy.types.Operator):
    bl_idname = "exr2nuke.op_aplly_fastselect"
    bl_label = "op_apply_fast_select"
    bl_description = "Use the fast selection button to select favorite passes"
    bl_options = {"REGISTER", "UNDO"}
    

    def execute(self, context):
        context = bpy.context
        view_layer = context.scene.view_layers["ViewLayer"]
        
        #lecture du fichier json qui gère le fast selection          
        Cycles_fast_select_json_path=libraries_path+'\Cycles_fast_select.json'      
        library={}
        with open(Cycles_fast_select_json_path, "r") as f:
            library = json.load(f)
            
        #attribution des valeurs du fichier json
        for i in library:
            if library[i]["parent"] == "view_layer":
                setattr(view_layer, library[i]["attribute"], library[i]["value"])
            elif library[i]["parent"] == "view_layer.cycles":
                setattr(view_layer.cycles, library[i]["attribute"], library[i]["value"])
        return {"FINISHED"}

class EXR2NUKE_OP_SAVE_FASTSELECT(bpy.types.Operator):
    bl_idname = "exr2nuke.op_save_fast_selection"
    bl_label = "op_save_fastselect"
    bl_description = "Save the actual selected passes as Fast Selection"
    bl_options = {"REGISTER", "UNDO"}


    def execute(self, context):
        context = bpy.context
        view_layer = context.scene.view_layers["ViewLayer"]
       
        Cycles_fast_select_json_path=libraries_path+'\Cycles_fast_select.json'     
        library={}
        with open(Cycles_fast_select_json_path, "r") as f:
            library = json.load(f)
        
        print(library)
        #attribution des valeurs du fichier json
        for i in library:
            if library[i]["parent"] == "view_layer":
                new_attr = getattr(view_layer, library[i]["attribute"])
                library[i]["value"] = new_attr
            elif library[i]["parent"] == "view_layer.cycles":
                new_attr = getattr(view_layer.cycles, library[i]["attribute"])
                library[i]["value"] = new_attr
        
        with open(Cycles_fast_select_json_path, "w") as f:
            json.dump(library, f, indent=4)
        return {"FINISHED"}

#Generate
class EXR2NUKE_OP_ONE_OUTPUT(bpy.types.Operator):
    bl_label = 'Generate'
    bl_idname = 'op_generate_1'
    
    def execute(self, context):
        
        One_output.create_setup()
        
        return {'FINISHED'}
    
class EXR2NUKE_OP_TWO_OUTPUT(bpy.types.Operator):
    bl_label = 'Generate'
    bl_idname = 'op_generate_2'
    
    def execute(self, context):
        
        Two_outputs.create_setup()
        
        return {'FINISHED'}

class EXR2NUKE_OP_THREE_OUTPUT(bpy.types.Operator):
    bl_label = 'Generate'
    bl_idname = 'op_generate_3'
    
    def execute(self, context):
        
        Three_outputs.create_setup()
        
        return {'FINISHED'}

#PANELS

class EXR2NUKE_MAINPANEL(bpy.types.Panel):
    bl_label = "Exr to nuke Panel"
    bl_idname = "B2N_PT_MAINPANEL"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'view_layer'
    bl_order = 1
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = "B2N"
    
    

    def draw(self, context):
        layout = self.layout

class EXR2NUKE_FASTSELECT_SUBPANEL(bpy.types.Panel):
    bl_label = 'Fast selection panel'
    bl_idname = 'B2N_PT_FAST'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'view_layer'
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = 'B2N_PT_MAINPANEL'
    bl_ui_units_x=0
    bl_order = 0
    
    def draw(self, context):
        layout = self.layout 
        row_1AFB2 = layout.row(heading='', align=False)
        row_1AFB2.alert = False
        row_1AFB2.enabled = True
        row_1AFB2.active = True
        row_1AFB2.use_property_split = True
        row_1AFB2.use_property_decorate = False
        row_1AFB2.scale_x = 1.4500000476837158
        row_1AFB2.scale_y = 1.3600000143051147
        row_1AFB2.alignment = 'Center'.upper()
        row_1AFB2.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        op = row_1AFB2.operator('b2n.op_fast_selection', text='Apply Fast Selection', icon_value=157, emboss=True, depress=False) 
        op = row_1AFB2.operator('b2n.op_save_fast_selection', text='Save Fast Selection Profile', icon_value=157, emboss=True, depress=False) 

class EXR2NUKE_DENOISE_SUBPANEL(bpy.types.Panel):
    bl_label = 'Denoise panel'
    bl_idname = 'B2N_PT_DENOISE'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'view_layer'
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = 'B2N_PT_MAINPANEL'
    bl_ui_units_x=0
    bl_order = 1
    
    
    def draw(self, context):
        layout=self.layout
        
        if bpy.context.scene.render.engine == 'CYCLES':

            layout.label(text='You are using Cycles passes can be denoised')
        
            row = layout.row(heading='', align=False)       
            row.alert = False
            row.active = True
            row.alignment = 'Center'.upper()
            row.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
            if bpy.data.scenes['Scene'].view_layers['ViewLayer'].cycles.denoising_store_passes:
                row.prop(bpy.data.scenes['Scene'].view_layers['ViewLayer'].cycles, 'denoising_store_passes', text='Passes are denoised.', icon_value=0, emboss=True)
            else:
                row.prop(bpy.data.scenes['Scene'].view_layers['ViewLayer'].cycles, 'denoising_store_passes', text='Passes are not denoised.', icon_value=0, emboss=True) 
            
            layout.label(text="Don't forget to regenerate the node tree after changing this option", icon_value=2)      

class EXR2NUKE_GENERATE_SUBPANEL(bpy.types.Panel):
    bl_label = 'Generate panel'
    bl_idname = 'B2N_PT_GENERATE'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'view_layer'
    bl_parent_id = 'B2N_PT_MAINPANEL'
    bl_ui_units_x=0
    
    def draw(self, context):
            layout = self.layout
            

            #Check box pour denoise ou non les passes

            
            #CREATE BUTTONS
            row = layout.row()
            row.label(text="How many outputs do you want to generate?")
            
            row = layout.row()
            row.label(text="One Exr")
            row.operator('node.1_operator', icon='NODE')
            
            row = layout.row()
            row.label(text="Beauty and Crypto Exrs")
            row.operator('node.2_operator', icon='NODE')
            
            row = layout.row()
            row.label(text="Light, Data and Crypto Exrs")
            row.operator('node.3_operator', icon='NODE')
 
class EXR2NUKE_OUTPUT_SUBPANEL(bpy.types.Panel):
    bl_label = 'Output panel'
    bl_idname = 'B2N_PT_OUTPUT'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'view_layer'
    bl_parent_id = 'B2N_PT_MAINPANEL'
    bl_ui_units_x=0
    
    def draw(self, context):
        layout = self.layout
            
        liste_outputs = ['Light_exr','Data_exr','Cryptomatte_exr','File_Output_exr']
        y=0
        for i in liste_outputs:
            if i in bpy.data.scenes['Scene'].node_tree.nodes:
                col_D70C6 = layout.column(heading='', align=False)
                col_D70C6.alert = False
                col_D70C6.enabled = True
                col_D70C6.active = True
                col_D70C6.use_property_split = False
                col_D70C6.use_property_decorate = False
                col_D70C6.scale_x = 1.0
                col_D70C6.scale_y = 1.0
                col_D70C6.alignment = 'Expand'.upper()
                col_D70C6.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                col_D70C6.label(text=i +':', icon_value=0)
                col_D70C6.prop(bpy.data.scenes['Scene'].node_tree.nodes[i], 'base_path', text='', icon_value=0, emboss=True)
                y=y+1
                
        if y == 0:
           layout.label(text='You have to select a method.', icon_value=2)


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
    bpy.utils.register_class(EXR2NUKE_DENOISE_SUBPANEL)
    bpy.utils.register_class(EXR2NUKE_GENERATE_SUBPANEL)
    bpy.utils.register_class(EXR2NUKE_OUTPUT_SUBPANEL)

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
    bpy.utils.unregister_class(EXR2NUKE_DENOISE_SUBPANEL)
    bpy.utils.register_class(EXR2NUKE_GENERATE_SUBPANEL)
    bpy.utils.register_class(EXR2NUKE_OUTPUT_SUBPANEL)
        
if __name__ == "__main__":
    register()
