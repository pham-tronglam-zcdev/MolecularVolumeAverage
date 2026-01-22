#!/usr/bin/env bash
# Compute volumes and radius of gyration from extracted Gaussian geometry files.
# Usage: ./compute_volumes.sh geom1_last_geom.txt geom2_last_geom.txt ...
# Output (to stdout): 4 columns -> file, method1(cube vol), method2(cuboid vol), method3(Rg)
# At the end, echoes units.
#
# Author: Pham Trong Lam
# Email: pham.trong.lam@zeon.co.jp

set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <geom_file1> [more_geom_files...]" >&2
  exit 1
fi

# Header (comment out if you prefer no header)
printf "%-40s\t%-15s\t%-15s\t%-15s\n" "File" "Cube_Vol(Å^3)" "Cuboid_Vol(Å^3)" "Rg_Vol(Å^3)"

for f in "$@"; do
  awk -v fname="$f" '
    # ---------- Helpers / Methods ----------
    function cube_vol(xlen,ylen,zlen) {
      # Method 1: smallest axis-aligned cube enclosing the molecule (L = max range)
      L = xlen; if (ylen > L) L = ylen; if (zlen > L) L = zlen;
      return L*L*L
    }
    function cuboid_vol(xlen,ylen,zlen) {
      # Method 2: axis-aligned bounding box volume
      return xlen*ylen*zlen
    }
    function radius_gyration_vol(N,sumx,sumy,sumz,sum_r2) {
      # Method 3: Rg = sqrt( mean(r^2) - ||mean(r)||^2 ), equal masses
      if (N <= 0) return "NA"
      mx = sumx/N; my = sumy/N; mz = sumz/N
      rg2 = (sum_r2/N) - (mx*mx + my*my + mz*mz)
      if (rg2 < 0) rg2 = 0    # numerical safety
      return sprintf("%.6f", 4./3. * 3.1415926*sqrt(rg2)^3)
    }

    # ---------- Accumulators ----------
    BEGIN {
      have = 0
      xmin = ymin = zmin = 0
      xmax = ymax = zmax = 0
      sumx = sumy = sumz = 0
      sum_r2 = 0
      N = 0
    }

    # ---------- Parse coordinate rows ----------
    {
      if (NR >= 5 ) {
        x = $4; y = $5; z = $6
        if (!have) {
          xmin=x; xmax=x; ymin=y; ymax=y; zmin=z; zmax=z; have=1
        } else {
          if (x < xmin) xmin = x; if (x > xmax) xmax = x
          if (y < ymin) ymin = y; if (y > ymax) ymax = y
          if (z < zmin) zmin = z; if (z > zmax) zmax = z
        }
        sumx += x; sumy += y; sumz += z
        sum_r2 += (x*x + y*y + z*z)
        N++
      }
    }

    # ---------- Compute and print ----------
    END {
      if (N == 0) {
        printf "%-40s\t%s\t%s\t%s\n", fname, "NA", "NA", "NA"
        exit
      }
      xlen = xmax - xmin
      ylen = ymax - ymin
      zlen = zmax - zmin

      cvol = cube_vol(xlen,ylen,zlen)
      bvol = cuboid_vol(xlen,ylen,zlen)
      rg   = radius_gyration_vol(N,sumx,sumy,sumz,sum_r2)

      printf "%-40s\t%.6f\t%.6f\t%s\n", fname, cvol, bvol, rg
    }
  ' "$f"
done