bl_info = {
    "name": "HRSDK Face Tools",
    "author": "Vytas Krisciunas",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Face Capture",
    "description": "Tool for recording animation from livelink",
    "warning": "",
    "wiki_url": "",
    "category": "Animation",
}
import sys
import os
# Try the dependencies that are shared to have priority so it wont have conflict with existing deps
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'deps'))
import bpy
from .livelink import FaceStartPortButtonOperator, FaceSetNeutralButtonOperator, FaceToggleUpdateButtonOperator, FaceBLUpdatePose, FaceLiveLinkPanel, FaceResetNeutralButtonOperator
from .streaming import FaceConnectROS, FaceDisconnectROS, FaceResetPoseButtonOperator, FaceStartStreamButtonOperator, FaceStopStreamButtonOperator,FaceStreamPanel, FaceStreaming
from .recording import LoadCSVOperator, FaceStartRecordButtonOperator, FaceStopRecordButtonOperator, FaceRecordPanel
from .utils import props

# Initially is not saved
props['faceGlobalTimerStarted'] = False



# Global timer for viweport functions

class FaceBLGlobalTimer(bpy.types.Operator):
    """Timer  Control"""
    bl_label = "Global Timer"
    bl_idname = 'wm.face_global_timer'

    _timer = None
    maxFPS = 50

    def execute(self, context):
        print("START GLOBAL TIMER")
        wm = context.window_manager
        self._timer = wm.event_timer_add(1/self.maxFPS, window=context.window)
        props['faceGlobalTimerStarted'] = True
        wm.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if not props['faceGlobalTimerStarted']:
            return self.cancel(context)
        return {'PASS_THROUGH'}

    def cancel(self, context):
        if self._timer:
            wm = context.window_manager
            wm.event_timer_remove(self._timer)

        return {'CANCELLED'}

    @classmethod
    def poll(cls, context):
        return True



# All classes should be explicitly registered by their class name
CLASSES = (
    FaceStartPortButtonOperator,
    FaceStartStreamButtonOperator,
    FaceStopStreamButtonOperator,
    FaceConnectROS, 
    FaceDisconnectROS,
    FaceResetPoseButtonOperator,
    FaceStartRecordButtonOperator,
    FaceStopRecordButtonOperator,
    FaceToggleUpdateButtonOperator,
    FaceSetNeutralButtonOperator,
    FaceBLGlobalTimer,
    FaceBLUpdatePose,
    FaceLiveLinkPanel,
    FaceRecordPanel,
    FaceStreamPanel,
    LoadCSVOperator,
    FaceResetNeutralButtonOperator,
    FaceStreaming
)


def register():
    props.register()
    for klass in CLASSES:
        bpy.utils.register_class(klass)
    

def unregister():

    props.unregister()
    
    for klass in CLASSES:
        bpy.utils.unregister_class(klass)

if __name__ == "__main__":
    register()