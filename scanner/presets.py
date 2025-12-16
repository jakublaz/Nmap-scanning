PRESETS = {
    "fast": "-T4 -F",
    "normal": "-sV --version-intensity 5 -T4",
    "deep": "-sS -sV -p- -T4 --min-rate 500 --max-retries 2",
    "vuln": "-sV --script vuln --script-timeout 2m -T3"
}
