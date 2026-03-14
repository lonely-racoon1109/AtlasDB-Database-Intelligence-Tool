# blah blah

## fetaure

1. **Upload relational database** as a ZIP of CSV tables.
2. **AI Summary**: Generates a concise, business-friendly summary of the database.
3. **Interactive ER / Knowledge Graph**: Explore tables and relationships visually.
4. **Schema Overview**: See tables, columns, types, constraints, missing values, and unique counts.
5. **Data Dictionary**: AI-generated, human-readable descriptions for each column.
6. **Data Quality Metrics**: Completeness, duplicates, memory usage, numeric/categorical column stats.
7. **Business Insights**: AI-generated high-level insights from the database.
8. **Downloadable Report**: PDF containing summary, ER diagram, schema, data quality, and insights.
9. **Chatbot Prototype**: Sidebar UI for asking questions (currently static placeholder).No AI processing YET.

---

## tech Stack

- **Streamlit**: Web app interface  
- **pandas**: Data handling and profiling  
- **zipfile**: Upload and read CSV files  
- **pyvis and graphviz**: Interactive ER/knowledge graph visualization  
- **OpenAI / GROQ**: AI-powered summary, data dictionary, and business insights  
- **markdown + WeasyPrint**: Generate PDF reports from Markdown  

---

## Installation

1. **Clone the repository**
2. **Create a virtual environment**
3. **Install dependencies**:

```
streamlit
pandas
pyvis (graphs)
graphvis (er-diagram)
weasyprint (report)
groq (LLM)
markdown
```
4. **Set API credentials** for AI calls:

make a .streamlit folder in your folder and in that make a secrets.toml file and paste your key there:

``` toml
GROQ_API_KEY="<key>"
```

use:

```python
from groq import GROQ
client = GROQ(api_key="YOUR_API_KEY")
```

5. **Run the app**:

```bash
streamlit run app.py
```
---

## Folder Structure

```
ai-db-intelligence/
│
├─ app.py                 # Main Streamlit app
├─ modules/
│   ├─ schema_extractor.py # Generate schema and data quality
│   ├─ graph_builder.py    # Build pyvis ER/knowledge graph
│   ├─ dq_metrics.py  #data qualit metrics
│   ├─ report.py    # report generator
│   └─ bi_insights.py    # summary, data dictionary and business intelligence generator              
├─ requirements.txt
└─ README.md
```

---

## Notes

* Ensure **GROQ API keys** are valid and set before generating AI-based summaries or data dictionary.
* ER diagram is generated automatically and saved as an image for PDF inclusion.
* Data dictionary and business insights are AI-generated; incomplete descriptions may occur for very noisy datasets.
* Chatbot is currently a **UI prototype** only.





