import streamlit as st
import zipfile
import pandas as pd
import streamlit.components.v1 as components

#IMPORTS FROM APP MODULES
from modules.schema_extractor import generate_schema
from modules.graph_builder import build_graph, build_er_diagram
from modules.dataquality_metrics import generate_data_quality
from modules.bi_insights import (
    generate_db_summary,
    generate_business_insights,
    generate_data_dictionary
)
from modules.report_generate import generate_markdown_report, convert_to_pdf

#PAGE CONFIGURATIONS
st.set_page_config(
    page_title="AI Database Intelligence Agent",
    layout="wide"
)

#FILE UPLOAD
uploaded_file = st.file_uploader(
    "Upload dataset.zip containing CSV tables",
    type=["zip"]
)

if uploaded_file is not None:
#CLEAR AI RESULTS OF PREVIOUS DATASET
    dataset_hash = uploaded_file.name

    if "dataset_hash" not in st.session_state or st.session_state.dataset_hash != dataset_hash:

        st.session_state.pop("ai_insights", None)
        st.session_state.pop("data_dictionary", None)
        st.session_state.pop("ai_summary", None)

    st.session_state.dataset_hash = dataset_hash

    with st.spinner("Uploading and processing dataset......"):
        tables={}

#LOAD DATASET
        with zipfile.ZipFile(uploaded_file) as z:
            file_list = z.namelist()
            st.write("Files detected: ")
            files_display = "\n".join([f"- `{file}`" for file in file_list])

            st.markdown(files_display)

            for file in file_list:
                if file.endswith(".csv"):
                    with z.open(file) as f:
                        df = pd.read_csv(f)

                        table_name = file.replace(".csv", "")
                        tables[table_name]  = df
        
    st.success("Dataset loaded successfully")

# GENERATE SCHEMA OF UPLOADED DATABASE 
    with st.spinner("Analyzing database structure..."):
        schema = generate_schema(tables)
    st.session_state["schema"] = schema

# CHATBOT SIDEBAR (COLLAPSABLE)
    with st.sidebar:
        if "chat_open" not in st.session_state:
            st.session_state.chat_open = True

        toggle_chat = st.checkbox("Open Chatbot", value=st.session_state.chat_open)
        st.session_state.chat_open = toggle_chat

        if st.session_state.chat_open:
            user_input = st.text_input("Type your message...", key="chat_input")
            if user_input:
                st.write(f"User: {user_input}")
                st.write("Bot: [This is a prototype. No response yet.]")

# DATABASE SUMMARY
    st.header("AI Database Summary")
    summary = "hi"
    dataset_hash = hash(str(schema))

    if "schema_hash" not in st.session_state or st.session_state.schema_hash != dataset_hash:

        with st.spinner("Generating AI summary..."):
            st.session_state.ai_summary = generate_db_summary(schema)
            st.session_state.schema_hash = dataset_hash

    summary = st.session_state.ai_summary

    st.markdown(summary)

# TABLES AND ROW COUNTS
    st.write("Tables:", len(schema))
    total_rows = sum([v["rows"] for v in schema.values()])

    st.write("Total Rows:", total_rows)

    st.divider()

# HUMAN READABLE AI-GENERATED DATA DICTIONARY
    if "data_dictionary" not in st.session_state:

        with st.spinner("Generating AI Data Dictionary..."):
            st.session_state["data_dictionary"] = generate_data_dictionary(schema)

    data_dictionary = st.session_state["data_dictionary"]

    for table, data in schema.items():

        st.subheader(table)

        rows = []

        for col, meta in data["columns"].items():

            rows.append({
                "Column": col,
                "Type": meta["dtype"],
                "Description": data_dictionary.get(table, {}).get(col, "")
            })

        st.table(rows)

# LEFT AND RIGHT DIVISION (60-40) FOR INTERACTIVE DIAGRAM AND SCHEMA SUMMARY
    left_col,right_col = st.columns([3,2])

# ER DIAGRAM AND KNOWLEDGE BASED DIAGRAM
    with left_col:
            st.subheader("Database Graph")
            view = st.radio(
                label="Graph View",
                options=[ "Knowledge Graph", "ER Diagram"],
                horizontal=True,
                label_visibility="collapsed"
            )

            if view == "Knowledge Graph":
                net = build_graph(schema, tables)
                net.save_graph("graph.html")

                HtmlFile = open("graph.html", "r", encoding="utf-8")
                components.html(HtmlFile.read(), height=650)
            else:
                er = build_er_diagram(schema)
                st.graphviz_chart(er, use_container_width=True, height=650)

# DATABASE SCHEMA 
    with right_col:
        st.subheader("Database Schema")
        with st.container(height=700):
                for table_name, table_data in schema.items():

                    st.markdown(f"**{table_name} ({table_data['rows']} rows)**")

                    df_schema = pd.DataFrame.from_dict(
                        table_data["columns"],
                        orient="index"
                    ).reset_index()

                    df_schema.rename(columns={
                        "index": "Column",
                        "dtype": "Type",
                        "constraints": "Constraints"
                    }, inplace=True)

                    df_schema = df_schema[["Column", "Type", "Constraints"]]
                    st.table(df_schema)

# DATA QUALITY METRICS
    st.markdown("### Data Quality Metrics")

    dq_summary = generate_data_quality(tables)

    dq_table = []

    for table, metrics in dq_summary.items():
        dq_table.append({
            "Table": table,
            "Rows": metrics["rows"],
            "Columns": metrics["columns"],
            "Completeness %": metrics["completeness"],
            "Duplicates": metrics["duplicates"],
            "Duplicates Rate % ": metrics["duplicate_rate"],
            "Null-heavy cols": len(metrics["null_heavy_cols"]),
            "Numeric Columns": metrics['numeric_cols'],
            "Categorical Columns":metrics["categorical_cols"],
            "Memory MB": metrics["memory_usage_mb"]
        })

    dq_df = pd.DataFrame(dq_table)

    st.dataframe(dq_df, use_container_width=True)
    
# BUSINESS INSIGHTS 
    st.markdown("### Business Insights (AI Generated)")

    with st.container():
        if "ai_insights" not in st.session_state:
            with st.spinner("Generating AI insights..."):
                st.session_state["ai_insights"] = generate_business_insights(dq_summary)

        ai_insights = st.session_state["ai_insights"]

        st.markdown(ai_insights)

# REPORT GENERATION (MARKDOWN -> PDF)
    md_report = generate_markdown_report(
    summary,
    schema,
    dq_summary,
    ai_insights,
    data_dictionary
    )

    pdf_path = convert_to_pdf(md_report)

    with open(pdf_path, "rb") as f:
        st.download_button(
            label="Download Full Report",
            data=f,
            file_name="database_report.pdf",
            mime="application/pdf"
        )