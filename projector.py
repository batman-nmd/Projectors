import logging
import math
import os

from enum import Enum
import bpy
from bpy.types import Operator

from .helper import (ADDON_ID, auto_offset,
                     get_projectors, get_projector, random_color)

from .projector_database import get_brands, get_models, get_lenses, update_projector_brand, update_projector_model

logging.basicConfig(
    format='[Projectors Addon]: %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(name=__file__)

def calculate_screen_size(throw_ratio, screen_distance, resolution):
    """
    Calcule la taille de l'écran selon throw ratio et distance
    """
    # Largeur image = distance / throw_ratio
    screen_width = screen_distance / throw_ratio
    
    # Hauteur selon aspect ratio de la résolution
    res_w, res_h = resolution.split('x')
    aspect_ratio = float(res_w) / float(res_h)
    screen_height = screen_width / aspect_ratio
    
    return screen_width, screen_height

def calculate_lux(power_lumens_ansi, screen_width, screen_height):
    """
    Calcule les lux sur l'écran
    Lux = Lumens ANSI / Surface_écran_m²
    """
    surface_m2 = (screen_width * screen_height)
    if surface_m2 > 0:
        return power_lumens_ansi / surface_m2
    return 0

def calculate_pixel_size(screen_width, screen_height, resolution):
    """
    Calcule la taille physique d'un pixel sur l'écran
    """
    res_w, res_h = resolution.split('x')
    pixel_width_m = screen_width / float(res_w)
    pixel_height_m = screen_height / float(res_h)
    
    # Convertir en millimètres
    pixel_width_mm = pixel_width_m * 1000
    pixel_height_mm = pixel_height_m * 1000
    
    return pixel_width_mm, pixel_height_mm

def find_screen_object_recursive(obj):
    """Trouve récursivement un objet dont le nom contient 'écran' ou 'screen'"""
    if not obj:
        return None
    
    # Vérifier l'objet actuel
    name_lower = obj.name.lower()
    if 'écran' in name_lower or 'ecran' in name_lower or 'screen' in name_lower:
        return obj
    
    # Recherche récursive dans tous les enfants
    for child in obj.children:
        result = find_screen_object_recursive(child)
        if result:
            return result
    
    return None

def find_dual_object_recursive(obj):
    """Trouve récursivement un objet dont le nom contient 'dual'"""
    if not obj:
        return None
    
    # Vérifier l'objet actuel
    name_lower = obj.name.lower()
    if 'dual' in name_lower:
        return obj
    
    # Recherche récursive dans tous les enfants
    for child in obj.children:
        result = find_dual_object_recursive(child)
        if result:
            return result
    
    return None

def update_orientation(proj_settings, context):
    """
    Met à jour la visibilité des objets selon l'orientation
    """
    projector = get_projector(context)
    
    # Chercher l'objet parent qui pourrait contenir l'objet dual
    parent_obj = context.active_object if context.active_object != projector else projector.parent
    if not parent_obj:
        parent_obj = projector
    
    # Trouver l'objet dual
    dual_obj = find_dual_object_recursive(parent_obj)
    if not dual_obj:
        dual_obj = find_dual_object_recursive(projector)
    
    if dual_obj:
        if proj_settings.orientation == 'LANDSCAPE DUAL':
            # Afficher l'objet dual (viewport ET rendu)
            dual_obj.hide_set(False)
            dual_obj.hide_render = False
            log.info(f"Dual object {dual_obj.name} made visible")
        else:
            # Cacher l'objet dual (viewport ET rendu)
            dual_obj.hide_set(True)
            dual_obj.hide_render = True
            log.info(f"Dual object {dual_obj.name} hidden")

def update_projector_model_local(proj_settings, context):
    """Version locale de update_projector_model"""
    from .projector_database import PROJECTOR_DATABASE
    
    proj_settings.projector_lens = 'NONE'
    
    brand = proj_settings.projector_brand
    model = proj_settings.projector_model
    
    print(f"LOCAL DEBUG: Brand: {brand}, Model: {model}")
    
    if (brand in PROJECTOR_DATABASE and 
        model in PROJECTOR_DATABASE[brand]):
        
        first_lens = next(iter(PROJECTOR_DATABASE[brand][model].values()))
        new_lumens = first_lens['ansi_lumens']
        proj_settings.lumens = new_lumens
        print(f"LOCAL DEBUG: Lumens set to {new_lumens}")
        
        # Force UI refresh
        bpy.context.area.tag_redraw() if bpy.context.area else None

def update_projector_lens_local(proj_settings, context):
    """Version locale de update_projector_lens"""
    from .projector_database import PROJECTOR_DATABASE, BARCO_SHIFT_COEFFICIENT
    
    brand = proj_settings.projector_brand
    model = proj_settings.projector_model
    lens = proj_settings.projector_lens
    
    print(f"LOCAL DEBUG LENS: Brand: {brand}, Model: {model}, Lens: {lens}")
    
    if (brand in PROJECTOR_DATABASE and 
        model in PROJECTOR_DATABASE[brand] and 
        lens in PROJECTOR_DATABASE[brand][model]):
        
        lens_data = PROJECTOR_DATABASE[brand][model][lens]
        
        # Mettre à jour SEULEMENT les lumens (pas les shift ranges qui n'existent pas)
        proj_settings.lumens = lens_data['ansi_lumens']
        print(f"LOCAL DEBUG LENS: Lumens set to {lens_data['ansi_lumens']}")
        
        # Force UI refresh
        bpy.context.area.tag_redraw() if bpy.context.area else None
    else:
        print(f"LOCAL DEBUG LENS: Brand/Model/Lens not found in database")
class Textures(Enum):
    CHECKER = 'checker_texture'
    COLOR_GRID = 'color_grid_texture'
    CUSTOM_TEXTURE = 'custom_texture'


RESOLUTIONS = [
    # 16:10 aspect ratio
    ('1280x800', 'WXGA (1280x800) 16:10', '', 1),
    ('1440x900', 'WXGA+ (1440x900) 16:10', '', 2),
    ('1920x1200', 'WUXGA (1920x1200) 16:10', '', 3),
    ('3840x2400', 'WQUXGA (3840x2400) 16:10', '', 4),
    # 16:9 aspect ratio
    ('1280x720', '720p (1280x720) 16:9', '', 5),
    ('1920x1080', '1080p (1920x1080) 16:9', '', 6),
    ('3840x2160', '4K Ultra HD (3840x2160) 16:9', '', 7),
    # 4:3 aspect ratio
    ('800x600', 'SVGA (800x600) 4:3', '', 8),
    ('1024x768', 'XGA (1024x768) 4:3', '', 9),
    ('1400x1050', 'SXGA+ (1400x1050) 4:3', '', 10),
    ('1600x1200', 'UXGA (1600x1200) 4:3', '', 11),
    # 17:9 aspect ratio
    ('4096x2160', 'Native 4K (4096x2160) 17:9', '', 12)
]

PROJECTED_OUTPUTS = [(Textures.CHECKER.value, 'Checker', '', 1),
                     (Textures.COLOR_GRID.value, 'Color Grid', '', 2),
                     (Textures.CUSTOM_TEXTURE.value, 'Custom Texture', '', 3)]


class PROJECTOR_OT_change_color_randomly(Operator):
    """ Randomly change the color of the projected checker texture."""
    bl_idname = 'projector.change_color'
    bl_label = 'Change color of projection checker texture'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(get_projectors(context, only_selected=True)) == 1

    def execute(self, context):
        projectors = get_projectors(context, only_selected=True)
        new_color = random_color(alpha=True)
        for projector in projectors:
            projector.proj_settings['projected_color'] = new_color[:-1]
            update_checker_color(projector.proj_settings, context)
        return {'FINISHED'}

class PROJECTOR_OT_auto_adjust_screen_size(Operator):
    """Automatically adjust screen size based on throw ratio and distance"""
    bl_idname = 'projector.auto_adjust_screen_size'
    bl_label = 'Auto Adjust Screen Size'
    bl_description = 'Automatically calculates and applies screen size based on throw ratio and screen distance'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        selected_projectors = get_projectors(context, only_selected=True)
        return len(selected_projectors) >= 1

    def execute(self, context):
        selected_projectors = get_projectors(context, only_selected=True)
        adjusted_screens = 0
        
        for projector in selected_projectors:
            # Obtenir les paramètres du projecteur
            proj_settings = projector.proj_settings
            throw_ratio = proj_settings.throw_ratio
            resolution = proj_settings.resolution
            
            # DEBUG : Afficher les objets et leurs propriétés
            print(f"DEBUG: Processing projector: {projector.name}")
            print(f"DEBUG: Projector parent: {projector.parent.name if projector.parent else 'None'}")
            print(f"DEBUG: Active object: {context.active_object.name if context.active_object else 'None'}")
            print(f"DEBUG: Number of selected projectors: {len(selected_projectors)}")
            
            # Vérifier où se trouve SCREEN_DISTANCE
            screen_distance_found = False
            if "SCREEN_DISTANCE" in projector:
                print(f"DEBUG: SCREEN_DISTANCE found in projector: {projector['SCREEN_DISTANCE']}")
                screen_distance_found = True
            if projector.parent and "SCREEN_DISTANCE" in projector.parent:
                print(f"DEBUG: SCREEN_DISTANCE found in parent: {projector.parent['SCREEN_DISTANCE']}")
                screen_distance_found = True
            if context.active_object and "SCREEN_DISTANCE" in context.active_object:
                print(f"DEBUG: SCREEN_DISTANCE found in active object: {context.active_object['SCREEN_DISTANCE']}")
                screen_distance_found = True
            
            if not screen_distance_found:
                print("DEBUG: SCREEN_DISTANCE not found anywhere!")
            
            # Chercher l'objet parent qui contient la distance écran
            parent_obj = None
            
            # En sélection INDIVIDUELLE : utiliser l'objet actif 
            if len(selected_projectors) == 1 and context.active_object and context.active_object != projector:
                parent_obj = context.active_object
                print(f"DEBUG: Using active object: {parent_obj.name}")
            # En MULTI-sélection OU si pas d'objet actif valide : utiliser le parent de CHAQUE projecteur
            elif projector.parent:
                parent_obj = projector.parent
                print(f"DEBUG: Using projector parent: {parent_obj.name}")
            # En dernier recours, le projecteur lui-même
            else:
                parent_obj = projector
                print(f"DEBUG: Using projector itself: {parent_obj.name}")
            
            # Vérifier si SCREEN_DISTANCE existe
            screen_distance = None
            if "SCREEN_DISTANCE" in parent_obj:
                screen_distance = parent_obj["SCREEN_DISTANCE"]
            elif "SCREEN_DISTANCE" in projector:
                screen_distance = projector["SCREEN_DISTANCE"]
            
            if screen_distance is None:
                self.report({'WARNING'}, f"No SCREEN_DISTANCE property found for {projector.name}")
                continue
            
            # Calculer la taille de l'écran
            try:
                screen_width, screen_height = calculate_screen_size(throw_ratio, screen_distance, resolution)
            except Exception as e:
                self.report({'ERROR'}, f"Error calculating screen size for {projector.name}: {str(e)}")
                continue
            
            # Trouver l'objet écran
            screen_obj = find_screen_object_recursive(parent_obj)
            if not screen_obj:
                # Chercher dans le projecteur lui-même
                screen_obj = find_screen_object_recursive(projector)
            
            if not screen_obj:
                self.report({'WARNING'}, f"No screen object found for {projector.name}")
                continue
            
            # Appliquer la nouvelle taille à l'écran
            if screen_obj.type == 'MESH':
                # Pour un mesh, on ajuste les dimensions
                screen_obj.scale[0] = screen_width  # Largeur
                screen_obj.scale[2] = screen_height  # Hauteur
                # Garder l'échelle Y (profondeur) inchangée
                
                adjusted_screens += 1
                
                log.info(f"Adjusted screen {screen_obj.name}: {screen_width:.2f}m x {screen_height:.2f}m "
                        f"(TR: {throw_ratio}, Dist: {screen_distance}m, Res: {resolution})")
            
            else:
                self.report({'WARNING'}, f"Screen object {screen_obj.name} is not a mesh")
        
        if adjusted_screens > 0:
            self.report({'INFO'}, f"Successfully adjusted {adjusted_screens} screen(s)")
        else:
            self.report({'WARNING'}, "No screens were adjusted")
        
        return {'FINISHED'}

def create_projector_textures():
    """ This function checks if the needed images exist and if not creates them. """
    name_template = '_proj.tex.{}'
    for res in RESOLUTIONS:
        img_name = name_template.format(res[0])
        w, h = res[0].split('x')
        if not bpy.data.images.get(img_name):
            log.debug(f'Create projection texture: {res}')
            bpy.ops.image.new(name=img_name,
                              width=int(w),
                              height=int(h),
                              color=(0.0, 0.0, 0.0, 1.0),
                              alpha=True,
                              generated_type='COLOR_GRID',
                              float=False)

        bpy.data.images[img_name].use_fake_user = True


def add_projector_node_tree_to_spot(spot):
    """
    This function turns a spot light into a projector.
    This is achieved through a texture on the spot light and some basic math.
    """

    spot.data.use_nodes = True
    root_tree = spot.data.node_tree
    root_tree.nodes.clear()

    node_group = bpy.data.node_groups.new('_Projector', 'ShaderNodeTree')

    # Create output sockets for the node group.
    if(bpy.app.version >= (4, 0)):
        node_group.interface.new_socket('texture vector',  in_out="OUTPUT", socket_type='NodeSocketVector')
        node_group.interface.new_socket('color', in_out="OUTPUT", socket_type='NodeSocketColor')
    else:
        output = node_group.outputs
        output.new('NodeSocketVector', 'texture vector')
        output.new('NodeSocketColor', 'color')

    # # Inside Group Node #
    # #####################

    # Hold important nodes inside a group node.
    group = spot.data.node_tree.nodes.new('ShaderNodeGroup')
    group.node_tree = node_group
    group.label = "!! Don't touch !!"

    nodes = group.node_tree.nodes
    tree = group.node_tree

    auto_pos = auto_offset()

    tex = nodes.new('ShaderNodeTexCoord')
    tex.location = auto_pos(200)

    geo = nodes.new('ShaderNodeNewGeometry')
    geo.location = auto_pos(0, -300)
    vec_transform = nodes.new('ShaderNodeVectorTransform')
    vec_transform.location = auto_pos(200)
    vec_transform.vector_type = 'NORMAL'

    map_1 = nodes.new('ShaderNodeMapping')
    map_1.vector_type = 'TEXTURE'
    # Flip the image horizontally and vertically to display it the intended way.
    if bpy.app.version < (2, 81):
        map_1.scale[0] = -1
        map_1.scale[1] = -1
    else:
        map_1.inputs[3].default_value[0] = -1
        map_1.inputs[3].default_value[1] = -1
    map_1.location = auto_pos(200)

    sep = nodes.new('ShaderNodeSeparateXYZ')
    sep.location = auto_pos(350)

    div_1 = nodes.new('ShaderNodeMath')
    div_1.operation = 'DIVIDE'
    div_1.name = ADDON_ID + 'div_01'
    div_1.location = auto_pos(200)

    div_2 = nodes.new('ShaderNodeMath')
    div_2.operation = 'DIVIDE'
    div_2.name = ADDON_ID + 'div_02'
    div_2.location = auto_pos(y=-200)

    com = nodes.new('ShaderNodeCombineXYZ')
    com.inputs['Z'].default_value = 1.0
    com.location = auto_pos(200)

    map_2 = nodes.new('ShaderNodeMapping')
    map_2.location = auto_pos(200)
    map_2.vector_type = 'TEXTURE'

    add = nodes.new('ShaderNodeMixRGB')
    add.blend_type = 'ADD'
    add.inputs[0].default_value = 1
    add.location = auto_pos(350)

    # Texture
    # a) Image
    img = nodes.new('ShaderNodeTexImage')
    img.extension = 'CLIP'
    img.location = auto_pos(200)

    # b) Generated checker texture.
    checker_tex = nodes.new('ShaderNodeTexChecker')
    # checker_tex.inputs['Color2'].default_value = random_color(alpha=True)
    checker_tex.inputs[3].default_value = 8
    checker_tex.inputs[1].default_value = (1, 1, 1, 1)
    checker_tex.location = auto_pos(y=-300)

    mix_rgb = nodes.new('ShaderNodeMixRGB')
    mix_rgb.name = 'Mix.001'
    mix_rgb.inputs[1].default_value = (0, 0, 0, 0)
    mix_rgb.location = auto_pos(200, y=-300)

    group_output_node = node_group.nodes.new('NodeGroupOutput')
    group_output_node.location = auto_pos(200)

    # # Root Nodes #
    # ##############
    auto_pos_root = auto_offset()
    # Image Texture
    user_texture = root_tree.nodes.new('ShaderNodeTexImage')
    user_texture.extension = 'CLIP'
    user_texture.label = 'Add your Image Texture or Movie here'
    user_texture.location = auto_pos_root(200, y=200)
    # Emission
    emission = root_tree.nodes.new('ShaderNodeEmission')
    emission.inputs['Strength'].default_value = 1
    emission.location = auto_pos_root(300)
    # Material Output
    output = root_tree.nodes.new('ShaderNodeOutputLight')
    output.location = auto_pos_root(200)

    # # LINK NODES #
    # ##############

    # Link inside group node
    if(bpy.app.version >= (4, 0)):
        tree.links.new(geo.outputs['Incoming'], vec_transform.inputs['Vector'])
        tree.links.new(vec_transform.outputs['Vector'], map_1.inputs['Vector'])
    else:
        tree.links.new(tex.outputs['Normal'], map_1.inputs['Vector'])
    tree.links.new(map_1.outputs['Vector'], sep.inputs['Vector'])

    tree.links.new(sep.outputs[0], div_1.inputs[0])  # X -> value0
    tree.links.new(sep.outputs[2], div_1.inputs[1])  # Z -> value1
    tree.links.new(sep.outputs[1], div_2.inputs[0])  # Y -> value0
    tree.links.new(sep.outputs[2], div_2.inputs[1])  # Z -> value1

    tree.links.new(div_1.outputs[0], com.inputs[0])
    tree.links.new(div_2.outputs[0], com.inputs[1])

    tree.links.new(com.outputs['Vector'], map_2.inputs['Vector'])

    # Textures
    # a) generated texture
    tree.links.new(map_2.outputs['Vector'], add.inputs['Color1'])
    tree.links.new(add.outputs['Color'], img.inputs['Vector'])
    tree.links.new(add.outputs['Color'], group_output_node.inputs[0])
    # b) checker texture
    tree.links.new(add.outputs['Color'], checker_tex.inputs['Vector'])
    tree.links.new(img.outputs['Alpha'], mix_rgb.inputs[0])
    tree.links.new(checker_tex.outputs['Color'], mix_rgb.inputs[2])

    # Link in root
    root_tree.links.new(group.outputs['texture vector'], user_texture.inputs['Vector'])
    root_tree.links.new(group.outputs['color'], emission.inputs['Color'])
    root_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])

    # Pixel Grid Setup
    pixel_grid_group = create_pixel_grid_node_group()
    pixel_grid_node = spot.data.node_tree.nodes.new('ShaderNodeGroup')
    pixel_grid_node.node_tree = pixel_grid_group
    pixel_grid_node.label = "Pixel Grid"
    pixel_grid_node.name = 'pixel_grid'
    loc = root_tree.nodes['Emission'].location
    pixel_grid_node.location = (loc[0], loc[1] - 150)

    root_tree.links.new(group.outputs[0], pixel_grid_node.inputs[1])
    root_tree.links.new(emission.outputs[0], pixel_grid_node.inputs[0])

