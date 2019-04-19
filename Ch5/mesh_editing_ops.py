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
    "mesh_editing_ops"
    )

import bpy
import bmesh
from math import pow
from mathutils import Vector

# ========== Utility Methods ====================================================
def create_canvas_obj(context, name = 'canvas_obj', location = (0, 0, 0), debug = True):
    # Create an object with an empty mesh and link it to the scene.
    mesh = bpy.data.meshes.new(name = name + '_mesh')
    obj = bpy.data.objects.new(name = name, object_data = mesh)
    obj.location = location
    context.scene.objects.link(obj) 

    # Set mesh select mode to edge by default.
    context.tool_settings.mesh_select_mode = [False, True, False]
    # Enable display of edge indices in the viewport.
    if debug:
        bpy.app.debug = True
        mesh.show_extra_indices = True

    if context.scene.objects.active is not None and \
        context.scene.objects.active.mode == 'EDIT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Set the test_obj to active, change it to Edit mode, and create a bmesh instance bm to edit it.
    context.scene.objects.active = obj
    bpy.ops.object.mode_set(mode = 'EDIT')
    bm = bmesh.from_edit_mesh(obj.data)
    
    return obj, bm
        
def create_loop_stack(context, name = 'loop_stack', location = (0, 0, 0), debug = False, \
    diameter = 2, num_loops = 2, loop_segments = 16, level_height = 1):
    loop_obj, bm = create_canvas_obj(context, name, location, debug)
    
    for i in range(num_loops):
        bmesh.ops.create_circle(bm, cap_ends = False, segments = loop_segments, \
            diameter = diameter)
    bm.verts.ensure_lookup_table()
    for i in range(1, num_loops, 1):
        for v in bm.verts[loop_segments*i:loop_segments*(i+1)]:
            v.co[2] += level_height*i
    bm.edges.ensure_lookup_table()
    
    return loop_obj, bm

def create_cylinder_bmesh(context, name = 'cylinder', location = (0, 0, 0), debug = False, \
    diameter1 = 3, diameter2 = 2, segments = 16, height = 1):
    cylinder_obj, bm = create_canvas_obj(context, name, location, debug) 
    bmesh.ops.create_cone(bm, cap_ends = True, cap_tris = False, segments = segments, \
        diameter1 = diameter1, diameter2 = diameter2, depth = height)
    bm.edges.ensure_lookup_table()  
    return cylinder_obj, bm
    
def create_cone_bmesh(context, name = 'cone', location = (0, 0, 0), debug = False, diameter = 2, segments = 16, height = 1):
    cone_obj, bm = create_cylinder_bmesh(context, name = name, location = location, debug = debug, diameter1 = diameter, diameter2 = 0, segments = segments, height = height)
    return cone_obj, bm

def create_cube_bmesh(context, name = 'cube', location = (0, 0, 0), debug = False, size = 2.0):
    cube_obj, bm = create_canvas_obj(context, name, location, debug) 
    bmesh.ops.create_cube(bm, size = size) 
    bm.edges.ensure_lookup_table()  
    return cube_obj, bm

def create_grid_bmesh(context, name = 'grid', location = (0, 0, 0), debug = False, x_segments = 5, y_segments = 10, size = 10):
    grid_obj, bm = create_canvas_obj(context, name, location, debug) 
    bmesh.ops.create_grid(bm, x_segments = x_segments, y_segments = y_segments, size = size) 
    bm.edges.ensure_lookup_table()  
    return grid_obj, bm    

def create_circle_bmesh(context, name = 'circle', location = (0, 0, 0), debug = False, diameter = 2, segments = 16):
    obj, bm = create_canvas_obj(context, name, location, debug)
    bmesh.ops.create_circle(bm, cap_ends = True, segments = segments, diameter = diameter)
    bm.edges.ensure_lookup_table()  
    return obj, bm    

def create_cylinder_by_extrusion(context, name = 'cylinder_extruded', location = (0, 0, 0), debug = False, diameter = 2, segments = 8, num_levels = 2, level_height = 2):
    obj, bm = create_circle_bmesh(bpy.context, name = name, location = location, debug = debug, diameter = diameter, segments = segments)
    bm.verts.ensure_lookup_table()
    seed_edge = bm.edges[0]
    direction = Vector((0, 0, level_height))
    scale = Vector((1, 1, 1))
    loops = []
    for i in range(num_levels):
        new_loop = extrude_edge_loop_copy_move(bm, seed_edge, direction, scale)
        seed_edge = new_loop[0]
        loops.append(new_loop)
    bm.edges.ensure_lookup_table()
    return obj, bm, loops

