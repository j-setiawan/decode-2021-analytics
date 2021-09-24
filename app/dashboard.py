import json
from random import randrange

import dash
import pandas as pd
import plotly.graph_objs as go
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output

from eventing.mqtt import MqttClient

genders = ['Female', 'Male', 'LGBTQ', 'Other']
languages = ['English', 'French', 'Mandarin', 'Tagalog', 'Hindi', 'Punjabi', 'Swahili']
centres = ['East York', 'Durham', 'Guelph', 'Kitchener', 'Meadowvale', 'Richmond Hill', 'Willowdale']
table_columns = ['Student_ID', 'name', 'centre', 'gender', 'grade', 'ESL/FSL', 'native language']
graph_axis = ['10-30-2020', '12-15-2020', '1-10-2020', '2-5-2020', '3-10-2020', '4-5-2020']


def on_message(client, userdata, msg):
    print(f'Message received on topic: {msg.topic}. Message: {msg.payload}')

    if msg.topic.startswith('user'):
        student = json.loads(msg.payload.decode('utf-8'))
        students.append({
            'Student_ID': student['id'],
            'centre': centres[randrange(len(centres))],
            'name': student['name'],
            'gender': genders[randrange(len(genders))],
            'grade': f'Grade {randrange(1, 8)}',
            'ESL/FSL': 'Yes' if randrange(0, 2) == 1 else 'No',
            'native language': languages[randrange(len(languages))],
        })

        grades.append({
            'name': student['name'],
            '10-30-2020': randrange(0, 101),
            '12-15-2020': randrange(0, 101),
            '1-10-2020': randrange(0, 101),
            '2-5-2020': randrange(0, 101),
            '3-10-2020': randrange(0, 101),
            '4-5-2020': randrange(0, 101),
        })

        name_options.append({'label': student['name'], 'value': student['name']})


with open('mqtt.properties') as fp:
    lines = fp.readlines()
    hostname = lines[0].strip()
    username = lines[1].strip()
    password = lines[2].strip()

mqtt = MqttClient(hostname, username, password, on_message)

students = []
name_options = []
grades = []

app = dash.Dash(__name__)

app.layout = html.Div([dash_table.DataTable(
    id='table',
    columns=[{'name': i, 'id': i} for i in table_columns],
    data=students,
),
    dcc.Graph(id='graph'),
    dcc.Dropdown(id='student-picker', options=name_options),
    dcc.Interval(
        id='interval-component',
        interval=1 * 1000,  # in milliseconds
        n_intervals=0
    )
])


@app.callback(Output('table', 'data'),
              Input('interval-component', 'n_intervals'))
def update_table(n):
    return students


@app.callback(Output('graph', 'figure'),
              Input('student-picker', 'value'),
              Input('interval-component', 'n_intervals'))
def update_graph(selected, n):
    if selected is not None:
        grade = [g for g in grades if g['name'] == selected][0]
        trace = [go.Bar(x=graph_axis, y=[v for k, v in grade.items() if k != 'name'], name=grade['name'])]
    else:
        trace = [go.Bar(x=graph_axis, y=[v for k, v in grade.items() if k != 'name'], name=grade['name']) for grade in grades]

    return {'data': trace, 'layout': go.Layout(title='Student Test Scores', xaxis={'title': 'dates'}, yaxis={'title': 'Test Score Percentage'})}


@app.callback(Output('student-picker', 'options'),
              Input('interval-component', 'n_intervals'))
def update_picker(n):
    return name_options


if __name__ == '__main__':
    app.run_server(host="0.0.0.0", debug=True)
