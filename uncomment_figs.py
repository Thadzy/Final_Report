import re
from pathlib import Path

tex_file = Path("/Users/thadzy/Documents/01_Projects/Final_Report/sections/05_results_verification.tex")
content = tex_file.read_text()

figures = [
    "fig_encoder_noise",
    "fig_homing_repeat",
    "fig_step_response_hw",
    "fig_accuracy_errorbar",
    "fig_repeatability_runchart",
    "fig_cycle_timeline"
]

count = 0
for fig in figures:
    # We will search for `% \begin{figure}[H]` and `% \end{figure}` that contains the `fig` string inside.
    # The new pattern looks for `% \begin{figure}... \includegraphics...{fig} ... \end{figure}`
    
    pattern = re.compile(
        r'(% \\begin\{figure\}\[H\]\n(?:% .*\n)*?% .*\\includegraphics\[.*?\]\{' + fig + r'\}.*?\n(?:% .*\n)*?% \\end\{figure\})',
        re.MULTILINE
    )
    
    def repl(m):
        global count
        count += 1
        block = m.group(1)
        # Uncomment by removing '% ' or '%' at the start of each line
        return re.sub(r'^%\s?', '', block, flags=re.MULTILINE)

    content = pattern.sub(repl, content)

tex_file.write_text(content)
print(f"Uncommented {count}/{len(figures)} figure blocks in 05_results_verification.tex")