#========= Test Creating Primitive Shapes ========================================================
def test_create_cylinder_bmesh():
    obj, bm = create_cylinder_bmesh(bpy.context, name = 'cylinder', location = (0, 0, 4), debug = False, diameter1 = 2, diameter2 = 1, segments = 8, height = 2)
    bmesh.update_edit_mesh(obj.data)
    bpy.context.scene.update()
    
def test_create_cone_bmesh():
    obj, bm = create_cone_bmesh(bpy.context, name = 'cone', location = (6, -6, 1), debug = False, diameter = 2, segments = 12, height = 2)
    bmesh.update_edit_mesh(obj.data)
    bpy.context.scene.update()
    
def test_create_cube_bmesh():
    obj, bm = create_cube_bmesh(bpy.context, name = 'cube_bm', location = (-6, -6, 0), debug = False, size = 2.0)
    bmesh.update_edit_mesh(obj.data)
    bpy.context.scene.update()

def test_create_grid_bmesh():
    obj, bm = create_grid_bmesh(bpy.context, name = 'grid', location = (0, 0, 0), debug = False, x_segments = 5, y_segments = 10, size = 10)
    bmesh.update_edit_mesh(obj.data)
    bpy.context.scene.update()

def test_create_loop_stack():
    obj, bm = create_loop_stack(bpy.context, name = 'loop_stack', location = (0, 0, 0), \
        debug = True, diameter = 3, num_loops = 5, loop_segments = 8, level_height = 2)
    bmesh.update_edit_mesh(obj.data)
    bpy.context.scene.update()

#========= Selecting Edge Loops =============================
def get_edge_loops(bm, ref_edges, select_rings = False):
    loops = []
    for re in ref_edges:
        bpy.ops.mesh.select_all(action = 'DESELECT')
        re.select = True
        bpy.ops.mesh.loop_multi_select(ring = select_rings)
        this_loop = []
        for e in bm.edges:
            if e.select:
                this_loop.append(e)
        loops.append(this_loop)
    bpy.ops.mesh.select_all(action = 'DESELECT')
    return loops

def select_edge_loops(bm, ref_edges, select_rings = False):
    bpy.ops.mesh.select_all(action = 'DESELECT')
    for re in ref_edges:
        re.select = True
    bpy.ops.mesh.loop_multi_select(ring = select_rings)
    
    loop_edges = []  
    for e in bm.edges:
        if e.select:
            loop_edges.append(e)
        
    return loop_edges

#============ Test Selecting Loops =========================================
def test_select_edge_loops():
    obj, bm = create_cylinder_bmesh(bpy.context, name = 'test_select_edge_loops', \
        location = (0, 0, 0), debug = True, diameter1 = 3, diameter2 = 2, \
        segments = 8, height = 2)

    loop_edges = select_edge_loops(bm, ref_edges = [bm.edges[0], bm.edges[1]], select_rings = False)
    #loop_edges = select_edge_loops(bm, ref_edges = [bm.edges[2]], select_rings = True)
    print(str([e.index for e in loop_edges]))

    bmesh.update_edit_mesh(obj.data)
    bpy.context.scene.update()

def test_get_edge_loops(bm):
    loops = get_edge_loops(bm, ref_edges = [bm.edges[0], bm.edges[1]], select_rings = False)
    for l in loops:
        print(str([e.index for e in l]))

#========= Bridging Edge Loops ===============================
def bridge_loops(bm, ref_edges):
    edges_in_loops = select_edge_loops(bm, ref_edges)
    new_geom = bmesh.ops.bridge_loops(bm, edges = edges_in_loops)
    return new_geom['faces'], new_geom['edges']

def bridge_loops_bpy(bm, ref_edges):
    select_edge_loops(bm, ref_edges)
    bpy.ops.mesh.bridge_edge_loops()

#============ Test Bridging Loops ==========================================
def test_bridge_loops():
    num_loops = 5
    num_segments = 8
    stack_obj, bm = create_loop_stack(bpy.context, name = 'test_bridge_loops', \
        location = (0, 0, 0), debug = True, diameter = 3, num_loops = num_loops, \
        loop_segments = num_segments, level_height = 2)
    loop_ref_edges = [bm.edges[i*num_segments] for i in range(num_loops)]
    
    resulted_faces, resulted_edges = bridge_loops(bm, loop_ref_edges)
    print(str([f.index for f in resulted_faces]))
    print(str([e.index for e in resulted_edges]))

    #bridge_loops_bpy(bm, loop_ref_edges)
    bmesh.update_edit_mesh(stack_obj.data)
    bpy.context.scene.update()
    
    #loop_slide(bpy.context, bm, ref_edge = loop_ref_edges[1], slide_distance = 0.5)
    #loop_cut_slide(bpy.context, ref_edge = loop_ref_edges[0], num_cuts = 3, slide_distance = 0.25)

