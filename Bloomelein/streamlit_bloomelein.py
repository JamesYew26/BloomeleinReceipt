import streamlit as st
import datetime
import re

# --- Receipt Generation Logic ---
def generate_bloomelein_receipt(customer_name, customer_address, items, delivery_charge, customer_phone=None):
    """
    Generates a formatted receipt string for Bloomelein florist shop,
    with WhatsApp bold formatting for titles and daily incrementing receipt number.
    """
    # --- Configuration ---
    shop_name = "Bloomelein"
    bank_details = "\n19851039946 \nYew Jun Chee \nHong Leong Bank"
    currency = "RM"
    # --- End Configuration ---

    now = datetime.datetime.now() # Get current datetime
    current_date_obj = now.date() # Get today's date object
    current_date_str_compare = current_date_obj.strftime("%Y-%m-%d") # Format for comparison YYYY-MM-DD
    date_part_receipt = current_date_obj.strftime("%y%m%d") # Format for receipt number YYMMDD
    date_display_str = now.strftime("%B %d, %Y") # Format for display on receipt

    # --- Daily Incrementing Receipt Number Logic ---
    # Get counter state, defaulting if not present
    last_receipt_date = st.session_state.get("last_receipt_date", None)
    daily_receipt_counter = st.session_state.get("daily_receipt_counter", 0)

    if current_date_str_compare != last_receipt_date:
        # Date has changed or first run of the day, reset counter
        current_counter = 1
        st.session_state.last_receipt_date = current_date_str_compare # Store comparison date
        st.session_state.daily_receipt_counter = current_counter
    else:
        # Same date, increment counter
        current_counter = daily_receipt_counter + 1
        st.session_state.daily_receipt_counter = current_counter

    # Format the receipt number YYMMDD-XXX (e.g., 250501-001)
    receipt_no = f"{date_part_receipt}-{current_counter:03d}"
    # --- End of Receipt Number Logic ---

    # --- Start building receipt text ---
    receipt_text = f"*🌸 {shop_name} Receipt 🌸*\n\n"
    receipt_text += f"*Date:* {date_display_str}\n" # Use display date here
    receipt_text += f"*Receipt No:* #{receipt_no}\n\n" # Use new receipt number format

    receipt_text += "*Sold to:*\n"
    receipt_text += f"Name: {customer_name}\n"
    receipt_text += f"Address: {customer_address}\n"
    if customer_phone:
        cleaned_phone = re.sub(r'\D', '', customer_phone)
        # Adjust phone number logic if needed (current logic seems fine)
        if cleaned_phone.startswith('0'):
            cleaned_phone = '60' + cleaned_phone[1:]
        elif cleaned_phone.startswith('6') and not cleaned_phone.startswith('60'):
             cleaned_phone = '60' + cleaned_phone[1:]

        if cleaned_phone.startswith('60'):
             receipt_text += f"Phone: {customer_phone}\n"
        else:
             receipt_text += f"Phone: {customer_phone} (Link generation skipped - check format)\n"

    receipt_text += "\n*Item(s) Purchased:*\n"
    item_subtotal = 0
    if items:
        for description, price in items:
            try:
                item_price = float(price)
                receipt_text += f"•  {description}\n"
                receipt_text += f"   Price: {currency}{item_price:.2f}\n"
                item_subtotal += item_price
            except ValueError:
                 receipt_text += f"•  {description}\n"
                 receipt_text += f"   Price: Error - Invalid Price ({price})\n"
    else:
        receipt_text += "(No items added)\n"

    receipt_text += "\n"

    # Delivery charge logic (seems fine)
    delivery_cost = 0.0
    delivery_display = "FOC"
    if isinstance(delivery_charge, str) and delivery_charge.strip().upper() == 'FOC':
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
        except (ValueError, TypeError):
             delivery_cost = 0.0
             delivery_display = "FOC (Invalid Input)"

    receipt_text += f"Delivery Charges: {delivery_display}\n\n"
    total_amount = item_subtotal + delivery_cost
    receipt_text += f"*Total:* {currency} {total_amount:.2f}\n\n"

    receipt_text += "*Payment Method:*\n"
    receipt_text += f"🏦 Bank Transfer: {bank_details}\n\n"
    receipt_text += "Thank you for your purchase! 🌷"

    return receipt_text
# --- End of receipt generation logic ---

# --- Streamlit App Interface ---

st.set_page_config(page_title="Bloomelein Receipt Generator", layout="centered")

st.title("🌸 Bloomelein Receipt 🌸")

# Initialize session state variables if they don't exist
# Ensure daily counter state variables are checked/initialized
if 'last_receipt_date' not in st.session_state: st.session_state.last_receipt_date = None
if 'daily_receipt_counter' not in st.session_state: st.session_state.daily_receipt_counter = 0
# Other state variables
if 'items_list' not in st.session_state: st.session_state.items_list = []
if 'generated_receipt' not in st.session_state: st.session_state.generated_receipt = ""
if 'customer_name' not in st.session_state: st.session_state.customer_name = ""
if 'customer_address' not in st.session_state: st.session_state.customer_address = ""
if 'customer_phone' not in st.session_state: st.session_state.customer_phone = ""
if 'item_desc' not in st.session_state: st.session_state.item_desc = ""
if 'item_price' not in st.session_state: st.session_state.item_price = 0.0
if 'delivery_charge' not in st.session_state: st.session_state.delivery_charge = "FOC"


