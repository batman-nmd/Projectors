from .helper import get_projectors
from .projector import RESOLUTIONS, Textures, calculate_screen_size, calculate_lux, calculate_pixel_size

import bpy, math
from bpy.types import Panel, PropertyGroup, UIList, Operator

def get_custom_icons():
    from . import custom_icons
    return custom_icons

class PROJECTOR_OT_focus_selected(Operator):
    """Focus the 3D view on selected object (same as View Selected)"""
    bl_idname = 'projector.focus_selected'
    bl_label = 'Focus Selected'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.view3d.view_selected()
        return {'FINISHED'}

class PROJECTOR_OT_view_camera(Operator):
    """Switch to camera view (same as View Camera)"""
    bl_idname = 'projector.view_camera'
    bl_label = 'View Camera'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Utilise le premier projecteur pour la vue caméra
        projectors = get_projectors(context, only_selected=True)
        if projectors:
            # Sélectionner temporairement le premier projecteur pour la vue caméra
            bpy.context.scene.camera = projectors[0]
        bpy.ops.view3d.view_camera()
        return {'FINISHED'}

class PROJECTOR_OT_toggle_screen(Operator):
    """Toggle visibility of screen object in viewport"""
    bl_idname = 'projector.toggle_screen'
    bl_label = 'Toggle Screen Visibility'
    bl_options = {'REGISTER', 'UNDO'}

    def find_screen_object(self, obj):
        """Trouve récursivement un objet dont le nom contient 'écran' ou 'screen'"""
        if not obj:
            return None
        
        # Vérifier l'objet actuel
        name_lower = obj.name.lower()
        if 'écran' in name_lower or 'ecran' in name_lower or 'screen' in name_lower:
            return obj
        
        # Recherche récursive dans tous les enfants
        for child in obj.children:
            result = self.find_screen_object(child)
            if result:
                return result
        
        return None

    def execute(self, context):
        # Agir sur tous les objets parents des projecteurs sélectionnés
        projectors = get_projectors(context, only_selected=True)
        if not projectors:
            self.report({'WARNING'}, "No projectors found")
            return {'FINISHED'}
        
        # Obtenir tous les objets parents
        parent_objects = []
        for obj in context.selected_objects:
            # Chercher l'objet parent qui a déclenché la détection du projecteur
            projector_child = None
            for projector in projectors:
                if projector.parent == obj or obj == projector:
                    parent_objects.append(obj)
                    break
        
        # Si pas de parents trouvés, utiliser les objets sélectionnés
        if not parent_objects:
            parent_objects = context.selected_objects
        
        screens_toggled = 0
        for parent_obj in parent_objects:
            screen_obj = self.find_screen_object(parent_obj)
            if screen_obj:
                # Toggle "Show in viewports" 
                current_state = screen_obj.hide_get()
                screen_obj.hide_set(not current_state)
                screens_toggled += 1
        
        if screens_toggled > 0:
            self.report({'INFO'}, f"Toggled {screens_toggled} screen(s)")
        else:
            self.report({'WARNING'}, "No screen objects found")
        
        return {'FINISHED'}

class PROJECTOR_OT_toggle_light(Operator):
    """Toggle visibility and render of projector light"""
    bl_idname = 'projector.toggle_light'
    bl_label = 'Toggle Light Visibility'
    bl_options = {'REGISTER', 'UNDO'}

    def find_light_object(self, projector):
        """Trouve la lumière enfant de la caméra projecteur"""
        if not projector:
            return None
        
        # Recherche dans les enfants directs du projecteur
        for child in projector.children:
            if child.type == 'LIGHT':
                return child
        
        return None

    def execute(self, context):
        projectors = get_projectors(context, only_selected=True)
        if not projectors:
            self.report({'WARNING'}, "No projectors found")
            return {'FINISHED'}
        
        lights_toggled = 0
        for projector in projectors:
            light_obj = self.find_light_object(projector)
            if light_obj:
                # Toggle visibility in viewport ET disable in renders
                current_viewport = light_obj.hide_viewport
                
                # Synchroniser les deux (ON = visible partout, OFF = caché partout)
                new_state = not current_viewport
                light_obj.hide_viewport = new_state
                light_obj.hide_render = new_state
                lights_toggled += 1
        
        if lights_toggled > 0:
            self.report({'INFO'}, f"Toggled {lights_toggled} light(s)")
        else:
            self.report({'WARNING'}, "No lights found")
        
        return {'FINISHED'}


