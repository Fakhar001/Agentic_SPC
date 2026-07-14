#!/usr/bin/env bash
set -euo pipefail

mkdir -p figures/rendered
for source in figures/*.mmd; do
  name="$(basename "${source%.mmd}")"
  npx -y @mermaid-js/mermaid-cli -i "$source" -o "figures/rendered/${name}.png" -b transparent
  echo "Rendered figures/rendered/${name}.png"
done
