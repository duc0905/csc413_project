import bpy
import os
from typing import Tuple

# Links
# https://docs.blender.org/manual/en/2.83/advanced/command_line/arguments.html
# blender.exe .\test.blend -b -P .\data_gen.py --addons import_off   
# https://blender.stackexchange.com/questions/318254/does-blender-have-a-built-in-basic-material-library
# https://docs.blender.org/manual/en/2.83/addons/materials/material_library.html
# https://docs.blender.org/api/current/bpy.ops.mesh.html - look for primtive_...

dataset_path = "./ModelNet40"
models = ["chair/test/chair_0890.off"]

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
    filename: str;

    def __init__(self, size_x: int, size_y: int, filepath: str) -> None:
        self.size_x = size_x
        self.size_y = size_y
        self.filename = filepath

def generate_image(
        modelfile: str,
        # object_opts: ObjectOptions,
        camera_opts: CameraOptions,
        img_opts: ImageOptions):

    # Load the model
    # NOTE: Name the object 'THE_THING'


    # Scale the thing
    the_thing = bpy.context.scene.objects['THE_THING']
    m = [1000000, 1000000, 1000000]
    M = [-1000000, -1000000, -1000000]
    for point in the_thing.bound_box:
        if m[0] > point[0]: m[0] = point[0]
        if M[0] < point[0]: M[0] = point[0]
        if m[1] > point[1]: m[1] = point[1]
        if M[1] < point[1]: M[1] = point[1]
        if m[2] > point[2]: m[2] = point[2]
        if M[2] < point[2]: M[2] = point[2]

    s = [(M[i] - m[i]) / 2.0 for i in range(3)]
    the_real_scale = s[0]
    if s[1] > the_real_scale: the_real_scale = s[1]
    if s[2] > the_real_scale: the_real_scale = s[2]
    for i in range(3): the_thing.scale[i] /= the_real_scale



    # Set the output file name
    dir_path = os.path.dirname(os.path.realpath(__file__))
    bpy.context.scene.render.filepath = os.path.join(dir_path, img_opts.filename)
    bpy.ops.render.render(write_still = True)


# def setup_tools():
#     # bpy.ops.preferences.addon_enable(module='import_off')
#     bpy.ops.preferences.addon_enable(module='materials_library_vx')
#
#     print("Add-on list:")
#     for addon in bpy.context.preferences.addons.keys():
#         print(addon)
#     print("=============")


def main():
    # setup_tools()

    for ob in bpy.context.scene.objects: ob.hide_render = ob.hide_get()

    for modelfile in models:
        generate_image(modelfile, CameraOptions((-3.06, -13.9174, 5.47669)), ImageOptions(512, 512, modelfile + ".png"))


main()
