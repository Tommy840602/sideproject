import subprocess

def parse_upsc_output() -> dict:
    result = subprocess.run([r"C:\NUT-for-Windows-x86_64-SNAPSHOT-2.8.3.3028-master\mingw64\sbin\upsc.exe", "dummy@127.0.0.1"], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    data = {}
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip()] = value.strip()
    return data

def get_light_color(status: str, battery_charge: int) -> str:
    if battery_charge <= 20:
        return "red"
    if "LB" in status or "OVER" in status or "FSD" in status:
        return "red"
    elif "OB" in status or "DISCHRG" in status:
        return "yellow"
    elif "OL" in status or "CHRG" in status:
        return "green"
    else:
        return "green"