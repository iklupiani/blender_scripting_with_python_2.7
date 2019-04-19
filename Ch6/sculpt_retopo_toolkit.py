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

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, FloatProperty, IntProperty
from mathutils import Vector
import bmesh
from math import floor

bl_info = {
    'name': 'Sculpt & Retopo Toolkit',
    'author': 'Isabel Lupiani',
    'version': (1, 1, 0),
    'blender': (2, 77, 1),
    'location': 'Tool Shelf > Tools',
    'warning': '',
    'description': 'Collection of grease pencil based sculpting and retopo tools.',
    'wiki_url': '',
    'category': 'Mesh',
}

def config_gp(context, clear_strokes = False):
    scene = context.scene
    if bpy.data.grease_pencil.find('srtk_gp') < 0:
        scene.grease_pencil = bpy.data.grease_pencil.new('srtk_gp')
    else:
        scene.grease_pencil = bpy.data.grease_pencil['srtk_gp']
    gp = scene.grease_pencil

    if gp.layers.find('srtk_gp_layer') < 0:
        gp.layers.active = gp.layers.new('srtk_gp_layer')
    else:
        gp.layers.active = gp.layers['srtk_gp_layer']

    frame0_found = False
    for f in gp.layers.active.frames:
        if f.frame_number == 0:
            if clear_strokes:
                f.clear()
            gp.layers.active.active_frame = f
            frame0_found = True
            break
    if not frame0_found:
        gp.layers.active.active_frame = gp.layers.active.frames.new(0)
    scene.frame_set(0)

    gp.layers.active.show_x_ray = True
    gp.layers.active.show_points = False
    gp.layers.active.color = (0, 0.5, 0.5)
    gp.layers.active.line_width = 3

    scene.tool_settings.use_gpencil_continuous_drawing = True
    scene.tool_settings.grease_pencil_source = 'SCENE'
    scene.tool_settings.gpencil_stroke_placement_view3d = 'SURFACE'
    scene.tool_settings.use_gpencil_stroke_endpoints = False

class BUTTON_OT_config_gp(Operator):
    bl_idname = 'button.config_gp'
    bl_label = 'Config GP'
    '''Config GP'''

    def execute(self, context):
        config_gp(context, clear_strokes = True)
        self.report({'INFO'}, 'Sculpt & Retopo Toolkit: Config GP.')
        return {'FINISHED'}

    def invoke(self, context, event):     
        return self.execute(context) 
    
def gp_knife_project(context):   
    config_gp(context, clear_strokes = False)
    mode_to_restore = context.mode
    knife_project_status = False

    if len(context.scene.grease_pencil.layers.active.frames[0].strokes) == 0:
        return knife_project_status, mode_to_restore    

    obj_to_be_cut = context.scene.objects.active
    if obj_to_be_cut and obj_to_be_cut.type == 'MESH':
        bpy.ops.object.mode_set(mode = 'GPENCIL_EDIT')
        bpy.ops.gpencil.select_all(action = 'SELECT')
        bpy.ops.gpencil.convert(type = 'CURVE', use_timing_data = False)
        curve_obj_name = context.scene.grease_pencil.layers.active.info
        curve_obj = context.scene.objects[curve_obj_name]
            
        obj_to_be_cut.select = True
        bpy.ops.object.mode_set(mode = 'EDIT')          
        bpy.ops.mesh.knife_project(cut_through = context.scene.cut_thru_checkbox)

        context.scene.objects.unlink(curve_obj)
        bpy.data.objects.remove(curve_obj)
        knife_project_status = True
    config_gp(context, clear_strokes = True)
    return knife_project_status, mode_to_restore

class BUTTON_OT_carve(Operator):
    bl_idname = 'button.carve'
    bl_label = 'Carve'
    '''Carve'''

    def execute(self, context):
        knife_project_success, mode_to_restore = gp_knife_project(context)
        if knife_project_success:
            try:
                bpy.ops.mesh.separate(type = 'SELECTED')
            except:
                self.report({'WARNING'}, 'Sculpt & Retopo Toolkit: \
                Carve - Draw a hole to carve with a closed loop.')
                return {'FINISHED'}

            obj_to_be_carved = context.scene.objects.active
            for hole_template_obj in context.scene.objects:
                if hole_template_obj != obj_to_be_carved and hole_template_obj.select \
                    and hole_template_obj.type == 'MESH':
                    boolean_mod = obj_to_be_carved.modifiers.new('boolean_mod', 'BOOLEAN')
                    boolean_mod.object = hole_template_obj
                    boolean_mod.operation = 'DIFFERENCE'
                    bpy.ops.object.mode_set(mode = 'OBJECT')
                    bpy.ops.object.modifier_apply(apply_as = 'DATA', modifier = boolean_mod.name)
                    context.scene.objects.unlink(hole_template_obj)
                    bpy.data.objects.remove(hole_template_obj)
                    break
            bpy.ops.object.mode_set(mode = mode_to_restore)
        self.report({'INFO'}, 'Sculpt & Retopo Toolkit: Carve.')
        return {'FINISHED'}

    def invoke(self, context, event):     
        return self.execute(context)

