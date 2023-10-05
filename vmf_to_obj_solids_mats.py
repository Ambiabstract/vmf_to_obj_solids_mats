import re
import os
import sys
import shutil
from collections import defaultdict

#
# Unfinished shitty VMF to OBJ converter script. Converts only solid (brush) geometry;
# Objects in OBJ are grouped by materials.
#
# Usage: install Python, drag-n-drop VMF(s) to this script.
# You will get the OBJ files in the same folder where the VMFs are located.
#
# Features:
# - geometry;
# - UV (only for same texel);
# - materials names;
# - meshes are grouped by materials;
# - optional removing geometry with NODRAW material.
#
# TODO:
# - vertex normals;
# - smoothing groups;
# - extra vertices weld;
# - hierarchy and naming polishing;
# - maybe awesome UV convert for different texels (idk how to do this but i want).
#

# Global vars
texel_dencity_tex = 2048    # default texture size
texel_dencity_units = 300   # default size of an area to apply this texture size (hammer units)
unit_scale = 0.01           # scale OBJ geometry, I need 0.01 because 100 hammer units is 1 meter for my project

# Log file
LOG_FILE = open('vmf_to_obj_log.txt', 'w', encoding='utf-8')

# Func to log and print something
def log_and_print(data):
    print(data)
    LOG_FILE.write(data + '\n')

# Function for counting braces
def find_brace_indices(content, start_index):
    open_brace_count = 0
    close_brace_count = 0
    open_brace_index = -1
    close_brace_index = -1

    for i in range(start_index, len(content)):
        if content[i] == '{':
            if open_brace_index == -1:
                open_brace_index = i
            open_brace_count += 1
        elif content[i] == '}':
            close_brace_count += 1
            if open_brace_count == close_brace_count:
                close_brace_index = i
                break

    return open_brace_index, close_brace_index

# Function for extracting content within braces
def extract_block_content(content, start_index):
    open_brace_index, close_brace_index = find_brace_indices(content, start_index)
    if open_brace_index == -1 or close_brace_index == -1:
        return None
    return content[open_brace_index + 1:close_brace_index].strip()

# Function for checking the amount of blocks and their IDs
def check_blocks_info(blocks, name, parent_name):
    blocks_counter=0
    for item in blocks:
        blocks_counter+=1
    log_and_print(f'{blocks_counter} {name} blocks in {parent_name}:')
    
    block_id = re.compile(r'"id"\s+"([^"]+)"', re.DOTALL)
    for item in blocks:
        #log_and_print(item)        # full content output of solid blocks
        #log_and_print("-" * 50)    # divider for convenience
        
        block_id_match = block_id.match(item)
        if block_id_match:
            log_and_print(block_id_match.group(0))
            
    log_and_print("")
    
# Function for extracting solid blocks from VMF
def extract_solids_from_vmf(vmf_content):
    solid_start_indices = [m.start() for m in re.finditer(r'solid\s*{\s*"id"\s*"', vmf_content)]
    solid_blocks = [extract_block_content(vmf_content, start) for start in solid_start_indices]
    
    check_blocks_info(solid_blocks, "solid", "VMF")
    #log_and_print("")
    
    return solid_blocks

# Extract 'side' blocks from a 'solid' block
def extract_sides_from_solid(solid_content):
    side_start_indices = [m.start() for m in re.finditer(r'side\s*{\s*"id"\s*"', solid_content)]
    side_blocks = [extract_block_content(solid_content, start) for start in side_start_indices]
    
    solid_parent_id_pattern = re.compile(r'"id"\s+"([^"]+)"', re.DOTALL)
    solid_match = solid_parent_id_pattern.match(solid_content)
    if solid_match:
        solid_parent_id = solid_match.group(1)
        #log_and_print(f'solid_content id: {solid_parent_id}')

    check_blocks_info(side_blocks, "side", f"solid {solid_parent_id}")
    
    return side_blocks

