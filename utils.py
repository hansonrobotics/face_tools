import bpy

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class bpy_props (metaclass=Singleton):
    def __init__(self):
        self.props = []

    def add(self, prop, name, default, min = None, max=None):
        # Default propertires
        if type(default) == bool:
            self.props.append((prop, bpy.props.BoolProperty(name = name, default = default)))
        if type(default) == str:
            self.props.append((prop, bpy.props.StringProperty(name = name, default = default)))
        if type(default) == int:
            self.props.append((prop, bpy.props.IntProperty(name = name, default = default, min = min, max = max)))
        if type(default) == float:
            self.props.append((prop, bpy.props.FloatProperty(name = name, default = default, min = min, max = max)))


    def register(self):
        for (prop_name, prop_value) in self.props:
            setattr(bpy.types.Scene, prop_name, prop_value)
    
    def unregister(self):
        for (prop_name, prop_value) in self.props:
            delattr(bpy.types.Scene, prop_name)
        self.props = []
    
props = bpy_props()