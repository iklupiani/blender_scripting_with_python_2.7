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
    "get_image_and_uv_editors",
    )

import bpy

def get_image_and_uv_editors(context):
    for area in context.screen.areas:
        if area.type == 'IMAGE_EDITOR':
            for space in area.spaces:
                if space.type == 'IMAGE_EDITOR':
                    return space, space.uv_editor
    return None, None

# Sample usage----------------------------------------------------
#image_editor, uv_editor = get_image_and_uv_editors(bpy.context)

# Turn on stretch color view to display faces of unwrapped 
# UVs in color.
#uv_editor.show_stretch = True

# Turn on live unwrap so whenever you edit the mesh or 
# change the seam in the viewport, the UVs are automatically
# updated to reflect the changes.
#uv_editor.use_live_unwrap = True