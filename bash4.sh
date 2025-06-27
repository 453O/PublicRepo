```bash
#!/bin/bash

# Exit on error, unset variables, or pipeline failure
set -euo pipefail

# Check if netstat is available, else fall back to ss
if command -v netstat >/dev/null 2>&1; then
    # Use netstat to get listening processes and ports
    output=$(netstat -tuln -p 2>/dev/null | awk '/LISTEN/ && /([0-9]+\/[a-zA-Z0-9_-]+)/ {
        split($7, proc, "/"); 
        split($4, addr, ":"); 
        port=addr[length(addr)]; 
        print proc[2] ":" port
    }' | sort -u | paste -sd ';')
else
    # Fallback to ss if netstat is unavailable
    output=$(ss -tuln -p | awk '/LISTEN/ && /pid=[0-9]+/ {
        match($0, /pid=[0-9]+,[^)]+\)\s*users:\(\("([^"]+)"/, proc); 
        split($5, addr, ":"); 
        port=addr[length(addr)]; 
        print proc[1] ":" port
    }' | sort -u | paste -sd ';')
fi

# Output result or empty string if no processes found
echo "${output:-}"
```
