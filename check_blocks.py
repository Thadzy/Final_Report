import re
import os
import sys

for root, _, files in os.walk("/Users/thadzy/Documents/01_Projects/Final_Report/sections"):
    for file in files:
        if file.endswith(".tex"):
            with open(os.path.join(root, file), 'r') as f:
                content = f.read()
                
                # Check figures
                figures = re.finditer(r'\\begin{figure}(.*?)\\end{figure}', content, re.DOTALL)
                for i, fig in enumerate(figures):
                    if r'\label{' not in fig.group(1):
                        print(f"Missing label in {file} Figure {i+1}")
                        
                # Check tables
                tables = re.finditer(r'\\begin{table}(.*?)\\end{table}', content, re.DOTALL)
                for i, tab in enumerate(tables):
                    if r'\label{' not in tab.group(1):
                        print(f"Missing label in {file} Table {i+1}")

print("Check finished.")
