# 💰 Personal Budget Tracker

A simple web app to track your daily expenses, see where your money goes, and stick to a monthly budget. Built with Python + Streamlit + SQLite.

---

## What you'll see

- A big number at the top showing how much you've spent this month
- A coloured progress bar showing how much of your budget is left (green → yellow → red)
- A pie chart of spending by category
- A bar chart of daily spending
- A table of every expense you've ever added
- A sidebar to filter by category and date, and to change your monthly budget

The first time you open the app it comes pre-loaded with **sample data** so the charts aren't empty. You can delete those entries any time.

---

## Step-by-step setup (for first-time coders)

You only need to do steps 1–3 once. After that, just run the command in step 4 whenever you want to use the app.

### 1. Install Python

If you don't already have Python, download it here: https://www.python.org/downloads/

Pick **Python 3.10 or newer**. During the installer, tick the box that says *"Add Python to PATH"* (Windows) or just follow the prompts (Mac).

To check it worked, open the Terminal app (Mac) or Command Prompt (Windows) and type:

```
python3 --version
```

You should see something like `Python 3.12.0`. If you do, you're good.

### 2. Open a terminal in this folder

On a Mac:
- Open the **Terminal** app
- Type `cd ` (with a space after `cd`)
- Drag the `budget_tracker` folder from Finder into the Terminal window — it pastes the path
- Press **Enter**

You should now be "inside" the folder. The terminal prompt usually shows the folder name.

### 3. Install the libraries the app needs

In the same terminal window, paste this and press Enter:

```
pip3 install -r requirements.txt
```

This downloads three free Python packages:
- **streamlit** — turns Python into a web app
- **pandas** — handles the expense table
- **plotly** — draws the pie and bar charts

It takes about a minute. You'll see lots of text scroll by — that's normal.

### 4. Run the app

Still in the terminal, run:

```
streamlit run app.py
```

Your web browser will pop open automatically at `http://localhost:8501` showing the budget tracker. If it doesn't open by itself, copy that link into your browser.

To **stop** the app, click back in the terminal and press `Ctrl + C`.

To **start it again** later, just open the terminal in this folder (step 2) and run `streamlit run app.py` again.

---

## How to use it

| Want to… | Do this |
|---|---|
| Add an expense | Type a name, pick a category, type the dollar amount, click **Add Expense** |
| Change your monthly budget | Use the **Monthly budget** box in the left sidebar |
| Filter the table and pie chart | Use the **Category** dropdown and **Date range** in the sidebar |
| Delete an expense | Open the **🗑️ Remove an expense** section under the table |

Your data is saved in a file called `budget.db` inside this folder. Don't delete it unless you want to wipe everything and start over.

---

## File overview

```
budget_tracker/
├── app.py             ← the web app (charts, forms, layout)
├── database.py        ← all the SQLite read/write functions
├── requirements.txt   ← list of libraries to install
├── README.md          ← this file
└── budget.db          ← your saved expenses (created on first run)
```

---

## Troubleshooting

**`command not found: pip3`** — try `pip` instead, or `python3 -m pip install -r requirements.txt`.

**`command not found: streamlit`** — try `python3 -m streamlit run app.py`.

**Charts look empty** — change the **Date range** in the sidebar; it might be filtered to a window with no expenses.

**Want a fresh start?** — close the app, delete `budget.db`, then run `streamlit run app.py` again. The sample data will be re-seeded.
