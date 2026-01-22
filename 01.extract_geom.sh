#!/usr/bin/env bash
# Extract the last "Standard orientation" geometry from Gaussian output files.
# Usage: ./extract_geom.sh file1.log file2.out ...
# Output: file1_last_geom.txt, file2_last_geom.txt, ...
#
# Author: Pham Trong Lam
# Email: pham.trong.lam@zeon.co.jp

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <gaussian_output_file> [more_files...]" >&2
  exit 1
fi

for f in "$@"; do
  echo "Working with ${f} ..."
  out="${f%.*}_last_geom.txt"

  # Find the last occurrence line number of "Standard orientation:"
  # (If none, create an empty output file as requested.)
  start_line=$(grep -n 'Standard orientation:' "$f" | tail -n1 | cut -d: -f1 || true)

  if [ -z "${start_line:-}" ]; then
    : > "$out"
    continue
  fi

  # From the last "Standard orientation:" onward, print:
  #   - The dashed line
  #   - The two header lines
  #   - The dashed line above coordinates
  #   - All coordinate lines
  # Stop BEFORE the trailing dashed line that closes the block.
  awk -v s="$start_line" '
    # Detect dashed separator lines
    function is_dash(line) {
      return (line ~ /^[-[:space:]]{5,}$/)
    }

    NR == s { inblock = 1; dash_count = 0; next }

    inblock {
      # First dashed line (top of table)
      if (dash_count == 0) {
        if (is_dash($0)) { print; dash_count = 1; next }
        else { next } # Skip until first dashed line
      }

      # After first dashed: print header lines and second dashed line
      if (dash_count == 1) {
        print
        if (is_dash($0)) { dash_count = 2; next }
        next
      }

      # After second dashed: coordinates until next dashed line (which we omit)
      if (dash_count == 2) {
        if (is_dash($0)) {
          # Trailing dashed at end of block -> stop printing
          exit
        } else if ($0 ~ /^[[:space:]]*$/) {
          # Blank line should not normally occur here; be safe
          exit
        } else {
          print
          next
        }
      }
    }
  ' "$f" > "$out"
done
``
echo Done