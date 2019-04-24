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
    "generate_and_seam_cube",
    "unwrap_model",
    "configure_viewport_settings_for_visualizing_uvs",
    )

import bpy
import bmesh

from Ch7.split_screen_area import *
from Ch7.view_fit import *
from Ch7.uv_settings import *
from Ch7.create_and_save_images import *

def generate_and_seam_cube(context, obj_name='cube_obj', side_length=1, center=(0, 0, 0)):
    # cube_mesh is an empty placeholder mesh
    cube_mesh = bpy.data.meshes.new(name='cube_mesh')
    # Create a new mesh object that uses cube_mesh as its mesh data.
    cube_obj = bpy.data.objects.new(name=obj_name, object_data=cube_mesh)
    # Link the object to the scene.
    context.scene.objects.link(cube_obj)

    # Even though cube_obj currently has an empty mesh, we still need to put it in 
    # EDIT mode in order to add stuff to it through bmesh.
    context.scene.objects.active = cube_obj
    bpy.ops.object.mode_set(mode = 'EDIT')

    # Create a bmesh instance bm based on cube_mesh
    bm = bmesh.from_edit_mesh(cube_mesh)

    # Then add stuff to my_mesh through bm
    half_side_len = side_length/2
    bottom_z = center[2] - half_side_len
    top_z = center[2] + half_side_len
    # verts of the bottom face, counterclockwise.
    #         3  2
    #         0  1
    verts = []
    verts.append(bm.verts.new((center[0]+half_side_len, center[1]-half_side_len, bottom_z)))
    verts.append(bm.verts.new((center[0]+half_side_len, center[1]+half_side_len, bottom_z)))
    verts.append(bm.verts.new((center[0]-half_side_len, center[1]+half_side_len, bottom_z)))
    verts.append(bm.verts.new((center[0]-half_side_len, center[1]-half_side_len, bottom_z)))
    bottom_face = verts[0:4]
    # verts of the top face, counterclockwise.
    #         7  6
    #         4  5
    verts.append(bm.verts.new((center[0]+half_side_len, center[1]-half_side_len, top_z)))
    verts.append(bm.verts.new((center[0]+half_side_len, center[1]+half_side_len, top_z)))
    verts.append(bm.verts.new((center[0]-half_side_len, center[1]+half_side_len, top_z)))
    verts.append(bm.verts.new((center[0]-half_side_len, center[1]-half_side_len, top_z)))
    top_face = verts[4:]

    # Fill in the faces.
    #         3 e2 2
    #        e3    e1
    #         0 e0 1
    bm.faces.new(verts[0:4])
    #         7 e6 6
    #        e7    e5
    #         4 e4 5
    bm.faces.new(verts[4:])
    for i in range(3):
        #         4+i       5+i
        #        e9+i      e8+i
        #         0+i       1+i
        bm.faces.new([verts[i], verts[i+1], verts[i+1+4], verts[i+4]])
    bm.faces.new([verts[3], verts[0], verts[4], verts[7]])
    bm.edges.ensure_lookup_table()

    # edges 1, 3, 5, 6, 7, 9, 10
    edge_indices_to_select = [1, 3, 5, 6, 7, 9, 10]
    for idx in edge_indices_to_select:
        bm.edges[idx].select = True
    bpy.ops.mesh.mark_seam(clear=False)

    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.mesh.select_all(action='DESELECT')
    # Update the scene so cube_obj shows up in the viewport.
    bpy.context.scene.update()

# This method assumes that the model has already been seamed.
def unwrap_model(context, model_name, num_min_stretch_iterations):
    # Split the screen area vertically in half (0.5 == 50%), and set the newly created area to UV/Image Editor 
    # (or retrieve a reference to an already open UV/Image Editor if there is one (use the first one found)).
    split_screen_area(context, 'VERTICAL', 0.5,'IMAGE_EDITOR', True)
    image_editor, uv_editor = get_image_and_uv_editors(bpy.context)

    # Turn on live unwrap so if the user needs to edit the seams the UVs will be automatically updated in the UV/Image Editor.
    uv_editor.use_live_unwrap = True

    # Turn on stretch color view in the UV/Image Editor. This draws the UV faces ranging from blue (little stretch/distortion), 
    # green, yellow, orange, to red (lots of stretch/distortion).
    # Same as pressing N in the UV/Image Editor to bring up the properties panel -> Display -> UVs -> check the Stretch box.
    uv_editor.show_stretch = True

    # Zoom in to the Unwrapped UV (In UV/Image Editor, View -> View Fit (View the entire image) or Shift-Home).
    # Note that since we're zooming inside the UV/Image Editor area specifically, we have to pass the correct context override into 
    # the operator call to bpy.ops.image.view_all so that Blender knows which area to perform the zoom in.
    image_editor_context_override = get_context_override(context, 'IMAGE_EDITOR', 'WINDOW')
    bpy.ops.image.view_all(image_editor_context_override, fit_view=True)

    # Check if the object by model_name exists, and if it is of type mesh.
    # find returns -1 if no object matching the given name exists.
    if context.scene.objects.find(model_name) < 0:
        return
    obj = context.scene.objects[model_name]
    if obj.type != 'MESH':
        return

    # If so, set it to be the current active object, switch it to Edit mode, and select all (to unwrap all).
    context.scene.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    # Unwrap the model.
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)

    # Reduce UV stretching (same as pressing Ctrl-V in the UV/Image Editor, or going to the menu UVs -> Minimize Stretch in the UV/Image Editor).
    bpy.ops.uv.minimize_stretch(iterations=num_min_stretch_iterations)
    
# Configure viewport and mesh display settings for visualizing UV qualities on model.
def configure_viewport_settings_for_visualizing_uvs(context):
    # Properties panel (N key to bring up) -> Shading -> select Multitexture from dropdown.
    context.scene.game_settings.material_mode = 'MULTITEXTURE'

    for a in context.window.screen.areas:
        if a.type == 'VIEW_3D':
            for s in a.spaces:
                if s.type == 'VIEW_3D':
                    # Check the Texture Solid checkbox.
                    s.show_textured_solid = True
                    # Check the Backface Culling checkbox.
                    s.show_backface_culling = True
                    # Set viewport Shading to Solid (or 'TEXTURE' for Texture).
                    s.viewport_shade = 'SOLID'

    # Make sure that the active object is a mesh object (since 
    # the faces shade smooth option we're about to set next 
    # only applies to meshes in Edit mode).
    if context.scene.objects.active.type != 'MESH':
        return

    # Switch the active object to Edit Mode (since the next operator to be run
    # requires the mesh to be in Edit mode).
    bpy.ops.object.mode_set(mode='EDIT')

    # Turn on smooth shading for the active object.
    # In Edit mode -> Tool shelf (T key to bring up) -> Shading/UVs tab -> Shading -> Faces -> press Smooth button.
    bpy.ops.mesh.faces_shade_smooth()

# Sample usage----------------------------------------------------
# Generate a cube with name 'test_cube', side length of 2, that centers at the origin, and mark seams on it.
#generate_and_seam_cube(bpy.context, 'test_cube', 2, (0, 0, 0))

# Unwrap the test_cube object with 2 minimize stretch iterations.
#unwrap_model(bpy.context, 'test_cube', 2)

# Create a UV grid texture image block and project it on the model using the unwrapped UVs.
#create_image_data_block(bpy.context, 'test_uv_grid_texture')

# Configure settings for visualizing UV quality on model.
#configure_viewport_settings_for_visualizing_uvs(bpy.context)