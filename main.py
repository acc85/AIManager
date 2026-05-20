import customtkinter as ctk
from openai import OpenAI
import threading
import os
import subprocess
import socket
from orchestrator import Orchestrator
from datetime import datetime
import json

import requests

class TaskExecution:
    def __init__(self, task_name):
        self.task_name = task_name
        self.slot_id = None
        self.status = "In Progress"
        self.reasoning_text = ""
        self.response_text = ""
        self.response_obj = None
        self.abort_generation = False
        self.bubbles = [{"sender": "Task Prompt", "text": task_name}]

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
        
        # Load persisted settings
        self.load_settings()
        
        # Bind close protocol
        self.llama_process = None
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Task execution tracking
        self.is_task_running = False
        self.current_task_info = ""
        self.current_task_response = ""
        self.current_task_response_obj = None
        self.abort_generation = False
        
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

        # Added Settings navigation button
        self.nav_settings_btn = ctk.CTkButton(self.sidebar_frame, text="Settings", corner_radius=8, height=45, fg_color="transparent", hover_color="#1E293B", text_color="#7C839B", font=("Inter", 14), anchor="w", command=lambda: self.select_frame("settings"))
        self.nav_settings_btn.grid(row=4, column=0, padx=20, pady=5, sticky="ew")

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
        
        # Dynamically set model badge from configuration
        self.model_badge = ctk.CTkLabel(self.top_bar, text=self.settings["model_name"].upper(), fg_color="#E0E7FF", text_color=self.c_brand, corner_radius=4, font=("JetBrains Mono", 11, "bold"))
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

        self.stop_button = ctk.CTkButton(self.input_container, text="Stop", command=self.stop_task, font=("Inter", 14, "bold"), fg_color="#EF4444", hover_color="#DC2626", text_color="#FFFFFF", corner_radius=8, height=40, width=80)
        self.stop_button.pack(side="right", padx=(0, 10), pady=10)
        self.stop_button.configure(state="disabled")

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
        self.table_grid.grid_columnconfigure(4, weight=1)

        hdr_bg = ctk.CTkFrame(self.table_grid, fg_color="#F2F4F6", corner_radius=0, height=40)
        hdr_bg.grid(row=0, column=0, columnspan=5, sticky="nsew")

        ctk.CTkLabel(self.table_grid, text="TASK NAME", font=("Inter", 12), text_color="#45464D", bg_color="#F2F4F6").grid(row=0, column=0, sticky="w", padx=20, pady=10)
        ctk.CTkLabel(self.table_grid, text="STATUS", font=("Inter", 12), text_color="#45464D", bg_color="#F2F4F6").grid(row=0, column=1, sticky="w", padx=20)
        ctk.CTkLabel(self.table_grid, text="PRIORITY", font=("Inter", 12), text_color="#45464D", bg_color="#F2F4F6").grid(row=0, column=2, sticky="w", padx=20)
        ctk.CTkLabel(self.table_grid, text="DUE DATE", font=("Inter", 12), text_color="#45464D", bg_color="#F2F4F6").grid(row=0, column=3, sticky="w", padx=20)
        ctk.CTkLabel(self.table_grid, text="ACTIONS", font=("Inter", 12), text_color="#45464D", bg_color="#F2F4F6").grid(row=0, column=4, sticky="w", padx=20)

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

        # --- 4. SETTINGS FRAME (System Configuration) ---
        self.settings_frame = ctk.CTkFrame(self, fg_color=self.c_main_bg, corner_radius=0)
        self.settings_frame.grid_columnconfigure(0, weight=1)
        self.settings_frame.grid_rowconfigure(1, weight=1)
        
        self.top_bar_set = ctk.CTkFrame(self.settings_frame, fg_color=self.c_card_bg, height=64, corner_radius=0, border_color=self.c_border, border_width=1)
        self.top_bar_set.grid(row=0, column=0, sticky="ew")
        self.top_bar_set.grid_propagate(False)
        
        self.back_btn_set = ctk.CTkButton(self.top_bar_set, text="< Back", font=("Inter", 14), fg_color="transparent", text_color="#45464D", hover_color="#F2F4F6", width=60, command=lambda: self.select_frame("editor"))
        self.back_btn_set.pack(side="left", padx=(40, 10), pady=15)
        
        ctk.CTkLabel(self.top_bar_set, text="System Settings", font=("Hanken Grotesk", 18, "bold"), text_color=self.c_text_primary).pack(side="left", pady=15)
        
        self.settings_scroll = ctk.CTkScrollableFrame(self.settings_frame, fg_color="transparent")
        self.settings_scroll.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        self.settings_scroll.grid_columnconfigure(0, weight=2)
        self.settings_scroll.grid_columnconfigure(1, weight=1)
        
        # Left Column: Configuration Cards
        self.settings_cards_container = ctk.CTkFrame(self.settings_scroll, fg_color="transparent")
        self.settings_cards_container.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        # Card 1: AI Configuration
        self.ai_config_card = ctk.CTkFrame(self.settings_cards_container, fg_color=self.c_card_bg, corner_radius=12, border_color=self.c_border, border_width=1)
        self.ai_config_card.pack(fill="x", pady=(0, 20))
        
        ai_card_header = ctk.CTkFrame(self.ai_config_card, fg_color="transparent")
        ai_card_header.pack(fill="x", padx=30, pady=(30, 15))
        ctk.CTkLabel(ai_card_header, text="🧠 AI Configuration", font=("Hanken Grotesk", 18, "bold"), text_color=self.c_text_primary).pack(side="left")
        
        ctk.CTkLabel(self.ai_config_card, text="AI URL ENDPOINT", font=("JetBrains Mono", 12, "bold"), text_color="#45464D").pack(anchor="w", padx=30, pady=(10, 5))
        self.settings_endpoint_entry = ctk.CTkEntry(self.ai_config_card, font=("Inter", 16), fg_color=self.c_main_bg, border_color=self.c_border, border_width=1, height=45, text_color=self.c_text_primary)
        self.settings_endpoint_entry.pack(fill="x", padx=30, pady=(0, 15))
        
        ctk.CTkLabel(self.ai_config_card, text="API KEY", font=("JetBrains Mono", 12, "bold"), text_color="#45464D").pack(anchor="w", padx=30, pady=(0, 5))
        self.settings_apikey_entry = ctk.CTkEntry(self.ai_config_card, font=("Inter", 16), fg_color=self.c_main_bg, border_color=self.c_border, border_width=1, height=45, text_color=self.c_text_primary, show="*")
        self.settings_apikey_entry.pack(fill="x", padx=30, pady=(0, 15))
        
        ctk.CTkLabel(self.ai_config_card, text="MODEL NAME", font=("JetBrains Mono", 12, "bold"), text_color="#45464D").pack(anchor="w", padx=30, pady=(0, 5))
        self.settings_model_entry = ctk.CTkEntry(self.ai_config_card, font=("Inter", 16), fg_color=self.c_main_bg, border_color=self.c_border, border_width=1, height=45, text_color=self.c_text_primary)
        self.settings_model_entry.pack(fill="x", padx=30, pady=(0, 15))
        
        ctk.CTkLabel(self.ai_config_card, text="AI TEMPERATURE", font=("JetBrains Mono", 12, "bold"), text_color="#45464D").pack(anchor="w", padx=30, pady=(0, 5))
        temp_val_row = ctk.CTkFrame(self.ai_config_card, fg_color="transparent")
        temp_val_row.pack(fill="x", padx=30, pady=(0, 5))
        self.temp_slider_label = ctk.CTkLabel(temp_val_row, text="0.7 (Balanced)", font=("Inter", 14), text_color=self.c_brand)
        self.temp_slider_label.pack(side="left")
        
        self.settings_temp_slider = ctk.CTkSlider(self.ai_config_card, from_=0.0, to=1.0, number_of_steps=100, fg_color=self.c_border, progress_color=self.c_brand, button_color=self.c_brand, button_hover_color="#0040CC", command=self.update_temp_slider_label)
        self.settings_temp_slider.pack(fill="x", padx=30, pady=(0, 30))
        
        # Card 2: System Configuration
        self.sys_config_card = ctk.CTkFrame(self.settings_cards_container, fg_color=self.c_card_bg, corner_radius=12, border_color=self.c_border, border_width=1)
        self.sys_config_card.pack(fill="x", pady=(0, 20))
        
        sys_card_header = ctk.CTkFrame(self.sys_config_card, fg_color="transparent")
        sys_card_header.pack(fill="x", padx=30, pady=(30, 15))
        ctk.CTkLabel(sys_card_header, text="⚙️ System Workspace Configuration", font=("Hanken Grotesk", 18, "bold"), text_color=self.c_text_primary).pack(side="left")
        
        ctk.CTkLabel(self.sys_config_card, text="WORKSPACE DIRECTORY PATH", font=("JetBrains Mono", 12, "bold"), text_color="#45464D").pack(anchor="w", padx=30, pady=(10, 5))
        self.settings_workspace_entry = ctk.CTkEntry(self.sys_config_card, font=("Inter", 16), fg_color=self.c_main_bg, border_color=self.c_border, border_width=1, height=45, text_color=self.c_text_primary)
        self.settings_workspace_entry.pack(fill="x", padx=30, pady=(0, 30))
        
        # Action Row
        self.settings_btn_row = ctk.CTkFrame(self.settings_cards_container, fg_color="transparent")
        self.settings_btn_row.pack(fill="x", pady=(0, 30))
        self.settings_save_btn = ctk.CTkButton(self.settings_btn_row, text="Save Settings", font=("Inter", 14, "bold"), fg_color=self.c_brand, hover_color="#0040CC", text_color="#FFFFFF", corner_radius=8, height=45, command=self.save_settings_from_ui)
        self.settings_save_btn.pack(side="right", padx=(10, 0))
        self.settings_discard_btn = ctk.CTkButton(self.settings_btn_row, text="Discard", font=("Inter", 14), fg_color="transparent", border_color=self.c_border, border_width=1, text_color=self.c_text_primary, hover_color="#F2F4F6", corner_radius=8, height=45, command=lambda: self.select_frame("editor"))
        self.settings_discard_btn.pack(side="right")
        
        # Right Column: Info Sidebar
        self.settings_sidebar = ctk.CTkFrame(self.settings_scroll, fg_color="transparent")
        self.settings_sidebar.grid(row=0, column=1, sticky="nsew")
        
        # Llama Server Logs Card (Right Sidebar)
        self.logs_card = ctk.CTkFrame(self.settings_sidebar, fg_color=self.c_card_bg, corner_radius=12, border_color=self.c_border, border_width=1)
        self.logs_card.pack(fill="x", pady=(0, 20))
        
        logs_header_row = ctk.CTkFrame(self.logs_card, fg_color="transparent")
        logs_header_row.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(logs_header_row, text="📋 Llama Server Logs", font=("Hanken Grotesk", 16, "bold"), text_color=self.c_text_primary).pack(side="left")
        
        # Clear Logs Button
        clear_logs_btn = ctk.CTkButton(logs_header_row, text="Clear", font=("Inter", 12), fg_color="transparent", text_color="#64748B", hover_color="#F2F4F6", width=50, height=24, command=self.clear_logs)
        clear_logs_btn.pack(side="right")
        
        # Scrollable textbox for terminal log viewing
        self.log_textbox = ctk.CTkTextbox(self.logs_card, height=450, fg_color="#0F172A", text_color="#34D399", font=("Consolas", 12), border_color="#1E293B", border_width=1)
        self.log_textbox.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.log_textbox.configure(state="disabled")
        
        self.settings_info = ctk.CTkFrame(self.settings_sidebar, fg_color="#131B2E", corner_radius=12)
        self.settings_info.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(self.settings_info, text="💡 CONFIGURATION HELP", font=("JetBrains Mono", 12, "bold"), text_color="#D8E2FF").pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(self.settings_info, text="Endpoints should specify the base API path (e.g. http://localhost:8080/v1). For local servers like llama-server, keep the endpoint on localhost:8080.\n\nTemperature values control AI output randomness: Precise (< 0.3), Balanced (0.3 - 0.7), and Creative (> 0.7).", font=("Inter", 14), text_color="#7C839B", justify="left", wraplength=300).pack(anchor="w", padx=20, pady=(0, 20))

        # --- STATE ---
        self.chat_messages = [
            {"role": "system", "content": "You are AIManager, an autonomous agent orchestrator."}
        ]
        self.row_counter = 0
        self.running_tasks = {}
        self.current_viewed_task_name = None
        self.gui_bubble_labels = []

        # --- 5. TASK LOGS FRAME (Specific Task execution logs) ---
        self.task_logs_frame = ctk.CTkFrame(self, fg_color=self.c_main_bg, corner_radius=0)
        self.task_logs_frame.grid_columnconfigure(0, weight=1)
        self.task_logs_frame.grid_rowconfigure(1, weight=1)
        
        self.top_bar_log = ctk.CTkFrame(self.task_logs_frame, fg_color=self.c_card_bg, height=64, corner_radius=0, border_color=self.c_border, border_width=1)
        self.top_bar_log.grid(row=0, column=0, sticky="ew")
        self.top_bar_log.grid_propagate(False)
        
        self.back_btn_log = ctk.CTkButton(self.top_bar_log, text="< Back", font=("Inter", 14), fg_color="transparent", text_color="#45464D", hover_color="#F2F4F6", width=60, command=lambda: self.select_frame("editor"))
        self.back_btn_log.pack(side="left", padx=(40, 10), pady=15)
        
        self.log_screen_title = ctk.CTkLabel(self.top_bar_log, text="Task Logs", font=("Hanken Grotesk", 18, "bold"), text_color=self.c_text_primary)
        self.log_screen_title.pack(side="left", pady=15)

        self.stop_task_btn = ctk.CTkButton(self.top_bar_log, text="Stop Task", font=("Inter", 14, "bold"), fg_color="#EF4444", hover_color="#DC2626", text_color="#FFFFFF", corner_radius=8, height=36, command=self.stop_current_logged_task)
        self.stop_task_btn.pack(side="right", padx=40)
        
        self.task_logs_scroll = ctk.CTkScrollableFrame(self.task_logs_frame, fg_color="transparent")
        self.task_logs_scroll.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        self.task_logs_scroll.grid_columnconfigure(0, weight=1)

        # Start local Llama server if it hasn't been started yet
        self.start_llama_server()
        
        # Initialize OpenAI client with configured parameters
        self.client = OpenAI(base_url=self.settings["api_endpoint"], api_key=self.settings["api_key"])

        # Phase 2: Start Orchestrator
        self.workspace_dir = self.settings["workspace_dir"]
        self.orchestrator = Orchestrator(self.workspace_dir, self.handle_new_task)
        self.orchestrator.start()

        self.select_frame("editor")
        
        self.add_bubble("System", "AIManager initialized. Persistent settings configuration loaded.")
        self.add_bubble("System", f"Polling engine started. Monitoring {self.workspace_dir}\\task.md for changes.")
        
        # Initial refresh
        self.after(500, self.refresh_task_table)

    def is_port_in_use(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex(('127.0.0.1', port)) == 0

    def start_llama_server(self):
        endpoint = self.settings.get("api_endpoint", "")
        # Only start llama-server if configured to localhost:8080 or 127.0.0.1:8080
        if "localhost:8080" not in endpoint and "127.0.0.1:8080" not in endpoint:
            print("Configured endpoint is not localhost:8080. Skipping local llama-server autostart.")
            self.append_log("System: Configured endpoint is not localhost:8080. Skipping local llama-server autostart.\n")
            return

        if self.is_port_in_use(8080):
            print("Port 8080 is in use. Assuming Llama server or another process is running.")
            self.add_bubble("System", "Port 8080 is active. Llama-server detection complete.")
            self.append_log("System: Llama-server is already running (detected active port 8080).\n")
            return

        llama_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "llama")
        exe_path = os.path.join(llama_dir, "llama-server.exe")

        if not os.path.exists(exe_path):
            self.add_bubble("System", f"Error: Could not locate llama-server.exe in {llama_dir}")
            self.append_log(f"System Error: Could not locate llama-server.exe in {llama_dir}\n")
            return

        cmd = [
            exe_path,
            "-m", "E:\\models\\unsloth\\Qwen3.6-35B-A3B-MTP-GGUF\\Qwen3.6-35B-A3B-UD-Q3_K_M.gguf",
            "-ngl", "100",
            "-fa", "on",
            "-c", "65536",
            "-np", "4",
            "--spec-type", "draft-mtp",
            "--spec-draft-n-max", "2"
        ]

        try:
            # CREATE_NO_WINDOW = 0x08000000 on Windows
            creation_flags = 0x08000000 if os.name == 'nt' else 0
            self.llama_process = subprocess.Popen(
                cmd,
                cwd=llama_dir,
                creationflags=creation_flags,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            self.add_bubble("System", "Llama-server launched. Monitoring logs...")
            self.append_log("System: Spawning Llama-server process...\n")
            
            # Start background thread to read output
            threading.Thread(target=self.log_reader, daemon=True).start()
        except Exception as e:
            self.add_bubble("System", f"Failed to start Llama-server: {e}")
            self.append_log(f"System Error: Failed to start Llama-server: {e}\n")

    def log_reader(self):
        try:
            while True:
                if not hasattr(self, 'llama_process') or not self.llama_process:
                    break
                line = self.llama_process.stdout.readline()
                if not line:
                    break
                self.after(0, self.append_log, line)
        except Exception as e:
            self.after(0, self.append_log, f"\nSystem Error reading logs: {e}\n")

    def append_log(self, text):
        if hasattr(self, 'log_textbox') and self.log_textbox.winfo_exists():
            self.log_textbox.configure(state="normal")
            self.log_textbox.insert("end", text)
            
            # Prevent memory issues: truncate logs if too long
            current_text = self.log_textbox.get("1.0", "end-1c")
            if len(current_text) > 100000:
                self.log_textbox.delete("1.0", "200.0")
                
            self.log_textbox.see("end")
            self.log_textbox.configure(state="disabled")

    def clear_logs(self):
        if hasattr(self, 'log_textbox') and self.log_textbox.winfo_exists():
            self.log_textbox.configure(state="normal")
            self.log_textbox.delete("1.0", "end")
            self.log_textbox.configure(state="disabled")

    def on_closing(self):
        if hasattr(self, 'orchestrator'):
            try:
                self.orchestrator.stop()
            except Exception:
                pass

        if hasattr(self, 'llama_process') and self.llama_process:
            try:
                self.llama_process.stdout.close()
            except Exception:
                pass
            try:
                self.llama_process.terminate()
                self.llama_process.wait(timeout=2)
            except Exception as e:
                print(f"Error terminating llama-server subprocess: {e}")

        self.destroy()

    def load_settings(self):
        self.settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
        default_settings = {
            "api_endpoint": "http://localhost:8080/v1",
            "api_key": "not-needed",
            "model_name": "local-model",
            "temperature": 0.7,
            "workspace_dir": os.path.join(os.path.dirname(os.path.abspath(__file__)), "workspace")
        }
        
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                                
                # Ensure all default keys exist
                for k, v in default_settings.items():
                    if k not in self.settings:
                        self.settings[k] = v
            except Exception as e:
                print(f"Error loading settings.json: {e}")
                self.settings = default_settings
        else:
            self.settings = default_settings
            self.save_settings_to_file()

    def save_settings_to_file(self):
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings.json: {e}")

    def apply_settings(self, new_settings):
        ws_changed = (new_settings["workspace_dir"] != self.settings["workspace_dir"])
        
        self.settings = new_settings
        self.save_settings_to_file()
        
        # Update client base URL and api key
        self.client = OpenAI(base_url=self.settings["api_endpoint"], api_key=self.settings["api_key"])
        
        # Update model badge
        self.model_badge.configure(text=self.settings["model_name"].upper())
        
        # Update workspace dir
        self.workspace_dir = self.settings["workspace_dir"]
        
        # Re-initialize observer if directory changed
        if ws_changed and hasattr(self, 'orchestrator'):
            self.orchestrator.stop()
            self.orchestrator = Orchestrator(self.workspace_dir, self.handle_new_task)
            self.orchestrator.start()
            self.add_bubble("System", f"Workspace directory updated. Now monitoring: {self.workspace_dir}")

    def update_temp_slider_label(self, val):
        val = round(float(val), 2)
        label = "Balanced"
        if val < 0.3:
            label = "Precise"
        elif val > 0.7:
            label = "Creative"
        self.temp_slider_label.configure(text=f"{val} ({label})")

    def load_settings_into_ui(self):
        self.settings_endpoint_entry.delete(0, "end")
        self.settings_endpoint_entry.insert(0, self.settings["api_endpoint"])
        
        self.settings_apikey_entry.delete(0, "end")
        self.settings_apikey_entry.insert(0, self.settings["api_key"])
        
        self.settings_model_entry.delete(0, "end")
        self.settings_model_entry.insert(0, self.settings["model_name"])
        
        temp_val = float(self.settings.get("temperature", 0.7))
        self.settings_temp_slider.set(temp_val)
        self.update_temp_slider_label(temp_val)
        
        self.settings_workspace_entry.delete(0, "end")
        self.settings_workspace_entry.insert(0, self.settings["workspace_dir"])

    def save_settings_from_ui(self):
        new_settings = {
            "api_endpoint": self.settings_endpoint_entry.get().strip(),
            "api_key": self.settings_apikey_entry.get().strip(),
            "model_name": self.settings_model_entry.get().strip(),
            "temperature": round(float(self.settings_temp_slider.get()), 2),
            "workspace_dir": self.settings_workspace_entry.get().strip()
        }
        
        if not new_settings["api_endpoint"] or not new_settings["workspace_dir"]:
            self.add_bubble("System", "Error: Endpoint and Workspace directory cannot be empty.")
            return
            
        self.apply_settings(new_settings)
        self.add_bubble("System", "Settings applied and saved successfully.")
        self.select_frame("editor")

    def refresh_task_table(self):
        # Clear existing rows
        for widget in self.table_grid.winfo_children():
            info = widget.grid_info()
            if 'row' in info and int(info['row']) > 0:
                widget.destroy()

        tasks = []
        task_queue_path = os.path.join(self.workspace_dir, "task.md")
        
        # Read file lock-free with error handling
        content = ""
        if os.path.exists(task_queue_path):
            try:
                with open(task_queue_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except IOError:
                return
                
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
                tasks.append((status, task_content))

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
            ctk.CTkLabel(self.table_grid, text="No active tasks in queue.", font=("Inter", 14), text_color="#64748B").grid(row=1, column=0, columnspan=5, pady=20)
        else:
            today = datetime.now().strftime("%b %d, %Y")
            current_row = 1
            for status, task_content in tasks:
                color = "#0058BE" if status == "Pending" else "#F59E0B" if status == "In Progress" else "#10B981"
                display_name = task_content.split(": ", 1)[0] if ": " in task_content else task_content
                
                task_btn = ctk.CTkButton(self.table_grid, text=display_name, font=("Inter", 14, "bold"), text_color=self.c_brand, hover_color="#F1F5F9", fg_color="transparent", anchor="w", command=lambda content=task_content: self.show_task_logs(content))
                task_btn.grid(row=current_row, column=0, sticky="w", padx=20, pady=15)
                ctk.CTkLabel(self.table_grid, text=status, font=("Inter", 14, "bold"), text_color=color).grid(row=current_row, column=1, sticky="w", padx=20)
                ctk.CTkLabel(self.table_grid, text="HIGH", font=("JetBrains Mono", 12, "bold"), text_color="#BA1A1A").grid(row=current_row, column=2, sticky="w", padx=20)
                ctk.CTkLabel(self.table_grid, text=today, font=("Inter", 14), text_color="#45464D").grid(row=current_row, column=3, sticky="w", padx=20)
                
                delete_btn = ctk.CTkButton(self.table_grid, text="Delete", font=("Inter", 12, "bold"), fg_color="#FCA5A5", hover_color="#EF4444", text_color="#7F1D1D", width=60, height=24, corner_radius=6, command=lambda content=task_content: self.delete_task(content))
                delete_btn.grid(row=current_row, column=4, sticky="w", padx=20)
                
                current_row += 1
                
                div = ctk.CTkFrame(self.table_grid, fg_color=self.c_border, height=1)
                div.grid(row=current_row, column=0, columnspan=5, sticky="ew")
                current_row += 1

    def select_frame(self, name):
        if name == "chat":
            self.chat_frame.grid(row=0, column=1, sticky="nsew")
            self.editor_frame.grid_forget()
            self.add_task_frame.grid_forget()
            self.settings_frame.grid_forget()
            self.task_logs_frame.grid_forget()
            self.nav_chat_btn.configure(fg_color=self.c_brand, text_color="#FFFFFF")
            self.nav_editor_btn.configure(fg_color="transparent", text_color="#7C839B")
            self.nav_settings_btn.configure(fg_color="transparent", text_color="#7C839B")
        elif name == "editor":
            self.editor_frame.grid(row=0, column=1, sticky="nsew")
            self.chat_frame.grid_forget()
            self.add_task_frame.grid_forget()
            self.settings_frame.grid_forget()
            self.task_logs_frame.grid_forget()
            self.nav_editor_btn.configure(fg_color=self.c_brand, text_color="#FFFFFF")
            self.nav_chat_btn.configure(fg_color="transparent", text_color="#7C839B")
            self.nav_settings_btn.configure(fg_color="transparent", text_color="#7C839B")
            self.refresh_task_table()
        elif name == "add_task":
            self.add_task_frame.grid(row=0, column=1, sticky="nsew")
            self.editor_frame.grid_forget()
            self.chat_frame.grid_forget()
            self.settings_frame.grid_forget()
            self.task_logs_frame.grid_forget()
            self.nav_editor_btn.configure(fg_color=self.c_brand, text_color="#FFFFFF")
            self.nav_chat_btn.configure(fg_color="transparent", text_color="#7C839B")
            self.nav_settings_btn.configure(fg_color="transparent", text_color="#7C839B")
        elif name == "settings":
            self.settings_frame.grid(row=0, column=1, sticky="nsew")
            self.chat_frame.grid_forget()
            self.editor_frame.grid_forget()
            self.add_task_frame.grid_forget()
            self.task_logs_frame.grid_forget()
            self.nav_settings_btn.configure(fg_color=self.c_brand, text_color="#FFFFFF")
            self.nav_chat_btn.configure(fg_color="transparent", text_color="#7C839B")
            self.nav_editor_btn.configure(fg_color="transparent", text_color="#7C839B")
            self.load_settings_into_ui()
        elif name == "task_logs":
            self.task_logs_frame.grid(row=0, column=1, sticky="nsew")
            self.chat_frame.grid_forget()
            self.editor_frame.grid_forget()
            self.add_task_frame.grid_forget()
            self.settings_frame.grid_forget()
            self.nav_settings_btn.configure(fg_color="transparent", text_color="#7C839B")
            self.nav_chat_btn.configure(fg_color="transparent", text_color="#7C839B")
            self.nav_editor_btn.configure(fg_color="transparent", text_color="#7C839B")

    def save_new_task(self):
        title = self.task_name_entry.get().strip()
        desc = self.task_desc_entry.get("1.0", "end-1c").strip()
        if not title:
            return
            
        task_queue_path = os.path.join(self.workspace_dir, "task.md")
        
        # Write file in a background worker thread to prevent main GUI thread blocking
        def write_task_bg():
            lock = self.orchestrator.lock if hasattr(self, 'orchestrator') else threading.RLock()
            with lock:
                try:
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
                except Exception as e:
                    print(f"Error saving task: {e}")
                    
        threading.Thread(target=write_task_bg, daemon=True).start()
            
        # clear fields
        self.task_name_entry.delete(0, "end")
        self.task_desc_entry.delete("1.0", "end")
        
        # go back to dashboard
        self.select_frame("editor")

    def delete_task(self, task_name):
        def delete_task_bg():
            task_queue_path = os.path.join(self.workspace_dir, "task.md")
            lock = self.orchestrator.lock if hasattr(self, 'orchestrator') else threading.RLock()
            with lock:
                try:
                    content = ""
                    if os.path.exists(task_queue_path):
                        with open(task_queue_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                    lines = content.split('\n')
                    new_lines = []
                    deleted = False
                    for line in lines:
                        strip_line = line.strip()
                        if strip_line.startswith("- [ ] ") or strip_line.startswith("- [>] ") or strip_line.startswith("- [x] "):
                            task_content = strip_line[6:]
                            if task_content == task_name:
                                deleted = True
                                continue
                        new_lines.append(line)
                        
                    if deleted:
                        new_content = '\n'.join(new_lines)
                        with open(task_queue_path, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        if hasattr(self, 'orchestrator'):
                            self.orchestrator.handler.last_content = new_content.strip()
                except Exception as e:
                    print(f"Error deleting task: {e}")
            self.after(0, self.refresh_task_table)

        threading.Thread(target=delete_task_bg, daemon=True).start()

    def stop_current_logged_task(self):
        if self.current_viewed_task_name and self.current_viewed_task_name in self.running_tasks:
            task_exec = self.running_tasks[self.current_viewed_task_name]
            task_exec.abort_generation = True
            if task_exec.response_obj:
                try:
                    task_exec.response_obj.close()
                except Exception:
                    pass
            task_exec.status = "Aborted"
            self.stop_task_btn.configure(state="disabled")
            self.add_task_log_bubble(task_exec, "System", "Task aborted via Stop Task button.")
            self.rollback_specific_task(task_exec.task_name)

    def show_task_logs(self, task_name):
        self.current_viewed_task_name = task_name
        self.select_frame("task_logs")
        
        # Clear existing logs widgets
        for widget in self.task_logs_scroll.winfo_children():
            widget.destroy()
            
        task_exec = self.running_tasks.get(task_name)
        if not task_exec:
            # Create a placeholder for historical/completed task
            task_exec = TaskExecution(task_name)
            task_exec.status = "Completed"
            safe_name = "".join([c if c.isalnum() or c in (" ", "_", "-") else "_" for c in task_name]).strip().replace(" ", "_")
            filename = f"task_output_{safe_name}.md"
            active_task_path = os.path.join(self.workspace_dir, filename)
            if os.path.exists(active_task_path):
                try:
                    with open(active_task_path, 'r', encoding='utf-8') as f:
                        saved_text = f.read()
                        task_exec.response_text = saved_text
                        # Split by double newline to form bubbles
                        paragraphs = [p.strip() for p in saved_text.split("\n\n") if p.strip()]
                        for p in paragraphs:
                            task_exec.bubbles.append({"sender": "AI Oracle", "text": p})
                except Exception:
                    pass
            self.running_tasks[task_name] = task_exec
            
        # Update Title & Stop Button
        slot_text = f"(Slot: {task_exec.slot_id})" if task_exec.slot_id is not None else "(Slot: Assigning...)"
        if task_exec.status != "In Progress":
            slot_text = ""
        self.log_screen_title.configure(text=f"Task Logs: {task_name[:30]}... {slot_text}")
        
        if task_exec.status == "In Progress":
            self.stop_task_btn.configure(state="normal")
        else:
            self.stop_task_btn.configure(state="disabled")
            
        # Re-render all bubbles
        self.gui_bubble_labels = []
        for bubble in task_exec.bubbles:
            self.render_log_bubble(bubble["sender"], bubble["text"])
            
        self.after(50, self.task_logs_scroll._parent_canvas.yview_moveto, 1.0)

    def render_log_bubble(self, sender, text):
        is_prompt = sender == "Task Prompt"
        is_system = sender == "System"
        is_thinking = sender == "AI Thinking"
        
        bubble_frame = ctk.CTkFrame(self.task_logs_scroll, fg_color="transparent")
        bubble_frame.pack(fill="x", anchor="w", pady=10)
        
        lbl_sender = ctk.CTkLabel(bubble_frame, text=sender, font=("Inter", 12, "bold"), text_color="#64748B")
        lbl_sender.pack(anchor="w", padx=5)
        
        if is_prompt:
            bg_color = "#1E293B"
            txt_color = "#FFFFFF"
        elif is_system:
            bg_color = "#FEF3C7"
            txt_color = "#78350F"
        elif is_thinking:
            bg_color = "#F1F5F9"
            txt_color = "#475569"
        else:
            bg_color = self.c_card_bg
            txt_color = self.c_text_primary
            
        font = ("Inter", 14, "italic") if is_thinking else ("Inter", 15)
        msg_label = ctk.CTkLabel(bubble_frame, text=text, font=font, fg_color=bg_color, text_color=txt_color, corner_radius=8, justify="left", wraplength=600)
        msg_label.pack(anchor="w", ipadx=15, ipady=10)
        
        self.gui_bubble_labels.append((sender, msg_label))
        return msg_label

    def update_task_generation_gui(self, task_exec):
        if self.current_viewed_task_name != task_exec.task_name:
            return
            
        rendered_ai_bubbles = [lbl for sender, lbl in self.gui_bubble_labels if sender in ("AI Thinking", "AI Oracle")]
        target_ai_bubbles = [b for b in task_exec.bubbles if b["sender"] in ("AI Thinking", "AI Oracle")]
        
        canvas = self.task_logs_scroll._parent_canvas
        scroll_pos = canvas.yview()
        # Auto-scroll only if we are near the bottom (end position > 0.93) or no AI bubbles rendered yet
        should_scroll = scroll_pos[1] > 0.93 or len(rendered_ai_bubbles) == 0
        
        for i, target in enumerate(target_ai_bubbles):
            if i < len(rendered_ai_bubbles):
                rendered_ai_bubbles[i].configure(text=target["text"])
            else:
                self.render_log_bubble(target["sender"], target["text"])
                
        if should_scroll:
            canvas.yview_moveto(1.0)

    def add_task_log_bubble(self, task_exec, sender, text):
        task_exec.bubbles.append({"sender": sender, "text": text})
        if self.current_viewed_task_name == task_exec.task_name:
            self.render_log_bubble(sender, text)
            self.after(50, self.task_logs_scroll._parent_canvas.yview_moveto, 1.0)

    def associate_slot_for_task(self, task_exec, chunk_id):
        try:
            task_id = int(chunk_id.split("-")[-1])
            res = requests.get(self.settings.get("api_endpoint", "http://localhost:8080/v1").replace("/v1", "") + "/slots", timeout=2)
            if res.status_code == 200:
                slots = res.json()
                for slot in slots:
                    if slot.get("id_task") == task_id:
                        task_exec.slot_id = slot.get("id")
                        self.after(0, self.update_logs_title_if_current, task_exec.task_name)
                        break
        except Exception as e:
            print("Error associating slot:", e)

    def update_logs_title_if_current(self, task_name):
        if self.current_viewed_task_name == task_name:
            task_exec = self.running_tasks.get(task_name)
            if task_exec:
                slot_text = f"(Slot: {task_exec.slot_id})" if task_exec.slot_id is not None else "(Slot: Assigning...)"
                self.log_screen_title.configure(text=f"Task Logs: {task_name[:30]}... {slot_text}")

    def rollback_specific_task(self, task_name):
        def run():
            task_queue_path = os.path.join(self.workspace_dir, "task.md")
            lock = self.orchestrator.lock if hasattr(self, 'orchestrator') else threading.RLock()
            with lock:
                try:
                    content = ""
                    if os.path.exists(task_queue_path):
                        with open(task_queue_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                    lines = content.split('\n')
                    updated = False
                    for i, line in enumerate(lines):
                        strip_line = line.strip()
                        if strip_line.startswith("- [>] "):
                            task_content = strip_line[6:]
                            if task_content == task_name:
                                lines[i] = line.replace("- [>] ", "- [ ] ", 1)
                                updated = True
                                break
                                
                    if updated:
                        new_content = '\n'.join(lines)
                        with open(task_queue_path, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        if hasattr(self, 'orchestrator'):
                            self.orchestrator.handler.last_content = new_content.strip()
                except Exception as e:
                    print(f"Error rolling back task {task_name}: {e}")
            self.after(0, self.refresh_task_table)
        threading.Thread(target=run, daemon=True).start()

    def mark_specific_task_completed(self, task_name):
        def run():
            task_queue_path = os.path.join(self.workspace_dir, "task.md")
            lock = self.orchestrator.lock if hasattr(self, 'orchestrator') else threading.RLock()
            with lock:
                try:
                    content = ""
                    if os.path.exists(task_queue_path):
                        with open(task_queue_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                    lines = content.split('\n')
                    updated = False
                    for i, line in enumerate(lines):
                        strip_line = line.strip()
                        if strip_line.startswith("- [>] "):
                            task_content = strip_line[6:]
                            if task_content == task_name:
                                lines[i] = line.replace("- [>] ", "- [x] ", 1)
                                updated = True
                                break
                                
                    if updated:
                        new_content = '\n'.join(lines)
                        with open(task_queue_path, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        if hasattr(self, 'orchestrator'):
                            self.orchestrator.handler.last_content = new_content.strip()
                except Exception as e:
                    print(f"Error completing task {task_name}: {e}")
            self.after(0, self.refresh_task_table)
        threading.Thread(target=run, daemon=True).start()

    def write_task_output(self, task_name, response_text):
        safe_name = "".join([c if c.isalnum() or c in (" ", "_", "-") else "_" for c in task_name]).strip().replace(" ", "_")
        filename = f"task_output_{safe_name}.md"
        active_task_path = os.path.join(self.workspace_dir, filename)
        with open(active_task_path, "w", encoding="utf-8") as f:
            f.write(response_text)

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

    def stop_task(self):
        self.abort_generation = True
        if hasattr(self, "current_task_response_obj") and self.current_task_response_obj:
            try:
                self.current_task_response_obj.close()
            except Exception:
                pass
        self.add_bubble("System", "Cancellation requested via Stop button.")
        self.stop_button.configure(state="disabled")

    def send_message(self):
        user_text = self.msg_entry.get().strip()
        if not user_text:
            return

        self.msg_entry.delete(0, "end")
        self.add_bubble("You", user_text)
        self.chat_messages.append({"role": "user", "content": user_text})

        # Disable entry & send, enable stop button
        self.msg_entry.configure(state="disabled")
        self.send_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        threading.Thread(target=self.call_llm, daemon=True).start()

    def call_llm(self):
        try:
            self.abort_generation = False
            response = self.client.chat.completions.create(
                model=self.settings.get("model_name", "local-model"),
                messages=self.chat_messages,
                temperature=float(self.settings.get("temperature", 0.7)),
                stream=True,
                timeout=15.0
            )
            self.current_task_response_obj = response
            
            # Thread-safe creation of bubble
            label_container = []
            creation_event = threading.Event()
            
            def create_bubble_on_main():
                lbl = self.add_bubble("AI Oracle", "")
                label_container.append(lbl)
                creation_event.set()
                
            self.after(0, create_bubble_on_main)
            creation_event.wait()
            ai_label = label_container[0]
            
            ai_message = ""
            for chunk in response:
                if getattr(self, "abort_generation", False):
                    if hasattr(response, "close"):
                        response.close()
                    break
                delta = chunk.choices[0].delta
                text_chunk = ""
                if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                    text_chunk = delta.reasoning_content
                elif hasattr(delta, "content") and delta.content:
                    text_chunk = delta.content
                elif isinstance(delta, dict):
                    text_chunk = delta.get("reasoning_content") or delta.get("content") or ""
                else:
                    # Fallback to dictionary attribute check if model returned as dict-like object
                    try:
                        text_chunk = getattr(delta, "reasoning_content", None) or getattr(delta, "content", None) or ""
                    except Exception:
                        pass
                
                if text_chunk:
                    ai_message += text_chunk
                    self.current_task_response = ai_message
                    self.after(0, lambda label=ai_label, txt=ai_message: label.configure(text=txt))
            
            if not getattr(self, "abort_generation", False):
                self.chat_messages.append({"role": "assistant", "content": ai_message})
                if hasattr(self, 'orchestrator'):
                    self.orchestrator.write_active_task(ai_message)
                    self.orchestrator.mark_task_completed()
                    self.after(0, self.refresh_task_table)

        except Exception as e:
            if getattr(self, "abort_generation", False):
                self.after(0, lambda: self.add_bubble("System", "Task aborted successfully."))
            else:
                self.after(0, lambda err=e: self.add_bubble("System", f"Error connecting to Llama Server: {err}"))
            if hasattr(self, 'orchestrator'):
                self.orchestrator.rollback_active_task()
                self.after(0, self.refresh_task_table)
        finally:
            self.is_task_running = False
            self.after(0, lambda: self.msg_entry.configure(state="normal"))
            self.after(0, lambda: self.send_button.configure(state="normal"))
            self.after(0, lambda: self.stop_button.configure(state="disabled"))

    def handle_new_task(self, task_content):
        if task_content not in self.running_tasks:
            self.running_tasks[task_content] = TaskExecution(task_content)
        self.after(0, self._process_task_gui_update, task_content)
        
    def _process_task_gui_update(self, task_content):
        self.add_bubble("System (Queue)", f"Detected new task from markdown:\n{task_content}")
        self.refresh_task_table()
        threading.Thread(target=self.run_task_thread, args=(task_content,), daemon=True).start()

    def run_task_thread(self, task_name):
        task_exec = self.running_tasks.get(task_name)
        if not task_exec:
            return

        try:
            task_exec.abort_generation = False
            messages = [
                {"role": "system", "content": "You are AIManager, executing a task from the backlog."},
                {"role": "user", "content": task_name}
            ]
            response = self.client.chat.completions.create(
                model=self.settings.get("model_name", "local-model"),
                messages=messages,
                temperature=float(self.settings.get("temperature", 0.7)),
                stream=True,
                timeout=15.0
            )
            task_exec.response_obj = response
            
            first_chunk = True
            for chunk in response:
                if task_exec.abort_generation:
                    if hasattr(response, "close"):
                        response.close()
                    break
                    
                if first_chunk:
                    chunk_id = getattr(chunk, "id", "")
                    if chunk_id:
                        self.associate_slot_for_task(task_exec, chunk_id)
                    first_chunk = False
                    
                delta = chunk.choices[0].delta
                reasoning_chunk = getattr(delta, "reasoning_content", None)
                if reasoning_chunk is None and hasattr(delta, "model_extra") and delta.model_extra:
                    reasoning_chunk = delta.model_extra.get("reasoning_content")
                elif reasoning_chunk is None and isinstance(delta, dict):
                    reasoning_chunk = delta.get("reasoning_content")
                
                content_chunk = getattr(delta, "content", None)
                if content_chunk is None and isinstance(delta, dict):
                    content_chunk = delta.get("content")
                    
                if reasoning_chunk:
                    task_exec.reasoning_text += reasoning_chunk
                if content_chunk:
                    task_exec.response_text += content_chunk
                    
                # Re-generate bubbles list as single continuous blocks to prevent layout jumpiness during streaming
                bubbles = [{"sender": "Task Prompt", "text": task_name}]
                if task_exec.reasoning_text:
                    bubbles.append({"sender": "AI Thinking", "text": task_exec.reasoning_text})
                if task_exec.response_text:
                    bubbles.append({"sender": "AI Oracle", "text": task_exec.response_text})
                        
                task_exec.bubbles = bubbles
                self.after(0, self.update_task_generation_gui, task_exec)
                    
            if not task_exec.abort_generation:
                task_exec.status = "Completed"
                
                # Split by double newline to form clean final paragraph-split bubbles
                final_bubbles = [{"sender": "Task Prompt", "text": task_name}]
                if task_exec.reasoning_text:
                    r_paragraphs = [p.strip() for p in task_exec.reasoning_text.split("\n\n") if p.strip()]
                    for p in r_paragraphs:
                        final_bubbles.append({"sender": "AI Thinking", "text": p})
                if task_exec.response_text:
                    paragraphs = [p.strip() for p in task_exec.response_text.split("\n\n") if p.strip()]
                    for p in paragraphs:
                        final_bubbles.append({"sender": "AI Oracle", "text": p})
                task_exec.bubbles = final_bubbles
                
                self.write_task_output(task_name, task_exec.response_text)
                self.mark_specific_task_completed(task_name)
                # Re-render logs screen with the final paragraph-split bubbles if looking at it
                if self.current_viewed_task_name == task_name:
                    self.after(0, lambda: self.show_task_logs(task_name))
                self.after(0, lambda: self.add_task_log_bubble(task_exec, "System", "Task completed successfully."))
                
        except Exception as e:
            if task_exec.abort_generation:
                self.after(0, lambda: self.add_task_log_bubble(task_exec, "System", "Task aborted successfully."))
            else:
                task_exec.status = "Error"
                self.after(0, lambda err=e: self.add_task_log_bubble(task_exec, "System", f"Error: {err}"))
            self.rollback_specific_task(task_name)
        finally:
            if self.current_viewed_task_name == task_name:
                self.after(0, lambda: self.stop_task_btn.configure(state="disabled"))

if __name__ == "__main__":
    app = AIManagerApp()
    app.mainloop()
