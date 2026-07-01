<div align="center">

# 💣 UnzipVirus Pro

**Advanced Decompression Bomb Generator — For Authorized Penetration Testing**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Kali%20|%20Linux%20|%20macOS-lightgrey)

⚠️ **AUTHORIZED USE ONLY** — This tool is designed for security professionals conducting
legitimate penetration tests with explicit written permission.

</div>

---

## 🎯 Overview

**UnzipVirus Pro** generates highly compressed archive bombs that expand to massive sizes
on target extraction. It tests:

- **Antivirus / EDR** archive scanning resilience
- **File upload handlers** for decompression DoS (CWE-409)
- **Zip parser implementations** for CVE-2024-0450 quoted-overlap
- **Resource exhaustion** under controlled test conditions

---

## ⚡ Features

| Feature | Description |
|---------|-------------|
| 🔄 **Recursive Zip Bomb** | Classic nested 16x-per-layer bomb (Silicon Valley / Gilfoyle style) |
| 🔗 **Quoted-Overlap Bomb** | CVE-2024-0450 — overlapping entries with extreme compression ratio |
| 🎨 **Colour Animation** | Live progress bars, animated spinners, colour-coded output |
| 📊 **Compression Metrics** | Real-time compressed / uncompressed / ratio display |
| 🧹 **Self-Cleaning** | Removes temp files automatically after generation |
| 📝 **JSON Report** | Auto-generates a structured report for test documentation |

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/unzipvirus-pro.git
cd unzipvirus-pro
chmod +x unzipvirus_pro.py
pip install -r requirements.txt  # No external deps required — pure stdlib
