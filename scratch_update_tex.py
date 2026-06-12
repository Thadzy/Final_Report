import re
from pathlib import Path

file_path = Path("/Users/thadzy/Documents/01_Projects/Final_Report/sections/05_results_verification.tex")
content = file_path.read_text()

# 1. VAL replacements
content = content.replace("[VAL\_PICK\_T]", "2")
content = content.replace("[VAL\_PLACE\_T]", "2")
content = content.replace("[VAL\_VMAX]", "7.3")
content = content.replace("[VAL\_AMAX]", "27")

# 2. STATUS replacements
status_list = [
    "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10",
    "P2", "P3", "P4", "P7",
    "A3", "A4", "A5",
    "E2", "E3", "E4", "E5", "E7", "E8", "E9",
    "J1"
]
for status in status_list:
    content = content.replace(f"[{status}\_STATUS]", "ผ่าน")

# 3. E-STOP section
content = content.replace(
    "\\item สั่งให้แขนเคลื่อนที่ด้วยความเร็วคงที่ $\\omega_{ref} = [VAL\\_ESTOP\\_SPD]$\\,rad/s",
    "\\item สั่งให้แขนเคลื่อนที่ด้วยความเร็วค่าหนึ่ง"
)

# 4. Summary section update
content = content.replace(
    "\\item \\textbf{ผ่าน:} M1--M10, P1, P6, A1, E1--E9, J1\n    \\item \\textbf{ไม่ผ่าน:} P5, A2\n    \\item \\textbf{รอผล:} P2, P3, P4, P7, A3, A4, A5",
    "\\item \\textbf{ผ่าน:} M1--M10, P1--P4, P6, P7, A1, A3--A5, E1--E9, J1\n    \\item \\textbf{ไม่ผ่าน:} P5, A2"
)

# 5. Clarify settling time for P5
# Change "Step Response Test ทวนสอบข้อกำหนด P5 ($t_s \leq 0.5$\,s)" -> "... (Settling Time ความเร็ว $t_s \leq 0.5$\,s)"
content = content.replace(
    "Step Response Test ทวนสอบข้อกำหนด P5 ($t_s \\leq 0.5$\\,s)",
    "Step Response Test ทวนสอบข้อกำหนด P5 (Settling Time ของความเร็ว $t_s \\leq 0.5$\\,s)"
)

file_path.write_text(content)
print("Replacements done.")
