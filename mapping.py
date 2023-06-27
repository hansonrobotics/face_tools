import math
from functools import partial

def convert(b, w, upper, lower, frame):
    ret = 0
    for i in range(len(b)):
        ret += frame[b[i]] * w[i]
    return max(min(ret,upper), lower)

def convert_head_x(frame):                                                                             
    return math.tan(-frame['HeadYaw']*math.pi/2) * 4

def convert_head_roll(frame):
    return min(frame['HeadRoll']*math.pi/2, 0.366519)

def convert_head_z(frame):
    return math.tan(frame['HeadPitch']*math.pi/2) * 4

def convert_eyes_x(frame):
    yaw = frame['HeadYaw'] - (frame['LeftEyeYaw']+frame['RightEyeYaw'])/2
    return math.tan(yaw*math.pi/2) * 4

def convert_eyes_z(frame):
    pitch = frame['HeadPitch'] - (frame['LeftEyePitch']+frame['RightEyePitch'])/2
    return math.tan(pitch*math.pi/2) * 4

Functions = {
 'eye_offset:0' : convert_eyes_x,
 'eye_offset:2' : convert_eyes_z,
 'head:0' : convert_head_x,
 'head:1' : convert_head_roll,
 'head:2' : convert_head_z,
 'chin:2' : partial(convert, ['JawOpen', 'MouthClose', 'MouthFunnel', 'MouthPucker', 'MouthShrugUpper', 'MouthShrugLower'], [0.16, -0.16, 0.08, -0.08, -0.06, -0.06], 0.16, 0),
 'nostril_L:1' : partial(convert, ['NoseSneerLeft'], [0.08], 0.04, 0),
 'nostril_R:1' : partial(convert, ['NoseSneerRight'], [0.08], 0.04, 0),
 'cheek_L:1' : partial(convert, ['CheekSquintLeft', 'EyeSquintLeft'], [0.06, 0.04], 0.04, 0),
 'cheek_R:1' : partial(convert, ['CheekSquintRight', 'EyeSquintRight'], [0.06, 0.04], 0.04, 0),
 'lip_D_L:1' : partial(convert, 
    ['MouthFunnel', 'MouthPucker', 'MouthSmileLeft', 'MouthFrownLeft', 'MouthRollLower', 'MouthShrugLower', 'MouthPressLeft', 'MouthLowerDownLeft'],
    [-0.02, -0.03, -0.00, -0.04, -0.04, 0.04, -0.02, 0.01], 0.04, -0.04),
 'lip_D_R:1' : partial(convert, 
    ['MouthFunnel', 'MouthPucker', 'MouthSmileRight', 'MouthFrownRight', 'MouthRollLower', 'MouthShrugLower', 'MouthPressLeft', 'MouthLowerDownRight'], 
    [-0.02, -0.03, -0.00, -0.04, -0.04, 0.04, -0.02, 0.01], 0.04, -0.04),
 'lip_D:1' : partial(convert, 
    ['MouthFunnel', 'MouthPucker', 'MouthSmileLeft', 'MouthSmileRight', 'MouthFrownLeft', 'MouthFrownRight', 'MouthRollLower', 'MouthShrugLower'], 
    [-0.02, -0.02, -0.000, -0.000, -0.02, -0.02, -0.04, 0.04], 0.04, -0.04),
 'lip_U_L:1' : partial(convert, 
    ['MouthFunnel', 'MouthPucker', 'MouthSmileLeft', 'MouthFrownLeft', 'MouthRollUpper', 'MouthShrugUpper', 'MouthPressLeft', 'MouthUpperUpLeft'],
    [-0.02, -0.03, 0.01, 0.01, -0.04, 0.01, 0.01, 0.01], 0.04, -0.04),
 'lip_U_R:1' : partial(convert, 
    ['MouthFunnel', 'MouthPucker', 'MouthSmileRight', 'MouthFrownRight', 'MouthRollUpper', 'MouthShrugUpper', 'MouthPressRight', 'MouthUpperUpRight'], 
    [-0.02, -0.03, 0.01, 0.01, -0.04, 0.01, 0.01, 0.01], 0.04, -0.04),
 'lip_U:1' : partial(convert, 
    ['MouthFunnel', 'MouthPucker', 'MouthSmileLeft', 'MouthSmileRight', 'MouthFrownLeft', 'MouthFrownRight', 'MouthRollUpper', 'MouthShrugUpper'], 
    [-0.02, -0.02, 0.005, 0.005, 0.005, 0.005, -0.04, 0.01], 0.04, -0.04),
 'mouth_C_L:1' : partial(convert, 
    ['MouthFunnel', 'MouthPucker', 'MouthLeft', 'MouthRight', 'MouthSmileLeft', 'MouthStretchLeft'],
    [-0.06, -0.06, 0.04, -0.04, 0.08, 0.08], 0.04, -0.04),
 'mouth_C_R:1' : partial(convert, 
    ['MouthFunnel', 'MouthPucker', 'MouthLeft', 'MouthRight', 'MouthSmileRight', 'MouthStretchRight'],
    [-0.06, -0.06, -0.04, 0.04, 0.08, 0.08], 0.04, -0.04),
 'mouth_D_L:1' : partial(convert, ['JawOpen', 'MouthFrownLeft', 'MouthStretchLeft'], [-0.05, 0.08, 0.04], 0.04, 0),
 'mouth_D_R:1' : partial(convert, ['JawOpen', 'MouthFrownRight', 'MouthStretchRight'], [-0.05, 0.08, 0.04], 0.04, 0),
 'mouth_U_L:1' : partial(convert, ['MouthSmileLeft'], [0.08], 0.04, 0),
 'mouth_U_R:1' : partial(convert, ['MouthSmileRight'], [0.08], 0.04, 0),
 'brow.inner.L:1' : partial(convert, ['BrowInnerUp', 'BrowDownLeft'], [0.06, -0.06], 0.04, -0.04),
 'brow.inner.R:1' : partial(convert, ['BrowInnerUp', 'BrowDownRight'], [0.06, -0.06], 0.04, -0.04),
 'brow.C:1' : partial(convert, ['BrowInnerUp', 'BrowDownLeft', 'BrowDownRight'], [0.06, -0.03, -0.03], 0.04, -0.04),
 'brow.L:1' : partial(convert, ['BrowOuterUpLeft', 'BrowDownLeft'], [0.06, -0.06], 0.04, -0.04),
 'brow.R:1' : partial(convert, ['BrowOuterUpRight', 'BrowDownRight'], [0.06, -0.06], 0.04, -0.04),
 'eyelid_LO_L:1' : partial(convert, ['EyeSquintLeft'], [-0.04], 0.04, -0.04),
 'eyelid_LO_R:1' : partial(convert, ['EyeSquintRight'], [-0.04], 0.04, -0.04),
 'eyelid_UP_L:1' : partial(convert, ['EyeBlinkLeft', 'EyeWideLeft'], [-0.04, 0.04], 0.04, -0.04), 
 'eyelid_UP_R:1' : partial(convert, ['EyeBlinkRight', 'EyeWideRight'], [-0.04, 0.04], 0.04, -0.04)
}

