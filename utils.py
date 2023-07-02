import bpy

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class bpy_props(metaclass=Singleton):
    def __init__(self):
        self.scene_props = {}
        self.local_props = {}

    def add(self, prop, name, default, min = None, max=None):
        '''
            Add scene property
        '''
        if type(default) == bool:
            self.scene_props[prop] =  bpy.props.BoolProperty(name = name, default = default)
        if type(default) == str:
            self.scene_props[prop] =  bpy.props.StringProperty(name = name, default = default)
        if type(default) == int:
            self.scene_props[prop] =  bpy.props.IntProperty(name = name, default = default, min = min, max = max)
        if type(default) == float:
            self.scene_props[prop] =  bpy.props.FloatProperty(name = name, default = default, min = min, max = max)


    def register(self):
        for prop_name, prop_value in self.scene_props.items():
            setattr(bpy.types.Scene, prop_name, prop_value)
    
    def unregister(self):
        for prop_name in self.scene_props:
            delattr(bpy.types.Scene, prop_name)
        self.scene_props = []
    
    def __getitem__(self, __name: str):
        if __name in self.scene_props:
            return getattr(bpy.context.scene, __name)
        if __name in self.local_props:
            return self.local_props[__name]        
        raise KeyError(f"Property {__name} not found")

    def __setitem__(self, __name: str, __value) -> None:
        if __name in self.scene_props:
            setattr(bpy.context.scene, __name, __value)
        else:   
            self.local_props[__name] = __value        

props = bpy_props()