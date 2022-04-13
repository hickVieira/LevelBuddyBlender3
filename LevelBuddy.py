#  ***** BEGIN GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  ***** END GPL LICENSE BLOCK *****


import os
import bpy
import bmesh
import addon_utils
from bpy_extras.io_utils import ImportHelper

bl_info = {
    "name": "Level Buddy",
    "author": "Matt Lucas, HickVieira (Blender 3.0 version)",
    "version": (1, 5),
    "blender": (3, 0, 0),
    "location": "View3D > Tools > Level Buddy",
    "description": "A set of workflow tools based on concepts from Doom and Unreal level mapping.",
    "warning": "WIP",
    "wiki_url": "https://github.com/hickVieira/LevelBuddyBlender3",
    "category": "Object",
}


def auto_texture(bool_obj, source_obj):
    mesh = bool_obj.data
    objectLocation = source_obj.location
    objectScale = source_obj.scale

    bm = bmesh.new()
    bm.from_mesh(mesh)

    uv_layer = bm.loops.layers.uv.verify()
    for f in bm.faces:
        nX = f.normal.x
        nY = f.normal.y
        nZ = f.normal.z
        if nX < 0:
            nX = nX * -1
        if nY < 0:
            nY = nY * -1
        if nZ < 0:
            nZ = nZ * -1
        faceNormalLargest = nX
        faceDirection = "x"
        if faceNormalLargest < nY:
            faceNormalLargest = nY
            faceDirection = "y"
        if faceNormalLargest < nZ:
            faceNormalLargest = nZ
            faceDirection = "z"
        if faceDirection == "x":
            if f.normal.x < 0:
                faceDirection = "-x"
        if faceDirection == "y":
            if f.normal.y < 0:
                faceDirection = "-y"
        if faceDirection == "z":
            if f.normal.z < 0:
                faceDirection = "-z"
        for l in f.loops:
            luv = l[uv_layer]
            if faceDirection == "x":
                luv.uv.x = (((l.vert.co.y * objectScale[1]) + objectLocation[1]) * source_obj.texture_tillings[1] + source_obj.wall_texture_offset[0]) * 0.5
                luv.uv.y = (((l.vert.co.z * objectScale[2]) + objectLocation[2]) * source_obj.texture_tillings[1] + source_obj.wall_texture_offset[1]) * 0.5
            if faceDirection == "-x":
                luv.uv.x = (((l.vert.co.y * objectScale[1]) + objectLocation[1]) * source_obj.texture_tillings[1] + source_obj.wall_texture_offset[0]) * -0.5
                luv.uv.y = (((l.vert.co.z * objectScale[2]) + objectLocation[2]) * source_obj.texture_tillings[1] + source_obj.wall_texture_offset[1]) * 0.5
            if faceDirection == "y":
                luv.uv.x = (((l.vert.co.x * objectScale[0]) + objectLocation[0]) * source_obj.texture_tillings[1] + source_obj.wall_texture_offset[0]) * -0.5
                luv.uv.y = (((l.vert.co.z * objectScale[2]) + objectLocation[2]) * source_obj.texture_tillings[1] + source_obj.wall_texture_offset[1]) * 0.5
            if faceDirection == "-y":
                luv.uv.x = (((l.vert.co.x * objectScale[0]) + objectLocation[0]) * source_obj.texture_tillings[1] + source_obj.wall_texture_offset[0]) * 0.5
                luv.uv.y = (((l.vert.co.z * objectScale[2]) + objectLocation[2]) * source_obj.texture_tillings[1] + source_obj.wall_texture_offset[1]) * 0.5
            if faceDirection == "z":
                luv.uv.x = (((l.vert.co.x * objectScale[0]) + objectLocation[0]) * source_obj.texture_tillings[0] + source_obj.ceiling_texture_offset[0]) * 0.5
                luv.uv.y = (((l.vert.co.y * objectScale[1]) + objectLocation[1]) * source_obj.texture_tillings[0] + source_obj.ceiling_texture_offset[1]) * 0.5
            if faceDirection == "-z":
                luv.uv.x = (((l.vert.co.x * objectScale[0]) + objectLocation[0]) * source_obj.texture_tillings[2] + source_obj.floor_texture_offset[0]) * 0.5
                luv.uv.y = (((l.vert.co.y * objectScale[1]) + objectLocation[1]) * source_obj.texture_tillings[2] + source_obj.floor_texture_offset[1]) * -0.5
            luv.uv.x = luv.uv.x
            luv.uv.y = luv.uv.y
    bm.to_mesh(mesh)
    bm.free()

    bool_obj.data = mesh


