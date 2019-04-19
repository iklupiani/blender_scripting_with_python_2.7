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
    "apply_all_modifiers",
    "apply_given_modifier",
    )
    
import bpy

def apply_all_modifiers(context, obj):    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    context.scene.objects.active = obj
    bpy.ops.object.mode_set(mode='OBJECT')

    for m in obj.modifiers:
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=m.name)
        
def apply_given_modifier(context, obj, modifier_type, modifier_name):
    bpy.ops.object.mode_set(mode='OBJECT')   
    context.scene.objects.active = obj
    bpy.ops.object.mode_set(mode='OBJECT')

    for m in obj.modifiers:
        if m.type == modifier_type and m.name == modifier_name:
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier=m.name)
            break
    
# Sample usage----------------------------------------------------
# Apply all modifiers of the object named 'test_cube'.
#apply_all_modifiers(bpy.context, bpy.context.scene.objects['test_cube'])
# Apply the bevel modifier named 'b' on the 'test_cube' object's modifier stack.
#apply_given_modifier(bpy.context, bpy.context.scene.objects['test_cube'], 'BEVEL', 'b')