def get_resolution(proj_settings, context):
    """ Find out what resolution is currently used and return it.
    Resolution from the dropdown or the resolution from the custom texture.
    """
    if proj_settings.use_custom_texture_res and proj_settings.projected_texture == Textures.CUSTOM_TEXTURE.value:
        projector = get_projector(context)
        root_tree = projector.children[0].data.node_tree
        image = root_tree.nodes['Image Texture'].image
        if image:
            w = image.size[0]
            h = image.size[1]
        else:
            w, h = 300, 300
    else:
        w, h = proj_settings.resolution.split('x')

    return float(w), float(h)


def update_throw_ratio(proj_settings, context):
    """
    Adjust some settings on a camera to achieve a throw ratio
    """
    projector = get_projector(context)
    # Update properties of the camera.
    throw_ratio = proj_settings.get('throw_ratio')
    distance = 1
    alpha = math.atan((distance/throw_ratio)*.5) * 2
    projector.data.lens_unit = 'FOV'
    projector.data.angle = alpha
    projector.data.sensor_width = 10
    projector.data.display_size = 1

    # Adjust Texture to fit new camera ###
    w, h = get_resolution(proj_settings, context)
    aspect_ratio = w/h
    inverted_aspect_ratio = 1/aspect_ratio

    # Projected Texture
    update_projected_texture(proj_settings, context)

    # Update spotlight properties.
    spot = projector.children[0]
    nodes = spot.data.node_tree.nodes['Group'].node_tree.nodes
    if bpy.app.version < (2, 81):
        nodes['Mapping.001'].scale[0] = 1 / throw_ratio
        nodes['Mapping.001'].scale[1] = 1 / throw_ratio * inverted_aspect_ratio
    else:
        nodes['Mapping.001'].inputs[3].default_value[0] = 1 / throw_ratio
        nodes['Mapping.001'].inputs[3].default_value[1] = 1 / \
            throw_ratio * inverted_aspect_ratio

    # Update lens shift because it depends on the throw ratio.
    update_lens_shift(proj_settings, context)

