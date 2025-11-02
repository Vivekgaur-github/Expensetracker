import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import mysql.connector
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- EDIT THESE DATABASE CREDENTIALS ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '#Vivek254',      # <- put your MySQL password here
    'database': 'expensetracker'
}
# ---------------------------------------

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

class ExpenseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Manager - Tkinter")
        self.geometry("1000x650")
        self.configure(bg='#f5f7fb')
        self.create_ui()
        self.load_expenses()

    def create_ui(self):
        top = tk.Frame(self, bg='#2b7cff', height=60)
        top.pack(fill='x', side='top')
        tk.Label(top, text="Expense Manager", bg='#2b7cff', fg='white', font=('Helvetica',16,'bold')).pack(padx=20, pady=12, anchor='w')

        main = tk.Frame(self, bg='#f5f7fb')
        main.pack(fill='both', expand=True, padx=12, pady=12)

        left = tk.Frame(main, bg='#f5f7fb', width=320)
        left.pack(fill='y', side='left', padx=(0,12))

        right = tk.Frame(main, bg='#f5f7fb')
        right.pack(fill='both', expand=True, side='left')

        card = tk.Frame(left, bg='white', bd=1, relief='flat')
        card.pack(fill='x', pady=(0,10))
        tk.Label(card, text="Add Expense", bg='white', font=('Helvetica',12,'bold')).pack(padx=12, pady=(12,6), anchor='w')

        form = tk.Frame(card, bg='white')
        form.pack(padx=12, pady=6, fill='x')
        tk.Label(form, text="Category", bg='white').grid(row=0,column=0,sticky='w')
        self.cat_entry = ttk.Entry(form)
        self.cat_entry.grid(row=0,column=1,sticky='ew', padx=6, pady=4)
        tk.Label(form, text="Amount", bg='white').grid(row=1,column=0,sticky='w')
        self.amount_entry = ttk.Entry(form)
        self.amount_entry.grid(row=1,column=1,sticky='ew', padx=6, pady=4)
        tk.Label(form, text="Date", bg='white').grid(row=2,column=0,sticky='w')
        self.date_entry = ttk.Entry(form)
        self.date_entry.insert(0, datetime.today().strftime('%Y-%m-%d'))
        self.date_entry.grid(row=2,column=1,sticky='ew', padx=6, pady=4)
        tk.Label(form, text="Description", bg='white').grid(row=3,column=0,sticky='w')
        self.desc_entry = ttk.Entry(form)
        self.desc_entry.grid(row=3,column=1,sticky='ew', padx=6, pady=4)
        form.columnconfigure(1, weight=1)

        add_btn = ttk.Button(card, text="Add Expense", command=self.add_expense)
        add_btn.pack(padx=12, pady=(6,12), fill='x')

        fcard = tk.Frame(left, bg='white', bd=1)
        fcard.pack(fill='x')
        tk.Label(fcard, text="Filters", bg='white', font=('Helvetica',10,'bold')).pack(padx=12, pady=(8,6), anchor='w')
        ffrm = tk.Frame(fcard, bg='white')
        ffrm.pack(padx=12, pady=6, fill='x')
        tk.Label(ffrm, text="From", bg='white').grid(row=0,column=0,sticky='w')
        self.from_entry = ttk.Entry(ffrm); self.from_entry.grid(row=0,column=1,padx=6)
        tk.Label(ffrm, text="To", bg='white').grid(row=1,column=0,sticky='w')
        self.to_entry = ttk.Entry(ffrm); self.to_entry.grid(row=1,column=1,padx=6)
        tk.Label(ffrm, text="Category", bg='white').grid(row=2,column=0,sticky='w')
        self.filter_cat = ttk.Entry(ffrm); self.filter_cat.grid(row=2,column=1,padx=6)
        ttk.Button(fcard, text="Apply Filters", command=self.load_expenses).pack(padx=12, pady=(6,8), fill='x')
        ttk.Button(fcard, text="Clear Filters", command=self.clear_filters).pack(padx=12, pady=(0,12), fill='x')

        charts_frame = tk.Frame(right, bg='#f5f7fb')
        charts_frame.pack(fill='x', pady=(0,8))

        self.fig = Figure(figsize=(6,2.5), dpi=100)
        self.ax1 = self.fig.add_subplot(121)
        self.ax2 = self.fig.add_subplot(122)
        self.canvas = FigureCanvasTkAgg(self.fig, master=charts_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='x', padx=6, pady=6)

        table_card = tk.Frame(right, bg='white', bd=1)
        table_card.pack(fill='both', expand=True)
        cols = ('date','category','amount','description','id')
        self.tree = ttk.Treeview(table_card, columns=cols, show='headings')
        self.tree.heading('date', text='Date'); self.tree.heading('category', text='Category')
        self.tree.heading('amount', text='Amount'); self.tree.heading('description', text='Description')
        self.tree.column('id', width=0, stretch=False)
        self.tree.pack(fill='both', expand=True, padx=6, pady=6)
        self.tree.bind('<Button-3>', self.show_row_menu)
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label='Delete', command=self.delete_selected)

    def show_row_menu(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            self.menu.post(event.x_root, event.y_root)

    def clear_filters(self):
        self.from_entry.delete(0,'end'); self.to_entry.delete(0,'end'); self.filter_cat.delete(0,'end')
        self.load_expenses()

    def add_expense(self):
        cat = self.cat_entry.get().strip()
        amount = self.amount_entry.get().strip()
        date = self.date_entry.get().strip()
        desc = self.desc_entry.get().strip()
        if not cat or not amount or not date:
            messagebox.showwarning("Validation", "Category, Amount and Date are required.")
            return
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO expenses (user_id, category, amount, exp_date, description) VALUES (%s,%s,%s,%s,%s)",
                        (1, cat, float(amount), date, desc))
            conn.commit()
            cur.close(); conn.close()
            self.cat_entry.delete(0,'end'); self.amount_entry.delete(0,'end'); self.desc_entry.delete(0,'end')
            messagebox.showinfo("Success", "Expense added!")
            self.load_expenses()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0])
        eid = item['values'][4]
        if messagebox.askyesno("Confirm", "Delete selected expense?"):
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("DELETE FROM expenses WHERE expense_id = %s", (eid,))
                conn.commit()
                cur.close(); conn.close()
                self.load_expenses()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def load_expenses(self):
        from_date = self.from_entry.get().strip()
        to_date = self.to_entry.get().strip()
        cat = self.filter_cat.get().strip()
        sql = "SELECT expense_id, category, amount, DATE_FORMAT(exp_date, '%Y-%m-%d') as exp_date, description FROM expenses"
        clauses = []
        params = []
        if from_date: clauses.append("exp_date >= %s"); params.append(from_date)
        if to_date: clauses.append("exp_date <= %s"); params.append(to_date)
        if cat: clauses.append("category LIKE %s"); params.append('%'+cat+'%')
        if clauses: sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY exp_date DESC"
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(sql, tuple(params))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
            rows = []

        for r in self.tree.get_children(): self.tree.delete(r)
        monthly = {}
        catmap = {}
        for r in rows:
            eid, category, amount, exp_date, desc = r
            self.tree.insert('', 'end', values=(exp_date, category, f"{amount:.2f}", desc, eid))
            month = exp_date[:7]
            monthly[month] = monthly.get(month, 0) + float(amount)
            catmap[category] = catmap.get(category, 0) + float(amount)

        self.ax1.clear(); self.ax2.clear()
        months = sorted(monthly.keys())
        vals = [monthly[m] for m in months]
        if months:
            self.ax1.bar(months, vals, color='#2b7cff')
            self.ax1.set_title('Monthly Total'); self.ax1.tick_params(axis='x', rotation=45)
        cats = list(catmap.keys()); cvals = [catmap[c] for c in cats]
        if cats:
            self.ax2.pie(cvals, labels=cats, autopct='%1.1f%%')
            self.ax2.set_title('Category Breakdown')
        self.canvas.draw()

if __name__ == '__main__':
    try:
        import mysql.connector
    except Exception as e:
        print("Missing mysql-connector-python. Install with: pip install mysql-connector-python")
    app = ExpenseApp()
    app.mainloop()
