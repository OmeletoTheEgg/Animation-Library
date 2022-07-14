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

# def create_animation_asset(context: bpy.types.Context) -> Optional[bpy.types.Action]:
#     bone_names = {bone.name for bone in context.selected_pose_bones_from_active_object}
#     params = PoseCreationParams(
#         context.object,
#         getattr(context.object.animation_data, "action", None),
#         context.scene.frame_current,
#         frozenset(bone_names),
#         asset_name
#     )
  
#     dst_action = bpy.data.actions.new("test")
#     dst_action.user_clear()
#     if params.src_action:
#         dst_action.id_root = params.src_action.id_root
    

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

class CreateAnimationAsset(bpy.types.Operator):
    bl_idname = "pose.create_animation_asset"
    bl_label = "Create Animation Asset test"
    bl_description = (
        "Creates an Action that contains the selected keyframes of the selected bones, marks it as an asset"
    )
    bl_options = {"REGISTER", "UNDO"} 


    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.active_object is not None

    def execute(self, context: bpy.types.Context) -> Set[str]:
        new_action = bpy.data.actions.new("test")
        src_action = bpy.context.object.animation_data.action
        bone_names = {bone.name for bone in bpy.context.selected_pose_bones_from_active_object}
        for bone_name in sorted(bone_names):
            for location_index in range(3):
                bone = bpy.context.object.pose.bones[bone_name]
                rna_path = bone.path_from_id("location")
                new_fcurve = new_action.fcurves.find(rna_path, index=location_index)
                if new_fcurve is None:
                    new_fcurve = new_action.fcurves.new(rna_path, index=location_index, action_group=bone_name)
                src_fcurve = src_action.fcurves.find(rna_path, index=location_index)
                for keyframe in src_fcurve.keyframe_points:
                    new_fcurve.keyframe_points.insert(frame=keyframe.co.x, value=keyframe.co.y)

                new_action.asset_mark()
                new_action.asset_generate_preview()


                

 

        # for fcurve in src_obj.action.fcurves:
        #     src_keyframe_points = fcurve.keyframe_points
        #     print(src_keyframe_points)

                # I need to figure out how to create fcurves from dst_action the same data path as each fcurve of src_action
                # probably need to look at what Pose Library did on that, but i need to ensure that I'm getting the keyframe points themselves,
                # not the value of the fcurve in the specific time which what Pose Library does

                # Maybe try having only operators to copy from existing action to new action.
                # But the problem with that is the new action doesn't initially have the same fcurves as the existing action
                
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(CreateAnimationAsset.bl_idname, text=CreateAnimationAsset.bl_label)

def register():
    bpy.utils.register_class(CreateAnimationAsset)
    bpy.types.VIEW3D_MT_pose.append(menu_func)

def unregister():
    bpy.utils.unregister_class(CreateAnimationAsset)
    bpy.types.VIEW3D_MT_pose.remove(menu_func)

if __name__ == "__main__":
    register()
