
# Expense Tracker (Tkinter + pandas + numpy)

Simple GUI expense tracker that stores data in `expenses.csv`. Designed to run on VS Code / local Python.

## Features
- Add expense with amount, category, note (date recorded automatically)
- View all expenses in a table
- Delete selected expense(s)
- Export CSV
- Summary: total spent, spent by category, daily & monthly averages, top 5 expenses

## Requirements
- Python 3.8+
- pandas
- numpy
- (tkinter comes bundled with most Python installs)

## How to run
1. Open the `ExpenseTracker` folder in VS Code.

2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python expense_tracker.py
   ```

## Data file
- `expenses.csv` is created automatically in the same folder when you first run the app.
- You can also open it with Excel or any CSV editor.

## Notes
- Amount is stored as a number; currency sign in the UI is just for display.
- This is intentionally lightweight and CSV-based for portability.
