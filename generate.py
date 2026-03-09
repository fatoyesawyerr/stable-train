from pymatgen.core import Structure
import itertools
import os
import random

# ================= USER SETTINGS =================
input_file = "osPOSCAR"     
output_dir = "os-Hf0.5Zr0.5O2_variants"

target = "Hf"
sub = "Zr"
frac = 0.5

max_structures = 100   # <<< CONTROL DATASET SIZE HERE
random_seed = 42
# =================================================

random.seed(random_seed)

# Load structure
struct = Structure.from_file(input_file)

print("Initial composition:", struct.composition)

# Find all target atom indices
hf_indices = [i for i, site in enumerate(struct) if site.species_string == target]
num_hf = len(hf_indices)

# Enforce exact 50% replacement
num_to_replace = num_hf // 2

print(f"Found {num_hf} {target} atoms.")
print(f"Replacing exactly {num_to_replace} with {sub} (50%).")

# Create output folder
os.makedirs(output_dir, exist_ok=True)

# Generate all possible combinations count (just for info)
from math import comb
total_combos = comb(num_hf, num_to_replace)
print(f"Total possible combinations: {total_combos}")

# ⚠ Avoid full explosion
print(f"Randomly sampling up to {max_structures} structures...")

# Use iterator instead of building huge list
combo_iterator = itertools.combinations(hf_indices, num_to_replace)

# Random sampling without building huge list
selected_combos = random.sample(list(combo_iterator), 
                                min(max_structures, total_combos))

# Generate structures
for count, combo in enumerate(selected_combos, start=1):

    new_struct = struct.copy()

    # Replace selected atoms safely
    for idx in combo:
        if new_struct[idx].species_string == target:
            new_struct.replace(idx, sub)

    # Verify composition
    comp = new_struct.composition
    if comp[target] != num_hf - num_to_replace or comp[sub] != num_to_replace:
        print("⚠ Composition mismatch — skipping")
        continue

    # Sort atoms as Hf, Zr, O
    ordered_species = ["Hf", "Zr", "O"]
    sorted_sites = []

    for specie in ordered_species:
        for site in new_struct:
            if site.species_string == specie:
                sorted_sites.append(site)

    reordered_struct = Structure.from_sites(sorted_sites)

    out_file = os.path.join(output_dir, f"POSCAR_var_{count}.vasp")
    reordered_struct.to(fmt="poscar", filename=out_file)

    print(f"Saved {count}: {reordered_struct.composition}")

print("Done. Controlled 50% Hf → Zr structures generated safely.")