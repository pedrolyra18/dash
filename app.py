from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

df = pd.read_csv('./education_career_success.csv')

app = Dash(__name__, external_stylesheets=['https://cdn.jsdelivr.net/npm/bootswatch@5.1.3/dist/cyborg/bootstrap.min.css'])

app.layout = html.Div(
    style={'background': 'linear-gradient(135deg, #1a1a1a 0%, #2c2c2c 100%)', 'padding': '40px', 'fontFamily': 'Arial, sans-serif', 'color': '#ffffff', 'minHeight': '100vh'},
    children=[
        html.H1("Dashboard Interativo - Dados de Estudantes", style={'textAlign': 'center', 'color': '#00ccff', 'marginBottom': '40px', 'fontSize': '36px', 'textShadow': '2px 2px 4px rgba(0, 204, 255, 0.3)'}),
        html.Div([
            html.Label("Selecione o Campo de Estudo:", style={'fontSize': '20px', 'marginRight': '15px', 'color': '#00ccff'}),
            dcc.Dropdown(id='field-dropdown', options=[{'label': field, 'value': field} for field in df['Field_of_Study'].unique()], value=df['Field_of_Study'].iloc[0], multi=False, style={'width': '50%', 'backgroundColor': '#333333', 'color': '#000000', 'borderRadius': '8px', 'border': '1px solid #00ccff'}),
            html.Label("Selecione o Gênero:", style={'fontSize': '20px', 'marginLeft': '30px', 'marginRight': '15px', 'color': '#00ccff'}),
            dcc.Dropdown(id='gender-dropdown', options=[{'label': gender, 'value': gender} for gender in df['Gender'].unique()], value=None, multi=True, style={'width': '50%', 'backgroundColor': '#333333', 'color': '#000000', 'borderRadius': '8px', 'border': '1px solid #00ccff'})
        ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '30px', 'alignItems': 'center'}),
        html.H2("Análise Exploratória", style={'textAlign': 'center', 'color': '#00ccff', 'marginBottom': '20px'}),
        html.Div(id='stats-table', style={'marginBottom': '30px', 'textAlign': 'center'}),
        dcc.Graph(id='grafico-histograma'),
        html.P(id='tendencia-texto', style={'textAlign': 'center', 'fontSize': '18px', 'marginTop': '20px'}),
        html.Div([
            html.Div(dcc.Graph(id='grafico-dispersao'), style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%'}),
            html.Div(dcc.Graph(id='grafico-caixa'), style={'width': '48%', 'display': 'inline-block'})
        ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '30px'}),
        html.Div([
            html.Div(dcc.Graph(id='grafico-dispersao-2'), style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%'}),
            html.Div(dcc.Graph(id='grafico-barras-2'), style={'width': '48%', 'display': 'inline-block'})
        ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '30px'}),
        html.Div([
            html.Div(dcc.Graph(id='grafico-pizza'), style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%'}),
            html.Div(dcc.Graph(id='grafico-area'), style={'width': '48%', 'display': 'inline-block'})
        ], style={'display': 'flex', 'justifyContent': 'center'})
    ]
)

@app.callback([
    Output('grafico-dispersao', 'figure'),
    Output('grafico-caixa', 'figure'),
    Output('grafico-dispersao-2', 'figure'),
    Output('grafico-barras-2', 'figure'),
    Output('grafico-pizza', 'figure'),
    Output('grafico-area', 'figure'),
    Output('stats-table', 'children'),
    Output('grafico-histograma', 'figure'),
    Output('tendencia-texto', 'children')
], [Input('field-dropdown', 'value'), Input('gender-dropdown', 'value')])
def atualizar_graficos(field_selecionado, gender_selecionado):
    df_filtrado = df[df['Field_of_Study'] == field_selecionado]
    if gender_selecionado:
        df_filtrado = df_filtrado[df_filtrado['Gender'].isin(gender_selecionado)]
    
    df_filtrado = df_filtrado.dropna()
    
    fig_dispersao = px.scatter(df_filtrado, x='SAT_Score', y='Starting_Salary', color='Gender', title=f'SAT Score vs Salário Inicial - {field_selecionado}', template='plotly_dark')
    fig_caixa = px.box(df_filtrado, x='Current_Job_Level', y='Career_Satisfaction', title='Satisfação na Carreira', template='plotly_dark')
    fig_dispersao_2 = px.scatter(df_filtrado, x='University_GPA', y='Job_Offers', color='Gender', title='Notas vs Ofertas de Emprego', template='plotly_dark')
    fig_barras_2 = px.bar(df_filtrado, x='Field_of_Study', y='Work_Life_Balance', title='Equilíbrio Trabalho-Vida', template='plotly_dark')
    df_entrepreneurship = df_filtrado.groupby(['Entrepreneurship']).size().reset_index(name='Count')
    fig_pizza = px.pie(df_entrepreneurship, names='Entrepreneurship', values='Count', title='Proporção de Empreendedores', template='plotly_dark')
    df_area = df_filtrado.groupby('Networking_Score')['Years_to_Promotion'].mean().reset_index()
    fig_area = px.area(df_area, x='Networking_Score', y='Years_to_Promotion', title='Anos para Promoção vs Networking', template='plotly_dark')
    
    stats = df_filtrado.describe().reset_index().round(2)
    stats_table = html.Table(
        [html.Tr([html.Th(col, style={'border': '1px solid #00ccff', 'padding': '8px'}) for col in stats.columns])] +
        [html.Tr([html.Td(stats.iloc[i][col], style={'border': '1px solid #00ccff', 'padding': '8px'}) for col in stats.columns]) for i in range(len(stats))],
        style={'width': '60%', 'margin': '0 auto', 'backgroundColor': '#333333', 'borderCollapse': 'collapse'}
    )
    
    fig_histograma = px.histogram(df_filtrado, x='SAT_Score', nbins=20, title=f'Distribuição de SAT Score em {field_selecionado}', template='plotly_dark')
    
    correlacao = df_filtrado['SAT_Score'].corr(df_filtrado['Starting_Salary'])
    tendencia = f"Tendência: Em {field_selecionado}, a correlação entre SAT Score e Salário Inicial é de {correlacao:.2f}, sugerindo uma relação positiva."
    
    return fig_dispersao, fig_caixa, fig_dispersao_2, fig_barras_2, fig_pizza, fig_area, stats_table, fig_histograma, tendencia

if __name__ == "__main__":
    app.run(debug=True)
