import logging
import bpy
from bpy.types import Operator
import math

from .helper import get_projectors

logging.basicConfig(
    format='[Projectors Addon]: %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(name=__file__)


class PROJECTOR_OT_mirror_projector(Operator):
    """Mirror selected projector based on its orientation (Landscape/Portrait)"""
    bl_idname = 'projector.mirror'
    bl_label = 'Mirror Projector'
    bl_description = 'Apply mirror transformation to projector based on its orientation'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        selected_projectors = get_projectors(context, only_selected=True)
        return len(selected_projectors) == 1

    def execute(self, context):
        selected_projectors = get_projectors(context, only_selected=True)
        if not selected_projectors:
            self.report({'WARNING'}, "No projector selected")
            return {'CANCELLED'}
        
        projector = selected_projectors[0]
        
        # Déterminer l'orientation du projecteur
        orientation = projector.proj_settings.orientation
        
        # Identifier l'objet parent à traiter
        if context.active_object and context.active_object != projector:
            parent_obj = context.active_object
        elif projector.parent:
            parent_obj = projector.parent
        else:
            parent_obj = projector
        
        log.info(f"Mirroring projector {projector.name} in {orientation} orientation")
        log.info(f"Parent object: {parent_obj.name}")
        
        try:
            if orientation == 'PORTRAIT':
                self.apply_portrait_mirror(parent_obj, projector)
            elif orientation in ['LANDSCAPE', 'LANDSCAPE DUAL']:
                self.apply_landscape_mirror(parent_obj, projector)
            else:
                self.report({'WARNING'}, f"Unknown orientation: {orientation}")
                return {'CANCELLED'}
            
            # Mettre à jour la scène
            bpy.context.view_layer.update()
            
            self.report({'INFO'}, f"Mirror applied to {projector.name} ({orientation})")
            
        except Exception as e:
            self.report({'ERROR'}, f"Mirror failed: {str(e)}")
            log.error(f"Mirror failed: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

    def apply_portrait_mirror(self, parent_obj, projector):
        """Applique la symétrie pour un projecteur en Portrait"""
        log.info("Applying Portrait mirror logic")
        
        # 1. Traiter l'objet parent
        if "parent" in parent_obj.name.lower():
            log.info(f"Processing parent object: {parent_obj.name}")
            parent_obj.location.y *= -1
            log.info(f"Parent Y position changed to: {parent_obj.location.y}")
        
        # 2. Obtenir tous les enfants récursivement
        all_children = self.get_all_children(parent_obj)
        
        # 2. Traiter le Pan de l'UI (custom property VP_PAN)
        if "VP_PAN" in parent_obj:
            current_pan_rad = parent_obj["VP_PAN"]
            current_pan_deg = math.degrees(current_pan_rad)
            
            # Nouveau pan = 180 - pan actuel
            new_pan_deg = 180 - current_pan_deg
            new_pan_rad = math.radians(new_pan_deg)
            
            parent_obj["VP_PAN"] = new_pan_rad
            log.info(f"UI Pan changed: {current_pan_deg:.1f}° -> {new_pan_deg:.1f}°")
        
        # 3. Traiter chaque enfant selon ses critères
        for child in all_children:
            child_name = child.name.lower()
            
            # Règle pour les objets "pan" sans "/"
            if child_name.startswith("pan") and "/" not in child_name:
                log.info(f"Processing pan object: {child.name}")
                
                # Angle actuel en degrés
                current_angle_rad = child.rotation_euler.z
                current_angle_deg = current_angle_rad * 57.2958
                
                # Nouveau angle = 180 - angle actuel
                new_angle_deg = 180 - current_angle_deg
                new_angle_rad = new_angle_deg * 0.0174533
                
                child.rotation_euler.z = new_angle_rad
                log.info(f"Pan rotation changed: {current_angle_deg:.1f}° -> {new_angle_deg:.1f}°")
            
            # Règle pour les caméras "Projector"
            elif child_name.startswith("projector") and child.type == 'CAMERA':
                log.info(f"Processing projector camera: {child.name}")
                if hasattr(child, 'proj_settings'):
                    # Vertical shift * -1
                    child.proj_settings.v_shift *= -1
                    log.info(f"Projector v_shift changed to: {child.proj_settings.v_shift}")

    def apply_landscape_mirror(self, parent_obj, projector):
        """Applique la symétrie pour un projecteur en Paysage"""
        log.info("Applying Landscape mirror logic")
        
        # 1. Traiter l'objet parent - Position Y * -1
        if "parent" in parent_obj.name.lower():
            log.info(f"Processing parent object: {parent_obj.name}")
            parent_obj.location.y *= -1
            log.info(f"Parent Y position changed to: {parent_obj.location.y}")
        
        # 2. Traiter le Pan et Double Pan de l'UI (custom properties)
        if "VP_PAN" in parent_obj:
            current_pan_rad = parent_obj["VP_PAN"]
            current_pan_deg = math.degrees(current_pan_rad)
            
            # Pan = 180 - valeur actuelle
            new_pan_deg = 180 - current_pan_deg
            new_pan_rad = math.radians(new_pan_deg)
            
            parent_obj["VP_PAN"] = new_pan_rad
            log.info(f"UI Pan changed: {current_pan_deg:.1f}° -> {new_pan_deg:.1f}°")

        if "VP_DOUBLE_PAN" in parent_obj:
            current_dpan_rad = parent_obj["VP_DOUBLE_PAN"]
            current_dpan_deg = math.degrees(current_dpan_rad)
            
            # DPan = valeur actuelle * -1
            new_dpan_deg = -current_dpan_deg
            new_dpan_rad = math.radians(new_dpan_deg)
            
            parent_obj["VP_DOUBLE_PAN"] = new_dpan_rad
            log.info(f"UI Double Pan changed: {current_dpan_deg:.1f}° -> {new_dpan_deg:.1f}°")

        # Ne pas toucher VP_TILT (pas de traitement)
        
        # 3. Obtenir tous les enfants récursivement
        all_children = self.get_all_children(parent_obj)
        
        # 4. Traiter chaque enfant selon ses critères
        for child in all_children:
            child_name = child.name.lower()
            
            # Règle pour les caméras "Projector"
            if child_name.startswith("projector") and child.type == 'CAMERA':
                log.info(f"Processing projector camera: {child.name}")
                if hasattr(child, 'proj_settings'):
                    # Shift Horizontal * -1, ne pas toucher Vertical
                    child.proj_settings.h_shift *= -1
                    log.info(f"Projector h_shift changed to: {child.proj_settings.h_shift}")
    
    def get_all_children(self, obj):
        """Obtient tous les enfants récursivement"""
        children = []
        for child in obj.children:
            children.append(child)
            children.extend(self.get_all_children(child))
        return children


class PROJECTOR_OT_mirror_with_duplicate(Operator):
    """Duplicate and mirror selected projector"""
    bl_idname = 'projector.mirror_duplicate'
    bl_label = 'Duplicate & Mirror'
    bl_description = 'Duplicate the projector and apply mirror transformation'
    bl_options = {'REGISTER', 'UNDO'}
    
    # Propriété pour le nouveau nom
    new_name: bpy.props.StringProperty(
        name="Mirror Name",
        description="Name for the mirrored projector",
        default="",
        maxlen=64
    )
    
    original_name: bpy.props.StringProperty(
        name="Original Name",
        description="Name of the original projector",
        default="",
        options={'HIDDEN'}
    )

    @classmethod
    def poll(cls, context):
        selected_projectors = get_projectors(context, only_selected=True)
        return len(selected_projectors) == 1

    def execute(self, context):
        selected_projectors = get_projectors(context, only_selected=True)
        if not selected_projectors:
            self.report({'WARNING'}, "No projector selected")
            return {'CANCELLED'}
        
        # Validation du nouveau nom
        if not self.new_name.strip():
            self.report({'ERROR'}, "Please provide a name for the mirrored projector")
            return {'CANCELLED'}
        
        # D'abord dupliquer avec l'opérateur de duplication existant
        try:
            # Utiliser l'opérateur de duplication existant
            duplicate_op = bpy.ops.projector.duplicate('INVOKE_DEFAULT')
            
            # Note: Cette approche nécessiterait d'adapter l'opérateur duplicate
            # Pour l'instant, on fait une duplication simple
            
            # Identifier l'objet parent
            projector = selected_projectors[0]
            if context.active_object and context.active_object != projector:
                parent_obj = context.active_object
            elif projector.parent:
                parent_obj = projector.parent
            else:
                parent_obj = projector
            
            # Sélectionner toute la hiérarchie
            self.select_hierarchy_recursive(parent_obj)
            
            # Dupliquer
            bpy.ops.object.duplicate(linked=False)
            
            # L'objet parent dupliqué devient l'objet actif
            duplicated_parent = context.view_layer.objects.active
            
            # Appliquer l'offset
            duplicated_parent.location.x += 2.0
            
            # Trouver le projecteur dans la hiérarchie dupliquée
            duplicated_projector = self.find_projector_in_hierarchy(duplicated_parent)
            
            if duplicated_projector:
                # Renommer le projecteur
                duplicated_projector.name = f"Projector {self.new_name.strip()}"
                
                # Maintenant appliquer le mirror sur la hiérarchie dupliquée
                mirror_op = PROJECTOR_OT_mirror_projector()
                
                # Préparer le contexte pour l'opération mirror
                temp_context = context.copy()
                temp_context['selected_objects'] = [duplicated_projector]
                temp_context['active_object'] = duplicated_parent
                
                # Appliquer le mirror
                orientation = duplicated_projector.proj_settings.orientation
                if orientation == 'PORTRAIT':
                    mirror_op.apply_portrait_mirror(duplicated_parent, duplicated_projector)
                elif orientation in ['LANDSCAPE', 'LANDSCAPE DUAL']:
                    mirror_op.apply_landscape_mirror(duplicated_parent, duplicated_projector)
                
                bpy.context.view_layer.update()
                
                self.report({'INFO'}, f"Duplicated and mirrored as '{self.new_name}'")
            else:
                self.report({'ERROR'}, "Could not find projector in duplicated hierarchy")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Duplicate & Mirror failed: {str(e)}")
            log.error(f"Duplicate & Mirror failed: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

    def invoke(self, context, event):
        selected_projectors = get_projectors(context, only_selected=True)
        if not selected_projectors:
            self.report({'WARNING'}, "No projector selected")
            return {'CANCELLED'}
        
        projector = selected_projectors[0]
        
        # Identifier l'objet parent pour proposer son nom
        if context.active_object and context.active_object != projector:
            parent_obj = context.active_object
        elif projector.parent:
            parent_obj = projector.parent
        else:
            parent_obj = projector
            
        self.original_name = parent_obj.name
        
        # Proposer un nom par défaut avec suffixe "Mirror"
        base_name = parent_obj.name
        self.new_name = f"{base_name} Mirror"
        
        # Ouvrir la boîte de dialogue
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        
        # Afficher le nom original
        row = layout.row()
        row.label(text=f"Original: {self.original_name}", icon='GROUP')
        
        # Champ pour le nouveau nom
        layout.prop(self, "new_name", text="Mirror Name")

    def select_hierarchy_recursive(self, obj):
        """Sélectionne un objet et tous ses enfants récursivement"""
        obj.select_set(True)
        for child in obj.children:
            self.select_hierarchy_recursive(child)

    def find_projector_in_hierarchy(self, obj):
        """Trouve récursivement le projecteur dans la hiérarchie"""
        if obj.type == 'CAMERA' and hasattr(obj, 'proj_settings'):
            return obj
        for child in obj.children:
            result = self.find_projector_in_hierarchy(child)
            if result:
                return result
        return None


def register():
    bpy.utils.register_class(PROJECTOR_OT_mirror_projector)
    bpy.utils.register_class(PROJECTOR_OT_mirror_with_duplicate)


def unregister():
    bpy.utils.unregister_class(PROJECTOR_OT_mirror_projector)
    bpy.utils.unregister_class(PROJECTOR_OT_mirror_with_duplicate)