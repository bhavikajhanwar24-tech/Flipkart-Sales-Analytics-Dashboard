from utils import load_data, clean_data, add_features, compute_kpis, generate_insights

import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Flipkart Dashboard", layout="wide")

st.markdown("""
    <style>
        .main {
            background-color: #f5f7fa;
        }
        .stMetric {
            background-color: white;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0px 3px 10px rgba(0,0,0,0.08);
        }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load():
    return load_data("data/flipkart_com-ecommerce_sample.csv")

df = load()
df = clean_data(df)
df = add_features(df)

st.sidebar.title("🔍 Advanced Filters")

category = st.sidebar.selectbox(
    "📦 Category",
    ["All"] + sorted(df['main_category'].dropna().unique())
)

price_range = st.sidebar.slider(
    "💰 Price Range",
    int(df['retail_price'].min()),
    int(df['retail_price'].max()),
    (int(df['retail_price'].min()), int(df['retail_price'].max()))
)

rating_filter = st.sidebar.slider("⭐ Minimum Rating", 0.0, 5.0, 0.0)
discount_filter = st.sidebar.slider("🔥 Minimum Discount %", 0, 100, 0)

sort_option = st.sidebar.selectbox(
    "📊 Sort By",
    ["Price Low to High", "Price High to Low", "Rating"]
)

filtered_df = df.copy()

if category != "All":
    filtered_df = filtered_df[filtered_df['main_category'] == category]

filtered_df = filtered_df[
    filtered_df['retail_price'].between(price_range[0], price_range[1])
]

if rating_filter > 0:
    filtered_df = filtered_df[
        filtered_df['product_rating'] >= rating_filter
    ]

if discount_filter > 0:
    filtered_df = filtered_df[
        filtered_df['discount_percent'] >= discount_filter
    ]

search = st.text_input("🔍 Search Product (e.g., shirt, mobile)")

if search:
    keywords = search.lower().split()
    for word in keywords:
        filtered_df = filtered_df[
            filtered_df['product_name']
            .str.lower()
            .str.contains(word, na=False)
        ]

if sort_option == "Price Low to High":
    filtered_df = filtered_df.sort_values(by='retail_price')
elif sort_option == "Price High to Low":
    filtered_df = filtered_df.sort_values(by='retail_price', ascending=False)
else:
    filtered_df = filtered_df.sort_values(by='product_rating', ascending=False)

st.title("🛒 Flipkart Sales Analytics Dashboard")
st.write(f"🔍 Showing {len(filtered_df)} products out of {len(df)}")

kpis = compute_kpis(filtered_df)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Products", kpis["total_products"])
col2.metric("Avg Price", kpis["avg_price"])
col3.metric("Avg Rating", kpis["avg_rating"])
col4.metric("Avg Discount %", kpis["avg_discount"])

tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Analysis", "🧠 Insights"])

with tab1:

    st.subheader("🖼 Sample Products")
    cols = st.columns(5)


    @st.cache_data
    def get_top_products(df):
        return df.head(5)


    top_products = get_top_products(filtered_df)

    cols = st.columns(5)

    for idx, (_, row) in enumerate(top_products.iterrows()):
        with cols[idx]:
            try:
                img = row['image_url']

                if not img or not isinstance(img, str) or not img.startswith("http"):
                    img = PLACEHOLDER

                st.image(img, use_container_width=True)

            except:
                st.image(PLACEHOLDER, use_container_width=True)

            st.caption(row['product_name'][:40])

    st.subheader("📊 Price Distribution")
    st.plotly_chart(px.histogram(filtered_df, x="retail_price"), use_container_width=True)

    st.subheader("⭐ Rating Distribution")
    st.plotly_chart(px.histogram(filtered_df, x="product_rating"), use_container_width=True)

with tab2:

    st.subheader("🏷 Category vs Avg Price")
    cat_price = df.groupby('main_category')['retail_price'].mean().sort_values(ascending=False)

    st.plotly_chart(px.line(x=cat_price.index, y=cat_price.values, markers=True), use_container_width=True)

    st.subheader("📦 Category Share")
    cat_count = df['main_category'].value_counts()

    st.plotly_chart(px.pie(values=cat_count.values, names=cat_count.index, hole=0.4), use_container_width=True)

    st.subheader("💰 Price vs Discount")
    st.plotly_chart(px.scatter(filtered_df, x="retail_price", y="discount_percent"), use_container_width=True)

    st.subheader("📈 Correlation Heatmap")
    corr = filtered_df[['retail_price', 'discounted_price', 'product_rating', 'discount_percent']].corr()
    st.plotly_chart(px.imshow(corr, text_auto=True), use_container_width=True)

with tab3:

    st.subheader("🧠 Insights")
    insights = generate_insights(filtered_df)
    for insight in insights:
        st.write(insight)

    st.subheader("🔥 Top Products")
    top_products = filtered_df.sort_values(by="product_rating", ascending=False).head(10)

    st.dataframe(top_products[['product_name', 'retail_price', 'product_rating']])

    st.download_button(
        label="⬇ Download Data",
        data=filtered_df.to_csv(index=False),
        file_name='filtered_data.csv'
    )