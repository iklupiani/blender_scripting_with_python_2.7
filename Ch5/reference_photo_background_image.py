# reference_photo_background_image.py (download from the book
import bpy
from math import radians

def load_background_image(context, filepath):
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            space_data = area.spaces.active
            background_image = space_data.background_images.new()
            background_image.image = bpy.data.images.load(filepath)

            # One of the values found in ['BOTTOM','TOP,'ALL','CAMERA
            background_image.view_axis = 'FRONT'

            # A number between 0 and 1 that controls the transparency of the
            # image.
            background_image.opacity = 0.5

            # If true, show in front of other objects in the viewport.
            background_image.show_on_foreground = True

            # Offset image horizontally/vertically from the world origin.
            background_image.offset_x = 0.5
            background_image.offset_y = 0.25

            # Rotation, ortho view only.
            background_image.rotation = radians(45) # 45 deg. to radians.

            # Scaling factor, ortho view only.
            background_image.size = 5.00

            space_data.show_background_images = True
            context.scene.update()
            break

#Sample usage
load_background_image(bpy.context, 'D:/blenderbook/bsp_revisions/ch3/modeling_reference_front.jpg')