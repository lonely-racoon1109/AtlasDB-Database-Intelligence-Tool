from groq import Groq
import streamlit as st
import os
import json

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def build_db_description(schema):

    desc = ""

    for table, data in schema.items():

        columns = ", ".join(data["columns"].keys())

        desc += f"""
        Table: {table}
        Rows: {data['rows']}
        Columns: {columns}
        """

    return desc

def generate_db_summary(schema):

    db_text = build_db_description(schema)

    prompt = f"""
    You are a data analyst.

    Summarize the following relational database in a concise paragraph (2-3 sentences) 
    and provide 3-5 short bullet points. Use simple, business-friendly language.

    Focus on:
    - Main entities and how they relate to each other
    - Data scale (rows, tables, key volumes)
    - Possible business context or use cases

    Database schema:
    {db_text}
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content

def generate_business_insights(dq_summary):

    insights_text = ""

    for table, metrics in dq_summary.items():
        insights_text += f"""
        Table: {table}
        Rows: {metrics['rows']}
        Columns: {metrics['columns']}
        Completeness: {metrics['completeness']}%
        Duplicates: {metrics['duplicates']}
        """

    prompt = f"""
    You are a senior data analyst.

    Based on this database summary, generate a concise set of business insights. 
    Focus on:

    - Key observations about the data (trends, patterns)
    - Potential anomalies or data quality issues
    - Relationships or correlations between tables
    - Any opportunities or risks apparent from the data

    Provide the insights as clear bullet points, in simple business language, no extra explanations.

    Database Summary:
    {insights_text}
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )

    return response.choices[0].message.content

def generate_data_dictionary(schema):

    dictionary = {}

    for table, data in schema.items():

        dictionary[table] = {}

        for col, meta in data["columns"].items():

            prompt = f"""
Explain this database column based on its table schema in simple business language.

Table: {table}
Column: {col}
Type: {meta["dtype"]}

Return ONLY one short sentence description.
"""

            try:

                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2
                )

                desc = response.choices[0].message.content.strip()

            except:
                desc = ""

            # fallback if model fails
            if not desc:
                desc = col.replace("_"," ") + " field"

            dictionary[table][col] = desc

    return dictionary
