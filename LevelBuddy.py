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
#
#
#  ***** TODO *****
#
#   - clean up code
#   - clean up panel UI
#
#  ***** END TODO *****


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
        matIndex = f.material_index
        if len(source_obj.data.materials) > matIndex:
            if source_obj.data.materials[matIndex] is not None:
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
                        luv.uv.x = ((l.vert.co.y * objectScale[1]) + objectLocation[1]) * source_obj.texture_scale[1]
                        luv.uv.y = ((l.vert.co.z * objectScale[2]) + objectLocation[2]) * source_obj.texture_scale[1]
                    if faceDirection == "-x":
                        luv.uv.x = (((l.vert.co.y * objectScale[1]) + objectLocation[1]) * source_obj.texture_scale[1]) * -1
                        luv.uv.y = ((l.vert.co.z * objectScale[2]) + objectLocation[2]) * source_obj.texture_scale[1]
                    if faceDirection == "y":
                        luv.uv.x = (((l.vert.co.x * objectScale[0]) + objectLocation[0]) * source_obj.texture_scale[1]) * -1
                        luv.uv.y = ((l.vert.co.z * objectScale[2]) + objectLocation[2]) * source_obj.texture_scale[1]
                    if faceDirection == "-y":
                        luv.uv.x = ((l.vert.co.x * objectScale[0]) + objectLocation[0]) * source_obj.texture_scale[1]
                        luv.uv.y = ((l.vert.co.z * objectScale[2]) + objectLocation[2]) * source_obj.texture_scale[1]
                    if faceDirection == "z":
                        luv.uv.x = ((l.vert.co.x * objectScale[0]) + objectLocation[0]) * source_obj.texture_scale[0]
                        luv.uv.y = ((l.vert.co.y * objectScale[1]) + objectLocation[1]) * source_obj.texture_scale[0]
                    if faceDirection == "-z":
                        luv.uv.x = (((l.vert.co.x * objectScale[0]) + objectLocation[0]) * source_obj.texture_scale[2]) * 1
                        luv.uv.y = (((l.vert.co.y * objectScale[1]) + objectLocation[1]) * source_obj.texture_scale[2]) * -1
                    luv.uv.x = luv.uv.x
                    luv.uv.y = luv.uv.y
    bm.to_mesh(mesh)
    bm.free()

    bool_obj.data = mesh


def map_duplicate_material_check():
    ob = bpy.context.object
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
                    map_duplicate_material_check()
                n_index += 1
            m_index += 1


def map_remove_material():
    ob = bpy.context.object
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


def update_sector_plane_modifier(ob):
    if ob.modifiers:
        mod = ob.modifiers[0]
        if mod.type == "SOLIDIFY":
            mod.use_even_offset = True
            mod.thickness = ob.ceiling_height - ob.floor_height
            mod.offset = 1 + ob.floor_height / (mod.thickness / 2)
            mod.material_offset = 1
            mod.material_offset_rim = 2


def update_sector_plane_materials(ob):
    if bpy.data.materials.find(ob.ceiling_texture) != -1:
        ob.material_slots[0].material = bpy.data.materials[ob.ceiling_texture]
    if bpy.data.materials.find(ob.floor_texture) != -1:
        ob.material_slots[1].material = bpy.data.materials[ob.floor_texture]
    if bpy.data.materials.find(ob.wall_texture) != -1:
        ob.material_slots[2].material = bpy.data.materials[ob.wall_texture]


def update_sector(self, context):
    ob = bpy.context.active_object
    if ob is not None:
        if ob.sector_type == 'SECTOR_2D':
            update_sector_plane_modifier(ob)
            update_sector_plane_materials(ob)
        update_location_precision(ob)
        bpy.ops.scene.level_buddy_build_map()


