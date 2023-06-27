import bpy
from threading import Thread
from llv.buchse import Buchse
from llv.gesicht import FaceFrame
from .mapping import Functions, MirroredFunctions
from .recording import recorder
from .utils import props


props.add('mirrorUpdate', "Mirror Update", False)
props.add('faceLiveUpdatePose', "Live Update", False)


class FaceToggleUpdateButtonOperator(bpy.types.Operator):
    bl_idname = "scene.face_toggle_update"
    bl_label = "Toggle Live Update"

    def execute(self, context):
        if not bpy.context.scene.faceLiveUpdatePose:
            bpy.context.scene.faceGlobalTimerStarted = True
            bpy.context.scene.faceLiveUpdatePose = True
            bpy.ops.wm.face_global_timer()
            bpy.ops.wm.face_live_update_pose()
        else:
            bpy.context.scene.faceGlobalTimerStarted = False
            bpy.context.scene.faceLiveUpdatePose = False
        return {'FINISHED'}
    
class FaceSetNeutralButtonOperator(bpy.types.Operator):
    bl_idname = "scene.face_set_neutral_pose"
    bl_label = "Set Neutral Pose"


    def execute(self, context):
        recorder.set_neutral_pose()
        return {'FINISHED'}
    
class FaceResetNeutralButtonOperator(bpy.types.Operator):
    bl_idname = "scene.face_reset_neutral_pose"
    bl_label = "Reset Neutral Pose"


    def execute(self, context):
        recorder.reset_neutral_pose()
        return {'FINISHED'}
    
class FaceStartPortButtonOperator(bpy.types.Operator):
    bl_idname = "scene.face_start_port"
    bl_label = "Start Listen to Phone"
    listening = False

    last_msg = None

    def execute(self, context):
        t1 = Thread(target=self.record, daemon=True)
        t1.start()
        return {'FINISHED'}
    

    def record(self, host='0.0.0.0', port=11111):
        try:
            buchse = Buchse(host, port, as_server=True)
        except Exception as e:
            FaceStartPortButtonOperator.listening = False
            raise e
        FaceStartPortButtonOperator.listening = True
        try:
            while True:
                data, size = buchse.horch(FaceFrame.PACKET_MAX_SIZE)
                if not data or 0 == size:
                    continue
                try:
                    frame = FaceFrame.from_raw(data, size)
                except Exception:
                    print("Failed to parse frame")
                    recorder.last_pose = None
                    continue
                recorder.add_frame(frame)
        finally:
            FaceStartPortButtonOperator.listening = False

class FaceBLUpdatePose(bpy.types.Operator):
    """Playback Control"""
    bl_label = "Start Update"
    bl_idname = 'wm.face_live_update_pose'

    def modal(self, context, event):
        if not context.scene.faceLiveUpdatePose:
            return self.cancel(context)

        if event.type == 'TIMER':
            if  recorder.last_pose is not None:
                if context.scene.mirrorUpdate:
                    f = MirroredFunctions
                else:
                    f = Functions
                pose = recorder.get_neutralized_pose(recorder.last_pose)
                for key in f.keys():
                    (name, index) = key.split(':')
                    index = int(index)
                    value = f[key](pose)
                    if key == 'head:1':
                        bpy.data.objects['deform'].pose.bones[name].rotation_euler.y = value
                    else:
                        if index == 0:
                            bpy.data.objects['deform'].pose.bones[name].location.x = value
                        if index == 1:
                            bpy.data.objects['deform'].pose.bones[name].location.y = value
                        if index == 2:
                            bpy.data.objects['deform'].pose.bones[name].location.z = value

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        wm.modal_handler_add(self)
        if not context.scene.faceGlobalTimerStarted:
            bpy.ops.wm.face_global_timer()
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        return {'CANCELLED'}

    @classmethod
    def poll(cls, context):
        return True
    
class FaceLiveLinkPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Sophia'
    bl_label = "Face Live Link"
    bl_idname = "VIEW3D_PT_face_update_panel"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator(FaceStartPortButtonOperator.bl_idname)
        row.enabled = not FaceStartPortButtonOperator.listening
        row = layout.row()
        if not context.scene.faceLiveUpdatePose:
            row.operator(FaceToggleUpdateButtonOperator.bl_idname, text = "Start Live Update")
        else:
            row.operator(FaceToggleUpdateButtonOperator.bl_idname, text = "Stop Live Update")
        row.enabled = FaceStartPortButtonOperator.listening
        row = layout.row()
        row.operator(FaceSetNeutralButtonOperator.bl_idname)
        if recorder.neutral_pose is not None:
            row.operator(FaceResetNeutralButtonOperator.bl_idname)
        row = layout.row()
        row.prop(bpy.context.scene, "mirrorUpdate")
        row.enabled = FaceStartPortButtonOperator.listening