MirroredFunctions = {
 'eye_offset:0' : lambda frame : -convert_eyes_x(frame),
 'eye_offset:2' : convert_eyes_z,
 'head:0' : lambda frame : -convert_head_x(frame),
 'head:1' : lambda frame: -convert_head_roll(frame),
 'head:2' : convert_head_z,
 'chin:2' : Functions['chin:2'],
 'nostril_L:1' : Functions['nostril_R:1'],
 'nostril_R:1' : Functions['nostril_L:1'],
 'cheek_L:1' : Functions['cheek_R:1'],
 'cheek_R:1' : Functions['cheek_L:1'],
 'lip_D_L:1' : Functions['lip_D_R:1'],
 'lip_D_R:1' : Functions['lip_D_L:1'],
 'lip_D:1' : Functions['lip_D:1'],
 'lip_U_L:1' : Functions['lip_U_R:1'],
 'lip_U_R:1' : Functions['lip_U_L:1'],
 'lip_U:1' : Functions['lip_U:1'],
 'mouth_D_L:1' : Functions['mouth_D_R:1'],
 'mouth_D_R:1' : Functions['mouth_D_L:1'],
 'mouth_C_L:1' : Functions['mouth_C_R:1'],
 'mouth_C_R:1' : Functions['mouth_C_L:1'],
 'mouth_U_L:1' : Functions['mouth_U_R:1'],
 'mouth_U_R:1' : Functions['mouth_U_L:1'],
 'brow.inner.L:1' : Functions['brow.inner.R:1'],
 'brow.inner.R:1' : Functions['brow.inner.L:1'],
 'brow.C:1' : Functions['brow.C:1'],
 'brow.L:1' : Functions['brow.R:1'],
 'brow.R:1' : Functions['brow.L:1'],
 'eyelid_LO_L:1' : Functions['eyelid_LO_R:1'],
 'eyelid_LO_R:1' : Functions['eyelid_LO_L:1'],
 'eyelid_UP_L:1' : Functions['eyelid_UP_R:1'],
 'eyelid_UP_R:1' : Functions['eyelid_UP_L:1']
}