def update_location_precision(ob):
    ob.location.x = round(ob.location.x, 1)
    ob.location.y = round(ob.location.y, 1)
    ob.location.z = round(ob.location.z, 1)
    cleanup_vertex_precision(ob)


def freeze_transforms(ob):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_pattern(pattern=ob.name)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.select_all(action='DESELECT')


def _update_sector_solidify(self, context):
    ob = context.active_object
    if ob.modifiers:
        mod = ob.modifiers[0]
        mod.thickness = ob.ceiling_height - ob.floor_height
        mod.offset = 1 + ob.floor_height / (mod.thickness / 2)


def update_brush_sector_modifier(ob):
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    mod = ob.modifiers[0]
    mod.use_even_offset = True
    mod.use_quality_normals = True
    mod.use_even_offset = True
    mod.thickness = ob.ceiling_height - ob.floor_height
    mod.offset = 1 + ob.floor_height / (mod.thickness / 2)
    mod.material_offset = 1
    mod.material_offset_rim = 2


def update_brush_sector_materials(ob):
    while len(ob.material_slots) < 3:
        bpy.ops.object.material_slot_add()
    while len(ob.material_slots) > 3:
        bpy.ops.object.material_slot_remove()

    if bpy.data.materials.find(ob.ceiling_texture) != -1:
        ob.material_slots[0].material = bpy.data.materials[ob.ceiling_texture]
    if bpy.data.materials.find(ob.floor_texture) != -1:
        ob.material_slots[1].material = bpy.data.materials[ob.floor_texture]
    if bpy.data.materials.find(ob.wall_texture) != -1:
        ob.material_slots[2].material = bpy.data.materials[ob.wall_texture]


# def update_brush_sector_materials(ob):
#     matCount = 0

#     ceilingMat = bpy.data.materials.find(ob.ceiling_texture) if ob.ceiling_texture != bpy.context.scene.remove_material else -1
#     floorMat = bpy.data.materials.find(ob.floor_texture) if ob.floor_texture != bpy.context.scene.remove_material else -1
#     wallMat = bpy.data.materials.find(ob.wall_texture) if ob.wall_texture != bpy.context.scene.remove_material else -1

#     if ceilingMat != -1:
#         matCount += 1
#     if floorMat != -1:
#         matCount += 1
#     if wallMat != -1:
#         matCount += 1

#     while len(ob.material_slots) < matCount:
#         bpy.ops.object.material_slot_add()
#     while len(ob.material_slots) > matCount:
#         bpy.ops.object.material_slot_remove()

#     matIndex = 0
#     if ceilingMat != -1:
#         ob.material_slots[matIndex].material = bpy.data.materials[ob.ceiling_texture]
#         matIndex += 1
#     if floorMat != -1:
#         ob.material_slots[matIndex].material = bpy.data.materials[ob.floor_texture]
#         matIndex += 1
#     if wallMat != -1:
#         ob.material_slots[matIndex].material = bpy.data.materials[ob.wall_texture]
#         matIndex += 1


def update_brush(obj):
    bpy.context.view_layer.objects.active = obj
    if obj:
        while len(obj.modifiers) > 0:
            obj.modifiers.remove(obj.modifiers[0])

        if obj.brush_type == 'SECTOR':
            update_brush_sector_modifier(obj)
            update_brush_sector_materials(obj)
        # else:

        update_location_precision(obj)


def cleanup_vertex_precision(ob):
    p = bpy.context.scene.map_precision
    if ob.type == 'BRUSH':
        for v in ob.data.vertices:
            if ob.modifiers:
                mod = ob.modifiers[0]
                if mod.type == "SOLIDIFY":
                    v.co.z = ob.floor_height
            v.co.x = round(v.co.x, p)
            v.co.y = round(v.co.y, p)
            v.co.z = round(v.co.z, p)


def apply_CSG(target, source_obj, bool_obj):
    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True)

    copy_materials(target, source_obj)

    mod = target.modifiers.new(name=source_obj.name, type='BOOLEAN')
    mod.object = bool_obj
    mod.operation = csg_operation_to_blender_boolean[source_obj.csg_operation]
    mod.solver = 'EXACT'
    bpy.ops.object.modifier_apply(modifier=source_obj.name)


