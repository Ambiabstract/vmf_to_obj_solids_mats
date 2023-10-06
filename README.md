# vmf_to_obj_solids_mats
Shitty VMF to OBJ converter script. Converts only solid (brush) geometry; objects in OBJ are grouped by materials (optional).

Comparison:
![изображение](https://github.com/Ambiabstract/vmf_to_obj_solids_mats/assets/60753651/7464d70d-8929-4630-87b9-1e1c48ce1ff7)
![изображение](https://github.com/Ambiabstract/vmf_to_obj_solids_mats/assets/60753651/38f29626-b3c8-47ef-88b6-53a4fabe1e91)
![изображение](https://github.com/Ambiabstract/vmf_to_obj_solids_mats/assets/60753651/ca90bc4b-d125-487f-a57c-4c3de1145294)
![изображение](https://github.com/Ambiabstract/vmf_to_obj_solids_mats/assets/60753651/01b1ec7e-f285-4a9e-8942-9a1ff4f50653)

Usage: install Python, drag-n-drop VMF(s) to this script.
You will get the OBJ files in the same folder where the VMFs are located.

Features:
- geometry;
- UV for default texture resolution;
- UV for different texels (only if VTF founded);
- materials names;
- meshes are grouped by materials;
- optional removing geometry with NODRAW material.

TODO:
- fix vertex normals;
- fix smoothing groups;
- extra vertices weld;
- hierarchy and naming polishing.
