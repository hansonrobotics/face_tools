import bpy
import csv
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from .utils import Singleton, props
from .mapping import Functions, MirroredFunctions
from copy import deepcopy
from threading import RLock

# Recording properties
props.add('mirrorRecord', "Mirror Recording", False)
props.add('saveHead', "Head Movement", True)
props.add('saveEyes', "Eye Movement", True)
props.add('saveEyelids', "Eyelids", True)
props.add('saveBrows', "Brows", True)
props.add('saveMouth', "Mouth", True)
props.add('saveSneer', "sneer/cheeck", True)


class Recorder(metaclass=Singleton):
    def __init__(self):
        self.current_recording = []
        self.is_recording = False
        self.start_frame = 0
        self.fps = 60
        self.multiplier = 1
        self.neutral_pose = None
        self.last_pose = None
        self.frame_lock = RLock()

    def start(self):
        self.clear()
        self.is_recording = True

    def stop(self):
        self.is_recording  = False

    def clear(self):
        self.current_recording = []
        self.start_frame = 0

    def set_neutral_pose(self):
        print("SET POSE {}".format(self.last_pose))
        self.neutral_pose = self.last_pose
    
    def reset_neutral_pose(self):
        self.neutral_pose = None

    def get_neutralized_pose(self, pose):
        if self.neutral_pose:
            for key in pose:
                pose[key] -= self.neutral_pose.get(key, 0)
        return pose
    


    def parse_timecode(self, timecode):
        timecode = timecode.split(':')
        hours = int(timecode[0])
        minutes = int(timecode[1])
        seconds = int(timecode[2])
        frames = int(timecode[3].split('.')[0])
        total_frame_num = frames + seconds * self.fps + minutes * self.fps * 60 + hours * self.fps * 60 * 60
        return total_frame_num

    def parse_llv_frame(self, frame):
        fn = 1
        ft = frame.frame_time
        if self.start_frame == 0:
            self.start_frame = ft['frame_number']
            self.multiplier = round((self.fps / float(ft['numerator'])),2)
        else:
            fn = 1+ (ft['frame_number'] - self.start_frame) * self.multiplier
        # make sure no reference errors
        frame = frame.blendshapes
        # Last pose is raw
        self.last_pose = deepcopy(frame)
        frame = self.get_neutralized_pose(frame)
        frame['frame'] = fn
        return frame
    
    # Frame by frame adding
    def add_frame(self, frame):
        with self.frame_lock:
            # Recalclute time
            if hasattr(frame, 'frame_time'):
                frame = self.parse_llv_frame(frame)
            elif 'Timecode' in frame:
                current_frame = self.parse_timecode(frame['Timecode'])
                if self.start_frame == 0:
                    self.start_frame = current_frame
                # Actions starts with the 1
                frame['frame'] = 1 + current_frame - self.start_frame
            if self.is_recording:
                self.current_recording.append(frame)

    # Parse action and save it as new action
    def save_action(self, head=True, brows=True, eyes=True, eyelids=True, mouth=True, sneer_cheecks=True, mirror=False):
        # Make sure its stopped
        self.stop()
        action = bpy.data.actions.new("TMP-Recorded")
        with self.frame_lock:
            for frame in self.current_recording:
                # Skip empty frames, keep timing
                if len(frame) == 0:
                    continue
                if mirror:
                    f = MirroredFunctions
                else:
                    f = Functions
                
                to_record = list(f.keys())
                if not head:
                    to_record = [key for key in to_record if not "head" in key]
                if not eyes:
                    to_record = [key for key in to_record if not "eye_offset" in key]
                if not eyelids:
                    to_record = [key for key in to_record if not key in ['eyelid_LO_R:1', 'eyelid_UP_R:1','eyelid_LO_L:1', 'eyelid_UP_L:1']]
                if not brows:
                    to_record = [key for key in to_record if not key in ['brow.inner.R:1', 'brow.R:1', 'brow.C:1', 'brow.inner.L:1', 'brow.L:1']]
                if not mouth:
                    to_record = [key for key in to_record if not "mouth" in key and not "lip" in key and not "chin" in key]
                if not sneer_cheecks:
                    to_record = [key for key in to_record if not "nostril" in key]
                if not sneer_cheecks:
                    to_record = [key for key in to_record if not "cheek" in key]

                for key in to_record:
                    (name, index) = key.split(':')
                    index = int(index)

                    if key == 'head:1':
                        path = 'pose.bones[\"{bname}\"].rotation_euler'.format(bname = name)
                    else:
                        path = 'pose.bones[\"{bname}\"].location'.format(bname = name)

                    fc = action.fcurves.find(path, index=index)
                    if not fc:
                        fc = action.fcurves.new(path, index=index)

                    value = f[key](frame)
                    fc.keyframe_points.insert(frame['frame'], value)
            new_action = self.resample_action(action.name, "GST-Recorded", 60, 48)
            

        

    def resample_action(self,original_action_name, new_action_name, original_fps, target_fps):
        # Get original action
        action = bpy.data.actions[original_action_name]

        # Calculate new frame count (assuming the action starts from frame 1)
        original_frame_count = len(action.fcurves[0].keyframe_points) - 1  # -1 as it is zero-based
        new_frame_count = int(original_frame_count * (target_fps / original_fps))

        # Create a new action
        new_action = bpy.data.actions.new(name=new_action_name)

        # Copy fcurves from the old action to the new one
        for fcurve in action.fcurves:
            new_fcurve = new_action.fcurves.new(fcurve.data_path, index=fcurve.array_index)

            # Interpolate new keyframes
            for i in range(new_frame_count):
                # Equivalent to np.linspace(1, original_frame_count, new_frame_count)
                value = fcurve.evaluate(i * (original_fps / target_fps))
                new_fcurve.keyframe_points.insert(i, value, options={'FAST'})

        # Return new action
        return new_action