def build_bool_object(sourceObj):
    bpy.ops.object.select_all(action='DESELECT')
    sourceObj.select_set(True)

    dg = bpy.context.evaluated_depsgraph_get()
    eval_obj = sourceObj.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(eval_obj)
    ob_bool = bpy.data.objects.new("_booley", me)
    copy_transforms(ob_bool, sourceObj)
    cleanup_vertex_precision(ob_bool)

    return ob_bool


def flip_object_normals(ob):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode='OBJECT')


def create_new_boolean_object(scn, name):
    old_map = None
    if bpy.data.meshes.get(name + "_MESH") is not None:
        old_map = bpy.data.meshes[name + "_MESH"]
        old_map.name = "map_old"
    me = bpy.data.meshes.new(name + "_MESH")
    if bpy.data.objects.get(name) is None:
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
    else:
        ob = bpy.data.objects[name]
        ob.data = me
    if old_map is not None:
        bpy.data.meshes.remove(old_map)
    # bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    return ob


def copy_materials(target, source):
    if source.data == None:
        return
    if source.data.materials == None:
        return

    for sourceMaterial in source.data.materials:
        if sourceMaterial != None:
            if sourceMaterial.name not in target.data.materials:
                target.data.materials.append(sourceMaterial)


def copy_transforms(a, b):
    a.location = b.location
    a.scale = b.scale
    a.rotation_euler = b.rotation_euler


def remove_material(obj):
    scn = bpy.context.scene
    if scn.remove_material is not "":
        i = 0
        remove = False
        for m in obj.material_slots:
            if scn.remove_material == m.name:
                remove = True
            else:
                if not remove:
                    i += 1
        obj.active_material_index = i
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.material_slot_select()
        bpy.ops.mesh.delete(type='FACE')
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.material_slot_remove()


bpy.types.Scene.map_precision = bpy.props.IntProperty(
    name="Map Precision",
    default=3,
    min=0,
    max=6,
    description='Controls the rounding level of vertex precisions.  Lower numbers round to higher values.  A level of "1" would round 1.234 to 1.2 and a level of "2" would round to 1.23'
)
bpy.types.Scene.remove_material = bpy.props.StringProperty(
    name="Remove Material",
    description="when the map is built all faces with this material will be removed."
)
bpy.types.Object.texture_tillings = bpy.props.FloatVectorProperty(
    name="Texture Tillings",
    default=(1, 1, 1),
    min=0,
    step=10,
    precision=3,
)
bpy.types.Object.ceiling_texture_offset = bpy.props.FloatVectorProperty(
    name="Ceiling Texture Offset",
    default=(0, 0),
    min=0,
    step=10,
    precision=3,
    size=2
)
bpy.types.Object.wall_texture_offset = bpy.props.FloatVectorProperty(
    name="Wall Texture Offset",
    default=(0, 0),
    min=0,
    step=10,
    precision=3,
    size=2
)
bpy.types.Object.floor_texture_offset = bpy.props.FloatVectorProperty(
    name="Floor Texture Offset",
    default=(0, 0),
    min=0,
    step=10,
    precision=3,
    size=2
)
bpy.types.Object.ceiling_height = bpy.props.FloatProperty(
    name="Ceiling Height",
    default=4,
    step=10,
    precision=3,
    update=_update_sector_solidify
)
bpy.types.Object.floor_height = bpy.props.FloatProperty(
    name="Floor Height",
    default=0,
    step=10,
    precision=3,
    update=_update_sector_solidify
)
bpy.types.Object.floor_texture = bpy.props.StringProperty(
    name="Floor Texture",
)
bpy.types.Object.wall_texture = bpy.props.StringProperty(
    name="Wall Texture",
)
bpy.types.Object.ceiling_texture = bpy.props.StringProperty(
    name="Ceiling Texture",
)
bpy.types.Object.brush_type = bpy.props.EnumProperty(
    items=[
        ("BRUSH", "Brush", "is a brush"),
        ("SECTOR", "Sector", "is a sector"),
        ("NONE", "None", "none"),
    ],
    name="Brush Type",
    description="the brush type",
    default='NONE'
)
bpy.types.Object.csg_operation = bpy.props.EnumProperty(
    items=[
        ("ADD", "Add", "add/union geometry to output"),
        ("SUBTRACT", "Subtract", "subtract/remove geometry from output"),
    ],
    name="CSG Operation",
    description="the CSG operation",
    default='ADD'
)
csg_operation_to_blender_boolean = {
    "ADD": "UNION",
    "SUBTRACT": "DIFFERENCE"
}
bpy.types.Object.csg_order = bpy.props.IntProperty(
    name="CSG Order",
    default=0,
    description='Controls the order of CSG operation of the object'
)
bpy.types.Object.brush_auto_texture = bpy.props.BoolProperty(
    name="Brush Auto Texture",
    default=True,
    description='Auto Texture on or off'
)
bpy.types.Scene.flip_normals = bpy.props.BoolProperty(
    name="Flip Normals",
    default=True,
    description='Flip output normals'
)


