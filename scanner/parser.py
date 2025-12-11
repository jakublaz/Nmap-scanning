import nmap
import subprocess
import shlex
import os
import tempfile

# Initialize the scanner object (used later for parsing XML)
nm = nmap.PortScanner()

def run_scan(target, args):
    """
    Runs Nmap ONCE using subprocess, saving output to temp files.
    Parses the XML for the summary and returns the raw text for the email.
    """
    results = {}
    
    # Create temp files for Nmap output
    # -oX: XML output (for Python to read)
    # -oN: Normal output (for human email attachment)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as f_xml:
        xml_path = f_xml.name
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f_txt:
        txt_path = f_txt.name

    try:
        # Construct the command
        # Syntax: nmap [ARGS] [TARGET] -oX [XML_FILE] -oN [TXT_FILE]
        
        # --- FIX APPLIED HERE ---
        # target.split() turns "192.168.0.1 192.168.0.2" into ["192.168.0.1", "192.168.0.2"]
        cmd = ["nmap"] + shlex.split(args) + target.split() + ["-oX", xml_path, "-oN", txt_path]
        
        # Run the scan (Capturing stdout/stderr just in case, though we rely on files)
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)

        # 1. READ RAW OUTPUT (For Email)
        with open(txt_path, 'r', encoding='utf-8', errors='replace') as f:
            raw_output = f.read()

        # 2. PARSE XML (For Summary)
        with open(xml_path, 'r', encoding='utf-8', errors='replace') as f:
            xml_content = f.read()
            
        # Feed the XML into python-nmap
        if xml_content.strip():
            nm.analyse_nmap_xml_scan(xml_content)
            
            # Extract data just like before
            for host in nm.all_hosts():
                host_data = {
                    "state": nm[host].state(),
                    "mac": nm[host]['addresses'].get('mac'),
                    "vendor": nm[host].get('vendor', {}), # vendor is a dict in some versions
                    "protocols": {},
                    "osmatch": nm[host].get("osmatch", []),
                    "osclass": nm[host].get("osclass", []),
                    "fingerprint": nm[host].get("osfingerprint"),
                    "host_scripts": nm[host].get("hostscript", [])
                }
                
                # Fix for vendor dict extraction if needed
                if isinstance(host_data['vendor'], dict):
                    # Try to flatten valid vendor strings or leave empty
                    # nm[host]['vendor'] is usually {mac: 'VendorName'}
                    vals = list(host_data['vendor'].values())
                    host_data['vendor'] = vals[0] if vals else ""

                for proto in nm[host].all_protocols():
                    port_info = {}
                    for port in nm[host][proto]:
                        entry = nm[host][proto][port]
                        port_info[port] = {
                            "state": entry.get("state"),
                            "service": entry.get("name"),
                            "product": entry.get("product"),
                            "version": entry.get("version")
                        }
                    host_data["protocols"][proto] = port_info
                    
                    # Capture NSE scripts run against ports
                    if 'script' in entry:
                         host_data.setdefault("port_scripts", {}).setdefault(port, {}).update(entry['script'])

                results[host] = host_data
        else:
            # If XML is empty, Nmap failed violently or found nothing
            raw_output += "\n\n[ERROR] Nmap produced no XML output."

    except subprocess.CalledProcessError as e:
        # Nmap crashed or returned non-zero exit code
        raw_output = e.output.decode('utf-8', errors='replace')
        results = {}
    
    finally:
        # CLEANUP: Delete the temp files
        if os.path.exists(xml_path):
            os.remove(xml_path)
        if os.path.exists(txt_path):
            os.remove(txt_path)

    return results, raw_output