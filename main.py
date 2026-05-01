import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from datetime import datetime
import os
from tkinter import font

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # API configuration
        self.api_key = "YOUR_API_KEY"  # Replace with your actual API key
        self.base_url = "https://v6.exchangerate-api.com/v6/"
        
        # Data storage
        self.currencies = []
        self.history_file = "history.json"
        self.conversion_history = []
        
        # Load history
        self.load_history()
        
        # Setup UI
        self.setup_ui()
        
        # Fetch currencies
        self.fetch_currencies()
        
    def setup_ui(self):
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_font = font.Font(size=16, weight="bold")
        title_label = ttk.Label(main_frame, text="Currency Converter", font=title_font)
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # From Currency
        ttk.Label(main_frame, text="From Currency:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.from_currency = ttk.Combobox(main_frame, values=[], state="readonly", width=15)
        self.from_currency.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(0, 10))
        
        # To Currency
        ttk.Label(main_frame, text="To Currency:").grid(row=1, column=2, sticky=tk.W, pady=5)
        self.to_currency = ttk.Combobox(main_frame, values=[], state="readonly", width=15)
        self.to_currency.grid(row=1, column=3, sticky=(tk.W, tk.E), pady=5)
        
        # Amount
        ttk.Label(main_frame, text="Amount:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.amount_entry = ttk.Entry(main_frame, width=20)
        self.amount_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Result
        ttk.Label(main_frame, text="Result:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.result_label = ttk.Label(main_frame, text="", font=("Arial", 12, "bold"))
        self.result_label.grid(row=3, column=1, columnspan=3, sticky=tk.W, pady=5)
        
        # Convert Button
        self.convert_btn = ttk.Button(main_frame, text="Convert", command=self.convert_currency)
        self.convert_btn.grid(row=4, column=0, columnspan=4, pady=20)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').grid(row=5, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        # History Section
        ttk.Label(main_frame, text="Conversion History", font=("Arial", 12, "bold")).grid(row=6, column=0, columnspan=4, sticky=tk.W, pady=(10, 5))
        
        # History Table Frame with Scrollbar
        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=7, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(table_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview for history
        columns = ("Date", "From", "To", "Amount", "Result")
        self.history_tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                         yscrollcommand=scrollbar_y.set,
                                         xscrollcommand=scrollbar_x.set)
        
        # Define headings
        self.history_tree.heading("Date", text="Date")
        self.history_tree.heading("From", text="From")
        self.history_tree.heading("To", text="To")
        self.history_tree.heading("Amount", text="Amount")
        self.history_tree.heading("Result", text="Result")
        
        # Set column widths
        self.history_tree.column("Date", width=150)
        self.history_tree.column("From", width=80)
        self.history_tree.column("To", width=80)
        self.history_tree.column("Amount", width=100)
        self.history_tree.column("Result", width=150)
        
        self.history_tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar_y.config(command=self.history_tree.yview)
        scrollbar_x.config(command=self.history_tree.xview)
        
        # Buttons for history management
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Clear History", command=self.clear_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save History", command=self.save_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load History", command=self.load_history_ui).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.columnconfigure(3, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
    def fetch_currencies(self):
        """Fetch available currencies from API"""
        try:
            # Show loading message
            self.convert_btn.config(state="disabled", text="Loading currencies...")
            self.root.update()
            
            url = f"{self.base_url}{self.api_key}/codes"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("result") == "success":
                # Extract currency codes and names
                self.currencies = [f"{code} - {name}" for code, name in data.get("supported_codes", [])]
                self.from_currency['values'] = self.currencies
                self.to_currency['values'] = self.currencies
                
                # Set default values
                if self.currencies:
                    # Find USD and EUR
                    usd_index = next((i for i, c in enumerate(self.currencies) if c.startswith("USD")), 0)
                    eur_index = next((i for i, c in enumerate(self.currencies) if c.startswith("EUR")), 1 if len(self.currencies) > 1 else 0)
                    
                    self.from_currency.current(usd_index)
                    self.to_currency.current(eur_index)
                    
                self.convert_btn.config(state="normal", text="Convert")
            else:
                messagebox.showerror("Error", "Failed to fetch currencies. Please check your API key.")
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Network error: {str(e)}")
            self.convert_btn.config(state="normal", text="Convert")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.convert_btn.config(state="normal", text="Convert")
    
    def validate_amount(self, amount):
        """Validate that amount is a positive number"""
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                return False, "Amount must be greater than 0"
            return True, amount_float
        except ValueError:
            return False, "Please enter a valid number"
    
    def convert_currency(self):
        """Perform currency conversion"""
        # Validate amount
        amount = self.amount_entry.get().strip()
        is_valid, result = self.validate_amount(amount)
        
        if not is_valid:
            messagebox.showerror("Validation Error", result)
            return
        
        amount_value = result
        
        # Get selected currencies
        from_currency_code = self.from_currency.get().split(" - ")[0] if self.from_currency.get() else ""
        to_currency_code = self.to_currency.get().split(" - ")[0] if self.to_currency.get() else ""
        
        if not from_currency_code or not to_currency_code:
            messagebox.showerror("Error", "Please select currencies")
            return
        
        try:
            # Disable button during conversion
            self.convert_btn.config(state="disabled", text="Converting...")
            self.root.update()
            
            # Make API request
            url = f"{self.base_url}{self.api_key}/pair/{from_currency_code}/{to_currency_code}/{amount_value}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("result") == "success":
                converted_amount = data.get("conversion_result")
                exchange_rate = data.get("conversion_rate")
                
                # Display result
                result_text = f"{amount_value:,.2f} {from_currency_code} = {converted_amount:,.2f} {to_currency_code} (Rate: {exchange_rate:.4f})"
                self.result_label.config(text=result_text)
                
                # Add to history
                history_entry = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "from_currency": from_currency_code,
                    "to_currency": to_currency_code,
                    "amount": amount_value,
                    "result": converted_amount,
                    "rate": exchange_rate
                }
                
                self.conversion_history.insert(0, history_entry)  # Add to beginning
                self.update_history_display()
                
                # Save history automatically
                self.save_history()
                
            else:
                messagebox.showerror("Error", "Conversion failed. Please try again.")
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Network error: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.convert_btn.config(state="normal", text="Convert")
    
    def update_history_display(self):
        """Update the history table display"""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Add history entries
        for entry in self.conversion_history:
            self.history_tree.insert("", "end", values=(
                entry["date"],
                entry["from_currency"],
                entry["to_currency"],
                f"{entry['amount']:,.2f}",
                f"{entry['result']:,.2f}"
            ))
    
    def save_history(self):
        """Save conversion history to JSON file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversion_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save history: {str(e)}")
    
    def load_history(self):
        """Load conversion history from JSON file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.conversion_history = json.load(f)
                self.update_history_display()
        except Exception as e:
            print(f"Could not load history: {str(e)}")
            self.conversion_history = []
    
    def load_history_ui(self):
        """Load history and show confirmation"""
        try:
            self.load_history()
            messagebox.showinfo("Success", "History loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load history: {str(e)}")
    
    def clear_history(self):
        """Clear all conversion history"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all history?"):
            self.conversion_history = []
            self.update_history_display()
            self.save_history()
            messagebox.showinfo("Success", "History cleared!")

def main():
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()