#========= Extrusion =========================================
def extrude_edge_loop_copy_move(bm, ref_edge, direction, scale_factor):
    select_edge_loops(bm, [ref_edge], select_rings = False)
    bpy.ops.mesh.duplicate()
    bpy.ops.transform.translate(value = direction)
    bpy.ops.transform.resize(value = scale_factor)

    new_edge_loop = []
    for e in bm.edges:
        if e.select:
            new_edge_loop.append(e)

    bridge_loops_bpy(bm, [new_edge_loop[0], ref_edge])
    return new_edge_loop

def loop_extrude_region_move(bm, ref_edge, direction):
    select_edge_loops(bm, [ref_edge], select_rings = False)
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": direction})

#============== Test Extrusion ========================================================== 
def test_extrude_before():
    segments = 8    
    obj, bm = create_circle_bmesh(bpy.context, name = 'test_extrude_before', location = (0, 3, 0), debug = False, diameter = 2, segments = 8)
    bmesh.update_edit_mesh(obj.data)
    bpy.context.scene.update()
           
def test_extrude_edge_loop_copy_move():
    obj, bm = create_circle_bmesh(bpy.context, name = 'test_extrude_copy_move', \
        location = (0, -3, 0), debug = False, diameter = 2, segments = 8)
    ref_edge = bm.edges[0]
    num_extrusions = 5

    for i in range(num_extrusions):
        direction = Vector((1, 1, 1.5)) if i % 2 == 0 else Vector((1, -1, 1.5))
        scale = Vector((0.75, 0.5, 1)) if i % 2 == 0 else Vector((0.5, 0.75, 1))
        new_loop = extrude_edge_loop_copy_move(bm, ref_edge, direction, scale)
        ref_edge = new_loop[0]
    
    bmesh.update_edit_mesh(obj.data)
    bpy.context.scene.update()
    
def test_loop_extrude_region_move():
    obj, bm = create_circle_bmesh(bpy.context, name = 'test_loop_extrude_region_move', \
        location = (0, -3, 0), debug = False, diameter = 2, segments = 8)
    loop_extrude_region_move(bm, ref_edge = bm.edges[0], direction = Vector((1, 1, 2)))
    bmesh.update_edit_mesh(obj.data)
    bpy.context.scene.update()

def test_extrude():
    test_extrude_before()
    test_extrude_edge_loop_copy_move()
    #test_loop_extrude_region_move()
    
#========== Loop Cuts and Slides ====================================
def loop_slide(context, bm, ref_edge, slide_distance):
    select_edge_loops(bm, [ref_edge], select_rings = False)
    bpy.ops.transform.edge_slide(get_context_override(context, 'VIEW_3D', 'WINDOW'), \
        value = slide_distance)

def get_context_override(context, area_type, region_type):
    override = context.copy()
    for area in override['screen'].areas:
        if area.type == area_type: # e.g. 'VIEW_3D' for viewport, 'IMAGE_EDITOR' for UV/Image Editor, etc.
            override['area'] = area
            break
    for region in override['area'].regions:
        if region.type == region_type: # e.g. 'WINDOW'
            override['region'] = region
            break
    return override
    
def loop_cut_slide(context, ref_edge, num_cuts, slide_distance):
    # reference_edge is the edge closest and perpendicular to where the loop cut should be made.
    bpy.ops.mesh.loopcut_slide(get_context_override(context, 'VIEW_3D', 'WINDOW'), \
        MESH_OT_loopcut={"number_cuts": num_cuts, "edge_index": ref_edge.index}, \
        TRANSFORM_OT_edge_slide={"value": slide_distance})

#=========== Test Loop Cuts + Slides =========================================================
def test_loop_cut_slide_before():
    obj, bm, loops = create_cylinder_by_extrusion(bpy.context, name = 'test_loop_cut_slide_before', location = (0, 7, 0), debug = True, diameter = 2, segments = 8)
    bmesh.update_edit_mesh(obj.data)
    bpy.context.scene.update() 

def test_loop_slide():
    #obj, bm, loops = create_cylinder_by_extrusion(bpy.context, name = 'test_loop_slide', location = (0, 0, 0), debug = True, diameter = 2, segments = 8)
    num_loops = 5
    num_segments = 8
    stack_obj, bm = create_loop_stack(bpy.context, name = 'test_bridge_loops', \
        location = (0, 0, 0), debug = True, diameter = 3, num_loops = num_loops, \
        loop_segments = num_segments, level_height = 2)
    loop_ref_edges = [bm.edges[i*num_segments] for i in range(num_loops)]
    resulted_faces, resulted_edges = bridge_loops(bm, loop_ref_edges)

    loop_slide(bpy.context, bm, ref_edge = loop_ref_edges[1], slide_distance = 0.5)
    #loop_cut_slide(bpy.context, ref_edge = loop_ref_edges[0], num_cuts = 2, slide_distance = 0.5)

    bmesh.update_edit_mesh(stack_obj.data)
    bpy.context.scene.update()

