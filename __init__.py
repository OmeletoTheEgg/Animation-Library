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

from typing import Optional, FrozenSet, Set, Union, Iterable, cast
import bpy

# class PoseCreationParams:
#     armature_ob: bpy.types.Object
#     src_action: Optional[bpy.types.Action]
#     src_frame_nr: float
#     bone_names: FrozenSet[str]
#     new_asset_name: str

# FCurveValue = Union[float, int]

# def create_animation_asset(context: bpy.types.Context, asset_name: str) -> Optional[bpy.types.Action]:
#     bone_names = {bone.name for bone in context.selected_pose_bones_from_active_object}
#     params = PoseCreationParams(
#         context.object,
#         getattr(context.object.animation_data, "action", None),
#         context.scene.frame_current,
#         frozenset(bone_names),
#         asset_name
#     )
  
#     dst_action = bpy.data.actions.new(params.new_asset_name)
#     if params.src_action:
#         dst_action.id_root = params.src_action.id_root
#     dst_action.user_clear()

#     for bone_name in sorted(params.bone_names):
#         for array_index in range(3):
#             bone = params.armature_ob.pose.bones[bone_name]
#             value_or_array = bpy.types.ID.path_resolve("location")
#             value = cast(FCurveValue, value_or_array[array_index])
#             rna_path = bone.path_from_id("location")
#             fcurve = dst_action.fcurves.find(rna_path, index=array_index)
#             if fcurve is None:
#                 fcurve = dst_action.fcurves.new(rna_path, index=array_index, action_group=bone_name)

#             fcurve.keyframe_points.insert(params.src_frame_nr, value=value)
#             fcurve.update()

#     if len(dst_action.fcurves) == 0:
#             bpy.data.actions.remove(dst_action)

# class CreateAnimationAsset(bpy.types.Operator):
#     bl_idname = "poselib.create_pose_asset"
#     bl_label = "Create Pose Asset"
#     bl_description = (
#         "Creates an Action that contains the selected keyframes of the selected bones, marks it as an asset"
#     )
#     bl_options = {"REGISTER", "UNDO"}

#     @classmethod
#     def poll(cls, context: Context) -> bool:
#         return context.active_object is not None

#     def execute(self, context: bpy.types.Context):
#         create_animation_asset(context, "test")

# def menu_func(self, context):
#     self.layout.operator(CreateAnimationAsset.bl_idname, text=CreateAnimationAsset.bl_label)

# def register():
#     bpy.utils.register_class(CreateAnimationAsset)
#     bpy.types.VIEW3D_MT_object.append(menu_func)

# def unregister():
#     bpy.utils.unregister_class(CreateAnimationAsset)
#     bpy.types.VIEW3D_MT_object.remove(menu_func)

# if __name__ == "__main__":
#     register()