def saveAction(self, context):
        action = recorder.save_action(head=context.scene.saveHead, brows=context.scene.saveBrows, eyes=context.scene.saveEyes, eyelids=context.scene.saveEyelids, mouth=context.scene.saveMouth, sneer_cheecks=context.scene.saveSneer, mirror=context.scene.mirrorRecord)
        context.object.animation_data.action = action

class FaceStartRecordButtonOperator(bpy.types.Operator):
    bl_idname = "scene.face_start_record"
    bl_label = "Start Recording on Blender"

    def execute(self, context):
        recorder.start()
        return {'FINISHED'}

class FaceStopRecordButtonOperator(bpy.types.Operator):
    bl_idname = "scene.face_stop_record"
    bl_label = "Stop Recording"


    def execute(self, context):
        saveAction(self, context)
        return {'FINISHED'}


    
class FaceRecordPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Sophia'
    bl_idname = "VIEW3D_PT_face_record_panel"
    bl_label = "Face Record"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        # row.prop(bpy.context.scene, "faceRecordingHz")
        row.prop(bpy.context.scene, "mirrorRecord")
        row = layout.row()
        if not recorder.is_recording:
            self.layout.operator(FaceStartRecordButtonOperator.bl_idname)
        else:
            self.layout.operator(FaceStopRecordButtonOperator.bl_idname)
        
        row = layout.row()
        row.prop(bpy.context.scene, "saveHead")
        row.prop(bpy.context.scene, "saveEyes")
        row = layout.row()
        row.prop(bpy.context.scene, "saveEyelids")
        row.prop(bpy.context.scene, "saveBrows")
        row = layout.row()
        row.prop(bpy.context.scene, "saveMouth")
        row.prop(bpy.context.scene, "saveSneer")
        row = layout.row()
        self.layout.operator(LoadCSVOperator.bl_idname)


class LoadCSVOperator(bpy.types.Operator, ImportHelper):
    bl_idname = "load.csv"
    bl_label = "Load CSV File"

    filter_glob: StringProperty(
        default='*.csv',
        options={'HIDDEN'}
    )

    def execute(self, context):
        # Step 3: File selection and CSV parsing
        def try_float(s):
            try:
                return float(s)
            except ValueError:
                return s
        with open(self.filepath, 'r') as file:
            recorder.start()
            csv_data = csv.DictReader(file)
            for row in csv_data:
                frow = {k: try_float(v) for k, v in row.items()}
                recorder.add_frame(frow)
        saveAction(self, context)
        return {'FINISHED'}

recorder = Recorder()
