import tkinter as tk
from tkinter import messagebox
import sqlite3
from plyer import notification
from tkcalendar import Calendar
import datetime

# Initialize main window
root = tk.Tk()
root.title("Daily To-Do App")
root.geometry("400x500")
root.configure(bg="#1e1e2e")  # Dark background for the app

# Font and Colors
FONT_TITLE = ("Helvetica", 14, "bold")
FONT_TEXT = ("Helvetica", 12)
COLOR_BG = "#1e1e2e"
COLOR_TEXT = "#f8f8f2"
COLOR_BTN = "#6272a4"
COLOR_ENTRY = "#44475a"

# Get today's date
today = datetime.date.today()

# Calendar widget (fixed size)
calendar = Calendar(root, selectmode="day", year=today.year, month=today.month, day=today.day)
calendar.pack(pady=10, fill=tk.X)  # Fixed width, doesn't expand horizontally

# Priority Dropdown Menu (fixed size)
priority_label = tk.Label(root, text="Priority:", font=FONT_TITLE, bg=COLOR_BG, fg=COLOR_TEXT)
priority_label.pack(pady=5)

priorities = ["Low", "Medium", "High"]
priority_var = tk.StringVar(value="Medium")  # Default priority
priority_menu = tk.OptionMenu(root, priority_var, *priorities)
priority_menu.config(font=FONT_TEXT, bg=COLOR_BTN, fg=COLOR_TEXT)
priority_menu.pack(pady=5, fill=tk.X)  # Fixed width

# Task Label and Entry (fixed size)
task_label = tk.Label(root, text="Task:", font=FONT_TITLE, bg=COLOR_BG, fg=COLOR_TEXT)
task_label.pack(pady=5)

task_entry = tk.Entry(root, width=40, font=FONT_TEXT, bg=COLOR_ENTRY, fg=COLOR_TEXT, insertbackground=COLOR_TEXT)
task_entry.pack(pady=10, fill=tk.X)  # Fixed width

# Add Task Button (fixed size)
add_task_button = tk.Button(root, text="Add Task", font=FONT_TEXT, bg=COLOR_BTN, fg=COLOR_TEXT)
add_task_button.pack(pady=5, fill=tk.X)  # Fixed width

# Frame for Listbox to make it flexible
frame = tk.Frame(root, bg=COLOR_BG)
frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  # Only this frame is flexible

# Task Listbox with Scrollbar (flexible)
task_listbox = tk.Listbox(frame, font=FONT_TEXT, bg=COLOR_ENTRY, fg=COLOR_TEXT, 
                          selectbackground="#ff79c6", selectforeground=COLOR_BG, bd=0, highlightthickness=0)
task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)  # Expands to fill the frame

scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

task_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=task_listbox.yview)

# Complete and Delete Buttons (fixed size)
complete_task_button = tk.Button(root, text="Mark as Complete", font=FONT_TEXT, bg=COLOR_BTN, fg=COLOR_TEXT)
complete_task_button.pack(pady=5, fill=tk.X)  # Fixed width

delete_task_button = tk.Button(root, text="Delete Task", font=FONT_TEXT, bg=COLOR_BTN, fg=COLOR_TEXT)
delete_task_button.pack(pady=5, fill=tk.X)  # Fixed width

# Set Up Database (Persistent Storage)
def setup_database():
    with sqlite3.connect("tasks.db") as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS tasks
                     (id INTEGER PRIMARY KEY,
                      description TEXT,
                      completed BOOLEAN,
                      priority TEXT,
                      due_date TEXT)''')
        conn.commit()

def add_task():
    task = task_entry.get()
    priority = priority_var.get()
    due_date = calendar.get_date()  # Gets the selected date from the calendar
    if task:
        conn = sqlite3.connect("tasks.db")
        c = conn.cursor()
        c.execute("INSERT INTO tasks (description, completed, priority, due_date) VALUES (?, ?, ?, ?)", 
                  (task, False, priority, due_date))
        conn.commit()
        conn.close()
        task_entry.delete(0, tk.END)
        update_task_list()
    else:
        messagebox.showwarning("Input Error", "Please enter a task description.")

# Function to Update Task List with IDs embedded for easy reference
def update_task_list():
    task_listbox.delete(0, tk.END)
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("SELECT id, description, completed, priority, due_date FROM tasks")
    tasks = c.fetchall()
    for task in tasks:
        task_id, description, completed, priority, due_date = task
        task_desc = f"[{'x' if completed else ' '}] {description} - Priority: {priority}, Due: {due_date}"
        task_listbox.insert(tk.END, f"{task_id}:{task_desc}")
        if priority == "High":
            task_listbox.itemconfig(tk.END, {'bg': '#ffcccb'})  # Light red background for high priority
    conn.close()

# Function to Mark Task as Complete
def mark_task_complete():
    try:
        selected_item = task_listbox.get(task_listbox.curselection()[0])
        task_id = int(selected_item.split(":")[0])  # Extract the task ID
        with sqlite3.connect("tasks.db") as conn:
            c = conn.cursor()
            c.execute("UPDATE tasks SET completed = ? WHERE id = ?", (True, task_id))
            conn.commit()
        update_task_list()
    except IndexError:
        messagebox.showwarning("Selection Error", "Please select a task to mark complete.")
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")

# Function to Delete Task
def delete_task():
    try:
        selected_item = task_listbox.get(task_listbox.curselection()[0])
        task_id = int(selected_item.split(":")[0])  # Extract the task ID
        with sqlite3.connect("tasks.db") as conn:
            c = conn.cursor()
            c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
        update_task_list()
    except IndexError:
        messagebox.showwarning("Selection Error", "Please select a task to delete.")
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")

# Assign button commands
add_task_button.config(command=add_task)
complete_task_button.config(command=mark_task_complete)
delete_task_button.config(command=delete_task)

# Initialize database and load tasks
setup_database()
update_task_list()
root.mainloop()