class LevelBuddyPanel(bpy.types.Panel):
    bl_label = "Level Buddy"
    bl_space_type = "VIEW_3D"
    bl_region_type = 'UI'
    bl_category = 'Level Buddy'

    def draw(self, context):
        ob = context.active_object
        scn = bpy.context.scene
        layout = self.layout
        col = layout.column(align=True)
        col.label(icon="WORLD", text="Map Settings")
        col.prop(scn, "map_precision")
        col.prop(scn, "flip_normals")
        col.prop_search(scn, "remove_material", bpy.data, "materials")
        col = layout.column(align=True)
        col.operator("scene.level_buddy_build_map", text="Build Map", icon="MOD_BUILD").bool_op = "UNION"
        col.operator("scene.level_buddy_open_material", text="Open Material", icon="TEXTURE")
        col = layout.column(align=True)
        col.label(icon="SNAP_PEEL_OBJECT", text="Tools")
        if bpy.context.mode == 'EDIT_MESH':
            col.operator("object.level_rip_geometry", text="Rip", icon="UNLINKED").remove_geometry = True
        else:
            col.operator("scene.level_buddy_new_geometry", text="New Sector", icon="MESH_PLANE").brush_type = 'SECTOR'
            col.operator("scene.level_buddy_new_geometry", text="New Brush", icon="CUBE").brush_type = 'BRUSH'
        if ob is not None and len(bpy.context.selected_objects) > 0:
            col = layout.column(align=True)
            col.label(icon="MOD_ARRAY", text="Brush Properties")
            col.prop(ob, "brush_type", text="Brush Type")
            col.prop(ob, "csg_operation", text="CSG Op")
            col.prop(ob, "csg_order", text="CSG Order")
            col.prop(ob, "brush_auto_texture", text="Auto Texture")
            if ob.brush_auto_texture:
                col = layout.column(align=True)
                col.prop(ob, "texture_tillings")
                col = layout.row(align=True)
                col.prop(ob, "ceiling_texture_offset")
                col = layout.row(align=True)
                col.prop(ob, "wall_texture_offset")
                col = layout.row(align=True)
                col.prop(ob, "floor_texture_offset")
            if ob.brush_type == 'SECTOR' and ob.modifiers:
                col = layout.column(align=True)
                col.label(icon="MOD_ARRAY", text="Sector Properties")
                col.prop(ob, "ceiling_height")
                col.prop(ob, "floor_height")
                # layout.separator()
                col = layout.column(align=True)
                col.prop_search(ob, "ceiling_texture", bpy.data, "materials", icon="MATERIAL", text="Ceiling")
                col.prop_search(ob, "wall_texture", bpy.data, "materials", icon="MATERIAL", text="Wall")
                col.prop_search(ob, "floor_texture", bpy.data, "materials", icon="MATERIAL", text="Floor")


class LevelBuddyNewGeometry(bpy.types.Operator):
    bl_idname = "scene.level_buddy_new_geometry"
    bl_label = "Level New Geometry"

    brush_type: bpy.props.StringProperty(name="brush_type", default='NONE')

    def execute(self, context):
        scn = bpy.context.scene
        bpy.ops.object.select_all(action='DESELECT')

        if self.brush_type == 'SECTOR':
            bpy.ops.mesh.primitive_plane_add(size=1)
        else:
            bpy.ops.mesh.primitive_cube_add(size=1)

        ob = bpy.context.active_object

        if self.brush_type == 'SECTOR':
            ob.csg_operation = 'SUBTRACT'
        else:
            ob.csg_operation = 'ADD'

        ob.display_type = 'WIRE'
        ob.name = self.brush_type
        ob.data.name = self.brush_type
        ob.brush_type = self.brush_type
        ob.csg_order = 0
        ob.brush_auto_texture = True
        bpy.context.view_layer.objects.active = ob

        ob.ceiling_height = 4
        ob.floor_height = 0
        ob.texture_tillings = (1.0, 1.0, 1.0)
        ob.ceiling_texture_offset = (0.0, 0.0)
        ob.wall_texture_offset = (0.0, 0.0)
        ob.floor_texture_offset = (0.0, 0.0)
        ob.ceiling_texture = ""
        ob.wall_texture = ""
        ob.floor_texture = ""

        update_brush(ob)

        return {"FINISHED"}


