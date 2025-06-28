vm_listening_process_metadata=$(ss -tuln -p | grep -v "Netid" | awk '{split($NF, a, "\""); split(a[2], b, "/"); print b[1]":"$5}' | awk -F: '{print $1":"$NF}' | sort -u | paste -sd';')
echo ${vm_listening_process_metadata}