def update_lens_shift(proj_settings, context):
    """
    Apply the shift to the camera, texture, and screen position.
    """
    projector = get_projector(context)
    h_shift = proj_settings.get('h_shift', 0.0) / 100
    v_shift = proj_settings.get('v_shift', 0.0) / 100
    throw_ratio = proj_settings.get('throw_ratio')

    w, h = get_resolution(proj_settings, context)
    inverted_aspect_ratio = h/w

    # Update the properties of the camera.
    cam = projector
    cam.data.shift_x = h_shift
    cam.data.shift_y = v_shift * inverted_aspect_ratio

    # Update spotlight node setup.
    spot = projector.children[0]
    nodes = spot.data.node_tree.nodes['Group'].node_tree.nodes
    if bpy.app.version < (2, 81):
        nodes['Mapping.001'].translation[0] = h_shift / throw_ratio
        nodes['Mapping.001'].translation[1] = v_shift / throw_ratio * inverted_aspect_ratio
    else:
        nodes['Mapping.001'].inputs[1].default_value[0] = h_shift / throw_ratio
        nodes['Mapping.001'].inputs[1].default_value[1] = v_shift / throw_ratio * inverted_aspect_ratio

    # ===== Déplacer l'écran automatiquement =====
    
    # Chercher l'objet parent qui pourrait contenir l'écran
    parent_obj = context.active_object if context.active_object != projector else projector.parent
    if not parent_obj:
        parent_obj = projector
    
    # Trouver l'objet écran
    screen_obj = find_screen_object_recursive(parent_obj)
    if not screen_obj:
        screen_obj = find_screen_object_recursive(projector)
    
    if screen_obj:
        # Obtenir la distance à l'écran
        screen_distance = None
        if "SCREEN_DISTANCE" in parent_obj:
            screen_distance = parent_obj["SCREEN_DISTANCE"]
        elif "SCREEN_DISTANCE" in projector:
            screen_distance = projector["SCREEN_DISTANCE"]
        
        if screen_distance:
            # Calculer le déplacement physique de l'écran basé sur le lens shift
            try:
                screen_width, screen_height = calculate_screen_size(throw_ratio, screen_distance, proj_settings.resolution)
                
                # Le déplacement de l'écran dépend de l'orientation
                if proj_settings.orientation == 'PORTRAIT':
                    screen_offset_x = -v_shift * screen_height  # V devient X
                    screen_offset_z = -h_shift * screen_width   # H devient Z
                else:  # PAYSAGE
                    screen_offset_x = h_shift * screen_width   # X = largeur
                    screen_offset_z = v_shift * screen_height  # Z = hauteur
                
                # Appliquer le déplacement à l'écran
                if '_original_location' not in screen_obj:
                    # Sauvegarder la position originale la première fois
                    screen_obj['_original_location'] = list(screen_obj.location)
                
                # Récupérer la position originale sauvegardée
                original_loc = screen_obj['_original_location']
                
                # Appliquer le nouvel offset à partir de la position originale
                screen_obj.location[0] = original_loc[0] + screen_offset_x
                screen_obj.location[2] = original_loc[2] + screen_offset_z
                
                log.debug(f"Screen offset applied: X={screen_offset_x:.3f}m, Z={screen_offset_z:.3f}m")
                
            except Exception as e:
                log.warning(f"Could not calculate screen offset: {e}")

