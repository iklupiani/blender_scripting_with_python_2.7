import bpy
from mathutils import Euler
from math import radians

def load_image_empty(context, name, image_file_path, position, transparency, rotation_degrees = [90, 0, 0]):
    empty = bpy.data.objects.new(name, None)
    empty.empty_draw_type = 'IMAGE'
    empty.data = bpy.data.images.load(image_file_path)    
    empty.location = position
    empty.rotation_euler = Euler((radians(d) for d in rotation_degrees), 'XYZ')
    empty.empty_image_offset[0] = 0.25
    empty.empty_image_offset[1] = 0.25
    empty.empty_draw_size = 5
    empty.color[3] = transparency
    context.scene.objects.link(empty)
    context.scene.update() 

#Sample usage
load_image_empty(bpy.context, 'ref_front', 'D:/blenderbook/bsp_revisions/ch3/modeling_reference_front.jpg', (0, 0, 0), 0.75)