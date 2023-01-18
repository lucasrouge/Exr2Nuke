import bpy
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
    library={
        "Image":{"name": "rgba", "denoise": True},
        "Alpha":{"name": "alpha", "denoise": False},
        "Depth":{"name": "depth", "denoise": False},   
        "Mist":{"name": "mist", "denoise": False},  
        "Position":{"name": "position", "denoise": False},  
        "Normal":{"name": "normal", "denoise": False},  
        "Vector":{"name": "vector", "denoise": False},  
        "UV":{"name": "uv", "denoise": False},  
        "DiffDir":{"name": "DiffDir", "denoise": True},  
        "DiffInd":{"name": "DiffInd", "denoise": True},  
        "DiffCol":{"name": "DiffCol", "denoise": True},  
        "GlossDir":{"name": "GlossDir", "denoise": True},  
        "GlossInd":{"name": "GlossInd", "denoise": True},  
        "GlossCol":{"name": "GlossCol", "denoise": True},  
        "TransDir":{"name": "TransDir", "denoise": True},  
        "TransInd":{"name": "TransInd", "denoise": True},  
        "TransCol":{"name": "TransCol", "denoise": True},  
        "VolumeDir":{"name": "VolDir", "denoise": True}, 
        "VolumeInd":{"name": "VolInd", "denoise": True}, 
        "Emit":{"name": "emit", "denoise": True}, 
        "Env":{"name": "env", "denoise": True}, 
        "AO":{"name": "ao", "denoise": True},
        "CryptoObject00":{"name": "CryptoObject00", "denoise": False},
        "CryptoObject01":{"name": "CryptoObject01", "denoise": False},
        "CryptoObject02":{"name": "CryptoObject02", "denoise": False},
        "CryptoMaterial00":{"name": "CryptoMaterial00", "denoise": False},
        "CryptoMaterial01":{"name": "CryptoMaterial01", "denoise": False},
        "CryptoMaterial02":{"name": "CryptoMaterial02", "denoise": False},
        "CryptoAsset00":{"name": "CryptoAsset00", "denoise": False},
        "CryptoAsset01":{"name": "CryptoAsset01", "denoise": False},
        "CryptoAsset02":{"name": "CryptoAsset02", "denoise": False},                  
    }



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
    FO_node.name = 'File_Output_EXR'
    FO_node.label = 'File_Output_EXR'
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
                        
    return {"One output done"}

if __name__ == "__main__":
    create_setup()
    print(create_setup())