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
pd_df = my_dataframe.to_pandas()

# Multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'],
    max_selections=5
)


if ingredients_list:
    for fruit_chosen in ingredients_list:
        # Look up the SEARCH_ON value using Pandas
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')

        if search_on == "N/A":
            st.warning(f"Sorry, {fruit_chosen} is not available in SmoothieFroot.")
        else:
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
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
