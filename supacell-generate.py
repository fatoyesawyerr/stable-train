from pymatgen.core import Structure, Species, DummySpecies
from pymatgen.transformations.advanced_transformations import EnumerateStructureTransformation
import os

# === USER SETTINGS ===
input_file = "POSCAR"        # your base HfO2 structure (16 cation sites + 32 O)
output_dir = "enumlib_variants"
anion = "O"
cation_mix = {"Hf": 8, "Zr": 7, "La": 1}  # total = 16 cations
# ======================

# Load structure
struct = Structure.from_file(input_file)

# Identify cation indices
cation_indices = [i for i, site in enumerate(struct) if site.species_string != anion]
print(f"Found {len(cation_indices)} cation sites.")

if sum(cation_mix.values()) != len(cation_indices):
    raise ValueError("Cation counts do not add up to number of cation sites!")

# Replace all cations with dummy species "X"
dummy = DummySpecies("X")
for idx in cation_indices:
    struct[idx] = dummy

# Define occupancies for "X"
occupancy = {
    Species("Hf"): cation_mix["Hf"]/len(cation_indices),
    Species("Zr"): cation_mix["Zr"]/len(cation_indices),
    Species("La"): cation_mix["La"]/len(cation_indices),
}

# Apply disorder
for idx in cation_indices:
    struct[idx] = occupancy

# Set up the enumerator
trans = EnumerateStructureTransformation(max_cell_size=1, symm_prec=1e-3)

# Enumerate ordered structures
enum_structs = trans.apply_transformation(struct, return_ranked_list=0)
print(f"Enumlib generated {len(enum_structs)} symmetry-distinct structures.")

# Save results
os.makedirs(output_dir, exist_ok=True)
for i, s in enumerate(enum_structs, start=1):
    out_file = os.path.join(output_dir, f"POSCAR_enum_{i}.vasp")
    s.to(fmt="poscar", filename=out_file)
    print(f"Saved: {out_file}")

print("All symmetry-distinct co-doped variants generated.")
