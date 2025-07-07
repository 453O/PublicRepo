Resources
| where type == 'microsoft.compute/virtualmachines'
| extend vmId = tolower(id)
| project vmId, vmName = name, location, resourceGroup
| join kind=leftouter (
    Resources
    | where type == 'microsoft.network/networkinterfaces'
    | extend nsgId = tolower(properties.networkSecurityGroup.id)
    | extend subnetId = tolower(properties.ipConfigurations[0].subnet.id)
    | project nicId = tolower(id), vmId = tolower(properties.virtualMachine.id), nsgId, subnetId
) on vmId
| join kind=leftouter (
    Resources
    | where type == 'microsoft.network/virtualnetworks'
    | mv-expand subnet = properties.subnets
    | extend subnetId = tolower(subnet.id)
    | extend subnetNsgId = tolower(subnet.properties.networkSecurityGroup.id)
    | project subnetId, subnetNsgId
) on subnetId
| join kind=leftouter (
    Resources
    | where type == 'microsoft.network/networksecuritygroups'
    | mv-expand rule = properties.securityRules
    | where rule.properties.direction == 'Inbound'
    | where rule.properties.access == 'Allow'
    | extend nsgId = tolower(id)
    | extend ports = rule.properties.destinationPortRange
    | extend portRanges = iff(isnotempty(rule.properties.destinationPortRanges), rule.properties.destinationPortRanges, array_split(ports, '-'))
    | mv-expand portRanges
    | extend portStart = toint(portRanges[0])
    | extend portEnd = iff(array_length(portRanges) > 1, toint(portRanges[1]), toint(portRanges[0]))
    | project nsgId, portStart, portEnd, protocol = rule.properties.protocol, source = rule.properties.sourceAddressPrefix
) on $left.nsgId == $right.nsgId
| join kind=leftouter (
    Resources
    | where type == 'microsoft.network/networksecuritygroups'
    | mv-expand rule = properties.securityRules
    | where rule.properties.direction == 'Inbound'
    | where rule.properties.access == 'Allow'
    | extend nsgId = tolower(id)
    | extend ports = rule.properties.destinationPortRange
    | extend portRanges = iff(isnotempty(rule.properties.destinationPortRanges), rule.properties.destinationPortRanges, array_split(ports, '-'))
    | mv-expand portRanges
    | extend portStart = toint(portRanges[0])
    | extend portEnd = iff(array_length(portRanges) > 1, toint(portRanges[1]), toint(portRanges[0]))
    | project nsgId, portStart, portEnd, protocol = rule.properties.protocol, source = rule.properties.sourceAddressPrefix
) on $left.subnetNsgId == $right.nsgId
| project
    vmName,
    resourceGroup,
    location,
    nicNsgPorts = iff(isnotnull(portStart), strcat(portStart, iff(portStart != portEnd, strcat('-', portEnd), '')), ''),
    nicNsgProtocol = protocol,
    nicNsgSource = source,
    subnetNsgPorts = iff(isnotnull(portStart1), strcat(portStart1, iff(portStart1 != portEnd1, strcat('-', portEnd1), '')), ''),
    subnetNsgProtocol = protocol1,
    subnetNsgSource = source1
| where isnotempty(nicNsgPorts) or isnotempty(subnetNsgPorts)
| order by vmName, nicNsgPorts, subnetNsgPorts
