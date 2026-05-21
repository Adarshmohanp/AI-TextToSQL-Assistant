import streamlit as st

from langchain_community.utilities import SQLDatabase

from langchain_core.prompts import ChatPromptTemplate

from langchain_core.output_parsers import StrOutputParser

from langchain_core.runnables import RunnablePassthrough

from langchain_groq import ChatGroq

import os


# =====================================
# GROQ API KEY
# =====================================

os.environ["GROQ_API_KEY"] = "your groq api key"  # Replace with your actual Groq API key


# =====================================
# LOAD GROQ MODEL
# =====================================

llm = ChatGroq(
    groq_api_key=os.environ["GROQ_API_KEY"],
    model_name="llama-3.3-70b-versatile"
)


# =====================================
# CONNECT MYSQL DATABASE
# =====================================

host = 'localhost'
port = '3306'

username = 'adarsh'

password = 'adarsh123'

database_schema = 'text_to_sql'

mysql_uri = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database_schema}"

db = SQLDatabase.from_uri(
    mysql_uri,
    sample_rows_in_table_info=2
)


# =====================================
# GET SCHEMA
# =====================================

def get_schema(_):
    return db.get_table_info()


# =====================================
# PROMPT TEMPLATE
# =====================================

template = """
You are an expert SQL query generator.

The database name is: text_to_sql

Based on the table schema below, write a SQL query that answers the user's question.

Rules:
- Return ONLY SQL query
- Do not add explanation
- Do not add markdown
- Write query in single line

Table Schema:
{schema}

Question:
{question}

SQL Query:
"""

prompt = ChatPromptTemplate.from_template(template)


# =====================================
# SQL CHAIN
# =====================================

sql_chain = (
    RunnablePassthrough.assign(
        schema=get_schema
    )
    | prompt
    | llm
    | StrOutputParser()
)


# =====================================
# STREAMLIT UI
# =====================================

st.title("AI Powered Text-to-SQL Assistant")

st.write("Ask questions from your MySQL database using natural language.")


# User Input
user_question = st.text_input("Enter your question:")


# Button
if st.button("Generate SQL"):

    if user_question:

        try:

            # Generate SQL
            response = sql_chain.invoke({
                "question": user_question
            })

            st.subheader("Generated SQL Query")

            st.code(response, language="sql")


            # Execute SQL
            result = db.run(response)

            st.subheader("Database Result")

            st.write(result)

        except Exception as e:

            st.error(f"Error: {e}")