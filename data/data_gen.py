import bpy
import os
import pandas as pd
from pathlib import Path
from typing import Tuple

# Links
# https://docs.blender.org/manual/en/2.83/advanced/command_line/arguments.html
# blender.exe .\test.blend -b -P .\data_gen.py --addons import_off
# https://blender.stackexchange.com/questions/318254/does-blender-have-a-built-in-basic-material-library
# https://docs.blender.org/manual/en/2.83/addons/materials/material_library.html
# https://docs.blender.org/api/current/bpy.ops.mesh.html - look for primtive_...

dir_path = os.path.dirname(os.path.realpath(__file__))
dataset_path = os.path.join(dir_path, "ModelNet40")
train_path = os.path.join(dir_path, "train")
test_path = os.path.join(dir_path, "test")

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
    objectfile = os.path.join(dataset_path, modelfile)
    bpy.ops.import_mesh.off(filepath=objectfile)

    # Get the imported object
    obj_name = Path(objectfile).stem
    obj = bpy.context.scene.objects[obj_name]

    # Scale the thing
    m = [1000000, 1000000, 1000000]
    M = [-1000000, -1000000, -1000000]
    for point in obj.bound_box:
        for i in range(3):
            if m[i] > point[i]: m[i] = point[i]
            if M[i] < point[i]: M[i] = point[i]

    scale_down = [(M[i] - m[i]) / 2.0 for i in range(3)]
    s = max(scale_down)

    # Size after scale down
    sizes = [(M[i] - m[i]) / s for i in range(3)]
    # Move the center of the base to (0,0)
    obj.location[0] -= (m[0] / s + sizes[0] / 2)
    obj.location[1] -= (m[1] / s + sizes[1] / 2)
    obj.location[2] -= m[2] / s

    for i in range(3):
        obj.scale[i] /= s

    # Set the output file name
    bpy.context.scene.render.filepath = os.path.join(train_path, img_opts.filename)
    bpy.ops.render.render(write_still = True)

    # TODO: Remove the object from the scene
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.object.delete()


def main():
    # setup_tools()

    # Hide the hidden object
    for ob in bpy.context.scene.objects: ob.hide_render = ob.hide_get()

    metadata = pd.read_csv("metadata_modelnet40.csv")
    # NOTE: Just for testing, rendering the first 10 models instead of 1 thousand
    chairs = metadata[(metadata["class"] == "chair")]

    for index, model in chairs[chairs["split"] == "train"].head(5).iterrows():
        print(index, str(model["object_path"]))
        generate_image(str(model["object_path"]),
                       CameraOptions(pos=(-3.06, -13.9174, 5.47669)),
                       ImageOptions(512, 512,
                                    os.path.join(train_path, Path(str(model["object_path"])).stem + ".png")))
    # for model in chairs[chairs["split"] == "test"].head(5):
        # generate_image(model.object_path,
        #                CameraOptions(pos=(-3.06, -13.9174, 5.47669)),
        #                ImageOptions(512, 512,
        #                             os.path.join(test_path, Path(model.object_path).stem + ".png")))


main()
