# vmf_to_obj_solids_mats
Shitty VMF to OBJ converter (Python script). Converts only solid (brush) geometry; objects in OBJ are grouped by materials (optional).

Comparison:
![изображение](https://github.com/Ambiabstract/vmf_to_obj_solids_mats/assets/60753651/ae041af9-576a-4290-8353-d913b3101e8a)
![изображение](https://github.com/Ambiabstract/vmf_to_obj_solids_mats/assets/60753651/87f51dde-245b-4db1-bcbc-919e5e06d995)
![изображение](https://github.com/Ambiabstract/vmf_to_obj_solids_mats/assets/60753651/ca90bc4b-d125-487f-a57c-4c3de1145294)
![изображение](https://github.com/Ambiabstract/vmf_to_obj_solids_mats/assets/60753651/01b1ec7e-f285-4a9e-8942-9a1ff4f50653)

Usage: install Python, install numpy, drag-n-drop VMF(s) to this script.
You will get the OBJ files in the same folder where the VMFs are located.

Features:
- geometry;
- UV for default texture resolution;
- UV for different texels (only if VTF founded);
- materials names;
- meshes are grouped by materials (optional);
- vertex normals from sides (no smoothing yet);
- optional removing geometry with NODRAW material.

TODO:
- smoothing groups;
- optimization (removal of identical values);
- extra vertices weld;
- hierarchy and naming polishing;
