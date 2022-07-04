import bpy

def create_animation_asset(context: Context, asset_name: str) -> Optional[Action]:
    bones = context.selected_pose_bones_

class CreateAnimationAsset(bpy.types.Operators):
    bl_idname = "poselib.create_pose_asset"
    bl_label = "Create Pose Asset"
    bl_description = (
        "Creates an Action that contains the selected keyframes of the selected bones, marks it as an asset"
    )
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, bpy.types.Context) -> Set[str]:
