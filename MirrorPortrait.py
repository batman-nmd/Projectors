import bpy
import bmesh
from mathutils import Vector

def apply_symmetry_to_selection():
    """
    Applique une symétrie sur l'objet sélectionné et ses sous-objets
    selon des règles spécifiques de nommage.
    """
    
    # Vérifier qu'un objet est sélectionné
    if not bpy.context.active_object:
        print("Aucun objet sélectionné!")
        return
    
    # Obtenir l'objet parent sélectionné
    parent_obj = bpy.context.active_object
    
    # Traiter l'objet parent
    if "parent" in parent_obj.name.lower():
        print(f"Traitement de l'objet parent: {parent_obj.name}")
        # Position Y * -1
        parent_obj.location.y *= -1
        print(f"  Position Y modifiée: {parent_obj.location.y}")
    
    # Obtenir tous les enfants récursivement
    def get_all_children(obj):
        children = []
        for child in obj.children:
            children.append(child)
            children.extend(get_all_children(child))
        return children
    
    all_children = get_all_children(parent_obj)
    
    # Traiter chaque enfant selon ses critères
    for child in all_children:
        child_name = child.name.lower()
        
        # Règle pour les objets "pan" sans "/"
        if child_name.startswith("pan") and "/" not in child_name:
            print(f"Traitement de l'objet pan: {child.name}")
            
            # Debug : afficher toutes les rotations pour comprendre
            print(f"  Rotation parent (radians): X={parent_obj.rotation_euler.x:.3f}, Y={parent_obj.rotation_euler.y:.3f}, Z={parent_obj.rotation_euler.z:.3f}")
            print(f"  Rotation parent (degrés): X={parent_obj.rotation_euler.x * 57.2958:.1f}°, Y={parent_obj.rotation_euler.y * 57.2958:.1f}°, Z={parent_obj.rotation_euler.z * 57.2958:.1f}°")
            
            print(f"  Rotation actuelle pan (radians): X={child.rotation_euler.x:.3f}, Y={child.rotation_euler.y:.3f}, Z={child.rotation_euler.z:.3f}")
            print(f"  Rotation actuelle pan (degrés): X={child.rotation_euler.x * 57.2958:.1f}°, Y={child.rotation_euler.y * 57.2958:.1f}°, Z={child.rotation_euler.z * 57.2958:.1f}°")
            
            # Tester différentes interprétations de "angle de l'objet de base"
            # Option 1: Angle Z du parent
            base_angle_parent_z = parent_obj.rotation_euler.z * 57.2958
            
            # Option 2: Angle Z actuel de l'objet pan
            base_angle_pan_z = child.rotation_euler.z * 57.2958
            
            print(f"  Option 1 - Angle Z parent: {base_angle_parent_z:.1f}° -> Nouveau: {180 - base_angle_parent_z:.1f}°")
            print(f"  Option 2 - Angle Z pan actuel: {base_angle_pan_z:.1f}° -> Nouveau: {180 - base_angle_pan_z:.1f}°")
            
            # Par défaut j'utilise l'angle actuel du pan (option 2)
            # Changez cette ligne si vous voulez l'angle du parent
            base_angle_degrees = base_angle_pan_z  # ou base_angle_parent_z
            
            new_angle_degrees = 180 - base_angle_degrees
            new_angle_radians = new_angle_degrees * 0.0174533
            child.rotation_euler.z = new_angle_radians
            print(f"  *** APPLIQUÉ: {base_angle_degrees:.1f}° -> {new_angle_degrees:.1f}° ***")
        
        # Règle pour les caméras "Projector"
        elif child_name.startswith("projector") and child.type == 'CAMERA':
            print(f"Traitement de la caméra projector: {child.name}")
            # Shift Y * -1 (propriété spécifique aux caméras)
            if child.data:  # Vérifier que les données de caméra existent
                child.data.shift_y *= -1
                print(f"  Camera Shift Y modifié: {child.data.shift_y}")
    
    # Mettre à jour la scène
    bpy.context.view_layer.update()
    print("Symétrie appliquée avec succès!")