def test_loop_cut_slide():
    obj, bm, loops = create_cylinder_by_extrusion(bpy.context, name = 'test_loop_cut_slide', location = (0, -7, 0), debug = True, diameter = 2, segments = 8)
    loop_cut_slide(bpy.context, ref_edge = loops[0][0], num_cuts = 2, slide_distance = 0.5)
    bmesh.update_edit_mesh(obj.data)
    bpy.context.scene.update()
    
def test_loop_cut_slide_methods():
    test_loop_cut_slide_before()
    test_loop_slide()
    test_loop_cut_slide()

#========== Merging Verts ===========================================
def merge_verts_bpy(target_map, merge_type = 'CENTER'):
    for v_from, v_to in target_map.items():
        bpy.ops.mesh.select_all(action='DESELECT')
        v_from.select = True
        v_to.select = True
    
        # type is: 'CENTER', 'CURSOR', or 'COLLAPSE'
        bpy.ops.mesh.merge(type = merge_type)

#=========== Test Merging Verts=============================================================
def test_merge_verts_before():
    obj, bm = create_grid_bmesh(bpy.context, name = 'test_merge_verts_before', location = (5, 0, 0), \
        debug = True, x_segments = 5, y_segments = 6, size = 3)
    bmesh.update_edit_mesh(obj.data)
    bpy.context.tool_settings.mesh_select_mode = [True, False, False]
    bpy.context.scene.update()
    
def test_merge_verts():
    obj, bm = create_grid_bmesh(bpy.context, name = 'test_merge_verts', \
        location = (-5, 0, 0), debug = True, x_segments = 5, y_segments = 6, size = 3)
    
    bpy.context.tool_settings.mesh_select_mode = [True, False, False]
    bm.verts.ensure_lookup_table()
    from_list = [bm.verts[i] for i in range(1, 4, 1)]
    to_list = [bm.verts[i] for i in range(6, 9, 1)]
    target_map = {from_list[i]: to_list[i] for i in range(3)}
    #bmesh.ops.weld_verts(bm, targetmap = target_map)
    merge_verts_bpy(target_map, merge_type = 'CENTER')
    
    bmesh.update_edit_mesh(obj.data)
    bpy.context.scene.update()

def test_merge_verts_bpy():
    obj, bm = create_grid_bmesh(bpy.context, name = 'test_merge_verts_bpy', location = (0, -10, 0), \
        debug = True, x_segments = 5, y_segments = 6, size = 3)
    bmesh.update_edit_mesh(obj.data)
    bpy.context.tool_settings.mesh_select_mode = [True, False, False]
    
    bm.verts.ensure_lookup_table()
    from_list = [bm.verts[i] for i in range(1, 4, 1)]
    to_list = [bm.verts[i] for i in range(6, 9, 1)]
    target_map = {from_list[i]: to_list[i] for i in range(3)}
    merge_verts_bpy(target_map, merge_type = 'CENTER')
    
    bmesh.update_edit_mesh(obj.data)
    bpy.context.scene.update()
        
def merge_vert_loops(bm, vert_loop_source, vert_loop_target):
    tm = dict()
    len_source = len(vert_loop_source)
    len_target = len(vert_loop_target)
    vert_loop_merged = vert_loop_target if len_source > len_target else vert_loop_source
    tm_length = min(len_source, len_target)
    
    for i in range(tm_length):
        tm[vert_loop_source[i]] = vert_loop_target[i]

    bmesh.ops.weld_verts(bm, targetmap = tm)
    vert_loop_merged[0:tm_length] = vert_loop_target
    resulted_indices = [v.index for v in vert_loop_merged]
    return vert_loop_merged, resulted_indices

#========== Test Merging Loops ===========================================================
def test_merge_vert_loops():
    segments = 8    
    obj, bm = create_cylinder_bmesh(bpy.context, name = 'merged_bottom_to_top', location = (0, 4, 0), debug = True, diameter1 = 2, diameter2 = 1, segments = segments, height = 2)
    bpy.context.tool_settings.mesh_select_mode = [True, False, False]
    bm.verts.ensure_lookup_table()
    even_verts = [bm.verts[i] for i in range(0, segments*2, 2)]
    odd_verts = [bm.verts[i] for i in range(1, segments*2, 2)]
    merge_vert_loops(bm, even_verts, odd_verts)
    bmesh.update_edit_mesh(obj.data)
    bpy.context.scene.update()
    
