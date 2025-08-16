import streamlit as st
import sqlite3
from datetime import date

conn = sqlite3.connect('ecommerce.db')
c = conn.cursor()

# Create tables if not exist
c.execute('''CREATE TABLE IF NOT EXISTS Customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, email TEXT, city TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS Products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, price REAL, stock INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS Orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER, product_id INTEGER, quantity INTEGER, order_date DATE,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id))''')

st.title("🛍️ E-Commerce Management System")

tab1, tab2, tab3 = st.tabs(["Add Customer", "Add Product", "Place Order"])

with tab1:
    st.subheader("Add New Customer")
    name = st.text_input("Name")
    email = st.text_input("Email")
    city = st.text_input("City")
    if st.button("Add Customer"):
        c.execute("INSERT INTO Customers (name, email, city) VALUES (?, ?, ?)", (name, email, city))
        conn.commit()
        st.success("Customer added!")

with tab2:
    st.subheader("Add New Product")
    pname = st.text_input("Product Name")
    price = st.number_input("Price", min_value=0.0)
    stock = st.number_input("Stock", min_value=0)
    if st.button("Add Product"):
        c.execute("INSERT INTO Products (name, price, stock) VALUES (?, ?, ?)", (pname, price, stock))
        conn.commit()
        st.success("Product added!")

with tab3:
    st.subheader("Place Order")
    customers = c.execute("SELECT customer_id, name FROM Customers").fetchall()
    products = c.execute("SELECT product_id, name FROM Products").fetchall()

    cust = st.selectbox("Select Customer", customers, format_func=lambda x: f"{x[0]} - {x[1]}")
    prod = st.selectbox("Select Product", products, format_func=lambda x: f"{x[0]} - {x[1]}")
    qty = st.number_input("Quantity", min_value=1)
    if st.button("Place Order"):
        c.execute("INSERT INTO Orders (customer_id, product_id, quantity, order_date) VALUES (?, ?, ?, ?)",
                  (cust[0], prod[0], qty, date.today()))
        c.execute("UPDATE Products SET stock = stock - ? WHERE product_id = ?", (qty, prod[0]))
        conn.commit()
        st.success("Order placed!")
