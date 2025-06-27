```bash
#!/bin/bash

# Exit on error, undefined variable, or pipeline failure
set -euo pipefail

# Check if netstat or ss is available
if command -v ss >/dev/null 2>&1; then
    NETSTAT_CMD="ss -tuln -p"
elif command -v netstat >/dev/null 2>&1; then
    NETSTAT_CMD="netstat -tuln -p"
else
    echo "Error: Neither 'ss' nor 'netstat' is installed." >&2
    exit 1
fi

# Get process names and their listening ports
output=$($NETSTAT_CMD | grep -E 'LISTEN' | awk '{print $4,$7}' | while read -r addr proc_info; do
    # Extract port from address (handles IPv4/IPv6 formats like 0.0.0.0:8001 or [::]:8001)
    port=$(echo "$addr" | grep -oE ':[0-9]+$' | tr -d ':')
    
    # Skip if no valid port is found
    [[ -z "$port" ]] && continue
    
    # Extract process name and PID (handles formats like "pid=1234,name" or "1234/name")
    if [[ "$proc_info" =~ pid=([0-9]+),([^[:space:]]+) || "$proc_info" =~ ([0-9]+)/([^[:space:]]+) ]]; then
        pid=${BASH_REMATCH[1]}
        name=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
        echo -n "$name:$port;"
    fi
done)

# Remove trailing semicolon if output exists
echo "${output%;}"
```
