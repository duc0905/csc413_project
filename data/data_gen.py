import bpy
import os
import pandas as pd
from pathlib import Path
from typing import Tuple
import pickle
import numpy as np
import math

# Links
# https://docs.blender.org/manual/en/2.83/advanced/command_line/arguments.html
# blender.exe .\test.blend -b -P .\data_gen.py --addons import_off
# https://blenderartists.org/t/raytracing-to-obtain-vertices-visible-to-camera/1362124
# https://pandas.pydata.org/docs/user_guide/10min.html#basic-data-structures-in-pandas
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

def move_camera(options: CameraOptions):
    cx, cy, cz = options.pos
    tx, ty, tz = options.look_at
    ox, oy, oz = tx-cx, ty-cy, tz-cz
    f = options.f
    camera = bpy.data.objects["Camera"]
    camera.location = options.pos
    rot_z = math.atan(oy/ox)
    #if ox > 0 and rot_z < 0:
    #    rot_z += math.pi
    #elif ox < 0 and rot_z > 0:
    #    rot_z -= math.pi
    rot_x = math.atan(-math.sqrt(ox ** 2 + oy ** 2)/oz)
    if (rot_x < 0):
        rot_x += math.pi
    camera.rotation_euler = (rot_x, 0, rot_z - math.pi/2)
    print(camera.rotation_euler)

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

    move_camera(camera_opts)

    # Set the output file name
    bpy.context.scene.render.filepath = os.path.join(train_path, img_opts.filename + "/img.png")
    bpy.context.scene.render.resolution_x = img_opts.size_x
    bpy.context.scene.render.resolution_y = img_opts.size_y
    bpy.ops.render.render(write_still = True)

    # NOTE: Get the visible vertices
    visible_verts = []
    hidden_verts = []
    cam_pos = bpy.data.objects["Camera"].location
    for vert in obj.data.vertices:
        v = obj.matrix_world @ vert.co
        d = cam_pos - v
        d.normalize()
        _v = v + 1e-6 * d

        hit, loc, normal, index, ob, mat = bpy.context.scene.ray_cast(bpy.context.view_layer, _v, d)
        if not hit: # Can be seen by the camera
            visible_verts.append([v[0],v[1],v[2]])
        else:
            hidden_verts.append([v[0],v[1],v[2]])

    # TODO: Save visible_verts and hidden_verts somewhere (in a file)
    hidden_verts = np.array(hidden_verts)
    visible_verts = np.array(visible_verts)
    
    hidden_verts_path = os.path.join(train_path, img_opts.filename + "/hidden")
    visible_verts_path = os.path.join(train_path, img_opts.filename + "/visible")
    print(hidden_verts_path)
    with open(hidden_verts_path, 'wb') as f:
        pickle.dump(hidden_verts, f)
    with open(visible_verts_path, 'wb') as f:
        pickle.dump(visible_verts, f)
    # with open(visible_verts_path, 'rb') as f:
    #     load = pickle.load(f)
    #     print(load)

    # NOTE: Remove the object from the scene
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.object.delete()


def main():
    # setup_tools()

    # Hide the hidden object
    for ob in bpy.context.scene.objects: ob.hide_render = ob.hide_get()
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects['Cube'].select_set(True)
    bpy.ops.object.delete()
    metadata = pd.read_csv("metadata_modelnet40.csv")

    chairs = metadata[(metadata["class"] == "chair")]

    # NOTE: Just for testing, rendering the first 10 models instead of 1 thousand
    for index, model in chairs[chairs["split"] == "train"].head(5).iterrows():
        generate_image(str(model["object_path"]),
                       CameraOptions(pos=(-3.06, -13.9174, 5.47669), look_at=(0,0,1)),
                       ImageOptions(128, 128, os.path.join(train_path, Path(str(model["object_path"])).stem)))
    # for model in chairs[chairs["split"] == "test"].head(5):
    #     generate_image(model.object_path,
    #                    CameraOptions(pos=(-3.06, -13.9174, 5.47669)),
    #                    ImageOptions(512, 512,
    #                                 os.path.join(test_path, Path(model.object_path).stem + ".png")))


main()
