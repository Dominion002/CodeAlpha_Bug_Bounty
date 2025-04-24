import ast
import subprocess
import autopep8
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter.filedialog import asksaveasfilename
import re
import Levenshtein  

def run_pylint(filepath):
    result = subprocess.run(["pylint", filepath], capture_output=True, text=True)
    return result.stdout or result.stderr

def parse_pylint_errors(pylint_output):
    error_lines = []
    messages = []
    undefined_vars = {}
    pattern = r"(?P<file>.+?):(?P<line>\d+):\d+: (?P<code>[A-Z]\d+): (?P<msg>.+)"

    for line in pylint_output.splitlines():
        match = re.match(pattern, line)
        if match:
            line_num = int(match.group("line"))
            msg = match.group("msg")
            error_lines.append(line_num)
            messages.append(f"Line {line_num}: {msg}")

            # Catch undefined-variable errors
            if "undefined-variable" in msg:
                bad_var = re.findall(r"'(.*?)'", msg)
                if bad_var:
                    undefined_vars[line_num] = bad_var[0]
    return error_lines, messages, undefined_vars

def get_known_variables(code):
    tree = ast.parse(code)
    defined_vars = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for arg in node.args.args:
                defined_vars.add(arg.arg)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    defined_vars.add(target.id)
    return defined_vars

def auto_fix_undefined_vars(code, undefined_vars, known_vars):
    lines = code.split('\n')
    for line_num, bad_var in undefined_vars.items():
        best_match = None
        best_score = 100
        for var in known_vars:
            score = Levenshtein.distance(bad_var, var)
            if score < best_score:
                best_score = score
                best_match = var
        if best_match and best_score <= 2:
            print(f"🔧 Fixing '{bad_var}' to '{best_match}' on line {line_num}")
            lines[line_num - 1] = lines[line_num - 1].replace(bad_var, best_match)
    return '\n'.join(lines)

def highlight_lines(textbox, lines, tag_name):
    for line in lines:
        index = f"{line}.0"
        textbox.tag_add(tag_name, index, f"{line}.end")

def highlight_diff(original, corrected, textbox):
    original_lines = original.strip().split('\n')
    corrected_lines = corrected.strip().split('\n')

    textbox.delete(1.0, tk.END)
    for idx, line in enumerate(corrected_lines):
        tag = ""
        if idx >= len(original_lines) or line.strip() != original_lines[idx].strip():
            tag = "changed"
        textbox.insert(tk.END, line + '\n', tag)

def upload_file():
    filepath = filedialog.askopenfilename(
        title="Select a Python file",
        filetypes=[("Python Files", "*.py")]
    )

    if filepath:
        try:
            with open(filepath, 'r') as file:
                code = file.read()

                original_code_box.delete(1.0, tk.END)
                original_code_box.insert(tk.END, code)

                # AST syntax check
                syntax_ok = True
                try:
                    ast.parse(code)
                except SyntaxError as e:
                    syntax_ok = False
                    messagebox.showerror("Syntax Error", f"❌ Syntax Error:\n{e}")

                if syntax_ok:
                    # Run pylint
                    pylint_output = run_pylint(filepath)
                    error_lines, error_messages, undefined_vars = parse_pylint_errors(pylint_output)
                    known_vars = get_known_variables(code)

                    # Only show success if truly clean
                    if not error_lines and not undefined_vars:
                        messagebox.showinfo("Syntax Check", "✅ No issues found. Your code looks good!")

                    # Highlight errors in original code
                    highlight_lines(original_code_box, error_lines, "pylint_error")

                    # Show bug summary
                    bug_summary_box.config(state="normal")
                    bug_summary_box.delete(1.0, tk.END)
                    if error_messages:
                        bug_summary_box.insert(tk.END, "\n".join(error_messages))
                    else:
                        bug_summary_box.insert(tk.END, "No logical issues found.")
                    bug_summary_box.config(state="disabled")

                    # Auto-fix undefined variables and format
                    fixed_code = auto_fix_undefined_vars(code, undefined_vars, known_vars)
                    corrected = autopep8.fix_code(fixed_code)
                    highlight_diff(code, corrected, corrected_code_box)
                    corrected_code_box.corrected_code = corrected

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")
    else:
        messagebox.showwarning("No File", "No file was selected.")

def download_corrected_code():
    if hasattr(corrected_code_box, 'corrected_code'):
        save_path = asksaveasfilename(defaultextension=".py", filetypes=[("Python files", "*.py")])
        if save_path:
            with open(save_path, 'w') as file:
                file.write(corrected_code_box.corrected_code)
            messagebox.showinfo("Saved", f"Corrected code saved to:\n{save_path}")
    else:
        messagebox.showwarning("Nothing to Save", "No corrected code available yet.")

def main_gui():
    global original_code_box, corrected_code_box, bug_summary_box

    window = tk.Tk()
    window.title("AI Python Debugger & AutoFixer")
    window.geometry("1100x750")
    window.configure(bg="#f0f0f0")

    top_frame = tk.Frame(window, bg="#f0f0f0")
    top_frame.pack(pady=10)

    upload_btn = tk.Button(top_frame, text="📂 Upload Python File", command=upload_file, width=25, bg="#007ACC", fg="white", font=("Arial", 11))
    upload_btn.pack(side=tk.LEFT, padx=10)

    download_btn = tk.Button(top_frame, text="⬇️ Download Fixed Code", command=download_corrected_code, width=25, bg="#28A745", fg="white", font=("Arial", 11))
    download_btn.pack(side=tk.LEFT, padx=10)

    # Bug Summary
    summary_frame = tk.Frame(window)
    summary_frame.pack(fill=tk.X, padx=20, pady=5)

    summary_label = tk.Label(summary_frame, text="🪲 Bug Summary", font=("Arial", 12, "bold"))
    summary_label.pack(anchor="w")

    bug_summary_box = scrolledtext.ScrolledText(summary_frame, height=5, font=("Courier", 10), state="disabled", bg="#fff7f7")
    bug_summary_box.pack(fill=tk.X)

    # Code Views
    text_frame = tk.Frame(window)
    text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    original_code_box = scrolledtext.ScrolledText(text_frame, height=30, width=60, font=("Courier", 10))
    original_code_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    original_code_box.tag_configure("pylint_error", background="#ffd6d6")

    corrected_code_box = scrolledtext.ScrolledText(text_frame, height=30, width=60, font=("Courier", 10))
    corrected_code_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    corrected_code_box.insert(tk.END, "# Corrected Code")
    corrected_code_box.tag_configure("changed", background="#ffdddd")

    window.mainloop()

if __name__ == "__main__":
    main_gui()
