"""
Calculate Oriented Cuboid Volume of Molecules
Parses geometry files and computes the minimal oriented bounding box volume

Author: Pham Trong Lam
Email: pham.trong.lam@zeon.co.jp
"""

import numpy as np
import os
from pathlib import Path
from typing import Tuple, List, Dict


def parse_geometry_file(filepath: str) -> np.ndarray:
    """
    Parse a geometry file and extract atomic coordinates.
    
    Args:
        filepath: Path to the geometry file
        
    Returns:
        numpy array of shape (N, 3) containing atomic coordinates in Angstroms
    """
    coordinates = []
    
    with open(filepath, 'r') as f:
        # Skip header lines
        lines = f.readlines()
        
        # Find the start of coordinate data (after the dashes)
        data_start = False
        for line in lines:
            if '-----' in line and data_start is False:
                data_start = True
                continue
            
            if data_start and line.strip():
                # Parse the coordinate line
                parts = line.split()
                if len(parts) >= 6:
                    try:
                        # Extract x, y, z coordinates (last 3 columns)
                        x = float(parts[-3])
                        y = float(parts[-2])
                        z = float(parts[-1])
                        coordinates.append([x, y, z])
                    except (ValueError, IndexError):
                        # Skip lines that can't be parsed
                        continue
    
    return np.array(coordinates)


def calculate_oriented_cuboid_volume(coordinates: np.ndarray) -> Tuple[float, Dict]:
    """
    Calculate the volume of the minimal oriented bounding box (OBB).
    
    Uses Principal Component Analysis (PCA) to find the principal axes
    of the point cloud and computes the bounding box in that coordinate system.
    
    Args:
        coordinates: numpy array of shape (N, 3) containing atomic coordinates
        
    Returns:
        Tuple containing:
        - volume: float, the volume of the oriented cuboid in cubic Angstroms
        - info: dict containing dimensions (length, width, height) and principal axes
    """
    # Center the coordinates
    center = np.mean(coordinates, axis=0)
    centered = coordinates - center
    
    # Compute covariance matrix
    cov_matrix = np.cov(centered.T)
    
    # Get eigenvalues and eigenvectors
    eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
    
    # Sort by eigenvalues in descending order
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    
    # Project points onto principal axes
    projected = centered @ eigenvectors
    
    # Get min and max along each principal axis
    min_coords = np.min(projected, axis=0)
    max_coords = np.max(projected, axis=0)
    
    # Calculate dimensions
    dimensions = max_coords - min_coords
    length, width, height = dimensions
    
    # Calculate volume
    volume = length * width * height
    
    info = {
        'center': center,
        'dimensions': {
            'length': length,
            'width': width,
            'height': height
        },
        'principal_axes': eigenvectors,
        'eigenvalues': eigenvalues,
        'num_atoms': len(coordinates)
    }
    
    return volume, info

def calculate_enclosed_cube_volume(info: Dict) -> float:
    """
    Calculate the volume of an enclosed cube based on the oriented bounding box.
    
    Uses the largest dimension of the oriented bounding box as the cube side length,
    ensuring the cube fits within the box.
    
    Args:
        info: Dictionary containing dimension information from calculate_oriented_cuboid_volume
        
    Returns:
        float: Volume of the cube in cubic Angstroms
    """
    dimensions = info['dimensions']
    side_length = max(dimensions['length'], dimensions['width'], dimensions['height'])
    cube_volume = side_length ** 3
    return cube_volume
    
def process_files(file_list: List[str]) -> Dict[str, Tuple[float, Dict]]:
    """
    Process a list of geometry files and calculate their cuboid volumes.
    
    Args:
        file_list: List of file paths to process
        
    Returns:
        Dictionary mapping filename to (volume, info) tuple
    """
    results = {}
    
    for filepath in file_list:
        if not os.path.exists(filepath):
            print(f"WARNING: File not found: {filepath}")
            continue
            
        try:
            print(f"Processing: {os.path.basename(filepath)}")
            coordinates = parse_geometry_file(filepath)
            
            if len(coordinates) == 0:
                print(f"  ERROR: No coordinates found in {filepath}")
                continue
            

            volume, info = calculate_oriented_cuboid_volume(coordinates)
            cube_volume = calculate_enclosed_cube_volume(info)
            results[os.path.basename(filepath)] = (volume, info, cube_volume)
            
            print(f"  ✓ Oriented Cuboid Volume: {volume:.2f} Ų (Angstroms³)")
            print(f"    Enclosed Cube Volume: {cube_volume:.2f} Ų (Angstroms³)")
            print(f"    Atoms: {info['num_atoms']}")
            print(f"    Dimensions: {info['dimensions']['length']:.2f} × {info['dimensions']['width']:.2f} × {info['dimensions']['height']:.2f} Å")
            
        except Exception as e:
            print(f"  ERROR processing {filepath}: {str(e)}")
    
    return results


def print_summary(results: Dict[str, Tuple[float, Dict]]) -> None:
    """
    Print a formatted summary of all results.
    
    Args:
        results: Dictionary of results from process_files
    """
    print("\n" + "="*100)
    print("CUBOID VOLUME SUMMARY")
    print("="*100)
    print(f"{'Filename':<40} {'Cuboid (Å³)':<20} {'Cube (Å³)':<20} {'Atoms':<10}")
    print("-"*100)
    
    for filename, (volume, info, cube_volume) in sorted(results.items()):
        print(f"{filename:<40} {volume:>15.2f}   {cube_volume:>15.2f}   {info['num_atoms']:>8}")
    print("="*100)


def main():
    """Main function to run the volume calculation."""
    
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    
    # Find all geometry files (ending with _last_geom.txt)
    geometry_files = list(script_dir.glob("*_last_geom.txt"))
    
    if not geometry_files:
        print("No geometry files found (*_last_geom.txt)")
        return
    
    print(f"Found {len(geometry_files)} geometry files")
    print()
    
    # Convert to strings
    file_list = [str(f) for f in sorted(geometry_files)]
    
    # Process all files
    results = process_files(file_list)
    
    # Print summary
    if results:
        print_summary(results)
        
        # Save results to CSV
        output_csv = script_dir / "cuboid_volumes.csv"
        with open(output_csv, 'w') as f:
            f.write("Filename,Cuboid_Volume (Å³),Cube_Volume (Å³),Num_Atoms,Length (Å),Width (Å),Height (Å)\n")
            for filename, (volume, info, cube_volume) in sorted(results.items()):
                dims = info['dimensions']
                f.write(f"{filename},{volume:.2f},{cube_volume:.2f},{info['num_atoms']},{dims['length']:.2f},{dims['width']:.2f},{dims['height']:.2f}\n")
        
        print(f"\nResults saved to: {output_csv}")
    else:
        print("No files were processed successfully.")


if __name__ == "__main__":
    main()

