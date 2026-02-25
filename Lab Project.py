import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

CAMPS_FILE = "camps.json"
VICTIMS_FILE = "victims.json"

# ---------------- SAFE LOAD ---------------- #
def load_data(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            data = json.load(f)

            if isinstance(data, list):
                new_data = {}
                for item in data:
                    if "camp_id" in item:
                        new_data[item["camp_id"]] = item
                    elif "victim_id" in item:
                        new_data[item["victim_id"]] = item
                data = new_data

            # Fix camp keys
            if file == CAMPS_FILE:
                for c in data.values():
                    c.setdefault("capacity", c.pop("max_capacity", 0))
                    c.setdefault("food", c.pop("food_packets", 0))
                    c.setdefault("medical", c.pop("medical_kits", 0))
                    c.setdefault("occupancy", 0)
                    c.setdefault("volunteers", 0)

            # Fix victim keys
            if file == VICTIMS_FILE:
                for v in data.values():
                    if "health_condition" in v:
                        v["health"] = v.pop("health_condition")
                    if "assigned_camp" in v:
                        v["camp"] = v.pop("assigned_camp")
                    v.setdefault("food_received", 0)
                    v.setdefault("medical_received", 0)

            return data
    return {}

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# ---------------- APP ---------------- #
class DisasterReliefApp:

    def __init__(self, root):
        self.root = root
        self.root.title("🌍 Disaster Relief Management System")
        self.root.geometry("900x800")   # width x height
        self.root.resizable(False, False)  # optional: disable resizing
        self.root.configure(bg="#eef2ff")

        self.camps = load_data(CAMPS_FILE)
        self.victims = load_data(VICTIMS_FILE)
        self.recalculate_occupancy()

        self.setup_style()
        self.login_screen()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=28)

    # --------- OCCUPANCY AUTO FIX --------- #
    def recalculate_occupancy(self):
        for camp in self.camps.values():
            camp["occupancy"] = 0

        for victim in self.victims.values():
            camp_id = victim.get("camp")
            if camp_id in self.camps:
                self.camps[camp_id]["occupancy"] += 1

        save_data(CAMPS_FILE, self.camps)

    # ---------------- LOGIN ---------------- #
        # ---------------- LOGIN ---------------- #
    def login_screen(self):
        self.clear()

        # FULL BACKGROUND
        bg_frame = tk.Frame(self.root, bg="#6366f1")
        bg_frame.pack(fill="both", expand=True)

        # CENTER CONTAINER
        container = tk.Frame(bg_frame, bg="#6366f1")
        container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(container,
                 text="DISASTER RELIEF SYSTEM",
                 font=("Segoe UI", 32, "bold"),
                 bg="#6366f1",
                 fg="white").pack(pady=40)

        tk.Button(container,
                  text="Administrator",
                  font=("Segoe UI", 14),
                  bg="#f97316",
                  fg="white",
                  width=20,
                  height=2,
                  relief="flat",
                  command=lambda: self.dashboard("admin")).pack(pady=15)

        tk.Button(container,
                  text="Volunteer",
                  font=("Segoe UI", 14),
                  bg="#10b981",
                  fg="white",
                  width=20,
                  height=2,
                  relief="flat",
                  command=lambda: self.dashboard("volunteer")).pack(pady=15)

    # ---------------- DASHBOARD ---------------- #
    def dashboard(self, role):
        self.role = role
        self.clear()

        header = tk.Frame(self.root, bg="#6366f1", height=70)
        header.pack(fill="x")

        tk.Label(header, text=f"{role.upper()} DASHBOARD",
                 font=("Segoe UI", 16, "bold"),
                 bg="#6366f1", fg="white").pack(side="left", padx=20)

        tk.Button(header, text="Logout",
                  bg="#ef4444", fg="white",
                  command=self.login_screen).pack(side="right", padx=20)

        sidebar = tk.Frame(self.root, bg="#0ea5e9", width=250)
        sidebar.pack(fill="y", side="left")

        self.content = tk.Frame(self.root, bg="white")
        self.content.pack(fill="both", expand=True)

        def menu(text, cmd, color):
            tk.Button(sidebar, text=text,
                      bg=color, fg="white",
                      width=22, height=2,
                      relief="flat",
                      command=cmd).pack(pady=6)

        if role == "admin":
            menu("🏕 Add Camp", self.add_camp_ui, "#f97316")
            menu("➕ Add Resources", self.add_resources_ui, "#14b8a6")

        menu("🧑 Register Victim", self.register_victim_ui, "#ec4899")
        menu("🎁 Distribute Resources", self.distribute_ui, "#22c55e")
        menu("📊 View Camps", self.view_camps_ui, "#6366f1")
        menu("👥 View Victims", self.view_victims_ui, "#10b981")
        menu("🔍 Search Victim", self.search_victim_ui, "#f59e0b")

        if role == "admin":
            menu("📈 Generate Report", self.report_ui, "#ef4444")

    # ---------------- CLEAR ---------------- #
    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    # ---------------- ADD CAMP ---------------- #
    def add_camp_ui(self):
        self.clear_content()

        fields = ["Camp ID", "Location", "Capacity",
                  "Food", "Medical", "Volunteers"]
        entries = []

        for f in fields:
            tk.Label(self.content, text=f, bg="white").pack(pady=5)
            e = tk.Entry(self.content)
            e.pack()
            entries.append(e)

        def save():
            cid = entries[0].get()
            if cid in self.camps:
                messagebox.showerror("Error", "Camp Exists")
                return

            self.camps[cid] = {
                "location": entries[1].get(),
                "capacity": int(entries[2].get()),
                "occupancy": 0,
                "food": int(entries[3].get()),
                "medical": int(entries[4].get()),
                "volunteers": int(entries[5].get())
            }

            save_data(CAMPS_FILE, self.camps)
            messagebox.showinfo("Success", "Camp Added")

        tk.Button(self.content, text="Save",
                  bg="#22c55e", fg="white",
                  width=15, height=2,
                  command=save).pack(pady=20)

    # ---------------- ADD RESOURCES ---------------- #
    def add_resources_ui(self):
        self.clear_content()

        tk.Label(self.content, text="Camp ID", bg="white").pack()
        cid = tk.Entry(self.content)
        cid.pack()

        tk.Label(self.content, text="Food", bg="white").pack()
        food = tk.Entry(self.content)
        food.pack()

        tk.Label(self.content, text="Medical", bg="white").pack()
        med = tk.Entry(self.content)
        med.pack()

        def save():
            if cid.get() not in self.camps:
                messagebox.showerror("Error", "Camp Not Found")
                return

            self.camps[cid.get()]["food"] += int(food.get())
            self.camps[cid.get()]["medical"] += int(med.get())

            save_data(CAMPS_FILE, self.camps)
            messagebox.showinfo("Success", "Resources Added")

        tk.Button(self.content, text="Add",
                  bg="#14b8a6", fg="white",
                  width=15, height=2,
                  command=save).pack(pady=20)

    # ---------------- REGISTER VICTIM ---------------- #
    def register_victim_ui(self):
        self.clear_content()

        fields = ["Victim ID", "Name", "Age",
                  "Health (normal/critical)", "Camp ID"]
        entries = []

        for f in fields:
            tk.Label(self.content, text=f, bg="white").pack(pady=5)
            e = tk.Entry(self.content)
            e.pack()
            entries.append(e)

        def save():
            vid = entries[0].get()
            camp_id = entries[4].get()

            if camp_id not in self.camps:
                messagebox.showerror("Error", "Camp Not Found")
                return

            camp = self.camps[camp_id]

            if camp["occupancy"] >= camp["capacity"]:
                messagebox.showerror("Full", "Camp Full")
                return

            self.victims[vid] = {
                "name": entries[1].get(),
                "age": int(entries[2].get()),
                "health": entries[3].get().lower(),
                "camp": camp_id,
                "food_received": 0,
                "medical_received": 0
            }

            self.recalculate_occupancy()
            save_data(CAMPS_FILE, self.camps)
            save_data(VICTIMS_FILE, self.victims)

            messagebox.showinfo("Success", "Victim Registered")

        tk.Button(self.content, text="Register",
                  bg="#ec4899", fg="white",
                  width=15, height=2,
                  command=save).pack(pady=20)

    # ---------------- DISTRIBUTE ---------------- #
    def distribute_ui(self):
        self.clear_content()

        tk.Label(self.content, text="Victim ID", bg="white").pack()
        vid = tk.Entry(self.content)
        vid.pack()

        tk.Label(self.content, text="Food", bg="white").pack()
        food = tk.Entry(self.content)
        food.pack()

        tk.Label(self.content, text="Medical", bg="white").pack()
        med = tk.Entry(self.content)
        med.pack()

        def distribute():
            if vid.get() not in self.victims:
                messagebox.showerror("Error", "Victim Not Found")
                return

            victim = self.victims[vid.get()]
            camp = self.camps[victim["camp"]]

            f = int(food.get())
            m = int(med.get())

            if victim["health"] == "critical":
                m = max(m, 1)

            if camp["food"] < f or camp["medical"] < m:
                messagebox.showerror("Error", "Insufficient Resources")
                return

            victim["food_received"] += f
            victim["medical_received"] += m
            camp["food"] -= f
            camp["medical"] -= m

            save_data(CAMPS_FILE, self.camps)
            save_data(VICTIMS_FILE, self.victims)

            messagebox.showinfo("Success", "Resources Distributed")

        tk.Button(self.content, text="Distribute",
                  bg="#22c55e", fg="white",
                  width=15, height=2,
                  command=distribute).pack(pady=20)

    # ---------------- SEARCH ---------------- #
    def search_victim_ui(self):
        self.clear_content()

        tk.Label(self.content, text="Enter Victim ID", bg="white").pack(pady=10)
        entry = tk.Entry(self.content)
        entry.pack()

        def search():
            vid = entry.get()
            if vid in self.victims:
                v = self.victims[vid]
                messagebox.showinfo("Found",
                                    f"Name: {v['name']}\n"
                                    f"Age: {v['age']}\n"
                                    f"Health: {v['health']}\n"
                                    f"Camp: {v['camp']}")
            else:
                messagebox.showerror("Not Found", "Victim Not Found")

        tk.Button(self.content, text="Search",
                  bg="#f59e0b", fg="white",
                  width=15, height=2,
                  command=search).pack(pady=20)

    # ---------------- VIEW CAMPS ---------------- #
    def view_camps_ui(self):
        self.clear_content()

        columns = ("ID", "Location", "Occupancy",
                   "Food", "Medical", "Volunteers")

        tree = ttk.Treeview(self.content, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        for cid, c in self.camps.items():
            tree.insert("", "end",
                        values=(cid,
                                c["location"],
                                f"{c['occupancy']}/{c['capacity']}",
                                c["food"],
                                c["medical"],
                                c["volunteers"]))

        tree.pack(fill="both", expand=True)

    # ---------------- VIEW VICTIMS ---------------- #
    def view_victims_ui(self):
        self.clear_content()

        columns = ("ID", "Name", "Age",
                   "Health", "Camp",
                   "Food", "Medical")

        tree = ttk.Treeview(self.content, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        for vid, v in self.victims.items():
            tree.insert("", "end",
                        values=(vid,
                                v["name"],
                                v["age"],
                                v["health"],
                                v["camp"],
                                v["food_received"],
                                v["medical_received"]))

        tree.pack(fill="both", expand=True)

    # ---------------- REPORT ---------------- #
    def report_ui(self):
        self.clear_content()

        total_camps = len(self.camps)
        total_victims = len(self.victims)

        highest = max(self.camps.items(),
                      key=lambda x: x[1]["occupancy"],
                      default=("N/A", {}))[0]

        total_food = sum(v["food_received"] for v in self.victims.values())
        total_med = sum(v["medical_received"] for v in self.victims.values())
        critical = sum(1 for v in self.victims.values()
                       if v["health"] == "critical")

        report = f"""
Total Camps: {total_camps}
Total Victims: {total_victims}
Camp with Highest Occupancy: {highest}
Total Food Distributed: {total_food}
Total Medical Distributed: {total_med}
Critical Victims: {critical}
"""

        tk.Label(self.content, text=report,
                 bg="white",
                 font=("Segoe UI", 13)).pack(pady=40)


root = tk.Tk()
app = DisasterReliefApp(root)
root.mainloop()