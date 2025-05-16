import streamlit as st
import datetime
import re

# --- Configuration ---

# Delivery Options Configuration
DELIVERY_OPTIONS = {
    "Self pickup (SGL)": {"charge_input_enabled": False, "requires_address": False, "base_charge": 0.0},
    "Self pickup (MKT)": {"charge_input_enabled": False, "requires_address": False, "base_charge": 0.0},
    "FOC Delivery": {"charge_input_enabled": False, "requires_address": True, "base_charge": 0.0},
    "Delivery (Grab/Lalamove)": {"charge_input_enabled": True, "requires_address": True, "base_charge": None}, # None means user inputs
    "Delivery": {"charge_input_enabled": True, "requires_address": True, "base_charge": None} # None means user inputs
}
DEFAULT_DELIVERY_OPTION_KEY = "FOC Delivery" # Default delivery option

# PIC Options Configuration
PIC_OPTIONS = ["LEE JIA YIN", "KAREN KONG KAR YAN", "YEW JUN CHEE"]
DEFAULT_PIC = PIC_OPTIONS[0] # Default to the first PIC

# Payment Method Options
PAYMENT_METHOD_OPTIONS = ["TnG", "Bank Account", "Others"]
DEFAULT_PAYMENT_METHOD = PAYMENT_METHOD_OPTIONS[0] # Default to TnG

# --- Receipt Generation Logic ---
# (This function remains the same, but you could add 'selected_pic' as an argument
#  if you want to include it in the receipt text later)
def generate_bloomelein_receipt(customer_name, customer_address, items,
                                delivery_method_description, delivery_cost_numeric,
                                customer_phone, pic_name=""): # Added pic_name, defaults to empty
    """
    Generates a formatted receipt string for Bloomelein florist shop.
    """
    shop_name = "Bloomelein"
    currency = "RM"

    now = datetime.datetime.now()
    current_date_obj = now.date()
    current_date_str_compare = current_date_obj.strftime("%Y-%m-%d")
    date_part_receipt = current_date_obj.strftime("%y%m%d")
    date_str = now.strftime("%B %d, %Y")

    last_receipt_date_in_state = st.session_state.get("last_receipt_date", None)
    daily_counter_in_state = st.session_state.get("daily_receipt_counter", 0)

    if current_date_str_compare != last_receipt_date_in_state:
        current_receipt_sequence = 1
        st.session_state.last_receipt_date = current_date_str_compare
        st.session_state.daily_receipt_counter = current_receipt_sequence
    else:
        current_receipt_sequence = daily_counter_in_state + 1
        st.session_state.daily_receipt_counter = current_receipt_sequence

    receipt_no = f"{date_part_receipt}-{current_receipt_sequence:03d}"

    receipt_text = f"*🌸 {shop_name} Receipt 🌸*\n\n"
    receipt_text += f"*Date:* {date_str}\n"
    receipt_text += f"*Receipt No:* #{receipt_no}\n\n"

    receipt_text += "*Sold to:*\n"
    receipt_text += f"Name: {customer_name}\n"

    if customer_address:
        receipt_text += f"Address: {customer_address}\n"

    cleaned_phone = re.sub(r'\D', '', customer_phone)
    if cleaned_phone.startswith('0'):
        cleaned_phone = '60' + cleaned_phone[1:]
    elif cleaned_phone.startswith('6') and not cleaned_phone.startswith('60'):
         cleaned_phone = '60' + cleaned_phone[1:]

    if cleaned_phone.startswith('60'):
         receipt_text += f"Phone: {customer_phone}\n"
    else:
         receipt_text += f"Phone: {customer_phone} (Link generation failed - check format)\n"

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

    receipt_text += f"*Delivery Method:* {delivery_method_description}\n"
    if delivery_cost_numeric > 0:
        receipt_text += f"Delivery Charges: {currency}{delivery_cost_numeric:.2f}\n\n"
    elif delivery_method_description not in ["Self pickup (SGL)", "Self pickup (MKT)"]:
        receipt_text += f"Delivery Charges: FOC\n\n"
    else:
        receipt_text += "\n"

    total_amount = item_subtotal + delivery_cost_numeric
    receipt_text += f"*Total:* {currency} {total_amount:.2f}\n"
    receipt_text += f"*Paid to:* {pic_name}\n\n"
    receipt_text += "Thank you for your purchase! 🌷"
    return receipt_text


