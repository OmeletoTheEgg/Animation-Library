bl_info = {
    "name": "Animation Library",
    "description": "Animation Library based on the Asset Browser.",
    "author": "Arjhi P. Moscosa",
    "version": (1, 0),
    "blender": (3, 2, 0),
    "warning": "In heavily development, things may change",
    "location": "Asset Browser -> Animations, and 3D Viewport -> Animation panel",
    "support": "OFFICIAL",
    "category": "Animation",
}

from . import gui, operators

import bpy

def register() -> None:
    
    operators.register()
    gui.register()

def unregister() -> None:
    gui.unregister()
    operators.unregister()

    try:
        del bpy.types.WindowManager.poselib_flipped
    except AttributeError:
        pass
    try:
        del bpy.types.WindowManager.poselib_previous_action
    except AttributeError:
        pass
