import streamlit as st
import pandas as pd
import sqlite3

# --- DB Setup ---
def init_db():
    conn = sqlite3.connect("ecommerce.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            image TEXT
        )
    """)
    conn.commit()
    return conn

conn = init_db()

# --- CRUD Functions ---
def add_product(name, price, stock, image):
    conn.execute("INSERT INTO products (name, price, stock, image) VALUES (?, ?, ?, ?)",
                 (name, price, stock, image))
    conn.commit()

def get_products():
    return pd.read_sql("SELECT * FROM products", conn)

def update_product(id, name, price, stock, image):
    conn.execute("UPDATE products SET name=?, price=?, stock=?, image=? WHERE id=?",
                 (name, price, stock, image, id))
    conn.commit()

def delete_product(id):
    conn.execute("DELETE FROM products WHERE id=?", (id,))
    conn.commit()

# --- UI ---
st.set_page_config(layout="wide")
st.title("🛍️ E-Commerce Product Manager")

tab1, tab2, tab3 = st.tabs(["📦 View Products", "➕ Add Product", "🛠️ Update/Delete"])

with tab1:
    df = get_products()
    if not df.empty:
        st.dataframe(df)
    else:
        st.info("No products found. Add some to get started!")

with tab2:
    st.subheader("Add New Product")
    name = st.text_input("Product Name")
    price = st.number_input("Price (₹)", min_value=0.0, format="%.2f")
    stock = st.number_input("Stock", min_value=0, step=1)
    image = st.text_input("Image URL (optional)")
    if st.button("Add Product"):
        if name:
            add_product(name, price, stock, image)
            st.success(f"✅ '{name}' added successfully!")
        else:
            st.error("Product name is required.")

with tab3:
    st.subheader("Update or Delete Product")
    df = get_products()
    if not df.empty:
        selected_id = st.selectbox("Select Product ID", df["id"])
        selected_row = df[df["id"] == selected_id].iloc[0]
        new_name = st.text_input("Name", selected_row["name"])
        new_price = st.number_input("Price", value=selected_row["price"], format="%.2f")
        new_stock = st.number_input("Stock", value=selected_row["stock"], step=1)
        new_image = st.text_input("Image URL", selected_row["image"])

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Update Product"):
                update_product(selected_id, new_name, new_price, new_stock, new_image)
                st.success("✅ Product updated.")
        with col2:
            if st.button("Delete Product"):
                delete_product(selected_id)
                st.warning("🗑️ Product deleted.")
    else:
        st.info("No products to manage.")
