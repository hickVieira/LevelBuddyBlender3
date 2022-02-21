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


import addon_utils
import bpy
import bmesh

bl_info = {
    "name": "Level Buddy",
    "author": "Matt Lucas + HickVieira (3.0 port)",
    "version": (1, 3),
    "blender": (3, 0, 0),
    "location": "View3D > Tools",
    "description": "A set of workflow tools based on concepts from Doom and Unreal level mapping.",
    "warning": "still under development and lacks documentation.",
    "wiki_url": "https://matt-lucas.itch.io/level-buddy",
    "tracker_url": "",
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
                luv.uv.x = ((l.vert.co.y * objectScale[1]) + objectLocation[1]) * source_obj.texture_tillings[1] + source_obj.wall_texture_offset[0]
                luv.uv.y = ((l.vert.co.z * objectScale[2]) + objectLocation[2]) * source_obj.texture_tillings[1] + source_obj.wall_texture_offset[1]
            if faceDirection == "-x":
                luv.uv.x = (((l.vert.co.y * objectScale[1]) + objectLocation[1]) * source_obj.texture_tillings[1] + source_obj.wall_texture_offset[0]) * -1
                luv.uv.y = ((l.vert.co.z * objectScale[2]) + objectLocation[2]) * source_obj.texture_tillings[1] + source_obj.wall_texture_offset[1]
            if faceDirection == "y":
                luv.uv.x = (((l.vert.co.x * objectScale[0]) + objectLocation[0]) * source_obj.texture_tillings[1] + source_obj.wall_texture_offset[0]) * -1
                luv.uv.y = ((l.vert.co.z * objectScale[2]) + objectLocation[2]) * source_obj.texture_tillings[1] + source_obj.wall_texture_offset[1]
            if faceDirection == "-y":
                luv.uv.x = ((l.vert.co.x * objectScale[0]) + objectLocation[0]) * source_obj.texture_tillings[1] + source_obj.wall_texture_offset[0]
                luv.uv.y = ((l.vert.co.z * objectScale[2]) + objectLocation[2]) * source_obj.texture_tillings[1] + source_obj.wall_texture_offset[1]
            if faceDirection == "z":
                luv.uv.x = ((l.vert.co.x * objectScale[0]) + objectLocation[0]) * source_obj.texture_tillings[0] + source_obj.ceiling_texture_offset[0]
                luv.uv.y = ((l.vert.co.y * objectScale[1]) + objectLocation[1]) * source_obj.texture_tillings[0] + source_obj.ceiling_texture_offset[1]
            if faceDirection == "-z":
                luv.uv.x = (((l.vert.co.x * objectScale[0]) + objectLocation[0]) * source_obj.texture_tillings[2] + source_obj.floor_texture_offset[0]) * 1
                luv.uv.y = (((l.vert.co.y * objectScale[1]) + objectLocation[1]) * source_obj.texture_tillings[2] + source_obj.floor_texture_offset[1]) * -1
            luv.uv.x = luv.uv.x
            luv.uv.y = luv.uv.y
    bm.to_mesh(mesh)
    bm.free()

    bool_obj.data = mesh


def duplicate_material_check(ob):
    m_index = 0
    for m in ob.material_slots:
        if m is not None:
            n_index = 0
            for n in ob.material_slots:
                if m.name == n.name and m_index < n_index:
                    ob.active_material_index = n_index
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='DESELECT')
                    bpy.ops.object.material_slot_select()
                    ob.active_material_index = m_index
                    bpy.ops.object.material_slot_assign()
                    bpy.ops.object.mode_set(mode='OBJECT')
                    ob.active_material_index = n_index
                    bpy.ops.object.material_slot_remove()
                    ob.active_material_index = m_index
                    duplicate_material_check(ob)
                n_index += 1
            m_index += 1


def apply_remove_material(ob):
    scn = bpy.context.scene
    if scn.remove_texture != "":
        i = 0
        remove = False
        for m in ob.material_slots:
            if scn.remove_texture == m.name:
                remove = True
            else:
                if not remove:
                    i += 1
        ob.active_material_index = i
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.material_slot_select()
        bpy.ops.mesh.delete(type='FACE')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.material_slot_remove()


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


def update_brush_sector_modifier(ob):
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    mod = ob.modifiers[0]
    mod.offset = 1
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


