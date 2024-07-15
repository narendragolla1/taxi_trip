import streamlit as st
import pandas as pd
import sqlite3
from streamlit_ace import st_ace
from streamlit import toggle as st_toggle_switch


# Function to execute SQL query and fetch results
def execute_query(query, conn):
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except sqlite3.Error as e:
        st.error(f"SQLite Error: {e}")
        return None
    except pd.io.sql.DatabaseError as e:
        st.error(f"Pandas SQL Error: {e}")
        return None
    except Exception as e:  # Catch any other unexpected errors
        st.error(f"Unexpected Error: {e}")
        return None



# Function to establish database connection
def get_db_connection(db_file=None):  # Allow optional db_file argument
    if db_file:
        return sqlite3.connect(db_file.name)  # Use db_file.name if provided
    else:
        return sqlite3.connect("tripdata.db")


# Main Streamlit app
def main():
    st.title("Trip Taxi")

    # File uploader for SQLite database
    db_file = st.file_uploader(
        "Upload SQLite Database (Optional - a default DB is available)", type=["db"]
    )

    if True:
        conn = get_db_connection(db_file)

        # SQL editor with placeholder and options
        query = st_ace(
            placeholder="Enter your SQL query here...",
            language="sql",
            theme="github",
            keybinding="vscode",
            font_size=14,
            height=200,
        )
        
        #Toggle buttons
        show_db_schema = st_toggle_switch(label="Show DB Schema")
        show_tables = st_toggle_switch(label="Show Tables")

        if show_db_schema:
            # Show database schema using sqlite_master table
            schema_df = execute_query("SELECT * FROM sqlite_master;", conn)
            st.subheader("Database Schema:")
            st.dataframe(schema_df)
        
        if show_tables:
            # Show available tables in the database
            tables_df = execute_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
            st.subheader("Tables:")
            st.dataframe(tables_df)

        # Execute button
        if st.button("Execute Query") and query:
            result_df = execute_query(query, conn)

            if result_df is not None:
                st.subheader("Query Results:")
                if not result_df.empty:
                    st.dataframe(result_df)
                else:
                    st.info("Query executed successfully, but no results found.")
        conn.close() # Close the connection after use to prevent resource leaks.

if __name__ == "__main__":
    main()
