import dash
import dash_bootstrap_components as dbc
from dash import Dash, dash_table, Input, Output, callback, dcc, html
import plotly.express as px
import pandas as pd
import utilities.dataframes as dfs

years, decades = dfs.years, dfs.decades

app = Dash(external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([

	html.Br(),

	dbc.Card(
		dbc.CardBody([
			html.H3('S&P 500 Index', className='display-10'),
			html.Hr(className='my-2'),
			dbc.Row([
				dbc.Col(html.P('Historical Returns', className='lead'))
			])
		]),
		className='bg-primary text-light rounded-3',
	),

	dcc.Graph(
		figure={},
		id='chart',
		config={'displayModeBar': False}
	),
	
	dcc.RangeSlider(
		min=years[0],
		max=years[1],
		value=years,
		step=1,
		allowCross=False, 
        marks={x: {'label': str(x)} for x in decades}, 
        tooltip={'placement': 'bottom', 'always_visible': True},
        id='slider'
    ),

	html.Br(),

	dbc.Row(
		dbc.Col(
			dbc.Card([
				dbc.CardHeader(
					html.P(children='', id='label', className='card-text text-center')
				),
				dbc.CardBody(
					dash_table.DataTable(
						data=[],
						style_header={'text-align': 'center'},
						style_cell_conditional=[
							{'if': {'column_id': 'Measure'}, 'textAlign': 'left'},
							{'if': {'column_id': 'Start'}, 'width': '15%'},
							{'if': {'column_id': 'End'}, 'width': '15%'},
							{'if': {'column_id': 'Multiple'}, 'width': '15%'},
							{'if': {'column_id': 'CAGR'}, 'width': '15%'}
						],
						columns=[
							{'name': 'Measure', 'id': 'Measure'},
							{'name': 'Start', 'id': 'Start', 'type': 'numeric',
								'format': {'specifier': ',.1f', 'locale': {'group': ',', 'decimal': '.'}}},
							{'name': 'End', 'id': 'End', 'type': 'numeric',
								'format': {'specifier': ',.1f', 'locale': {'group': ',', 'decimal': '.'}}},
							{'name': 'Multiple', 'id': 'Multiple', 'type': 'numeric',
								'format': {'specifier': ',.1f', 'locale': {'group': ',', 'decimal': '.'}}},
							{'name': 'CAGR', 'id': 'CAGR', 'type': 'numeric',
								'format': {'specifier': '.1%'}},
						],
						id='table'
					)
				)
			]), width=6
		), justify='center'
	)

])

@callback(
	Output(component_id='chart', component_property='figure'),
	Output(component_id='table', component_property='data'),
	Output(component_id='label', component_property='children'),
	Input(component_id='slider', component_property='value')
)
def chart_update(value):
	dff = dfs.dataframe_filter(value)
	figure = px.line(dff, x='Date', y='S&P 500 Index')
	figure.update_layout(
		xaxis_title='Year',
		yaxis_title='Index',
		yaxis_tickformat = ',.0f'
	)

	dftr = dfs.table_returns(value)
	data = dftr.to_dict('records')

	label = f'S&P 500 Index - {value[1] - value[0]} years from {value[0]} to {value[1]}'
	
	return figure, data, label


if __name__=="__main__":
	app.run_server(debug=True, port=8888)