def test_merge_vert_loops_reverse():
    segments = 8    
    obj, bm = create_cylinder_bmesh(bpy.context, name = 'merged_top_to_bottom', location = (0, -4, 0), debug = True, diameter1 = 2, diameter2 = 1, segments = segments, height = 2)
    bpy.context.tool_settings.mesh_select_mode = [True, False, False]
    bm.verts.ensure_lookup_table()
    even_verts = [bm.verts[i] for i in range(0, segments*2, 2)]
    odd_verts = [bm.verts[i] for i in range(1, segments*2, 2)]
    merge_vert_loops(bm, odd_verts, even_verts)
    bmesh.update_edit_mesh(obj.data)
    bpy.context.scene.update()
    
# ========== Ripping Verts ======================================================
def rip_verts_bmesh(rip_map, offset):
    ripped_verts = []
    for f, rip_corner_index in rip_map.items():
        v = bmesh.utils.face_vert_separate(f, f.verts[rip_corner_index])
        v.co += offset
        ripped_verts.append(v)
    return ripped_verts

#=========== Test Ripping =============================================================
def test_rip_verts_before():
    obj, bm = create_grid_bmesh(bpy.context, name = 'test_rip_verts_before', location = (7, 0, 0), debug = True, x_segments = 10, y_segments = 4, size = 6)
    bmesh.update_edit_mesh(obj.data)
    bpy.context.tool_settings.mesh_select_mode = [True, False, False]
    bpy.context.scene.update()    
    
def test_rip_verts_bmesh():
    obj, bm = create_grid_bmesh(bpy.context, name = 'test_rip_verts_bmesh', \
        location = (-7, 0, 0), debug = True, x_segments = 10, y_segments = 4, size = 6)

    bpy.context.tool_settings.mesh_select_mode = [False, False, True]
    bm.faces.ensure_lookup_table()
    offset = Vector((1, 0.75, 1.25))
    rip_map = {bm.faces[10]: 0, bm.faces[12]: 1, bm.faces[14]: 2, bm.faces[16]: 3}
    rip_verts_bmesh(rip_map, offset)
    
    bmesh.update_edit_mesh(obj.data)
    bpy.context.scene.update()
    
def test_rip_verts():
    test_rip_verts_before()
    test_rip_verts_bmesh()

# ========== Insetting + Beveling ===============================================
def bevel_bpy(edge_list, offset = 0.15, segments = 2, loop_slide = True, vertex_only = False):
    bpy.ops.mesh.select_all(action='DESELECT')
    for e in edge_list:
        e.select = True
    bpy.ops.mesh.bevel(offset = offset, segments = segments, loop_slide = loop_slide, \
        vertex_only = vertex_only)

#========= Test Insettting ========================================================
def test_inset_bmesh_before():
    obj, bm = create_grid_bmesh(bpy.context, name = 'test_inset_before', location = (0, 0, 2), \
        debug = True, x_segments = 10, y_segments = 4, size = 6)
    bpy.context.tool_settings.mesh_select_mode = [False, False, True]
    bmesh.update_edit_mesh(obj.data)
    bpy.context.scene.update()
    
def test_inset_bmesh():
    obj, bm = create_grid_bmesh(bpy.context, name = 'test_inset_indv', location = (0, 0, 2), \
        debug = True, x_segments = 10, y_segments = 4, size = 6)
    bpy.context.tool_settings.mesh_select_mode = [False, False, True]
    
    bm.faces.ensure_lookup_table()
    faces_indv_out = bm.faces[0:4]
    faces_indv_in = bm.faces[5:9]
    faces_region_out = bm.faces[9:12] + bm.faces[14:18]
    faces_region_in = bm.faces[18:22] + bm.faces[24:26]    
    # When depth is > 0, the faces stick outward instead of inward (outset).
    # When depth is < 0, the faces stick inward (inset).
    bmesh.ops.inset_individual(bm, faces = faces_indv_out, thickness = 0.3, depth = 0.5)
    bmesh.ops.inset_individual(bm, faces = faces_indv_in, thickness = 0.5, depth = -0.2)
    bmesh.ops.inset_region(bm, faces = faces_region_out, thickness = 0.3, depth = 0.5)
    bmesh.ops.inset_region(bm, faces = faces_region_in, thickness = 0.5, depth = -0.2)
    
    bmesh.update_edit_mesh(obj.data)
    bpy.context.scene.update()

