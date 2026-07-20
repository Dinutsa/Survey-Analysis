# Survey Analysis Tool

**Survey Analysis Tool** is a web application for automated analysis and report generation based on Google Forms survey results. The app allows you to upload a "raw" Excel file, filter data, and instantly get professionally formatted reports in **PDF**, **Word** (.docx), **PowerPoint** (.pptx) та **Excel**.

Look for more in a **Survey_Analysis_Case.pdf**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red)
![Status](https://img.shields.io/badge/Status-Active-success)

---

## Key Features

* **Data import:** Support for `.xlsx` files exported directly from Google Forms. Automatic header detection even when extra rows are present.
* **Data Analysis:**
    * Automatic question classification: **Scale** (1-10 rating) or **Single Choice** (option selection).
    * Building relevant charts: bar charts for ratings, pie charts for categories.
* **Processing Tools:**
    * Survey range filtering (Slicing).
    * Detailed statistics preview for each question.
    * Cross-filtering for in-depth dependency analysis.
* **Multi-format Export**
    * **PDF:** Official report with full Unicode support, charts, and tables.
    * **Word (.docx):** Editable document with pre-configured styles and headers.
    * **PowerPoint (.pptx):** Ready-to-present slides with a title page, and visual results.
    * **Excel:** Processed summary pivot table.

---

## Language Support 🌐

The application is designed with internationalization in mind and features a fully multilingual interface. Currently, the tool supports three languages:
* Ukrainian (UA)
* English (EN)
* Romanian (RO)
* Polish (PL)

Language switching happens seamlessly in the UI, instantly translating all interface elements, table headers, chart labels, and generated export files (PDF, Word, PPTX) into the selected language.

---

## Tech Stack

The project is built on **Python** using the following libraries:

* **[Streamlit]:** Web interface and interactivity.
* **[Pandas]:** Tabular data processing and analysis.
* **[Matplotlib] / [Plotly]:** Data visualization (static and interactive charts).
* **[FPDF]:** PDF report generation.
* **[Python-docx]:** Word document creation.
* **[Python-pptx]:** PowerPoint presentation creation.
* **XlsxWriter / OpenPyXL:** Excel file operations.

---

## Installation & Usage

### 1. Clone the repository
Download the project to your local machine:
```bash
git clone [https://github.com/your-username/survey-analytics.git](https://github.com/your-username/survey-analytics.git)
cd survey-analytics
```
### 2. Install dependencies
```bash
pip install -r requirements.txt
```
### 3. Run the application
```bash
streamlit run app.py
```
After running, your browser will open automatically at http://localhost:8501.

---

## Project Structure

* **app.py** — Main application file (Frontend and interface logic).
* **data_loader.py** — Loading and initial cleaning of Excel files.
* **classification.py** — Question type detection algorithms.
* **summary.py** — Statistics aggregation.
* **pdf_export.py** — PDF generation module.
* **docx_export.py** — Word generation module.
* **pptx_export.py** — PowerPoint generation module.
* **excel_export.py** — Excel generation module.
* **lang.py** — Language dictionary.

---

## Demo & Testing Files
* **demo_surveys_en.xlsx** — A sample dataset containing demo survey responses in English. You can use this file to test the application's functionality without needing your own data.

* **gen_data.py** — A utility script for generating synthetic/mock survey data. Useful for creating robust test datasets with various parameters.

---

## Implementation Details

* **In-Memory Processing:** All files are generated in RAM (`io.BytesIO`) (io.BytesIO) without being saved to the local disk, ensuring fast processing and server cleanliness.
* **Session State:** Utilizes Streamlit's state management mechanism for stable operation during user interactions.
* **Unicode Support in PD:** Integrated custom fonts (e.g., Arial/Tinos) for correct rendering of Ukrainian, Romanian, Polish and special characters, as standard PDF libraries often have Unicode limitations.
* **Responsive Design:** The interface is optimized for a seamless user experience on both desktop and mobile devices.

## Authors

* **Developer:** Diana Kaptar (MPUiK Student)
* **Project Supervisor:** Associate Professor Valeriy Fratavchan

> *This project was created as part of a diploma thesis.*