# Function to extract vertices from a 'side' block content
def extract_vertices_from_side(side_content):
    # Regular expression pattern for extracting vertices
    vertices_re = re.compile(r'"v" "(.*?)"', re.DOTALL)
    
    # Extract vertices
    vertices_matches = vertices_re.findall(side_content)
    vertices = [tuple(map(float, v.split())) for v in vertices_matches]
    vertices.reverse()  # reverse the vertex order to have correct normals in the final mesh
    
    log_and_print(f"Vertices:\n{vertices}\n")
    
    return vertices

# Function to extract key attributes from a 'side' block content
def extract_side_attributes(side_content):
    # Regular expression patterns for extracting attributes
    plane_re = re.compile(r'"plane"\s+"([^"]+)"', re.DOTALL)
    material_re = re.compile(r'"material"\s+".*/([^/"]+)"', re.DOTALL)
    uaxis_re = re.compile(r'"uaxis"\s+"([^"]+)"', re.DOTALL)
    vaxis_re = re.compile(r'"vaxis"\s+"([^"]+)"', re.DOTALL)
    
    # Extract attributes
    plane_match = plane_re.search(side_content)
    material_match = material_re.search(side_content)
    uaxis_match = uaxis_re.search(side_content)
    vaxis_match = vaxis_re.search(side_content)
    
    plane = plane_match.group(1) if plane_match else None
    material = material_match.group(1) if material_match else None
    uaxis = uaxis_match.group(1) if uaxis_match else None
    vaxis = vaxis_match.group(1) if vaxis_match else None
    
    log_and_print(f"Material:\n{material}\n")
    log_and_print(f"UVs:\n{uaxis}\n{vaxis}\n")
    
    return plane, material, uaxis, vaxis

def convert_vmf_to_obj(vmf_content):
    log_and_print(f"Start convert_vmf_to_obj...\n")
    obj_data = "".join(f'#\n# Atmus OBJ\n#\n\n')
    solid_contents = extract_solids_from_vmf(vmf_content)
    solid_content_index=0
    vertex_index = 0
    for solid_content in solid_contents:
        log_and_print("-" * 50)
        solid_content_index+=1
        solid_id_pattern = re.compile(r'"id"\s+"([^"]+)"', re.DOTALL)
        solid_match = solid_id_pattern.match(solid_content)
        if solid_match:
            solid_id = solid_match.group(1)
        
        if int(solid_id) <= 9:
            tripled_solid_id = "00" + f'{solid_id}'
        elif int(solid_id) <= 99:
            tripled_solid_id = "0" + f'{solid_id}'
        else:
            tripled_solid_id = solid_id
        
        log_and_print(f"Converting Solid_{tripled_solid_id}...")
        
        converted_solid = ""
        converted_solid += f'#\n# Solid_{tripled_solid_id}\n#\n\n'
        
        sides = extract_sides_from_solid(solid_content)
        side_index = 0
        for side in sides:
            side_index += 1
          
            side_id_pattern = re.compile(r'"id"\s+"([^"]+)"', re.DOTALL)
            side_match = side_id_pattern.match(side)
            if side_match:
                side_id = side_match.group(1)
                
            if int(side_id) <= 9:
                tripled_side_id = "00" + f'{side_id}'
            elif int(side_id) <= 99:
                tripled_side_id = "0" + f'{side_id}'
            else:
                tripled_side_id = side_id
            
            vertices = extract_vertices_from_side(side)
            plane, material, uaxis, vaxis = extract_side_attributes(side)
    
            for vert_x, vert_y, vert_z in vertices:
                vertex_index += 1
                converted_solid += f'v {vert_x * unit_scale} {vert_z * unit_scale} {-vert_y * unit_scale}\n'
                
                # UV
                uv_pattern = re.compile(r"(-?\d+\.?\d*)", re.DOTALL)
                u_match = re.findall(uv_pattern, uaxis)
                if u_match:
                    ux, uy, uz, u_shift, u_tex_scale = map(float, u_match)
                v_match = re.findall(uv_pattern, vaxis)
                if v_match:
                    vx, vy, vz, v_shift, v_tex_scale = map(float, v_match)

                u = (vert_x * ux + vert_y * uy + vert_z * uz) / texel_dencity_units + u_shift / texel_dencity_tex
                v = -((vert_x * vx + vert_y * vy + vert_z * vz) / texel_dencity_units + v_shift / texel_dencity_tex)
                
                converted_solid += f'vt {u} {v}\n'
                
            
            converted_solid += f'vn 0.5774 0.5774 -0.5774\n'    # temp normals
            
            converted_solid += f'usemtl {material}\n'           # materials per side
            
            converted_solid += f's off\n'                       # temp smoothing groups
            #converted_solid += f's 1\n'                        # temp smoothing groups

            converted_solid += f'o Side_{tripled_side_id}\n'    # temp object
            converted_solid += f'g Side_{tripled_side_id}\n'    # temp group

            # Faces generation
            converted_solid += f'f '
            for i in range(len(vertices)):
                converted_solid += f'{vertex_index-len(vertices)+i+1}/{vertex_index-len(vertices)+i+1} '
            converted_solid += f'\n'        
            
        converted_data = converted_solid
        
        if converted_data is not None:
            obj_data += converted_data
            obj_data += "\n"
        else:
            print(f"Warning: convert_solid_to_obj_with_uvs returned None for solid_content: {solid_content_index}")

    return obj_data

