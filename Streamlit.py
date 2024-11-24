# -*- coding: utf-8 -*-
# Refactored beta-lactam-allergy-app for Streamlit
import os

# Ensure openpyxl is installed
try:
    import openpyxl
except ImportError:
    os.system('pip install openpyxl')

import streamlit as st
import pandas as pd

# Load and prepare the dataset
file_path = 'cross_reactivity_analysis.xlsx'
data = pd.read_excel(file_path, 'Sheet1')
cross_reactivity_data = data[['Drug1', 'Drug2', 'Cross_Reactivity_Label']]

# Streamlit app layout
st.title('Antibiotic Cross-Reactivity Checker')

# Select Drug 1
drug1 = st.selectbox(
    'Antimicrobial patient reports allergy to:',
    options=cross_reactivity_data['Drug1'].unique()
)

# Select Drug 2
drug2 = st.selectbox(
    'Antimicrobial you want to use:',
    options=cross_reactivity_data['Drug2'].unique()
)

# Display the result
if drug1 and drug2:
    # Filter the dataset to find the cross-reactivity label
    filtered_data = cross_reactivity_data[
        (cross_reactivity_data['Drug1'] == drug1) &
        (cross_reactivity_data['Drug2'] == drug2)
    ]

    if filtered_data.empty:
        st.write('No data available for the selected drugs.')
    else:
        label = filtered_data['Cross_Reactivity_Label'].values[0]
        if label == 0:
            st.success('<2% chance of cross-reactivity expected')
        elif label == 1:
            st.markdown('<div style="background-color:#ffdddd; padding:10px; border-radius:5px;"><strong style="color:red;">⚠️ 20-40% chance of cross-reactivity. Consider another agent or utilizing a test dose.</strong></div>', unsafe_allow_html=True)
            # Provide alternatives with a cross-reactivity rating of 0 or 2
            alternative_data = cross_reactivity_data[(cross_reactivity_data['Drug1'] == drug1) & (cross_reactivity_data['Cross_Reactivity_Label'] != 1)]
            if not alternative_data.empty:
                st.write('---')
                if (alternative_data['Cross_Reactivity_Label'] == 0).any():
                    st.markdown('### <2% Cross-Reactivity Expected:')
                    for _, row in alternative_data[alternative_data['Cross_Reactivity_Label'] == 0].iterrows():
                        st.write(f'- **{row["Drug2"]}**')
                if (alternative_data['Cross_Reactivity_Label'] == 2).any():
                    st.markdown('### Possible Cross-Reactivity:')
                    for _, row in alternative_data[alternative_data['Cross_Reactivity_Label'] == 2].iterrows():
                        st.write(f'- **{row["Drug2"]}**')
        elif label == 2:
            st.info('Possible cross-reactivity')
        else:
            st.error('Unknown cross-reactivity label.')
else:
    st.write('Please select both drugs to check cross-reactivity.')
