# Molecular Oriented Cuboid Volume Calculator

This script calculates the oriented bounding box (OBB) volume for molecules from geometry coordinate files.

## Features

- Parses molecular geometry files (txt format with atomic coordinates)
- Calculates minimal oriented cuboid volume using Principal Component Analysis (PCA)
- Outputs volume for each molecule
- Generates CSV summary report
- Provides detailed dimension information (length × width × height)

## Author

Pham Trong Lam
pham.trong.lam@zeon.co.jp

## Installation

```bash
pip install -r requirements.txt
```

## Usage

There are **two methods** to calculate molecular volumes:

### Method 1: Bash & AWK (Direct from Gaussian Log Files)

This method uses shell scripts to extract geometry data from Gaussian output files and calculate volumes.

**Step 1:** Extract molecular geometry from Gaussian log files
```bash
./01.extract_geom.sh *.log
```

This script processes all Gaussian log files (`*.log`) and extracts the last configuration/geometry from each file, outputting files named `*_last_geom.txt`.

**Step 2:** Calculate volumes from geometry files
```bash
./02.geometry_to_volume.sh *_last_geom.txt
```

This script processes the extracted geometry files and calculates molecular volumes, outputting results to `02.volume_output.csv`.

**Important:** When using Method 1, ensure you use the **cuboid volume** column from the output CSV. Do not use other volume columns as they may represent different calculation methods.

---

### Method 2: Python Script

This method uses Python with PCA (Principal Component Analysis) for oriented bounding box calculation.

**Run the script:**
```bash
python calculate_cuboid_volume.py
```

The script automatically finds all geometry files in the directory (files ending with `_last_geom.txt`).

### Output

The script produces:

1. **Console Output**: Detailed information for each file
   - Volume in cubic Angstroms (Ų)
   - Number of atoms
   - Dimensions (length × width × height)

2. **CSV Report**: `cuboid_volumes.csv`
   - Filename
   - Volume (Angstroms³)
   - Number of atoms
   - Dimensions (Length, Width, Height in Å)

3. **Summary Statistics**
   - Mean, minimum, and maximum volumes

## Algorithm

### Method 2: Python Script Logic (PCA-based)

The Python script calculates the oriented bounding box volume using Principal Component Analysis (PCA):

1. **Center the coordinates** at the molecular centroid
2. **Compute covariance matrix** of atomic coordinates
3. **Find principal axes** via eigenvalue decomposition
4. **Project atoms** onto principal axes
5. **Calculate dimensions** as the span along each principal axis
6. **Compute volume** as: length × width × height

This approach finds the minimal volume cuboid aligned with the principal axes of the molecular structure, providing the smallest possible cuboid that completely encloses the molecule.

## File Format

Input files should be text files with the following format:

```
Center     Atomic      Atomic             Coordinates (Angstroms)
Number     Number       Type             X           Y           Z
---------------------------------------------------------------------
      1          6           0       -3.235812   -1.123373   -0.296103
      2          6           0       -3.352231    0.000003   -1.351243
      ...
```

The script extracts the X, Y, Z coordinates from each line.

## Example Output

```
Processing: monomer_chair_last_geom.txt
  ✓ Volume: 2456.78 Ų (Angstroms³)
    Atoms: 52
    Dimensions: 12.34 × 15.67 × 12.89 Å

================================================================================
CUBOID VOLUME SUMMARY
================================================================================
Filename                                 Volume (Å³)      Atoms
--------------------------------------------------------------------------------
addpoly_chair_last_geom.txt               5678.90        58
dcbod_chair_last_geom.txt                 3456.78        48
monomer_chair_last_geom.txt               2456.78        52
ROMP_chair_last_geom.txt                  4234.56        54
...
================================================================================
```

