# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

__all__ = (
    "create_image_data_block",
    "save_image_to_file",
    "export_uv_layout",
    "pack_image",
    )
    
import bpy

from Ch7.split_screen_area import *
from Ch7.view_fit import *
from Ch7.uv_settings import *

def create_image_data_block(context, name, type='UV_GRID', color=(0, 0, 0, 1)):
    if bpy.data.images.find(name) < 0:
    	# Create a new image data block with the specified name.
    	bpy.data.images.new(name=name, width=1024, height=1024, alpha=True, float_buffer=False, stereo3d=False)
    	bpy.data.images[name].generated_color = color
    	bpy.data.images[name].generated_type = type
    
    # Make this image data block the actively selected one (same as when you select it from the drop down list).
    split_screen_area(context, 'VERTICAL', 0.5, 'IMAGE_EDITOR', True)
    image_editor, uv_editor = get_image_and_uv_editors(context)
    image_editor.image = bpy.data.images[name]
    
    # Adjust zoom on the newly created image data block (In UV/Image Editor, View -> View Fit (View the entire image) or Shift-Home).
    # Note that since we're zooming inside the UV/Image Editor area specifically, we have to pass the correct context override into 
    # the operator call to bpy.ops.image.view_all so that Blender knows which area to perform the zoom in.
    image_editor_context_override = get_context_override(context, 'IMAGE_EDITOR', 'WINDOW')
    bpy.ops.image.view_all(image_editor_context_override, fit_view=True)      
    
def save_image_to_file(context, name, dirpath):
    # Make this image data block the actively selected one (same as when you select it from the drop down list).
    image_editor, uv_editor = get_image_and_uv_editors(context)
    image_editor.image = bpy.data.images[name]
    
    # Save the image data block to file.
    image_editor_context_override = get_context_override(context, 'IMAGE_EDITOR', 'WINDOW')
    bpy.ops.image.save_as(image_editor_context_override, save_as_render=False, copy=False, \
    filepath=dirpath+name+'.png', relative_path=False, show_multiview=False, use_multiview=False)
    
def export_uv_layout(name, dirpath):
    bpy.ops.uv.export_layout(filepath=dirpath+name+'.png', check_existing=True, \
    export_all=False, modified=False, mode='PNG', size=(1024, 1024), opacity=0.25)
    
def pack_image(context, name):
    # Make this image data block the actively selected one (same as when you select it from the drop down list).
    image_editor, uv_editor = get_image_and_uv_editors(context)
    image_editor.image = bpy.data.images[name]
    
    # Get a context override for the UV/Image Editor.
    image_editor_context_override = get_context_override(context, 'IMAGE_EDITOR', 'WINDOW')
    # Pack the active image data block into the *.blend file.    
    bpy.ops.image.pack(image_editor_context_override)

# Sample usage----------------------------------------------------
# Test creating image data block and saving image data block to file.
#image_name = "test_image_block1"
#create_image_data_block(bpy.context, image_name)
#save_image_to_file(bpy.context, image_name, "D:\\blenderbook\\Ch6 - UV Mapping\\")

# Test packing a single image.
#pack_image(bpy.context, 'front24.jpg')

# Test unpacking a single image to file.
#bpy.ops.file.unpack_item(method='WRITE_LOCAL', id_name="front24.jpg")

# Test exporting the current active layout to file.
#export_uv_layout("uv_layout", "D:\\blenderbook\\Ch6 - UV Mapping\\")
