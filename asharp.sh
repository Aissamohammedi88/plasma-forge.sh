#!/bin/bash
# A# Launcher via Wine — Aissa Mohammedi (DGK)
cd "/home/nexus/.wine/drive_c/mgnat" || exit 1
wine asharp.exe "$@"