def rename_selection_with_hierarchy(search_text, replace_text):
    """
    Renomme l'objet sélectionné et toute sa hiérarchie en remplaçant le texte spécifié
    """
    
    if not bpy.context.active_object:
        print("Aucun objet sélectionné!")
        return 0
    
    parent_obj = bpy.context.active_object
    
    # Obtenir tous les enfants récursivement
    def get_all_children(obj):
        children = []
        for child in obj.children:
            children.append(child)
            children.extend(get_all_children(child))
        return children
    
    all_children = get_all_children(parent_obj)
    all_objects = [parent_obj] + all_children
    
    renamed_count = 0
    
    # Renommer chaque objet
    for obj in all_objects:
        old_name = obj.name
        if search_text in old_name:
            new_name = old_name.replace(search_text, replace_text)
            obj.name = new_name
            print(f"Renommé: '{old_name}' -> '{new_name}'")
            renamed_count += 1
        else:
            print(f"Pas de changement: '{old_name}' (ne contient pas '{search_text}')")
    
    print(f"Renommage terminé! {renamed_count} objets renommés.")
    return renamed_count

def duplicate_selection_with_hierarchy():
    """
    Duplique l'objet sélectionné et toute sa hiérarchie sans appliquer de symétrie
    """
    
    if not bpy.context.active_object:
        print("Aucun objet sélectionné!")
        return
    
    parent_obj = bpy.context.active_object
    
    # Obtenir tous les enfants récursivement
    def get_all_children(obj):
        children = []
        for child in obj.children:
            children.append(child)
            children.extend(get_all_children(child))
        return children
    
    all_children = get_all_children(parent_obj)
    
    # Désélectionner tout d'abord
    bpy.ops.object.select_all(action='DESELECT')
    
    # Sélectionner l'objet parent
    parent_obj.select_set(True)
    print(f"Duplication du parent: {parent_obj.name}")
    
    # Sélectionner tous les enfants
    for child in all_children:
        child.select_set(True)
        print(f"Duplication de l'enfant: {child.name}")
    
    # S'assurer que le parent reste l'objet actif
    bpy.context.view_layer.objects.active = parent_obj
    
    print(f"Total d'objets à dupliquer: {len([obj for obj in bpy.context.selected_objects])}")
    
    # Dupliquer toute la hiérarchie sélectionnée
    bpy.ops.object.duplicate()
    
    print("Duplication terminée!")

def delete_selection_with_hierarchy():
    """
    Supprime l'objet sélectionné et toute sa hiérarchie
    """
    
    if not bpy.context.active_object:
        print("Aucun objet sélectionné!")
        return
    
    parent_obj = bpy.context.active_object
    
    # Obtenir tous les enfants récursivement
    def get_all_children(obj):
        children = []
        for child in obj.children:
            children.append(child)
            children.extend(get_all_children(child))
        return children
    
    all_children = get_all_children(parent_obj)
    
    # Désélectionner tout d'abord
    bpy.ops.object.select_all(action='DESELECT')
    
    # Sélectionner l'objet parent
    parent_obj.select_set(True)
    print(f"Suppression du parent: {parent_obj.name}")
    
    # Sélectionner tous les enfants
    for child in all_children:
        child.select_set(True)
        print(f"Suppression de l'enfant: {child.name}")
    
    # S'assurer que le parent reste l'objet actif
    bpy.context.view_layer.objects.active = parent_obj
    
    print(f"Total d'objets à supprimer: {len([obj for obj in bpy.context.selected_objects])}")
    
    # Supprimer toute la hiérarchie sélectionnée
    bpy.ops.object.delete(use_global=False)
    
    print("Suppression terminée!")

def apply_symmetry_with_duplicate():
    """
    Version alternative qui duplique l'objet et toute sa hiérarchie avant d'appliquer la symétrie
    """
    
    if not bpy.context.active_object:
        print("Aucun objet sélectionné!")
        return
    
    parent_obj = bpy.context.active_object
    
    # Obtenir tous les enfants récursivement
    def get_all_children(obj):
        children = []
        for child in obj.children:
            children.append(child)
            children.extend(get_all_children(child))
        return children
    
    all_children = get_all_children(parent_obj)
    
    # Désélectionner tout d'abord
    bpy.ops.object.select_all(action='DESELECT')
    
    # Sélectionner l'objet parent
    parent_obj.select_set(True)
    print(f"Sélection du parent: {parent_obj.name}")
    
    # Sélectionner tous les enfants
    for child in all_children:
        child.select_set(True)
        print(f"Sélection de l'enfant: {child.name}")
    
    # S'assurer que le parent reste l'objet actif
    bpy.context.view_layer.objects.active = parent_obj
    
    print(f"Total d'objets sélectionnés: {len([obj for obj in bpy.context.selected_objects])}")
    
    # Dupliquer toute la hiérarchie sélectionnée
    bpy.ops.object.duplicate()
    
    print("Duplication terminée, application de la symétrie...")
    
    # Appliquer la symétrie sur la copie
    apply_symmetry_to_selection()

