# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Write directly to the app
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Customize your Smoothie!")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be", name_on_order)

# Get fruit options from Snowflake (with FRUIT_NAME + SEARCH_ON)
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON"))
pd_df = my_dataframe.to_pandas()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'],
    max_selections=5    
)

# Only proceed if user picked something
# if ingredients_list:
#     ingredients_string = ", ".join(ingredients_list)
#     st.write("Ingredients chosen:", ingredients_string)

#     # Show nutrition only for valid fruits
#     for fruit_chosen in ingredients_list:
#         search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

#         st.subheader(f"{fruit_chosen} Nutrition Information")

#         if search_on == "N/A":
#             st.info(f"{fruit_chosen} added to your smoothie! ✅ (No nutrition data available)")
#         else:
#             response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
#             if response.status_code == 200:
#                 st.dataframe(response.json(), use_container_width=True)
#             else:
#                 st.warning(f"Sorry, no data found for {fruit_chosen}")

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)

    # Add a Submit button
    if st.button("Submit Order"):
        my_insert_stmt = """
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES (?, ?)
        """
        session.sql(my_insert_stmt, (ingredients_string, name_on_order)).collect()
    
    
        st.success('Your Smoothie is ordered! ✅')

