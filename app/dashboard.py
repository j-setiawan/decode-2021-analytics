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
graph_axis = ['quiz_1', 'quiz_2', 'quiz_3', 'quiz_4', 'quiz_5', 'exam']


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

        for i in range(1, 6):
            lessons[i].append({
                'name': student['name'],
                'exam': randrange(0, 101),
                'quiz_1': randrange(0, 101),
                'quiz_2': randrange(0, 101),
                'quiz_3': randrange(0, 101),
                'quiz_4': randrange(0, 101),
                'quiz_5': randrange(0, 101),
                'happy': randrange(0, 10),
                'sad': randrange(0, 10),
                'neutral': randrange(0, 10),
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
lessons = {1: [], 2: [], 3: [], 4: [], 5: []}

app = dash.Dash(__name__)

app.layout = html.Div([dash_table.DataTable(
    id='table',
    columns=[{'name': i, 'id': i} for i in table_columns],
    data=students,
),
    dcc.Graph(id='graph'),
    dcc.Graph(id='graph2'),
    dcc.Dropdown(id='student-picker', options=name_options),
    dcc.Dropdown(id='lesson-picker', options=[{'label': str(i), 'value': str(i)} for i in range(1, 6)], value='1'),
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
              Input('lesson-picker', 'value'),
              Input('interval-component', 'n_intervals'))
def update_graph(student, lesson, n):
    grades = lessons[int(lesson)]

    if student is not None:
        grade = [g for g in grades if g['name'] == student][0]
        trace = [go.Bar(x=graph_axis, y=[v for k, v in grade.items() if k != 'name'], name=grade['name'])]
    else:
        trace = [go.Bar(x=graph_axis, y=[v for k, v in grade.items() if k != 'name'], name=grade['name']) for grade in grades]

    return {'data': trace, 'layout': go.Layout(title='Student Test Scores', xaxis={'title': 'dates'}, yaxis={'title': 'Test Score Percentage'})}


@app.callback(Output('graph2', 'figure'), [Input('student-picker', 'value'), Input('lesson-picker', 'value')])
def update_figure2(selected_name, selected_lesson):
    lesson = [l for l in lessons[int(selected_lesson)] if l['name'] == selected_name][0]
    data = [go.Bar(x=['happy', 'sad', 'neutral'], y=[v for k, v in lesson.items() if k != 'name'], name=lesson['name'])]
    return {'data': data,
            'layout': go.Layout(title=f'{selected_name} Sentiment for Lesson {selected_lesson}', xaxis={'title': 'Sentiments'}, yaxis={'title': 'Frequency'})}


@app.callback(Output('student-picker', 'options'),
              Input('interval-component', 'n_intervals'))
def update_picker(n):
    return name_options


if __name__ == '__main__':
    app.run_server(host="0.0.0.0", debug=True)
