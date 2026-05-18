import customtkinter as ctk
from openai import OpenAI
import threading
import os
from orchestrator import Orchestrator
from datetime import datetime

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

class AIManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Manager")
        self.geometry("1400x900")
        
        self.c_sidebar = "#0F172A"
        self.c_main_bg = "#F8FAFC"
        self.c_card_bg = "#FFFFFF"
        self.c_brand = "#0052FF"
        self.c_text_primary = "#0F172A"
        self.c_text_sidebar = "#FFFFFF"
        self.c_border = "#E2E8F0"
        
        self.configure(fg_color=self.c_main_bg)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # --- SIDEBAR ---
        self.sidebar_frame = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=self.c_sidebar)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="AI Manager", font=("Hanken Grotesk", 24, "bold"), text_color=self.c_text_sidebar)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 10), sticky="w")
        self.sub_logo = ctk.CTkLabel(self.sidebar_frame, text="Enterprise Scaffolding", font=("JetBrains Mono", 12), text_color="#7C839B")
        self.sub_logo.grid(row=1, column=0, padx=20, pady=(0, 30), sticky="w")
        
        self.nav_chat_btn = ctk.CTkButton(self.sidebar_frame, text="Chat", corner_radius=8, height=45, fg_color="transparent", hover_color="#1E293B", text_color="#7C839B", font=("Inter", 14), anchor="w", command=lambda: self.select_frame("chat"))
        self.nav_chat_btn.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.nav_editor_btn = ctk.CTkButton(self.sidebar_frame, text="Tasks", corner_radius=8, height=45, fg_color=self.c_brand, text_color="#FFFFFF", font=("Inter", 14), anchor="w", command=lambda: self.select_frame("editor"))
        self.nav_editor_btn.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        self.new_instance_btn = ctk.CTkButton(self.sidebar_frame, text="+ New Instance", corner_radius=8, height=45, fg_color=self.c_brand, hover_color="#0040CC", text_color="#FFFFFF", font=("Inter", 14, "bold"))
        self.new_instance_btn.grid(row=6, column=0, padx=20, pady=30, sticky="ew")

        # --- 1. CHAT FRAME ---
        self.chat_frame = ctk.CTkFrame(self, fg_color=self.c_main_bg, corner_radius=0)
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self.chat_frame.grid_rowconfigure(1, weight=1)
        
        self.top_bar = ctk.CTkFrame(self.chat_frame, fg_color=self.c_card_bg, height=64, corner_radius=0, border_color=self.c_border, border_width=1)
        self.top_bar.grid(row=0, column=0, sticky="ew")
        self.top_bar.grid_propagate(False)
        self.top_bar.grid_columnconfigure(1, weight=1)
        
        self.screen_title = ctk.CTkLabel(self.top_bar, text="AI Chat", font=("Hanken Grotesk", 18, "bold"), text_color=self.c_text_primary)
        self.screen_title.grid(row=0, column=0, padx=40, pady=15)
        
        self.model_badge = ctk.CTkLabel(self.top_bar, text="GPT-4 PRO", fg_color="#E0E7FF", text_color=self.c_brand, corner_radius=4, font=("JetBrains Mono", 11, "bold"))
        self.model_badge.grid(row=0, column=1, sticky="w", padx=10)

        self.chat_scroll = ctk.CTkScrollableFrame(self.chat_frame, fg_color="transparent")
        self.chat_scroll.grid(row=1, column=0, sticky="nsew", padx=40, pady=(20, 0))
        self.chat_scroll.grid_columnconfigure(0, weight=1)

        self.input_container = ctk.CTkFrame(self.chat_frame, fg_color=self.c_card_bg, corner_radius=12, border_color=self.c_border, border_width=1)
        self.input_container.grid(row=2, column=0, padx=40, pady=(20, 10), sticky="ew")
        
        self.msg_entry = ctk.CTkEntry(self.input_container, placeholder_text="Type a message or ask for enterprise architectural advice...", font=("Inter", 16), fg_color="transparent", text_color=self.c_text_primary, border_width=0, height=50)
        self.msg_entry.pack(side="left", fill="x", expand=True, padx=(20, 10), pady=10)
        self.msg_entry.bind("<Return>", lambda event: self.send_message())

        self.send_button = ctk.CTkButton(self.input_container, text="Send", command=self.send_message, font=("Inter", 14, "bold"), fg_color=self.c_brand, hover_color="#0040CC", text_color="#FFFFFF", corner_radius=8, height=40, width=80)
        self.send_button.pack(side="right", padx=(0, 20), pady=10)

        self.quick_actions = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        self.quick_actions.grid(row=3, column=0, padx=40, pady=(0, 40), sticky="ew")
        self.quick_actions.grid_columnconfigure((0,1,2,3), weight=1)
        
        actions = ["Summarize Docs", "Check Logs", "Security Audit", "Sync Resources"]
        for i, act in enumerate(actions):
            btn = ctk.CTkButton(self.quick_actions, text=act, fg_color=self.c_card_bg, text_color="#45464D", border_color=self.c_border, border_width=1, corner_radius=8, hover_color="#F1F5F9", font=("Inter", 13))
            btn.grid(row=0, column=i, padx=5, sticky="ew")

        # --- 2. EDITOR FRAME (Task Dashboard) ---
        self.editor_frame = ctk.CTkFrame(self, fg_color=self.c_main_bg, corner_radius=0)
        self.editor_frame.grid_columnconfigure(0, weight=1)
        self.editor_frame.grid_rowconfigure(1, weight=1)
        
        self.top_bar_ed = ctk.CTkFrame(self.editor_frame, fg_color=self.c_card_bg, height=64, corner_radius=0, border_color=self.c_border, border_width=1)
        self.top_bar_ed.grid(row=0, column=0, sticky="ew")
        self.top_bar_ed.grid_propagate(False)
        self.screen_title_ed = ctk.CTkLabel(self.top_bar_ed, text="Tasks", font=("Hanken Grotesk", 18, "bold"), text_color=self.c_text_primary)
        self.screen_title_ed.pack(side="left", padx=40, pady=15)
        
        self.new_task_btn = ctk.CTkButton(self.top_bar_ed, text="+ New Task", font=("Inter", 14, "bold"), fg_color=self.c_brand, hover_color="#0040CC", text_color="#FFFFFF", corner_radius=8, height=36, command=lambda: self.select_frame("add_task"))
        self.new_task_btn.pack(side="right", padx=40)
        
        self.dash_scroll = ctk.CTkScrollableFrame(self.editor_frame, fg_color="transparent")
        self.dash_scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.dash_scroll.grid_columnconfigure(0, weight=1)
        
        # Metrics Row
        self.metrics_frame = ctk.CTkFrame(self.dash_scroll, fg_color="transparent")
        self.metrics_frame.pack(fill="x", pady=(0, 20))
        self.metrics_frame.grid_columnconfigure((0,1,2,3), weight=1)
        
        self.kpi_labels = {}
        def create_metric_card(parent, title, value, col, highlight=False):
            bg = "#131b2e" if highlight else self.c_card_bg
            txt = "#FFFFFF" if highlight else self.c_text_primary
            subtxt = "#7c839b" if highlight else "#64748B"
            card = ctk.CTkFrame(parent, fg_color=bg, corner_radius=8, border_color=self.c_border if not highlight else bg, border_width=1)
            card.grid(row=0, column=col, padx=10, sticky="ew")
            l_title = ctk.CTkLabel(card, text=title, font=("JetBrains Mono", 12), text_color=subtxt)
            l_title.pack(anchor="w", padx=20, pady=(20, 5))
            l_val = ctk.CTkLabel(card, text=value, font=("Hanken Grotesk", 32, "bold"), text_color=txt)
            l_val.pack(anchor="w", padx=20, pady=(0, 20))
            return l_val

        self.kpi_labels["active"] = create_metric_card(self.metrics_frame, "ACTIVE TASKS", "0", 0)
        self.kpi_labels["completion"] = create_metric_card(self.metrics_frame, "COMPLETION RATE", "-", 1)
        self.kpi_labels["resolution"] = create_metric_card(self.metrics_frame, "AVG. RESOLUTION", "-", 2)
        self.kpi_labels["capacity"] = create_metric_card(self.metrics_frame, "AI CAPACITY", "92%", 3, highlight=True)

        # Priority & Insights Grid
        self.mid_grid = ctk.CTkFrame(self.dash_scroll, fg_color="transparent")
        self.mid_grid.pack(fill="x", pady=(0, 20))
        self.mid_grid.grid_columnconfigure(0, weight=2)
        self.mid_grid.grid_columnconfigure(1, weight=1)
        
        # Priority Actions (Left)
        self.priority_actions = ctk.CTkFrame(self.mid_grid, fg_color=self.c_card_bg, corner_radius=8, border_color=self.c_border, border_width=1)
        self.priority_actions.grid(row=0, column=0, padx=10, sticky="nsew")
        ctk.CTkLabel(self.priority_actions, text="Priority Actions", font=("Hanken Grotesk", 18, "bold"), text_color=self.c_text_primary).pack(anchor="w", padx=20, pady=15)
        
        act1 = ctk.CTkLabel(self.priority_actions, text="Critical System Patch: Node 7\nUnusual latency detected in Northern region cluster.", font=("Inter", 14), justify="left", text_color="#45464D")
        act1.pack(anchor="w", padx=20, pady=10)
        
        act2 = ctk.CTkLabel(self.priority_actions, text="Workflow Optimization Opportunity\nAI detected redundant validation steps in 'Monthly Report'.", font=("Inter", 14), justify="left", text_color="#45464D")
        act2.pack(anchor="w", padx=20, pady=10)

        # AI Insights Panel (Right)
        self.insights = ctk.CTkFrame(self.mid_grid, fg_color="#131B2E", corner_radius=8)
        self.insights.grid(row=0, column=1, padx=10, sticky="nsew")
        ctk.CTkLabel(self.insights, text="AI Insights", font=("Hanken Grotesk", 18, "bold"), text_color="#FFFFFF").pack(anchor="w", padx=20, pady=15)
        
        ctk.CTkLabel(self.insights, text="PREDICTIVE ANALYSIS\nProject 'Aegis' will likely hit a bottleneck in 3 days.", font=("Inter", 13), justify="left", text_color="#7C839B").pack(anchor="w", padx=20, pady=10)
        ctk.CTkLabel(self.insights, text="SENTIMENT TRACKER\nTeam communication shows rising fatigue markers.", font=("Inter", 13), justify="left", text_color="#7C839B").pack(anchor="w", padx=20, pady=10)

        # Task Inventory Table
        self.inventory = ctk.CTkFrame(self.dash_scroll, fg_color=self.c_card_bg, corner_radius=8, border_color=self.c_border, border_width=1)
        self.inventory.pack(fill="x", padx=10, pady=(0, 20))
        
        ctk.CTkLabel(self.inventory, text="Task Inventory", font=("Hanken Grotesk", 18, "bold"), text_color=self.c_text_primary).pack(anchor="w", padx=20, pady=15)
        
        self.table_grid = ctk.CTkFrame(self.inventory, fg_color="transparent")
        self.table_grid.pack(fill="x", pady=(0, 10))
        self.table_grid.grid_columnconfigure(0, weight=3)
        self.table_grid.grid_columnconfigure(1, weight=1)
        self.table_grid.grid_columnconfigure(2, weight=1)
        self.table_grid.grid_columnconfigure(3, weight=1)

        hdr_bg = ctk.CTkFrame(self.table_grid, fg_color="#F2F4F6", corner_radius=0, height=40)
        hdr_bg.grid(row=0, column=0, columnspan=4, sticky="nsew")

        ctk.CTkLabel(self.table_grid, text="TASK NAME", font=("JetBrains Mono", 12), text_color="#45464D", bg_color="#F2F4F6").grid(row=0, column=0, sticky="w", padx=20, pady=10)
        ctk.CTkLabel(self.table_grid, text="STATUS", font=("JetBrains Mono", 12), text_color="#45464D", bg_color="#F2F4F6").grid(row=0, column=1, sticky="w", padx=20)
        ctk.CTkLabel(self.table_grid, text="PRIORITY", font=("JetBrains Mono", 12), text_color="#45464D", bg_color="#F2F4F6").grid(row=0, column=2, sticky="w", padx=20)
        ctk.CTkLabel(self.table_grid, text="DUE DATE", font=("JetBrains Mono", 12), text_color="#45464D", bg_color="#F2F4F6").grid(row=0, column=3, sticky="w", padx=20)

        # --- 3. ADD TASK FRAME ---
        self.add_task_frame = ctk.CTkFrame(self, fg_color=self.c_main_bg, corner_radius=0)
        self.add_task_frame.grid_columnconfigure(0, weight=1)
        self.add_task_frame.grid_rowconfigure(1, weight=1)
        
        self.top_bar_add = ctk.CTkFrame(self.add_task_frame, fg_color=self.c_card_bg, height=64, corner_radius=0, border_color=self.c_border, border_width=1)
        self.top_bar_add.grid(row=0, column=0, sticky="ew")
        self.top_bar_add.grid_propagate(False)
        
        self.back_btn = ctk.CTkButton(self.top_bar_add, text="< Back", font=("Inter", 14), fg_color="transparent", text_color="#45464D", hover_color="#F2F4F6", width=60, command=lambda: self.select_frame("editor"))
        self.back_btn.pack(side="left", padx=(40, 10), pady=15)
        
        ctk.CTkLabel(self.top_bar_add, text="Add Task", font=("Hanken Grotesk", 18, "bold"), text_color=self.c_text_primary).pack(side="left", pady=15)
        
        self.add_scroll = ctk.CTkScrollableFrame(self.add_task_frame, fg_color="transparent")
        self.add_scroll.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        self.add_scroll.grid_columnconfigure(0, weight=2)
        self.add_scroll.grid_columnconfigure(1, weight=1)
        
        # Left Column: Form
        self.form_container = ctk.CTkFrame(self.add_scroll, fg_color=self.c_card_bg, corner_radius=12, border_color=self.c_border, border_width=1)
        self.form_container.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        ctk.CTkLabel(self.form_container, text="TASK NAME", font=("JetBrains Mono", 12, "bold"), text_color="#45464D").pack(anchor="w", padx=30, pady=(30, 5))
        self.task_name_entry = ctk.CTkEntry(self.form_container, font=("Inter", 16), fg_color=self.c_main_bg, border_color=self.c_border, border_width=1, height=45, text_color=self.c_text_primary)
        self.task_name_entry.pack(fill="x", padx=30, pady=(0, 20))
        
        ctk.CTkLabel(self.form_container, text="DESCRIPTION", font=("JetBrains Mono", 12, "bold"), text_color="#45464D").pack(anchor="w", padx=30, pady=(0, 5))
        self.task_desc_entry = ctk.CTkTextbox(self.form_container, font=("Inter", 16), fg_color=self.c_main_bg, border_color=self.c_border, border_width=1, height=150, text_color=self.c_text_primary)
        self.task_desc_entry.pack(fill="x", padx=30, pady=(0, 20))
        
        self.form_row = ctk.CTkFrame(self.form_container, fg_color="transparent")
        self.form_row.pack(fill="x", padx=30, pady=(0, 30))
        self.form_row.grid_columnconfigure((0,1), weight=1)
        
        self.priority_frame = ctk.CTkFrame(self.form_row, fg_color="transparent")
        self.priority_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(self.priority_frame, text="PRIORITY", font=("JetBrains Mono", 12, "bold"), text_color="#45464D").pack(anchor="w", pady=(0, 5))
        self.priority_var = ctk.StringVar(value="Medium")
        self.pri_seg = ctk.CTkSegmentedButton(self.priority_frame, values=["Low", "Medium", "High"], variable=self.priority_var, fg_color=self.c_main_bg, selected_color=self.c_brand, unselected_color=self.c_main_bg, selected_hover_color="#0040CC", height=40)
        self.pri_seg.pack(fill="x")
        
        self.date_frame = ctk.CTkFrame(self.form_row, fg_color="transparent")
        self.date_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        ctk.CTkLabel(self.date_frame, text="DUE DATE", font=("JetBrains Mono", 12, "bold"), text_color="#45464D").pack(anchor="w", pady=(0, 5))
        self.date_entry = ctk.CTkEntry(self.date_frame, font=("Inter", 16), fg_color=self.c_main_bg, border_color=self.c_border, border_width=1, height=40, placeholder_text="YYYY-MM-DD", text_color=self.c_text_primary)
        self.date_entry.pack(fill="x")
        
        self.btn_row = ctk.CTkFrame(self.form_container, fg_color="transparent")
        self.btn_row.pack(fill="x", padx=30, pady=(0, 30))
        self.create_btn = ctk.CTkButton(self.btn_row, text="Create Task", font=("Inter", 14, "bold"), fg_color=self.c_brand, hover_color="#0040CC", text_color="#FFFFFF", corner_radius=8, height=45, command=self.save_new_task)
        self.create_btn.pack(side="right", padx=(10, 0))
        self.discard_btn = ctk.CTkButton(self.btn_row, text="Discard", font=("Inter", 14), fg_color="transparent", border_color=self.c_border, border_width=1, text_color=self.c_text_primary, hover_color="#F2F4F6", corner_radius=8, height=45, command=lambda: self.select_frame("editor"))
        self.discard_btn.pack(side="right")
        
        # Right Column: AI Sidebar
        self.ai_sidebar = ctk.CTkFrame(self.add_scroll, fg_color="transparent")
        self.ai_sidebar.grid(row=0, column=1, sticky="nsew")
        
        self.ai_assist = ctk.CTkFrame(self.ai_sidebar, fg_color="#131B2E", corner_radius=12)
        self.ai_assist.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(self.ai_assist, text="COGNITIVE ASSIST", font=("JetBrains Mono", 12, "bold"), text_color="#D8E2FF").pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(self.ai_assist, text="AI can help you break this down into sub-tasks once saved. It will analyze your description to generate a structured roadmap.", font=("Inter", 14), text_color="#7C839B", justify="left", wraplength=300).pack(anchor="w", padx=20, pady=(0, 20))
        
        self.meta_card = ctk.CTkFrame(self.ai_sidebar, fg_color=self.c_card_bg, corner_radius=12, border_color=self.c_border, border_width=1)
        self.meta_card.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(self.meta_card, text="SYSTEM METADATA", font=("JetBrains Mono", 12, "bold"), text_color="#45464D").pack(anchor="w", padx=20, pady=(20, 10))
        
        def add_meta_row(parent, key, val, is_badge=False):
            r = ctk.CTkFrame(parent, fg_color="transparent")
            r.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(r, text=key, font=("Inter", 14), text_color="#45464D").pack(side="left")
            if is_badge:
                ctk.CTkLabel(r, text=val, font=("JetBrains Mono", 12), fg_color="#D8E2FF", text_color="#004395", corner_radius=4).pack(side="right")
            else:
                ctk.CTkLabel(r, text=val, font=("Inter", 14), text_color=self.c_text_primary).pack(side="right")
                
        add_meta_row(self.meta_card, "Assigned To", "You", True)
        add_meta_row(self.meta_card, "Workspace", "Main Scaffold")
        add_meta_row(self.meta_card, "Security Level", "Level 4")
        ctk.CTkFrame(self.meta_card, fg_color="transparent", height=10).pack()


        self.chat_messages = [
            {"role": "system", "content": "You are AIManager, an autonomous agent orchestrator."}
        ]
        self.row_counter = 0

        # Phase 2: Start Orchestrator
        self.workspace_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workspace")
        self.orchestrator = Orchestrator(self.workspace_dir, self.handle_new_task)
        self.orchestrator.start()

        self.select_frame("editor")
        
        self.add_bubble("System", "AIManager initialized. Please ensure your LM Studio local server is running on port 1234.")
        self.add_bubble("System", f"Polling engine started. Monitoring workspace\\task.md for changes.")
        
        # Initial refresh
        self.after(500, self.refresh_task_table)

    def refresh_task_table(self):
        # Clear existing rows
        for widget in self.table_grid.winfo_children():
            info = widget.grid_info()
            if 'row' in info and int(info['row']) > 0:
                widget.destroy()

        tasks = []
        task_queue_path = os.path.join(self.workspace_dir, "task.md")
        if os.path.exists(task_queue_path):
            with open(task_queue_path, 'r', encoding='utf-8') as f:
                content = f.read()
            for line in content.split('\n'):
                line = line.strip()
                status = None
                if line.startswith('- [ ] '):
                    status = "Pending"
                elif line.startswith('- [>] '):
                    status = "In Progress"
                elif line.startswith('- [x] '):
                    status = "Completed"
                    
                if status:
                    task_content = line[6:]
                    name = task_content.split(": ", 1)[0] if ": " in task_content else task_content
                    tasks.append((status, name))

        # Update KPI
        if hasattr(self, 'kpi_labels'):
            active_count = len(tasks)
            self.kpi_labels["active"].configure(text=str(active_count))
            if active_count == 0:
                self.kpi_labels["completion"].configure(text="-")
                self.kpi_labels["resolution"].configure(text="-")
            else:
                self.kpi_labels["completion"].configure(text="0%")
                self.kpi_labels["resolution"].configure(text="0h")

        if not tasks:
            ctk.CTkLabel(self.table_grid, text="No active tasks in queue.", font=("Inter", 14), text_color="#64748B").grid(row=1, column=0, columnspan=4, pady=20)
        else:
            today = datetime.now().strftime("%b %d, %Y")
            current_row = 1
            for status, task_name in tasks:
                color = "#0058BE" if status == "Pending" else "#F59E0B" if status == "In Progress" else "#10B981"
                
                ctk.CTkLabel(self.table_grid, text=task_name, font=("Inter", 14, "bold"), text_color=self.c_text_primary).grid(row=current_row, column=0, sticky="w", padx=20, pady=15)
                ctk.CTkLabel(self.table_grid, text=status, font=("Inter", 14, "bold"), text_color=color).grid(row=current_row, column=1, sticky="w", padx=20)
                ctk.CTkLabel(self.table_grid, text="HIGH", font=("JetBrains Mono", 12, "bold"), text_color="#BA1A1A").grid(row=current_row, column=2, sticky="w", padx=20)
                ctk.CTkLabel(self.table_grid, text=today, font=("Inter", 14), text_color="#45464D").grid(row=current_row, column=3, sticky="w", padx=20)
                current_row += 1
                
                div = ctk.CTkFrame(self.table_grid, fg_color=self.c_border, height=1)
                div.grid(row=current_row, column=0, columnspan=4, sticky="ew")
                current_row += 1

    def select_frame(self, name):
        if name == "chat":
            self.chat_frame.grid(row=0, column=1, sticky="nsew")
            self.editor_frame.grid_forget()
            self.add_task_frame.grid_forget()
            self.nav_chat_btn.configure(fg_color=self.c_brand, text_color="#FFFFFF")
            self.nav_editor_btn.configure(fg_color="transparent", text_color="#7C839B")
        elif name == "editor":
            self.editor_frame.grid(row=0, column=1, sticky="nsew")
            self.chat_frame.grid_forget()
            self.add_task_frame.grid_forget()
            self.nav_editor_btn.configure(fg_color=self.c_brand, text_color="#FFFFFF")
            self.nav_chat_btn.configure(fg_color="transparent", text_color="#7C839B")
            self.refresh_task_table()
        elif name == "add_task":
            self.add_task_frame.grid(row=0, column=1, sticky="nsew")
            self.editor_frame.grid_forget()
            self.chat_frame.grid_forget()
            # Deselect sidebar nav visually as we are in a sub-screen
            self.nav_editor_btn.configure(fg_color=self.c_brand, text_color="#FFFFFF")
            self.nav_chat_btn.configure(fg_color="transparent", text_color="#7C839B")

    def save_new_task(self):
        title = self.task_name_entry.get().strip()
        desc = self.task_desc_entry.get("1.0", "end-1c").strip()
        if not title:
            return
            
        task_queue_path = os.path.join(self.workspace_dir, "task.md")
        content = ""
        if os.path.exists(task_queue_path):
            with open(task_queue_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
        if "# Tasks" not in content:
            content = "# Tasks\n\n"
            
        task_string = f"- [ ] {title}: {desc}\n"
        content += task_string
        
        with open(task_queue_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        # clear fields
        self.task_name_entry.delete(0, "end")
        self.task_desc_entry.delete("1.0", "end")
        
        # go back to dashboard
        self.select_frame("editor")

    def open_task_file(self):
        task_queue_path = os.path.join(self.workspace_dir, "task.md")
        if os.path.exists(task_queue_path):
            os.startfile(task_queue_path)
            self.add_bubble("System", "Opened task.md. Edit and save to trigger AI processing.")

    def add_bubble(self, sender, text):
        is_user = (sender == "You")
        
        bubble_frame = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        bubble_frame.grid(row=self.row_counter, column=0, sticky="e" if is_user else "w", pady=10)
        self.row_counter += 1
        
        header = ctk.CTkLabel(bubble_frame, text=sender, font=("Inter", 12, "bold"), text_color=self.c_brand if is_user else "#45464D")
        header.pack(anchor="e" if is_user else "w", padx=5, pady=(0, 2))
        
        bg_color = self.c_brand if is_user else self.c_card_bg
        txt_color = "#FFFFFF" if is_user else self.c_text_primary
        
        msg_label = ctk.CTkLabel(bubble_frame, text=text, font=("Inter", 15), fg_color=bg_color, text_color=txt_color, corner_radius=8, justify="left" if not is_user else "right", wraplength=600)
        msg_label.pack(anchor="e" if is_user else "w", ipadx=15, ipady=10)
        
        self.after(50, self.chat_scroll._parent_canvas.yview_moveto, 1.0)
        return msg_label

    def send_message(self):
        user_text = self.msg_entry.get().strip()
        if not user_text:
            return

        self.msg_entry.delete(0, "end")
        self.add_bubble("You", user_text)
        self.chat_messages.append({"role": "user", "content": user_text})

        self.send_button.configure(state="disabled")
        threading.Thread(target=self.call_llm, daemon=True).start()

    def call_llm(self):
        try:
            response = client.chat.completions.create(
                model="local-model",
                messages=self.chat_messages,
                temperature=0.7,
                stream=True
            )
            
            ai_label = self.add_bubble("AI Oracle", "")
            
            ai_message = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    text_chunk = chunk.choices[0].delta.content
                    ai_message += text_chunk
                    self.after(0, lambda label=ai_label, txt=ai_message: label.configure(text=txt))
            
            self.chat_messages.append({"role": "assistant", "content": ai_message})
            
            if hasattr(self, 'orchestrator'):
                self.orchestrator.write_active_task(ai_message)
                self.orchestrator.mark_task_completed()
                
                self.after(0, self.refresh_task_table)

        except Exception as e:
            self.add_bubble("System", f"Error connecting to LM Studio: {e}")
        finally:
            self.send_button.configure(state="normal")

    def handle_new_task(self, task_content):
        self.after(0, self._process_task_gui_update, task_content)
        
    def _process_task_gui_update(self, task_content):
        self.add_bubble("System (Queue)", f"Detected new task from markdown:\n{task_content}")
        self.chat_messages.append({"role": "user", "content": task_content})
        self.refresh_task_table()
        
        self.send_button.configure(state="disabled")
        threading.Thread(target=self.call_llm, daemon=True).start()

if __name__ == "__main__":
    app = AIManagerApp()
    app.mainloop()
