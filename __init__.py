from . import ui
from . import projector
from . import operators
from . import duplicate
from . import mirror
import bpy.utils.previews

custom_icons = None

bl_info = {
    "name": "Projector by Lotchi",
    "author": "Baptiste Jazé",
    "description": "Easy Projector creation and modification.",
    "blender": (4, 5, 0),
    "version": (2025, 2, 1),
    "location": "3D Viewport > Add > Light > Projector",
    "category": "Lighting",
    "wiki_url": "",
    "tracker_url": ""
}


def register():
    global custom_icons
    
    # Charger les icônes personnalisées
    import os
    custom_icons = bpy.utils.previews.new()
    
    # Chemin vers le dossier icons
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    
    # Charger le logo
    custom_icons.load("logo", os.path.join(icons_dir, "logo.png"), 'IMAGE')
    
    projector.register()
    operators.register()
    duplicate.register()
    mirror.register()
    ui.register()


def unregister():
    global custom_icons
    
    # Décharger les icônes
    if custom_icons:
        bpy.utils.previews.remove(custom_icons)
        
    ui.unregister()
    mirror.unregister()
    duplicate.unregister()
    operators.unregister()
    projector.unregister()
