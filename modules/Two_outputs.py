import bpy
import json
import os
from pathlib import Path


def create_setup():

    # On récupère le nom du fichier
    file_name=bpy.context.blend_data.filepath #On récupère le chemin du fichier sous forme de chaine de caractère
    file_name=Path(file_name).stem #Path le transforme en chemin et stem récupère seulement le nom

    #Sauvegarde du nom des files outputs
    try :
        light_data_node_name = bpy.data.scenes["Scene"].node_tree.nodes["Light_Data_exr"].base_path
    except:
        light_data_node_name = '//Render/Light_Data/{}'.format(file_name) + '_###.exr' #mettre le path du projet

    try :
        cryptomattes_node_name = bpy.data.scenes["Scene"].node_tree.nodes["Cryptomatte_exr"].base_path
    except:
        cryptomattes_node_name = '//Render/Cryptomatte/{}'.format(file_name) + '_###.exr' #mettre le path du projet


    # On active l'utilisation des nodes
    bpy.context.scene.use_nodes = True

    # On nettoie le node tree
    for node in bpy.context.scene.node_tree.nodes:
        bpy.context.scene.node_tree.nodes.remove(node)

    #raccourci d'écriture
    tree = bpy.context.scene.node_tree
    links = tree.links

    #Lecture du fichier JSON pour savoir comment link   
    json_directory=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+'\Libraries'
    Cycles_json_path = json_directory + r"\Cycles_Node_Library_2.json"
    Eevee_json_path = json_directory + r"\Eevee_Node_Library_2.json"
    
    library={}
    if bpy.context.scene.render.engine == 'CYCLES':   
        with open(Cycles_json_path, "r") as f:
            library = json.load(f)
    else:     
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
    
    nombre_light=0
    for y in outputs_useful:
        if library[y]["out"]==["Light_Data"]:
            nombre_light += 1
    position_crypto=-100-nombre_light*24
    
    
    
#File Outputs

    #Light_exr
    FO_Light_node = tree.nodes.new('CompositorNodeOutputFile')
    FO_Light_node.name = 'Light_Data_exr'
    FO_Light_node.label = 'Light_Data_exr'
    FO_Light_node.use_custom_color = True
    FO_Light_node.color = (0.608, 0.169093, 0.34445)   
    FO_Light_node.location = 800,0
    FO_Light_node.format.file_format = 'OPEN_EXR_MULTILAYER'
    FO_Light_node.format.color_depth = '16'
    FO_Light_node.base_path = light_data_node_name
    FO_Light_node.inputs.clear() #retire tous les inputs
    

    #Cryptomatte_exr
    crypto_exist=bpy.context.scene.view_layers["ViewLayer"].use_pass_cryptomatte_object == True or bpy.context.scene.view_layers["ViewLayer"].use_pass_cryptomatte_material == True or bpy.context.scene.view_layers["ViewLayer"].use_pass_cryptomatte_asset == True
    
    if crypto_exist:
        FO_Crypto_node = tree.nodes.new('CompositorNodeOutputFile')
        FO_Crypto_node.name = 'Cryptomatte_exr'
        FO_Crypto_node.label = 'Cryptomatte_exr'
        FO_Crypto_node.use_custom_color = True
        FO_Crypto_node.color = (0.343566, 0.608, 0.178791)   
        FO_Crypto_node.location = 800,position_crypto
        FO_Crypto_node.format.file_format = 'OPEN_EXR_MULTILAYER'
        FO_Crypto_node.format.color_depth = '32'
        FO_Crypto_node.base_path = cryptomattes_node_name
        FO_Crypto_node.inputs.clear()
    
    
#LINK NODES

    links = tree.links
    Denoise_pos = -150
    
    for i in outputs_useful:
        for y in library[i]["out"]:
            if y == "Light_Data":
                FO_node=FO_Light_node
            elif (y == "Crypto" and not crypto_exist):
                break
            elif (y == "Crypto" and crypto_exist):
                FO_node=FO_Crypto_node
            new_in=FO_node.file_slots.new(name=library[i]["name"])
            
            if library[i]["denoise"]:
                #create Denoise
                DN_node = tree.nodes.new('CompositorNodeDenoise')
                DN_node.name="Denoise_" + library[i]["name"]
                DN_node.label=DN_node.name
                DN_node.location = 400,Denoise_pos
                DN_node.hide = True
                Denoise_pos += -30
                DN_node_save=DN_node
                    

                    
                #Indenoise
                link = links.new(RL_node.outputs[i], DN_node.inputs[0]) #Image
                link = links.new(RL_node.outputs['Denoising Normal'], DN_node.inputs[1]) #Denoising Normal
                link = links.new(RL_node.outputs['Denoising Albedo'], DN_node.inputs[2]) #Denoising Albedo
                            
                #Outdenoise
                for y in FO_node.inputs: 
                    if y.name == library[i]["name"]: 
                        link = links.new(DN_node.outputs[0], y)
                        
            else:
                for y in FO_node.inputs: 
                    if y.name == library[i]["name"]: 
                        link = links.new(RL_node.outputs[i], y)


if __name__ == "__main__":
    create_setup()