def update_resolution(proj_settings, context):
    projector = get_projector(context)
    nodes = projector.children[0].data.node_tree.nodes['Group'].node_tree.nodes
    # Change resolution image texture
    nodes['Image Texture'].image = bpy.data.images[f'_proj.tex.{proj_settings.resolution}']
    update_throw_ratio(proj_settings, context)
    update_pixel_grid(proj_settings, context)


def update_checker_color(proj_settings, context):
    # Update checker texture color
    nodes = get_projector(
        context).children[0].data.node_tree.nodes['Group'].node_tree.nodes
    c = proj_settings.projected_color
    nodes['Checker Texture'].inputs['Color2'].default_value = [c.r, c.g, c.b, 1]


def update_power(proj_settings, context):
    # Update spotlight power - convertir le pourcentage en intensité
    spot = get_projector(context).children[0]
    power_percentage = proj_settings["power"]
    actual_power = (power_percentage / 100.0) * 10000.0
    spot.data.energy = actual_power


def update_pixel_grid(proj_settings, context):
    """ Update the pixel grid. Meaning, make it visible by linking the right node and updating the resolution. """
    root_tree = get_projector(context).children[0].data.node_tree
    nodes = root_tree.nodes
    pixel_grid_nodes = nodes['pixel_grid'].node_tree.nodes
    width, height = get_resolution(proj_settings, context)
    pixel_grid_nodes['_width'].outputs[0].default_value = width
    pixel_grid_nodes['_height'].outputs[0].default_value = height
    if proj_settings.show_pixel_grid:
        root_tree.links.new(nodes['pixel_grid'].outputs[0], nodes['Light Output'].inputs[0])
    else:
        root_tree.links.new(nodes['Emission'].outputs[0], nodes['Light Output'].inputs[0])

    
