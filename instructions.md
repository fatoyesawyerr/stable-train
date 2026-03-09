# AI Coding Agent Instructions

## Project Overview

This is a **CHGNet machine learning training pipeline** that processes VASP (Vienna Ab initio Simulation Package) computational materials science simulations. The project extracts atomic structures, energies, and forces from VASP output files to build datasets for machine learning models.

### Architecture

- **Input**: VASP simulation outputs (directories numbered 1-6 within `50-hzo-m/`) containing `vasprun.xml` files
- **Processing**: `train.py` aggregates multi-structure VASP data using CHGNet's `StructureData` class
- **Output**: Unified dataset object ready for ML model training
- **Dependencies**: CHGNet (`chgnet.data.dataset`), PyMatGen (`pymatgen.io.vasp`)

## Key Data Structures

### VASP Output Organization
```
50-hzo-m/
  ├── POSCAR_*.vasp          # Initial structure definitions
  └── 1-6/                   # Simulation runs (numbered directories)
      └── vasprun.xml        # Complete simulation results (parsed by train.py)
```

### Data Extraction Flow
1. Glob discovers all `vasprun.xml` files recursively: `glob.glob("*/vasprun.xml")`
2. PyMatGen parses each file into: `Vasprun(vr_file)`
3. Extract three parallel arrays:
   - **Structures**: `vr.final_structure` (atomic positions after convergence)
   - **Energies**: `vr.final_energy / len(structure)` (normalized per-atom energy)
   - **Forces**: `vr.ionic_steps[-1]["forces"]` (forces on atoms at final step)
4. CHGNet wraps them: `StructureData(structures=..., energies=..., forces=...)`

## Critical Code Patterns

### Error Handling
- Wraps each Vasprun parse in try-except; failures print diagnostic and skip file
- **Pattern**: Robustness over strictness—incomplete VASP runs are gracefully ignored
- **Location**: Lines 15-24 in `train.py`

### Progress Tracking
- Print statements at load time and completion: `print(f"Loaded {vr_file}")`, `print("Dataset ready!")`
- **Convention**: Use string interpolation with file paths for debugging parallel file processing

### Normalization Convention
- **Energy is per-atom**: Divide `final_energy` by structure size—NOT stored raw
- **Forces are as-is**: Numpy arrays from final ionic step, not normalized

## Running the Pipeline

### Prerequisites
- Python 3.8+
- Required packages: `chgnet`, `pymatgen`
- Install via: `pip install chgnet pymatgen`

### Execution
```bash
# From the project root (stable-train directory)
python train.py
```

- Script discovers all `vasprun.xml` files under `50-hzo-m/` subdirectories
- Prints progress for each file loaded and completion status
- Output: `dataset` object in memory (not persisted unless code is modified)

### Expected Output
```
Found 6 VASP runs
Loaded 50-hzo-m/1/vasprun.xml
Loaded 50-hzo-m/2/vasprun.xml
...
Dataset ready!
```

## Common Workflows

### Adding New Data Sources
1. Place new VASP simulation subdirectories in `50-hzo-m/` with names matching the glob pattern (e.g., `7/`, `8/`)
2. Ensure each contains a `vasprun.xml` file
3. Re-run `train.py`; glob will auto-discover new files

### Debugging Failed Parses
- Check exception message in console output
- Common causes: corrupted `vasprun.xml`, incomplete VASP convergence (missing `ionic_steps[-1]`)
- Inspect raw OUTCAR or INCAR files in that run's directory

### Dataset Inspection
- After creation, `dataset.structures`, `dataset.energies`, `dataset.forces` are list-like
- Each parallel index maps: `structures[i]`, `energies[i]`, `forces[i]` belong together

## External Integrations

- **CHGNet**: Provides `StructureData` container—acts as data standardization layer
- **PyMatGen**: VASP I/O parsing; tolerates minor format variations in `vasprun.xml`
- Both dependencies handle unit conversions internally (eV to ML-ready formats)

## Project-Specific Notes

- This is a **data preparation stage**, not model training—no ML code here
- VASP file hierarchy (1-6 subdirectories) represents independent MD/relaxation runs
- The flat structure (not deep nesting) makes glob patterns simple and predictable
