# Dynamic Pricing Optimizer

An AI-powered pricing optimization system built using Streamlit, OpenAI GPT-4o, Pandas, and Plotly.

The application analyzes internal pricing data, competitor pricing, economic news, and weather conditions to generate intelligent pricing recommendations for storage units. It also provides reasoning behind pricing adjustments and visualizes pricing trends through interactive charts.

---

## Features

- Upload Excel-based pricing datasets
- AI-generated pricing recommendations
- Competitor price comparison
- Economic and weather-based risk analysis
- Dynamic pricing optimization
- Interactive visualizations using Plotly
- Automated pricing explanations
- Adjustable pricing sensitivity controls
- Real-time business intelligence integration

---

## Tech Stack

- Python
- Streamlit
- OpenAI GPT-4o
- Pandas
- Plotly
- News API
- OpenWeather API
- OpenPyXL

---

## Project Workflow

1. Upload:
   - Base pricing Excel file
   - Competitor pricing Excel file

2. The system:
   - Reads and processes pricing data
   - Fetches business news risk signals
   - Fetches weather-related market risk
   - Calculates combined market risk score

3. GPT-4o analyzes:
   - Online prices
   - In-store prices
   - Competitor prices
   - Economic risk
   - Weather risk
   - User-defined sensitivity factors

4. The AI generates:
   - Recommended prices
   - Explanations for pricing changes

5. Results are visualized using interactive charts.

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/dynamic-pricing-optimizer.git
cd dynamic-pricing-optimizer
