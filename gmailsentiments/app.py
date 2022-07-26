from itertools import count
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly
import plotly.graph_objs as go
from sqlalchemy import create_engine
from sqlalchemy import text
import psycopg2
import pandas as pd
from dash import Dash, html, dcc,dash_table
import plotly.express as px
import pandas as pd
from collections import Counter
import string
#from cache import cache
#from config import stop_words
import time
import pickle
import numpy as np

#connection to my postgres database in docker
conn = create_engine('postgresql://joric:0809@localhost:5555/gmail', echo=True)


#df = pd.read_sql("SELECT date,subject,sender,snippet,sentiment FROM messages",conn)
app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])


sentiment_colors = {-1:"#EE6055",
                    -0.5:"#FDE74C",
                     0:"#FFE6AC",
                     0.5:"#D0F2DF",
                     1:"#9CEC5B",}


colors = {
    'background': '#0C0F0A',
    'text': '#FFFFFF',
    'sentiment-plot':'#41EAD4',
    'volume-bar':'#FBFC74',
    'someothercolor':'#FF206E',
}

pos_sentiment = 0.05
neg_sentiment = -0.05
MAX_DF_LENGTH = 100




# Build the layout to define what will be displayed on the page
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Live Gmail Sentiment Analysis", className = "text-center text-primary")
        ], width=12)
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='live-graph', animate=True), dcc.Interval(
                id='graph-update',
                interval=1000, # in milliseconds
                n_intervals=-1)
        ], width={"size": 8}),
          
            dbc.Col([
            dcc.Graph(id='sentiment-pie', animate=True), dcc.Interval(
                id='pie-update',
                interval=1000, # in milliseconds
                n_intervals=-1)
        ],width=4)
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id='recent-table'), dcc.Interval(
                id='table-update',
                interval=1000, # in milliseconds
                n_intervals=-1)
        ],width=12)
        ])
])








def quick_color(s):
    # except return bg as app_colors['background']
    if s >= pos_sentiment:
        # positive
        return "#002C0D"
    elif s <= -pos_sentiment:
        # negative:
        return "#270000"

    else:
        return colors['background']


def generate_table(df, max_rows=10):
    return html.Table(className="responsive-table",
                      children=[
                          html.Thead(
                              html.Tr(
                                  children=[
                                      html.Th(col.title()) for col in df.columns.values],
                                  style={'color':colors['text']}
                                  )
                              ),
                          html.Tbody(
                              [
                                  
                              html.Tr(
                                  children=[
                                      html.Td(data) for data in d
                                      ], style={'color':colors['text'],
                                                'background-color':quick_color(d[4])}
                                  )
                               for d in df.values.tolist()])
                          ]
    )



@app.callback(Output('live-graph', 'figure'),
              Input('graph-update','interval'))
              
def update_graph_scatter(n):
    try:
        df = pd.read_sql("SELECT date,subject,sender,snippet,sentiment FROM messages WHERE date > '2022-07-05T19:33:50' ORDER BY date DESC limit 15",conn)
        df.sort_values('date', inplace=True)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df['sentiment_smoothed'] = df['sentiment']
        X = df.index.values
        Y = df.sentiment_smoothed.values
        data = plotly.graph_objs.Scatter(
                x=X,
                y=Y,
                name='Sentiment',
                mode= 'lines+markers',
                line = dict(color = (colors['sentiment-plot']),
                            ))

        return {'data':[data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                          yaxis=dict(range=[min(Y),max(Y)], side='left', overlaying='y',title='sentiment'),
                                                          title="Live Sentiments of Messages",
                                                          font={'color':colors['text']},
                                                          plot_bgcolor = colors['background'],
                                                          paper_bgcolor = colors['background'],
                                                          showlegend=True)}

    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')





@app.callback(Output('recent-table', 'children'),
              Input('table-update','interval'))
def update_recent_messages(n):
        df = pd.read_sql("SELECT date,subject,sender,snippet,sentiment FROM messages ORDER BY date DESC LIMIT 10",conn)
        df['date'] = pd.to_datetime(df['date'], unit='ms')
        return generate_table(df,max_rows=10)






@app.callback(Output('sentiment-pie', 'figure'),
              Input('pie-update','interval'))
def update_pie_chart(n):
    df = pd.read_sql("SELECT date,sentiment FROM messages" ,conn)
    df_pos = df[df["sentiment"] >= 0.05].count()
    df_neg = df[df["sentiment"] <= -0.05].count()

    values = [df_pos.sentiment, df_neg.sentiment]
    labels = ["positive", "negative"]
    colors = ["#002C0D", "#270000"]

    fig = go.Figure()
    fig.add_trace(
        go.Pie(
            labels=labels,
            values=values,
            textposition='inside',
            hoverinfo="label+percent",
            textinfo='percent+label',
            textfont=dict(
                size=20,
                color='#FFFFFF'  # 1st color in colors
            ),
            marker=dict(
                colors=colors,
                line=dict(
                    color='#0C0F0A'  # 2nd color in colors
                )
            )
        )
    )

    fig.update_layout(
        title="Positive vs Negative Sentiment",
        font={"color": '#FFFFFF'},
        plot_bgcolor='#0C0F0A',
        paper_bgcolor='#0C0F0A',
        showlegend=True
    )

    return fig

    
    
'''
    #color_discrete_sequence =['#002C0D']
    labels=['positive','negative']
    
    values = pd.DataFrame(df['pos'],df['neg'])
    
    colors = ['#007F25', '#800000']

    trace = go.Pie(labels=labels,values=values,
                   hoverinfo='label+percent', textinfo='value', 
                   textfont=dict(size=20, color=colors['text']),
                   marker=dict(colors=colors, 
                               line=dict(color=colors['background'])))

    return {"data":[trace],'layout' : go.Layout(
                                                  title='Positive vs Negative sentiment for',
                                                  font={'color':colors['text']},
                                                  plot_bgcolor = colors['background'],
                                                  paper_bgcolor = colors['background'],
                                                  showlegend=True)}'''






external_css = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css"]
for css in external_css:
    app.css.append_css({"external_url": css})


external_js = ['https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/js/materialize.min.js',
               'https://pythonprogramming.net/static/socialsentiment/googleanalytics.js']
for js in external_js:
    app.scripts.append_script({'external_url': js})




































































if __name__ == '__main__':
    app.run_server(debug=True)



