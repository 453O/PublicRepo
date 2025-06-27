#!/bin/bash

# Check if the script is run as root, as ss may require elevated privileges for full access
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root to access all process and port information" >&2
   exit 1
fi

# Check if ss and ps commands are available
if ! command -v ss &> /dev/null || ! command -v ps &> /dev/null; then
    echo "Required commands (ss or ps) not found. Please ensure they are installed." >&2
    exit 1
fi

# Initialize an array to store process-port pairs
declare -a process_port_pairs

# Use ss to get listening ports and their associated PIDs
# -t: TCP, -u: UDP, -l: listening, -p: show process, -n: numeric output
while IFS= read -r line; do
    # Extract PID and port from ss output
    if [[ $line =~ ([0-9]+)\ ([0-9]+)\/([a-zA-Z0-9_-]+) ]]; then
        pid=${BASH_REMATCH[1]}
        port=${BASH_REMATCH[2]}
        process_name=${BASH_REMATCH[3]}

        # Verify process name using ps to ensure accuracy
        process_name=$(ps -p "$pid" -o comm= 2>/dev/null)
        if [[ -n "$process_name" && -n "$port" ]]; then
            process_port_pairs+=("${process_name}:${port}")
        fi
    fi
done < <(ss -tuln -p | awk '/pid=/ {print $NF}' | sed -n 's/.*pid=\([0-9]*\),.*port=\([0-9]*\)\/*\([^)]*\)/\1 \2\/\3/p')

# Remove duplicates and sort the array
readarray -t sorted_pairs < <(printf '%s\n' "${process_port_pairs[@]}" | sort -u)

# Join the array elements with semicolons
if [ ${#sorted_pairs[@]} -eq 0 ]; then
    echo "No processes with listening ports found."
else
    result=$(IFS=';'; echo "${sorted_pairs[*]}")
    echo "$result"
fi

exit 0
