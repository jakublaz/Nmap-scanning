# 1. Get the requested preset (default to fast if missing)
:global scanType
:if ([:len $scanType] = 0) do={ :set scanType "fast" }

:log info ("Scheduler requesting Nmap scan with preset: " . $scanType)

# 2. Define Container Name
:local containerName "Nmap-python"
:local containerId [ /container find name=$containerName ]

# 3. Stop the container if it is running
:if ([/container get $containerId status] = "running") do={
    /container stop $containerId
    # Wait loop: wait up to 10 seconds for it to actually stop
    :local waitCount 0
    :while ([/container get $containerId status] = "running" && $waitCount < 15) do={
        :delay 1s
        :set waitCount ($waitCount + 1)
    }
}

# 4. Change the Command
# Update the 'cmd' field without deleting the container
/container set $containerId cmd=("auto --preset " . $scanType)

# 5. Start it up
:log info ("Starting Nmap container with preset: " . $scanType)
/container start $containerId