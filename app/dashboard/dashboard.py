import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

df = pd.read_csv('Ontario_PACE_data.csv')
df2 = pd.read_csv('sample_test_data.csv')
app = dash.Dash(__name__)
name_options = []
df['Participant Fullname'] = df['Participant Firstname'] + ' ' + df['Participant Last Name']
for name in df['Participant Fullname']:
    name_options.append({'label': str(name), 'value': name})
app.layout = html.Div([dash_table.DataTable(
    id='table',
    columns=[{'name': i, 'id': i} for i in df.columns if i != 'Participant Fullname' if i != 'Participant Birthdate'],
    data=df.to_dict('records'),
),
    dcc.Graph(id='graph'),
    dcc.Dropdown(id='student-picker', options=name_options, value=df['Participant Fullname'][0])
])


@app.callback(Output('graph', 'figure'), [Input('student-picker', 'value')])
def update_figure(selected_name):
    df2['Participant Fullname'] = df2['Participant Firstname'] + ' ' + df2['Participant Last Name']
    filtered_df2 = df2[df2['Participant Fullname'] == selected_name]
    filtered_df2.drop(['Participant Firstname'], ['Participant Last Name'], axis=1, inplace=True)
    filtered_df2.set_index('Participant Fullname', inplace=True)
    trace = [go.Scatter(x=filtered_df2.columns, y=filtered_df2.loc[name], mode='lines', name=name) for name in filtered_df2.index]
    return {'data': trace, 'layout': go.Layout(title='Student Test Scores', xaxis={'title': 'dates'}, yaxis={'title': 'Test Score Percentage'})}


if __name__ == '__main__':
    app.run_server(debug=True)
