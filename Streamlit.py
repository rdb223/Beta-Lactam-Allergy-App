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
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator, DataStructs

# Load and prepare the dataset
file_path = 'cross_reactivity_analysis.xlsx'
data = pd.read_excel(file_path, 'Sheet1')
cross_reactivity_data = data[['Drug1', 'Drug2', 'Cross_Reactivity_Label', 'SMILES_Drug1_x', 'SMILES_Drug2_x']]

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
        drug1_smiles = filtered_data['SMILES_Drug1_x'].values[0]
        drug2_smiles = filtered_data['SMILES_Drug2_x'].values[0]

        # Tanimoto Similarity Calculation
        if pd.notna(drug1_smiles) and pd.notna(drug2_smiles):
            drug1_mol = Chem.MolFromSmiles(drug1_smiles)
            drug2_mol = Chem.MolFromSmiles(drug2_smiles)

            if drug1_mol is None or drug2_mol is None:
                st.warning("Unable to generate molecule from SMILES for one or both drugs. Please verify the SMILES strings.")
            else:
                # Proceed with fingerprint generation and similarity calculation
                fp_gen = rdFingerprintGenerator.GetMorganGenerator(fpSize=2048, radius=2)
                drug1_fp = fp_gen.GetFingerprint(drug1_mol)
                drug2_fp = fp_gen.GetFingerprint(drug2_mol)
                tanimoto_similarity = DataStructs.TanimotoSimilarity(drug1_fp, drug2_fp)

                # Display Tanimoto Similarity
                st.write('---')
                st.subheader('Tanimoto Similarity Coefficient')
                st.write(f'Tanimoto Similarity between **{drug1}** and **{drug2}**: {tanimoto_similarity:.2f}')
                st.markdown(
                    """
                    **What does this mean?**
                    - A Tanimoto Similarity score close to **1** indicates that the two molecules are very similar in structure.
                    - A score close to **0** indicates that the molecules are structurally very different.
                    """
                )
        else:
            st.warning('SMILES data is not available for one or both selected drugs, so Tanimoto similarity cannot be calculated.')

        # Display Cross-Reactivity Information
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
