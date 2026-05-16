<div align="center">

# Global Food & Nutrition Dashboard

<br>

<a href="#project-overview">
  <img src="https://img.shields.io/badge/What_does_the_world_eat,_how_healthy_is_it,_and_what's_really_in_our_food%3F-FF6B35?style=for-the-badge&labelColor=FF6B35" alt="Research Question" />
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
We divided our analysis into two main perspectives:
1. **Country-Level Analysis ("What Does the World Eat?"):** We investigate how dietary patterns and daily calorie supplies vary across different regions. We also look at how these patterns correlate with health outcomes, such as obesity and malnutrition.
2. **Product-Level Analysis ("What's Really in Our Food?"):** We dive into the details of over 45,000 food products to assess their nutritional quality (using the Nutri-Score framework) and their processing levels (using the NOVA classification).

### Alignment with Project Requirements
Our project meets and exceeds the core requirements of the Project 2 assignment:
- **Charts and Visualizations:** We've built over 6 charts using 4 distinct types, including interactive choropleth maps, time-series line charts, scatter plots, and bar charts. This easily covers the minimum requirement of 5 charts and 3 types.
- **Interactivity:** The dashboard allows users to dynamically explore the data through interactive year and food-type filtering, alongside cross-filtered, linked visual components.
- **Machine Learning and Analytics (COMP 5120):** We integrated several ML components directly into the workflow, such as predicting Nutri-Scores, clustering countries based on diet, and running obesity regression models.
- **Reproducibility:** The entire pipeline is reproducible. We've included clear setup instructions, data collection scripts, and a complete dependencies list.

---

## Datasets Used

To build this dashboard, we synthesized data from four major sources:

| Source | Level | Coverage | Description |
|--------|-------|----------|-------------|
| [FAOSTAT Food Balance Sheets](https://www.fao.org/faostat/en/#data/FBS) | Country | 180+ countries, 2010–2023 | Global food supply and macronutrient composition |
| [Our World in Data — Food Supply](https://ourworldindata.org/food-supply) | Country | 200+ countries, 1961–2023 | Historical trends in diet and food availability |
| [WHO GHO — Nutrition](https://apps.who.int/gho/data/node.home) | Country | Global health indicators | Health outcomes (obesity, malnutrition) |
| [Kaggle — Global Food & Nutrition](https://www.kaggle.com/) | Product | 45,000+ food items | Granular product-level nutritional profiles |

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
├── notebooks/                # EDA and ML model training notebooks
├── report/                   # Milestone 2: Final LaTeX report (Due June 7)
└── slides/                   # Presentation slides for the proposal and final demo
```

---

## 👥 Team

| Member | Student ID | Responsibilities |
|--------|-----------|------------------|
| **Nguyen Thi Tra My** | V202503042 | Country-level data & visualizations (Charts 1–3), country clustering, obesity regression model |
| **Tran Thi Hoai Phuong** | V202502962 | Product-level data & visualizations (Charts 4–6), Nutri-Score classification model |


---

## Timeline and Deadlines

| Milestone | Deliverables | Due Date | Status |
|-----------|--------------|----------|--------|
| **Proposal** | Write-up (<500 words), Wireframes, Slides | May 18, 2026 | In Progress |
| **Development**| Data Collection, Cleaning, and ML Modeling | May 25, 2026 | Not Started |
| **Dashboard MVP**| Implementation of the Shiny App with initial charts | June 1, 2026 | Not Started |
| **Final Submission**| Source code, LaTeX Report, Final Slides, and Demo | June 7, 2026 | Not Started |

---

## Live Demo

*The dashboard will be deployed to [shinyapps.io](https://www.shinyapps.io/) as required by the assignment.*  
**Link:** *(To be added after deployment)*

---

## License

This project was created for academic purposes for COMP5120 Data Visualization.