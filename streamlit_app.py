# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

cnx = st.connection("snowflake")
session = cnx.session()

# Write directly to the app
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Customize your Smoothie!")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be", name_on_order)

# Get fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col("FRUIT_NAME"), col("SEARCH_ON")
)


# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5    
)

if ingredients_list:
    ingredients_string = ", ".join(ingredients_list)
    st.write("Ingredients chosen:", ingredients_string)

    for fruit_chosen in ingredients_list:
        # 🔎 Look up SEARCH_ON from Snowflake for this FRUIT_NAME
        search_value = (
            session.table("smoothies.public.fruit_options")
            .filter(col("FRUIT_NAME") == fruit_chosen)
            .select(col("SEARCH_ON"))
            .collect()[0][0]
        )

        st.subheader(f"{fruit_chosen} Nutrition Information")

        if search_value == "N/A":
            st.warning(f"Sorry, {fruit_chosen} is not available in SmoothieFroot.")
        else:
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_value}")
            if response.status_code == 200:
                st.dataframe(response.json(), use_container_width=True)
            else:
                st.error(f"Could not fetch data for {fruit_chosen}")


# Add a Submit button
if st.button("Submit Order"):
    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders(ingredients, name_on_order)
    VALUES ('{ingredients_string}', '{name_on_order}')
    """
    session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered! ✅')
