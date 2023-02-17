import bpy
import os
import json
from pathlib import Path




def create_setup():

    # On récupère le nom du fichier
    file_name=bpy.context.blend_data.filepath #On récupère le chemin du fichier sous forme de chaine de caractère
    file_name=Path(file_name).stem #Path le transforme en chemin et stem récupère seulement le nom

    # On active l'utilisation des nodes
    bpy.context.scene.use_nodes = True

    # On nettoie le node tree
    for node in bpy.context.scene.node_tree.nodes:
        bpy.context.scene.node_tree.nodes.remove(node)

    #raccourci d'écriture
    tree = bpy.context.scene.node_tree
    links = tree.links

    # Bibliothèque pour décider comment ranger les passes et si on doit les denoiser
    
#    #script_directory = bpy.utils.script_path_user()
#    json_directory = script_directory + r"\addons\Exr2Nuke\libraries"


    json_directory=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'\Libraries'
    Cycles_json_path = json_directory + r"\Cycles_Node_Library.json"
    Eevee_json_path = json_directory + r"\Cycles_Node_Library.json"
    library={}
    if bpy.context.scene.render.engine == 'CYCLES':   
        with open(Cycles_json_path, "r") as f:
            library = json.load(f)
    elif bpy.context.scene.render.engine == 'BLENDER_EEVEE':     
        with open(Eevee_json_path, "r") as f:
            library = json.load(f)
        


    # On décide si on veut denoiser ou pas, si non on change l'attribut dans la bibliothèque
    if not bpy.context.scene.view_layers["ViewLayer"].cycles.denoising_store_passes :
        for i in library:
            library[i]["denoise"]=False


    # CREATION DES NOEUDS

    # Création du Render Layer node
    RL_node = tree.nodes.new(type='CompositorNodeRLayers')
    RL_node.location = 0,0

    # Création d'une bibliothèque qui contient les passes utiles et leur index dans le Render Layer node
    outputs_enabled={}
    index=0
    for i in RL_node.outputs:
        if i.enabled :
            outputs_enabled[i.name]=str(index)
        index+=1

    #Les outputs utiles sont ceux qui sont à la fois activés et qui sont dans la librairie
    outputs_useful = [i for i in outputs_enabled if i in library]

    # Création du File Output node
    FO_node = tree.nodes.new('CompositorNodeOutputFile')
    FO_node.name = 'File_Output_exr'
    FO_node.label = 'File_Output_exr'
    FO_node.use_custom_color = True
    FO_node.color = (0.551642, 0.335332, 0.566339)   
    FO_node.location = 800,0
    FO_node.format.file_format = 'OPEN_EXR_MULTILAYER'
    FO_node.format.color_depth = '32'
    FO_node.base_path = f"//Render/{file_name}_render_###.exr"
    FO_node.inputs.clear() 


    #On initialise la postion des nodes de denoise
    Denoise_pos = -150


    for i in outputs_useful:
        
            # Création d'un nouvel input dans le File output node
            new_in=FO_node.file_slots.new(name=library[i]["name"])
            
            if library[i]["denoise"]:
                
                # Création d'un noeud Denoise
                DN_node = tree.nodes.new('CompositorNodeDenoise')
                DN_node.name="Denoise_" + library[i]["name"]
                DN_node.label=DN_node.name
                DN_node.location = 400,Denoise_pos
                DN_node.hide = True
                Denoise_pos += -30
                
                # Branchement des noeuds
                link = links.new(RL_node.outputs[i], DN_node.inputs[0]) # Image
                link = links.new(RL_node.outputs['Denoising Normal'], DN_node.inputs[1]) # Normale de denoise
                link = links.new(RL_node.outputs['Denoising Albedo'], DN_node.inputs[2]) # Albedo de denoise
                
                # Sortie du noeud denoise
                for y in FO_node.inputs: 
                    if y.name == library[i]["name"]: 
                        link = links.new(DN_node.outputs[0], y)
            else:
                for y in FO_node.inputs: 
                    if y.name == library[i]["name"]: 
                        link = links.new(RL_node.outputs[i], y)
                        

if __name__ == "__main__":
    create_setup()
    print(create_setup())