def test_inset():
    test_inset_bmesh_before()
    test_inset_bmesh()

#=========== Test Beveling ===================================================
def test_bevel_bpy_before():
    obj, bm = create_cube_bmesh(bpy.context, name = 'test_bevel_bpy_before', location = (0, 0, 3), debug = False, size = 5.0)
    bmesh.update_edit_mesh(obj.data)
    bpy.context.scene.update()    
    
def test_bevel_bpy_edges():
    obj, bm = create_cube_bmesh(bpy.context, name = 'test_bevel_bpy_edges', \
        location = (0, 0, 3), debug = False, size = 5.0)

    bm.edges.ensure_lookup_table()
    bevel_bpy(edge_list = bm.edges[0:4], offset = 1.0, segments = 5, \
        loop_slide = True, vertex_only = False)

    bmesh.update_edit_mesh(obj.data)
    bpy.context.scene.update()
    
def test_bevel_bpy_edges_no_slide():
    obj, bm = create_cube_bmesh(bpy.context, name = 'test_bevel_bpy_edges_no_slide', location = (0, 0, 3), debug = False, size = 5.0)

    bm.edges.ensure_lookup_table()
    bevel_bpy(edge_list = bm.edges[0:4], offset = 1.0, segments = 5, loop_slide = False, vertex_only = False)

    bmesh.update_edit_mesh(obj.data)
    bpy.context.scene.update()
    
def test_bevel_bpy_vertex_only():
    obj, bm = create_cube_bmesh(bpy.context, name = 'test_bevel_bpy_vertex_only', location = (0, 0, 3), debug = False, size = 5.0)

    bm.edges.ensure_lookup_table()
    bevel_bpy(edge_list = bm.edges[0:4], offset = 1.0, segments = 5, loop_slide = False, vertex_only = True)

    bmesh.update_edit_mesh(obj.data)
    bpy.context.scene.update()
    
def test_bevel_bpy():
    test_bevel_bpy_before()
    test_bevel_bpy_edges()
    test_bevel_bpy_edges_no_slide()
    test_bevel_bpy_vertex_only()
       
# ========== Remove Loose Verts =================================================       
def remove_loose_verts(bm):
    verts_to_remove = []
    for v in bm.verts:
        if len(v.link_edges) == 0:
            verts_to_remove.append(v)
            
    for v in verts_to_remove:
        bm.verts.remove(v)

#=========== Test Removing Loose Verts ====================================
def gen_mesh_with_loose_verts(location, name):
    obj, bm = create_cube_bmesh(bpy.context, name = name, location = location, debug = True, size = 4.0)
    existing_verts = list(bm.verts)
    for v in existing_verts:
        bm.verts.new(v.co + Vector((-1, -1, 1)))
    bm.verts.ensure_lookup_table()  
    return obj, bm

def test_remove_loose_verts_before():
    obj_before, bm_before = gen_mesh_with_loose_verts((0, 4, 0), 'test_remove_loose_verts_before')
    bpy.context.tool_settings.mesh_select_mode = [True, False, False]
    bmesh.update_edit_mesh(obj_before.data)
    bpy.context.scene.update()

def test_remove_loose_verts_after():    
    obj_after, bm_after = gen_mesh_with_loose_verts((0, -4, 0), 'test_remove_loose_verts_after')
    remove_loose_verts(bm_after)
    bpy.context.tool_settings.mesh_select_mode = [True, False, False]
    bmesh.update_edit_mesh(obj_after.data)
    bpy.context.scene.update()
    
def test_remove_loose_verts():
    test_remove_loose_verts_before()
    test_remove_loose_verts_after()

#=========== Test Joining + Splitting Faces =============================================================
def test_join_split_faces_before():
    obj, bm = create_grid_bmesh(bpy.context, name = 'test_join_faces_before', location = (7, 0, 0), debug = True, x_segments = 10, y_segments = 4, size = 6)
    bmesh.update_edit_mesh(obj.data)
    bpy.context.tool_settings.mesh_select_mode = [True, False, True]
    bpy.context.scene.update()    
    
def test_join_split_faces_bmesh():
    obj, bm = create_grid_bmesh(bpy.context, name = 'test_join_faces_bmesh', \
        location = (-7, 0, 0), debug = True, x_segments = 10, y_segments = 4, size = 6)

    bpy.context.tool_settings.mesh_select_mode = [True, False, True]
    bm.faces.ensure_lookup_table()
    faces_to_join = bm.faces[0:9]
    face_to_split = bm.faces[13]
    joined_face = bmesh.utils.face_join(faces_to_join)
    split_face = bmesh.utils.face_split(face_to_split, face_to_split.verts[0], \
        face_to_split.verts[2])
    joined_face.select = True
    split_face[0].select = True
    
    bmesh.update_edit_mesh(obj.data)
    bpy.context.scene.update()