def get_screen_button_text(context):
    """Retourne le texte du bouton selon l'état des écrans"""
    projectors = get_projectors(context, only_selected=True)
    if not projectors:
        return "Screen"
    
    def find_screen_recursive(obj):
        if not obj:
            return None
        name_lower = obj.name.lower()
        if 'écran' in name_lower or 'screen' in name_lower:
            return obj
        for child in obj.children:
            result = find_screen_recursive(child)
            if result:
                return result
        return None
    
    # Compter les états des écrans
    screen_on = 0
    screen_off = 0
    
    for obj in context.selected_objects:
        screen_obj = find_screen_recursive(obj)
        if screen_obj:
            if screen_obj.hide_get():
                screen_off += 1
            else:
                screen_on += 1
    
    if screen_on > 0 and screen_off > 0:
        return "Screen Mixed"
    elif screen_off > 0:
        return "Screen OFF"
    elif screen_on > 0:
        return "Screen ON"
    else:
        return "Screen"

def get_light_button_text(context):
    """Retourne le texte du bouton selon l'état des lumières"""
    projectors = get_projectors(context, only_selected=True)
    if not projectors:
        return "Light"
    
    # Compter les états des lumières
    light_on = 0
    light_off = 0
    
    for projector in projectors:
        for child in projector.children:
            if child.type == 'LIGHT':
                if child.hide_viewport:
                    light_off += 1
                else:
                    light_on += 1
                break
    
    if light_on > 0 and light_off > 0:
        return "Light Mixed"
    elif light_off > 0:
        return "Light OFF"
    elif light_on > 0:
        return "Light ON"
    else:
        return "Light"

class PROJECTOR_OT_set_color(Operator):
    """Set projector color to a specific value"""
    bl_idname = 'projector.set_color'
    bl_label = 'Set Projector Color'
    bl_options = {'REGISTER', 'UNDO'}
    
    color: bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=3,
        min=0.0, max=1.0,
        default=(1.0, 1.0, 1.0)
    )
    
    @classmethod
    def poll(cls, context):
        selected_projectors = get_projectors(context, only_selected=True)
        if not selected_projectors:
            return False
        # Vérifier qu'au moins un projecteur utilise checker texture
        for projector in selected_projectors:
            if projector.proj_settings.projected_texture == Textures.CHECKER.value:
                return True
        return False

    def execute(self, context):
        from .projector import update_checker_color
        selected_projectors = get_projectors(context, only_selected=True)
        
        for projector in selected_projectors:
            if projector.proj_settings.projected_texture == Textures.CHECKER.value:
                projector.proj_settings.projected_color = self.color
                update_checker_color(projector.proj_settings, context)
        
        return {'FINISHED'}

