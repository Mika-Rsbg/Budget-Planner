import tkinter as tk
from tkinter import ttk, messagebox
import locale
from utils.ai.budget_suggestions import BudgetSuggestionEngine

class BudgetSuggestionDialog(tk.Toplevel):
    """Dialog for collecting income/expense data and showing budget suggestions."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("AI Budget Suggestions")
        self.geometry("600x500")
        self.resizable(False, False)
        
        # Initialize suggestion engine
        self.suggestion_engine = BudgetSuggestionEngine()
        
        # Set up the UI
        self._init_ui()
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
    def _init_ui(self):
        """Initialize the user interface."""
        # Main frame
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Pack Buttons LAST with side=tk.BOTTOM ---
        self.button_frame = ttk.Frame(main_frame)

        # Use tk.Button for color customization
        tk.Button(
            self.button_frame, 
            text="Generate Suggestions", 
            command=self._generate_suggestions,
            bg="#4CAF50",        # Green background
            fg="white",          # White text
            activebackground="#45a049",  # Darker green when pressed
            activeforeground="white"
        ).pack(side=tk.RIGHT, padx=5)

        tk.Button(
            self.button_frame, 
            text="Cancel", 
            command=self.destroy,
            bg="#f44336",        # Red background
            fg="white",          # White text
            activebackground="#d32f2f",  # Darker red when pressed
            activeforeground="white"
        ).pack(side=tk.RIGHT, padx=5)
        
        # --- Pack Content sections TOP ---
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="AI Budget Suggestions", 
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(pady=(0, 20))  # REMOVE side=tk.TOP
        
        # Income frame
        income_frame = ttk.LabelFrame(main_frame, text="Monthly Income", padding=10)
        income_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(income_frame, text="Monthly Income (€):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.income_var = tk.StringVar()
        self.income_entry = ttk.Entry(income_frame, textvariable=self.income_var, width=15)
        self.income_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        # Expenses frame
        expenses_frame = ttk.LabelFrame(main_frame, text="Monthly Expenses (Optional)", padding=10)
        expenses_frame.pack(fill=tk.X, pady=10)  # REMOVE side=tk.TOP
        
        # Expense categories
        self.expense_vars = {}
        expense_categories = [
            ("Housing (rent/mortgage)", "housing"),
            ("Utilities", "utilities"),
            ("Food & Groceries", "food"),
            ("Transportation", "transportation"),
            ("Healthcare", "healthcare"),
            ("Entertainment", "entertainment"),
            ("Debt Payments", "debt")
        ]
        
        for i, (label, key) in enumerate(expense_categories):
            ttk.Label(expenses_frame, text=f"{label} (€):").grid(row=i, column=0, sticky=tk.W, pady=5)
            self.expense_vars[key] = tk.StringVar()
            ttk.Entry(expenses_frame, textvariable=self.expense_vars[key], width=15).grid(
                row=i, column=1, sticky=tk.W, pady=5
            )

        # --- Pack the Button Frame ---
        self.button_frame.pack(fill=tk.X, pady=(20, 0), side=tk.BOTTOM) # Pack buttons at the bottom

        # Results frame (created but not packed initially)
        self.results_frame = ttk.LabelFrame(main_frame, text="Your Personalized Budget Plan", padding=10)
        
        # Set focus to income entry
        self.income_entry.focus_set()
    
    def _generate_suggestions(self):
        """Generate and display budget suggestions based on user input."""
        print("Generate Suggestions button clicked")  # Debug print
        try:
            # Get income
            income_str = self.income_var.get().strip()
            if not income_str:
                messagebox.showerror("Error", "Please enter your monthly income.")
                return
            
            income = float(income_str.replace(',', '.'))
            
            # Get expenses (if provided)
            expenses = {}
            for key, var in self.expense_vars.items():
                value = var.get().strip()
                if value:
                    expenses[key] = float(value.replace(',', '.'))
            
            # Generate suggestions
            suggestions = self.suggestion_engine.get_suggestion(income, expenses)
            print("Suggestions generated:", suggestions)  # Debug print
            
            # Display results
            self._display_suggestions(suggestions, income)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for income and expenses.")

    def _display_suggestions(self, suggestions, income):
        """Display the generated suggestions."""
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Always pack (or repack) the results frame
        self.results_frame.pack_forget()
        self.results_frame.pack(fill=tk.BOTH, expand=True, pady=10)  # REMOVE side=tk.TOP
        self.button_frame.lift()

        # Show results frame if not already visible
        if not self.results_frame.winfo_ismapped():
            # Pack the results frame before the button frame
            self.results_frame.pack(fill=tk.BOTH, expand=True, pady=10, side=tk.TOP) 
            # Ensure button frame stays at the bottom
            self.button_frame.lift() 

        # --- Allocations Section ---
        allocations_frame = ttk.Frame(self.results_frame)
        allocations_frame.pack(fill=tk.X, pady=(0, 10)) # Add padding below
        
        ttk.Label(
            allocations_frame, 
            text="Suggested Monthly Allocations:", 
            font=("Helvetica", 12, "bold")
        ).pack(anchor=tk.W)
        
        # Create a table-like display for allocations
        allocation_table = ttk.Frame(allocations_frame)
        allocation_table.pack(fill=tk.X, pady=5)
        
        # Headers
        headers = ["Category", "Percentage", "Amount (€)"]
        for col, header in enumerate(headers):
            ttk.Label(allocation_table, text=header, font=("Helvetica", 10, "bold")).grid(
                row=0, column=col, sticky=tk.W, padx=5, pady=2
            )
            allocation_table.columnconfigure(col, weight=1 if col == 0 else 0) # Allow category name to expand

        # Data rows
        category_names = {
            "needs": "Needs (essentials)",
            "wants": "Wants (non-essentials)",
            "savings": "Savings & Debt Repayment" # Updated name for clarity
        }
        
        row = 1
        for category, percentage in suggestions["allocations"].items():
            # Category Name
            ttk.Label(allocation_table, text=category_names.get(category, category)).grid(
                row=row, column=0, sticky=tk.W, padx=5, pady=2
            )
            # Percentage
            ttk.Label(allocation_table, text=f"{percentage*100:.0f}%").grid(
                row=row, column=1, sticky=tk.W, padx=5, pady=2
            )
            # Amount
            amount = suggestions["suggested_amounts"][category]
            # Use locale for currency formatting
            amount_str = locale.format_string("%.2f", amount, grouping=True) 
            ttk.Label(allocation_table, text=amount_str).grid(
                row=row, column=2, sticky=tk.W, padx=5, pady=2
            )
            row += 1
        
        # Separator
        ttk.Separator(self.results_frame, orient=tk.HORIZONTAL).pack(
            fill=tk.X, pady=10
        )
        
        # --- Tips Section ---
        tips_frame = ttk.Frame(self.results_frame)
        # Pack below separator, allow vertical expansion and fill horizontally
        tips_frame.pack(fill=tk.X, pady=5) 
        
        ttk.Label(
            tips_frame, 
            text="Personalized Tips:", 
            font=("Helvetica", 12, "bold")
        ).pack(anchor=tk.W, pady=(0, 5)) # Add padding below title
        
        # Use a Text widget for better display of multiple tips
        tips_text = tk.Text(
            tips_frame, 
            wrap=tk.WORD, # Wrap long lines
            height=5,     # Adjust height as needed
            borderwidth=0, # Make it look like a label
            relief=tk.FLAT, # No border
            # background=self.results_frame.cget("background"), # REMOVE THIS LINE
            font=("Helvetica", 10)
        )
        tips_text.pack(fill=tk.X, expand=True)
        
        # Insert tips with bullet points
        for tip in suggestions["tips"]:
            tips_text.insert(tk.END, f"• {tip}\n") 
            
        # Disable editing
        tips_text.config(state=tk.DISABLED) 

        # Adjust dialog size slightly if results make it too cramped (optional)
        self.geometry("600x650") # Increase height to accommodate results

        # Disable editing
        tips_text.config(state=tk.DISABLED)  # Make read-only