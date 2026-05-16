<div align="center">

# Global Food & Nutrition Dashboard

<br>

<a href="#project-overview">
  <img src="https://readme-typing-svg.demolab.com?font=Poppins&weight=700&size=30&duration=4000&pause=1000&color=FF6B35&center=true&vCenter=true&width=900&height=60&lines=%F0%9F%8D%94+What+does+the+world+eat%2C+how+healthy+is+it%2C;and+what's+really+in+our+food%3F" alt="Research Question" />
</a>

<br><br>

An interactive data visualization dashboard built with **Python Shiny** for COMP5120 — Data Visualization (Spring).

<p>
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/Shiny-Python-green" alt="Shiny" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License" />
</p>

</div>

---

## Project Overview

This project explores the global food supply, nutrition, and health through an interactive two-part dashboard. We designed it to answer real-world questions about our food systems, while tackling the challenge of visualizing complex, high-dimensional data that spans both global trends and individual products.

### Key Questions Answered
Our main question has three parts, each mapped to a dedicated dashboard section:
1. **"What does the world eat?"** — We investigate how dietary patterns and daily calorie supplies vary across 180+ countries and how food source composition (meat, cereals, dairy) has shifted over decades.
2. **"How healthy is it?"** — We link dietary patterns to health outcomes (obesity, malnutrition, life expectancy) using WHO and OWID data, and apply ML models (country clustering, dietary profiling) to uncover hidden relationships.
3. **"What's really in our food?"** — We drill into 45,000+ food products to assess their nutritional quality (Nutri-Score A–E) and processing levels (NOVA classification), and predict quality scores using ML.

### Dashboard Highlights

- **Charts and Visualizations:** We've built **12 interactive charts** using **7 distinct types** — choropleth maps, line charts, stacked area charts, horizontal bar charts, scatter plots, donut charts, and 2D cluster projections — spanning all three tabs of the dashboard.
- **Interactivity:** The dashboard allows users to dynamically explore data through year sliders, continent and food-type dropdowns, and cross-filtering between linked charts. Clicking a country on the map updates trend lines; brushing a scatter plot highlights individual products.
- **Machine Learning and Analytics:** We integrated several ML components directly into the visual workflow — K-means clustering of countries by dietary profile, parallel coordinates for comparing high- vs. low-obesity diets, and a Nutri-Score classifier that predicts food quality from macronutrient inputs.
- **Reproducibility:** The entire data pipeline is automated via `python data/collect_data.py`, with a complete dependency list in `requirements.txt` and clear setup instructions for one-command replication.

---

## Datasets Used

All datasets are downloaded automatically via `python data/collect_data.py`. The script is idempotent — re-running it skips already-downloaded files.

### Question 1: "What does the world eat?"

