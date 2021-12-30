bl_info = {
    "name": "ybNFT batch export glTF/glb files",
    "author": "Pedro Arroyo",
    "version": (0, 1, 0),
    "blender": (3, 0, 0),
    "location": "File > Import-Export",
    "description": "Batch export collections to glTF/glb files",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"}


import bpy
import os
import itertools

from bpy_extras.io_utils import ExportHelper
from bpy.props import (BoolProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       IntProperty,
                       CollectionProperty
                       )


def highlightObjects(selection_list):
    for i in selection_list:
        bpy.data.objects[i.name].select = True
        
def file_name(s):
    """Return valid file name from string"""
    #return "".join(x for x in s if x.isalnum())
    return "".join( x for x in s if (x.isalnum() or x in "._- "))

def col_hierarchy(root_col, levels=1):
    """Read hierarchy of the collections in the scene"""
    level_lookup = {}
    def recurse(root_col, parent, depth):
        if depth > levels: 
            return
        if isinstance(parent,  bpy.types.Collection):
            level_lookup.setdefault(parent, []).append(root_col)
        for child in root_col.children:
            recurse(child, root_col,  depth + 1)
    recurse(root_col, root_col.children, 0)
    return level_lookup

def flatten(B):    # function needed for code below;
        A = []
        for i in B:
            if type(i) == list: A.extend(i)
            else: A.append(i)
        return A

                
class TOPBAR_MT_ybnft_menu(bpy.types.Menu):
    bl_label = "ybNFT"

    def draw(self, context):
        layout = self.layout
        #layout.operator("mesh.primitive_cube_add")
        layout.operator("export_scene.ybnft_export_gltfs")

    def menu_draw(self, context):
        self.layout.menu("TOPBAR_MT_ybnft_menu")        

class ExportMultipleObjs(bpy.types.Operator, ExportHelper):
    """Iterates over top level scene collections and batch exports all permutations of subobjects"""
    bl_idname = "export_scene.ybnft_export_gltfs"
    bl_label = "Export Collections to GLTFs"
    bl_options = {'PRESET', 'UNDO'}

    # ExportHelper mixin class uses this
    filename_ext = ''

    filter_glob: StringProperty(
            default='*.glb;*.gltf', 
            options={'HIDDEN'}
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator setting before calling.
    batch_export_format: EnumProperty(
        name='Format',
        items=(('GLB', 'glTF Binary (.glb)',
                'Exports a single file, with all data packed in binary form. '
                'Most efficient and portable, but more difficult to edit later'),
               ('GLTF_EMBEDDED', 'glTF Embedded (.gltf)',
                'Exports a single file, with all data packed in JSON. '
                'Less efficient than binary, but easier to edit later'),
               ('GLTF_SEPARATE', 'glTF Separate (.gltf + .bin + textures)',
                'Exports multiple files, with separate JSON, binary and texture data. '
                'Easiest to edit later')),
        description=(
            'Output format and embedding options. Binary is most efficient, '
            'but JSON (embedded or separate) may be easier to edit later'
        ),
        default='GLB'
    )

    batch_export_copyright: StringProperty(
        name='Copyright',
        description='Legal rights and conditions for the model',
        default=''
    )

    batch_export_image_format: EnumProperty(
        name='Images',
        items=(('AUTO', 'Automatic',
                'Save PNGs as PNGs and JPEGs as JPEGs.\n'
                'If neither one, use PNG'),
                ('JPEG', 'JPEG Format (.jpg)',
                'Save images as JPEGs. (Images that need alpha are saved as PNGs though.)\n'
                'Be aware of a possible loss in quality'),
               ),
        description=(
            'Output format for images. PNG is lossless and generally preferred, but JPEG might be preferable for web '
            'applications due to the smaller file size'
        ),
        default='AUTO'
    )

    batch_export_levels: IntProperty(
        name='Collection Levels',
        description='Set the levels of collections',
        default=1
    )

    batch_export_materials: EnumProperty(
        name='Materials',
        items=(('EXPORT', 'Export',
        'Export all materials used by included objects'),
        ('PLACEHOLDER', 'Placeholder',
        'Do not export materials, but write multiple primitive groups per mesh, keeping material slot information'),
        ('NONE', 'No export',
        'Do not export materials, and combine mesh primitive groups, losing material slot information')),
        description='Export materials ',
        default='EXPORT'
    )

    batch_export_colors: BoolProperty(
        name='Export Vertex Colors',
        description='Export vertex colors with meshes',
        default=True
    )

    batch_export_cameras: BoolProperty(
        name='Export Cameras',
        description='Export cameras',
        default=False
    )

    batch_export_extras: BoolProperty(
        name='Export Custom Properties',
        description='Export custom properties as glTF extras',
        default=False
    )

    batch_export_apply: BoolProperty(
        name='Export Apply Modifiers',
        description='Apply modifiers (excluding Armatures) to mesh objects -'
                    'WARNING: prevents exporting shape keys',
        default=False
    )

    batch_export_yup: BoolProperty(
        name='+Y Up',
        description='Export using glTF convention, +Y up',
        default=True
    )

    
    def execute(self, context):                

        # Get the folder
        folder_path = os.path.dirname(self.filepath)
        scn_col = context.scene.collection

        # Lookups (Collections per level and Parents)
        #lkp_col = col_hierarchy(scn_col, levels=self.batch_export_levels) 
            

        lkp_col = col_hierarchy(scn_col, levels=2)
        lkp_col.pop(bpy.data.scenes['Scene'].collection)
        print("lkp_col")
        print(lkp_col)
        print();

        prt_col = {i : k for k, v in lkp_col.items() for i in v}
        print("prt_col")
        print(prt_col)
        print();

        scn_obj = [o for o in scn_col.objects]
        #candidates = [x for v in lkp_col.values() for x in v]
                
        keys, values = zip(*lkp_col.items())
        candidatedicts = [dict(zip(keys, v)) for v in itertools.product(*values)]
        candidates = []
        for candidatedict in candidatedicts:
            candidates.append(list(candidatedict.values())) 

        print("candidates")
        for candidate in candidates:
            print (candidate)
            print ()    
        #print(list(candidates))        
        #print()

        if not candidates:
            self.report({'INFO'}, "Nothing to export")
            return {'CANCELLED'}        

        # Unlink all Collections and objects
        for c in candidates:
            prt_col.get(c).children.unlink(c)
        for o in scn_obj: 
            scn_col.objects.unlink(o)
        
        # (Re-)link collections of choice to root level and export        
                
        """            
        outlist =[]; templist =[[]]
        for c in candidates:
            #for sublist in c.all_objects:
            outlist = templist; templist = [[]]
            for sitem in c.all_objects:
                for oitem in outlist:
                    newitem = [oitem]
                    if newitem == [[]]: newitem = [sitem]
                    else: newitem = [newitem[0], sitem]
                    templist.append(flatten(newitem))

        outlist = list(filter(lambda x: len(x)==len(candidates), templist))  # remove some partial lists that also creep in
        print ("OUTPUT SETS")
        count = 1
        for outelement in outlist:
            print ("Set #" + str(count))            
            print (outelement)
            print ()  
            count = count + 1
        """        
        # Exports all our candidate sets of collections.
        
        assetname = bpy.path.basename(bpy.context.blend_data.filepath).split('.')[0]
        assetindex = 0
        for collections in candidates:
            
            for collection in collections:
                scn_col.objects.link(collection.all_objects)

            # Generates an export filename of the format <blender file name>_<00x>    
            findex = str(assetindex).rjust(3, '0')    
            fname = file_name(assetname+"_"+findex)
            fpath = os.path.join(folder_path, fname)

            bpy.ops.export_scene.gltf(
                filepath = fpath,
                export_format = self.batch_export_format,
                export_copyright = self.batch_export_copyright,
                export_image_format = self.batch_export_image_format,
                export_materials = self.batch_export_materials,
                export_colors = self.batch_export_colors,
                export_cameras = self.batch_export_cameras,
                export_extras = self.batch_export_extras,
                export_yup = self.batch_export_yup,
                export_apply = self.batch_export_apply
            )

            for collection in collections:
                scn_col.objects.unlink(collection.all_objects)
            
            assetindex += 1
           
        # Reset all back
        for o in scn_obj: 
            scn_col.objects.link(o)
#        for c in candidates: 
#            prt_col.get(c).children.link(c)

        
        return {'FINISHED'}


classes = (ExportMultipleObjs, TOPBAR_MT_ybnft_menu,)


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ExportMultipleObjs.bl_idname, text="Wavefront Batch (.obj)")


def register():
    #bpy.utils.register_class(ExportMultipleObjs)
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_editor_menus.append(TOPBAR_MT_ybnft_menu.menu_draw)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_import)
    #bpy.types.INFO_MT_file_export.append(menu_func_import)
    

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_import)
    bpy.types.TOPBAR_MT_editor_menus.remove(TOPBAR_MT_ybnft_menu.menu_draw)
    for cls in classes:
        bpy.utils.unregister_class(cls)
    #bpy.types.INFO_MT_file_export.remove(menu_func_import)


if __name__ == "__main__":
    register()

    # test call
    #bpy.ops.export_scene.multiple_objs('INVOKE_DEFAULT')
    