class LevelBuddyRipGeometry(bpy.types.Operator):
    bl_idname = "object.level_rip_geometry"
    bl_label = "Level Rip Sector"

    remove_geometry: bpy.props.BoolProperty(name="remove_geometry", default=False)

    def execute(self, context):
        active_obj = bpy.context.active_object

        active_obj_bm = bmesh.from_edit_mesh(active_obj.data)
        riped_obj_bm = bmesh.new()

        # https://blender.stackexchange.com/questions/179667/split-off-bmesh-selected-faces
        active_obj_bm.verts.ensure_lookup_table()
        active_obj_bm.edges.ensure_lookup_table()
        active_obj_bm.faces.ensure_lookup_table()

        selected_faces = [x for x in active_obj_bm.faces if x.select]
        selected_edges = [x for x in active_obj_bm.edges if x.select]

        py_verts = []
        py_edges = []
        py_faces = []

        # rip geometry
        if len(selected_faces) > 0:
            for f in selected_faces:
                cur_face_indices = []
                for v in f.verts:
                    if v not in py_verts:
                        py_verts.append(v)
                    cur_face_indices.append(py_verts.index(v))

                py_faces.append(cur_face_indices)
        elif len(selected_edges) > 0:
            for e in selected_edges:
                if e.verts[0] not in py_verts:
                    py_verts.append(e.verts[0])
                if e.verts[1] not in py_verts:
                    py_verts.append(e.verts[1])

                vIndex0 = py_verts.index(e.verts[0])
                vIndex1 = py_verts.index(e.verts[1])

                py_edges.append([vIndex0, vIndex1])
        else:
            # early out
            riped_obj_bm.free()
            return {"CANCELLED"}

        # remove riped
        if active_obj.brush_type != 'BRUSH' and self.remove_geometry and len(selected_faces) > 0:
            edges_to_remove = []
            for f in selected_faces:
                for e in f.edges:
                    if e not in edges_to_remove:
                        edges_to_remove.append(e)

            for f in selected_faces:
                active_obj_bm.faces.remove(f)

            for e in edges_to_remove:
                if e.is_wire:
                    active_obj_bm.edges.remove(e)

        active_obj_bm.verts.ensure_lookup_table()
        active_obj_bm.edges.ensure_lookup_table()
        active_obj_bm.faces.ensure_lookup_table()

        # create mesh
        riped_mesh = bpy.data.meshes.new(name='riped_mesh')
        mat = active_obj.matrix_world
        if len(py_faces) > 0:
            riped_mesh.from_pydata([mat @ x.co for x in py_verts], [], py_faces)
        else:
            riped_mesh.from_pydata([mat @ x.co for x in py_verts], py_edges, [])

        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        riped_obj = active_obj.copy()
        riped_obj.data = riped_mesh
        copy_materials(riped_obj, active_obj)
        bpy.context.scene.collection.objects.link(riped_obj)

        riped_obj.select_set(True)
        bpy.context.view_layer.objects.active = riped_obj
        bpy.ops.object.mode_set(mode='EDIT')

        bpy.ops.mesh.select_all(action='SELECT')

        riped_obj_bm.free()

        return {"FINISHED"}


