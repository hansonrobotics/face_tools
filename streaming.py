import bpy
import roslibpy
import threading
from queue import Queue
from .utils import Singleton, props
from mathutils import Matrix, Euler, Quaternion
import math
# FROM ranimation_manager
# Single action names that match single bone

props['faceStreaming'] = False
props.add('robotIP', "Robot IP address", '10.0.0.10')

HEAD_BONES = {
    'BrowOuterLeft' : 'brow.L',
    'BrowInnerLeft' : 'brow.inner.L',
    'BrowCenter' : 'brow.C',
    'BrowInnerRight' : 'brow.inner.R',
    'BrowOuterRight' : 'brow.R',
    'UpperLidLeft' : 'eyelid_UP_L',
    'UpperLidRight' : 'eyelid_UP_R',
    'LowerLidLeft' : 'eyelid_LO_L',
    'LowerLidRight' : 'eyelid_LO_R',
    'CheekSquintLeft' : 'cheek_L',
    'CheekSquintRight' : 'cheek_R',
    'SneerLeft': 'nostril_R',
    'SneerRight': 'nostril_L',
    'UpperLipLeft' : 'lip_U_L',
    'UpperLipCenter' : 'lip_U',
    'UpperLipRight' : 'lip_U_R',
    'LowerLipLeft' : 'lip_D_L',
    'LowerLipCenter' : 'lip_D',
    'LowerLipRight' : 'lip_D_R',
    'LipsStretchLeft' : 'mouth_C_L',
    'LipsStretchRight': 'mouth_C_R',
    'FrownLeft' : 'mouth_D_L',
    'FrownRight' : 'mouth_D_R',
    'SmileLeft' : 'mouth_U_L',
    'SmileRight' : 'mouth_U_R',
    'Jaw' : 'chin',
}




class ROSManager(metaclass=Singleton):
    def __init__(self):
        self.command_queue = Queue()
        self.publishers = {}
        self.ros = None
        self.thread = threading.Thread(target=self.worker_thread, daemon=True)
        self.thread.start()

    def connect(self, url, publishers):
        self.command_queue.put(('connect', (url, publishers)))

    def publish(self, topic_name, data):
        self.command_queue.put(('publish', (topic_name, data)))

    def disconnect(self):
        self.command_queue.put(('disconnect', None))

    def is_connected(self):
        return self.ros and self.ros.is_connected

    def worker_thread(self):
        while True:
            command, args = self.command_queue.get()

            if command == 'connect':
                self._connect(*args)
            elif command == 'publish':
                self._publish(*args)
            elif command == 'disconnect':
                self._disconnect()

    def _connect(self, url, publishers):
        self.ros = roslibpy.Ros(url)
        self.ros.run()
        for pub in publishers:
            topic_type, topic = publishers[pub]
            self.publishers[pub] = roslibpy.Topic(self.ros, topic, topic_type)

    def _publish(self, topic_name, data):
        if topic_name in self.publishers:
            self.publishers[topic_name].publish(roslibpy.Message(data))

    def _disconnect(self):
        try:
            self.ros.close()
        except Exception:
            pass

    


class ExternalStream(metaclass=Singleton):
    def __init__(self):
        self.streaming = False
        self.bones = bpy.data.objects['deform'].pose.bones
    
    def get_pose(self):
        pose = {}
        for key, bone in HEAD_BONES.items():
            # Default case
            j = 1
            if key == 'Jaw':
                j = 2
            pose[key] = min(1, max(-1,(self.bones[bone].location[j] * 25)))
        head = self.getHeadData()
        eyes = self.getEyesData()
        neck = self.getNeckData()
        print(neck)
        pose.update(head)
        pose.update(eyes)
        pose.update(neck)
        return pose
    
    '''
        These are copied from head data export functions in roscom package
    '''
    def getHeadData(self):
        bones = self.bones
        rhead = bones['DEF-head'].matrix @ Matrix.Rotation(math.pi/2, 4, 'X')
        rneck = bones['DEF-neck'].matrix @ Matrix.Rotation(-math.pi/2, 4, 'X')
        rneck.invert()
        # I think this is the correct order for the neck rotations.
        q = (rneck @ rhead).to_euler('XYZ')
        # q = (rhead * rneck).to_quaternion()
        return {
            'HeadYaw': -q.z,
            'HeadPitch': -q.x,
            'HeadRoll': -q.y
        }


    # Same as head, but for the lower neck joint.
    def getNeckData(self):
        # Unused, as API only support HEAD joint
        bones = self.bones
        rneck = bones['DEF-neck'].matrix @ Matrix.Rotation(-math.pi/2, 4, 'X')
        q = rneck.to_euler('XYZ')
        return {
            # 'NeckYaw': q.z, Not used
            'NeckPitch': q.x,
            'NeckRoll': q.y
        }

    # Gets Eye rotation angles:
    # Pitch: down(negative) to up(positive)
    # Yaw: left (negative) to right(positive)

    def getEyesData(self):
        bones = self.bones
        head = (bones['DEF-head'].id_data.matrix_world @ bones['DEF-head'].matrix @ Matrix.Rotation(-math.pi/2, 4, 'X')).to_euler()
        leye = bones['eye.L'].matrix.to_euler()
        reye = bones['eye.R'].matrix.to_euler()
        # Relative to head. Head angles are inversed.
        leye_p = leye.x + head.x
        leye_y = math.pi - leye.z if leye.z >= 0 else -(math.pi+leye.z)
        reye_p = reye.x + head.x
        reye_y = math.pi - reye.z if reye.z >= 0 else -(math.pi+reye.z)
        # Add head target
        leye_y += head.z
        reye_y += head.z
        # Current API do not support separate eye movements
        return {
            'EyesYaw': leye_y,
            'EyesPitch': leye_p,
        }


