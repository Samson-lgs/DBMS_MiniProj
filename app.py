import streamlit as st
import pandas as pd
import sqlite3

# --- DB Setup ---
conn = sqlite3.connect("ecommerce.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL
)
""")
conn.commit()

# --- Helper Functions ---
def get_products():
    return pd.read_sql("SELECT * FROM products", conn)

def add_product(name, price, stock):
    cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
    conn.commit()

def update_product(id, name, price, stock):
    cursor.execute("UPDATE products SET name=?, price=?, stock=? WHERE id=?", (name, price, stock, id))
    conn.commit()

def delete_product(id):
    cursor.execute("DELETE FROM products WHERE id=?", (id,))
    conn.commit()

# --- UI ---
st.title("🛍️ E-Commerce Dashboard")

tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "➕ Add Product", "🛠️ Manage Products"])

with tab1:
    df = get_products()
    if not df.empty:
        st.metric("Total Products", len(df))
        st.metric("Total Stock", df["stock"].sum())
        st.dataframe(df)
    else:
        st.warning("No products found. Add some to get started!")

with tab2:
    st.subheader("Add New Product")
    name = st.text_input("Product Name")
    price = st.number_input("Price", min_value=0.0, format="%.2f")
    stock = st.number_input("Stock", min_value=0, step=1)
    if st.button("Add Product"):
        if name:
            add_product(name, price, stock)
            st.success(f"Product '{name}' added!")
        else:
            st.error("Product name is required.")

with tab3:
    st.subheader("Update or Delete Products")
    df = get_products()
    if not df.empty:
        selected_id = st.selectbox("Select Product ID", df["id"])
        selected_row = df[df["id"] == selected_id].iloc[0]
        new_name = st.text_input("Name", selected_row["name"])
        new_price = st.number_input("Price", value=selected_row["price"], format="%.2f")
        new_stock = st.number_input("Stock", value=selected_row["stock"], step=1)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Update"):
                update_product(selected_id, new_name, new_price, new_stock)
                st.success("Product updated.")
        with col2:
            if st.button("Delete"):
                delete_product(selected_id)
                st.warning("Product deleted.")
    else:
        st.info("No products to manage.")
