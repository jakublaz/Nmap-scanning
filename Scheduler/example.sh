# Scheduler used 

# Define the container name
:local containerName "Nmap-scheduler-0.5h"

# Find the container ID
:local containerId [/container find name=$containerName]

# Check if container exists
:if ([:len $containerId] > 0) do={

    # Get the container details
    :local containerInfo ([/container print as-value where name=$containerName]->0)
    
    # Check the "running" flag (It returns true or false)
    :local isRunning ($containerInfo->"running")

    # If it is NOT running (false), then start it
    :if ($isRunning = false) do={
        :log info "Starting Nmap Scan..."
        /container start $containerId
    } else={
        :log warning "Nmap Container is already running."
    }

} else={
    :log error "Nmap Container not found. Please run the build script first."
}