def test_join_split_faces():
    test_join_split_faces_before()
    test_join_split_faces_bmesh()
    
#=========== Putting It Altogether ===========================================
def gen_stylized_fire_hydrant(context, debug = False, location = (0, 0, 0), \
    num_cir_segments = 16, pole_diameter = 2, num_pole_levels = 3, num_dome_levels = 5, \
    stylize = False, pole_bent_factor = 1, dome_bent_factor = 1, subsurf = False, \
    subsurf_level = 2):
    fh_obj, bm = create_canvas_obj(context, name = 'fire_hydrant', location = location, \
        debug = debug) 
    bmesh.ops.create_cone(bm, cap_ends = False, cap_tris = False, \
        segments = num_cir_segments, diameter1 = pole_diameter*1.33, \
        diameter2 = pole_diameter*1.33, depth = pole_diameter*0.5)
    bm.edges.ensure_lookup_table()
    if subsurf:
        fh_subsurf_mod = fh_obj.modifiers.new('subsurf_mod', 'SUBSURF')
        fh_subsurf_mod.levels = subsurf_level

    loop_cut_slide(context, bm.edges[1], num_cuts = 2, slide_distance = 0)
    
    bm.edges.ensure_lookup_table()
    bm.edges[num_cir_segments*3 + 1].select = True
    bpy.ops.mesh.loop_multi_select(ring = True)
    context.tool_settings.mesh_select_mode = [False, False, True]

    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate = {"value": Vector((0, 0, 0))})
    bpy.ops.transform.shrink_fatten(value = -0.1)

    bpy.ops.mesh.bevel(offset = 0.1, segments = 2, loop_slide = False, vertex_only = False)

    context.tool_settings.mesh_select_mode = [False, True, False]
    bm.edges.ensure_lookup_table()
    select_edge_loops(bm, [bm.edges[2]], select_rings = False)

    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate = {"value": Vector((0, 0, 0))})
    bpy.ops.transform.shrink_fatten(value = pole_diameter*0.33)

    bm.edges.ensure_lookup_table()
    for e in bm.edges:
        if e.select:
            ref_edge = e
            break
    context.tool_settings.mesh_select_mode = [False, False, True]
    edge_loops_pole_cross_sections = []
    for i in range(num_pole_levels + 1):
        z_offset = pole_diameter if i < num_pole_levels else pole_diameter*0.5
        if stylize:            
            skew = pole_diameter*0.25*pole_bent_factor
            direction = Vector((skew, skew, z_offset)) if i % 2 == 0 \
                else Vector((-skew, -skew, z_offset))
            scale = Vector((0.85, 1, 1)) if i % 2 == 0 else Vector((1, 0.85, 1))
        else:
            direction = Vector((0, 0, z_offset))
            scale = Vector((1, 1, 1))
        extrusion = extrude_edge_loop_copy_move(bm, ref_edge, direction, scale)
        edge_loops_pole_cross_sections.append(extrusion)
        ref_edge = extrusion[0]

        if i == 0:
            bm.faces.ensure_lookup_table()
            face_loop_pole_bottom = []
            face_idx = 0
            for f in bm.faces:
                if f.select:
                    if face_idx % 2 == 0:
                        face_loop_pole_bottom.append(f)
                    face_idx += 1
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate = {"value": Vector((0, 0, 0))})
    bpy.ops.transform.shrink_fatten(value = pole_diameter*-0.25)
    bm.faces.ensure_lookup_table()
    face_loop_pole_top = []
    for f in bm.faces:
        if f.select:
            face_loop_pole_top.append(f)

    face_loops_dome = []
    face_loops_dome_cap = []
    for i in range(num_dome_levels + 3):
        if i < num_dome_levels:
            z_offset = pole_diameter*0.5*pow(0.5, i)
            skew = pole_diameter*0.1*dome_bent_factor if stylize else 0          
            direction = Vector((skew, skew, z_offset)) if i % 2 == 0 \
                else Vector((-skew, -skew, z_offset))
            scale = Vector((0.85, 0.85, 1))
        else:
            z_offset = pole_diameter*0.1
            direction = Vector((0, 0, z_offset))
            scale = Vector((1, 1, 1))
        extrusion = extrude_edge_loop_copy_move(bm, ref_edge, direction, scale)
        edge_loops_pole_cross_sections.append(extrusion)
        ref_edge = extrusion[0]        
        bm.faces.ensure_lookup_table()
        
        if i < num_dome_levels:
            face_idx = 0
            for f in bm.faces:
                if f.select:
                    if face_idx % 2 == 0:
                        face_loops_dome.append(f)
                    face_idx += 1
        else:
            cur_loop = []
            for f in bm.faces:
                if f.select:
                    cur_loop.append(f)
            face_loops_dome_cap.append(cur_loop)

    bpy.ops.mesh.select_all(action = 'DESELECT')
    for f in face_loops_dome_cap[1]:
        f.select = True
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate = {"value": Vector((0, 0, 0))})
    bpy.ops.transform.shrink_fatten(value = pole_diameter*-0.1)
    bpy.ops.mesh.select_all(action = 'DESELECT')
    for f in face_loops_dome_cap[2]:
        f.select = True
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate = {"value": Vector((0, 0, 0))})
    bpy.ops.transform.shrink_fatten(value = pole_diameter*0.15)
    bpy.ops.mesh.select_all(action = 'DESELECT')
    select_edge_loops(bm, [ref_edge], select_rings = False)
    bpy.ops.mesh.edge_collapse()

    bmesh.ops.inset_region(bm, faces = face_loop_pole_top, thickness = 0.3, depth = 0.1)
    bmesh.ops.inset_individual(bm, faces = face_loop_pole_bottom, thickness = 0.2, depth = -0.1)
    bmesh.ops.inset_region(bm, faces = face_loops_dome, thickness = 0.1, depth = -0.15)

    bmesh.ops.recalc_face_normals(bm, faces = bm.faces)
    bmesh.update_edit_mesh(fh_obj.data)
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action = 'SELECT')
    bpy.ops.object.shade_smooth()
    bpy.ops.object.select_all(action = 'DESELECT')
    config_viewport_shading(context)
    bpy.context.scene.update()

