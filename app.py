import pandas as pd
import numpy as np
import folium
import openpyxl
import plotly.express as px
import plotly.graph_objects as go
import dash_table
import dash
from dash import dcc, html, Dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

df_al_shab = pd.read_csv('https://raw.githubusercontent.com/dakotaroark/render/main/al_shab.csv')
target_types = pd.DataFrame(df_al_shab['targtype1_txt'].value_counts())
target_types = target_types.reset_index()
target_types1 = target_types.rename(columns = {'targtype1_txt': 'occurrences'})
target_types = target_types1.rename(columns = {'index': 'targtype1_txt'})
caus_df = df_al_shab.groupby('targtype1_txt', as_index=False)['ncasualities'].sum()
target_breakdown = pd.merge(target_types, caus_df, on = 'targtype1_txt')
target_breakdown['casualities_per_attack'] = target_breakdown['ncasualities']/target_breakdown['occurrences']

colors = {
    'background': '#111111',
    'text': '#ffffff'
}
fig_attacktargets = fig = px.bar(target_breakdown, x = 'ncasualities', y = 'targtype1_txt', color = 'casualities_per_attack', hover_data = ['occurrences'], 
labels = {'targtype1_txt': 'Target Type', 'ncasualities': 'Number of Casualities', 'casualities_per_attack': 'Casualities Per Attack'})
fig.update_layout(barmode = 'stack', yaxis ={'categoryorder': 'total descending'})
fig.update_layout(title = dict(text = 'Number of Casualities by Attack Target', font = dict(size = 25)))
fig.update_layout(
    title_font_family = 'Times New Roman',
    title_font_color = '#ffffff',
    title_x = 0.5)
fig.update_layout(
    plot_bgcolor = colors['background'],
    paper_bgcolor = colors['background'],
    font_color = colors['text'])

weapon_types = pd.DataFrame(df_al_shab['weapsubtype1_txt'].value_counts()).reset_index()
weapon_types1 = weapon_types.rename(columns = {'weapsubtype1_txt': 'occurrences'})
weapon_types = weapon_types1.rename(columns = {'index': 'weapsubtype1_txt'})
weapon_casualities = df_al_shab.groupby('weapsubtype1_txt', as_index=False)['ncasualities'].sum()
weapon_breakdown = pd.merge(weapon_types, weapon_casualities, on = 'weapsubtype1_txt')
weapon_breakdown['casualities_per_weapon'] = weapon_breakdown['ncasualities']/weapon_breakdown['occurrences']

fig_casualities = fig = px.bar(weapon_breakdown, x = 'ncasualities', y = 'weapsubtype1_txt', color = 'casualities_per_weapon', hover_data = ['occurrences'], 
labels = {'weapsubtype1_txt': 'Weapon Type', 'ncasualities': 'Number of Casualities', 'casualities_per_weapon': 'Casualities per occurrences'})
fig.update_layout(barmode = 'stack', yaxis ={'categoryorder': 'total descending'})
fig.update_layout(title = dict(text = 'Number of Casualities by Attack Method', font = dict(size = 25)))
fig.update_layout(
    title_font_family = 'Times New Roman',
    title_font_color = '#ffffff',
    title_x = 0.5
)
fig.update_layout(
    plot_bgcolor = colors['background'],
    paper_bgcolor = colors['background'],
    font_color = colors['text']
)


dash_df = df_al_shab[['date', 'city', 'ncasualities', 'weapsubtype1_txt','targtype1_txt', 'scite1']]
rename_dict = {'date':'Date', 'city':'City', 'ncasualities': 'Casualties', 'weapsubtype1_txt': 'Weapon Type', 'targtype1_txt':'Target Type', 'scite1': 'Site'}
dash_df = dash_df.rename(columns=rename_dict)

dash_df['Weapon Type'] = dash_df['Weapon Type'].fillna('Unknown')

total_casualties = df_al_shab['ncasualities'].sum()
total_attacks = len(df_al_shab)
weapon_type = df_al_shab['weaptype1_txt'].mode()[0]

def create_card(header, value, color):
    return dbc.Col(
        dbc.Card(
            [
                dbc.CardHeader(header),
                dbc.CardBody(
                    [
                        html.H4(f"{value}", className="card-title"),
                    ]
                ),
            ],
            color=color,
            inverse=True,
        ),
        width=4,
    )

cards = [
    create_card("Total Casualties", total_casualties, "danger"),
    create_card("Total Attacks", total_attacks, "orange"),
    create_card("Most used Weapon Type", weapon_type, "purple")
]

# Create the row of cards
card_row = dbc.Row(cards, className="mb-4")

card_row = dbc.Row(cards, className="mb-4")

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

colors = {
    'background': '#111111',
    'text': '#ffffff'
}

grouped_df = df_al_shab.groupby(['eventid','date','city', 'targsubtype1_txt','weapsubtype1_txt', 'latitude', 'longitude'])['ncasualities'].sum()
grouped_df = grouped_df.reset_index()

