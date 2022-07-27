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
# import re

from pathlib import Path
from typing import Any, List, Iterable

from bpy.types import (
    Action,
    Object,
    FCurve,
    Operator,
    AssetHandle,
    Context,
    Panel,
    UIList,
    WindowManager,
    WorkSpace,
)
from bpy_extras import asset_utils

# Things left to do
# Fix when the selected bones in the asset is not present in the destination action
# Try not using bone.path_from_id all that shit
# Select bones operator
# Do the things for rotation and location, maybe also bbone 
# Create fail-cases of like what if there's no keyframes selected
# Check if pose library only works in pose mode. If so, make an exception to not have object mode
# Make a button for create pose asset

addon_keymaps: List[Tuple[bpy.types.KeyMap, bpy.types.KeyMapItem]] = []

def insert_keyframes(from_fcurve: FCurve, to_fcurve: FCurve, frame_current: float, smallest_x: float, apply: bool):
    for keyframe in from_fcurve.keyframe_points:
        
        if not apply:
            if keyframe.select_control_point:
                to_fcurve.keyframe_points.insert(frame=keyframe.co.x, value=keyframe.co.y, keyframe_type='JITTER')
                to_fcurve.keyframe_points.update()
        else:
            to_fcurve.keyframe_points.insert(frame=(keyframe.co.x + frame_current) - smallest_x, value=keyframe.co.y, keyframe_type='JITTER')
            to_fcurve.keyframe_points.update()
            
def copy_location_to_action(from_action: Action, to_action: Action, frame_current: float, smallest_x: float, apply: bool):
    bone_names = {bone.name for bone in bpy.context.selected_pose_bones_from_active_object}
    for bone_name in bone_names:
        for location_index in range(3):
            bone = bpy.context.object.pose.bones[bone_name]
            print(bone)
            rna_path = bone.path_from_id("location")
            from_fcurve = from_action.fcurves.find(rna_path, index=location_index)
            if from_fcurve is None:
                break

            to_fcurve = to_action.fcurves.find(rna_path, index=location_index)
            if to_fcurve is None:
                to_fcurve = to_action.fcurves.new(rna_path, index=location_index, action_group=bone_name)
            
            insert_keyframes(from_fcurve, to_fcurve, frame_current, smallest_x, apply)
                

def copy_rotation_to_action(from_action: Action, to_action: Action, frame_current: float, smallest_x: float, apply: bool):
    bone_names = {bone.name for bone in bpy.context.selected_pose_bones_from_active_object}
    for bone_name in bone_names:
        bone = bpy.context.object.pose.bones[bone_name]
        if bone.rotation_mode == "QUATERNION":
            for rotation_index in range(4):
                rna_path = bone.path_from_id("rotation_quaternion")
                from_fcurve = from_action.fcurves.find(rna_path, index=rotation_index)
                if from_fcurve is None:
                    break

                to_fcurve = to_action.fcurves.find(rna_path, index=rotation_index)
                if to_fcurve is None:
                    to_fcurve = to_action.fcurves.new(rna_path, index=rotation_index, action_group=bone_name)

                insert_keyframes(from_fcurve, to_fcurve, frame_current, smallest_x, apply)

        elif bone.rotation_mode == "AXIS_ANGLE":
            for rotation_index in range(4):
                rna_path = bone.path_from_id("rotation_axis_angle")
                from_fcurve = from_action.fcurves.find(rna_path, index=rotation_index)
                if from_fcurve is None:
                    break

                to_fcurve = to_action.fcurves.find(rna_path, index=rotation_index)
                if to_fcurve is None:
                    to_fcurve = to_action.fcurves.new(rna_path, index=rotation_index, action_group=bone_name)
                    
                insert_keyframes(from_fcurve, to_fcurve, frame_current, smallest_x, apply)
                
        else:
            for rotation_index in range(3):
                rna_path = bone.path_from_id("rotation_euler")
                from_fcurve = from_action.fcurves.find(rna_path, index=rotation_index)
                if from_fcurve is None:
                    break

                to_fcurve = to_action.fcurves.find(rna_path, index=rotation_index)
                if to_fcurve is None:
                    to_fcurve = to_action.fcurves.new(rna_path, index=rotation_index, action_group=bone_name)
                    
                insert_keyframes(from_fcurve, to_fcurve, frame_current, smallest_x, apply)
                
def copy_scale_to_action(from_action: Action, to_action: Action, frame_current: float, smallest_x: float, apply: bool):
    bone_names = {bone.name for bone in bpy.context.selected_pose_bones_from_active_object}
    for bone_name in bone_names:
        for scale_index in range(3):
            bone = bpy.context.object.pose.bones[bone_name]
            rna_path = bone.path_from_id("scale")
            from_fcurve = from_action.fcurves.find(rna_path, index=scale_index)
            if from_fcurve is None:
                break

            to_fcurve = to_action.fcurves.find(rna_path, index=scale_index)
            if to_fcurve is None:
                to_fcurve = to_action.fcurves.new(rna_path, index=scale_index, action_group=bone_name)
                
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
        copy_rotation_to_action(from_action, to_action, 0, 0, False)
        copy_scale_to_action(from_action, to_action, 0, 0, False)
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
        current_library_name = context.area.spaces.active.params.asset_library_ref
        selected_asset_name = []
        asset_file = context.selected_asset_files[0]

        if current_library_name != "LOCAL":  # NOT Current file
            library_path = Path(context.preferences.filepaths.asset_libraries.get(current_library_name).path)
            asset_fullpath = library_path / asset_file.relative_path
            selected_asset_name = asset_fullpath.name
            with bpy.data.libraries.load(str(asset_fullpath.parent.parent), assets_only = True) as (data_from, data_to):
                data_to.actions = [selected_asset_name]
        else:
            selected_asset_name = asset_file.local_id.name
            
        from_action = bpy.data.actions.get(selected_asset_name)
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
        copy_rotation_to_action(from_action, to_action, frame_current, smallest_x, True)
        copy_scale_to_action(from_action, to_action, frame_current, smallest_x, True)

        if current_library_name != 'LOCAL':
            bpy.data.actions.remove(from_action)
        return {'FINISHED'}
        
class AnimationLibraryPanel(bpy.types.Panel):
    """Creates a Sub-Panel in the Property Area of the 3D View"""
    bl_label = "Animation Library (by Omeleto)"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Animation"
    bl_context = "posemode"

    def draw(self, context):

        layout = self.layout

        row = layout.row()
        row.operator("animation.create_animation_asset")
        layout.separator()


def menu_func(self, context):
    self.layout.operator(CreateAnimationAsset.bl_idname, text=CreateAnimationAsset.bl_label)
    self.layout.operator(ApplyAnimationAsset.bl_idname, text=ApplyAnimationAsset.bl_label)

def register():
    bpy.utils.register_class(CreateAnimationAsset)
    bpy.utils.register_class(ApplyAnimationAsset)
    bpy.types.VIEW3D_MT_pose.append(menu_func)
    
    bpy.utils.register_class(AnimationLibraryPanel)

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

    bpy.utils.unregister_class(AnimationLibraryPanel)


    # Clear shortcuts from the keymap.
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
