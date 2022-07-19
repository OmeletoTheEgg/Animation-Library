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

import inspect
from typing import Optional, FrozenSet, Set, Union, Iterable, cast, List, Tuple
import bpy
from bpy.types import (
    Action,
    Object,
    Operator
)

# Things left to do
# 
# Try not using bone.path_from_id all that shit
# Fix fcurve update
# Select bones operator
# Do the things for rotation and location, maybe also bbone 
# Create fail-cases of like what if there's no keyframes selected
# Check if pose library only works in pose mode. If so, make an exception to not have object mode



addon_keymaps: List[Tuple[bpy.types.KeyMap, bpy.types.KeyMapItem]] = []

def copy_location_to_action(from_action: Action, to_action: Action, frame_current: float, smallest_x: float, apply: bool):
    bone_names = {bone.name for bone in bpy.context.selected_pose_bones_from_active_object}
    print("test")
    for bone_name in sorted(bone_names):
        for location_index in range(3):
            bone = bpy.context.object.pose.bones[bone_name]
            rna_path = bone.path_from_id("location")
            from_fcurve = from_action.fcurves.find(rna_path, index=location_index)
            to_fcurve = to_action.fcurves.find(rna_path, index=location_index)
            if to_fcurve is None:
                to_fcurve = to_action.fcurves.new(rna_path, index=location_index, action_group=bone_name)
                
            for keyframe in from_fcurve.keyframe_points:
                
                if not apply:
                    if keyframe.select_control_point:
                        to_fcurve.keyframe_points.insert(frame=keyframe.co.x, value=keyframe.co.y)
                else:
                    to_fcurve.keyframe_points.insert(frame=(keyframe.co.x + frame_current) - smallest_x, value=keyframe.co.y)

                
            
class CreateAnimationAsset(Operator):
    bl_idname = "animation.create_animation_asset"
    bl_label = "Create Animation Asset"
    bl_description = (
        "Creates an Action that contains the selected keyframes of the selected bones, marks it as an asset"
    )
    bl_options = {"REGISTER", "UNDO"} 


    @classmethod
    def poll(cls, context: Operator) -> bool:
        return context.active_object is not None

    def execute(self, context: Operator) -> Set[str]:
        to_action = bpy.data.actions.new(context.object.animation_data.action.name_full)
        from_action = context.object.animation_data.action
        copy_location_to_action(from_action, to_action, 0, 0, False)
        to_action.asset_mark()
        to_action.asset_generate_preview()
        
        return {'FINISHED'}


class ApplyAnimationAsset(Operator):
    bl_idname = "animation.apply_animation_asset"
    bl_label = "Apply Animation Asset"
    bl_description = (
        "Applies the Asset keyframes to the current action"
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.active_object is not None

    def execute(self, context: bpy.types.Context) -> Set[str]:
        selected_asset_name = context.selected_asset_files[0].local_id.name
        from_action = bpy.data.actions[selected_asset_name]
        to_action = context.object.animation_data.action
        frame_current = context.scene.frame_current
        if to_action is None:
            to_action = bpy.data.actions.new(context.object.name_full)
            context.object.animation_data.action = to_action

        smallest_x = from_action.fcurves[0].keyframe_points[0].co.x
        
        for fcurves in from_action.fcurves:
            keyframe = fcurves.keyframe_points[0]
            if keyframe.co.x < smallest_x:
                smallest_x = keyframe.co.x

        copy_location_to_action(from_action, to_action, frame_current, smallest_x, True)
        # this is just to update the fcurves after inserting. I found that fcurve.update() isn't working maybe just from what I expect
        context.scene.frame_current = frame_current
        return {'FINISHED'}
        
def menu_func(self, context):
    self.layout.operator(CreateAnimationAsset.bl_idname, text=CreateAnimationAsset.bl_label)
    self.layout.operator(ApplyAnimationAsset.bl_idname, text=ApplyAnimationAsset.bl_label)

def register():
    bpy.utils.register_class(CreateAnimationAsset)
    bpy.utils.register_class(ApplyAnimationAsset)
    bpy.types.VIEW3D_MT_pose.append(menu_func)

    window_manager = bpy.context.window_manager
    if window_manager.keyconfigs.addon is None:
        return

    km = window_manager.keyconfigs.addon.keymaps.new(name="File Browser Main", space_type="FILE_BROWSER")

    kmi = km.keymap_items.new("animation.apply_animation_asset", "RIGHTMOUSE", "DOUBLE_CLICK")
    addon_keymaps.append((km, kmi))

def unregister():
    bpy.utils.unregister_class(CreateAnimationAsset)
    bpy.utils.unregister_class(ApplyAnimationAsset)
    bpy.types.VIEW3D_MT_pose.remove(menu_func)

    # Clear shortcuts from the keymap.
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
