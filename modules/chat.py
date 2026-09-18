from groq import Groq
import streamlit as st
import duckdb
import re

def conversate(question, schema, dq_summary, data_dictionary, ai_summary, chat_history=None):

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    history = ""

    if chat_history:
        for message in chat_history[-6:]:

            if message["role"] == "user":
                history += f"USER: {message['content']}\n"

            elif message["role"] == "assistant":

                if message["type"] == "text":
                    history += f"ASSISTANT: {message['content']}\n"

                elif message["type"] == "table":
                    history += f"ASSISTANT SQL: {message['sql']}\n"

    prompt = f"""
        You are a database intelligence assistant.
        
        DATABASE SCHEMA:
        {schema}

        DATA QUALITY SUMMARY:
        {dq_summary}

        DATA DICTIONARY:
        {data_dictionary}

        DATABASE SUMMARY:
        {ai_summary}

        RECENT CONVERSATION:
        {history}

        USER QUESTION:
        {question}

        Decide whether the question requires querying the actual
database or can be answered from the provided database context.

If the question requires actual data such as:
- filtering
- sorting
- aggregation
- counting
- averages
- sums
- comparisons
- rankings
- dates
- specific records

return exactly:

TYPE: SQL
SQL: <valid DuckDB SQL query>

If the question asks for an overview, explanation, interpretation,
or assessment that can be answered using the provided context,
return exactly:

TYPE: TEXT
TEXT: <answer>

For TEXT responses, do not invent facts that are not present
in the provided context.

For SQL responses:
- Return only valid DuckDB SQL after SQL:
- Use only tables and columns present in the schema.
- Use SELECT queries only.
- Do not use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, or other
  data-modifying statements.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip()


def extract_sql(response):

    match = re.search(
        r"TYPE:\s*SQL\s*SQL:\s*(.*)",
        response,
        re.IGNORECASE | re.DOTALL
    )

    if not match:
        return None

    sql = match.group(1).strip()

    # Remove markdown code fences if the model adds them
    sql = re.sub(r"```sql", "", sql, flags=re.IGNORECASE)
    sql = sql.replace("```", "").strip()

    return sql

def execute_query(sql, tables):

    con = duckdb.connect()

    for table_name, df in tables.items():
        con.register(table_name, df)

    result = con.execute(sql).fetchdf()

    con.close()

    return result

def extract_text(response):

    match = re.search(
        r"TYPE:\s*TEXT\s*TEXT:\s*(.*)",
        response,
        re.IGNORECASE | re.DOTALL
    )

    if not match:
        return None

    return match.group(1).strip()
