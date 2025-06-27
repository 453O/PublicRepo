#!/bin/bash

# Exit on error, unset variables, or pipeline failure
set -euo pipefail

# Get list of processes with listening ports using ss and awk
output=$(ss -tuln -p | awk 'NR>1 && /LISTEN/ && /\([0-9]+\)/ {
    match($0, /pid=([0-9]+)/, pid);
    match($0, /users:\(\("([^"]+)"/, proc);
    split($4, addr, ":");
    port=addr[length(addr)];
    print proc[1] ":" port
}' | sort -u | paste -sd ';')

echo "$output"