def create_pixel_grid_node_group():
    node_group = bpy.data.node_groups.new(
        '_Projectors-Addon_PixelGrid', 'ShaderNodeTree')

    # Create input/output sockets for the node group.
    if(bpy.app.version >= (4, 0)):
        node_group.interface.new_socket('Shader', socket_type='NodeSocketShader')
        node_group.interface.new_socket('Vector', socket_type='NodeSocketVector')

        node_group.interface.new_socket('Shader', in_out='OUTPUT', socket_type='NodeSocketShader')
    else:
        inputs = node_group.inputs
        inputs.new('NodeSocketShader', 'Shader')
        inputs.new('NodeSocketVector', 'Vector')

        outputs = node_group.outputs
        outputs.new('NodeSocketShader', 'Shader')

    nodes = node_group.nodes

    auto_pos = auto_offset()

    group_input = nodes.new('NodeGroupInput')
    group_input.location = auto_pos(200)

    sepXYZ = nodes.new('ShaderNodeSeparateXYZ')
    sepXYZ.location = auto_pos(200)

    in_width = nodes.new('ShaderNodeValue')
    in_width.name = '_width'
    in_width.label = 'Width'
    in_width.location = auto_pos(100)

    in_height = nodes.new('ShaderNodeValue')
    in_height.name = '_height'
    in_height.label = 'Height'
    in_height.location = auto_pos(y=-200)

    mul1 = nodes.new('ShaderNodeMath')
    mul1.operation = 'MULTIPLY'
    mul1.location = auto_pos(100)

    mul2 = nodes.new('ShaderNodeMath')
    mul2.operation = 'MULTIPLY'
    mul2.location = auto_pos(y=-200)

    mod1 = nodes.new('ShaderNodeMath')
    mod1.operation = 'MODULO'
    mod1.inputs[1].default_value = 1
    mod1.location = auto_pos(100)

    mod2 = nodes.new('ShaderNodeMath')
    mod2.operation = 'MODULO'
    mod2.inputs[1].default_value = 1
    mod2.location = auto_pos(y=-200)

    col_ramp1 = nodes.new('ShaderNodeValToRGB')
    col_ramp1.color_ramp.elements[1].position = 0.025
    col_ramp1.color_ramp.interpolation = 'CONSTANT'
    col_ramp1.location = auto_pos(100)

    col_ramp2 = nodes.new('ShaderNodeValToRGB')
    col_ramp2.color_ramp.elements[1].position = 0.025
    col_ramp2.color_ramp.interpolation = 'CONSTANT'
    col_ramp2.location = auto_pos(y=-200)

    mix_rgb = nodes.new('ShaderNodeMixRGB')
    mix_rgb.use_clamp = True
    mix_rgb.blend_type = 'MULTIPLY'
    mix_rgb.inputs[0].default_value = 1
    mix_rgb.location = auto_pos(200)
    
    transparent = nodes.new('ShaderNodeBsdfTransparent')
    transparent.location = auto_pos(y=-200)

    mix_shader = nodes.new('ShaderNodeMixShader')
    mix_shader.location = auto_pos(100)

    group_output = nodes.new('NodeGroupOutput')
    group_output.location = auto_pos(100)
    
    # Link Nodes
    links = node_group.links

    links.new(group_input.outputs[0], mix_shader.inputs[2])
    links.new(group_input.outputs[1], sepXYZ.inputs[0])

    links.new(in_width.outputs[0], mul1.inputs[1])
    links.new(in_height.outputs[0], mul2.inputs[1])

    links.new(sepXYZ.outputs[0], mul1.inputs[0])
    links.new(sepXYZ.outputs[1], mul2.inputs[0])

    links.new(mul1.outputs[0], mod1.inputs[0])
    links.new(mul2.outputs[0], mod2.inputs[0])

    links.new(mod1.outputs[0], col_ramp1.inputs[0])
    links.new(mod2.outputs[0], col_ramp2.inputs[0])

    links.new(col_ramp1.outputs[0], mix_rgb.inputs[1])
    links.new(col_ramp2.outputs[0], mix_rgb.inputs[2])

    links.new(mix_rgb.outputs[0], mix_shader.inputs[0])
    links.new(transparent.outputs[0], mix_shader.inputs[1])

    links.new(mix_shader.outputs[0], group_output.inputs[0])

    return node_group
    

