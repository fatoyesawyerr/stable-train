from chgnet.data.dataset import StructureData
from pymatgen.io.vasp import Vasprun
import glob
import os

structures = []
energies = []
forces = []

vasp_files = glob.glob("50-hzo-*/*/vasprun.xml")

print(f"Found {len(vasp_files)} VASP runs")

for vr_file in vasp_files:
    try:
        vr = Vasprun(vr_file)
        structure = vr.final_structure
        energy = vr.final_energy / len(structure)
        force = vr.ionic_steps[-1]["forces"]

        structures.append(structure)
        energies.append(energy)
        forces.append(force)

        print(f"Loaded {vr_file}")

    except Exception as e:
        print(f"Skipping {vr_file}: {e}")

dataset = StructureData(
    structures=structures,
    energies=energies,
    forces=forces
)

print("Dataset ready!")
