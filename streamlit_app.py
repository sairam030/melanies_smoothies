# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

cnx = st.connection("snowflake")
session = cnx.session()

# Write directly to the app
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Customize your Smoothie!")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be", name_on_order)

# Get fruit options (FRUIT_NAME shown to user, SEARCH_ON used for API calls)
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON')).to_pandas()

# Multiselect for ingredients (show FRUIT_NAME in dropdown)
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe['FRUIT_NAME'],
    max_selections=5    
)

# Only proceed if user picked something
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)

    # Loop through fruits chosen
    for fruit_chosen in ingredients_list:
        # Lookup the API-safe search term
        search_term = my_dataframe.loc[my_dataframe['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].values[0]

        # Call SmoothieFroot API
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_term.lower()}")

        st.subheader(f"{fruit_chosen} Nutrition Information")

        if smoothiefroot_response.status_code == 200:
            sf_df = pd.json_normalize(smoothiefroot_response.json())
            st.dataframe(sf_df, use_container_width=True)
        else:
            st.error(f"Sorry, {fruit_chosen} not found in SmoothieFroot database.")

    # Add a Submit button
    if st.button("Submit Order"):
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered! ✅')
