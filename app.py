# -*- coding: utf-8 -*-
"""Copy of beta-lactam-allergy-app

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1IoBhY0OHWeo9hRqf00E_5FPalqhYkcTm
"""

# app.py
import dash
from dash import dcc, html, Input, Output
import pandas as pd

# Load and prepare the dataset
file_path = 'cross_reactivity_analysis.xlsx'
data = pd.read_excel(file_path, 'Sheet1')
cross_reactivity_data = data[['Drug1', 'Drug2', 'Cross_Reactivity_Label']]

# Create a Dash application
app = dash.Dash(__name__)
server = app.server  # Expose the server variable for deployment

# Define the layout of the application
app.layout = html.Div([
    html.H1('Antibiotic Cross-Reactivity Checker'),
    html.Label('Select Drug 1:'),
    dcc.Dropdown(
        id='drug1-dropdown',
        options=[{'label': drug, 'value': drug} for drug in cross_reactivity_data['Drug1'].unique()],
        value=None
    ),
    html.Label('Select Drug 2:'),
    dcc.Dropdown(
        id='drug2-dropdown',
        options=[{'label': drug, 'value': drug} for drug in cross_reactivity_data['Drug2'].unique()],
        value=None
    ),
    html.Br(),
    html.Div(id='output-container', style={'fontSize': 18, 'marginTop': 20})
])

# Define the callback to update the output based on user input
@app.callback(
    Output('output-container', 'children'),
    [Input('drug1-dropdown', 'value'),
     Input('drug2-dropdown', 'value')]
)
def update_output(drug1, drug2):
    if drug1 is None or drug2 is None:
        return 'Please select both drugs to check cross-reactivity.'

    # Filter the dataset to find the cross-reactivity label
    filtered_data = cross_reactivity_data[(cross_reactivity_data['Drug1'] == drug1) &
                                          (cross_reactivity_data['Drug2'] == drug2)]

    if filtered_data.empty:
        return 'No data available for the selected drugs.'

    label = filtered_data['Cross_Reactivity_Label'].values[0]
    if label == 0:
        return 'No cross-reactivity expected.'
    elif label == 1:
        return 'Probable cross-reactivity.'
    elif label == 2:
        return 'Possible cross-reactivity.'
    else:
        return 'Unknown cross-reactivity label.'

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)

