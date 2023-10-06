import pandas as pd

import streamlit as stm

stm.set_page_config(page_title="AAA project")
stm.title("This is a Gant Chart.")
stm.sidebar.success("Select Any Page from here")

import plotly.express as px


df = pd.DataFrame([
    dict(Task="Job A", Start='2009-01-01', Finish='2009-02-28', Completion_pct=50),
    dict(Task="Job B", Start='2009-03-05', Finish='2009-04-15', Completion_pct=25),
    dict(Task="Job C", Start='2009-02-20', Finish='2009-05-30', Completion_pct=75)
])

edited_df = stm.data_editor(df, num_rows="dynamic")
stm.markdown(f"Your favorite command is  🎈")

fig = px.timeline(edited_df, x_start="Start", x_end="Finish", y="Task", color="Completion_pct")
fig.update_yaxes(autorange="reversed")
stm.plotly_chart(fig, use_container_width=True)