# --- Callback function for adding items (to fix the previous error) ---
def add_item_callback():
    item_description = st.session_state.item_desc
    item_price_val = st.session_state.item_price

    if item_description and item_price_val > 0:
        st.session_state.items_list.append((item_description, item_price_val))
        # Clear state inside callback
        st.session_state.item_desc = ""
        st.session_state.item_price = 0.0
        # No need for st.success here, page re-runs anyway
    elif not item_description:
        st.warning("Please enter an item description.")
    else:
        st.warning("Please enter a valid price greater than 0.")

# --- Customer Details ---
st.header("Customer Details")
st.text_input("Name:", key="customer_name")
st.text_area("Address:", key="customer_address", height=100)
st.text_input("Phone (Optional, e.g., 012-3456789):", key="customer_phone")

# --- Add Items Section ---
st.header("Add Items")
col1, col2 = st.columns([3, 1])
with col1:
    st.text_input("Item Description:", key="item_desc")
with col2:
    st.number_input("Price (RM):", min_value=0.0, format="%.2f", step=0.10, key="item_price")

# Use the callback for the Add Item button
st.button("➕ Add Item", on_click=add_item_callback)

# --- Display Added Items ---
st.subheader("Current Items in Order:")
if not st.session_state.items_list:
    st.info("No items added yet.")
else:
    items_text_display = ""
    total_items = 0.0 # Calculate subtotal for display here if desired
    for i, (desc, price) in enumerate(st.session_state.items_list):
        items_text_display += f"{i+1}. {desc} - RM{price:.2f}\n"
        total_items += price
    st.text_area(f"Items ({len(st.session_state.items_list)}):", value=items_text_display, height=max(100, len(st.session_state.items_list)*35), disabled=True, key="items_display_area")
    st.text(f"Items Subtotal: RM {total_items:.2f}") # Display subtotal

    # Add a button to remove the LAST item added
    if st.button("➖ Remove Last Item", key="remove_last"):
        if st.session_state.items_list:
            removed = st.session_state.items_list.pop()
            st.session_state.generated_receipt = "" # Clear generated receipt if items change
            st.success(f"Removed: {removed[0]}")
            st.rerun() # Rerun to update display

    if st.button("Clear All Items", key="clear_items"):
         st.session_state.items_list = []
         st.session_state.generated_receipt = "" # Clear generated receipt
         st.rerun()

# --- Delivery Charges ---
st.header("Delivery")
st.text_input("Delivery Charge (RM or 'FOC'):", key="delivery_charge")

# --- Generate Receipt Action ---
st.header("Generate Receipt")
if st.button("📄 Generate Receipt"):
    customer_name_val = st.session_state.customer_name
    customer_address_val = st.session_state.customer_address
    customer_phone_val = st.session_state.customer_phone
    delivery_charge_val = st.session_state.delivery_charge

    if not customer_name_val or not customer_address_val: st.error("Customer Name and Address are required.")
    elif not st.session_state.items_list: st.error("Please add at least one item to the order.")
    else:
        # Call the generation function - it will handle the receipt number logic
        receipt = generate_bloomelein_receipt(
            customer_name=customer_name_val,
            customer_address=customer_address_val,
            items=st.session_state.items_list,
            delivery_charge=delivery_charge_val,
            customer_phone=customer_phone_val if customer_phone_val else None
        )
        st.session_state.generated_receipt = receipt
        st.success(f"Receipt Generated! (No: #{st.session_state.get('last_receipt_date','').replace('-','')[:6]}-{st.session_state.get('daily_receipt_counter',0):03d})") # Show the number generated

# --- Display Generated Receipt & Manual Copy Instruction ---
st.subheader("Generated Receipt Output:")
generated_receipt_text = st.session_state.get("generated_receipt", "")

if generated_receipt_text:
    st.text_area(
        "Receipt Content (Select and Copy Text Below):",
        value=generated_receipt_text,
        height=400,
        key="receipt_output_view",
        help="Click in the box, select all text (Cmd+A or Ctrl+A), then copy (Cmd+C or Ctrl+C)."
    )
    st.info("👆 Select the text above and copy it to paste into WhatsApp or elsewhere.")
else:
    st.text_area(
        "Receipt Content:",
        value="Receipt will appear here once generated...",
        height=400,
        key="receipt_output_placeholder",
        disabled=True
    )

# 1. Define the callback function (place it before the button is created)
def clear_form_callback():
    # Move all state modifications inside the callback
    st.session_state.customer_name = ""
    st.session_state.customer_address = ""
    st.session_state.customer_phone = ""
    st.session_state.item_desc = ""
    st.session_state.item_price = 0.0
    st.session_state.items_list = []
    st.session_state.delivery_charge = "FOC"
    st.session_state.generated_receipt = ""
    # Note: No need to explicitly preserve the counter state here,
    # just don't clear it. st.rerun() is also not needed inside the callback.

# --- (Your other code like Customer Details, Add Items, etc.) ---


# --- Clear Form Button ---
st.divider()
# 2. Attach the callback to the button using on_click
st.button("✨ Start New Receipt (Clear Form)", on_click=clear_form_callback)
# The 'if' block is no longer needed here as the callback handles the action.
# The st.rerun() happens automatically after the callback finishes and
# the script finishes executing.