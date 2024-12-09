import bpy
import os
from typing import Tuple
import math

# Links
# https://docs.blender.org/manual/en/2.83/advanced/command_line/arguments.html
# https://blender.stackexchange.com/questions/318254/does-blender-have-a-built-in-basic-material-library
# https://docs.blender.org/manual/en/2.83/addons/materials/material_library.html
# https://docs.blender.org/api/current/bpy.ops.mesh.html - look for primtive_...

dataset_path = "./ModelNet40"
test_models = ["chair/test/chair_0890.off"]

class CameraOptions:
    # Camera position
    pos: Tuple[float, float, float]

    look_at: Tuple[float, float, float]
    up: Tuple[float, float, float]

    # Focal length (mm)
    f: float

    def __init__(self,
                 pos: Tuple[float, float, float],
                 look_at: Tuple[float, float, float] = (0, 0, 0),
                 up: Tuple[float, float, float] = (0, 1, 0),
                 f: float = 50) -> None:
        self.pos = pos
        self.look_at = look_at
        self.up = up
        self.f = f


class ImageOptions:
    size_x: int;
    size_y: int;
    filepath: str;

    def __init__(self, size_x: int, size_y: int, filepath: str) -> None:
        self.size_x = size_x
        self.size_y = size_y
        self.filepath = filepath

def generate_image(
        modelfile: str,
        # object_opts: ObjectOptions,
        camera_opts: CameraOptions,
        img_opts: ImageOptions):
    # TODO:
    pass


def create_light_source(
        x: int,
        y: int,
        z: int,
        energy: int):
    # https://stackoverflow.com/questions/17355617/can-you-add-a-light-source-in-blender-using-python
    light_data = bpy.data.lights.new(name="light", type='POINT')
    light_data.energy = energy
    light_object = bpy.data.objects.new(name="light", object_data=light_data)
    light_object.location = (x, y, z)

    bpy.context.collection.objects.link(light_object)
    bpy.context.view_layer.objects.active = light_object
    pass

def make_scene(modelfile: str):
    """
    Make the scene empty with:
    - A light source at (0, 0, 3)
    - A camera
        - position at (hmmm TODO)
        - looking at (0, 0, 0)
        - focal length 50mm
    - A floor at the XZ-plane (a plane)
    - A wall in the back (also a plane)
    """

    # TODO:
    try:
        filepath = os.path.join(dataset_path, modelfile)
        # filepath = "./ModelNet40/chair/test/chair_0890.off"
        print("Import: ", bpy.ops.import_mesh.off(filepath=filepath))
        create_light_source(0, 0, 3)
        print("Create_light_source")
        
    except Exception as e:
        print("Fk", e)
    pass

def setup_tools():
    bpy.ops.preferences.addon_enable(module='import_off')
    bpy.ops.preferences.addon_enable(module='materials_library_vx')

    print("Add-on list:")
    for addon in bpy.context.preferences.addons.keys():
        print(addon)
    print("=============")


def main():
    setup_tools()

    # Select the damn default cube
    bpy.context.scene.objects['Cube'].select_set(True)
    # Delete the selected object(s)
    bpy.ops.object.delete()

    for model in test_models:
        make_scene(model)

    for obj in bpy.context.scene.objects:
        print(obj)

main()