def create_projector(context):
    """
    Create a new projector composed out of a camera (parent obj) and a spotlight (child not intended for user interaction).
    The camera is the object intended for the user to manipulate and custom properties are stored there.
    The spotlight with a custom nodetree is responsible for actual projection of the texture.
    """
    create_projector_textures()
    log.debug('Creating projector.')

    # Create a camera and a spotlight
    # ### Spot Light ###
    bpy.ops.object.light_add(type='SPOT', location=(0, 0, 0))
    spot = context.object
    spot.name = 'Projector.Spot'
    spot.scale = (.01, .01, .01)
    spot.data.spot_size = math.pi - 0.001
    spot.data.spot_blend = 0
    spot.data.shadow_soft_size = 0.0
    spot.hide_select = True
    spot[ADDON_ID.format('spot')] = True
    spot.data.cycles.use_multiple_importance_sampling = False
    add_projector_node_tree_to_spot(spot)

    # ### Camera ###
    bpy.ops.object.camera_add(enter_editmode=False,
                              location=(0, 0, 0),
                              rotation=(0, 0, 0))
    cam = context.object
    cam.name = 'Projector'

    # Parent light to cam.
    spot.parent = cam

    # Move newly create projector (cam and spotlight) to 3D-Cursor position.
    cam.location = context.scene.cursor.location
    cam.rotation_euler = context.scene.cursor.rotation_euler
    return cam


