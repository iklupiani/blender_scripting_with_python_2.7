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
    "split_screen_area",
    )
    
import bpy

def split_screen_area(context, split_dir, split_ratio, type_of_new_area, check_existing=False):
    existing_areas = list(context.screen.areas)

    if check_existing:
        for area in existing_areas:
            # Found an existing area of matching type
            if area.type == type_of_new_area:
                return area

    bpy.ops.screen.area_split(direction=split_dir, factor=split_ratio)

    for area in context.screen.areas:
        if area not in existing_areas:
            area.type = type_of_new_area
            return area
        
# Sample usage----------------------------------------------------
# Split the area in half vertically, and set the new area 
# to a UV/Image Editor.
#new_area = split_screen_area(bpy.context, 'VERTICAL', 0.5, 'IMAGE_EDITOR')