def config_viewport_shading(context):
    for a in context.window.screen.areas:
        if a.type == 'VIEW_3D':
            for s in a.spaces:
                if s.type == 'VIEW_3D':
                    s.viewport_shade = 'SOLID'
                    s.show_textured_solid = True
                    s.fx_settings.use_ssao = True                  
                    s.show_floor = False
                    s.show_axis_x = False
                    s.show_axis_y = False

#========= Test Fire Hydrant Generation ======================================================
def test_gen_fire_hydrant():
    gen_stylized_fire_hydrant(bpy.context, location = (15, -12, 0))
    gen_stylized_fire_hydrant(bpy.context, location = (5, -12, 0), subsurf = True)
    gen_stylized_fire_hydrant(bpy.context, location = (-5, -12, 0), \
        pole_diameter = 2, num_pole_levels = 2, num_dome_levels = 3)
    gen_stylized_fire_hydrant(bpy.context, location = (-13, -12, 0), \
        pole_diameter = 1, num_pole_levels = 6, num_dome_levels = 5)

    gen_stylized_fire_hydrant(bpy.context, location = (15, 0, 0), stylize = True)
    gen_stylized_fire_hydrant(bpy.context, location = (5, 0, 0), stylize = True, subsurf = True)
    gen_stylized_fire_hydrant(bpy.context, location = (-5, 0, 0), \
        pole_diameter = 2, num_pole_levels = 2, num_dome_levels = 3, stylize = True)
    gen_stylized_fire_hydrant(bpy.context, location = (-13, 0, 0), \
        pole_diameter = 1, num_pole_levels = 6, num_dome_levels = 5, \
        stylize = True, pole_bent_factor = 2, dome_bent_factor = 1.5)

def test_gen_fh_num_segments():
    gen_stylized_fire_hydrant(bpy.context, location = (12, 0, 0), num_cir_segments = 8)
    gen_stylized_fire_hydrant(bpy.context, location = (5, 0, 0), num_cir_segments = 16)
    gen_stylized_fire_hydrant(bpy.context, location = (-2, 0, 0), num_cir_segments = 25)
    gen_stylized_fire_hydrant(bpy.context, location = (-9, 0, 0), num_cir_segments = 64)

#========= Sample Usage ======================================================
#test_create_cylinder_bmesh()
#test_create_cone_bmesh()
#test_create_cube_bmesh()
#test_create_grid_bmesh()

#test_select_edge_loops()
     
#test_create_loop_stack()
#test_bridge_loops()

#test_extrude()
#test_loop_slide()

#test_merge_verts_before()
#test_merge_verts()
#test_merge_vert_loops()
#test_merge_vert_loops_reverse()
#test_rip_verts()
#test_join_split_faces()

#test_bevel_bpy()
#test_inset()

#test_remove_loose_verts()

test_gen_fire_hydrant()
#test_gen_fh_num_segments()