def init_projector(proj_settings, context):
    # # Add custom properties to store projector settings on the camera obj.
    proj_settings.throw_ratio = 0.8
    proj_settings.power = 100.0
    proj_settings.lumens = 10000.0
    proj_settings.projected_texture = Textures.CHECKER.value
    proj_settings.h_shift = 0.0
    proj_settings.v_shift = 0.0
    proj_settings.projected_color = random_color()
    proj_settings.resolution = '1920x1200'
    proj_settings.use_custom_texture_res = True

    # Init Projector
    update_throw_ratio(proj_settings, context)
    update_projected_texture(proj_settings, context)
    update_resolution(proj_settings, context)
    update_checker_color(proj_settings, context)
    update_lens_shift(proj_settings, context)
    update_power(proj_settings, context)
    update_pixel_grid(proj_settings, context)


class PROJECTOR_OT_create_projector(Operator):
    """Create Projector"""
    bl_idname = 'projector.create'
    bl_label = 'Create a new Projector'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        projector = create_projector(context)
        init_projector(projector.proj_settings, context)
        return {'FINISHED'}


def update_projected_texture(proj_settings, context):
    """ Update the projected output source. """
    projector = get_projectors(context, only_selected=True)[0]
    root_tree = projector.children[0].data.node_tree
    group_tree = root_tree.nodes['Group'].node_tree
    group_output_node = group_tree.nodes['Group Output']
    group_node = root_tree.nodes['Group']
    emission_node = root_tree.nodes['Emission']

    # Switch between the three possible cases by relinking some nodes.
    case = proj_settings.projected_texture
    if case == Textures.CHECKER.value:
        mix_node = group_tree.nodes['Mix.001']
        group_tree.links.new(
            mix_node.outputs['Color'], group_output_node.inputs[1])
        root_tree.links.new(group_node.outputs[1], emission_node.inputs[0])
    elif case == Textures.COLOR_GRID.value:
        img_node = group_tree.nodes['Image Texture']
        group_tree.links.new(img_node.outputs[0], group_output_node.inputs[1])
        root_tree.links.new(group_node.outputs[1], emission_node.inputs[0])
    elif case == Textures.CUSTOM_TEXTURE.value:
        custom_tex_node = root_tree.nodes['Image Texture']
        root_tree.links.new(
            custom_tex_node.outputs[0], emission_node.inputs[0])


