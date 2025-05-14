import tkinter as tk
from tkinter import ttk  # For themed widgets (looks slightly better)
from tkinter import scrolledtext # For scrollable text areas
from tkinter import messagebox # For pop-up messages
import datetime
import re

# --- Receipt Generation Logic ---
def generate_bloomelein_receipt(customer_name, customer_address, items, delivery_charge, customer_phone=None):
    """
    Generates a formatted receipt string for Bloomelein florist shop,
    with WhatsApp bold formatting for titles.
    """
    # --- Configuration ---
    shop_name = "Bloomelein"
    bank_details = "19851039946 Yew Jun Chee"
    currency = "RM"
    # --- End Configuration ---

    now = datetime.datetime.now()
    receipt_no = now.strftime("%y%m%d-%H%M%S")
    date_str = now.strftime("%B %d, %Y")

    # --- Receipt Text Generation with Bold Titles ---
    # Add asterisks (*) around titles for WhatsApp bold formatting
    receipt_text = f"*🌸 {shop_name} Receipt 🌸*\n\n" # Bold main title
    receipt_text += f"*Date:* {date_str}\n"           # Bold Date label
    receipt_text += f"*Receipt No:* #{receipt_no}\n\n" # Bold Receipt No label

    receipt_text += "*Sold to:*\n"                     # Bold Sold to label
    receipt_text += f"Name: {customer_name}\n"
    receipt_text += f"Address: {customer_address}\n"
    if customer_phone:
        # Clean and format phone number for WhatsApp link
        cleaned_phone = re.sub(r'\D', '', customer_phone)
        if cleaned_phone.startswith('0'):
            cleaned_phone = '60' + cleaned_phone[1:]
        elif cleaned_phone.startswith('6') and not cleaned_phone.startswith('60'):
             cleaned_phone = '60' + cleaned_phone[1:]

        if cleaned_phone.startswith('60'):
             receipt_text += f"Phone: {customer_phone}\n"
             whatsapp_link = f"https://wa.me/{cleaned_phone}"
             receipt_text += f"WhatsApp Contact: {whatsapp_link}\n"
        else:
             receipt_text += f"Phone: {customer_phone} (Link generation skipped - check format)\n"

    receipt_text += "\n*Item(s) Purchased:*\n" # Bold Item(s) Purchased label
    item_subtotal = 0
    for description, price in items:
        try:
            item_price = float(price)
            receipt_text += f"•  {description}\n"
            receipt_text += f"   Price: {currency}{item_price:.2f}\n"
            item_subtotal += item_price
        except ValueError:
             receipt_text += f"•  {description}\n"
             receipt_text += f"   Price: Error - Invalid Price ({price})\n"

    receipt_text += "\n"

    # Format Delivery Charges
    delivery_cost = 0.0
    delivery_display = "FOC"
    if isinstance(delivery_charge, str) and delivery_charge.upper() == 'FOC':
        delivery_cost = 0.0
        delivery_display = "FOC"
    else:
        try:
            delivery_cost = float(delivery_charge)
            if delivery_cost > 0:
                 delivery_display = f"{currency}{delivery_cost:.2f}"
            else:
                 delivery_cost = 0.0
                 delivery_display = "FOC"
        except ValueError:
             delivery_cost = 0.0
             delivery_display = "FOC (Invalid Input)"

    receipt_text += f"Delivery Charges: {delivery_display}\n\n" # Not bolding this one, but could if needed

    # Bold Total label
    total_amount = item_subtotal + delivery_cost
    receipt_text += f"*Total:* {currency} {total_amount:.2f}\n\n"

    # Bold Payment Method label
    receipt_text += "*Payment Method:*\n"
    receipt_text += f"🏦 Bank Transfer: {bank_details}\n\n"

    receipt_text += "Thank you for your purchase! 🌷"

    return receipt_text
# --- End of receipt generation logic ---