def init_scene_vars():
    bpy.types.Scene.cut_thru_checkbox = BoolProperty(
        name = 'Cut Through',
        description = 'Whether to cut thru the mesh to the other side with Carve and In/Outset.',
        default = False)

    bpy.types.Scene.inoutset_amount = FloatProperty(
        name = 'In/Outset Amount',
        description = 'Amount to inset(+) or outset(-).',
        default = 0.1)

    bpy.types.Scene.num_grid_lines = IntProperty(
        name = 'Grid Lines',
        description = 'Number of horizontal grid lines to make from GP strokes.',
        default = 5,
        min = 2)

class BUTTON_OT_inset(Operator):
    bl_idname = 'button.inset'
    bl_label = 'Inset'
    '''Inset'''

    def execute(self, context):
        knife_project_success, mode_to_restore = gp_knife_project(context)
        if knife_project_success:
            bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate = \
                {'value': Vector((0, 0, 0))})
            bpy.ops.transform.shrink_fatten(value = context.scene.inoutset_amount)
            bpy.ops.object.mode_set(mode = mode_to_restore)
        self.report({'INFO'}, 'Sculpt & Retopo Toolkit: In/Outset.')
        return {'FINISHED'}

    def invoke(self, context, event):     
        return self.execute(context)

class BUTTON_OT_draw_grid(Operator):
    bl_idname = 'button.draw_grid'
    bl_label = 'Draw Grid'
    '''Draw Grid'''

    def execute(self, context):
        config_gp(context, clear_strokes = False)
        gp = context.scene.grease_pencil
        obj_to_add_grid = context.scene.objects.active
        if obj_to_add_grid and obj_to_add_grid.type == 'MESH':
            bpy.ops.object.mode_set(mode = 'EDIT')      
            bpy.ops.mesh.select_all(action = 'DESELECT')
            context.scene.tool_settings.use_snap = True
            context.scene.tool_settings.snap_element = 'FACE'
            context.scene.tool_settings.snap_target = 'CLOSEST'
            context.scene.tool_settings.use_snap_self = True
            bm = bmesh.from_edit_mesh(obj_to_add_grid.data)
            verts_prev_stroke = []
            for s in gp.layers.active.frames[0].strokes:
                num_pts = len(s.points)
                if num_pts < context.scene.num_grid_lines:
                    continue
                num_pts_per_cell = floor(num_pts/context.scene.num_grid_lines)

                v_prev = None
                verts_cur_stroke = []
                num_gls_left = context.scene.num_grid_lines
                for i in range(0, num_pts, num_pts_per_cell):
                    if num_gls_left == 0:
                        break
                    v = bm.verts.new(s.points[i].co - obj_to_add_grid.location)
                    v.select = True
                    if v_prev:
                        e = bm.edges.new([v_prev, v])
                        e.select = True
                    
                    v_prev = v
                    verts_cur_stroke.append(v)
                    num_gls_left -= 1

                if len(verts_prev_stroke) > 0:
                    num_verts_to_bridge = min(len(verts_prev_stroke), len(verts_cur_stroke))
                    for j in range(num_verts_to_bridge):
                        e = bm.edges.new([verts_prev_stroke[j], verts_cur_stroke[j]])
                        e.select = True
                verts_prev_stroke = verts_cur_stroke
            bpy.ops.mesh.edge_face_add()
            bmesh.update_edit_mesh(obj_to_add_grid.data)
            context.scene.update()
        self.report({'INFO'}, 'Sculpt & Retopo Toolkit: Draw Grid.')
        config_gp(context, clear_strokes = True)
        return {'FINISHED'}

    def invoke(self, context, event):     
        return self.execute(context)
    
class ToolShelfPanel(bpy.types.Panel):
    bl_label = 'Sculpt & Retopo Toolkit'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Tools'
    '''A collection of grease pencil driven sculpt and retopo tools'''
 
    def draw(self, context):  
        layout = self.layout
        col0 = layout.column()
        col0.operator('button.config_gp')

        box0 = col0.box()
        box0.label('Sculpt Tools', icon = 'SCULPTMODE_HLT')
        box0_row0 = box0.row(align = True)
        box0_row0.prop(context.scene, 'cut_thru_checkbox')                 
        box0.operator('button.carve')
        box0_row1 = box0.row(align = True)
        box0_row1.prop(context.scene, 'inoutset_amount')    
        box0.operator('button.inset', text = 'In/Outset')

        box1 = col0.box()
        box1.label('Retopo Tools', icon = 'MESH_GRID')
        box1_row0 = box1.row(align = True)
        box1_row0.prop(context.scene, 'num_grid_lines')    
        box1.operator('button.draw_grid')

def del_scene_vars():
    del bpy.types.Scene.cut_thru_checkbox
    del bpy.types.Scene.inoutset_amount
    del bpy.types.Scene.num_grid_lines

classes = [BUTTON_OT_config_gp, BUTTON_OT_carve, BUTTON_OT_inset, ToolShelfPanel, BUTTON_OT_draw_grid]
      
def register():
    for c in classes:
        bpy.utils.register_class(c)
    init_scene_vars()

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    del_scene_vars()
      
if __name__ == '__main__':
    register()