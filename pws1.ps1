$vm_listening_process_metadata = (Get-NetTCPConnection -State Listen | ForEach-Object { $proc = Get-Process -Id $_.OwningProcess; "$($proc.Name):$($_.LocalPort)" }) -join ";"
