import customtkinter as ctk
import random
from typing import Dict, Any, List
from data_manager import DataManager

# Configuration
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

QUESTIONS_FILE = 'questions.json'
ANALYTICS_FILE = 'analytics.json'

class FlashcardApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("Flashcard Wizard")
        self.geometry("700x500")

        # Data Loading
        self.questions = DataManager.load_json(QUESTIONS_FILE, default=[])
        self.analytics = DataManager.load_analytics(ANALYTICS_FILE)
        self.current_question = None
        
        # Session Data
        self.session_data = {"correct": 0, "total": 0, "mistakes": []}

        # Sync Analytics Categories
        self.sync_analytics_categories()
        
        # UI Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.tab_practice = self.tab_view.add("Practice")
        self.tab_analytics = self.tab_view.add("Analytics")
        
        # Setup Tabs
        self.setup_practice_tab()
        self.setup_analytics_tab()
        
        # Start First Round
        self.next_question()

    def sync_analytics_categories(self):
        """Ensures all categories in questions.json exist in analytics."""
        categories = DataManager.get_unique_categories(self.questions)
        if "performance" not in self.analytics:
            self.analytics["performance"] = {}
            
        updated = False
        for cat in categories:
            if cat not in self.analytics["performance"]:
                self.analytics["performance"][cat] = {"correct": 0, "total": 0}
                updated = True
        
        if updated:
            DataManager.save_json(ANALYTICS_FILE, self.analytics)

    def setup_practice_tab(self):
        # Configure Grid
        self.tab_practice.grid_columnconfigure(0, weight=1)
        self.tab_practice.grid_rowconfigure(1, weight=1) # Buttons area expands

        # Category Selection
        self.frm_controls = ctk.CTkFrame(self.tab_practice, fg_color="transparent")
        self.frm_controls.grid(row=0, column=0, pady=10, sticky="ew")
        self.frm_controls.grid_columnconfigure((0,1), weight=1)

        self.lbl_category_sel = ctk.CTkLabel(self.frm_controls, text="Study Category:", font=("Roboto", 14))
        self.lbl_category_sel.grid(row=0, column=0, sticky="e", padx=10)

        categories = ["All"] + DataManager.get_unique_categories(self.questions)
        self.cmb_category = ctk.CTkComboBox(self.frm_controls, values=categories, command=self.on_category_change)
        self.cmb_category.set("All")
        self.cmb_category.grid(row=0, column=1, sticky="w", padx=10)

        # Question Area (Moved down slightly)
        self.lbl_category = ctk.CTkLabel(self.tab_practice, text="Category: Loading...", font=("Roboto", 12))
        self.lbl_category.grid(row=1, column=0, pady=(10, 0))

        # Question Label
        self.lbl_question = ctk.CTkLabel(self.tab_practice, text="Question text here", font=("Roboto", 20),
                                         wraplength=600)
        self.lbl_question.grid(row=2, column=0, pady=20, sticky="n")

        # Options Container
        self.frm_options = ctk.CTkFrame(self.tab_practice, fg_color="transparent")
        self.frm_options.grid(row=3, column=0, pady=20, sticky="ew")
        self.frm_options.grid_columnconfigure((0,1), weight=1)

        # Create Buttons (4)
        self.option_buttons = []
        for i in range(4):
            btn = ctk.CTkButton(self.frm_options, text=f"Option {i}", height=50, 
                                font=("Roboto", 14),
                                command=lambda idx=i: self.check_answer(idx))
            btn.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="ew")
            self.option_buttons.append(btn)
        
        # Next Button & Finish Session
        self.frm_actions = ctk.CTkFrame(self.tab_practice, fg_color="transparent")
        self.frm_actions.grid(row=4, column=0, pady=20)
        
        self.btn_next = ctk.CTkButton(self.frm_actions, text="Next Question", command=self.next_question,
                                      fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.btn_next.grid(row=0, column=0, padx=10)

        self.btn_finish = ctk.CTkButton(self.frm_actions, text="Finish Session", command=self.show_session_report,
                                        fg_color="#D32F2F", hover_color="#B71C1C")
        self.btn_finish.grid(row=0, column=1, padx=10)
        self.btn_next.configure(state="disabled")

    def setup_analytics_tab(self):
        self.tab_analytics.grid_columnconfigure(0, weight=1)
        
        # Header
        self.lbl_analytics_header = ctk.CTkLabel(self.tab_analytics, text="Performance Dashboard", font=("Roboto", 24, "bold"))
        self.lbl_analytics_header.grid(row=0, column=0, pady=20)
        
        # Stats Container
        self.frm_stats = ctk.CTkScrollableFrame(self.tab_analytics, label_text="Category Breakdown")
        self.frm_stats.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # Insights Label
        self.lbl_insights = ctk.CTkLabel(self.tab_analytics, text="Insights loading...", font=("Roboto", 14),
                                         wraplength=600, justify="left")
        self.lbl_insights.grid(row=2, column=0, pady=20, sticky="w", padx=20)

        # Reset Button
        self.btn_reset = ctk.CTkButton(self.tab_analytics, text="Reset Analytics", command=self.reset_analytics,
                                       fg_color="#D32F2F", hover_color="#B71C1C")
        self.btn_reset.grid(row=3, column=0, pady=20)

    def on_category_change(self, choice):
        self.next_question()

    def next_question(self):
        if not self.questions:
            self.lbl_question.configure(text="No questions available.")
            return

        # Filter by Category
        selected_cat = self.cmb_category.get()
        if selected_cat == "All":
            pool = self.questions
        else:
            pool = [q for q in self.questions if q.get('category') == selected_cat]

        if not pool:
             self.lbl_question.configure(text=f"No questions found for '{selected_cat}'.")
             # Disable options
             for btn in self.option_buttons:
                 btn.configure(state="disabled", text="")
             self.btn_next.configure(state="disabled")
             return

        # Simple Random Selection
        self.current_question = random.choice(pool)
        
        # Update UI
        self.lbl_category.configure(text=f"Category: {self.current_question.get('category', 'General')}")
        self.lbl_question.configure(text=self.current_question.get('question', ''))
        
        # Reset Buttons
        options = self.current_question.get('options', [])
        mapping = ['A', 'B', 'C', 'D']
        
        for i, btn in enumerate(self.option_buttons):
            if i < len(options):
                btn.configure(text=options[i], state="normal", fg_color=["#3B8ED0", "#1F6AA5"]) # Default Blue
            else:
                btn.configure(state="disabled", text="")
        
        self.btn_next.configure(state="disabled")

    def check_answer(self, idx):
        if not self.current_question:
            return

        mapping = ['A', 'B', 'C', 'D']
        selected_option = mapping[idx] if idx < 4 else ""
        correct_option = self.current_question.get('correct_answer', '')
        category = self.current_question.get('category', 'General')

        is_correct = (selected_option == correct_option)
        
        # Immediate UI Feedback
        if is_correct:
            self.option_buttons[idx].configure(fg_color="green")
        else:
            self.option_buttons[idx].configure(fg_color="red")
            # Highlight correct one
            correct_idx = mapping.index(correct_option) if correct_option in mapping else -1
            if correct_idx != -1:
                self.option_buttons[correct_idx].configure(fg_color="green")

        # Disable all buttons
        for btn in self.option_buttons:
            btn.configure(state="disabled")
        
        self.btn_next.configure(state="normal")
        
        # Update Analytics Data
        self.update_analytics(category, is_correct)
        
        # Update Session Data
        self.session_data["total"] += 1
        if is_correct:
            self.session_data["correct"] += 1
        else:
            self.session_data["mistakes"].append({
                "question": self.current_question.get("question"),
                "category": category
            })


    def update_analytics(self, category: str, is_correct: bool):
        # Update Streak
        if is_correct:
            self.analytics["streak"] = self.analytics.get("streak", 0) + 1
        else:
            self.analytics["streak"] = 0
            
        # Update Category Performance
        if "performance" not in self.analytics:
            self.analytics["performance"] = {}
            
        cat_stats = self.analytics["performance"].get(category, {"correct": 0, "total": 0})
        cat_stats["total"] += 1
        if is_correct:
            cat_stats["correct"] += 1
            
        self.analytics["performance"][category] = cat_stats
        
        # Save
        DataManager.save_json(ANALYTICS_FILE, self.analytics)
        
        # Refresh Analytics Tab
        self.refresh_analytics_ui()

    def refresh_analytics_ui(self):
        # Clear existing widgets in scroll frame
        for widget in self.frm_stats.winfo_children():
            widget.destroy()
            
        perf = self.analytics.get("performance", {})
        
        # Determine Strongest/Weakest
        max_pct = -1.0
        min_pct = 101.0
        strongest = "None"
        weakest = "None"
        
        row = 0
        for cat, stats in perf.items():
            total = stats.get("total", 0)
            correct = stats.get("correct", 0)
            if total == 0: continue
            
            pct = (correct / total)
            
            if pct > max_pct:
                max_pct = pct
                strongest = cat
            if pct < min_pct:
                min_pct = pct
                weakest = cat
            
            # Draw UI Row
            lbl = ctk.CTkLabel(self.frm_stats, text=f"{cat} ({correct}/{total})", width=100, anchor="w")
            lbl.grid(row=row, column=0, padx=10, pady=5)
            
            prog = ctk.CTkProgressBar(self.frm_stats)
            prog.set(pct)
            prog.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
            
            pct_lbl = ctk.CTkLabel(self.frm_stats, text=f"{pct*100:.1f}%")
            pct_lbl.grid(row=row, column=2, padx=10, pady=5)
            
            row += 1
            
        # Update Streak & Insights
        streak = self.analytics.get("streak", 0)
        self.lbl_insights.configure(text=f"Current Streak: {streak} 🔥\n"
                                         f"Strongest Area: {strongest} ({max_pct*100:.1f}%)\n"
                                         f"Area to Improve: {weakest} ({min_pct*100:.1f}%)")

    def reset_analytics(self):
        # Reset Data
        self.analytics = {"streak": 0, "performance": {}}
        self.sync_analytics_categories() # Re-add empty categories
        DataManager.save_json(ANALYTICS_FILE, self.analytics)
        self.refresh_analytics_ui()
    
    def show_session_report(self):
        report = ctk.CTkToplevel(self)
        report.title("Session Report")
        report.geometry("400x500")
        
        total = self.session_data["total"]
        if total == 0:
            ctk.CTkLabel(report, text="No questions attempted yet!", font=("Roboto", 16)).pack(pady=20)
            return

        correct = self.session_data["correct"]
        pct = (correct / total) * 100
        
        ctk.CTkLabel(report, text="Session Summary", font=("Roboto", 20, "bold")).pack(pady=10)
        ctk.CTkLabel(report, text=f"Score: {pct:.1f}% ({correct}/{total})", font=("Roboto", 18)).pack(pady=5)
        
        if pct >= 80:
            msg = "Great job! You're doing well."
            color = "green"
        elif pct >= 50:
            msg = "Good effort, keep practicing!"
            color = "orange"
        else:
            msg = "Review needed in weak areas."
            color = "red"
            
        ctk.CTkLabel(report, text=msg, text_color=color, font=("Roboto", 14)).pack(pady=10)
        
        if self.session_data["mistakes"]:
            ctk.CTkLabel(report, text="Needs Improvement:", font=("Roboto", 14, "bold")).pack(pady=5)
            
            # Group mistakes by category
            mistake_cats = {}
            for m in self.session_data["mistakes"]:
                cat = m['category']
                mistake_cats[cat] = mistake_cats.get(cat, 0) + 1
                
            for cat, count in mistake_cats.items():
                ctk.CTkLabel(report, text=f"• {cat} ({count} mistakes)").pack()

        ctk.CTkButton(report, text="Close", command=report.destroy).pack(pady=20, side="bottom")

if __name__ == "__main__":
    app = FlashcardApp()
    app.refresh_analytics_ui() # Initial populate
    app.mainloop()
