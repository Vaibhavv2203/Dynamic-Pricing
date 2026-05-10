import streamlit as st
import openai
import pandas as pd
import requests
import datetime
import plotly.express as px

# Configure APIs
OPENAI_API_KEY = 'YOUR_OPENAI_KEY' #Replace with your api key
NEWS_API_KEY = 'YOUR_NEWS_API_KEY' #Replace with your api key
WEATHER_API_KEY = 'YOUR_WEATHER_API_KEY' #Replace with your api key

openai.api_key = OPENAI_API_KEY

# Streamlit UI
st.title('Dynamic Price Optimizer')
st.write("Upload Excel files with your price data and competitor price data.")
base_file = st.file_uploader("Upload Base Price File (Excel)", type=["xlsx"])
competitor_file = st.file_uploader("Upload Competitor Price File (Excel)", type=["xlsx"])
beta = st.slider('Risk Sensitivity Factor (Beta - news/weather)', 0.0, 1.0, 0.3)
alpha = st.slider('Competitor Sensitivity Factor (Alpha)', 0.0, 1.0, 0.3)

# External API functions
def get_news_risk_score():
    url = f'https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey={NEWS_API_KEY}'
    try:
        response = requests.get(url).json()
        if 'articles' in response:
            risk_score = sum(1 for article in response['articles'] if 'inflation' in article['title'].lower()) / 10
            return min(risk_score, 1.0)
    except Exception as e:
        print("News API failed:", e)
    return 0.3

def get_weather_risk_score(city='New York'):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}'
    high_risk = ['Thunderstorm', 'Snow', 'Tornado', 'Squall']
    moderate_risk = ['Rain', 'Drizzle', 'Fog']
    low_risk = ['Clouds', 'Clear']
    try:
        response = requests.get(url).json()
        if 'weather' in response:
            desc = response['weather'][0]['description']
            if any(condition.lower() in desc.lower() for condition in high_risk):
                return 0.7
            elif any(condition.lower() in desc.lower() for condition in moderate_risk):
                return 0.5
            elif any(condition.lower() in desc.lower() for condition in low_risk):
                return 0.3
    except Exception as e:
        print("Weather API failed:", e)
    return 0.2

def get_ai_recommendation(online_price, offline_price, competitor_price, risk_score, beta, alpha):
    prompt = f"""
    You are a pricing optimization expert. Consider the following:

    - Our Online Price: {online_price}
    - Our In-store Price: {offline_price}
    - Competitor Price: {competitor_price}
    - Economic & Weather Risk Score: {risk_score}
    - Beta (economic/weather factor): {beta}
    - Alpha (competitor sensitivity): {alpha}

    Provide:
    - Recommended price only. Please don't output the "Recommended price:" with it. (For eg: $26.90/mo). Also if there is no online price then don't suggest any recommended price. 
    - Three-line reason for the change based on differences in our prices and competitor price, and market risk.
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a pricing optimization expert."},
                {"role": "user", "content": prompt}
            ],
            timeout=30
        )
        return response.choices[0].message.content.strip().split("\n", 1)
    except Exception as e:
        print("OpenAI call failed:", e)
        return ["Error", "Could not get recommendation"]

# Button block
if st.button('Calculate Recommended Prices') and base_file and competitor_file:
    with st.spinner("Running recommendations..."):
        try:
            base_df = pd.read_excel(base_file)
            comp_df = pd.read_excel(competitor_file)
            base_df = base_df.head(20)  # TEMP: Limit for demo
            comp_df = comp_df.head(20)

            if all(col in base_df.columns for col in ['gate_hours', 'price_online', 'price_in_store', 'other_flag']) and \
               all(col in comp_df.columns for col in ['price_online']):
                
                news_risk = get_news_risk_score()
                weather_risk = get_weather_risk_score()
                combined_risk = (news_risk + weather_risk) / 2
                base_df['Risk_Score'] = combined_risk

                recommended_prices = []
                reasons = []

                for i, row in base_df.iterrows():
                    comp_price = comp_df.loc[i, 'price_online'] if i < len(comp_df) else row['price_online']
                    rec_price, reason = get_ai_recommendation(
                        row['price_online'],
                        row['price_in_store'],
                        comp_price,
                        combined_risk,
                        beta,
                        alpha
                    )
                    recommended_prices.append(rec_price)
                    reasons.append(reason)

                base_df['Recommended_Price'] = recommended_prices
                base_df['Reasons'] = reasons

                st.success("Pricing completed successfully!")
                st.write('### Recommended Price Details')
                display_df = base_df[['locker_id','name', 'size', 'locker_details', 'price_online', 'Recommended_Price', 'Reasons']].rename(columns={
                            'price_online': 'Online Price',
                            'Recommended_Price': 'Recommended Price',
                            'Reasons': 'Reasons',
                            'locker_details': 'Locker Details',
                            'name': 'Name',
                            'size': 'Size',
                            'locker_id': 'Locker ID'
                    })
                st.dataframe(display_df, use_container_width=True)

                #display the figure in streamlit
                st.subheader("Bar Graph for Data Visualization")


                display_df['online_price_n'] = display_df['Online Price'].str.extract(r'\$([\d.]+)')
                display_df['rec_price_n'] = display_df['Recommended Price'].str.extract(r'\$([\d.]+)')

                display_df['online_price_n'] = display_df['online_price_n'].astype(float)
                display_df['rec_price_n'] = display_df['rec_price_n'].astype(float)

                # Scatter plot to show relation between Online Price and Recommended Price
                scatter_fig = px.scatter(
                    display_df,
                    x='online_price_n',
                    y='rec_price_n',
                    hover_data=['Name', 'Size', 'Locker Details', 'Online Price', 'Recommended Price'],
                    labels={'online_price_n': 'Online Price ($)', 'rec_price_n': 'Recommended Price ($)'},
                    title="Online Price vs Recommended Price",
                    trendline="ols"  # Adds a linear regression trendline
                )

                scatter_fig.update_traces(marker=dict(size=10, color='blue'), selector=dict(mode='markers'))
                scatter_fig.update_layout(
                    xaxis=dict(title='Online Price ($)'),
                    yaxis=dict(title='Recommended Price ($)'),
                    title_x=0.5
                )

                #st.plotly_chart(scatter_fig, use_container_width=True)
##
##
##


                # Create a long-form DataFrame for grouped bar chart
                melted_df = pd.melt(
                    display_df,
                    id_vars=['Locker ID'],
                    value_vars=['online_price_n', 'rec_price_n'],
                    var_name='Price Type',
                    value_name='Price'
                )

                # Rename for clarity
                melted_df['Price Type'] = melted_df['Price Type'].map({
                    'online_price_n': 'Online Price',
                    'rec_price_n': 'Recommended Price'
                })

                # Plot grouped bar chart
                bar_fig = px.bar(
                    melted_df,
                    x='Locker ID',
                    y='Price',
                    color='Price Type',
                    barmode='group',
                    labels={'Locker ID': 'Locker ID', 'Price': 'Price ($)'},
                    title='Online vs Recommended Price by Locker ID'
                )

                bar_fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(bar_fig, use_container_width=True)

##                #create bubble chart with color, different symbols and hover data
##                coloured_bubble_fig = px.bar(display_df, x='online_price_n', y='rec_price_n')
##                st.plotly_chart(coloured_bubble_fig)
##                #st.dataframe(base_df[['name', 'gate_hours', 'size', 'locker_details', 'price_online', 'Risk_Score', 'Recommended_Price', 'Reasons']])
            else:
                st.error("Required columns missing in one of the files.")
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            print("ERROR:", e)
    