# Function for merge objects by material and remove geometry with some material (TOOLSNODRAW)
def merge_and_filter_objects_by_material_inplace(obj_file_path, materials_to_remove=None):
    temp_file_path = obj_file_path + '.tmp'
    
    material_to_faces = defaultdict(list)
    current_material = None
    
    vertices = []
    texture_coords = []
    normals = []
    
    if materials_to_remove is None:
        materials_to_remove = set()
    
    # Read the OBJ file and group faces by material, also collect vertices, texture coordinates, and normals
    with open(obj_file_path, 'r') as infile:
        for line in infile:
            line = line.strip()
            if line.startswith('usemtl'):
                current_material = line.split()[1]
            elif line.startswith('f'):
                if current_material is not None and current_material not in materials_to_remove:
                    material_to_faces[current_material].append(line)
            elif line.startswith('v '):
                vertices.append(line)
            elif line.startswith('vt '):
                texture_coords.append(line)
            elif line.startswith('vn '):
                normals.append(line)
    
    # Write the new content to a temporary OBJ file
    with open(temp_file_path, 'w') as outfile:
        # Write vertices, texture coordinates, and normals
        outfile.write('\n'.join(vertices) + '\n')
        outfile.write('\n'.join(texture_coords) + '\n')
        outfile.write('\n'.join(normals) + '\n')
        
        # Write grouped faces by material
        for material, faces in material_to_faces.items():
            outfile.write(f'g {material}\n')
            outfile.write(f'usemtl {material}\n')
            for face in faces:
                outfile.write(face + '\n')
                
    # Replace the original OBJ file with the new content
    shutil.move(temp_file_path, obj_file_path)
    
def main():
    # Assuming the VMF files are dragged onto the script
    for arg in sys.argv[1:]:
        if arg.lower().endswith('.vmf'):
            with open(arg, 'r') as f:
                vmf_content = f.read()
            obj_content = convert_vmf_to_obj(vmf_content)
            
            # Save the OBJ content to a file in the same directory as the VMF file
            obj_file_path = os.path.join(os.path.dirname(arg), f"{os.path.splitext(os.path.basename(arg))[0]}.obj")
            with open(obj_file_path, 'w') as f:
                f.write(obj_content)
            
            # Merge by materials
            merge_and_filter_objects_by_material_inplace(obj_file_path, "TOOLSNODRAW")

try:
    if __name__ == '__main__':
        main()
        log_and_print("-" * 50)
        log_and_print(f'Done!')
        # Close log file because we are decent dudes
        LOG_FILE.close()
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    input("\nPress Enter to exit...")