class PROJECTOR_OT_delete_projector(Operator):
    """Delete Projector"""
    bl_idname = 'projector.delete'
    bl_label = 'Delete Projector'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bool(get_projectors(context, only_selected=True))

    def execute(self, context):
        selected_projectors = get_projectors(context, only_selected=True)
        for projector in selected_projectors:
            for child in projector.children:
                bpy.data.objects.remove(child, do_unlink=True)
            else:
                bpy.data.objects.remove(projector, do_unlink=True)
        return {'FINISHED'}

def update_lumens(proj_settings, context):
    """Mettre à jour les calculs quand les lumens changent"""
    # Optionnel : déclencher une mise à jour des calculs de lux
    pass

class ProjectorSettings(bpy.types.PropertyGroup):
    orientation: bpy.props.EnumProperty(
        name="Orientation",
        description="Screen orientation",
        items=[
            ('LANDSCAPE', 'Paysage', 'Landscape orientation', 'LANDSCAPE', 0),
            ('LANDSCAPE DUAL', 'Paysage Dual', 'Landscape dual orientation', 'LANDSCAPE DUAL', 1),
            ('PORTRAIT', 'Portrait', 'Portrait orientation', 'PORTRAIT', 2)
        ],
        default='LANDSCAPE',
        update=update_orientation)
    projector_brand: bpy.props.EnumProperty(
        name="Brand",
        description="Projector brand", 
        items=get_brands,
        update=update_projector_brand)

    projector_model: bpy.props.EnumProperty(
        name="Model",
        description="Projector model",
        items=get_models,
        update=update_projector_model_local)

    projector_lens: bpy.props.EnumProperty(
        name="Lens",
        description="Projector lens/optic", 
        items=get_lenses,
        update=update_projector_lens_local)
    throw_ratio: bpy.props.FloatProperty(
        name="Throw Ratio",
        soft_min=0.4, soft_max=3,
        update=update_throw_ratio,
        precision=2,
        subtype='FACTOR')
    power: bpy.props.FloatProperty(
        name="Light Power",
        description="Light intensity percentage (0-100%)",
        default=100.0,
        soft_min=0, soft_max=100,
        precision=0,
        update=update_power,
        subtype='PERCENTAGE')
    lumens: bpy.props.FloatProperty(
    name="Projector Lumens",
    description="Projector brightness in ANSI lumens",
    default=10000.0,
    soft_min=0, soft_max=50000,
    precision=0,
    unit='NONE',
    update=update_lumens)
    resolution: bpy.props.EnumProperty(
        items=RESOLUTIONS,
        default='1920x1200',
        description="Select a Resolution for your Projector",
        update=update_resolution)
    use_custom_texture_res: bpy.props.BoolProperty(
        name="Let Image Define Projector Resolution",
        default=True,
        description="Use the resolution from the image as the projector resolution. Warning: After selecting a new image toggle this checkbox to update",
        update=update_throw_ratio)
    h_shift: bpy.props.FloatProperty(
        name="Horizontal Shift",
        description="Horizontal Lens Shift",
        soft_min=-50, soft_max=50,
        update=update_lens_shift,
        subtype='PERCENTAGE')
    v_shift: bpy.props.FloatProperty(
        name="Vertical Shift",
        description="Vertical Lens Shift",
        soft_min=-50, soft_max=50,
        update=update_lens_shift,
        subtype='PERCENTAGE')
    projected_color: bpy.props.FloatVectorProperty(
        subtype='COLOR',
        update=update_checker_color)
    projected_texture: bpy.props.EnumProperty(
        items=PROJECTED_OUTPUTS,
        default=Textures.CHECKER.value,
        description="What do you to project?",
        update=update_throw_ratio)
    show_pixel_grid: bpy.props.BoolProperty(
        name="Show Pixel Grid",
        description="When checked the image is divided into a pixel grid with the dimensions of the image resolution.",
        default=False,
        update=update_pixel_grid)


def register():
    bpy.utils.register_class(ProjectorSettings)
    bpy.utils.register_class(PROJECTOR_OT_create_projector)
    bpy.utils.register_class(PROJECTOR_OT_delete_projector)
    bpy.utils.register_class(PROJECTOR_OT_change_color_randomly)
    bpy.utils.register_class(PROJECTOR_OT_auto_adjust_screen_size)

    bpy.types.Object.proj_settings = bpy.props.PointerProperty(
        type=ProjectorSettings)


def unregister():
    
    bpy.utils.unregister_class(PROJECTOR_OT_change_color_randomly)
    bpy.utils.unregister_class(PROJECTOR_OT_delete_projector)
    bpy.utils.unregister_class(PROJECTOR_OT_create_projector)
    bpy.utils.unregister_class(ProjectorSettings)