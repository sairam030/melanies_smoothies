# Import python packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

cnx = st.connection("snowflake")
session = cnx.session()

# Write directly to the app
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Customize your Smoothie!")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be", name_on_order)

# Get fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5    
)

# Only proceed if user picked something
if ingredients_list:
    # Convert list into a comma-separated string
    ingredients_string = ", ".join(ingredients_list)
    st.write("Ingredients chosen:", ingredients_string)

    # 🍉 Call SmoothieFroot API for each selected ingredient
    for fruit in ingredients_list:
        fruit_name = fruit.lower()
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_name}")

        if smoothiefroot_response.status_code == 200:
            sf_df = pd.json_normalize(smoothiefroot_response.json())
            st.subheader(f"Nutrition for {fruit}")
            st.dataframe(sf_df)
        else:
            st.error(f"Could not find {fruit} in SmoothieFroot API.")

    # Add a Submit button
    if st.button("Submit Order"):
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered! ✅')