class PROJECTOR_OT_reset_values(Operator):
    """Reset angles and shifts to zero"""
    bl_idname = 'projector.reset_values'
    bl_label = 'Reset Values'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        selected_projectors = get_projectors(context, only_selected=True)
        return len(selected_projectors) >= 1

    def execute(self, context):
        selected_projectors = get_projectors(context, only_selected=True)
        reset_count = 0
        
        for projector in selected_projectors:
            proj_settings = projector.proj_settings
            parent_obj = context.active_object if context.active_object != projector else projector.parent
            if not parent_obj:
                parent_obj = projector
            
            # Reset shifts
            proj_settings.h_shift = 0.0
            proj_settings.v_shift = 0.0
            
            # Reset angles if they exist
            if "VP_PAN" in parent_obj:
                parent_obj["VP_PAN"] = 0.0
            if "VP_TILT" in parent_obj:
                parent_obj["VP_TILT"] = 0.0
            if "VP_DOUBLE_PAN" in parent_obj:
                parent_obj["VP_DOUBLE_PAN"] = 0.0
            
            # Forcer la mise à jour
            parent_obj.update_tag()
            bpy.context.view_layer.update()
                
            reset_count += 1
        
        self.report({'INFO'}, f"Reset values for {reset_count} projector(s)")
        return {'FINISHED'}
