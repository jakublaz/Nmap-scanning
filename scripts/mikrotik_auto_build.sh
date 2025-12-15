# --- INPUT SECTION ---
:global ContainerCmd

# Configuration Variables
:local containerName "Nmap-python"
:local fileName "nmap-python.tar"
:local interfaceName "veth1"
:local envListName "scan_vars"
:local mountListName "Nmap-python"
:local rootDirName "Nmap-python"
:local cmdString

# --- SETUP ENV LIST ---
:log info "Ensuring environment variables exist..."

# 1. Clear old values in scan_vars to ensure no duplicates/conflicts
/container envs remove [find list=$envListName]

# 2. Add the required variables fresh
/container envs add list=$envListName key="ROUTER_IP" value="192.168.0.3"
/container envs add list=$envListName key="ROUTER_USER" value="user"
/container envs add list=$envListName key="ROUTER_PASS" value="password"
/container envs add list=$envListName key="AUTO" value="192.168.0.0/24"

# Logic: Check if global input exists. If yes, use it. If no, use default.
:if ([:len $ContainerCmd] > 0) do={
    :set cmdString $ContainerCmd
    :log info "Received custom command: $cmdString"
    :set ContainerCmd "" 
} else={
    :set cmdString "custom 192.168.0.0/24 --preset fast"
    :log info "No input provided. Using default: $cmdString"
}

:log info "--- Starting Nmap Container Update ---"

# 1. Stop old container safely
:if ([:len [/container find name=$containerName]] > 0) do={
    :log info "Found old container. Checking status..."
    
    # Try to stop, but ignore error if it's already stopped
    :do {
        /container stop [find name=$containerName]
        :delay 15s
    } on-error={
        :log info "Container was already stopped (or could not be stopped). Proceeding..."
    }
    
    :log info "Removing old container..."
    /container remove [find name=$containerName]
}

# 2. Create new container
:log info "Creating new container with CMD: $cmdString"
/container add \
    file=$fileName \
    interface=$interfaceName \
    envlist=$envListName \
    mounts=$mountListName \
    root-dir=$rootDirName \
    cmd=$cmdString \
    name=$containerName