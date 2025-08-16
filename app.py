import streamlit as st
import pandas as pd
import sqlite3

# --- DB Setup ---
def init_db():
    conn = sqlite3.connect("ecommerce.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    """)
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
def add_customer(name, email):
    conn.execute("INSERT INTO customers (name, email) VALUES (?, ?)", (name, email))
    conn.commit()

def get_customers():
    return pd.read_sql("SELECT * FROM customers", conn)

def add_product(name, price, stock, image):
    conn.execute("INSERT INTO products (name, price, stock, image) VALUES (?, ?, ?, ?)",
                 (name, price, stock, image))
    conn.commit()

def get_products():
    return pd.read_sql("SELECT * FROM products", conn)

def get_product_by_id(pid):
    return pd.read_sql(f"SELECT * FROM products WHERE id={pid}", conn).iloc[0]

# --- Session State Setup ---
if "cart" not in st.session_state:
    st.session_state.cart = []

if "customer_id" not in st.session_state:
    st.session_state.customer_id = None

# --- UI ---
st.set_page_config(layout="wide")
st.title("🛍️ E-Commerce App with Customer & Cart")

tab1, tab2, tab3, tab4 = st.tabs(["👤 Register/Login", "🛒 Shop", "📦 Cart", "➕ Add Product"])

# --- Customer Registration/Login ---
with tab1:
    st.subheader("Customer Login / Registration")
    customers_df = get_customers()
    customer_email = st.text_input("Enter your email")
    customer_name = st.text_input("Enter your name (if new)")
    if st.button("Login / Register"):
        if customer_email:
            existing = customers_df[customers_df["email"] == customer_email]
            if not existing.empty:
                st.session_state.customer_id = existing.iloc[0]["id"]
                st.success(f"Welcome back, {existing.iloc[0]['name']}!")
            elif customer_name:
                add_customer(customer_name, customer_email)
                st.session_state.customer_id = get_customers().query("email == @customer_email").iloc[0]["id"]
                st.success(f"Registered and logged in as {customer_name}")
            else:
                st.error("Please enter your name to register.")
        else:
            st.error("Email is required.")

# --- Product Shopping ---
with tab2:
    st.subheader("Browse Products")
    if st.session_state.customer_id:
        products_df = get_products()
        cols = st.columns(3)
        for i, row in products_df.iterrows():
            with cols[i % 3]:
                st.image(row["image"], use_column_width=True)
                st.markdown(f"**{row['name']}**")
                st.write(f"💰 ₹{row['price']} | 📦 Stock: {row['stock']}")
                if st.button(f"Add to Cart", key=f"cart_{row['id']}"):
                    st.session_state.cart.append(row["id"])
                    st.success(f"Added {row['name']} to cart!")
    else:
        st.warning("Please log in to start shopping.")

# --- Cart View ---
with tab3:
    st.subheader("Your Cart")
    if st.session_state.customer_id:
        if st.session_state.cart:
            cart_items = [get_product_by_id(pid) for pid in st.session_state.cart]
            total = 0
            for item in cart_items:
                st.image(item["image"], width=100)
                st.write(f"**{item['name']}** - ₹{item['price']}")
                total += item["price"]
            st.markdown(f"### 🧾 Total: ₹{total}")
            if st.button("Checkout"):
                st.success("🛍️ Order placed successfully!")
                st.session_state.cart = []
        else:
            st.info("Your cart is empty.")
    else:
        st.warning("Please log in to view your cart.")

# --- Product Admin ---
with tab4:
    st.subheader("Add New Product")
    name = st.text_input("Product Name")
    price = st.number_input("Price (₹)", min_value=0.0, format="%.2f")
    stock = st.number_input("Stock", min_value=0, step=1)
    image = st.text_input("Image URL")
    if st.button("Add Product"):
        if name:
            add_product(name, price, stock, image)
            st.success(f"✅ '{name}' added successfully!")
        else:
            st.error("Product name is required.")