# Adding folium map in the code
def create_map():
    my_map = folium.Map(location=[5.152149, 46.199616], zoom_start=6)

    def marker_colors(ncasualities):
        if ncasualities > 30:
            return '#ff0000'
        elif ncasualities > 10:
            return '#ffb84d'
        elif ncasualities > 5:
            return '#ffff00'
        elif ncasualities > 0:
            return '#996600'
        else:
            return '#33cc33'

    # Create a dictionary to map color values to corresponding labels for the legend
    legend_labels = {
        'High Casualties': '#ff0000',
        'Moderate to High Casualties': '#ffb84d',
        'Moderate Casualties': '#ffff00',
        'Low Casualties': '#996600',
        'No Casualties': '#33cc33'
    }

    for _, row in grouped_df.iterrows():
        latitude = row['latitude']
        longitude = row['longitude']
        ncasualities = row['ncasualities']
        date = row['date']
        weapsubtype1_txt = row['weapsubtype1_txt']

        tooltip_text = f"Date: {date}<br>Weapon Type: {weapsubtype1_txt}<br>Casualties: {ncasualities}"

        marker_color = marker_colors(ncasualities)

        folium.CircleMarker(
            location=[latitude, longitude],
            radius=2,
            weight=5,
            color=marker_color,
            tooltip=tooltip_text
        ).add_to(my_map)

    # Create the legend
    legend_html = '''
        <div style="position: absolute; 
                    top: 20px; right: 20px; width: 120px; 
                    height: 220px; border:2px solid grey; 
                    z-index:9999; font-size:12px;
                    background-color:white;
                    opacity: 0.8;
                    ">
            <p style="text-align:center; margin-top: 10px;"><strong>Legend</strong></p>
            '''
    for label, color in legend_labels.items():
        legend_html += f'''
            <div style="display: flex; align-items: center; margin: 5px;">
                <div style="background-color:{color}; width: 20px; height: 20px; 
                            margin-right: 5px; border:1px solid grey;"></div>
                <div>{label}</div>
            </div>
            '''
    legend_html += '</div>' 
    my_map.get_root().html.add_child(folium.Element(legend_html))

    return my_map._repr_html_()



# Define the layout
app.layout = html.Div(
    style={'backgroundColor': colors['background']},
    children=[
        html.H1(
            children='Al-Shabaab Attack Dashboard',
            style={
                'textAlign': 'left',
                'color': colors['text']
            }
        ),

        html.Div(
            children='Data is from 2021, thanks to START from Univeristy of Maryland',
            style={
                'textAlign': 'left',
                'color': colors['text']
            }
        ),

        html.Div(
            children=dbc.Container([card_row], fluid=True),
        ),
        dcc.Tabs(
            id='tabs',
            value='tab-1',
            style={'backgroundColor': colors['background'], 'color': colors['text']},
            children=[
                dcc.Tab(
                    label='Plots',
                    value='tab-1',
                    style={'backgroundColor': colors['background'], 'color': colors['text']},
                    children=[
                        html.Div(
                            dcc.Graph(figure=fig_attacktargets),
                            className='six columns'
                        ),
                        html.Div(
                            dcc.Graph(figure=fig_casualities),
                            className='six columns'
                        )
                    ]
                ),
                dcc.Tab(
                    label='Map',
                    value='tab-2',
                    style={'backgroundColor': colors['background'], 'color': colors['text']},
                    children=[
                        html.Iframe(
                            id='map-iframe',
                            srcDoc=create_map(),
                            width='100%',
                            height='600px'
                        )
                    ]
                ),
                dcc.Tab(
                    label='Data',
                    value='tab-3',
                    style={'backgroundColor': colors['background'], 'color': colors['text']},
                    children=[
                        html.Div(
                            dash_table.DataTable(
                                id='datatable',
                                columns=[{'name': col, 'id': col} for col in dash_df.columns],
                                data=dash_df.to_dict('records'),
                                style_cell={
                                    'backgroundColor': '#1e2130',
                                    'color': '#ffffff',
                                    'textAlign': 'left',
                                    'maxWidth': '150px',
                                    'overflow': 'hidden',
                                    'textOverflow': 'ellipsis',
                                    'whitespace': 'nowrap'
                                },
                                style_header={
                                    'backgroundColor': '#111111',
                                    'fontWeight': 'bold'
                                },
                                tooltip_data=[
                                    {
                                        column: {'value': str(value), 'type':'text'}
                                        for column, value in row.items()
                                    } for row in dash_df.to_dict('rows')
                                ],
                                tooltip_duration=None,
                                filter_action='native', 
                                sort_action='native',    
                                sort_mode='multi',       
                                page_action='native',    
                                page_current=0,          
                                page_size=10              
                            ),
                            className='six columns', 
                            style={'margin': '20px'}
                        )
                    ]
                )
            ]
        ),
        html.Div(id='tab-content')
    ]
)


# Run the Dash application
if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)
