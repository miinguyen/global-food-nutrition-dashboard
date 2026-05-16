# 🍔 Global Food & Nutrition Dashboard

> **What does the world eat, how healthy is it, and what's really in our food?**

An interactive data visualization dashboard built with **Python Shiny** for COMP5120 — Data Visualization (Spring 2026).

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Shiny](https://img.shields.io/badge/Shiny-Python-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📖 Project Overview

This project explores global food supply, nutrition, and health through an interactive two-section dashboard:

1. **Country-Level Analysis** — *"What Does the World Eat?"*
   - Visualize daily calorie supply, food source composition, and health outcomes (obesity, malnutrition) across 180+ countries using data from FAOSTAT and Our World in Data.

2. **Product-Level Analysis** — *"What's Really in Our Food?"*
   - Drill down into 45,000+ food products to explore nutritional quality (Nutri-Score), processing levels (NOVA classification), and macronutrient profiles.

### Key Features
- 🗺️ Interactive choropleth maps with year/food-type filters
- 📈 Time-series visualizations of global food trends
- 🤖 ML components: Nutri-Score prediction, country clustering, obesity regression
- 🔗 Cross-filtered, linked visual components
- 📊 6+ chart types across two analytical sections

---

## 📊 Datasets

| Source | Level | Coverage |
|--------|-------|----------|
| [FAOSTAT Food Balance Sheets](https://www.fao.org/faostat/en/#data/FBS) | Country | 180+ countries, 2010–2023 |
| [Our World in Data — Food Supply](https://ourworldindata.org/food-supply) | Country | 200+ countries, 1961–2023 |
| [WHO GHO — Nutrition](https://apps.who.int/gho/data/node.home) | Country | Global health indicators |
| [Kaggle — Global Food & Nutrition](https://www.kaggle.com/) | Product | 45,000+ food items |

---

## 🛠️ Tech Stack

- **Framework**: Python Shiny
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Data Processing**: Pandas, NumPy, GeoPandas
- **Machine Learning**: Scikit-learn
- **Deployment**: [shinyapps.io](https://www.shinyapps.io/)

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/miinguyen/global-food-nutrition-dashboard.git
cd global-food-nutrition-dashboard

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Run the App

```bash
cd app
shiny run app.py
```

The app will be available at `http://localhost:8000`.

---

## 📁 Project Structure

```
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── project_2.md              # Assignment specification
├── .gitignore                # Git ignore rules
│
├── proposal/                 # Proposal deliverables (Due May 18)
│   ├── proposal_writeup.md   # Write-up (under 500 words)
│   └── wireframe/            # Dashboard wireframe sketches
│
├── data/                     # Datasets (CSV/XLSX)
│
├── app/                      # Main Shiny application
│   └── app.py                # Dashboard entry point
│
├── notebooks/                # EDA & analysis notebooks
│
├── report/                   # Final LaTeX report (Due June 7)
│
├── slides/                   # Presentation slides
│
└── week10/                   # Course exercise examples
```

---

## 👥 Team

| Member | Responsibilities |
|--------|-----------------|
| Member 1 | Country-level data & viz (Charts 1–3), clustering, obesity regression |
| Member 2 | Product-level data & viz (Charts 4–6), Nutri-Score classification |

---

## 📅 Timeline

| Milestone | Due Date | Status |
|-----------|----------|--------|
| Proposal & Wireframe | May 18, 2026 | 🔄 In Progress |
| Data Collection & Cleaning | May 25, 2026 | ⬜ Not Started |
| Dashboard MVP | June 1, 2026 | ⬜ Not Started |
| Final Submission & Presentation | June 7, 2026 | ⬜ Not Started |

---

## 🌐 Live Demo

> *Deployment link will be added after deploying to shinyapps.io*

---

## 📄 License

This project is for academic purposes — COMP5120 Data Visualization, Spring 2026.