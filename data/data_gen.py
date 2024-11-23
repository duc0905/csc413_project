import bpy

class CameraOptions:
    # Camera position
    pos: tuple[float, float, float]

    look_at: tuple[float, float, float]
    up: tuple[float, float, float]

    # Focal length (mm)
    f: float

    def __init__(self,
                 pos: tuple[float, float, float],
                 look_at: tuple[float, float, float] = (0, 0, 0),
                 up: tuple[float, float, float] = (0, 1, 0),
                 f: float = 50) -> None:
        self.pos = pos
        self.look_at = look_at
        self.up = up
        self.f = f


class ImageOptions:
    size_x: int;
    size_y: int;

    def __init__(self, size_x: int, size_y: int) -> None:
        self.size_x = size_x
        self.size_y = size_y

def generate_image(
        modelfile: str,
        # object_opts: ObjectOptions,
        camera_opts: CameraOptions,
        img_opts: ImageOptions):
    pass

def make_scene(modelfile: str):
    """
    Make the scene empty with:
    - A light source at (0, 0, 3)
    - A camera at ()
    - A floor at the XZ-plane
    - A wall in the back
    """

    pass

bpy.context.scene.objects['Cube'].select_set(True)
bpy.ops.object.delete()

for obj in bpy.context.scene.objects:
    print(obj)

# print(bpy.context.active_object)