def cleanup_vertex_precision(ob):
    p = bpy.context.scene.map_precision
    if ob.type == 'SECTOR_3D':
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
bpy.types.Object.texture_scale = bpy.props.FloatVectorProperty(
    name="Texture Scale",
    default=(1.0, 1.0, 1.0),
    min=0,
    step=10,
    precision=1,
    update=update_sector
)
bpy.types.Object.ceiling_height = bpy.props.FloatProperty(
    name="Ceiling Height",
    default=4,
    step=10,
    precision=1,
    update=update_sector
)
bpy.types.Object.floor_height = bpy.props.FloatProperty(
    name="Floor Height",
    default=0,
    step=10,
    precision=1,
    update=update_sector
)
bpy.types.Scene.remove_texture = bpy.props.StringProperty(
    name="Remove Material",
    description="when the map is built all faces with this material will be removed."
)
bpy.types.Object.floor_texture = bpy.props.StringProperty(
    name="Floor Texture",
    update=update_sector
)
bpy.types.Object.wall_texture = bpy.props.StringProperty(
    name="Wall Texture",
    update=update_sector
)
bpy.types.Object.ceiling_texture = bpy.props.StringProperty(
    name="Ceiling Texture",
    update=update_sector
)
bpy.types.Object.sector_type = bpy.props.EnumProperty(
    items=[
        ("SECTOR_2D", "2D Sector", "is a 2d sector plane"),
        ("SECTOR_3D", "3D Sector", "is a 3d sector mesh"),
        ("BRUSH_ADD", "Brush Add", "is a 3d brush volume"),
        ("BRUSH_SUB", "Brush Subtract", "is a 3d brush volume"),
        ("NONE", "None", "none"),
    ],
    name="Sector Type",
    description="the sector type",
    default='NONE'
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
        col = layout.column(align=True)
        col.operator("scene.level_buddy_build_map", text="Build Map", icon="MOD_BUILD").bool_op = "UNION"
        col.operator("scene.level_buddy_cleanup", icon="ERROR")
        col.operator("scene.level_buddy_empty_trash", icon="ERROR")
        # layout.separator()
        col = layout.column(align=True)
        col.label(icon="SNAP_PEEL_OBJECT", text="New Sector")
        col.operator("scene.level_new_geometry", text="New 2D Sector", icon="SURFACE_NCURVE").s_type = 'SECTOR_2D'
        col.operator("scene.level_new_geometry", text="New 3D Sector", icon="SNAP_FACE").s_type = 'SECTOR_3D'
        col.operator("scene.level_new_geometry", text="New Brush Add", icon="SNAP_VOLUME").s_type = 'BRUSH_ADD'
        col.operator("scene.level_new_geometry", text="New Brush Sub", icon="SNAP_VOLUME").s_type = 'BRUSH_SUB'
        # layout.separator()
        col = layout.column(align=True)
        if ob is not None and len(bpy.context.selected_objects) > 0:
            col.label(icon="MOD_ARRAY", text="Sector Settings")
            col.prop(ob, "sector_type", text="Type")
            if ob.sector_type == 'SECTOR_2D' or ob.sector_type == 'SECTOR_3D':
                col = layout.row(align=True)
                col.prop(ob, "texture_scale")
            if ob.modifiers:
                mod = ob.modifiers[0]
                if mod.type == "SOLIDIFY":
                    col = layout.column(align=True)
                    col.prop(ob, "ceiling_height")
                    col.prop(ob, "floor_height")
                    # layout.separator()
                    col = layout.column(align=True)
                    col.label(icon="MATERIAL", text="Sector Materials")
                    col.prop_search(ob, "ceiling_texture", bpy.data, "materials", icon="MATERIAL", text="Ceiling")
                    col.prop_search(ob, "wall_texture", bpy.data, "materials", icon="MATERIAL", text="Wall")
                    col.prop_search(ob, "floor_texture", bpy.data, "materials", icon="MATERIAL", text="Floor")


class LevelNewGeometry(bpy.types.Operator):
    bl_idname = "scene.level_new_geometry"
    bl_label = "Level New Geometry"

    s_type : bpy.props.StringProperty(name="s_type", default='NONE')

    def execute(self, context):
        scn = bpy.context.scene
        bpy.ops.object.select_all(action='DESELECT')

        bpy.ops.mesh.primitive_plane_add(size=1)
        ob = bpy.context.active_object

        ob.display_type = 'WIRE'
        ob.name = self.s_type
        ob.data.name = self.s_type
        ob.sector_type = self.s_type
        bpy.context.view_layer.objects.active = ob
        bpy.context.object.hide_render = True

        if self.s_type == 'SECTOR_2D' or self.s_type == 'SECTOR_3D':
            ob.texture_scale = (1.0, 1.0, 1.0)

        if self.s_type == 'SECTOR_2D':
            bpy.ops.object.modifier_add(type='SOLIDIFY')
            bpy.context.object.modifiers["Solidify"].offset = 1
            bpy.context.object.modifiers["Solidify"].use_even_offset = True
            bpy.context.object.modifiers["Solidify"].use_quality_normals = True
            ob.ceiling_height = 4
            ob.floor_height = 0
            if len(bpy.data.materials) > 0:
                ob.data.materials.append(bpy.data.materials[0])
                ob.data.materials.append(bpy.data.materials[0])
                ob.data.materials.append(bpy.data.materials[0])
                ob.ceiling_texture = bpy.data.materials[0].name
                ob.wall_texture = bpy.data.materials[0].name
                ob.floor_texture = bpy.data.materials[0].name
            else:
                bpy.ops.object.material_slot_add()
                bpy.ops.object.material_slot_add()
                bpy.ops.object.material_slot_add()
                ob.ceiling_texture = ""
                ob.wall_texture = ""
                ob.floor_texture = ""
            bpy.ops.object.level_update_sector()

        return {"FINISHED"}


class LevelUpdateSector(bpy.types.Operator):
    bl_idname = "object.level_update_sector"
    bl_label = "Level Update Sector"

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        for ob in selected_objects:
            update_sector_plane_modifier(ob)
        return {"FINISHED"}


class LevelCleanupPrecision(bpy.types.Operator):
    bl_idname = "scene.level_buddy_cleanup"
    bl_label = "Level Cleanup Precision"

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        for ob in selected_objects:
            update_location_precision(ob)
        return {"FINISHED"}


class LevelEmptyTrash(bpy.types.Operator):
    bl_idname = "scene.level_buddy_empty_trash"
    bl_label = "Level Empty Trash"

    def execute(self, context):
        for o in bpy.data.objects:
            if o.users == 0:
                bpy.data.objects.remove(o)
        for m in bpy.data.meshes:
            if m.users == 0:
                bpy.data.meshes.remove(m)
        for m in bpy.data.materials:
            if m.users == 0:
                bpy.data.materials.remove(m)
        return {"FINISHED"}


class LevelBuddyBuildMap(bpy.types.Operator):
    bl_idname = "scene.level_buddy_build_map"
    bl_label = "Level Buddy Build Map"

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

        sector_list = []
        brushAdd_list = []
        brushSub_list = []

        level_map = create_new_boolean_object(scn, "LevelGeometry")
        level_map.data = bpy.data.meshes.new("LevelGeometryMesh")

        visible_objects = bpy.context.scene.collection.all_objects
        for ob in visible_objects:
            if ob != level_map and ob.sector_type != 'NONE':
                if ob.sector_type == 'SECTOR_2D' or ob.sector_type == 'SECTOR_3D':
                    sector_list.append(ob)
                    freeze_transforms(ob)
                if ob.sector_type == 'BRUSH_ADD':
                    brushAdd_list.append(ob)
                    update_location_precision(ob)
                if ob.sector_type == 'BRUSH_SUB':
                    brushSub_list.append(ob)
                    update_location_precision(ob)

        bpy.context.view_layer.objects.active = level_map

        for i in range(0, len(sector_list)):
            sector_list[i].name = "sector" + str(i)
            bool_obj = build_bool_object(sector_list[i])
            auto_texture(bool_obj, sector_list[i])
            apply_boolean(level_map, sector_list[i], bool_obj, 'UNION')

        for i in range(0, len(brushAdd_list)):
            brushAdd_list[i].name = "brush_add" + str(i)
            bool_obj = build_bool_object(brushAdd_list[i])
            auto_texture(bool_obj, brushAdd_list[i])
            apply_boolean(level_map, brushAdd_list[i], bool_obj, 'DIFFERENCE')
            update_location_precision(level_map)

        for i in range(0, len(brushSub_list)):
            brushSub_list[i].name = "brush_sub" + str(i)
            bool_obj = build_bool_object(brushSub_list[i])
            auto_texture(bool_obj, brushSub_list[i])
            apply_boolean(level_map, brushSub_list[i], bool_obj, 'UNION')
            update_location_precision(level_map)

        flip_object_normals(level_map)

        map_duplicate_material_check()
        map_remove_material()

        level_map.hide_set(False)
        bpy.ops.object.select_all(action='DESELECT')
        if oldActiveObj is not None:
            oldActiveObj.select_set(True)
            bpy.context.view_layer.objects.active = oldActiveObj
        if edit_mode:
            bpy.ops.object.mode_set(mode='EDIT')

        return {"FINISHED"}


def register():
    bpy.utils.register_class(LevelBuddyPanel)
    bpy.utils.register_class(LevelBuddyBuildMap)
    bpy.utils.register_class(LevelUpdateSector)
    bpy.utils.register_class(LevelNewGeometry)
    bpy.utils.register_class(LevelCleanupPrecision)
    bpy.utils.register_class(LevelEmptyTrash)


def unregister():
    bpy.utils.unregister_class(LevelBuddyPanel)
    bpy.utils.unregister_class(LevelBuddyBuildMap)
    bpy.utils.unregister_class(LevelUpdateSector)
    bpy.utils.unregister_class(LevelNewGeometry)
    bpy.utils.unregister_class(LevelCleanupPrecision)
    bpy.utils.unregister_class(LevelEmptyTrash)


if __name__ == "__main__":
    register()
