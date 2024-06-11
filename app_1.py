import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO

class InvoiceGenerator:
    def __init__(self, products):
        self.products = products

    def generate_pdf(self):
        # Create a new PDF with the invoice details
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        col_widths = [7, 100, 20, 20, 20, 20]

        # Add header with color
        headers = ['#', 'Name', 'Price', 'Discount', 'Tax', 'Quantity']
        pdf.set_fill_color(200, 220, 255)  # Light blue color for header
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, border=1, fill=True, align='C')
        pdf.ln()

        # Add product rows with text wrapping
        for index, product in enumerate(self.products, start=1):
            pdf.cell(col_widths[0], 10, str(index), border=1, align='R')
            pdf.cell(col_widths[1], 10, product['name'], border=1)
            for i, key in enumerate(['price', 'discount', 'tax', 'quantity'], 2):
                pdf.cell(col_widths[i], 10, f"{product[key]:.2f}", border=1, align='R')
            pdf.ln()

        # Calculate totals
        total_price = sum(product['price'] * product['quantity'] for product in self.products)
        total_discount = sum(product['discount'] * product['quantity'] for product in self.products)
        total_tax = sum(product['tax'] * product['quantity'] for product in self.products)
        grand_total = total_price - total_discount + total_tax

        # Add totals row
        pdf.ln()
        pdf.set_font("Arial", size=12, style='B')
        pdf.cell(col_widths[0], 10, '', border=0)
        pdf.cell(col_widths[1], 10, 'Total', border=1)
        pdf.cell(col_widths[2], 10, f"{total_price:.2f}", border=1, align='R')
        pdf.cell(col_widths[3], 10, f"{total_discount:.2f}", border=1, align='R')
        pdf.cell(col_widths[4], 10, f"{total_tax:.2f}", border=1, align='R')
        pdf.cell(col_widths[5], 10, f"{grand_total:.2f}", border=1, align='R')

        # Save the invoice PDF to a file-like object
        pdf_output = BytesIO()
        pdf_bytes = pdf.output(dest='S').encode('latin1')
        pdf_output.write(pdf_bytes)
        pdf_output.seek(0)
        return pdf_output.getvalue()

# Streamlit app
st.title("Invoice Generator")

if 'products' not in st.session_state:
    st.session_state.products = []

st.header("Add a Product")

name = st.text_input("Product Name")
price = st.number_input("Price", min_value=0.0)
discount = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, step=0.1)
tax = st.number_input("Tax (%)", min_value=0.0, max_value=100.0, step=0.1)
quantity = st.number_input("Quantity", min_value=1, step=1)

if st.button("Add Product"):
    if name and price and quantity:
        product = {
            'name': name,
            'price': price,
            'discount': discount,
            'tax': tax,
            'quantity': quantity
        }
        st.session_state.products.append(product)
        st.success(f"Added {name}")
    else:
        st.error("Product name, price, and quantity are required")

st.header("Products")
if st.session_state.products:
    df = pd.DataFrame(st.session_state.products)
    st.dataframe(df)
else:
    st.write("No products added yet")

# Generate PDF when button is clicked
if st.button("Generate PDF"):
    if not st.session_state.products:
        st.error("No products to generate a PDF")
    else:
        invoice_generator = InvoiceGenerator(st.session_state.products)
        pdf_content = invoice_generator.generate_pdf()
        st.success("PDF Generated Successfully!")
        st.download_button(
            label="Download PDF",
            data=pdf_content,
            file_name="invoice.pdf",
            mime="application/pdf"
        )
