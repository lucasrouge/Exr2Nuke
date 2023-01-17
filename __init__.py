# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Exr to Nuke",
    "author" : "Lucas ROUGE, Adrien BLANCHARD", 
    "description" : "A simple way to export exr to Nuke.",
    "blender" : (3, 3, 1),
    "version" : (1, 0, 0),
    "location" : "Render Properties",
    "warning" : "",
    "doc_url": "", 
    "tracker_url": "", 
    "category" : "Render" 
}


import bpy
import bpy.utils.previews


addon_keymaps = {}
_icons = None


def sna_update_sna_single_method_cycles_1F8F2(self, context):
    sna_updated_prop = self.sna_single_method_cycles
    if sna_updated_prop:
        # On récupère le nom du fichier
        file_name=bpy.path.basename(bpy.context.blend_data.filepath).replace(".blend","")
        # On initialise certains paramètres
        bpy.context.scene.use_nodes = True
        bpy.context.scene.cycles.use_denoising = False
        tree = bpy.context.scene.node_tree
        # On nettoie le node tree
        for node in bpy.context.scene.node_tree.nodes:
            bpy.context.scene.node_tree.nodes.remove(node)
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
        # Bibliothèque pour décider comment ranger les passes et si on doit les denoiser dans le cas ou le moteur de rendu est Eevee
        if bpy.context.scene.render.engine == 'BLENDER_EEVEE':
            library={
                "Image":{"name": "rgba", "denoise": False},
                "Alpha":{"name": "alpha", "denoise": False},
                "Depth":{"name": "depth", "denoise": False},   
                "Mist":{"name": "mist", "denoise": False},   
                "Normal":{"name": "normal", "denoise": False},  
                "DiffDir":{"name": "DiffLight", "denoise": False},   
                "DiffCol":{"name": "DiffCol", "denoise": False},  
                "GlossDir":{"name": "GlossLight", "denoise": False},  
                "GlossCol":{"name": "GlossCol", "denoise": False},  
                "VolumeDir":{"name": "VolLight", "denoise": False}, 
                "Emit":{"name": "emit", "denoise": False}, 
                "Env":{"name": "env", "denoise": False}, 
                "Shadow":{"name": "shadow", "denoise": False}, 
                "AO":{"name": "ao", "denoise": False},
                "BloomCol":{"name": "bloom", "denoise": False}, 
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
        # On décide si on veut denoiser ou pas, si oui on change l'attribut dans la bibliothèque
        if not bpy.context.scene.view_layers["ViewLayer"].cycles.denoising_store_passes :
            for i in library:
                library[i]["denoise"]=False
        # CREATION DES NOEUDS
        # Render Layer
        RL_node = tree.nodes.new(type='CompositorNodeRLayers')
        RL_node.location = 0,0
        # Création d'une bibliothèque avec nom:index
        RL_node_info={}
        index=0
        for i in RL_node.outputs:
            if i.enabled :
                RL_node_info[i.name]=str(index)
            index+=1
        # File Outputs
        # Light_exr
        FO_node = tree.nodes.new('CompositorNodeOutputFile')
        FO_node.name = 'File_Output_EXR'
        FO_node.label = 'File_Output_EXR'
        FO_node.use_custom_color = True
        FO_node.color = (0.551642, 0.335332, 0.566339)   
        FO_node.location = 800,0
        FO_node.format.file_format = 'OPEN_EXR_MULTILAYER'
        FO_node.format.color_depth = '32'
        FO_node.base_path = '//Render/{}'.format(file_name) + '_###.exr' #mettre le path du projet
        FO_node.inputs.clear() #retire tous les inputs
        # Lien des noeuds
        links = tree.links
        Denoise_pos = -150
        for i in RL_node_info:
            if i in library:
                # Création d'un nouveau slot d'entrée pour la sortie de fichier correspondant à l'élément en cours
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
                            # Branchement direct du Render Layer à la sortie de fichier sans débruitage
                            link = links.new(RL_node.outputs[i], y)
    else:
        # On parcourt tous les noeuds de l'arbre de noeuds de la scène en cours
        for node in bpy.context.scene.node_tree.nodes:
            # On retire chaque noeud de l'arbre de noeuds
            bpy.context.scene.node_tree.nodes.remove(node)


def sna_update_sna_multiple_method_cycles_15156(self, context):
    sna_updated_prop = self.sna_multiple_method_cycles
    if sna_updated_prop:
        #On récupère le nom du fichier
        file_name=bpy.path.basename(bpy.context.blend_data.filepath).replace(".blend","")
        #On initialise certains paramètres
        bpy.context.scene.use_nodes = True
        bpy.context.scene.cycles.use_denoising = False
        tree = bpy.context.scene.node_tree
        # On nettoie le node tree
        for node in bpy.context.scene.node_tree.nodes:
            bpy.context.scene.node_tree.nodes.remove(node)
        # Bibliothèque pour décider comment ranger les passes et si on doit les denoiser
        library={
            "Image":{"name": "rgba", "denoise": True, "out":["Light","Data","Crypto"]},
            "Alpha":{"name": "alpha", "denoise": False, "out":["Data"]},
            "Depth":{"name": "depth", "denoise": False, "out":["Data"]},   
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
            "Emit":{"name": "emit", "denoise": True, "out":["Light"]}, 
            "Env":{"name": "env", "denoise": True, "out":["Light"]}, 
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
        # Bibliothèque pour décider comment ranger les passes et si on doit les denoiser dans le cas ou le moteur de rendu est Eevee
        if bpy.context.scene.render.engine == 'BLENDER_EEVEE':
            library={
                "Image":{"name": "rgba", "denoise": False, "out":["Light","Data","Crypto"]},
                "Alpha":{"name": "alpha", "denoise": False, "out":["Data"]},
                "Depth":{"name": "depth", "denoise": False, "out":["Data"]},   
                "Mist":{"name": "mist", "denoise": False, "out":["Data"]},   
                "Normal":{"name": "normal", "denoise": False, "out":["Data"]},  
                "DiffDir":{"name": "DiffLight", "denoise": False, "out":["Light"]},   
                "DiffCol":{"name": "DiffCol", "denoise": False, "out":["Light"]},  
                "GlossDir":{"name": "GlossLight", "denoise": False, "out":["Light"]},  
                "GlossCol":{"name": "GlossCol", "denoise": False, "out":["Light"]},  
                "VolumeDir":{"name": "VolLight", "denoise": False, "out":["Light"]}, 
                "Emit":{"name": "emit", "denoise": False, "out":["Light"]}, 
                "Env":{"name": "env", "denoise": False, "out":["Light"]}, 
                "Shadow":{"name": "shadow", "denoise": False, "out":["Light"]}, 
                "AO":{"name": "ao", "denoise": False, "out":["Light"]},
                "BloomCol":{"name": "bloom", "denoise": False, "out":["Light"]}, 
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
        #On décide si on veut denoise ou pas, si oui on change l'attribut dans la bibliothèque
        if not bpy.context.scene.view_layers["ViewLayer"].cycles.denoising_store_passes :
            for i in library:
                library[i]["denoise"]=False
        # CREATION DES NOEUDS
        #Render Layer
        RL_node = tree.nodes.new(type='CompositorNodeRLayers')
        RL_node.location = 0,0
        #Création d'une bibliothèque avec nom:index
        RL_node_info={}
        index=0
        for i in RL_node.outputs:
            if i.enabled:
                RL_node_info[i.name]=str(index)
            index+=1
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
        # Lien des noeuds
        links = tree.links
        Denoise_pos = -150
        for i in RL_node_info:
            if i in library:
                for y in library[i]["out"]:
                    # Détermination de la sortie de fichier en fonction de l'attribut "out" de l'élément en cours dans la bibliothèque
                    if y == "Data":
                        FO_node=FO_Data_node
                    elif y == "Light":
                        FO_node=FO_Light_node
                    elif (y == "Crypto" and not crypto_exist):
                        # Si l'attribut est "Crypto" mais que crypto_exist est faux, on sort de la boucle
                        break
                    elif (y == "Crypto" and crypto_exist):
                        FO_node=FO_Crypto_node
                    # Création d'un nouveau slot d'entrée pour la sortie de fichier correspondant à l'élément en cours
                    new_in=FO_node.file_slots.new(name=library[i]["name"])
                    if library[i]["denoise"]:
                        # Création d'un noeud Denoise
                        DN_node = tree.nodes.new('CompositorNodeDenoise')
                        DN_node.name="Denoise_" + library[i]["name"]
                        DN_node.label=DN_node.name
                        DN_node.location = 400,Denoise_pos
                        DN_node.hide = True
                        Denoise_pos += -30
                        DN_node_save=DN_node
                        # Branchement des noeuds pour le débruitage
                        link = links.new(RL_node.outputs[i], DN_node.inputs[0]) # Image
                        link = links.new(RL_node.outputs['Denoising Normal'], DN_node.inputs[1]) # Normale de denoise
                        link = links.new(RL_node.outputs['Denoising Albedo'], DN_node.inputs[2]) # Albedo de denoise
                        # Sortie du noeud Denoise vers la sortie de fichier correspondante
                        for y in FO_node.inputs: 
                            if y.name == library[i]["name"]: 
                                link = links.new(DN_node.outputs[0], y)
                    else:
                        # Branchement direct du Render Layer à la sortie de fichier sans débruitage
                        for y in FO_node.inputs: 
                            if y.name == library[i]["name"]: 
                                link = links.new(RL_node.outputs[i], y)
    else:
        # On parcourt tous les noeuds de l'arbre de noeuds de la scène en cours
        for node in bpy.context.scene.node_tree.nodes:
            # On retire chaque noeud de l'arbre de noeuds
            bpy.context.scene.node_tree.nodes.remove(node)


def sna_update_sna_multiple_method_eevee_349C5(self, context):
    sna_updated_prop = self.sna_multiple_method_eevee
    if sna_updated_prop:
        #On récupère le nom du fichier
        file_name=bpy.path.basename(bpy.context.blend_data.filepath).replace(".blend","")
        #On initialise certains paramètres
        bpy.context.scene.use_nodes = True
        bpy.context.scene.cycles.use_denoising = False
        tree = bpy.context.scene.node_tree
        # On nettoie le node tree
        for node in bpy.context.scene.node_tree.nodes:
            bpy.context.scene.node_tree.nodes.remove(node)
        # Bibliothèque pour décider comment ranger les passes et si on doit les denoiser
        library={
            "Image":{"name": "rgba", "denoise": True, "out":["Light","Data","Crypto"]},
            "Alpha":{"name": "alpha", "denoise": False, "out":["Data"]},
            "Depth":{"name": "depth", "denoise": False, "out":["Data"]},   
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
            "Emit":{"name": "emit", "denoise": True, "out":["Light"]}, 
            "Env":{"name": "env", "denoise": True, "out":["Light"]}, 
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
        # Bibliothèque pour décider comment ranger les passes et si on doit les denoiser dans le cas ou le moteur de rendu est Eevee
        if bpy.context.scene.render.engine == 'BLENDER_EEVEE':
            library={
                "Image":{"name": "rgba", "denoise": False, "out":["Light","Data","Crypto"]},
                "Alpha":{"name": "alpha", "denoise": False, "out":["Data"]},
                "Depth":{"name": "depth", "denoise": False, "out":["Data"]},   
                "Mist":{"name": "mist", "denoise": False, "out":["Data"]},   
                "Normal":{"name": "normal", "denoise": False, "out":["Data"]},  
                "DiffDir":{"name": "DiffLight", "denoise": False, "out":["Light"]},   
                "DiffCol":{"name": "DiffCol", "denoise": False, "out":["Light"]},  
                "GlossDir":{"name": "GlossLight", "denoise": False, "out":["Light"]},  
                "GlossCol":{"name": "GlossCol", "denoise": False, "out":["Light"]},  
                "VolumeDir":{"name": "VolLight", "denoise": False, "out":["Light"]}, 
                "Emit":{"name": "emit", "denoise": False, "out":["Light"]}, 
                "Env":{"name": "env", "denoise": False, "out":["Light"]}, 
                "Shadow":{"name": "shadow", "denoise": False, "out":["Light"]}, 
                "AO":{"name": "ao", "denoise": False, "out":["Light"]},
                "BloomCol":{"name": "bloom", "denoise": False, "out":["Light"]}, 
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
        #On décide si on veut denoise ou pas, si oui on change l'attribut dans la bibliothèque
        if not bpy.context.scene.view_layers["ViewLayer"].cycles.denoising_store_passes :
            for i in library:
                library[i]["denoise"]=False
        # CREATION DES NOEUDS
        #Render Layer
        RL_node = tree.nodes.new(type='CompositorNodeRLayers')
        RL_node.location = 0,0
        #Création d'une bibliothèque avec nom:index
        RL_node_info={}
        index=0
        for i in RL_node.outputs:
            if i.enabled:
                RL_node_info[i.name]=str(index)
            index+=1
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
        # Lien des noeuds
        links = tree.links
        Denoise_pos = -150
        for i in RL_node_info:
            if i in library:
                for y in library[i]["out"]:
                    # Détermination de la sortie de fichier en fonction de l'attribut "out" de l'élément en cours dans la bibliothèque
                    if y == "Data":
                        FO_node=FO_Data_node
                    elif y == "Light":
                        FO_node=FO_Light_node
                    elif (y == "Crypto" and not crypto_exist):
                        # Si l'attribut est "Crypto" mais que crypto_exist est faux, on sort de la boucle
                        break
                    elif (y == "Crypto" and crypto_exist):
                        FO_node=FO_Crypto_node
                    # Création d'un nouveau slot d'entrée pour la sortie de fichier correspondant à l'élément en cours
                    new_in=FO_node.file_slots.new(name=library[i]["name"])
                    if library[i]["denoise"]:
                        # Création d'un noeud Denoise
                        DN_node = tree.nodes.new('CompositorNodeDenoise')
                        DN_node.name="Denoise_" + library[i]["name"]
                        DN_node.label=DN_node.name
                        DN_node.location = 400,Denoise_pos
                        DN_node.hide = True
                        Denoise_pos += -30
                        DN_node_save=DN_node
                        # Branchement des noeuds pour le débruitage
                        link = links.new(RL_node.outputs[i], DN_node.inputs[0]) # Image
                        link = links.new(RL_node.outputs['Denoising Normal'], DN_node.inputs[1]) # Normale de denoise
                        link = links.new(RL_node.outputs['Denoising Albedo'], DN_node.inputs[2]) # Albedo de denoise
                        # Sortie du noeud Denoise vers la sortie de fichier correspondante
                        for y in FO_node.inputs: 
                            if y.name == library[i]["name"]: 
                                link = links.new(DN_node.outputs[0], y)
                    else:
                        # Branchement direct du Render Layer à la sortie de fichier sans débruitage
                        for y in FO_node.inputs: 
                            if y.name == library[i]["name"]: 
                                link = links.new(RL_node.outputs[i], y)
    else:
        # On parcourt tous les noeuds de l'arbre de noeuds de la scène en cours
        for node in bpy.context.scene.node_tree.nodes:
            # On retire chaque noeud de l'arbre de noeuds
            bpy.context.scene.node_tree.nodes.remove(node)


def sna_update_sna_single_method_eevee_9C3E0(self, context):
    sna_updated_prop = self.sna_single_method_eevee
    if sna_updated_prop:
        # On récupère le nom du fichier
        file_name=bpy.path.basename(bpy.context.blend_data.filepath).replace(".blend","")
        # On initialise certains paramètres
        bpy.context.scene.use_nodes = True
        bpy.context.scene.cycles.use_denoising = False
        tree = bpy.context.scene.node_tree
        # On nettoie le node tree
        for node in bpy.context.scene.node_tree.nodes:
            bpy.context.scene.node_tree.nodes.remove(node)
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
        # Bibliothèque pour décider comment ranger les passes et si on doit les denoiser dans le cas ou le moteur de rendu est Eevee
        if bpy.context.scene.render.engine == 'BLENDER_EEVEE':
            library={
                "Image":{"name": "rgba", "denoise": False},
                "Alpha":{"name": "alpha", "denoise": False},
                "Depth":{"name": "depth", "denoise": False},   
                "Mist":{"name": "mist", "denoise": False},   
                "Normal":{"name": "normal", "denoise": False},  
                "DiffDir":{"name": "DiffLight", "denoise": False},   
                "DiffCol":{"name": "DiffCol", "denoise": False},  
                "GlossDir":{"name": "GlossLight", "denoise": False},  
                "GlossCol":{"name": "GlossCol", "denoise": False},  
                "VolumeDir":{"name": "VolLight", "denoise": False}, 
                "Emit":{"name": "emit", "denoise": False}, 
                "Env":{"name": "env", "denoise": False}, 
                "Shadow":{"name": "shadow", "denoise": False}, 
                "AO":{"name": "ao", "denoise": False},
                "BloomCol":{"name": "bloom", "denoise": False}, 
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
        # On décide si on veut denoiser ou pas, si oui on change l'attribut dans la bibliothèque
        if not bpy.context.scene.view_layers["ViewLayer"].cycles.denoising_store_passes :
            for i in library:
                library[i]["denoise"]=False
        # CREATION DES NOEUDS
        # Render Layer
        RL_node = tree.nodes.new(type='CompositorNodeRLayers')
        RL_node.location = 0,0
        # Création d'une bibliothèque avec nom:index
        RL_node_info={}
        index=0
        for i in RL_node.outputs:
            if i.enabled :
                RL_node_info[i.name]=str(index)
            index+=1
        # File Outputs
        # Light_exr
        FO_node = tree.nodes.new('CompositorNodeOutputFile')
        FO_node.name = 'File_Output_EXR'
        FO_node.label = 'File_Output_EXR'
        FO_node.use_custom_color = True
        FO_node.color = (0.551642, 0.335332, 0.566339)   
        FO_node.location = 800,0
        FO_node.format.file_format = 'OPEN_EXR_MULTILAYER'
        FO_node.format.color_depth = '32'
        FO_node.base_path = '//Render/{}'.format(file_name) + '_###.exr' #mettre le path du projet
        FO_node.inputs.clear() #retire tous les inputs
        # Lien des noeuds
        links = tree.links
        Denoise_pos = -150
        for i in RL_node_info:
            if i in library:
                # Création d'un nouveau slot d'entrée pour la sortie de fichier correspondant à l'élément en cours
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
                            # Branchement direct du Render Layer à la sortie de fichier sans débruitage
                            link = links.new(RL_node.outputs[i], y)
    else:
        # On parcourt tous les noeuds de l'arbre de noeuds de la scène en cours
        for node in bpy.context.scene.node_tree.nodes:
            # On retire chaque noeud de l'arbre de noeuds
            bpy.context.scene.node_tree.nodes.remove(node)


class SNA_OT_Op_Fast_Selection_F9Fd6(bpy.types.Operator):
    bl_idname = "sna.op_fast_selection_f9fd6"
    bl_label = "op_fast_selection"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        # Obtenir le contexte actuel
        context = bpy.context
        # Accéder à la couche de vue "ViewLayer"
        view_layer = context.scene.view_layers["ViewLayer"]
        # Désactiver les passes de rendu
        view_layer.use_pass_position = False
        view_layer.use_pass_normal = False
        view_layer.use_pass_vector = False
        view_layer.use_pass_uv = False
        view_layer.use_pass_object_index = False
        view_layer.use_pass_material_index = False
        view_layer.cycles.pass_debug_sample_count = False
        view_layer.pass_alpha_threshold = 0.5
        view_layer.use_pass_shadow = False  
        view_layer.cycles.use_pass_shadow_catcher = False 
        # Activer les passes de rendu
        view_layer.use_pass_combined = True
        view_layer.use_pass_z = True
        view_layer.use_pass_mist = True
        view_layer.use_pass_diffuse_direct = True
        view_layer.use_pass_diffuse_indirect = True
        view_layer.use_pass_diffuse_color = True
        view_layer.use_pass_glossy_direct = True
        view_layer.use_pass_glossy_indirect = True
        view_layer.use_pass_glossy_color = True
        view_layer.use_pass_transmission_direct = True
        view_layer.use_pass_transmission_indirect = True
        view_layer.use_pass_transmission_color = True
        view_layer.cycles.use_pass_volume_direct = True
        view_layer.cycles.use_pass_volume_indirect = True
        view_layer.use_pass_emit = True
        view_layer.use_pass_environment = True
        view_layer.use_pass_ambient_occlusion = True
        view_layer.use_pass_cryptomatte_object = True
        view_layer.use_pass_cryptomatte_material = True
        view_layer.use_pass_cryptomatte_asset = True
        view_layer.pass_cryptomatte_depth = 6
        view_layer.cycles.denoising_store_passes = True
        # Vérifier si le moteur de rendu est "BLENDER_EEVEE"
        if context.scene.render.engine == "BLENDER_EEVEE":
            # Désactiver les passes normales
            view_layer.use_pass_normal = False
            view_layer.use_pass_shadow = False
            # Activer les effets de rendu
            context.scene.eevee.use_bloom = True
            # Activer les passes de rendu
            view_layer.use_pass_combined = True
            view_layer.use_pass_z = True
            view_layer.use_pass_mist = True
            view_layer.use_pass_diffuse_direct = True
            view_layer.use_pass_diffuse_color = True
            view_layer.use_pass_diffuse_direct = True
            view_layer.use_pass_diffuse_color = True
            view_layer.use_pass_glossy_direct = True
            view_layer.use_pass_glossy_color = True
            view_layer.eevee.use_pass_volume_direct = True
            view_layer.cycles.use_pass_volume_direct = True
            view_layer.use_pass_emit = True
            view_layer.use_pass_environment = True
            view_layer.use_pass_ambient_occlusion = True
            view_layer.eevee.use_pass_bloom = True
            view_layer.use_pass_cryptomatte_object = True
            view_layer.use_pass_cryptomatte_material = True
            view_layer.use_pass_cryptomatte_asset = True
            view_layer.pass_cryptomatte_depth = 6
            view_layer.use_pass_cryptomatte_accurate = True
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_OT_Op_Fast_Selection_Eevee_81E1A(bpy.types.Operator):
    bl_idname = "sna.op_fast_selection_eevee_81e1a"
    bl_label = "op_fast_selection_eevee"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return not False

    def execute(self, context):
        # Obtenir le contexte actuel
        context = bpy.context
        # Accéder à la couche de vue "ViewLayer"
        view_layer = context.scene.view_layers["ViewLayer"]
        # Désactiver les passes de rendu
        view_layer.use_pass_position = False
        view_layer.use_pass_normal = False
        view_layer.use_pass_vector = False
        view_layer.use_pass_uv = False
        view_layer.use_pass_object_index = False
        view_layer.use_pass_material_index = False
        view_layer.cycles.pass_debug_sample_count = False
        view_layer.pass_alpha_threshold = 0.5
        view_layer.use_pass_shadow = False  
        view_layer.cycles.use_pass_shadow_catcher = False 
        # Activer les passes de rendu
        view_layer.use_pass_combined = True
        view_layer.use_pass_z = True
        view_layer.use_pass_mist = True
        view_layer.use_pass_diffuse_direct = True
        view_layer.use_pass_diffuse_indirect = True
        view_layer.use_pass_diffuse_color = True
        view_layer.use_pass_glossy_direct = True
        view_layer.use_pass_glossy_indirect = True
        view_layer.use_pass_glossy_color = True
        view_layer.use_pass_transmission_direct = True
        view_layer.use_pass_transmission_indirect = True
        view_layer.use_pass_transmission_color = True
        view_layer.cycles.use_pass_volume_direct = True
        view_layer.cycles.use_pass_volume_indirect = True
        view_layer.use_pass_emit = True
        view_layer.use_pass_environment = True
        view_layer.use_pass_ambient_occlusion = True
        view_layer.use_pass_cryptomatte_object = True
        view_layer.use_pass_cryptomatte_material = True
        view_layer.use_pass_cryptomatte_asset = True
        view_layer.pass_cryptomatte_depth = 6
        view_layer.cycles.denoising_store_passes = True
        # Vérifier si le moteur de rendu est "BLENDER_EEVEE"
        if context.scene.render.engine == "BLENDER_EEVEE":
            # Désactiver les passes normales
            view_layer.use_pass_normal = False
            view_layer.use_pass_shadow = False
            # Activer les effets de rendu
            context.scene.eevee.use_bloom = True
            # Activer les passes de rendu
            view_layer.use_pass_combined = True
            view_layer.use_pass_z = True
            view_layer.use_pass_mist = True
            view_layer.use_pass_diffuse_direct = True
            view_layer.use_pass_diffuse_color = True
            view_layer.use_pass_diffuse_direct = True
            view_layer.use_pass_diffuse_color = True
            view_layer.use_pass_glossy_direct = True
            view_layer.use_pass_glossy_color = True
            view_layer.eevee.use_pass_volume_direct = True
            view_layer.cycles.use_pass_volume_direct = True
            view_layer.use_pass_emit = True
            view_layer.use_pass_environment = True
            view_layer.use_pass_ambient_occlusion = True
            view_layer.eevee.use_pass_bloom = True
            view_layer.use_pass_cryptomatte_object = True
            view_layer.use_pass_cryptomatte_material = True
            view_layer.use_pass_cryptomatte_asset = True
            view_layer.pass_cryptomatte_depth = 6
            view_layer.use_pass_cryptomatte_accurate = True
        return {"FINISHED"}

    def invoke(self, context, event):
        return self.execute(context)


class SNA_PT_EXR_TO_NUKE_2969F(bpy.types.Panel):
    bl_label = 'Exr to Nuke'
    bl_idname = 'SNA_PT_EXR_TO_NUKE_2969F'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'
    bl_order = 1
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = 'RENDER_PT_context'
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        box_508D7 = layout.box()
        box_508D7.alert = False
        box_508D7.enabled = True
        box_508D7.active = True
        box_508D7.use_property_split = False
        box_508D7.use_property_decorate = False
        box_508D7.alignment = 'Expand'.upper()
        box_508D7.scale_x = 1.0
        box_508D7.scale_y = 0.550000011920929
        box_508D7.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_E9EE8 = box_508D7.row(heading='', align=False)
        row_E9EE8.alert = False
        row_E9EE8.enabled = True
        row_E9EE8.active = True
        row_E9EE8.use_property_split = False
        row_E9EE8.use_property_decorate = False
        row_E9EE8.scale_x = 1.0
        row_E9EE8.scale_y = 1.0
        row_E9EE8.alignment = 'Center'.upper()
        row_E9EE8.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_E9EE8.label(text='EXR TO NUKE', icon_value=0)
        if (bpy.context.engine == 'CYCLES'):
            pass


class SNA_PT_OUTPUT_7AC16(bpy.types.Panel):
    bl_label = '3. Output.'
    bl_idname = 'SNA_PT_OUTPUT_7AC16'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'
    bl_order = 4
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = 'SNA_PT_EXR_TO_NUKE_2969F'
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not ((not (bpy.context.engine == 'CYCLES')))

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        if bpy.context.scene.sna_single_method_cycles:
            layout.label(text='Path:', icon_value=0)
            layout.prop(bpy.data.scenes['Scene'].node_tree.nodes['File_Output_EXR'], 'base_path', text='', icon_value=0, emboss=True)
        else:
            if bpy.context.scene.sna_multiple_method_cycles:
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
                col_D70C6.label(text='Light:', icon_value=0)
                col_D70C6.prop(bpy.data.scenes['Scene'].node_tree.nodes['Light_exr'], 'base_path', text='', icon_value=0, emboss=True)
                col_D70C6.label(text='Data:', icon_value=0)
                col_D70C6.prop(bpy.data.scenes['Scene'].node_tree.nodes['Data_exr'], 'base_path', text='', icon_value=0, emboss=True)
                col_D70C6.label(text='Cryptomatte:', icon_value=0)
                col_D70C6.prop(bpy.data.scenes['Scene'].node_tree.nodes['Cryptomatte_exr'], 'base_path', text='', icon_value=0, emboss=True)
            else:
                layout.label(text='You have to select a method.', icon_value=2)


class SNA_PT_SELECT_METHOD_6F4F2(bpy.types.Panel):
    bl_label = '2. Select method.'
    bl_idname = 'SNA_PT_SELECT_METHOD_6F4F2'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'
    bl_order = 3
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = 'SNA_PT_EXR_TO_NUKE_2969F'
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not ((not (bpy.context.engine == 'CYCLES')))

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        row_2995C = layout.row(heading='', align=False)
        row_2995C.alert = False
        row_2995C.enabled = (bpy.context.scene.sna_single_method_cycles == bpy.context.scene.sna_multiple_method_cycles)
        row_2995C.active = True
        row_2995C.use_property_split = False
        row_2995C.use_property_decorate = False
        row_2995C.scale_x = 1.0
        row_2995C.scale_y = 1.0
        row_2995C.alignment = 'Expand'.upper()
        row_2995C.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        if bpy.data.scenes['Scene'].view_layers['ViewLayer'].cycles.denoising_store_passes:
            row_2995C.prop(bpy.data.scenes['Scene'].view_layers['ViewLayer'].cycles, 'denoising_store_passes', text='Passes are denoised.', icon_value=0, emboss=True)
        else:
            row_2995C.prop(bpy.data.scenes['Scene'].view_layers['ViewLayer'].cycles, 'denoising_store_passes', text='Passes are not denoised.', icon_value=0, emboss=True)
        row_EDEBF = layout.row(heading='', align=False)
        row_EDEBF.alert = False
        row_EDEBF.enabled = True
        row_EDEBF.active = True
        row_EDEBF.use_property_split = False
        row_EDEBF.use_property_decorate = False
        row_EDEBF.scale_x = 1.0
        row_EDEBF.scale_y = 1.0
        row_EDEBF.alignment = 'Center'.upper()
        row_EDEBF.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_EDEBF.label(text='-------------------------', icon_value=0)
        row_438D0 = layout.row(heading='', align=False)
        row_438D0.alert = False
        row_438D0.enabled = (not bpy.context.scene.sna_multiple_method_cycles)
        row_438D0.active = True
        row_438D0.use_property_split = False
        row_438D0.use_property_decorate = False
        row_438D0.scale_x = 1.0
        row_438D0.scale_y = 1.0
        row_438D0.alignment = 'Expand'.upper()
        row_438D0.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_438D0.prop(bpy.context.scene, 'sna_single_method_cycles', text='Single (Everything in an exr).', icon_value=0, emboss=True, toggle=False, index=0)
        row_78F3F = layout.row(heading='', align=False)
        row_78F3F.alert = False
        row_78F3F.enabled = (not bpy.context.scene.sna_single_method_cycles)
        row_78F3F.active = True
        row_78F3F.use_property_split = False
        row_78F3F.use_property_decorate = False
        row_78F3F.scale_x = 1.0
        row_78F3F.scale_y = 1.0
        row_78F3F.alignment = 'Expand'.upper()
        row_78F3F.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_78F3F.prop(bpy.context.scene, 'sna_multiple_method_cycles', text='Multiple (Light, Data, Cryptomatte are separate).', icon_value=0, emboss=True, index=0)


class SNA_PT_PICK_YOUR_PASSES_A4D89(bpy.types.Panel):
    bl_label = '1. Pick your passes.'
    bl_idname = 'SNA_PT_PICK_YOUR_PASSES_A4D89'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'
    bl_order = 2
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = 'SNA_PT_EXR_TO_NUKE_2969F'
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not ((not (bpy.context.engine == 'CYCLES')))

    def draw_header(self, context):
        layout = self.layout

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
        op = row_1AFB2.operator('sna.op_fast_selection_f9fd6', text='Fast Selection', icon_value=157, emboss=True, depress=False)
        layout.label(text='Data', icon_value=0)
        if hasattr(bpy.types,"CYCLES_RENDER_PT_passes_data"):
            if not hasattr(bpy.types.CYCLES_RENDER_PT_passes_data, "poll") or bpy.types.CYCLES_RENDER_PT_passes_data.poll(context):
                bpy.types.CYCLES_RENDER_PT_passes_data.draw(self, context)
            else:
                layout.label(text="Can't display this panel here!", icon="ERROR")
        else:
            layout.label(text="Can't display this panel!", icon="ERROR")
        layout.label(text='Light', icon_value=0)
        if hasattr(bpy.types,"CYCLES_RENDER_PT_passes_light"):
            if not hasattr(bpy.types.CYCLES_RENDER_PT_passes_light, "poll") or bpy.types.CYCLES_RENDER_PT_passes_light.poll(context):
                bpy.types.CYCLES_RENDER_PT_passes_light.draw(self, context)
            else:
                layout.label(text="Can't display this panel here!", icon="ERROR")
        else:
            layout.label(text="Can't display this panel!", icon="ERROR")
        layout.label(text='Cryptomatte', icon_value=0)
        if hasattr(bpy.types,"CYCLES_RENDER_PT_passes_crypto"):
            if not hasattr(bpy.types.CYCLES_RENDER_PT_passes_crypto, "poll") or bpy.types.CYCLES_RENDER_PT_passes_crypto.poll(context):
                bpy.types.CYCLES_RENDER_PT_passes_crypto.draw(self, context)
            else:
                layout.label(text="Can't display this panel here!", icon="ERROR")
        else:
            layout.label(text="Can't display this panel!", icon="ERROR")


class SNA_PT_OUTPUT_268FC(bpy.types.Panel):
    bl_label = '3. Output.'
    bl_idname = 'SNA_PT_OUTPUT_268FC'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'
    bl_order = 4
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = 'SNA_PT_EXR_TO_NUKE_2969F'
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not ((bpy.context.engine == 'CYCLES'))

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        if bpy.context.scene.sna_single_method_eevee:
            layout.label(text='Path', icon_value=0)
            layout.prop(bpy.data.scenes['Scene'].node_tree.nodes['File_Output_EXR'], 'base_path', text='', icon_value=0, emboss=True)
        else:
            if bpy.context.scene.sna_multiple_method_eevee:
                col_38856 = layout.column(heading='', align=False)
                col_38856.alert = False
                col_38856.enabled = True
                col_38856.active = True
                col_38856.use_property_split = False
                col_38856.use_property_decorate = False
                col_38856.scale_x = 1.0
                col_38856.scale_y = 1.0
                col_38856.alignment = 'Expand'.upper()
                col_38856.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
                col_38856.label(text='Light:', icon_value=0)
                col_38856.prop(bpy.data.scenes['Scene'].node_tree.nodes['Light_exr'], 'base_path', text='', icon_value=0, emboss=True)
                col_38856.label(text='Data:', icon_value=0)
                col_38856.prop(bpy.data.scenes['Scene'].node_tree.nodes['Data_exr'], 'base_path', text='', icon_value=0, emboss=True)
                col_38856.label(text='Cryptomatte:', icon_value=0)
                col_38856.prop(bpy.data.scenes['Scene'].node_tree.nodes['Cryptomatte_exr'], 'base_path', text='', icon_value=0, emboss=True)
            else:
                layout.label(text='You have to select a method.', icon_value=0)


class SNA_PT_SELECT_METHOD_49D4E(bpy.types.Panel):
    bl_label = '2. Select method.'
    bl_idname = 'SNA_PT_SELECT_METHOD_49D4E'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'
    bl_order = 3
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = 'SNA_PT_EXR_TO_NUKE_2969F'
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not ((bpy.context.engine == 'CYCLES'))

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        row_48AF2 = layout.row(heading='', align=False)
        row_48AF2.alert = False
        row_48AF2.enabled = (not bpy.context.scene.sna_multiple_method_eevee)
        row_48AF2.active = True
        row_48AF2.use_property_split = False
        row_48AF2.use_property_decorate = False
        row_48AF2.scale_x = 1.0
        row_48AF2.scale_y = 1.0
        row_48AF2.alignment = 'Expand'.upper()
        row_48AF2.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_48AF2.prop(bpy.context.scene, 'sna_single_method_eevee', text='Single (Everything in an exr).', icon_value=0, emboss=True, toggle=False, index=0)
        row_F2AE3 = layout.row(heading='', align=False)
        row_F2AE3.alert = False
        row_F2AE3.enabled = (not bpy.context.scene.sna_single_method_eevee)
        row_F2AE3.active = True
        row_F2AE3.use_property_split = False
        row_F2AE3.use_property_decorate = False
        row_F2AE3.scale_x = 1.0
        row_F2AE3.scale_y = 1.0
        row_F2AE3.alignment = 'Expand'.upper()
        row_F2AE3.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        row_F2AE3.prop(bpy.context.scene, 'sna_multiple_method_eevee', text='Multiple (Light, Data, Cryptomatte are separate).', icon_value=0, emboss=True, index=0)


class SNA_PT_PICK_YOUR_PASSES_63D9D(bpy.types.Panel):
    bl_label = '1. Pick your passes.'
    bl_idname = 'SNA_PT_PICK_YOUR_PASSES_63D9D'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'
    bl_order = 2
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = 'SNA_PT_EXR_TO_NUKE_2969F'
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not ((bpy.context.engine == 'CYCLES'))

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        row_7A84F = layout.row(heading='', align=False)
        row_7A84F.alert = False
        row_7A84F.enabled = True
        row_7A84F.active = True
        row_7A84F.use_property_split = True
        row_7A84F.use_property_decorate = False
        row_7A84F.scale_x = 1.4500000476837158
        row_7A84F.scale_y = 1.3600000143051147
        row_7A84F.alignment = 'Center'.upper()
        row_7A84F.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        op = row_7A84F.operator('sna.op_fast_selection_eevee_81e1a', text='Fast Selection', icon_value=157, emboss=True, depress=False)
        layout.label(text='Data', icon_value=0)
        if hasattr(bpy.types,"VIEWLAYER_PT_eevee_layer_passes_data"):
            if not hasattr(bpy.types.VIEWLAYER_PT_eevee_layer_passes_data, "poll") or bpy.types.VIEWLAYER_PT_eevee_layer_passes_data.poll(context):
                bpy.types.VIEWLAYER_PT_eevee_layer_passes_data.draw(self, context)
            else:
                layout.label(text="Can't display this panel here!", icon="ERROR")
        else:
            layout.label(text="Can't display this panel!", icon="ERROR")
        layout.label(text='Light', icon_value=0)
        if hasattr(bpy.types,"VIEWLAYER_PT_eevee_layer_passes_light"):
            if not hasattr(bpy.types.VIEWLAYER_PT_eevee_layer_passes_light, "poll") or bpy.types.VIEWLAYER_PT_eevee_layer_passes_light.poll(context):
                bpy.types.VIEWLAYER_PT_eevee_layer_passes_light.draw(self, context)
            else:
                layout.label(text="Can't display this panel here!", icon="ERROR")
        else:
            layout.label(text="Can't display this panel!", icon="ERROR")
        layout.label(text='Effects', icon_value=0)
        if hasattr(bpy.types,"VIEWLAYER_PT_eevee_layer_passes_effects"):
            if not hasattr(bpy.types.VIEWLAYER_PT_eevee_layer_passes_effects, "poll") or bpy.types.VIEWLAYER_PT_eevee_layer_passes_effects.poll(context):
                bpy.types.VIEWLAYER_PT_eevee_layer_passes_effects.draw(self, context)
            else:
                layout.label(text="Can't display this panel here!", icon="ERROR")
        else:
            layout.label(text="Can't display this panel!", icon="ERROR")
        layout.label(text='Cryptomatte', icon_value=0)
        if hasattr(bpy.types,"VIEWLAYER_PT_layer_passes_cryptomatte"):
            if not hasattr(bpy.types.VIEWLAYER_PT_layer_passes_cryptomatte, "poll") or bpy.types.VIEWLAYER_PT_layer_passes_cryptomatte.poll(context):
                bpy.types.VIEWLAYER_PT_layer_passes_cryptomatte.draw(self, context)
            else:
                layout.label(text="Can't display this panel here!", icon="ERROR")
        else:
            layout.label(text="Can't display this panel!", icon="ERROR")


class SNA_PT_RENDER_14C4D(bpy.types.Panel):
    bl_label = 'Render:'
    bl_idname = 'SNA_PT_RENDER_14C4D'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'
    bl_order = 0
    bl_parent_id = 'SNA_PT_OUTPUT_7AC16'
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not (((not bpy.context.scene.sna_single_method_cycles) == (not bpy.context.scene.sna_multiple_method_cycles)))

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        row_A62F6 = layout.row(heading='', align=True)
        row_A62F6.alert = False
        row_A62F6.enabled = True
        row_A62F6.active = True
        row_A62F6.use_property_split = False
        row_A62F6.use_property_decorate = False
        row_A62F6.scale_x = 1.0
        row_A62F6.scale_y = 1.25
        row_A62F6.alignment = 'Expand'.upper()
        row_A62F6.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        op = row_A62F6.operator('render.render', text='Render Image', icon_value=192, emboss=True, depress=False)
        op.write_still = True
        op = row_A62F6.operator('render.render', text='Render Animation', icon_value=191, emboss=True, depress=False)
        op.animation = True


class SNA_PT_RENDER_9EEAD(bpy.types.Panel):
    bl_label = 'Render:'
    bl_idname = 'SNA_PT_RENDER_9EEAD'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'
    bl_order = 0
    bl_parent_id = 'SNA_PT_OUTPUT_268FC'
    bl_ui_units_x=0

    @classmethod
    def poll(cls, context):
        return not (((not bpy.context.scene.sna_single_method_eevee) == (not bpy.context.scene.sna_multiple_method_eevee)))

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        row_3F5BD = layout.row(heading='', align=True)
        row_3F5BD.alert = False
        row_3F5BD.enabled = True
        row_3F5BD.active = True
        row_3F5BD.use_property_split = False
        row_3F5BD.use_property_decorate = False
        row_3F5BD.scale_x = 1.0
        row_3F5BD.scale_y = 1.25
        row_3F5BD.alignment = 'Expand'.upper()
        row_3F5BD.operator_context = "INVOKE_DEFAULT" if True else "EXEC_DEFAULT"
        op = row_3F5BD.operator('render.render', text='Render Image', icon_value=192, emboss=True, depress=False)
        op.write_still = True
        op = row_3F5BD.operator('render.render', text='Render Animation', icon_value=191, emboss=True, depress=False)
        op.animation = True


def register():
    global _icons
    _icons = bpy.utils.previews.new()
    bpy.types.Scene.sna_single_method_cycles = bpy.props.BoolProperty(name='single_method_cycles', description='', default=False, update=sna_update_sna_single_method_cycles_1F8F2)
    bpy.types.Scene.sna_multiple_method_cycles = bpy.props.BoolProperty(name='multiple_method_cycles', description='', default=False, update=sna_update_sna_multiple_method_cycles_15156)
    bpy.types.Scene.sna_multiple_method_eevee = bpy.props.BoolProperty(name='multiple_method_eevee', description='', default=False, update=sna_update_sna_multiple_method_eevee_349C5)
    bpy.types.Scene.sna_single_method_eevee = bpy.props.BoolProperty(name='single_method_eevee', description='', default=False, update=sna_update_sna_single_method_eevee_9C3E0)
    bpy.utils.register_class(SNA_OT_Op_Fast_Selection_F9Fd6)
    bpy.utils.register_class(SNA_OT_Op_Fast_Selection_Eevee_81E1A)
    bpy.utils.register_class(SNA_PT_EXR_TO_NUKE_2969F)
    bpy.utils.register_class(SNA_PT_OUTPUT_7AC16)
    bpy.utils.register_class(SNA_PT_SELECT_METHOD_6F4F2)
    bpy.utils.register_class(SNA_PT_PICK_YOUR_PASSES_A4D89)
    bpy.utils.register_class(SNA_PT_OUTPUT_268FC)
    bpy.utils.register_class(SNA_PT_SELECT_METHOD_49D4E)
    bpy.utils.register_class(SNA_PT_PICK_YOUR_PASSES_63D9D)
    bpy.utils.register_class(SNA_PT_RENDER_14C4D)
    bpy.utils.register_class(SNA_PT_RENDER_9EEAD)


def unregister():
    global _icons
    bpy.utils.previews.remove(_icons)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    for km, kmi in addon_keymaps.values():
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    del bpy.types.Scene.sna_single_method_eevee
    del bpy.types.Scene.sna_multiple_method_eevee
    del bpy.types.Scene.sna_multiple_method_cycles
    del bpy.types.Scene.sna_single_method_cycles
    bpy.utils.unregister_class(SNA_OT_Op_Fast_Selection_F9Fd6)
    bpy.utils.unregister_class(SNA_OT_Op_Fast_Selection_Eevee_81E1A)
    bpy.utils.unregister_class(SNA_PT_EXR_TO_NUKE_2969F)
    bpy.utils.unregister_class(SNA_PT_OUTPUT_7AC16)
    bpy.utils.unregister_class(SNA_PT_SELECT_METHOD_6F4F2)
    bpy.utils.unregister_class(SNA_PT_PICK_YOUR_PASSES_A4D89)
    bpy.utils.unregister_class(SNA_PT_OUTPUT_268FC)
    bpy.utils.unregister_class(SNA_PT_SELECT_METHOD_49D4E)
    bpy.utils.unregister_class(SNA_PT_PICK_YOUR_PASSES_63D9D)
    bpy.utils.unregister_class(SNA_PT_RENDER_14C4D)
    bpy.utils.unregister_class(SNA_PT_RENDER_9EEAD)