StreamingFunctions = {
 'EyesYaw': partial(convert, ['LeftEyeYaw', 'RightEyeYaw'], [-math.pi/4, -math.pi/4], 2, -2),
 'EyesPitch': partial(convert, ['LeftEyePitch', 'RightEyePitch'], [-math.pi/4, -math.pi/4], 2, -2),
 'HeadYaw' : partial(convert, ['HeadYaw'], [-math.pi/2], 2, -2),
 'HeadRoll' : partial(convert, ['HeadRoll'], [math.pi/2], 2, -2),
 'HeadPitch' : partial(convert, ['HeadPitch'], [math.pi/2], 2, -2),
 'Jaw' : partial(convert, ['JawOpen', 'MouthClose'], [1, -1], 1, 0),
 'SneerLeft' : lambda x : 25 * Functions['nostril_L:1'](x),
 'SneerRight' : lambda x : 25 * Functions['nostril_R:1'](x),
 'CheekSquintLeft' : lambda x : 25 * Functions['cheek_L:1'](x),
 'CheekSquintRight' : lambda x : 25 * Functions['cheek_R:1'](x),
 'LowerLipLeft' : lambda x : 25 * Functions['lip_D_L:1'](x),
 'LowerLipRight' : lambda x : 25 * Functions['lip_D_R:1'](x),
 'LowerLipCenter' : lambda x : 25 * Functions['lip_D:1'](x),
 'UpperLipLeft' : lambda x : 25 * Functions['lip_U_L:1'](x),
 'UpperLipRight' : lambda x : 25 * Functions['lip_U_R:1'](x),
 'UpperLipCenter' : lambda x : 25 * Functions['lip_U:1'](x),
 'FrownLeft' : lambda x : 25 * Functions['mouth_D_L:1'](x),
 'FrownRight' : lambda x : 25 * Functions['mouth_D_R:1'](x),
 'LipStretchLeft' : lambda x : 25 * Functions['mouth_C_L:1'](x),
 'LipStretchRight' : lambda x : 25 * Functions['mouth_C_R:1'](x),
 'SmileLeft' : lambda x : 25 * Functions['mouth_U_L:1'](x),
 'SmileRight' : lambda x : 25 * Functions['mouth_U_R:1'](x),
 'BrowInnerLeft' : lambda x : 25 * Functions['brow.inner.L:1'](x),
 'BrowInnerRight' : lambda x : 25 * Functions['brow.inner.R:1'](x),
 'BrowCenter' :  lambda x : 25 * Functions['brow.C:1'](x),
 'BrowOuterLeft' : lambda x : 25 * Functions['brow.L:1'](x),
 'BrowOuterRight' : lambda x : 25 * Functions['brow.R:1'](x),
 'LowerLidLeft' : lambda x : 25 * Functions['eyelid_LO_L:1'](x),
 'LowerLidRight' : lambda x : 25 * Functions['eyelid_LO_R:1'](x),
 'UpperLidLeft' : lambda x : 25 * Functions['eyelid_UP_L:1'](x),
 'UpperLidRight' :lambda x : 25 * Functions['eyelid_UP_R:1'](x),
}

