import os
import re

SUMMARY_DIR = "/summary"
DATA_DIR = "/data"

def run_cleanup():
    print("==========================================")
    print("STARTING SMART CLEANUP")
    print("==========================================")

    if not os.path.exists(SUMMARY_DIR) or not os.path.exists(DATA_DIR):
        print("[ERROR] Summary or Data directory missing.")
        return

    summary_files = [f for f in os.listdir(SUMMARY_DIR) if f.startswith("summary_") and f.endswith(".txt")]

    if not summary_files:
        print("[INFO] No summary files found. Nothing to clean.")
        return

    # Dictionary: Key = "preset_target", Value = (timestamp, filename)
    latest_scans = {}

    # --- FIX 1: UPDATED REGEX ---
    # Now accepts an optional 'Z' at the end of the timestamp
    # Matches: summary_fast_192-168-1-1_20251214T120000Z.txt
    pattern = re.compile(r"summary_(.+)_\d{8}[T]?\d+Z?\.txt")

    for f in summary_files:
        match = pattern.match(f)
        if match:
            scan_id = match.group(1) # e.g. "fast_192-168-0-0-24"
            
            # Extract timestamp: Split by '_' and remove .txt (and optional Z)
            timestamp = f.split("_")[-1].replace(".txt", "")
            
            if scan_id not in latest_scans:
                latest_scans[scan_id] = (timestamp, f)
            else:
                current_best_ts = latest_scans[scan_id][0]
                if timestamp > current_best_ts:
                    latest_scans[scan_id] = (timestamp, f)
        else:
            print(f"[WARN] File skipped (Regex mismatch): {f}")

    # --- FIX 2: SAFETY LOCK ---
    # If regex failed and we found NO keepers, STOP immediately.
    if not latest_scans:
        print("[CRITICAL WARNING] No valid 'Keeper' files identified!")
        print("Skipping deletion to prevent data loss. Check your regex pattern.")
        return

    keeper_timestamps = set()
    keeper_summaries = set()

    print("[INFO] KEEPING the following latest scans:")
    for scan_id, data in latest_scans.items():
        ts, filename = data
        print(f"   * {scan_id} -> {filename}")
        keeper_timestamps.add(ts)
        keeper_summaries.add(filename)

    # 3. CLEAN UP SUMMARIES
    print("\n[INFO] Cleaning /summary folder...")
    for f in summary_files:
        if f not in keeper_summaries:
            try:
                os.remove(os.path.join(SUMMARY_DIR, f))
                print(f"   [DEL] Old summary: {f}")
            except OSError as e:
                print(f"   [ERR] Cannot delete {f}: {e}")

    # 4. CLEAN UP DATA FILES
    print("\n[INFO] Cleaning /data folder (Matching timestamps)...")
    data_files = [f for f in os.listdir(DATA_DIR) if f.startswith("scan_") and f.endswith(".txt")]
    
    for f in data_files:
        # scan_20251214T120000Z.txt -> 20251214T120000Z
        ts = f.replace("scan_", "").replace(".txt", "")
        
        # We check if this timestamp matches any of the summary timestamps we kept
        if ts not in keeper_timestamps:
            try:
                os.remove(os.path.join(DATA_DIR, f))
                print(f"   [DEL] Orphan/Old data: {f}")
            except OSError as e:
                print(f"   [ERR] Cannot delete {f}: {e}")
        else:
            print(f"   [KEEP] Matched data: {f}")

    print("==========================================")
    print("CLEANUP COMPLETED")
    print("==========================================")