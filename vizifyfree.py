# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 07:43:10 2023

@author: 27823
"""

import streamlit as st
from lida import Manager, TextGenerationConfig, llm
from lida.datamodel import Goal
import os
import pandas as pd
from streamlit_extras.grid import grid
from PIL import Image

# make data dir if it doesn't exist
os.makedirs("data", exist_ok=True)

st.set_page_config(
    page_title="vizify",
    page_icon="📊",
    layout="wide"
)

img_logo = Image.open("images/vizifysmall.PNG")
st.image(img_logo)

st.markdown("---")
st.write("Want to upload your own dataset? Upgrade for only €10 per month")

st.link_button("Upgrade", "https://vizify.streamlit.app/")
#from st_paywall import add_auth

#add_auth(required=True)

#Only after authentication and subscription, the user will see this
#st.sidebar.write(f"Subscription Status: {st.session_state.user_subscribed}")
#st.write("Yay! You're all set!")
#st.write(f"By the way, your email is {st.session_state.email}")

# Design hide "made with streamlit" footer menu area
hide_streamlit_footer = """<style>#MainMenu {visibility: hidden;}
                        footer {visibility: hidden;}</style>"""
st.markdown(hide_streamlit_footer, unsafe_allow_html=True)



#lida = Manager(text_gen = llm("openai", api_key="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"))
#textgen_config = TextGenerationConfig(n=1, temperature=0.1, model="gpt-3.5-turbo-16k", use_cache=True)

# Handle dataset selection and upload


datasets = [
    {"label": "Select a dataset", "url": None},
    {"label": "Cars", "url": "https://raw.githubusercontent.com/uwdata/draco/master/data/cars.csv"},
    {"label": "Weather", "url": "https://raw.githubusercontent.com/uwdata/draco/master/data/weather.json"},
]

summary = None
selected_dataset = None

st.sidebar.markdown("---")

selected_dataset_label = st.sidebar.selectbox(
    'Choose a dataset',
    options=[dataset["label"] for dataset in datasets],
    index=0
)



st.sidebar.markdown("---")

st.sidebar.write("FAQs")

st.sidebar.markdown('<div><a href="https://fern-gear-e53.notion.site/Useful-Natural-Language-Personas-for-Visualization-Refinement-69071442df5b498e90b2c348a7e10212?pvs=4" target="_blank">Persona Examples</a></div>', unsafe_allow_html=True)
st.sidebar.markdown('<div><a href="https://fern-gear-e53.notion.site/Natural-Language-Instructions-for-Visualization-Refinement-1396950d456646189e8a118c233cc389?pvs=4" target="_blank">Modify Chart Examples</a></div>', unsafe_allow_html=True)
st.sidebar.markdown('<div><a href="https://fern-gear-e53.notion.site/FAQ-2ad94858e7774de48d979a904db0e1e6?pvs=4" target="_blank">Limitations</a></div>', unsafe_allow_html=True)
st.sidebar.markdown('<div><a href="https://fern-gear-e53.notion.site/Natural-Language-Queries-for-Dataset-fb150202508b42b0a731610302a4bfe3?pvs=4" target="_blank">Query Examples</a></div>', unsafe_allow_html=True)


# Handle the case where the user hasn't selected any dataset
if selected_dataset_label != "Select a dataset":
    selected_dataset = [dataset["url"] for dataset in datasets if dataset["label"] == selected_dataset_label][0]

    # Generate summary only if a dataset is selected
    lida = Manager(text_gen=llm("openai", api_key="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"))
    textgen_config = TextGenerationConfig(n=1, temperature=0.1, model="gpt-3.5-turbo-16k", use_cache=True)

    # Generate the summary
    summary = lida.summarize(
        selected_dataset,
        summary_method="llm",
        textgen_config=textgen_config
    )

if not summary:
    st.info("To continue, select a dataset from the sidebar on the left or upgrade to upload your own.")

# Step 3 - Generate data summary
if selected_dataset:
    lida = Manager(text_gen=llm("openai", api_key="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"))
    textgen_config = TextGenerationConfig(
        n=1,
        temperature=0.1,
        use_cache=True)
    
    with st.expander("Show Dataset"):
        
    # **** lida.summarize *****
        summary = lida.summarize(
            selected_dataset,
            summary_method="llm",
            textgen_config=textgen_config)

        if "dataset_description" in summary:
            st.write(summary["dataset_description"])
    
        if "fields" in summary:
            fields = summary["fields"]
            nfields = []
            for field in fields:
                flatted_fields = {}
                flatted_fields["column"] = field["column"]
                # flatted_fields["dtype"] = field["dtype"]
                for row in field["properties"].keys():
                    if row != "samples":
                        flatted_fields[row] = field["properties"][row]
                    else:
                        flatted_fields[row] = str(field["properties"][row])
                # flatted_fields = {**flatted_fields, **field["properties"]}
                nfields.append(flatted_fields)
            nfields_df = pd.DataFrame(nfields)
            nfields_df_ = st.data_editor(nfields_df, hide_index=True, use_container_width=True)
        else:
            st.write(str(summary))

if summary:
    # **** lida.goals *****
    persona = st.text_input("Describe your persona")
    goals = lida.goals(summary, n=4, textgen_config=textgen_config, persona=persona)
    
    default_goal = goals[0].question
    goal_questions = [goal.question for goal in goals]
    
    # Allow the user to add their own goal
    own_goal = st.checkbox("Add Your Own Query")
    if own_goal:
        user_goal = st.text_input("Describe Your Query")
    
        if user_goal:
            new_goal = Goal(question=user_goal, visualization=user_goal, rationale="")
            goals.append(new_goal)
            goal_questions.append(new_goal.question)
    
    # Create a grid for displaying goals and visualizations
    my_grid = grid( [0.3, 0.6], gap="large", vertical_align="bottom")
    
    # Add a container for each goal
    for goal in goals:
        goal_container = my_grid.container()
            
       # Display goal rationale with a rounded border
        goal_container.markdown(
            f"<div style='border: 2px solid #ddd; padding: 10px; border-radius: 10px;'>⚡ {goal.rationale}</div>",
            unsafe_allow_html=True
        )
    
        with my_grid.container():
            # Step 5 - Generate visualizations
            if goal:
                library = "matplotlib"
    
                textgen_config = TextGenerationConfig(
                    n=1, temperature=0.2,
                    use_cache=True)
    
                visualizations = lida.visualize(
                    summary=summary,
                    goal=goal,
                    textgen_config=textgen_config,
                    library=library
                )
    
                # Check if there are visualizations before trying to access them
                if visualizations:
                    # Display visualizations for each goal
                    for selected_viz in visualizations:
                        # **** lida.visualize *****
                        instructions = st.text_input(f"## Modify Chart for {goal.question}")
                        with st.spinner(text=f'Loading visualization for {goal.question}...'):
                            visualizations_edit = lida.edit(
                                code=selected_viz.code,
                                summary=summary,
                                textgen_config=textgen_config,
                                library=library,
                                instructions=instructions
                            )
    
                        # Assuming there's a specific visualization associated with the selected goal
                        selected_viz_index = 0
    
                        if 0 <= selected_viz_index < len(visualizations_edit):
                            selected_viz = visualizations_edit[selected_viz_index]
    
                            if selected_viz.raster:
                                from PIL import Image
                                import io
                                import base64
    
                                imgdata = base64.b64decode(selected_viz.raster)
                                img = Image.open(io.BytesIO(imgdata))
                                st.image(img, use_column_width=False)
    
                                # Add download button
                                download_button = st.download_button(
                                    label=f"Download Chart ({goal.question})",
                                    data=imgdata,
                                    file_name=f"downloaded_chart_{goal.question}.png",
                                    key=f"download_button_{goal.question}"
                                )
    
                            if download_button:
                                st.success(f"Image downloaded successfully for {goal.question}")
    
                        else:
                            st.warning(f"No visualization found for {goal.question}. Please try another goal.")
    
                else:
                    st.warning(f"No visualizations found for {goal.question}. Please try another goal.")


# Adding a footer
footer = """
    <style>
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #f1f1f1;
            text-align: center;
            padding: 10px;
            display: flex;
            justify-content: space-around;  # equally space the divs
        }
        .footer div {
            flex: 1;  # each div will take up an equal amount of space
            border: 1px solid #ccc;  # just to visualize the divs, can be removed
            padding: 10px;
        }
    </style>
    <div class="footer">
        <div>© Made by <a href="https://masinsightdata.com/">masinsightdata</a> 2023. All rights reserved.</div>
        <div><a href="https://fern-gear-e53.notion.site/masinsightdata-Privacy-Policy-99cc44bdb1e54aa095b4a64ab8218eb3?pvs=4"> Privacy Policy </a></div>
        <div><a href="https://fern-gear-e53.notion.site/masinsightdata-Terms-and-Conditions-b16c6bc067ed4bab9f38167da4445e6f?pvs=4"> Terms and Conditions </a></div>
    </div>
"""
st.markdown(footer, unsafe_allow_html=True)
           
            
            
         