| File | Source | Records | Key Variables |
|------|--------|---------|---------------|
| `owid_calorie_supply.csv` | [Our World in Data](https://ourworldindata.org/grapher/daily-per-capita-caloric-supply) | 200+ countries, 1961–2023 | Daily kcal per capita by country and year |
| `owid_food_composition.csv` | [Our World in Data](https://ourworldindata.org/grapher/dietary-composition-by-country) | 200+ countries, 1961–2023 | Calorie breakdown by food group (meat, cereals, dairy, fruits, oils) |

### Question 2: "How healthy is it?"

| File | Source | Records | Key Variables |
|------|--------|---------|---------------|
| `owid_obesity.csv` | [Our World in Data](https://ourworldindata.org/grapher/share-of-adults-defined-as-obese) | 200+ countries, 1975–2016 | Share of adults with BMI ≥ 30 (%) |
| `owid_life_expectancy.csv` | [Our World in Data](https://ourworldindata.org/grapher/life-expectancy) | 200+ countries, 1543–2023 | Life expectancy at birth (years) |
| `who_obesity_adults.csv` | [WHO GHO API](https://ghoapi.azureedge.net/api/) | 190+ countries, 1975–2022 | Obesity prevalence (both sexes), with confidence intervals |
| `who_underweight_children.csv` | [WHO GHO API](https://ghoapi.azureedge.net/api/) | 130+ countries, 1983–2022 | Underweight prevalence in children under 5 |

### Question 3: "What's really in our food?"

| File | Source | Records | Key Variables |
|------|--------|---------|---------------|
| `open_food_facts_sample.csv` | [Open Food Facts](https://world.openfoodfacts.org/data) | ~10,000 products | Nutri-Score (A–E), NOVA group (1–4), energy, fat, sugar, salt, protein, fiber |

---

## Tech Stack

- **Framework:** Python Shiny
- **Visualization:** Plotly, Matplotlib, Seaborn
- **Data Processing:** Pandas, NumPy, GeoPandas
- **Machine Learning:** Scikit-learn
- **Deployment:** [shinyapps.io](https://www.shinyapps.io/)

---

## Getting Started

If you'd like to run the dashboard locally and reproduce our work, follow these steps:

### Prerequisites
- Python 3.10 or higher
- pip

### Installation and Run Instructions

```bash
# 1. Clone the repository
git clone https://github.com/miinguyen/global-food-nutrition-dashboard.git
cd global-food-nutrition-dashboard

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate

# 3. Install the required dependencies
pip install -r requirements.txt

# 4. Launch the application
cd app
shiny run app.py
```

The app will then be available in your browser at `http://localhost:8000`.

---

## Repository Structure

We've organized our repository to clearly map to the project deliverables:

```text
├── README.md                 # This documentation
├── requirements.txt          # Python dependencies for reproducibility
├── project_2.md              # Original assignment specification
├── .gitignore                # Git ignore rules
│
├── proposal/                 # Milestone 1: Proposal (Due May 18)
│   ├── proposal_writeup.md   # Write-up covering motivation and visualization challenges
│   └── wireframe/            # Dashboard wireframe sketches and interaction plans
│
├── app/                      # Milestone 2: Shiny Application (Due June 7)
│   └── app.py                # Dashboard entry point
│
├── data/                     # Data files and collection scripts
│   ├── collect_data.py       # Automated data collection script (run this first)
│   ├── owid_calorie_supply.csv
│   ├── owid_food_composition.csv
│   ├── owid_obesity.csv
│   ├── owid_life_expectancy.csv
│   ├── who_obesity_adults.csv
│   ├── who_underweight_children.csv
│   └── open_food_facts_sample.csv
│
├── notebooks/                # EDA and ML model training notebooks
├── report/                   # Milestone 2: Final LaTeX report (Due June 7)
└── slides/                   # Presentation slides for the proposal and final demo
```

---

## 👥 Team

| Member | Student ID | Responsibilities |
|--------|-----------|------------------|
| **Nguyen Thi Tra My** | V202503042 | Country-level data & visualizations (Charts 1–4), country clustering, dietary profiling |
| **Tran Thi Hoai Phuong** | V202502962 | Product-level data & visualizations (Charts 4–6), Nutri-Score classification model |


---

## Timeline and Deadlines

| Milestone | Deliverables | Due Date | Status |
|-----------|--------------|----------|--------|
| **Proposal** | Write-up (<500 words), Wireframes, Slides, Data Collection | May 18, 2026 | In Progress |
| **Development**| Cleaning, and ML Modeling | May 25, 2026 | Not Started |
| **Dashboard MVP**| Implementation of the Shiny App with initial charts | June 1, 2026 | Not Started |
| **Final Submission**| Source code, LaTeX Report, Final Slides, and Demo | June 7, 2026 | Not Started |

---

## Live Demo

*The dashboard will be deployed to [shinyapps.io](https://www.shinyapps.io/) as required by the assignment.*  
**Link:** *(To be added after deployment)*

---

## License

This project was created for academic purposes for COMP5120 Data Visualization.