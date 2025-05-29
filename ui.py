from .helper import get_projectors
from .projector import RESOLUTIONS, Textures

import bpy
from bpy.types import Panel, PropertyGroup, UIList, Operator

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
        parent_obj = context.active_object
        screen_obj = self.find_screen_object(parent_obj)
        
        if screen_obj:
            # Toggle "Show in viewports" uniquement
            current_state = screen_obj.hide_get()
            screen_obj.hide_set(not current_state)
            
            status = "OFF" if screen_obj.hide_get() else "ON"
            self.report({'INFO'}, f"Screen {status}: {screen_obj.name}")
        else:
            self.report({'WARNING'}, "No screen object found (name should contain 'écran' or 'ecran' or 'screen')")
        
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
            self.report({'WARNING'}, "No projector found")
            return {'FINISHED'}
        
        projector = projectors[0]
        light_obj = self.find_light_object(projector)
        
        if light_obj:
            # Toggle visibility in viewport ET disable in renders
            current_viewport = light_obj.hide_viewport
            current_render = light_obj.hide_render
            
            # Synchroniser les deux (ON = visible partout, OFF = caché partout)
            new_state = not current_viewport
            light_obj.hide_viewport = new_state
            light_obj.hide_render = new_state
            
            status = "OFF" if new_state else "ON"
            self.report({'INFO'}, f"Light {status}: {light_obj.name}")
        else:
            self.report({'WARNING'}, "No light object found in projector children")
        
        return {'FINISHED'}

def get_screen_button_text(context):
    """Retourne le texte du bouton selon l'état de l'écran"""
    
    def find_screen_recursive(obj):
        """Recherche récursive d'un objet écran"""
        if not obj:
            return None
        
        # Vérifier l'objet actuel
        name_lower = obj.name.lower()
        if 'écran' in name_lower or 'screen' in name_lower:
            return obj
        
        # Recherche dans tous les enfants
        for child in obj.children:
            result = find_screen_recursive(child)
            if result:
                return result
        
        return None
    
    parent_obj = context.active_object
    screen_obj = find_screen_recursive(parent_obj)
    
    if screen_obj:
        return "Screen OFF" if screen_obj.hide_get() else "Screen ON"
    else:
        return "Screen"

def get_light_button_text(context):
    """Retourne le texte du bouton selon l'état de la lumière"""
    projectors = get_projectors(context, only_selected=True)
    if not projectors:
        return "Light"
    
    projector = projectors[0]
    
    # Trouver la lumière enfant
    for child in projector.children:
        if child.type == 'LIGHT':
            return "Light OFF" if child.hide_viewport else "Light ON"
    
    return "Light"
class PROJECTOR_PT_projector_settings(Panel):
    bl_idname = 'OBJECT_PT_projector_n_panel'
    bl_label = 'Proj By Lotchi'
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Proj By Lotchi"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row(align=True)
        row.operator('projector.create',
                     icon='ADD', text="New")
        row.operator('projector.delete',
                     text='Remove', icon='REMOVE')

        if context.scene.render.engine == 'BLENDER_EEVEE':
            box = layout.box()
            box.label(text='Image Projection only works in Cycles.', icon='ERROR')
            box.operator('projector.switch_to_cycles')

        selected_projectors = get_projectors(context, only_selected=True)
        if len(selected_projectors) == 1:
            projector = selected_projectors[0]
            proj_settings = projector.proj_settings
            parent_obj = context.active_object

            layout.separator()
            
            # Afficher le nom de la caméra projecteur en cours de gestion
            info_box = layout.box()
            info_row = info_box.row()
            info_row.label(text=f"Editing: {projector.name}", icon='OUTLINER_OB_CAMERA')
            # Boutons Focus, POV, Screen et Light en dessous, côte à côte
            buttons_row = info_box.row(align=True)
            buttons_row.operator('projector.focus_selected', text="Focus", icon='ZOOM_SELECTED')
            buttons_row.operator('projector.view_camera', text="POV", icon='VIEW_CAMERA')
            screen_btn_text = get_screen_button_text(context)
            buttons_row.operator('projector.toggle_screen', text=screen_btn_text, icon='HIDE_OFF')
            light_btn_text = get_light_button_text(context)
            buttons_row.operator('projector.toggle_light', text=light_btn_text, icon='LIGHT')

            layout.label(text='Projector Settings:')
            box = layout.box()
            box.prop(proj_settings, 'throw_ratio')
            box.prop(proj_settings, 'power', text='Power')
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
            col.prop(proj_settings,
                     'h_shift', text='Horizontal Shift')
            col.prop(proj_settings, 'v_shift', text='Vertical Shift')
            layout.prop(proj_settings,
                        'projected_texture', text='Project')
            # Pixel Grid
            box.prop(proj_settings, 'show_pixel_grid')

            # Custom Texture
            if proj_settings.projected_texture == Textures.CUSTOM_TEXTURE.value:
                box = layout.box()
                box.prop(proj_settings, 'use_custom_texture_res')
                node = get_projectors(context, only_selected=True)[
                    0].children[0].data.node_tree.nodes['Image Texture']
                box.template_image(node, 'image', node.image_user, compact=False)

class PROJECTOR_PT_projected_color(Panel):
    bl_label = "Projected Color"
    bl_parent_id = "OBJECT_PT_projector_n_panel"
    bl_option = {'DEFAULT_CLOSED'}
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(self, context):
        """ Only show if projected texture is set to  'checker'."""
        projector = context.object
        return bool(get_projectors(context, only_selected=True)) and projector.proj_settings.projected_texture == Textures.CHECKER.value

    def draw(self, context):
        projector = context.object
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
    # Register create  in the blender add menu.
    bpy.types.VIEW3D_MT_light_add.append(append_to_add_menu)


def unregister():
    # Register create in the blender add menu.
    bpy.types.VIEW3D_MT_light_add.remove(append_to_add_menu)
    bpy.utils.unregister_class(PROJECTOR_PT_projected_color)
    bpy.utils.unregister_class(PROJECTOR_PT_projector_settings)
    bpy.utils.unregister_class(PROJECTOR_OT_focus_selected)
    bpy.utils.unregister_class(PROJECTOR_OT_view_camera)
    bpy.utils.unregister_class(PROJECTOR_OT_toggle_screen) 
    bpy.utils.unregister_class(PROJECTOR_OT_toggle_light)