class LevelBuddyBuildMap(bpy.types.Operator):
    bl_idname = "scene.level_buddy_build_map"
    bl_label = "Build Map"

    bool_op: bpy.props.StringProperty(
        name="bool_op",
        default="UNION"
    )

    def execute(self, context):
        scn = bpy.context.scene
        was_edit_mode = False
        old_active = bpy.context.active_object
        old_selected = bpy.context.selected_objects.copy()
        if bpy.context.mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='OBJECT')
            was_edit_mode = True

        brush_dictionary_list = {}
        brush_orders_sorted_list = []

        level_map = create_new_boolean_object(scn, "LevelGeometry")
        level_map.data = bpy.data.meshes.new("LevelGeometryMesh")
        level_map.hide_select = True
        level_map.hide_set(False)

        visible_objects = bpy.context.scene.collection.all_objects
        for ob in visible_objects:

            if not ob:
                continue

            if ob != level_map and ob.brush_type != 'NONE':
                update_brush(ob)

                if brush_dictionary_list.get(ob.csg_order, None) == None:
                    brush_dictionary_list[ob.csg_order] = []

                if ob.csg_order not in brush_orders_sorted_list:
                    brush_orders_sorted_list.append(ob.csg_order)

                brush_dictionary_list[ob.csg_order].append(ob)

        brush_orders_sorted_list.sort()
        bpy.context.view_layer.objects.active = level_map

        name_index = 0
        for order in brush_orders_sorted_list:
            brush_list = brush_dictionary_list[order]
            for brush in brush_list:
                brush.name = brush.csg_operation + "[" + str(order) + "]" + str(name_index)
                name_index += 1
                bool_obj = build_bool_object(brush)
                if brush.brush_auto_texture:
                    auto_texture(bool_obj, brush)
                apply_CSG(level_map, brush, bool_obj)

        remove_material(level_map)

        update_location_precision(level_map)

        if bpy.context.scene.flip_normals:
            flip_object_normals(level_map)

        # restore context
        bpy.ops.object.select_all(action='DESELECT')
        if old_active:
            old_active.select_set(True)
            bpy.context.view_layer.objects.active = old_active
        if was_edit_mode:
            bpy.ops.object.mode_set(mode='EDIT')
        for obj in old_selected:
            if obj:
                obj.select_set(True)

        # remove trash
        for o in bpy.data.objects:
            if o.users == 0:
                bpy.data.objects.remove(o)
        for m in bpy.data.meshes:
            if m.users == 0:
                bpy.data.meshes.remove(m)
        # for m in bpy.data.materials:
        #     if m.users == 0:
        #         bpy.data.materials.remove(m)

        return {"FINISHED"}


class LevelBuddyOpenMaterial(bpy.types.Operator, ImportHelper):
    bl_idname = "scene.level_buddy_open_material"
    bl_label = "Open Material"

    filter_glob: bpy.props.StringProperty(
        default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp',
        options={'HIDDEN'}
    )

    files: bpy.props.CollectionProperty(
        type=bpy.types.OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    def execute(self, context):
        directory, fileNameExtension = os.path.split(self.filepath)

        # do it for all selected files/images
        for f in self.files:
            fileName, fileExtension = os.path.splitext(f.name)

            # new material or find it
            new_material_name = fileName
            new_material = bpy.data.materials.get(new_material_name)

            if new_material == None:
                new_material = bpy.data.materials.new(new_material_name)

            new_material.use_nodes = True
            new_material.preview_render_type = 'FLAT'

            # We clear it as we'll define it completely
            new_material.node_tree.links.clear()
            new_material.node_tree.nodes.clear()

            # create nodes
            bsdfNode = new_material.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
            outputNode = new_material.node_tree.nodes.new('ShaderNodeOutputMaterial')
            texImageNode = new_material.node_tree.nodes.new('ShaderNodeTexImage')
            texImageNode.name = fileName
            texImageNode.image = bpy.data.images.load(directory + "\\" + fileName + fileExtension, check_existing=True)

            # create node links
            new_material.node_tree.links.new(bsdfNode.outputs['BSDF'], outputNode.inputs['Surface'])
            new_material.node_tree.links.new(bsdfNode.inputs['Base Color'], texImageNode.outputs['Color'])

            # some params
            bsdfNode.inputs['Roughness'].default_value = 0
            bsdfNode.inputs['Specular'].default_value = 0

        return {"FINISHED"}


def register():
    bpy.utils.register_class(LevelBuddyPanel)
    bpy.utils.register_class(LevelBuddyBuildMap)
    bpy.utils.register_class(LevelBuddyNewGeometry)
    bpy.utils.register_class(LevelBuddyRipGeometry)
    bpy.utils.register_class(LevelBuddyOpenMaterial)


def unregister():
    bpy.utils.unregister_class(LevelBuddyPanel)
    bpy.utils.unregister_class(LevelBuddyBuildMap)
    bpy.utils.unregister_class(LevelBuddyNewGeometry)
    bpy.utils.unregister_class(LevelBuddyRipGeometry)
    bpy.utils.unregister_class(LevelBuddyOpenMaterial)


if __name__ == "__main__":
    register()