class PROJECTOR_OT_export_csv(Operator):
    """Export projector data to CSV"""
    bl_idname = 'projector.export_csv'
    bl_label = 'Export to CSV'
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filename_ext = ".csv"
    
    filter_glob: bpy.props.StringProperty(
        default="*.csv",
        options={'HIDDEN'},
        maxlen=255,
    )
    
    def execute(self, context):
        import csv
        import os
        
        projectors = get_projectors(context, only_selected=True)
        if not projectors:
            self.report({'WARNING'}, "No projectors selected")
            return {'FINISHED'}
        
        # CSV headers (normalized in English)
        headers = ['vp_name', 'brand', 'model', 'lens', 'resolution', 'lumens', 
           'orientation', 'throw_ratio', 'pan', 'tilt', 'dpan', 'shift_h', 'shift_v', 
           'pixel_size', 'lux', 'screen_distance', 'image_width', 'image_height']
        
        rows = []
        
        for projector in projectors:
            proj_settings = projector.proj_settings
            
            # Get parent object for custom properties
            parent_obj = context.active_object if context.active_object != projector else projector.parent
            if not parent_obj:
                parent_obj = projector
            
            # Basic info avec récupération depuis custom properties
            vp_name = projector.name

            # Essayer de récupérer depuis les custom properties d'abord
            brand = projector.get("SELECTED_BRAND", "")
            model = projector.get("SELECTED_MODEL", "")
            lens = projector.get("SELECTED_LENS", "")

            # Fallback vers les enum si custom properties pas disponibles
            if not brand:
                try:
                    brand_val = proj_settings.projector_brand
                    if brand_val and brand_val != 'NONE':
                        brand = brand_val
                except:
                    pass

            resolution = proj_settings.resolution

            print(f"DEBUG CSV - {vp_name}: Brand='{brand}', Model='{model}', Lens='{lens}'")
            
            orientation = proj_settings.orientation
            throw_ratio = proj_settings.throw_ratio
            
            # Movement properties
            pan = parent_obj.get("VP_PAN", 0)
            tilt = parent_obj.get("VP_TILT", 0)
            dpan = parent_obj.get("VP_DOUBLE_PAN", 0)
            
            # Shift properties
            shift_h = proj_settings.h_shift
            shift_v = proj_settings.v_shift
            
            # Screen distance
            screen_distance = parent_obj.get("SCREEN_DISTANCE", 0)
            lumens_value = proj_settings.lumens
            
            # Calculated values
            pixel_size = ""
            lux = ""
            image_width = ""
            image_height = ""
            
            if screen_distance > 0:
                try:
                    # Calculate screen size
                    screen_w, screen_h = calculate_screen_size(throw_ratio, screen_distance, resolution)
                    image_width = f"{screen_w:.3f}"
                    image_height = f"{screen_h:.3f}"
                    
                    # Calculate lux
                    lux_value = calculate_lux(proj_settings.lumens, screen_w, screen_h)
                    lux = f"{lux_value:.0f}"
                    
                    # Calculate pixel size (taking only width for simplicity)
                    pixel_w_mm, pixel_h_mm = calculate_pixel_size(screen_w, screen_h, resolution)
                    pixel_size = f"{pixel_w_mm:.2f}"
                    
                except Exception as e:
                    pass
            
            # Create row
            # Create row avec formatage des valeurs numériques
            row = [vp_name, brand, model, lens, resolution, f"{lumens_value:.0f}", orientation, 
                f"{throw_ratio:.2f}", f"{math.degrees(pan):.0f}", f"{math.degrees(tilt):.0f}", f"{math.degrees(dpan):.0f}",
                f"{shift_h:.2f}", f"{shift_v:.2f}", f"{float(pixel_size):.2f}" if pixel_size else "", lux,
                f"{screen_distance:.2f}", f"{float(image_width):.2f}" if image_width else "", f"{float(image_height):.2f}" if image_height else ""]
            rows.append(row)
            
            # Special case: if orientation is "Paysage Dual", add duplicate row
            if orientation == 'LANDSCAPE DUAL':
                dual_row = row.copy()
                dual_row[0] = vp_name + " DUAL"  # Change name
                rows.append(dual_row)
        
        # Write CSV
        try:
            with open(self.filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(rows)
            
            self.report({'INFO'}, f"Exported {len(rows)} projector(s) to {os.path.basename(self.filepath)}")
            
        except Exception as e:
            self.report({'ERROR'}, f"Export failed: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        import os
        
        # Récupérer le chemin du fichier Blender actuel
        blend_filepath = bpy.data.filepath
        if blend_filepath:
            # Utiliser le même dossier que le fichier Blender
            blend_folder = os.path.dirname(blend_filepath)
            # Extraire le nom du fichier sans l'extension .blend
            blend_filename = os.path.basename(blend_filepath)
            base_name = os.path.splitext(blend_filename)[0]  # Supprime l'extension
            default_filename = f"{base_name}.csv"
        else:
            # Fichier non sauvegardé, utiliser le dossier Downloads
            blend_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            default_filename = "projectors_export.csv"
        
        # Chemin complet par défaut
        self.filepath = os.path.join(blend_folder, default_filename)
        
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class PROJECTOR_PT_projector_settings(Panel):
    bl_idname = 'OBJECT_PT_projector_n_panel'
    bl_label = 'Proj By Lotchi 25.2.1'
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Proj By Lotchi"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        # Afficher le logo en haut
        custom_icons = get_custom_icons()
        if custom_icons and "logo" in custom_icons:
            row = layout.row()
            row.alignment = 'CENTER'
            row.template_icon(icon_value=custom_icons["logo"].icon_id, scale=3.0)
            #layout.separator()

        # Boutons de base : New, Duplicate, Remove
        row = layout.row(align=True)
        row.operator('projector.create',
                     icon='ADD', text="New")
        
        # Bouton Dupliquer - seulement si exactement un projecteur est sélectionné
        selected_projectors = get_projectors(context, only_selected=True)
        if len(selected_projectors) == 1:
            row.operator('projector.duplicate',
                         icon='DUPLICATE', text="Duplicate")
        # Dans la ligne des boutons, après Duplicate
        if len(selected_projectors) == 1:
            row.operator('projector.mirror', icon='MOD_MIRROR', text="Mirror")
        
        row.operator('projector.delete',
                     text='Remove', icon='REMOVE')

        if context.scene.render.engine == 'BLENDER_EEVEE':
            box = layout.box()
            box.label(text='Image Projection only works in Cycles.', icon='ERROR')
            box.operator('projector.switch_to_cycles')

        selected_projectors = get_projectors(context, only_selected=True)
        if len(selected_projectors) >= 1:  # ← CHANGEMENT : >= au lieu de ==
            
            layout.separator()
            
            # Affichage du nombre de projecteurs sélectionnés
            info_box = layout.box()
            info_row = info_box.row()
            if len(selected_projectors) == 1:
                info_row.label(text=f"Editing: {selected_projectors[0].name}", icon='OUTLINER_OB_CAMERA')
            else:
                info_row.label(text=f"Editing: {len(selected_projectors)} projectors", icon='OUTLINER_OB_CAMERA')
            
            # Boutons Focus, POV, Screen et Light en dessous, côte à côte
            buttons_row = info_box.row(align=True)
            buttons_row.operator('projector.focus_selected', text="Focus", icon='ZOOM_SELECTED')
            buttons_row.operator('projector.view_camera', text="POV", icon='VIEW_CAMERA')
            screen_btn_text = get_screen_button_text(context)
            buttons_row.operator('projector.toggle_screen', text=screen_btn_text, icon='HIDE_OFF')
            light_btn_text = get_light_button_text(context)
            buttons_row.operator('projector.toggle_light', text=light_btn_text, icon='LIGHT')
            # Bouton Export en dessous
            export_row = info_box.row()
            export_row.operator('projector.export_csv', text="Export CSV", icon='EXPORT')
            
            # Boutons de couleurs de projection
            # colors_box = info_box.box()
            # colors_box.label(text="Projection Colors:", icon='COLOR')
            
            # # Première ligne : White, Red, Blue, Green
            # colors_row1 = colors_box.row(align=True)
            
            # white_op = colors_row1.operator('projector.set_color', text="WHI")
            # white_op.color = (1.0, 1.0, 1.0)  # White
            
            # red_op = colors_row1.operator('projector.set_color', text="RED")
            # red_op.color = (1.0, 0.0, 0.0)  # Red
            
            # blue_op = colors_row1.operator('projector.set_color', text="BLU")
            # blue_op.color = (0.0, 0.0, 1.0)  # Blue
            
            # green_op = colors_row1.operator('projector.set_color', text="GRE")
            # green_op.color = (0.0, 1.0, 0.0)  # Green
    
            
            # magenta_op = colors_row1.operator('projector.set_color', text="MAG")
            # magenta_op.color = (1.0, 0.0, 1.0)  # Magenta
            
            # yellow_op = colors_row1.operator('projector.set_color', text="YEL")
            # yellow_op.color = (1.0, 1.0, 0.0)  # Yellow
            
            # cyan_op = colors_row1.operator('projector.set_color', text="CYA")
            # cyan_op.color = (0.0, 1.0, 1.0)  # Cyan
            
            # # Espace pour équilibrer
            # colors_row1.operator('projector.change_color', text="?", icon='QUESTION')

            # === PROPRIÉTÉS - SEULEMENT SI UN SEUL PROJECTEUR ===
            if len(selected_projectors) == 1:
                projector = selected_projectors[0]
                proj_settings = projector.proj_settings
                parent_obj = context.active_object

                layout.label(text='Projector Settings:')
                box = layout.box()
                box.prop(proj_settings, 'orientation', text='Orientation')
                # Base de données projecteurs
                db_col = box.column(align=True)

                db_col.prop(proj_settings, 'projector_brand', text='Brand')
                db_col.prop(proj_settings, 'projector_model', text='Model') 
                db_col.prop(proj_settings, 'projector_lens', text='Lens')
                box.prop(proj_settings, 'power', text='Power')
                #box.prop(proj_settings, 'lumens', text='Lumens')
                box.prop(proj_settings, 'throw_ratio')
                
                res_row = box.row()
                res_row.prop(proj_settings, 'resolution',
                             text='Resolution', icon='PRESET')
                if proj_settings.projected_texture == Textures.CUSTOM_TEXTURE.value and proj_settings.use_custom_texture_res:
                    res_row.active = False
                    res_row.enabled = False
                else:
                    res_row.active = True
                    res_row.enabled = True

                # Vérification et affichage des custom properties
                if parent_obj and ("SCREEN_DISTANCE" in parent_obj or "VP_PAN" in parent_obj or "VP_TILT" in parent_obj or "VP_DOUBLE_PAN" in parent_obj):
                    
                    # Screen Distance
                    if "SCREEN_DISTANCE" in parent_obj:
                        box.prop(parent_obj, '["SCREEN_DISTANCE"]', text='Screen Distance')
                    
                    # VP Pan & Tilt
                    col = box.column(align=True)
                    if "VP_PAN" in parent_obj:
                        col.prop(parent_obj, '["VP_PAN"]', text='Pan')
                    if "VP_TILT" in parent_obj:
                        col.prop(parent_obj, '["VP_TILT"]', text='Tilt')
                    if "VP_DOUBLE_PAN" in parent_obj:
                        col.prop(parent_obj, '["VP_DOUBLE_PAN"]', text='DPan')
                
                # Lens Shift
                col = box.column(align=True)
                col.prop(proj_settings, 'h_shift', text='Horizontal Shift')
                col.separator()
                col.prop(proj_settings, 'v_shift', text='Vertical Shift')

                # Petit espace
                col.separator()

                # Reset button plus petit en largeur
                reset_row = col.row()
                reset_row.scale_x = 0.6
                reset_row.operator('projector.reset_values', text='Reset Values', icon='LOOP_BACK')
                
                # Screen Auto-Sizing
                layout.separator()
                auto_box = layout.box()

                auto_box.label(text="Projection infos")
                auto_box.operator('projector.auto_adjust_screen_size', 
                                  text="Adjust Screen Size", 
                                  icon='FULLSCREEN_ENTER')

                # Afficher les informations de calcul si disponible
                if parent_obj and "SCREEN_DISTANCE" in parent_obj:
                    try:
                        # Calculs de base
                        screen_w, screen_h = calculate_screen_size(proj_settings.throw_ratio, 
                                                                  parent_obj["SCREEN_DISTANCE"], 
                                                                  proj_settings.resolution)
                        
                        # Calcul des lux
                        lux = calculate_lux(proj_settings.lumens, screen_w, screen_h)
                        
                        # Calcul de la taille de pixel
                        pixel_w_mm, pixel_h_mm = calculate_pixel_size(screen_w, screen_h, proj_settings.resolution)
                        
                        # Affichage des informations avec espacement réduit
                        info_col = auto_box.column(align=True)  # align=True réduit l'espacement
                        info_col.scale_y = 0.8  # Facteur de réduction de l'espacement vertical
                        # Récupérer les informations du projecteur
                        brand = projector.get("SELECTED_BRAND", "")
                        model = projector.get("SELECTED_MODEL", "")
                        lens = projector.get("SELECTED_LENS", "")

                        # Ligne avec Brand, Model, Lens et shifts min/max
                        if brand and model and lens:
                            # Récupérer les shifts min/max
                            h_min = proj_settings.h_shift_min
                            h_max = proj_settings.h_shift_max
                            v_min = proj_settings.v_shift_min
                            v_max = proj_settings.v_shift_max
                            
                            # Construire le texte de la lentille (version courte)
                            lens_short = lens.split(' ')[0] if ' ' in lens else lens  # Prendre seulement le ratio
                            
                            info_col.label(text=f"{brand} {model} | {proj_settings.lumens:.0f} ANSI", icon='CAMERA_DATA')
                        
                        info_col.label(text=f"Lens: {lens_short} | H:{h_min:.0f}/{h_max:.0f} V:{v_min:.0f}/{v_max:.0f}", icon='LIGHT_AREA')
                        info_col.label(text=f"Distance: {parent_obj['SCREEN_DISTANCE']:.1f}m, TR: {proj_settings.throw_ratio:.2f}", icon='INFO')

                        # Calcul du ratio d'image
                        res_w, res_h = proj_settings.resolution.split('x')
                        image_ratio = float(res_w) / float(res_h)
                        
                        info_col.label(text=f"Screen: {screen_w:.2f}×{screen_h:.2f}m (Ratio: {image_ratio:.1f})", icon='MESH_PLANE')
                        info_col.label(text=f"Lux: {lux:.0f} lx", icon='LIGHT_SUN')
                        info_col.label(text=f"Pixel: {pixel_w_mm:.2f}mm", icon='GRID')
                        
                    except Exception as e:
                        # Fallback en cas d'erreur
                        auto_box.label(text="Calculation error", icon='ERROR')
                layout.prop(proj_settings,
                            'projected_texture', text='Project')
                # Pixel Grid TO DELETE ??
                #box.prop(proj_settings, 'show_pixel_grid')

                # Custom Texture
                if proj_settings.projected_texture == Textures.CUSTOM_TEXTURE.value:
                    box = layout.box()
                    box.prop(proj_settings, 'use_custom_texture_res')
                    node = get_projectors(context, only_selected=True)[
                        0].children[0].data.node_tree.nodes['Image Texture']
                    box.template_image(node, 'image', node.image_user, compact=False)
            
            # === MESSAGE POUR SÉLECTION MULTIPLE ===
            else:
                layout.separator()
                msg_box = layout.box()
                msg_box.label(text=f"{len(selected_projectors)} projectors selected", icon='INFO')
                msg_box.label(text="• Buttons affect all projectors")
                msg_box.label(text="• Select one projector to edit properties")

class PROJECTOR_PT_projected_color(Panel):
    bl_label = "Projected Color"
    bl_parent_id = "OBJECT_PT_projector_n_panel"
    bl_option = {'DEFAULT_CLOSED'}
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(self, context):
        """ Only show if projected texture is set to  'checker' AND only one projector selected."""
        selected_projectors = get_projectors(context, only_selected=True)
        if len(selected_projectors) != 1:  # Seulement pour un projecteur
            return False
        projector = selected_projectors[0]
        return projector.proj_settings.projected_texture == Textures.CHECKER.value

    def draw(self, context):
        projector = get_projectors(context, only_selected=True)[0]
        layout = self.layout
        layout.use_property_decorate = False
        col = layout.column()
        col.use_property_split = True
        col.prop(projector.proj_settings, 'projected_color', text='Color')
        col.operator('projector.change_color',
                     icon='MODIFIER_ON', text='Random Color')


def append_to_add_menu(self, context):
    self.layout.operator('projector.create',
                         text='Projector', icon='CAMERA_DATA')


def register():
    bpy.utils.register_class(PROJECTOR_OT_focus_selected)
    bpy.utils.register_class(PROJECTOR_OT_view_camera)
    bpy.utils.register_class(PROJECTOR_OT_toggle_screen)
    bpy.utils.register_class(PROJECTOR_OT_toggle_light)
    bpy.utils.register_class(PROJECTOR_PT_projector_settings)
    bpy.utils.register_class(PROJECTOR_PT_projected_color)
    bpy.utils.register_class(PROJECTOR_OT_export_csv)
    bpy.utils.register_class(PROJECTOR_OT_set_color)
    bpy.utils.register_class(PROJECTOR_OT_reset_values)
    # Register create  in the blender add menu.
    bpy.types.VIEW3D_MT_light_add.append(append_to_add_menu)


def unregister():
    # Register create in the blender add menu.
    bpy.types.VIEW3D_MT_light_add.remove(append_to_add_menu)
    bpy.utils.register_class(PROJECTOR_OT_set_color)
    bpy.utils.unregister_class(PROJECTOR_OT_reset_values)
    bpy.utils.unregister_class(PROJECTOR_OT_export_csv)
    bpy.utils.unregister_class(PROJECTOR_PT_projected_color)
    bpy.utils.unregister_class(PROJECTOR_PT_projector_settings)
    bpy.utils.unregister_class(PROJECTOR_OT_focus_selected)
    bpy.utils.unregister_class(PROJECTOR_OT_view_camera)
    bpy.utils.unregister_class(PROJECTOR_OT_toggle_screen) 
    bpy.utils.unregister_class(PROJECTOR_OT_toggle_light)