def _update_brush(self, context):
    ob = bpy.context.active_object
    if ob is not None:

        while len(ob.modifiers) > 0:
            ob.modifiers.remove(ob.modifiers[0])

        if ob.brush_type == 'SECTOR':
            update_brush_sector_modifier(ob)
            update_brush_sector_materials(ob)
        # else:

        update_location_precision(ob)

def update_brush(obj):
    bpy.context.view_layer.objects.active = obj
    if obj is not None:

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


def apply_boolean(target, source_obj, bool_obj, bool_op):
    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True)

    copy_materials(target, source_obj)
    mod = target.modifiers.new(name=source_obj.name, type='BOOLEAN')
    mod.object = bool_obj
    mod.operation = bool_op
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
    for m in source.data.materials:
        has_material = False
        for mat in target.data.materials:
            if mat is not None and m is not None:
                if mat.name == m.name:
                    has_material = True
        if not has_material:
            target.data.materials.append(m)


def copy_transforms(a, b):
    a.location = b.location
    a.scale = b.scale
    a.rotation_euler = b.rotation_euler


bpy.types.Scene.map_precision = bpy.props.IntProperty(
    name="Map Precision",
    default=3,
    min=0,
    max=6,
    description='Controls the rounding level of vertex precisions.  Lower numbers round to higher values.  A level of "1" would round 1.234 to 1.2 and a level of "2" would round to 1.23'
)
bpy.types.Object.texture_tillings = bpy.props.FloatVectorProperty(
    name="Texture Tillings",
    default=(1, 1, 1),
    min=0,
    step=10,
    precision=1,
    update=_update_brush
)
bpy.types.Object.ceiling_texture_offset = bpy.props.FloatVectorProperty(
    name="Ceiling Texture Offset",
    default=(0, 0),
    min=0,
    step=10,
    precision=1,
    update=_update_brush,
    size=2
)
bpy.types.Object.wall_texture_offset = bpy.props.FloatVectorProperty(
    name="Wall Texture Offset",
    default=(0, 0),
    min=0,
    step=10,
    precision=1,
    update=_update_brush,
    size=2
)
bpy.types.Object.floor_texture_offset = bpy.props.FloatVectorProperty(
    name="Floor Texture Offset",
    default=(0, 0),
    min=0,
    step=10,
    precision=1,
    update=_update_brush,
    size=2
)
bpy.types.Object.ceiling_height = bpy.props.FloatProperty(
    name="Ceiling Height",
    default=4,
    step=10,
    precision=1,
    update=_update_brush
)
bpy.types.Object.floor_height = bpy.props.FloatProperty(
    name="Floor Height",
    default=0,
    step=10,
    precision=1,
    update=_update_brush
)
bpy.types.Scene.remove_texture = bpy.props.StringProperty(
    name="Remove Material",
    description="when the map is built all faces with this material will be removed."
)
bpy.types.Object.floor_texture = bpy.props.StringProperty(
    name="Floor Texture",
    update=_update_brush
)
bpy.types.Object.wall_texture = bpy.props.StringProperty(
    name="Wall Texture",
    update=_update_brush
)
bpy.types.Object.ceiling_texture = bpy.props.StringProperty(
    name="Ceiling Texture",
    update=_update_brush
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
    "ADD" : "UNION",
    "SUBTRACT" : "DIFFERENCE"
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
    bl_category = 'Buddy Tools'

    def draw(self, context):
        ob = context.active_object
        scn = bpy.context.scene
        layout = self.layout
        col = layout.column(align=True)
        col.label(icon="WORLD", text="Map Settings")
        col.prop_search(scn, "remove_texture", bpy.data, "materials", icon="MATERIAL")
        col.prop(scn, "map_precision")
        col.prop(scn, "flip_normals")
        col = layout.column(align=True)
        col.operator("scene.level_buddy_build_map", text="Build Map", icon="MOD_BUILD").bool_op = "UNION"
        # layout.separator()
        col = layout.column(align=True)
        col.label(icon="SNAP_PEEL_OBJECT", text="Tools")
        if bpy.context.mode == 'EDIT_MESH':
            col.operator("object.level_rip_geometry", text="Rip", icon="UNLINKED").remove_geometry = True
        else:
            col.operator("scene.level_new_geometry", text="New Sector", icon="MESH_PLANE").brush_type = 'SECTOR'
            col.operator("scene.level_new_geometry", text="New Brush", icon="CUBE").brush_type = 'BRUSH'
        # layout.separator()
        col = layout.column(align=True)
        if ob is not None and len(bpy.context.selected_objects) > 0:
            col.label(icon="MOD_ARRAY", text="Brush Properties")
            col.prop(ob, "brush_type", text="Brush Type")
            col.prop(ob, "csg_operation", text="CSG Op")
            col.prop(ob, "csg_order", text="CSG Order")
            col.prop(ob, "brush_auto_texture", text="Auto Texture")
            if ob.brush_auto_texture:
                col = layout.row(align=True)
                col.prop(ob, "texture_tillings")
                col = layout.row(align=True)
                col.prop(ob, "ceiling_texture_offset")
                col = layout.row(align=True)
                col.prop(ob, "wall_texture_offset")
                col = layout.row(align=True)
                col.prop(ob, "floor_texture_offset")
            if ob.brush_type == 'SECTOR' and ob.modifiers:
                col = layout.column(align=True)
                col.prop(ob, "ceiling_height")
                col.prop(ob, "floor_height")
                # layout.separator()
                col = layout.column(align=True)
                col.prop_search(ob, "ceiling_texture", bpy.data, "materials", icon="MATERIAL", text="Ceiling")
                col.prop_search(ob, "wall_texture", bpy.data, "materials", icon="MATERIAL", text="Wall")
                col.prop_search(ob, "floor_texture", bpy.data, "materials", icon="MATERIAL", text="Floor")


class LevelNewGeometry(bpy.types.Operator):
    bl_idname = "scene.level_new_geometry"
    bl_label = "Level New Geometry"

    brush_type : bpy.props.StringProperty(name="brush_type", default='NONE')

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
        bpy.context.object.hide_render = True

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


class LevelRipGeometry(bpy.types.Operator):
    bl_idname = "object.level_rip_geometry"
    bl_label = "Level Rip Sector"

    remove_geometry : bpy.props.BoolProperty(name="remove_geometry", default=False)

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
        if self.remove_geometry and len(selected_faces) > 0:
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
        edit_mode = False
        oldActiveObj = None
        if bpy.context.active_object is not None:
            oldActiveObj = bpy.context.active_object
        if bpy.context.mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='OBJECT')
            edit_mode = True

        brush_dictionary_list = {}
        brush_orders_sorted_list = []

        level_map = create_new_boolean_object(scn, "LevelGeometry")
        level_map.data = bpy.data.meshes.new("LevelGeometryMesh")

        visible_objects = bpy.context.scene.collection.all_objects
        for ob in visible_objects:
            if ob != level_map and ob.brush_type != 'NONE':
                update_brush(ob)
                
                if brush_dictionary_list.get(ob.csg_order, None) == None:
                    brush_dictionary_list[ob.csg_order] = []
                
                if ob.csg_order not in brush_orders_sorted_list:
                    brush_orders_sorted_list.append(ob.csg_order)

                brush_dictionary_list[ob.csg_order].append(ob)

        brush_orders_sorted_list.sort()
        bpy.context.view_layer.objects.active = level_map

        for order in brush_orders_sorted_list:
            brush_list = brush_dictionary_list[order]
            for i in range(0, len(brush_list)):
                brush_list[i].name = "brush" + str(i)
                bool_obj = build_bool_object(brush_list[i])
                if brush_list[i].brush_auto_texture:
                    auto_texture(bool_obj, brush_list[i])
                apply_boolean(level_map, brush_list[i], bool_obj, csg_operation_to_blender_boolean[brush_list[i].csg_operation])

        update_location_precision(level_map)
        duplicate_material_check(level_map)
        apply_remove_material(level_map)

        if bpy.context.scene.flip_normals:
            flip_object_normals(level_map)

        level_map.hide_set(False)
        bpy.ops.object.select_all(action='DESELECT')
        if oldActiveObj is not None:
            oldActiveObj.select_set(True)
            bpy.context.view_layer.objects.active = oldActiveObj
        if edit_mode:
            bpy.ops.object.mode_set(mode='EDIT')
        
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


def register():
    bpy.utils.register_class(LevelBuddyPanel)
    bpy.utils.register_class(LevelBuddyBuildMap)
    bpy.utils.register_class(LevelNewGeometry)
    bpy.utils.register_class(LevelRipGeometry)


def unregister():
    bpy.utils.unregister_class(LevelBuddyPanel)
    bpy.utils.unregister_class(LevelBuddyBuildMap)
    bpy.utils.unregister_class(LevelNewGeometry)
    bpy.utils.unregister_class(LevelRipGeometry)


if __name__ == "__main__":
    register()
