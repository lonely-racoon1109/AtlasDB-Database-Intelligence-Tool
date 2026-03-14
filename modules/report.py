import markdown
from weasyprint import HTML

import markdown
from weasyprint import HTML


def generate_markdown_report(summary, schema, dq_summary, insights, data_dictionary):

    md = f"""
## AI Database Intelligence Report

---

### AI Database Summary

{summary}

---

## Data Dictionary
"""

    # -----------------------
    # Data Dictionary
    # -----------------------
    for table, data in schema.items():

        md += f"\n### {table}\n"

        md += "| Column | Type | Description |\n"
        md += "|------|------|------|\n"

        for col, meta in data["columns"].items():

            desc = data_dictionary.get(table, {}).get(col, "")

            md += f"| {col} | {meta['dtype']} | {desc} |\n"

    # -----------------------
    # ER Diagram
    # -----------------------
    md += """
---

## ER Diagram

![ER Diagram](er_diagram.png)

---
"""

    # -----------------------
    # Database Schema
    # -----------------------
    md += "\n## Database Schema\n"

    for table, data in schema.items():

        md += f"\n### {table} ({data['rows']} rows)\n"

        md += "| Column | Type | Constraint | Missing | Unique |\n"
        md += "|------|------|------|------|------|\n"

        for col, meta in data["columns"].items():

            md += f"| {col} | {meta['dtype']} | {meta['constraints']} | {meta['missing']} | {meta['unique']} |\n"

    # -----------------------
    # Data Quality
    # -----------------------
    md += "\n---\n## Data Quality Analysis\n\n"

    md += "| Table | Rows | Cols | Completeness % | Duplicates | Dup Rate % | Null-heavy | Memory MB |\n"
    md += "|------|------|------|------|------|------|------|------|\n"

    for table, metrics in dq_summary.items():

        md += (
            f"| {table} "
            f"| {metrics['rows']} "
            f"| {metrics['columns']} "
            f"| {round(metrics['completeness'],2)} "
            f"| {metrics['duplicates']} "
            f"| {round(metrics['duplicate_rate'],2)} "
            f"| {len(metrics['null_heavy_cols'])} "
            f"| {round(metrics['memory_usage_mb'],2)} |\n"
        )

    # -----------------------
    # Business Insights
    # -----------------------
    md += "\n---\n## Business Insights (AI Generated)\n\n"

    md += insights

    return md

def convert_to_pdf(md_text):

    html_text = markdown.markdown(md_text, extensions=["tables"])

    styled_html = f"""
    <html>
    <head>
    <style>
        body {{
            font-family: "Times New Roman";
            margin: 20px;
        }}

        h1 {{
            page-break-after: avoid;
            color: #2c3e50;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
            table-layout: fixed;
            page-break-inside:avoid;
            font-size: 10px;
        }}

        th, td {{
            border: 1px solid #999;
            padding: 3px;
            text-align: center;
            overflow-wrap: break-word;
        }}

        th {{
            background-color: #f2f2f2;
        }}

        img {{
            max-width: 80%;
            height:auto;
            page-break-inside: avoid;
        }}

    </style>
    </head>
    <body>
    {html_text}
    </body>
    </html>
    """

    pdf_path = "database_report.pdf"

    HTML(string=styled_html, base_url=".").write_pdf(pdf_path)

    return pdf_path


    