# --- Streamlit App Interface ---

st.set_page_config(page_title="Bloomelein Receipt Generator", layout="centered")
st.title("Bloomelein 🌸")

# Initialize session state variables
if 'items_list' not in st.session_state: st.session_state.items_list = []
if 'generated_receipt' not in st.session_state: st.session_state.generated_receipt = ""
if 'selected_delivery_option' not in st.session_state: st.session_state.selected_delivery_option = DEFAULT_DELIVERY_OPTION_KEY
if 'delivery_charge_input' not in st.session_state: st.session_state.delivery_charge_input = 0.0
if 'last_receipt_date' not in st.session_state: st.session_state.last_receipt_date = None
if 'daily_receipt_counter' not in st.session_state: st.session_state.daily_receipt_counter = 0
if 'item_desc' not in st.session_state: st.session_state.item_desc = ""
if 'item_price' not in st.session_state: st.session_state.item_price = 0.0
if 'customer_name' not in st.session_state: st.session_state.customer_name = ""
if 'customer_address' not in st.session_state: st.session_state.customer_address = ""
if 'customer_phone' not in st.session_state: st.session_state.customer_phone = ""
# NEW: Initialize selected_pic
if 'selected_pic' not in st.session_state: st.session_state.selected_pic = DEFAULT_PIC


# --- Callback for Add Item Button ---
def add_item_callback():
    item_description_val = st.session_state.item_desc
    item_price_val = st.session_state.item_price
    if item_description_val and item_price_val > 0:
        st.session_state.items_list.append((item_description_val, item_price_val))
        st.session_state.item_desc = ""
        st.session_state.item_price = 0.0
        st.success(f"Added: {item_description_val}")
    elif not item_description_val: st.warning("Please enter an item description.")
    else: st.warning("Please enter a valid price greater than 0.")

# --- Callback for Clear Form Button ---
def clear_form_callback():
    st.session_state.customer_name = ""
    st.session_state.customer_address = ""
    st.session_state.customer_phone = ""
    st.session_state.item_desc = ""
    st.session_state.item_price = 0.0
    st.session_state.items_list = []
    st.session_state.generated_receipt = ""
    st.session_state.selected_delivery_option = DEFAULT_DELIVERY_OPTION_KEY
    st.session_state.delivery_charge_input = 0.0
    st.session_state.selected_pic = DEFAULT_PIC # Reset PIC to default

# --- NEW: PIC Selection ---
st.selectbox(
    "Select Person In Charge (PIC):",
    options=PIC_OPTIONS,
    key="selected_pic" # This will directly update st.session_state.selected_pic
)
st.divider() # Optional: add a visual separator

# --- Customer Details ---
st.header("Customer Details")
st.text_input("Name:", key="customer_name")

selected_delivery_option_val = st.session_state.selected_delivery_option
selected_delivery_properties = DELIVERY_OPTIONS[selected_delivery_option_val]
address_label = "Address:"
if selected_delivery_properties["requires_address"]:
    address_label = "Address: (Required for Delivery)"
else:
    address_label = "Address: (Optional for Self Pickup)"
st.text_area(address_label, key="customer_address", height=100)
st.text_input("Phone (Required, e.g., 012-3456789 or 60123456789):", key="customer_phone")

# --- Add Items Section ---
st.header("Add Items")
col1, col2 = st.columns([3, 1])
with col1: st.text_input("Item Description:", key="item_desc")
with col2: st.number_input("Price (RM):", min_value=0.0, format="%.2f", step=0.10, key="item_price")
st.button("➕ Add Item", on_click=add_item_callback)

# --- Display Added Items ---
st.subheader("Current Items in Order:")
if not st.session_state.items_list: st.info("No items added yet.")
else:
    items_text_display = ""
    for i, (desc, price) in enumerate(st.session_state.items_list):
        items_text_display += f"{i+1}. {desc} - RM{price:.2f}\n"
    st.text_area("Items:", value=items_text_display, height=max(100, len(st.session_state.items_list)*35), disabled=True, key="items_display_area_disabled")
    if st.button("Clear All Items", key="clear_items_button"):
         st.session_state.items_list = []
         st.rerun()