# --- GUI Application Class ---
# (This class remains exactly the same as the previous version with the copy button)
class ReceiptApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bloomelein Receipt Generator")
        self.root.geometry("650x700") # Window size

        self.items_list = [] # To store (description, price) tuples

        self.style = ttk.Style()
        self.style.theme_use('clam')

        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Customer Details Frame ---
        customer_frame = ttk.LabelFrame(main_frame, text="Customer Details", padding="10")
        customer_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        main_frame.columnconfigure(0, weight=1)

        ttk.Label(customer_frame, text="Name:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.customer_name_entry = ttk.Entry(customer_frame, width=40)
        self.customer_name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(customer_frame, text="Address:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.customer_address_entry = tk.Text(customer_frame, height=3, width=40)
        self.customer_address_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(customer_frame, text="Phone (Optional):").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.customer_phone_entry = ttk.Entry(customer_frame, width=40)
        self.customer_phone_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        customer_frame.columnconfigure(1, weight=1)

        # --- Items Frame ---
        items_frame = ttk.LabelFrame(main_frame, text="Add Items", padding="10")
        items_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        items_frame.columnconfigure(1, weight=1)
        items_frame.columnconfigure(3, weight=1)

        ttk.Label(items_frame, text="Description:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.item_desc_entry = ttk.Entry(items_frame, width=30)
        self.item_desc_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(items_frame, text="Price (RM):").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.item_price_entry = ttk.Entry(items_frame, width=10)
        self.item_price_entry.grid(row=0, column=3, padx=5, pady=2, sticky="ew")

        self.add_item_button = ttk.Button(items_frame, text="Add Item", command=self.add_item)
        self.add_item_button.grid(row=0, column=4, padx=10, pady=5)

        # --- Items List Display ---
        self.items_display = scrolledtext.ScrolledText(main_frame, height=6, width=70, wrap=tk.WORD, state=tk.DISABLED)
        self.items_display.grid(row=2, column=0, padx=15, pady=5, sticky="ew")

        # --- Delivery & Action Buttons Frame ---
        actions_frame = ttk.Frame(main_frame, padding="5")
        actions_frame.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        actions_frame.columnconfigure(1, weight=1)
        actions_frame.columnconfigure(3, weight=0)
        actions_frame.columnconfigure(4, weight=0)

        ttk.Label(actions_frame, text="Delivery Charge (RM or FOC):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.delivery_charge_entry = ttk.Entry(actions_frame, width=15)
        self.delivery_charge_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.delivery_charge_entry.insert(0, "FOC")

        # --- Copy Button ---
        self.copy_button = ttk.Button(actions_frame, text="Copy Receipt", command=self.copy_receipt_to_clipboard)
        self.copy_button.grid(row=0, column=3, padx=5, pady=5, sticky="e")

        # --- Generate Button ---
        self.generate_button = ttk.Button(actions_frame, text="Generate Receipt", command=self.generate_action)
        self.generate_button.grid(row=0, column=4, padx=5, pady=5, sticky="e")

        # --- Receipt Output Frame ---
        output_frame = ttk.LabelFrame(main_frame, text="Generated Receipt (Copy from here or use button)", padding="10")
        output_frame.grid(row=4, column=0, padx=5, pady=5, sticky="nsew")
        main_frame.rowconfigure(4, weight=1)

        self.receipt_output_text = scrolledtext.ScrolledText(output_frame, height=15, width=70, wrap=tk.WORD)
        self.receipt_output_text.pack(fill=tk.BOTH, expand=True)
        self.receipt_output_text.configure(state=tk.DISABLED)

    def add_item(self):
        """Adds item description and price to the list and display."""
        description = self.item_desc_entry.get().strip()
        price_str = self.item_price_entry.get().strip()

        if not description:
            messagebox.showerror("Error", "Please enter an item description.")
            return
        if not price_str:
             messagebox.showerror("Error", "Please enter an item price.")
             return

        try:
            price = float(price_str)
            if price < 0:
                 messagebox.showerror("Error", "Price cannot be negative.")
                 return
        except ValueError:
            messagebox.showerror("Error", f"Invalid price entered: '{price_str}'. Please enter a number.")
            return

        self.items_list.append((description, price))

        display_text = f"• {description} - RM{price:.2f}"
        self.items_display.configure(state=tk.NORMAL)
        self.items_display.insert(tk.END, display_text + "\n")
        self.items_display.configure(state=tk.DISABLED)

        self.item_desc_entry.delete(0, tk.END)
        self.item_price_entry.delete(0, tk.END)
        self.item_desc_entry.focus()

    def generate_action(self):
        """Gets all inputs, calls generator, and displays the receipt."""
        customer_name = self.customer_name_entry.get().strip()
        customer_address = self.customer_address_entry.get("1.0", tk.END).strip()
        customer_phone = self.customer_phone_entry.get().strip() or None
        delivery_charge_str = self.delivery_charge_entry.get().strip()

        if not customer_name:
            messagebox.showerror("Error", "Customer Name cannot be empty.")
            return
        if not customer_address:
             messagebox.showerror("Error", "Customer Address cannot be empty.")
             return
        if not self.items_list:
            messagebox.showerror("Error", "Please add at least one item.")
            return

        delivery_charge_input = 0.0
        if delivery_charge_str.upper() == 'FOC':
             delivery_charge_input = 'FOC'
        else:
            try:
                delivery_charge_input = float(delivery_charge_str)
                if delivery_charge_input < 0:
                    messagebox.showwarning("Warning", "Delivery charge cannot be negative. Treating as FOC.")
                    delivery_charge_input = 'FOC'
            except ValueError:
                 messagebox.showwarning("Warning", f"Invalid delivery charge '{delivery_charge_str}'. Treating as FOC.")
                 delivery_charge_input = 'FOC'

        try:
             # Call the updated generator function
             receipt_content = generate_bloomelein_receipt(
                 customer_name=customer_name,
                 customer_address=customer_address,
                 items=self.items_list,
                 delivery_charge=delivery_charge_input,
                 customer_phone=customer_phone
             )

             self.receipt_output_text.configure(state=tk.NORMAL)
             self.receipt_output_text.delete("1.0", tk.END)
             self.receipt_output_text.insert("1.0", receipt_content)
             self.receipt_output_text.configure(state=tk.DISABLED)

        except Exception as e:
             messagebox.showerror("Generation Error", f"An unexpected error occurred:\n{e}")

    def copy_receipt_to_clipboard(self):
        """Copies the content of the receipt output text area to the clipboard."""
        receipt_content = self.receipt_output_text.get("1.0", tk.END).strip()
        if not receipt_content:
            messagebox.showinfo("Info", "Nothing to copy yet. Please generate a receipt first.")
            return

        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(receipt_content)
            messagebox.showinfo("Copied!", "Receipt content copied to clipboard.")
        except Exception as e:
            messagebox.showerror("Clipboard Error", f"Could not copy to clipboard:\n{e}")

# --- Run the application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = ReceiptApp(root)
    root.mainloop()