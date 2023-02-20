import bpy
import json
import os

addon_directory=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
module_directory=addon_directory+'\Modules'
libraries_directory=addon_directory+'\Libraries'
Cycles_fast_select_json_path=libraries_directory+'\Cycles_fast_select.json'   

context = bpy.context
view_layer = context.scene.view_layers["ViewLayer"]

def apply():
    #lecture du fichier json qui gère le fast selection               
    library={}
    with open(Cycles_fast_select_json_path, "r") as f:
        library = json.load(f)
        
    #attribution des valeurs du fichier json
    for i in library:
        if library[i]["parent"] == "view_layer":
            setattr(view_layer, library[i]["attribute"], library[i]["value"])
        elif library[i]["parent"] == "view_layer.cycles":
            setattr(view_layer.cycles, library[i]["attribute"], library[i]["value"])
def save():  
    library={}
    with open(Cycles_fast_select_json_path, "r") as f:
        library = json.load(f)
    
    for i in library:
        if library[i]["parent"] == "view_layer":
            new_attr = getattr(view_layer, library[i]["attribute"])
            library[i]["value"] = new_attr
        elif library[i]["parent"] == "view_layer.cycles":
            new_attr = getattr(view_layer.cycles, library[i]["attribute"])
            library[i]["value"] = new_attr
    
    with open(Cycles_fast_select_json_path, "w") as f:
        json.dump(library, f, indent=4)