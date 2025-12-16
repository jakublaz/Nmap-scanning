# 1. Default inputs
:global scanType
:global scanTarget
:local containerName "Nmap-python"
:local sharedPath "disk1/nmap-data"

#Defaults
:if ([:len $scanType] = 0) do={ :set scanType "fast" }
:local cmdString ""

:if ([:len $scanTarget] = 0) do={
    :set cmdString ("auto --preset " . $scanType)
} else={
    :set cmdString ("custom " . $scanTarget . " --preset " . $scanType)
}

:log info ("Scheduler requesting Nmap scan with preset: " . $scanType)

# 2. Define Container Name
:local containerData [/container print as-value where name=$containerName]
:local containerId (($containerData->0)->".id")
:local currentStatus (($containerData->0)->"status")

:log info ("Found Container ID: " . $containerId . " | Status: " . $currentStatus)

# 3. Stop if Running
:if ($currentStatus = "running") do={
    :log info "Container is running. Stopping it..."
    /container stop $containerId
    
    # Wait loop (Max 15s)
    :local waitCount 0
    :while ($waitCount < 15) do={
        :delay 1s
        # Re-check status safely
        :local check [/container print as-value where name=$containerName]
        :if ((($check->0)->"status") != "running") do={
            :set waitCount 100 
        }
        :set waitCount ($waitCount + 1)
    }
}


# 4. Change the Command
/container set $containerId cmd=$cmdString

:local flagName "scheduled.flag.txt"
:local fullFlagPath ($sharedPath . "/" . $flagName)

# A. Clean up if the flag already exists from a previous run
/file remove [find name=$fullFlagPath]

# B. Create the file
/file print file=$fullFlagPath where name="non-existent"
:delay 2s


# 5. Start it up
:log info ("Starting Nmap container with preset: " . $scanType)
/container start $containerId

:set scanType ""
:set scanTarget ""