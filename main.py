import pandas as pd

import streamlit as stm

stm.set_page_config(page_title="AAA project")
stm.title("This is a Gant Chart.")
stm.sidebar.success("Select Any Page from here")

import plotly.express as px


df = pd.DataFrame([
    dict(Task="Role Selection", Start='2023-09-05', Finish='2023-09-13', Completion_pct=100),
    dict(Task="First Meeting", Start='2023-09-19', Finish='2023-09-20', Completion_pct=100),
    dict(Task="Project Proposal", Start='2023-10-02', Finish='2023-10-10', Completion_pct=75)
])

edited_df = stm.data_editor(df, num_rows="dynamic")
# stm.markdown(f"Your favorite command is  🎈")

fig = px.timeline(edited_df, x_start="Start", x_end="Finish", y="Task", color="Completion_pct")
fig.update_yaxes(autorange="reversed")
stm.plotly_chart(fig, use_container_width=True)