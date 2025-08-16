import streamlit as st
import pandas as pd
import sqlite3

DB_PATH = "ecommerce.db"

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            product TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_customer(name, email, product):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO customers (name, email, product) VALUES (?, ?, ?)", (name, email, product))
    conn.commit()
    conn.close()

def fetch_customers():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM customers", conn)
    conn.close()
    return df

def delete_customer(customer_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
    conn.commit()
    conn.close()

def update_customer(customer_id, name, email, product):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE customers
        SET name = ?, email = ?, product = ?
        WHERE id = ?
    """, (name, email, product, customer_id))
    conn.commit()
    conn.close()

# --- UI Setup ---
st.set_page_config(page_title="Customer Management", layout="wide")
init_db()

st.sidebar.title("🔧 System Controls")
section = st.sidebar.radio("Go to", ["Dashboard", "Add", "Update", "Delete"])

# --- Dashboard ---
if section == "Dashboard":
    st.title("📊 Customer Dashboard")
    df = fetch_customers()
    st.metric("Total Customers", len(df))
    st.metric("Unique Products", df["product"].nunique())
    st.subheader("📁 All Customers")
    st.dataframe(df)

# --- Add Customer ---
elif section == "Add":
    st.title("➕ Add New Customer")
    with st.form("add_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        product = st.text_input("Product")
        submitted = st.form_submit_button("Add")
        if submitted:
            insert_customer(name, email, product)
            st.success("✅ Customer added!")

# --- Update Customer ---
elif section == "Update":
    st.title("✏️ Update Customer")
    df = fetch_customers()
    customer_ids = df["id"].tolist()
    selected_id = st.selectbox("Select Customer ID", customer_ids)
    selected_row = df[df["id"] == selected_id].iloc[0]

    with st.form("update_form"):
        name = st.text_input("Name", selected_row["name"])
        email = st.text_input("Email", selected_row["email"])
        product = st.text_input("Product", selected_row["product"])
        updated = st.form_submit_button("Update")
        if updated:
            update_customer(selected_id, name, email, product)
            st.success("✅ Customer updated!")

# --- Delete Customer ---
elif section == "Delete":
    st.title("🗑️ Delete Customer")
    df = fetch_customers()
    customer_ids = df["id"].tolist()
    selected_id = st.selectbox("Select Customer ID to Delete", customer_ids)
    selected_row = df[df["id"] == selected_id].iloc[0]
    st.write(f"Name: {selected_row['name']}, Email: {selected_row['email']}, Product: {selected_row['product']}")
    if st.button("Delete"):
        delete_customer(selected_id)
        st.warning("⚠️ Customer deleted!")

