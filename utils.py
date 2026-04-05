import pandas as pd
import numpy as np

def load_data(path):
    df = pd.read_csv(path)
    return df

def clean_data(df):
    df = df.copy()

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Convert to numeric
    df['product_rating'] = pd.to_numeric(df['product_rating'], errors='coerce')
    df['retail_price'] = pd.to_numeric(df['retail_price'], errors='coerce')
    df['discounted_price'] = pd.to_numeric(df['discounted_price'], errors='coerce')

    # Drop missing important values
    df.dropna(subset=['retail_price', 'product_rating'], inplace=True)

    # Remove duplicates
    df.drop_duplicates(inplace=True)

    return df

import ast

def add_features(df):
    df = df.copy()

    df['discount_percent'] = (
                                     (df['retail_price'] - df['discounted_price']) / df['retail_price']
                             ) * 100

    # Clean category
    df['product_category_tree'] = df['product_category_tree'].astype(str)
    df['product_category_tree'] = df['product_category_tree'].str.replace(r'[\[\]\"]', '', regex=True)
    df['main_category'] = (
    df['product_category_tree']
    .str.split(">>").str[0]
    .str.strip()
    .str.title())

    # 🔥 FIX IMAGE COLUMN
    def extract_image(img):
        try:
            img_list = ast.literal_eval(img)  # convert string → list
            if isinstance(img_list, list) and len(img_list) > 0:
                return img_list[0]  # take first image
        except:
            return None
        return None

    df['image_url'] = df['image'].apply(extract_image)

    return df

def compute_kpis(df):
    return {
        "total_products": len(df),
        "avg_price": round(df['retail_price'].mean(), 2),
        "avg_rating": round(df['product_rating'].mean(), 2),
        "avg_discount": round(df['discount_percent'].mean(), 2)
    }

def filter_data(df, category, price_range):
    return df[
        (df['main_category'] == category) &
        (df['retail_price'] >= price_range[0]) &
        (df['retail_price'] <= price_range[1])
        ]

def generate_insights(df):
    insights = []

    if df['product_rating'].mean() > 4:
        insights.append("✅ Highly rated products")
    else:
        insights.append("⚠️ Ratings need improvement")

    if df['discount_percent'].mean() > 30:
        insights.append("🔥 High discount strategy")

    if df['retail_price'].mean() > 3000:
        insights.append("💎 Premium category")
    else:
        insights.append("💰 Budget-friendly")

    return insights