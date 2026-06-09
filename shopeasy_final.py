import streamlit as st
import pandas as pd
from functools import reduce

st.set_page_config(
    page_title="ShopEasy Sdn.Bhd",
    layout="wide",
)
# Styling (HTML, CSS)
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.brand-header {
    background: linear-gradient(135deg, #1e1e2f 0%, #2d2d44 100%);
    padding: 30px;
    border-radius: 12px;
    margin-bottom: 25px;
    text-align: center;
}

.brand-header h1 {
    color: white;
    margin: 0;
}

.brand-header p {
    color: #d1d5db;
    margin-top: 5px;
}

.section-heading {
    border-bottom: 2px solid #e5e7eb;
    padding-bottom: 8px;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# Core Datasets
@st.cache_data
def load_data():

    catalog = [
        ("Premium Jasmine Rice 5kg", "Groceries", 28.50, 45),
        ("Cooking Oil 2kg", "Groceries", 14.20, 12),
        ("Organic Whole Milk 1L", "Groceries", 7.90, 8),
        ("Wireless Mouse", "Electronics", 45.00, 22),
        ("Mechanical Keyboard", "Electronics", 120.00, 15),
        ("Bluetooth Earbuds", "Electronics", 85.00, 5),
        ("Oversized Cotton T-Shirt", "Clothing", 25.00, 40),
        ("Denim Jeans", "Clothing", 79.00, 14),
        ("Scented Candle", "Home & Living", 18.50, 30),
        ("LED Desk Lamp", "Home & Living", 45.00, 11),
        ("Hydrating Sunscreen", "Health & Beauty", 35.00, 25),
        ("Lip Balm", "Health & Beauty", 8.50, 19),
        ("Local Cavendish Bananas", "Fresh Produce", 5.90, 18),
        ("Premium Fuji Apples (5pc)", "Fresh Produce", 9.90, 24),
        ("Wholemeal Sliced Bread", "Bakery", 4.20, 35),
        ("Butter Croissants (4pc)", "Bakery", 12.00, 7),
        ("Ipoh White Coffee Mix", "Beverages", 15.50, 50),
        ("Organic Green Tea Bags", "Beverages", 11.90, 16),
        ("Potato Chips BBQ 150g", "Snacks", 4.80, 60),
        ("Roasted Almonds 200g", "Snacks", 14.50, 9),
        ("Eco Baby Wipes 80s", "Baby Care", 9.50, 42),
        ("Ultra Dry Diapers M-Size", "Baby Care", 43.90, 6)
    ]

    sales_records = []

    dates = pd.date_range(
        start="2026-01-01",
        periods=88,
        freq="D"
    ).date

    for i in range(88):

        product, category, price, stock = catalog[i % len(catalog)]

        qty = (i % 5) + 1

        sales_records.append({
            "Product": product,
            "Category": category,
            "Qty": qty,
            "Price": price,
            "Date": dates[i],
            "Revenue": qty * price
        })

    df_sales = pd.DataFrame(sales_records)

    df_inventory = pd.DataFrame([
        {
            "Product": item[0],
            "Category": item[1],
            "Stock": item[3]
        }
        for item in catalog
    ])

    return df_sales, df_inventory


# Filtering Functions [def()]
def apply_filters(df_sales, df_inventory, category, dates):

    filtered_sales = df_sales.copy()
    filtered_inventory = df_inventory.copy()

    if category != "All Categories":

        filtered_sales = filtered_sales[
            filtered_sales["Category"] == category
        ]

        filtered_inventory = filtered_inventory[
            filtered_inventory["Category"] == category
        ]

    if len(dates) == 2:

        start_date, end_date = dates

        filtered_sales = filtered_sales[
            filtered_sales["Date"].between(
                start_date,
                end_date
            )
        ]

    return filtered_sales, filtered_inventory


# Dashboard
def display_metrics(df):

    revenue = df["Revenue"].sum()
    units = df["Qty"].sum()
    avg_price = df["Price"].mean()

# Columns = col1, col2, col3
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Gross Revenue",
        f"RM {revenue:,.2f}"
    )

    col2.metric(
        "Units Sold",
        f"{units:,}"
    )

    col3.metric(
        "Average Price",
        f"RM {avg_price:,.2f}"
    )

def display_sales_charts(df):

    col1, col2 = st.columns(2)

    with col1:
        st.write("Revenue by Category")
        st.bar_chart(
            df.groupby("Category")["Revenue"].sum()
        )

    with col2:
        st.write("Daily Revenue Trend")
        st.line_chart(
            df.groupby("Date")["Revenue"].sum()
        )

    st.write("Price vs Quantity Sold")

    st.scatter_chart(
        data=df,
        x="Price",
        y="Qty",
        color="Category"
    )

def inventory_analysis(df_inventory, threshold):

    inventory_records = df_inventory.to_dict("records")

    low_stock = list(
        filter(
            lambda item: item["Stock"] < threshold,
            inventory_records
        )
    )

    total_stock = reduce(
        lambda total, item: total + item["Stock"],
        low_stock,
        0
    )

    return low_stock, total_stock

def show_inventory_alert(low_stock, total_stock):

    if low_stock:

        st.warning(
            f"{len(low_stock)} products are below "
            f"the threshold. "
            f"Remaining units: {total_stock}"
        )

        with st.expander("View Low Stock Products"):

            for item in low_stock:

                st.write(
                    f"🟥 {item['Product']} "
                    f"({item['Stock']} units)"
                )

    else:

        st.success(
            "All products are safe."
        )

def display_inventory_table(df_inventory, threshold):

    styled_table = df_inventory.style.apply(
        lambda row: [
            "background-color:#D12828"
            if row["Stock"] < threshold
            else "background-color:#10943C"
        ] * len(row),
        axis=1
    )

    st.dataframe(
        styled_table,
        use_container_width=True
    )

# Sales Dashboard
def sales_dashboard(df_sales):

    st.markdown(
        '<h2 class="section-heading">Sales Dashboard</h2>',
        unsafe_allow_html=True
    )

    display_metrics(df_sales)

    st.subheader("Sales Records")

    st.dataframe(
        df_sales,
        use_container_width=True
    )

    display_sales_charts(df_sales)

# Inventory
def inventory_dashboard(df_inventory, df_sales):

    st.markdown(
        '<h2 class="section-heading">Inventory Dashboard</h2>',
        unsafe_allow_html=True
    )

    threshold = st.slider(
        "Safety Stock Threshold",
        5,
        30,
        20
    )

    low_stock, total_stock = inventory_analysis(
        df_inventory,
        threshold
    )

    show_inventory_alert(
        low_stock,
        total_stock
    )

    st.subheader("Inventory Status")

    display_inventory_table(
        df_inventory,
        threshold
    )

    st.markdown("---")

    st.subheader("Operational Summary")

    display_metrics(df_sales)

# Main
df_sales, df_inventory = load_data()

st.markdown("""
<div class="brand-header">
    <h1>🛒 ShopEasy Sdn.Bhd</h1>
    <p>Sales & Inventory Monitoring</p>
</div>
""", unsafe_allow_html=True)

# Sidebar Controls

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Choose your page:",
    [
        "📈 Sales Overview",
        "📦 Inventory Dashboard",
    ]
)

category_filter = st.sidebar.selectbox(
    "Category Filter",
    ["All Categories"] +
    list(df_inventory["Category"].unique())
)

date_filter = st.sidebar.date_input(
    "Date Range",
    [
        df_sales["Date"].min(),
        df_sales["Date"].max()
    ]
)

# Apply Filters
df_sales, df_inventory = apply_filters(
    df_sales,
    df_inventory,
    category_filter,
    date_filter
)

# Page Routing
if page == "📈 Sales Overview":

    sales_dashboard(df_sales)

else:

    inventory_dashboard(
        df_inventory,
        df_sales
    )