import bpy

if bpy.context.scene.objects.active is not None:
    bpy.ops.object.mode_set(mode = 'OBJECT')
bpy.ops.object.select_all(action = 'DESELECT')

cube = bpy.context.scene.objects['Cube']
bpy.context.scene.objects.active = cube
cube.select = True
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_all(action = 'SELECT')
bpy.context.scene.update()
