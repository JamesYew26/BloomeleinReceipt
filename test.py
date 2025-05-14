import streamlit as st
from streamlit_gsheets import GSheetsConnection

conn = st.connection("gsheets", type=GSheetsConnection)

data = conn.read(worksheet="Receipt")
st.dataframe(data)

# st.subheader("Receipt check")
# sql = '''
# SELECT *
#     "ReceiptNo",
#     "CustName",
#     "PhoneNo",
#     "CustAddress",
#     "Item",
#     "Price"
# FROM
#     Receipt
# '''
# df_receipt = conn.query(sql=sql)
# st.dataframe(df_receipt)
