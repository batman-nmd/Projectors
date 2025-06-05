import logging
import re
import bpy
from bpy.types import Operator

from .helper import get_projectors

logging.basicConfig(
    format='[Projectors Addon]: %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(name=__file__)


class PROJECTOR_OT_duplicate_projector(Operator):
    """Duplicate selected projector with all its children"""
    bl_idname = 'projector.duplicate'
    bl_label = 'Duplicate Projector'
    bl_options = {'REGISTER', 'UNDO'}
    
    # Propriétés pour le renommage complet
    search_text: bpy.props.StringProperty(
        name="Remplacer",
        description="Texte à rechercher dans les noms d'objets",
        default="",
        maxlen=64
    )
    
    replace_text: bpy.props.StringProperty(
        name="Par", 
        description="Nouveau texte de remplacement",
        default="",
        maxlen=64
    )
    offset_x: bpy.props.FloatProperty(
        name="Offset X",
        description="Décalage en X pour l'objet dupliqué",
        default=0.0,
        unit='LENGTH',
        precision=2
    )

    @classmethod
    def poll(cls, context):
        selected_projectors = get_projectors(context, only_selected=True)
        return len(selected_projectors) == 1

    def execute(self, context):
        # Import tardif pour éviter l'import circulaire
        from .projector import (update_throw_ratio, update_projected_texture, 
                               update_checker_color, update_lens_shift, update_power)
        
        selected_projectors = get_projectors(context, only_selected=True)
        if not selected_projectors:
            self.report({'WARNING'}, "No projector selected")
            return {'CANCELLED'}
        
        original_projector = selected_projectors[0]
        
        # Validation des champs de renommage
        if not self.search_text.strip():
            self.report({'ERROR'}, "Veuillez spécifier le texte à remplacer")
            return {'CANCELLED'}
        
        if not self.replace_text.strip():
            self.report({'ERROR'}, "Veuillez spécifier le texte de remplacement")
            return {'CANCELLED'}
        
        # NOUVEAU : Identifier l'objet parent à dupliquer
        # Utiliser l'objet actif s'il est différent du projecteur, sinon le parent du projecteur
        if context.active_object and context.active_object != original_projector:
            parent_to_duplicate = context.active_object
        elif original_projector.parent:
            parent_to_duplicate = original_projector.parent
        else:
            parent_to_duplicate = original_projector
        
        log.info(f"Duplicating parent object: {parent_to_duplicate.name}")
        
        # Sauvegarder la sélection actuelle
        original_selection = context.selected_objects.copy()
        original_active = context.view_layer.objects.active
        
        try:
            # Désélectionner tout
            bpy.ops.object.select_all(action='DESELECT')
            
            # NOUVEAU : Fonction pour sélectionner récursivement tous les enfants
            def select_hierarchy_recursive(obj):
                """Sélectionne un objet et tous ses enfants récursivement"""
                obj.select_set(True)
                for child in obj.children:
                    select_hierarchy_recursive(child)
            
            # Sélectionner l'objet parent ET TOUS ses enfants récursivement
            select_hierarchy_recursive(parent_to_duplicate)
            context.view_layer.objects.active = parent_to_duplicate
            
            # Dupliquer TOUTE la hiérarchie sélectionnée
            bpy.ops.object.duplicate(linked=False)  # linked=False pour une vraie duplication
            
            # L'objet parent dupliqué devient l'objet actif
            duplicated_parent = context.view_layer.objects.active
            
            # NOUVEAU : Appliquer l'offset à l'objet parent dupliqué
            duplicated_parent.location.x += self.offset_x
            
            # NOUVEAU : Renommer TOUTE la hiérarchie dupliquée selon les critères utilisateur
            def rename_hierarchy_recursive(obj, search_text, replace_text):
                """Renomme récursivement tous les objets contenant le texte recherché"""
                renamed_count = 0
                
                # D'abord essayer avec ".001" ajouté au texte de recherche
                search_with_suffix = f"{search_text}.001"

                if search_with_suffix in obj.name:
                    # Trouvé avec .001
                    old_name = obj.name
                    new_name = old_name.replace(search_with_suffix, replace_text)
                    obj.name = new_name
                    log.info(f"Renamed: '{old_name}' -> '{new_name}'")
                    renamed_count += 1
                elif search_text in obj.name:
                    # Pas trouvé avec .001, essayer sans
                    old_name = obj.name
                    new_name = old_name.replace(search_text, replace_text)
                    obj.name = new_name
                    log.info(f"Renamed: '{old_name}' -> '{new_name}'")
                    renamed_count += 1
                
                # Renommer récursivement tous les enfants
                for child in obj.children:
                    renamed_count += rename_hierarchy_recursive(child, search_text, replace_text)
                
                return renamed_count
            
            # Appliquer le renommage à toute la hiérarchie dupliquée
            renamed_count = rename_hierarchy_recursive(duplicated_parent, self.search_text.strip(), self.replace_text.strip())
            
            # Trouver le projecteur dans la hiérarchie dupliquée
            def find_projector_in_hierarchy(obj):
                """Trouve récursivement le projecteur dans la hiérarchie"""
                if obj.type == 'CAMERA' and hasattr(obj, 'proj_settings'):
                    return obj
                for child in obj.children:
                    result = find_projector_in_hierarchy(child)
                    if result:
                        return result
                return None
            
            # Trouver le projecteur renommé pour les opérations suivantes
            duplicated_projector = find_projector_in_hierarchy(duplicated_parent)
            
            if not duplicated_projector:
                # Si l'objet parent EST le projecteur
                if duplicated_parent.type == 'CAMERA' and hasattr(duplicated_parent, 'proj_settings'):
                    duplicated_projector = duplicated_parent
                else:
                    self.report({'ERROR'}, "Could not find projector in duplicated hierarchy")
                    return {'CANCELLED'}
                
            # Sélectionner l'objet parent dupliqué et le projecteur
            bpy.ops.object.select_all(action='DESELECT')
            duplicated_parent.select_set(True)
            duplicated_projector.select_set(True)
            context.view_layer.objects.active = duplicated_parent
            
            # Copier toutes les propriétés personnalisées du projecteur original
            for key in original_projector.keys():
                if key not in ['_RNA_UI']:  # Exclure les métadonnées Blender
                    duplicated_projector[key] = original_projector[key]
            
            # Copier les paramètres du projecteur (de manière sécurisée)
            original_settings = original_projector.proj_settings
            duplicated_settings = duplicated_projector.proj_settings
            
            # Copier toutes les propriétés des settings de manière sécurisée
            try:
                duplicated_settings.orientation = original_settings.orientation
            except:
                pass
                
            # Pour les enums de la base de données, ne pas les copier pour éviter les erreurs
            # Ils seront remis à 'NONE' par défaut
            
         
            
            self.report({'INFO'}, f"Duplicated and renamed {renamed_count} object(s)")
            log.info(f"Duplicated parent {parent_to_duplicate.name} and renamed {renamed_count} objects")
            
        except Exception as e:
            # Restaurer la sélection en cas d'erreur
            bpy.ops.object.select_all(action='DESELECT')
            for obj in original_selection:
                if obj.name in context.view_layer.objects:
                    obj.select_set(True)
            if original_active and original_active.name in context.view_layer.objects:
                context.view_layer.objects.active = original_active
            
            self.report({'ERROR'}, f"Duplication failed: {str(e)}")
            log.error(f"Duplication failed: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}

    def invoke(self, context, event):
        # Obtenir le projecteur sélectionné
        selected_projectors = get_projectors(context, only_selected=True)
        if not selected_projectors:
            self.report({'WARNING'}, "No projector selected")
            return {'CANCELLED'}
        
        original_projector = selected_projectors[0]
        
        # Identifier l'objet parent pour proposer les valeurs par défaut
        if context.active_object and context.active_object != original_projector:
            parent_obj = context.active_object
        elif original_projector.parent:
            parent_obj = original_projector.parent
        else:
            parent_obj = original_projector
        
        # Proposer des valeurs par défaut intelligentes
        parent_name = parent_obj.name
        
        # Détecter le pattern "Parent " et extraire ce qui vient après
        if parent_name.startswith("Parent "):
            # Extraire tout ce qui vient après "Parent "
            suffix = parent_name[7:]  # Enlever "Parent " (7 caractères)
            
            # Maintenant essayer de détecter un pattern numérique dans le suffixe
            match = re.search(r'(\D+)(\d+)', suffix)
            if match:
                base_name = match.group(1)  # Partie texte du suffixe
                number = int(match.group(2))  # Partie numérique
                
                self.search_text = suffix  # Le suffixe complet actuel
                self.replace_text = f"{base_name}{(number+1):03d}"  # Incrémenter le numéro
            else:
                # Pas de numéro détecté, juste proposer le suffixe + Copy
                self.search_text = suffix
                self.replace_text = f"{suffix}_Copy"
        else:
            # Pas de pattern "Parent " détecté, utiliser l'ancienne logique
            match = re.search(r'(\D+)(\d+)', parent_name)
            if match:
                base_name = match.group(1)  # Partie texte
                number = int(match.group(2))  # Partie numérique
                
                self.search_text = f"{base_name}{number:03d}"  # Format avec zéros
                self.replace_text = f"{base_name}{(number+1):03d}"  # Incrémenter
            else:
                # Pas de pattern numérique détecté, proposer des valeurs génériques
                self.search_text = parent_name
                self.replace_text = f"{parent_name}_Copy"
        
        # Ouvrir la boîte de dialogue
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        
        # Titre explicatif
        box = layout.box()
        box.label(text="Renommage de la hiérarchie :", icon='OUTLINER_DATA_FONT')
        
        # Champs de renommage
        box.prop(self, "search_text", text="Remplacer")
        box.prop(self, "replace_text", text="Par")
        
        # Champ d'offset
        layout.separator()
        layout.prop(self, "offset_x", text="Offset X")


def register():
    bpy.utils.register_class(PROJECTOR_OT_duplicate_projector)


def unregister():
    bpy.utils.unregister_class(PROJECTOR_OT_duplicate_projector)