# --- Delivery Options ---
st.header("Delivery Method")
delivery_options_keys = list(DELIVERY_OPTIONS.keys())
st.selectbox(
    "Choose Delivery Option:",
    options=delivery_options_keys,
    key="selected_delivery_option"
)
current_delivery_config = DELIVERY_OPTIONS[st.session_state.selected_delivery_option]
actual_delivery_charge = 0.0
if current_delivery_config["charge_input_enabled"]:
    st.number_input(
        "Delivery Charge (RM):",
        min_value=0.0,
        format="%.2f",
        step=0.10,
        key="delivery_charge_input"
    )
    actual_delivery_charge = float(st.session_state.delivery_charge_input)
    if actual_delivery_charge < 0:
        st.warning("Delivery charge cannot be negative. Setting to RM0.00.")
        actual_delivery_charge = 0.0
        st.session_state.delivery_charge_input = 0.0
else:
    if st.session_state.selected_delivery_option in ["Self pickup (SGL)", "Self pickup (MKT)"]:
         st.info(f"{st.session_state.selected_delivery_option} selected. No delivery charge.")
    else:
         st.info(f"{st.session_state.selected_delivery_option} selected. Delivery charge is RM0.00.")
    actual_delivery_charge = 0.0
    if st.session_state.delivery_charge_input != 0.0:
        st.session_state.delivery_charge_input = 0.0

# --- NEW: Payment Method Section ---
st.header("Payment Method")
st.radio(
    "Select Payment Method:",
    options=PAYMENT_METHOD_OPTIONS,
    key="selected_payment_method",
    horizontal=True # Display radio buttons horizontally
)

# Conditionally display text input if "Others" is selected
if st.session_state.selected_payment_method == "Others":
    st.text_input(
        "Please specify other payment method:",
        key="other_payment_method_text"
    )

# --- Generate Receipt Action ---
st.header("Generate & Copy Receipt")
if st.button("📄 Generate Receipt"):
    customer_name_val = st.session_state.customer_name
    customer_address_val = st.session_state.customer_address
    customer_phone_val = st.session_state.customer_phone
    errors = []
    if not customer_name_val: errors.append("Customer Name is required.")
    if not customer_phone_val: errors.append("Customer Phone is required.")
    else:
        cleaned_phone_for_validation = re.sub(r'\D', '', customer_phone_val)
        if not ( (cleaned_phone_for_validation.startswith('0') and len(cleaned_phone_for_validation) >= 10) or \
                 (cleaned_phone_for_validation.startswith('60') and len(cleaned_phone_for_validation) >= 11) ):
            errors.append("Please enter a valid Malaysian phone number (e.g., 012-3456789 or 60123456789).")
    if current_delivery_config["requires_address"] and not customer_address_val:
        errors.append(f"Customer Address is required for {st.session_state.selected_delivery_option}.")
    if not st.session_state.items_list: errors.append("Please add at least one item to the order.")

    if errors:
        for error in errors: st.error(error)
    else:
        receipt = generate_bloomelein_receipt( # Pass selected_pic to the function
            customer_name=customer_name_val,
            customer_address=customer_address_val,
            items=st.session_state.items_list,
            delivery_method_description=st.session_state.selected_delivery_option,
            delivery_cost_numeric=float(actual_delivery_charge),
            customer_phone=customer_phone_val,
            pic_name=st.session_state.selected_pic # Pass the selected PIC
        )
        st.session_state.generated_receipt = receipt
        st.success("Receipt Generated!")

# --- Display Generated Receipt & Copy Option ---
st.subheader("Generated Receipt Output:")
st.text_area(
    "Receipt Content:",
    value=st.session_state.generated_receipt,
    height=400,
    key="receipt_output_display",
    help="You can select and copy the text from this box.",
    disabled=True
)

# --- Clear Form Button ---
if st.session_state.generated_receipt: # Only show if a receipt was generated
    st.info("Select the text above and copy (Cmd+C or Ctrl+C) to paste into WhatsApp.")

# Always show the clear form button for better UX
st.button("✨ Start New Receipt (Clear Form)", on_click=clear_form_callback)