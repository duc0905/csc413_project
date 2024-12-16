import bpy
import os
import pandas as pd
from pathlib import Path
from typing import Tuple
import pickle
import numpy as np
import math
from mathutils import Vector

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

vis_cnt = 0
hid_cnt = 0

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
    p = Vector(options.pos)
    point = Vector(options.look_at)
    direction = point - p
    f = options.f
    camera = bpy.data.objects["Camera"]
    camera.location = options.pos
    rot_quat = direction.to_track_quat('-Z', 'Y')

    # rot_z = math.atan(oy/ox)
    #if ox > 0 and rot_z < 0:
    #    rot_z += math.pi
    #elif ox < 0 and rot_z > 0:
    #    rot_z -= math.pi
    # rot_x = math.atan(-math.sqrt(ox ** 2 + oy ** 2)/oz)
    # if (rot_x < 0):
    #     rot_x += math.pi
    # camera.rotation_euler = (rot_x, 0, rot_z - math.pi/2)
    camera.rotation_euler = rot_quat.to_euler()
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
    obj_name = Path(modelfile).stem
    print(modelfile)
    print(obj_name)
    print(bpy.context.scene.objects.keys())
    obj = bpy.context.scene.objects[0]

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

    vis = len(visible_verts)
    hid = len(hidden_verts)
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

    return vis, hid


def main():
    # setup_tools()

    # Hide the hidden object
    for ob in bpy.context.scene.objects: ob.hide_render = ob.hide_get()
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects['Cube'].select_set(True)
    bpy.ops.object.delete()
    metadata = pd.read_csv("metadata_modelnet40.csv")

    cups = metadata[(metadata["class"] == "cup")]
    viss = []
    hids = []

    cam_opts = [
        CameraOptions(pos=(-3.0, -14.0, 5.0), look_at=(0,0,1)),
        CameraOptions(pos=(3.0, -13.0, 4.0), look_at=(0,0,1)),
        CameraOptions(pos=(-7.0, -8.0, 2.5), look_at=(0,0,1)),
        CameraOptions(pos=(7.0, -8.0, 10.8), look_at=(0,0,1)),
    ]

    for _, model in cups[cups["split"] == "train"].iterrows():
        for i, cam_opt in enumerate(cam_opts):
            vis, hid = generate_image(str(model["object_path"]),
                           cam_opt,
                           ImageOptions(128, 128, os.path.join(train_path, Path(str(model["object_path"])).stem + str(i))))
            viss.append(vis)
            hids.append(hid)

    for _, model in cups[cups["split"] == "test"].iterrows():
        for i, cam_opt in enumerate(cam_opts):
            vis, hid = generate_image(str(model["object_path"]),
                           cam_opt,
                           ImageOptions(128, 128, os.path.join(test_path, Path(str(model["object_path"])).stem + str(i))))

    print(viss)
    print("Mean, var: ", np.mean(np.array(viss)), np.var(np.array(viss)))


main()
