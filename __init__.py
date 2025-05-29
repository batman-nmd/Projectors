from . import ui
from . import projector
from . import operators

bl_info = {
    "name": "Projector by Lotchi",
    "author": "Baptiste Jazé",
    "description": "Easy Projector creation and modification.",
    "blender": (4, 5, 0),
    "version": (2025, 29, 5),
    "location": "3D Viewport > Add > Light > Projector",
    "category": "Lighting",
    "wiki_url": "",
    "tracker_url": ""
}


def register():
    projector.register()
    operators.register()
    ui.register()


def unregister():
    ui.unregister()
    operators.unregister()
    projector.unregister()