# Interface utilisateur simple
class OBJECT_OT_apply_symmetry(bpy.types.Operator):
    """Applique une symétrie personnalisée sur l'objet sélectionné"""
    bl_idname = "object.apply_custom_symmetry"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        apply_symmetry_to_selection()
        return {'FINISHED'}

class OBJECT_OT_rename_hierarchy(bpy.types.Operator):
    """Renomme l'objet sélectionné et toute sa hiérarchie"""
    bl_idname = "object.rename_custom_hierarchy"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    
    # Propriétés pour la boîte de dialogue
    search_text: bpy.props.StringProperty(
        name="Remplacer",
        description="Texte à rechercher dans les noms",
        default=""
    )
    
    replace_text: bpy.props.StringProperty(
        name="Par",
        description="Nouveau texte de remplacement",
        default=""
    )
    
    def draw(self, context):
        layout = self.layout
        # Afficher les champs dans l'ordre et mettre le focus sur le premier
        layout.prop(self, "search_text")
        layout.prop(self, "replace_text")
    
    def execute(self, context):
        if not self.search_text:
            self.report({'WARNING'}, "Veuillez spécifier le texte à remplacer")
            return {'CANCELLED'}
        
        renamed_count = rename_selection_with_hierarchy(self.search_text, self.replace_text)
        
        if renamed_count > 0:
            self.report({'INFO'}, f"{renamed_count} objets renommés")
        else:
            self.report({'INFO'}, "Aucun objet renommé")
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # Réinitialiser les champs à chaque ouverture
        self.search_text = ""
        self.replace_text = ""
        # Afficher la boîte de dialogue avec focus automatique sur le premier champ
        return context.window_manager.invoke_props_dialog(self, width=300)

class OBJECT_OT_duplicate_hierarchy(bpy.types.Operator):
    """Duplique l'objet sélectionné et toute sa hiérarchie"""
    bl_idname = "object.duplicate_custom_hierarchy"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        duplicate_selection_with_hierarchy()
        return {'FINISHED'}

class OBJECT_OT_delete_hierarchy(bpy.types.Operator):
    """Supprime l'objet sélectionné et toute sa hiérarchie"""
    bl_idname = "object.delete_custom_hierarchy"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        delete_selection_with_hierarchy()
        return {'FINISHED'}

class VIEW3D_PT_custom_symmetry_panel(bpy.types.Panel):
    """Panel pour les outils de symétrie personnalisée"""
    bl_label = "Symétrie Personnalisée"
    bl_idname = "VIEW3D_PT_custom_symmetry"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"
    
    def draw(self, context):
        layout = self.layout
        
        # Créer une ligne horizontale pour tous les boutons avec icônes plus grandes
        row = layout.row(align=True)
        row.scale_x = 1.5  # Largeur des boutons
        row.scale_y = 1.5  # Hauteur des boutons
        row.operator("object.duplicate_custom_hierarchy", icon='DUPLICATE')
        row.operator("object.apply_custom_symmetry", icon='MOD_MIRROR')
        row.operator("object.rename_custom_hierarchy", icon='OUTLINER_DATA_FONT')
        row.operator("object.delete_custom_hierarchy", icon='TRASH')

def register():
    bpy.utils.register_class(OBJECT_OT_apply_symmetry)
    bpy.utils.register_class(OBJECT_OT_duplicate_hierarchy)
    bpy.utils.register_class(OBJECT_OT_rename_hierarchy)
    bpy.utils.register_class(OBJECT_OT_delete_hierarchy)
    bpy.utils.register_class(VIEW3D_PT_custom_symmetry_panel)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_apply_symmetry)
    bpy.utils.unregister_class(OBJECT_OT_duplicate_hierarchy)
    bpy.utils.unregister_class(OBJECT_OT_rename_hierarchy)
    bpy.utils.unregister_class(OBJECT_OT_delete_hierarchy)
    bpy.utils.unregister_class(VIEW3D_PT_custom_symmetry_panel)

if __name__ == "__main__":
    # Enregistrer les classes
    register()
    
    # Ou exécuter directement la fonction
    # apply_symmetry_to_selection()