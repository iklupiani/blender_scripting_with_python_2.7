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
    "get_context_override",
    )

import bpy

def get_context_override(context, area_type, region_type):
    override = {}
    override['scene'] = context.scene
    override['window'] = context.window
    override['screen'] = context.window.screen
    for area in override['screen'].areas:
        if area.type == area_type: # e.g. 'VIEW_3D' for viewport, 'IMAGE_EDITOR' for UV/Image Editor, etc.
            override['area'] = area
            break
    for region in override['area'].regions:
        if region.type == region_type: # e.g. 'WINDOW'
            override['region'] = region
    override['edit_object'] = context.edit_object
    return override

# Sample usage----------------------------------------------------    
#image_editor_context_override = get_context_override(bpy.context, 'IMAGE_EDITOR', 'WINDOW')

# Zoom in to the Unwrapped UV (In UV/Image Editor, View -> View Fit (View the entire image) or Shift-Home).
# Note that since we're zooming inside the UV/Image Editor area specifically, we have to pass the correct context override into 
# the call to bpy.ops.image.view_all so that Blender knows which area to perform the zoom in.
#bpy.ops.image.view_all(image_editor_context_override, fit_view=True)