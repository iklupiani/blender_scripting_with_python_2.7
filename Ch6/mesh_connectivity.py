import bpy
import bmesh
from mathutils import Vector
import math 

def select_poles(context):
    obj = context.scene.objects.active
    if obj is not None and obj.type == 'MESH':
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action = 'DESELECT')
        context.tool_settings.mesh_select_mode = [True, False, False]
        bm = bmesh.from_edit_mesh(obj.data)
        for v in bm.verts:
            valence = len(v.link_edges)
            if valence == 3 or valence > 4:
                v.select = True
        bmesh.update_edit_mesh(obj.data)
        context.scene.update()
        
def get_angle_between_vectors(vector1, vector2):
    theta = math.acos( vector1.dot(vector2) / (vector1.length * vector2.length) )
    return math.degrees(theta)    
        
def get_angle_between_edges(e1, e2):
    if e1.verts[0] in e2.verts:
        vert_shared = e1.verts[0]
    else:
        vert_shared = e1.verts[1]
    
    e1_end_v = e1.other_vert(vert_shared) 
    e2_end_v = e2.other_vert(vert_shared)
    vector1 = e1_end_v.co - vert_shared.co
    vector2 = e2_end_v.co - vert_shared.co
    return get_angle_between_vectors(vector1, vector2)       
    
def select_face_corners_less_than_angle(context, angle_in_degrees):
    obj = context.scene.objects.active
    if obj is not None and obj.type == 'MESH':
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action = 'DESELECT')
        context.tool_settings.mesh_select_mode = [False, True, False]
        bm = bmesh.from_edit_mesh(obj.data)
        for v in bm.verts:
            num_edges = len(v.link_edges)
            for i in range(num_edges):
                e1 = v.link_edges[i]
                e2 = v.link_edges[0] if i == num_edges - 1 else v.link_edges[i+1]
                    
                if get_angle_between_edges(e1, e2) <= angle_in_degrees:
                    e1.select = True
                    e2.select = True
        bmesh.update_edit_mesh(obj.data)
        context.scene.update()
        
def auto_mark_sharp(context, angle_in_degrees):
    obj = context.scene.objects.active
    if obj is not None and obj.type == 'MESH':
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action = 'DESELECT')
        context.tool_settings.mesh_select_mode = [False, True, False]
        bm = bmesh.from_edit_mesh(obj.data)
        for e in bm.edges:
            if len(e.link_faces) == 2:
                theta = get_angle_between_vectors(e.link_faces[0].normal, e.link_faces[1].normal)
                if theta >= angle_in_degrees:
                    e.select = True
        bmesh.update_edit_mesh(obj.data)
        context.scene.update()
        bpy.ops.mesh.mark_seam(clear = False)
        bpy.ops.mesh.select_all(action = 'DESELECT')

def select_ngons(context):
    obj = context.scene.objects.active
    if obj is not None and obj.type == 'MESH':
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action = 'DESELECT')
        context.tool_settings.mesh_select_mode = [False, False, True]
        bm = bmesh.from_edit_mesh(obj.data)
        for f in bm.faces:
            if len(f.verts) > 4:
                f.select = True
        bmesh.update_edit_mesh(obj.data)
        context.scene.update()
        
def select_non_quads(context):
    obj = context.scene.objects.active
    if obj is not None and obj.type == 'MESH':
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action = 'DESELECT')
        context.tool_settings.mesh_select_mode = [False, False, True]
        bm = bmesh.from_edit_mesh(obj.data)
        for f in bm.faces:
            if len(f.verts) != 4:
                f.select = True
        bmesh.update_edit_mesh(obj.data)
        context.scene.update()

# Sample Usage
#select_poles(bpy.context)
#select_ngons(bpy.context)
#select_non_quads(bpy.context)
select_face_corners_less_than_angle(bpy.context, 60)
#auto_mark_sharp(bpy.context, 60)