class FaceResetPoseButtonOperator(bpy.types.Operator):
    bl_idname = "scene.face_reset_pose"
    bl_label = "Reset Robot Pose"

    def execute(self, context):
        pose = ExternalStream().get_pose()
        # Send an empty pose
        tp = {
            'names': list(pose.keys()),
            'values': [0]*len(pose.keys())
        }
        ROSManager().publish('pose', tp)
        return{'FINISHED'}

class FaceStopStreamButtonOperator(bpy.types.Operator):
    bl_idname = "scene.face_stop_stream"
    bl_label = "Stop Streaming"

    def execute(self, context):
        ExternalStream().streaming = False
        return{'FINISHED'}


class FaceStreamPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Sophia'
    bl_idname = "VIEW3D_PT_face_stream_panel"
    bl_label = "Face Stream"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(bpy.context.scene, "robotIP")
        row = layout.row()
        if ROSManager().is_connected():
            row.operator(FaceDisconnectROS.bl_idname)
        else:
            row.operator(FaceConnectROS.bl_idname)
        if ROSManager().is_connected():
            row.operator(FaceResetPoseButtonOperator.bl_idname)
            row = layout.row()
            if not ExternalStream().streaming:
                row.operator(FaceStartStreamButtonOperator.bl_idname)
            else:
                row.operator(FaceStopStreamButtonOperator.bl_idname)


class FaceStartStreamButtonOperator(bpy.types.Operator):
    bl_idname = "scene.face_start_stream"
    bl_label = "Start Streaming to Robot"

    def execute(self, context):
        ExternalStream().streaming = True
        if not props['faceStreaming']:
            bpy.ops.wm.face_live_update_pose()
        return {'FINISHED'}


class FaceConnectROS(bpy.types.Operator):
    bl_idname = "scene.face_connect_ros"
    bl_label = "Connect to robot"
     
    def execute(self, context):
        ROSManager().connect(f"ws://{context.scene.robotIP}:9090", {
            'pose': ('hr_msgs/TargetPosture', '/hr/animation/set_state')
        })
        return {'FINISHED'}


class FaceDisconnectROS(bpy.types.Operator):
    bl_idname = "scene.face_disconnect_ros"
    bl_label = "Disconnect from  robot"

    def execute(self, context):
        ROSManager().disconnect()
        return {'FINISHED'}


class FaceStreaming(bpy.types.Operator):
    """ Face Streaming callback on timer """
    bl_label = "Start Face Stream"
    bl_idname = 'wm.face_live_update_pose'

    def modal(self, context, event):
        if event.type == 'TIMER':
            if  ExternalStream().streaming:
                pose = ExternalStream().get_pose()
                # Send pose
                tp = {
                    'names': list(pose.keys()),
                    'values': list(pose.values())
                }
                ROSManager().publish('pose', tp)
        return {'PASS_THROUGH'}

    def execute(self, context):
        print("START STREAMING")
        wm = context.window_manager
        wm.modal_handler_add(self)
        if not props['faceGlobalTimerStarted']:
            bpy.ops.wm.face_global_timer()
        props['faceStreaming'] = True
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        return {'CANCELLED'}

    @classmethod
    def poll(cls, context):
        return True