#!/bin/sh
# #172: una corrida por propuesta sobre sub-6, contra s6-base-t4 (llama-server original, -t 4, primera consulta de hoy).
set -e
M="python3 -I medir.py"
L=/data/local/tmp/a56-lab
$M s6-numero  --lista sub-6 --consulta numero --prefijo salto -- -t 4      # propuesta 2
$M s6-t6      --lista sub-6 -- -t 6                                        # propuesta 3
$M s6-t8      --lista sub-6 -- -t 8                                        # propuesta 3
$M s6-i8mm    --lista sub-6 --binarios $L/llama-i8mm -- -t 4               # propuesta 5: build con dotprod+i8mm
$M s6-vk      --lista sub-6 --binarios $L/llama-vk -- -t 4 -ngl 99         # propuesta 3: Vulkan (CPU con dotprod+i8mm)
$M s6-ub128   --lista sub-6 -- -t 4 -ub 128                                # propuesta 5
$M s6-kv-q8   --lista sub-6 -- -t 4 -fa on -ctk q8_0 -ctv q8_0             # propuesta 5 (la caché q8 en V pide -fa)
$M s6-rendimiento --lista sub-6 --antes "cmd power set-fixed-performance-mode-enabled true" -- -t 4   # propuesta 5
adb shell cmd power set-fixed-performance-mode-enabled false
