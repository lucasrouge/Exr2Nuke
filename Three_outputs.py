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
        "Image":{"name": "rgba", "denoise": True, "out":["Light","Data","Crypto"]},
        "Alpha":{"name": "alpha", "denoise": False, "out":["Data"]},
        "Depth":{"name": "Depth", "denoise": False, "out":["Data"]},   
        "Mist":{"name": "mist", "denoise": False, "out":["Data"]},  
        "Position":{"name": "position", "denoise": False, "out":["Data"]},  
        "Normal":{"name": "normal", "denoise": False, "out":["Data"]},  
        "Vector":{"name": "vector", "denoise": False, "out":["Data"]},  
        "UV":{"name": "uv", "denoise": False, "out":["Data"]},  
        "DiffDir":{"name": "DiffDir", "denoise": True, "out":["Light"]},  
        "DiffInd":{"name": "DiffInd", "denoise": True, "out":["Light"]},  
        "DiffCol":{"name": "DiffCol", "denoise": True, "out":["Light"]},  
        "GlossDir":{"name": "GlossDir", "denoise": True, "out":["Light"]},  
        "GlossInd":{"name": "GlossInd", "denoise": True, "out":["Light"]},  
        "GlossCol":{"name": "GlossCol", "denoise": True, "out":["Light"]},  
        "TransDir":{"name": "TransDir", "denoise": True, "out":["Light"]},  
        "TransInd":{"name": "TransInd", "denoise": True, "out":["Light"]},  
        "TransCol":{"name": "TransCol", "denoise": True, "out":["Light"]},  
        "VolumeDir":{"name": "VolDir", "denoise": True, "out":["Light"]}, 
        "VolumeInd":{"name": "VolInd", "denoise": True, "out":["Light"]}, 
        "Emit":{"name": "Emit", "denoise": True, "out":["Light"]}, 
        "Env":{"name": "Env", "denoise": True, "out":["Light"]}, 
        "AO":{"name": "ao", "denoise": True, "out":["Light"]},
        "CryptoObject00":{"name": "CryptoObject00", "denoise": False, "out":["Crypto"]},
        "CryptoObject01":{"name": "CryptoObject01", "denoise": False, "out":["Crypto"]},
        "CryptoObject02":{"name": "CryptoObject02", "denoise": False, "out":["Crypto"]},
        "CryptoMaterial00":{"name": "CryptoMaterial00", "denoise": False, "out":["Crypto"]},
        "CryptoMaterial01":{"name": "CryptoMaterial01", "denoise": False, "out":["Crypto"]},
        "CryptoMaterial02":{"name": "CryptoMaterial02", "denoise": False, "out":["Crypto"]},
        "CryptoAsset00":{"name": "CryptoAsset00", "denoise": False, "out":["Crypto"]},
        "CryptoAsset01":{"name": "CryptoAsset01", "denoise": False, "out":["Crypto"]},
        "CryptoAsset02":{"name": "CryptoAsset02", "denoise": False, "out":["Crypto"]},                  
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
    
    
    
#File Outputs

    #Light_exr
    FO_Light_node = tree.nodes.new('CompositorNodeOutputFile')
    FO_Light_node.name = 'Light_exr'
    FO_Light_node.label = 'Light_exr'
    FO_Light_node.use_custom_color = True
    FO_Light_node.color = (0.169093, 0.35699, 0.608)   
    FO_Light_node.location = 800,0
    FO_Light_node.format.file_format = 'OPEN_EXR_MULTILAYER'
    FO_Light_node.format.color_depth = '16'
    FO_Light_node.base_path = '//Render/Light/{}'.format(file_name) + '_###.exr' #mettre le path du projet
    FO_Light_node.inputs.clear() #retire tous les inputs
    
    #Data_exr
    FO_Data_node = tree.nodes.new('CompositorNodeOutputFile')
    FO_Data_node.name = 'Data_exr'
    FO_Data_node.label = 'Data_exr'
    FO_Data_node.use_custom_color = True
    FO_Data_node.color = (0.608, 0.407564, 0.169093)   
    FO_Data_node.location = 800,-410
    FO_Data_node.format.file_format = 'OPEN_EXR_MULTILAYER'
    FO_Data_node.format.color_depth = '16'
    FO_Data_node.base_path = '//Render/Data/{}'.format(file_name) + '_###.exr' #mettre le path du projet
    FO_Data_node.inputs.clear()
    
    #Cryptomatte_exr
    crypto_exist=bpy.context.scene.view_layers["ViewLayer"].use_pass_cryptomatte_object == True or bpy.context.scene.view_layers["ViewLayer"].use_pass_cryptomatte_material == True or bpy.context.scene.view_layers["ViewLayer"].use_pass_cryptomatte_asset == True
    
    if crypto_exist:
        FO_Crypto_node = tree.nodes.new('CompositorNodeOutputFile')
        FO_Crypto_node.name = 'Cryptomatte_exr'
        FO_Crypto_node.label = 'Cryptomatte_exr'
        FO_Crypto_node.use_custom_color = True
        FO_Crypto_node.color = (0.343566, 0.608, 0.178791)   
        FO_Crypto_node.location = 800,-670
        FO_Crypto_node.format.file_format = 'OPEN_EXR_MULTILAYER'
        FO_Crypto_node.format.color_depth = '32'
        FO_Crypto_node.base_path = '//Render/Crypto/{}'.format(file_name) + '_###.exr' #mettre le path du projet
        FO_Crypto_node.inputs.clear()
    
    
#LINK NODES

    links = tree.links
    Denoise_pos = -150
    
    for i in outputs_useful:
        for y in library[i]["out"]:
            if y == "Data":
                FO_node=FO_Data_node
            elif y == "Light":
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