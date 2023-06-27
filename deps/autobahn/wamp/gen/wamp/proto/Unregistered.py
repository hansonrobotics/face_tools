# automatically generated by the FlatBuffers compiler, do not modify

# namespace: proto

import flatbuffers
from flatbuffers.compat import import_numpy
np = import_numpy()

class Unregistered(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAs(cls, buf, offset=0):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = Unregistered()
        x.Init(buf, n + offset)
        return x

    @classmethod
    def GetRootAsUnregistered(cls, buf, offset=0):
        """This method is deprecated. Please switch to GetRootAs."""
        return cls.GetRootAs(buf, offset)
    # Unregistered
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # Unregistered
    def Session(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint64Flags, o + self._tab.Pos)
        return 0

    # Unregistered
    def Request(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint64Flags, o + self._tab.Pos)
        return 0

    # Unregistered
    def Registration(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Uint64Flags, o + self._tab.Pos)
        return 0

    # Unregistered
    def Reason(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(10))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

def UnregisteredStart(builder): builder.StartObject(4)
def Start(builder):
    return UnregisteredStart(builder)
def UnregisteredAddSession(builder, session): builder.PrependUint64Slot(0, session, 0)
def AddSession(builder, session):
    return UnregisteredAddSession(builder, session)
def UnregisteredAddRequest(builder, request): builder.PrependUint64Slot(1, request, 0)
def AddRequest(builder, request):
    return UnregisteredAddRequest(builder, request)
def UnregisteredAddRegistration(builder, registration): builder.PrependUint64Slot(2, registration, 0)
def AddRegistration(builder, registration):
    return UnregisteredAddRegistration(builder, registration)
def UnregisteredAddReason(builder, reason): builder.PrependUOffsetTRelativeSlot(3, flatbuffers.number_types.UOffsetTFlags.py_type(reason), 0)
def AddReason(builder, reason):
    return UnregisteredAddReason(builder, reason)
def UnregisteredEnd(builder): return builder.EndObject()
def End(builder):
    return UnregisteredEnd(builder)