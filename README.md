A GUI-based Python debugging tool that analyzes, detects, and fixes common errors in Python code automatically. Built with tkinter, pylint, and ast for smart corrections.

✨ Features
✅ Syntax Error Detection – Catches mistakes before runtime.
✅ Auto-Fix Undefined Variables – Uses Levenshtein distance for smart suggestions.
✅ Pylint Integration – Provides detailed code quality reports.
✅ Code Formatting – Applies autopep8 for PEP 8 compliance.
✅ Side-by-Side Comparison – Highlights changes between original and fixed code.
✅ Export Fixed Code – Save corrected scripts with one click.

🚀 Installation
Clone the repository:

bash
git clone https://github.com/Dominion002/CodeAlpha_Bug_Bounty.git
cd CodeAlpha_Bug_Bounty
Install dependencies:

bash
pip install autopep8 pylint python-Levenshtein
🖥️ Usage
Run the debugger:

bash
python debugger_app.py
Steps:

Click "Upload Python File" to analyze your script.

View errors & auto-fixes in the GUI.

Download the corrected code when satisfied.

🛠️ How It Works
Parses code using ast for syntax checks.

Detects undefined variables and suggests corrections.

Runs Pylint for code quality analysis.

Formats code with autopep8.

📂 Project Structure
Debugger/
├── debugger_app.py      # Main application
├── README.md           # Documentation
└── requirements.txt    # Dependencies
🤝 Contributing
Pull requests welcome! For major changes, open an issue first.

