import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
from datetime import datetime
import os

CSV_FILE = os.path.join(os.path.dirname(__file__), "expenses.csv")
CATEGORIES = ["Food", "Transport", "Groceries", "Entertainment", "Bills", "Health", "Other"]

def ensure_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=["date", "amount", "category", "note"])
        df.to_csv(CSV_FILE, index=False)

class ExpenseTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker")
        self.geometry("800x550")
        ensure_csv()
        self.create_widgets()
        self.load_expenses()

    def create_widgets(self):
        frm_entry = ttk.Frame(self, padding=10)
        frm_entry.pack(fill="x")

        ttk.Label(frm_entry, text="Amount (₹):").grid(column=0, row=0, sticky="w")
        self.amount_var = tk.StringVar()
        ttk.Entry(frm_entry, textvariable=self.amount_var, width=15).grid(column=1, row=0, padx=5)

        ttk.Label(frm_entry, text="Category:").grid(column=2, row=0, sticky="w")
        self.cat_var = tk.StringVar(value=CATEGORIES[0])
        ttk.Combobox(frm_entry, values=CATEGORIES, textvariable=self.cat_var, state="readonly", width=18).grid(column=3, row=0, padx=5)

        ttk.Label(frm_entry, text="Note:").grid(column=0, row=1, sticky="w", pady=6)
        self.note_var = tk.StringVar()
        ttk.Entry(frm_entry, textvariable=self.note_var, width=60).grid(column=1, row=1, columnspan=3, padx=5, sticky="w")

        ttk.Button(frm_entry, text="Add Expense", command=self.add_expense).grid(column=3, row=2, sticky="e", pady=8)

    
        cols = ("date", "amount", "category", "note")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=12)
        for c in cols:
            self.tree.heading(c, text=c.capitalize())
            if c == "note":
                self.tree.column(c, width=300)
            else:
                self.tree.column(c, width=100)
        self.tree.pack(fill="both", padx=10, pady=5, expand=True)

        frm_bottom = ttk.Frame(self, padding=10)
        frm_bottom.pack(fill="x")
        ttk.Button(frm_bottom, text="Refresh", command=self.load_expenses).grid(column=0, row=0)
        ttk.Button(frm_bottom, text="Delete Selected", command=self.delete_selected).grid(column=1, row=0, padx=6)
        ttk.Button(frm_bottom, text="Export CSV...", command=self.export_csv).grid(column=2, row=0, padx=6)

        self.summary_text = tk.Text(frm_bottom, height=6, width=80, state="disabled")
        self.summary_text.grid(column=0, row=1, columnspan=4, pady=8)

    def add_expense(self):
        amt = self.amount_var.get().strip()
        cat = self.cat_var.get().strip()
        note = self.note_var.get().strip()
        if not amt:
            messagebox.showwarning("Input error", "Please enter an amount.")
            return
        try:
            amt_f = float(amt)
        except ValueError:
            messagebox.showwarning("Input error", "Amount must be a number.")
            return

        date = datetime.now().strftime("%Y-%m-%d")
        df = pd.read_csv(CSV_FILE)
        new_row = pd.DataFrame([{"date": date, "amount": amt_f, "category": cat, "note": note}])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)

        self.amount_var.set("")
        self.note_var.set("")
        self.load_expenses()

    def load_expenses(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        try:
            df = pd.read_csv(CSV_FILE, parse_dates=["date"])
        except Exception:
            df = pd.DataFrame(columns=["date", "amount", "category", "note"])

        for _, row in df.iterrows():
            self.tree.insert("", "end", values=(
                pd.to_datetime(row["date"]).strftime("%Y-%m-%d") if not pd.isna(row["date"]) else "",
                f"{row['amount']:.2f}" if pd.notna(row["amount"]) else "",
                row.get("category", ""),
                row.get("note", "")
            ))

        self.update_summary(df)

    def update_summary(self, df):
        text = []
        if df.empty:
            text = ["No expenses recorded yet."]
        else:
            total = df["amount"].sum()
            text.append(f"Total spent: ₹{total:.2f}")

            by_cat = df.groupby("category", dropna=True)["amount"].sum().sort_values(ascending=False)
            text.append("\nSpent by category:")
            for cat, val in by_cat.items():
                text.append(f"  {cat}: ₹{val:.2f}")

            df_dates = df.copy()
            df_dates["date_only"] = pd.to_datetime(df_dates["date"]).dt.date
            daily = df_dates.groupby("date_only")["amount"].sum()
            daily_avg = daily.mean() if not daily.empty else 0.0
            text.append(f"\nDaily average (over {len(daily)} days): ₹{daily_avg:.2f}")

            df_dates["month"] = pd.to_datetime(df_dates["date"]).dt.to_period("M")
            monthly = df_dates.groupby("month")["amount"].sum()
            monthly_avg = monthly.mean() if not monthly.empty else 0.0
            text.append(f"Monthly average (over {len(monthly)} months): ₹{monthly_avg:.2f}")

            top5 = df.nlargest(5, "amount")[["date", "amount", "category", "note"]]
            text.append("\nTop 5 expenses:")
            for _, r in top5.iterrows():
                d = pd.to_datetime(r["date"]).strftime("%Y-%m-%d")
                text.append(f"  {d} — ₹{r['amount']:.2f} — {r['category']} — {r.get('note','')}")

        self.summary_text.config(state="normal")
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("end", "\n".join(text))
        self.summary_text.config(state="disabled")

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Delete", "No row selected.")
            return

        confirm = messagebox.askyesno("Confirm", "Delete selected expense(s)? This cannot be undone.")
        if not confirm:
            return

        try:
            df = pd.read_csv(CSV_FILE)
            for s in sel:
                vals = self.tree.item(s, "values")
                date, amount, category, note = vals
                amount_f = float(amount)
                df = df[~(
                    (df["date"].astype(str) == date) &
                    (np.isclose(df["amount"].astype(float), amount_f)) &
                    (df["category"].astype(str) == category) &
                    (df["note"].astype(str) == note)
                )]
            df.to_csv(CSV_FILE, index=False)
            self.load_expenses()
            messagebox.showinfo("Deleted", "Selected expense(s) deleted successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        df = pd.read_csv(CSV_FILE)
        df.to_csv(path, index=False)
        messagebox.showinfo("Export", f"Exported to {path}")

if __name__ == "__main__":
    app = ExpenseTrackerApp()
    app.mainloop()
