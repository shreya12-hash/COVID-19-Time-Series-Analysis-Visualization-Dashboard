#from app import server
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pycountry
import plotly
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import date 
from datetime import timedelta 
import matplotlib.pyplot as plt
plt.style.use('dark_background')
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
plt.rcParams['figure.figsize'] = [15, 30]
from IPython import display
from ipywidgets import interact, widgets
#from scipy.interpolate import interp1d
## Read Data for Cases, Deaths and Recoveries
ConfirmedCases_raw=pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
Deaths_raw=pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
recoveredcases_raw=pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
country_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv')







o=pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_time.csv",parse_dates=['Last_Update'])
confirmed_df=ConfirmedCases_raw.copy(deep=True)
confirmed_df.drop('Province/State', axis=1, inplace=True)
confirmed_df.rename(columns={'Country/Region': 'Country'}, inplace=True)
confirmed_df2 = pd.melt(confirmed_df, id_vars=['Country', 'Lat', 'Long', ], var_name='Date', value_name='Confirmed_no')
confirmed_df2['Date'] = pd.to_datetime(confirmed_df2['Date'])
death_df=Deaths_raw.copy(deep=True)
death_df.drop('Province/State', axis=1, inplace=True)
death_df.rename(columns={'Country/Region': 'Country'}, inplace=True)
death_df2 = pd.melt(death_df, id_vars=['Country', 'Lat', 'Long', ], var_name='Date', value_name='Death_no')
death_df2['Date'] = pd.to_datetime(death_df2['Date'])
recovered_df=recoveredcases_raw.copy(deep=True)
recovered_df.drop('Province/State', axis=1, inplace=True)
recovered_df.rename(columns={'Country/Region': 'Country'}, inplace=True)
recovered_df2 = pd.melt(recovered_df, id_vars=['Country', 'Lat', 'Long', ], var_name='Date', value_name='Recovered_no')
recovered_df2['Date'] = pd.to_datetime(recovered_df2['Date'])
country_df.drop(['People_Tested', 'People_Hospitalized'], axis=1, inplace=True)
country_df.rename(columns={'Country_Region': 'Country', 'Long_': 'Long'}, inplace=True)
wc_heading = html.H2(id='nav-wc-link', children='COVID-19: Progression of spread', className='mt-5 pb-3 text-center')
df_data = o.groupby(['Last_Update', 'Country_Region'])['Confirmed', 'Deaths'].max().reset_index().fillna(0)
df_data["Last_Update"] = pd.to_datetime( df_data["Last_Update"]).dt.strftime('%m/%d/%Y')
fi_1 = px.choropleth(df_data, locations="Country_Region", locationmode='country names', 
                     color=np.power(df_data["Confirmed"],0.3)-2 , hover_name="Country_Region",
                     hover_data=["Confirmed"],
                     range_color= [0, max(np.power(df_data["Confirmed"],0.3))], 
                      animation_frame="Last_Update",
                     color_continuous_scale=px.colors.sequential.Peach
                    )
fi_1.update_geos(fitbounds="locations", visible=True)
fi_1.update_coloraxes(colorscale="jet")
fi_1.update(layout_coloraxis_showscale=True)
fi_1.update_layout( margin={"r":0,"l":0,"b":0}, height=700,template='plotly_dark')
#fi_1.show()
wd_heading = html.H2(id='nav-wd-link', children='COVID-19:Progression of Death Cases', className='mt-5 pb-3 text-center')
df_data = o.groupby(['Last_Update', 'Country_Region'])['Confirmed', 'Deaths'].max().reset_index().fillna(0)
df_data["Last_Update"] = pd.to_datetime( df_data["Last_Update"]).dt.strftime('%m/%d/%Y')

fi_2 = px.choropleth(df_data, locations="Country_Region", locationmode='country names', 
                     color=np.power(df_data["Deaths"],0.3)-2 , hover_name="Country_Region",
                     hover_data=["Deaths"],
                     range_color= [0, max(np.power(df_data["Deaths"],0.3))], 
                      animation_frame="Last_Update",
                     color_continuous_scale=px.colors.sequential.Plasma
                    )
fi_2.update_geos(fitbounds="locations", visible=True)
fi_2.update_coloraxes(colorscale="hot")
fi_2.update(layout_coloraxis_showscale=True)
fi_2.update_layout( margin={"r":0,"l":0,"b":0}, height=700,template='plotly_dark')
#fi_2.show()





ConfirmedCases=confirmed_df2.rename(columns={'Confirmed_no':'cases'})
Deaths=death_df2.rename(columns={'Death_no':'cases'})
Recoveries=recovered_df2.rename(columns={'Recovered_no':'cases'})
def countrydata(df_cleaned,oldname,newname):
    df_country=df_cleaned.groupby(['Country','Date'])['cases'].sum().reset_index()
    df_country=df_country.set_index(['Country','Date'])
    df_country.index=df_country.index.set_levels([df_country.index.levels[0], pd.to_datetime(df_country.index.levels[1])])
    df_country=df_country.groupby(level=0).fillna(0)
    df_country=df_country.sort_values(['Country','Date'],ascending=True)
    #df_country=df_country.groupby(level=0).fillna(0)
    df_country=df_country.rename(columns={oldname:newname})
    return df_country
  
ConfirmedCasesCountry=countrydata(ConfirmedCases,'cases','Total Confirmed Cases')
DeathsCountry=countrydata(Deaths,'cases','Total Deaths')
RecoveriesCountry=countrydata(Recoveries,'cases','Total Recoveries')

### Get DailyData from Cumulative sum
def dailydata(dfcountry,oldname,newname):
    dfcountrydaily=dfcountry.groupby(level=0).diff().fillna(0)
    dfcountrydaily=dfcountrydaily.rename(columns={oldname:newname})
    return dfcountrydaily
NewCasesCountry=dailydata(ConfirmedCasesCountry,'Total Confirmed Cases','Daily New Cases')
NewDeathsCountry=dailydata(DeathsCountry,'Total Deaths','Daily New Deaths')
NewRecoveriesCountry=dailydata(RecoveriesCountry,'Total Recoveries','Daily New Recoveries')
CountryConsolidated=pd.merge(ConfirmedCasesCountry,NewCasesCountry,how='left',left_index=True,right_index=True)
CountryConsolidated=pd.merge(CountryConsolidated,DeathsCountry,how='left',left_index=True,right_index=True)
CountryConsolidated=pd.merge(CountryConsolidated,NewDeathsCountry,how='left',left_index=True,right_index=True)
CountryConsolidated=pd.merge(CountryConsolidated,RecoveriesCountry,how='left',left_index=True,right_index=True)
CountryConsolidated=pd.merge(CountryConsolidated,NewRecoveriesCountry,how='left',left_index=True,right_index=True)
CountryConsolidated['Active Cases']=CountryConsolidated['Total Confirmed Cases']-CountryConsolidated['Total Deaths']-CountryConsolidated['Total Recoveries']
CountryConsolidated['Share of Recoveries - Closed Cases']=np.round(CountryConsolidated['Total Recoveries']/(CountryConsolidated['Total Recoveries']+CountryConsolidated['Total Deaths']),2)
CountryConsolidated['Death to Cases Ratio']=np.round(CountryConsolidated['Total Deaths']/CountryConsolidated['Total Confirmed Cases'],3)
CountryConsolidated.tail()
u=CountryConsolidated.copy(deep=True)
B=CountryConsolidated.copy(deep=True)
r=CountryConsolidated.loc['India']
#r
u
B=B.reset_index().set_index('Date')



app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title="Corona-Dashboard"
server=app.server






# navbar code
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(html.A("Corona Virus Update", href="#nav-f1", style = {'color': 'yellow'}), className="mr-5"),
        dbc.NavItem(html.A("Most effected", href="#nav-top-country-graph", style = {'color': 'yellow'}), className="mr-5"),
        dbc.NavItem(html.A("Comparison", href="#nav-cr-link", style = {'color': 'yellow'}), className="mr-5"),
    ],
    brand="COVID-19",
    brand_href="/",
    color="black",
    dark=True,
    className="p-3 fixed-top"
)
main_heading = dbc.Container(
[
    html.H1(["COVID-19 Time Series Analysis And Visualization Dashboard"], className="my-5 pt-5 text-center"),
 ]
, className='pt-3')

# what is covid-19

what_is_covid = dbc.Container(
    [
        html.Div([
            html.H2('What is COVID-19?'),
            html.P("A coronavirus is a kind of common virus that causes an infection in your nose, sinuses, or upper throat. Most coronaviruses aren't dangerous."),
            html.P("COVID-19 is a disease that can cause what doctors call a respiratory tract infection. It can affect your upper respiratory tract (sinuses, nose, and throat) or lower respiratory tract (windpipe and lungs). It's caused by a coronavirus named SARS-CoV-2."),
            html.P("It spreads the same way other coronaviruses do, mainly through person-to-person contact. Infections range from mild to serious."),
            html.Span('More information '),
            dcc.Link(' here', href='https://www.who.int/emergencies/diseases/novel-coronavirus-2019')
        ])
    ]
, className="mb-5")
f1_heading = html.H2(id='nav-f1', children='Countrywise COVID-19 Report', className='mt-5 pb-3 text-center')
fc1=B['Country'].unique().tolist()
fc1_list=[]
cl_type=['Total Confirmed Cases', 'Total Deaths','Total Recoveries','Active Cases','Daily New Cases','Daily New Deaths','Daily New Recoveries']
c1_type_list=[]

 
for i in fc1:
    fc1_list.append({'label': i, 'value': i})
    
for i in cl_type:
    c1_type_list.append({'label': i, 'value': i})
#for i in colors:
    #colors_list.append({'label': i, 'value': i})
country_dropdown_1 = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(children = [html.Label('Select Country'), 
                        html.Div(dcc.Dropdown(id = 'select-country-1', options =fc1_list, value='India',style={'color':'black'}))],
                        width=3, className='p-2 mr-5'),
                
                #dbc.Col(children = [html.Label('Select Color'), 
                        #html.Div(dcc.Dropdown(id = 'select-color-1', options =colors_list, value='red'))],
                        #width=3, className='p-2 mr-5'),
                
                dbc.Col(children = [html.Label('Select category', style = {'padding-top': '0px'}), 
                        html.Div(dcc.Dropdown(id = 'select-category-1', options = c1_type_list,value='Total Confirmed Cases',style={'color':'black'}))],
                        width=3, className='p-2 ml-5'),
            ]
        , className='my-4 justify-content-center'),
            
    ]
)
def daily(new_df,ctype):
    f=go.Figure()
    f.add_trace(go.Scatter(x=new_df['Date'], y=new_df[ctype], name="Covid-19 Report",mode='lines',
       line=dict(color='deeppink',width=4)))
    f.add_trace(go.Scatter(
        x=new_df['Date'],
        y=new_df[ctype],
        name='Scatter Plot',
        mode='markers',
        marker=dict(
        size=5,
            color='yellow') 
        ))
    f.update_layout(height=700,template='plotly_dark')
    daily_data = []
    daily_data.append(f)
    
    return daily_data
@app.callback(
     [Output('country-total', 'children')],
     [Input('select-country-1', 'value')]
)

def total_of_country(country):
    
    my_country = country_df[country_df['Country'] == country].loc[:, ['Confirmed', 'Deaths', 'Recovered', 'Active']]
    
    country_total = dbc.Container(
    [   
        html.H4('Total case in '+ country+ ''),
        
        dbc.Row(
            [
                dbc.Col(children = [html.H6('Confirmed',style={'color':'black','font_weight':'bold'}), 
                        html.Div(my_country['Confirmed'].sum(), className='text-info', style = {'font-size': '34px', 'font-weight': '700','background-color': '#000000'})],
                        width=3, className='text-center bg-light border-right p-2', style = {'border-top-left-radius': '6px', 'border-bottom-left-radius': '6px'}),
                
                dbc.Col(children = [html.H6('Recovered', style = {'padding-top': '0px','color':'black','font_weight':'bold'}),
                        html.Div(my_country['Recovered'].sum(), className='text-success', style = {'font-size': '34px', 'font-weight': '700','background-color': '#000000'})],
                        width=3, className='text-center bg-light border-right p-2'),
                
                dbc.Col(children = [html.H6('Death', style = {'padding-top': '0px','color':'black','font_weight':'bold'}), 
                        html.Div(my_country['Deaths'].sum(), className='text-danger', style = {'font-size': '34px', 'font-weight': '700','background-color': '#000000'})],
                        width=3, className='text-center bg-light border-right p-2'),
                
                dbc.Col(children = [html.H6('Active',style={'color':'black','font_weight':'bold'}),
                        html.Div(my_country['Active'].sum(),className='text-warning', style = {'font-size': '34px', 'font-weight': '700','background-color': '#000000'})],
                        width=3, className='text-center bg-light p-2', style = {'border-top-right-radius': '6px', 'border-bottom-right-radius': '6px'}),
            ]
        , className='my-4 shadow justify-content-center'),
            
    ]
        ,style={'background_color': '#000000'}
        
)
    
    return [country_total]

@app.callback(
     [Output('f1', 'figure')],
     [Input('select-country-1', 'value'),
      Input('select-category-1', 'value')
      ]
)
def countrywise(countryname,ctype):
   
    dftype = B.copy(deep=True)
    country = dftype.groupby('Country')
    country = country.get_group(countryname)
    country=country.reset_index()
    
    country['Date']=pd.to_datetime(country['Date'])
    return(daily(country,ctype))

f2_heading = html.H2(id='nav-f2', children='Trend Comparison Of Different Cases Per Country', className='mt-5 pb-3 text-center')
fc2=B['Country'].unique().tolist()
fc2_list=[]

for i in fc2:
    fc2_list.append({'label': i, 'value': i})
    
country_dropdown_2 = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(children = [html.Label('Select Country'), 
                        html.Div(dcc.Dropdown(id = 'select-country-2', options =fc2_list, value='India',style={'color':'black'}))],
                        width=3, className='p-2 mr-5'),
            ]
        , className='my-4 justify-content-center'),
            
    ]
)
@app.callback(
     [Output('f2', 'figure')],
     [Input('select-country-2', 'value')]
)
def countrywise2(countryname):
    dftype = B.copy(deep=True)
        #category = 'COVID-19 cases'

    # group by country name
    country = dftype.groupby('Country')
    # select the given country
    country = country.get_group(countryname)

    country=country.reset_index()
    country['Date']=pd.to_datetime(country['Date'])

    fig= make_subplots(rows=3, cols=3,shared_xaxes=True,
                   subplot_titles=('Total Confirmed Cases','Total Deaths','Total Recoveries','Daily New Cases','Daily New Deaths','Daily New Recoveries','Active Cases','Share of Recoveries - Closed Cases','Death to Cases Ratio'))

    fig.add_trace(go.Scatter(x=country['Date'],y=country['Total Confirmed Cases'],
                         mode='lines',
                         name='Total Confirmed Cases',
                         line=dict(color='aqua',width=2)),
                          row=1,col=1)
    fig.add_trace(go.Scatter(x=country['Date'],y=country['Total Deaths'],
                         mode='lines',
                         name='Total Deaths',
                         line=dict(color='dodgerblue',width=2)),
                          row=1,col=2)
    fig.add_trace(go.Scatter(x=country['Date'],y=country['Total Recoveries'],
                         mode='lines',
                         name='Total Recoveries',
                         line=dict(color='yellow',width=2)),
                          row=1,col=3)    
                           
    fig.add_trace(go.Scatter(x=country['Date'],y=country['Daily New Cases'],
                         mode='lines',
                         name='Daily New Cases',
                         line=dict(color='springgreen',width=2)),
                          row=2,col=1)
  
    fig.add_trace(go.Scatter(x=country['Date'],y=country['Daily New Deaths'],
                         mode='lines',
                         name='Daily New Deaths',
                         line=dict(color='deeppink',width=2)),
                          row=2,col=2)
    fig.add_trace(go.Scatter(x=country['Date'],y=country['Daily New Recoveries'],
                         mode='lines',
                         name='Daily New Recoveries',
                         line=dict(color='peru',width=2)),
                          row=2,col=3)
    fig.add_trace(go.Scatter(x=country['Date'],y=country['Active Cases'],
                         mode='lines',
                         name='Active Cases', 
                         line=dict(color='limegreen',width=2)),
                          row=3,col=1)
    fig.add_trace(go.Scatter(x=country['Date'],y=country['Share of Recoveries - Closed Cases'],
                         mode='lines',
                         name='Share of Recoveries - Closed Cases',
                         line=dict(color='tomato',width=2)),
                          row=3,col=2)
    fig.add_trace(go.Scatter(x=country['Date'],y=country['Death to Cases Ratio'],
                         mode='lines',
                         name='Death to Cases Ratio',
                         line=dict(color='orange',width=2)),
                         row=3,col=3)
    fig.update_layout(showlegend=True, margin={"r":0,"l":0,"b":0}, height=700,template='plotly_dark')
    #fig.show()
    d=[]
    d.append(fig)
    return d
f3_heading = html.H2(id='nav-f3', children='COVID-19 Case Study Per Country', className='mt-5 pb-3 text-center')
fc3=B['Country'].unique().tolist()
fc3_list=[]
c2_type=['Total Confirmed Cases', 'Total Deaths','Total Recoveries','Active Cases','Daily New Cases','Daily New Deaths','Daily New Recoveries']
c2_type_list=[]
colors3=['aliceblue', 'antiquewhite', 'aqua', 'aquamarine', 'azure',
            'beige', 'bisque', 'black', 'blanchedalmond', 'blue',
            'blueviolet', 'brown', 'burlywood', 'cadetblue',
            'chartreuse', 'chocolate', 'coral', 'cornflowerblue',
            'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan',
            'darkgoldenrod', 'darkgray', 'darkgrey', 'darkgreen',
            'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange',
            'darkorchid', 'darkred', 'darksalmon', 'darkseagreen',
            'darkslateblue', 'darkslategray', 'darkslategrey',
            'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue',
            'dimgray','dodgerblue', 'firebrick',
            'floralwhite', 'forestgreen', 'fuchsia', 'gainsboro',
            'ghostwhite', 'gold', 'goldenrod', 'gray', 'grey', 'green',
            'greenyellow', 'honeydew', 'hotpink', 'indianred', 'indigo',
            'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen',
            'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan',
            'lightgoldenrodyellow', 'lightgray', 'lightgrey',
            'lightgreen', 'lightpink', 'lightsalmon', 'lightseagreen',
            'lightskyblue', 'lightslategray', 'lightslategrey',
            'lightsteelblue', 'lightyellow', 'lime', 'limegreen',
            'linen', 'magenta', 'maroon', 'mediumaquamarine',
            'mediumblue', 'mediumorchid', 'mediumpurple',
            'mediumseagreen', 'mediumslateblue', 'mediumspringgreen',
            'mediumturquoise', 'mediumvioletred', 'midnightblue',
            'mintcream', 'mistyrose','moccasin', 'navajowhite', 'navy',
            'oldlace','olive', 'olivedrab', 'orange', 'orangered',
            'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise',
            'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink',
            'plum', 'powderblue', 'purple', 'red', 'rosybrown',
            'royalblue', 'rebeccapurple', 'saddlebrown', 'salmon',
            'sandybrown', 'seagreen', 'seashell', 'sienna', 'silver',
            'skyblue', 'slateblue', 'slategray', 'slategrey', 'snow',
            'springgreen', 'steelblue', 'tan', 'teal', 'thistle', 'tomato',
            'turquoise', 'violet', 'wheat', 'white', 'whitesmoke',
            'yellow', 'yellowgreen']
colors3_list=[]
for i in fc3:
    fc3_list.append({'label': i, 'value': i})
    
for i in c2_type:
    c2_type_list.append({'label': i, 'value': i})
for i in colors3:
    colors3_list.append({'label': i, 'value': i})
# dropdown to select country
country_dropdown_3=dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(children = [html.Label('Select Country'), 
                        html.Div(dcc.Dropdown(id = 'select-country-3', options =fc3_list, value='India',style={'color':'black'}))],
                        width=3, className='p-2 mr-5'),
                
                dbc.Col(children = [html.Label('Select Color'), 
                        html.Div(dcc.Dropdown(id = 'select-color-3', options =colors3_list, value='dodgerblue',style={'color':'black'}))],
                        width=3, className='p-2 mr-5'),
                
                dbc.Col(children = [html.Label('Select category', style = {'padding-top': '0px'}), 
                        html.Div(dcc.Dropdown(id = 'select-category-3', options = c2_type_list,value='Total Confirmed Cases',style={'color':'black'}))],
                        width=3, className='p-2 ml-5'),
            ]
        , className='my-4 justify-content-center'),
            
    ]
)    
@app.callback(
     [Output('f3', 'figure')],
     [Input('select-country-3', 'value'),
      Input('select-color-3', 'value'),
      Input('select-category-3', 'value')
      ]
)
def countrywise3(countryname,color1,ctype):
  
    dftype = B.copy(deep=True)
    # group by country name
    country = dftype.groupby('Country')
    country = country.get_group(countryname)
    country=country.reset_index()
    country['Date']=pd.to_datetime(country['Date'])

        
    fig1=go.Figure()
    fig1.add_traces(go.Bar(
        x=country['Date'],
        y=country[ctype], 
        marker=dict(color=color1) 
    ))
    fig1.update_layout(height=700,template='plotly_dark')
    e=[]
    e.append(fig1)
    return e
    
f4_heading = html.H2(id='nav-f4', children='Comparison Of COVID-19 Cases Per Country Using Bar Diagrams(Subplot) ', className='mt-5 pb-3 text-center')
fc4=B['Country'].unique().tolist()
fc4_list=[]
for i in fc4:
    fc4_list.append({'label': i, 'value': i})

country_dropdown_4 = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(children = [html.Label('Select Country'), 
                        html.Div(dcc.Dropdown(id = 'select-country-4', options =fc4_list, value='India',style={'color':'black'}))],
                        width=3, className='p-2 mr-5'),
            ]
        , className='my-4 justify-content-center'),
            
    ]
)
@app.callback(
     [Output('f4', 'figure')],
     [Input('select-country-4', 'value')]
)
def countrywise2(countryname):
    dftype = B.copy(deep=True)
    country = dftype.groupby('Country')
    # select the given country
    country = country.get_group(countryname)

    country=country.reset_index()
    
    country['Date']=pd.to_datetime(country['Date'])
   
    fig= make_subplots(rows=4, cols=2,shared_xaxes=True,specs=[[{}, {}],[{},{}],[{},{}],[{"colspan": 2}, None]],
                   subplot_titles=('Total Confirmed Cases','Total Deaths','Total Recoveries','Daily New Cases','Daily New Deaths','Daily New Recoveries','Active Cases'))

    fig.add_trace(go.Bar(x=country['Date'],y=country['Total Confirmed Cases'],
                         #mode='lines+markers',
                         name='Total Confirmed Cases',
                         marker=dict(color='royalblue')),
                          row=1,col=1)
    fig.add_trace(go.Bar(x=country['Date'],y=country['Total Deaths'],
                         #mode='lines+markers',
                         name='Total Deaths',
                         marker=dict(color='limegreen')),
                          row=1,col=2)
    fig.add_trace(go.Bar(x=country['Date'],y=country['Total Recoveries'],
                         #mode='lines+markers',
                         name='Total Recoveries',
                         marker=dict(color='gold')),
                          row=2,col=1)    
                           
    fig.add_trace(go.Bar(x=country['Date'],y=country['Daily New Cases'],
                         #mode='lines+markers',
                         name='Daily New Cases',
                         marker=dict(color='deeppink')),
                          row=2,col=2)
  
    fig.add_trace(go.Bar(x=country['Date'],y=country['Daily New Deaths'],
                         #mode='lines+markers',
                         name='Daily New Deaths',
                         marker=dict(color='greenyellow')),
                          row=3,col=1)
    fig.add_trace(go.Bar(x=country['Date'],y=country['Daily New Recoveries'],
                         #mode='lines+markers',
                         name='Daily New Recoveries',
                         marker=dict(color='deepskyblue')),
                          row=3,col=2)
    fig.add_trace(go.Bar(x=country['Date'],y=country['Active Cases'],
                         #mode='lines+markers',
                         name='Active Cases', 
                         marker=dict(color='darkorange')),
                          row=4,col=1)
    fig.update_layout(showlegend=True,title='Comparison Of Each Cases',margin={"r":0,"l":0,"b":0}, height=1000,template='plotly_dark')
    #fig.show()
    g=[]
    g.append(fig)
    return g
India=u.loc['India']
Italy=u.loc['Italy']
Germany=u.loc['Germany']
Germany.head(10)
US=u.loc['US']
UK=u.loc['United Kingdom']
Russia=u.loc['Russia']
Spain=u.loc['Spain']
Brazil=u.loc['Brazil']
Chile=u.loc['Chile']
Mexico=u.loc['Mexico']
Iran=u.loc['Iran']
Peru=u.loc['Peru']
f5_heading = html.H2(id='nav-f5', children='Trend Comparison Of Different Countries', className='mt-5 pb-3 text-center')
c5_type=['Total Confirmed Cases', 'Total Deaths','Total Recoveries','Active Cases','Daily New Cases','Daily New Deaths','Daily New Recoveries']
c5_type_list=[]

for i in c5_type:
    c5_type_list.append({'label': i, 'value': i})
country_dropdown_5 = dbc.Container(
    [
        dbc.Row(
            [
                #dbc.Col(children = [html.Label('Select Country'), 
                        #html.Div(dcc.Dropdown(id = 'select-country-5', options =fc2_list, value='India'))],
                        #width=3, className='p-2 mr-5'),
                
                dbc.Col(children = [html.Label('Select category', style = {'padding-top': '0px'}), 
                        html.Div(dcc.Dropdown(id = 'select-category-10', options = c5_type_list,value='Total Confirmed Cases',style={'color':'black'}))],
                        width=3, className='p-2 ml-5'),
            ]
        , className='my-4 justify-content-center'),
            
    ]
)
@app.callback(
     [Output('f5', 'figure')],
     [Input('select-category-10','value')]
)
def columnwise(ctype):
    #chartcol=color1
    fig12 = make_subplots(rows=4, cols=3,shared_xaxes=True,specs=[[{}, {}, {}],[{},{}, {}],
                       [{},{},{}],  [{},{},{}]],subplot_titles=('Italy','Germany','India','Spain','United Kingdom','US','Brazil','Russia','Peru','Chile','Iran','Mexico'))
    fig12.add_trace(go.Scatter(x=Italy.index,y=Italy[ctype],
                         mode='lines',
                         #name='Confirmed Cases',
                         line=dict(color='dodgerblue',width=2)),
                         row=1,col=1)
    fig12.add_trace(go.Scatter(x=Germany.index,y=Germany[ctype],
                         #mode='lines+markers',
                         name='Confirmed Cases',
                         line=dict(color='crimson',width=2)),
                         row=1,col=2)
    fig12.add_trace(go.Scatter(x=India.index,y=India[ctype],
                         mode='lines',
                         #name='Confirmed Cases',
                         line=dict(color='deeppink',width=2)),
                         row=1,col=3)
    fig12.add_trace(go.Scatter(x=Russia.index,y=Russia[ctype],
                         mode='lines',
                         #name='Confirmed Cases',
                         line=dict(color='#f36',width=2)),
                         row=2,col=1)
    fig12.add_trace(go.Scatter(x=Spain.index,y=Spain[ctype],
                         mode='lines',
                         #name='Confirmed Cases',
                         line=dict(color='cyan',width=2)),
                         row=2,col=2)
    fig12.add_trace(go.Scatter(x=UK.index,y=UK[ctype],
                         mode='lines',
                         #name='Confirmed Cases',
                         line=dict(color='darkorange',width=2)),
                         row=2,col=3)
    fig12.add_trace(go.Scatter(x=US.index,y=US[ctype],
                         mode='lines',
                         #name='Confirmed Cases',
                         line=dict(color='magenta',width=2)),
                         row=3,col=1)
    fig12.add_trace(go.Scatter(x=Brazil.index,y=Brazil[ctype],
                         mode='lines',
                         #name='Confirmed Cases',
                         line=dict(color='orchid',width=2)),
                         row=3,col=2)
    fig12.add_trace(go.Scatter(x=Peru.index,y=Peru[ctype],
                         mode='lines',
                         #name='Confirmed Cases',
                         line=dict(color='greenyellow',width=2)),
                         row=3,col=3)
    fig12.add_trace(go.Scatter(x=Chile.index,y=Chile[ctype],
                         mode='lines',
                         #name='Confirmed Cases',
                         line=dict(color='aqua',width=2)),
                         row=4,col=1)
    fig12.add_trace(go.Scatter(x=Iran.index,y=Iran[ctype],
                         mode='lines',
                         #name='Confirmed Cases',
                         line=dict(color='springgreen',width=2)),
                         row=4,col=2)
    fig12.add_trace(go.Scatter(x=Mexico.index,y=Mexico[ctype],
                         mode='lines',
                         #name='Confirmed Cases',
                         line=dict(color='blueviolet',width=2)),
                         row=4,col=3)
    fig12.update_layout(showlegend=False,title='Comparision On ' + ctype +'Of Top Countries ', margin={"r":0,"l":0,"b":0}, height=700,template='plotly_dark')
    m=[]
    m.append(fig12)
    return m
f6_heading = html.H2(id='nav-f6', children='Relative Comparision Between Top Countries', className='mt-5 pb-3 text-center')
c6_type=['Total Confirmed Cases', 'Total Deaths','Total Recoveries','Active Cases','Daily New Cases','Daily New Deaths','Daily New Recoveries']
c6_type_list=[]
for i in c6_type:
    c6_type_list.append({'label': i, 'value': i})
# dropdown to select country
country_dropdown_6 = dbc.Container(
    [
        dbc.Row(
            [
                 dbc.Col(children = [html.Label('Select category', style = {'padding-top': '0px'}), 
                        html.Div(dcc.Dropdown(id = 'select-category-6', options = c6_type_list,value='Total Confirmed Cases',style={'color':'black'}))],
                        width=3, className='p-2 ml-5'),
            ]
        , className='my-4 justify-content-center'),
            
    ]
)
@app.callback(
     [Output('f6', 'figure')],
     [Input('select-category-6','value')]
)
def columnwise1(ctype):
    #chartcol=color1
    #fig3_heading = html.H2(id='nav-fig3-link', children='COVId-19 Worldwide Relative Comparision', className='mt-5 pb-3 text-center')
    fig3 = go.Figure(data=[go.Bar(name='US',x=US.index, y=US[ctype]),go.Bar(name='UK',x=UK.index, y=UK[ctype]),go.Bar(name='India',x=India.index, y=India[ctype]),go.Bar(name='Italy',x=Italy.index, y=Italy[ctype]), go.Bar(name='Brazil',x=Brazil.index,y=Brazil[ctype]),go.Bar(name='Russia',x=Russia.index,y=Russia[ctype]),go.Bar(name='Spain',x=Spain.index,y=Spain[ctype]),go.Bar(name='Mexico',x=Mexico.index,y=Mexico[ctype]),go.Bar(name='Chile',x=Chile.index,y=Chile[ctype]),go.Bar(name='Iran',x=Iran.index,y=Iran[ctype]),go.Bar(name='Germany',x=Germany.index,y=Germany[ctype]),go.Bar(name='Peru',x=Peru.index,y=Peru[ctype])])
    fig3.update_layout(margin={"r":0,"l":0,"b":0}, height=700,barmode='stack',template='plotly_dark')
    fig3.update_yaxes(showticklabels=True)
    m1=[]
    m1.append(fig3)
    return m1
top_country_heading = html.H2(id='nav-top-country-graph', children='Top most Effected countries with COVID-19', className='mt-5 pb-3 text-center')
no_of_country = []

top_category = country_df.loc[0:, ['Confirmed', 'Active', 'Deaths', 'Recovered', 'Mortality_Rate']].columns.tolist()
top_category_list = []

for i in range(1,180):
    no_of_country.append({'label': i, 'value': i})
    
for i in top_category:
    top_category_list.append({'label': i, 'value': i})
    

# country dropdown object
top_10_country = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(children = [html.Label('Select no of Country'), 
                        html.Div(dcc.Dropdown(id = 'no-of-country', options = no_of_country, value=10,style={'color':'black'}))],
                        width=3, className='p-2 mr-5'),
                
                dbc.Col(children = [html.Label('Select category', style = {'padding-top': '0px'}), 
                        html.Div(dcc.Dropdown(id = 'top-category', options = top_category_list, value='Confirmed',style={'color':'black'}))],
                        width=3, className='p-2 ml-5'),
            ]
        , className='my-4 justify-content-center'),
            
    ]
)
@app.callback(
     [Output('top-country-graph', 'figure')],
     [Input('no-of-country', 'value'),
      Input('top-category', 'value')]
    )

# method to get the top countries

def top_ten(number, sort_by):
    # sorting the columns with top death rate
    country_df2 = country_df.sort_values(by=sort_by, ascending=False)
    
    # sort country with highest number of cases
    country_df2 = country_df2.head(number)
    
    top_country_data = []
    f4=go.Figure()
   
    f4.add_traces(go.Bar(x=country_df2['Country'], y=country_df2[sort_by]))
    f4.update_layout(title='Top ' + str(number) +' Country - ' + sort_by + ' case',height=700,margin={'r':0},template='plotly_dark')
    top_country_data.append(f4)
    '''layout = {
        'title': 'Top ' + str(number) +' Country - ' + sort_by + ' case',
        'title_font_size': 26,
        'height':700,
        'xaxis': dict(title = 'Countries'),
        'yaxis': dict(title = sort_by),
        'margin':{"r":0}
    }
    
    figure = [{
        'data': top_country_data,
        'layout': layout
    }]'''
    
    return top_country_data
country_df.sort_values('Confirmed', ascending=False, inplace=True)
cr_heading = html.H2(id='nav-cr-link', children="Top 10 countires with Confirmed,Deaths,Recovered and Active case", className='mt-5 pb-3 text-center')

# confrirm and recovered cases
top_country = country_df.head(10)
top_country_name = list(top_country['Country'].values)

cr = go.Figure(data=[
    go.Bar(name='Confirmed',marker_color='#f36', x=top_country_name, y=list(top_country['Confirmed'])),
    go.Bar(name='Deaths',marker_color='red', x=top_country_name, y=list(top_country['Deaths'])),
    go.Bar(name='Recovered', marker_color='#1abc9c',x=top_country_name, y=list(top_country['Recovered'])),
    go.Bar(name='Active',marker_color='yellow', x=top_country_name, y=list(top_country['Active'])),
])

cr.update_layout(barmode='group', height=700,template='plotly_dark')


global_map_heading = html.H2(children='World map view', className='mt-5 py-4 pb-3 text-center')

temp_df = pd.DataFrame(country_df["Recovered"])
#temp_df = temp_df.reset_index()
fig10=px.choropleth(temp_df, locations=country_df["Country"],
                color=np.log10(temp_df["Recovered"]), # lifeExp is a column of gapminder
                hover_name=country_df["Country"], # column to add to hover information
                hover_data=["Recovered"],
                color_continuous_scale=px.colors.sequential.Plasma,locationmode="country names")
fig10.update_geos(fitbounds="locations", visible=False)
fig10.update_layout(title_text="Recovered Cases Heat Map (Log Scale)", margin={"r":0,"l":0,"b":0}, height=600,template='plotly_dark')
fig10.update_coloraxes(colorbar_title="Recovered Cases(Log Scale)",colorscale='bugn')
world_tally = dbc.Container(
    [
        html.H2('World Data', style = {'text-align': 'center'}),
        
        dbc.Row(
            [
                dbc.Col(children = [html.H4('Confirmed',style={'color':'black','font_weight':'bold'}), 
                        html.Div(country_df['Confirmed'].sum(), className='text-info', style = {'font-size': '34px', 'font-weight': '700','background-color': '#000000'})],
                        width=3, className='text-center bg-light border-right p-2', style = {'border-top-left-radius': '6px', 'border-bottom-left-radius': '6px'}),
                
                dbc.Col(children = [html.H4('Recovered', style = {'padding-top': '0px','color':'black','font_weight':'bold'}),
                        html.Div(country_df['Recovered'].sum(), className='text-success', style = {'font-size': '34px', 'font-weight': '700','background-color': '#000000'})],
                        width=3, className='text-center bg-light border-right p-2'),
                
                dbc.Col(children = [html.H4('Death', style = {'padding-top': '0px','color':'black','font_weight':'bold'}), 
                        html.Div(country_df['Deaths'].sum(), className='text-danger', style = {'font-size': '34px', 'font-weight': '700','background-color': '#000000'})],
                        width=3, className='text-center bg-light border-right p-2'),
                
                dbc.Col(children = [html.H4('Active',style={'color':'black','font_weight':'bold'}),
                        html.Div(country_df['Active'].sum(),className='text-warning', style = {'font-size': '34px', 'font-weight': '700','background-color': '#000000'})],
                        width=3, className='text-center bg-light p-2', style = {'border-top-right-radius': '6px', 'border-bottom-right-radius': '6px'}),
            ]
        , className='my-4 shadow justify-content-center'),
            
    ],style={'background-color': '#000000'}
)


GlobalTotals=u.reset_index().groupby('Date').sum()
#GlobalTotals=GlobalTotals.set_index(['Country/Region','Date'])
GlobalTotals['Share of Recoveries - Closed Cases']=np.round(GlobalTotals['Total Recoveries']/(GlobalTotals['Total Recoveries']+GlobalTotals['Total Deaths']),2)
GlobalTotals['Death to Cases Ratio']=np.round(GlobalTotals['Total Deaths']/GlobalTotals['Total Confirmed Cases'],3)
fig9_heading = html.H2(id='nav-fig9-link', children='Global Case Studies Using Subplots(Line Diagram)', className='mt-5 pb-3 text-center')
fig9= make_subplots(rows=3, cols=3,shared_xaxes=True,
                   subplot_titles=('Total Confirmed Cases','Total Deaths','Total Recoveries','Daily New Cases','Daily New Deaths','Daily New Recoveries','Active Cases','Share of Recoveries - Closed Cases','Death to Cases Ratio'))

fig9.update_xaxes(title_text="Number of Days since Outbreak", row=3, col=1)

fig9.update_xaxes(title_text="Number of Days since Outbreak", row=3, col=2)

fig9.update_xaxes(title_text="Number of Days since Outbreak", row=3, col=3)

fig9.add_trace(go.Scatter(x=GlobalTotals.index,y=GlobalTotals['Total Confirmed Cases'],
                         mode='lines',
                         name='Total Confirmed Cases',
                         line=dict(color='red',width=2)),
                          row=1,col=1)
fig9.add_trace(go.Scatter(x=GlobalTotals.index,y=GlobalTotals['Total Deaths'],
                         mode='lines',
                         name='Total Deaths',
                         line=dict(color='dodgerblue',width=2)),
                          row=1,col=2)
fig9.add_trace(go.Scatter(x=GlobalTotals.index,y=GlobalTotals['Total Recoveries'],
                         mode='lines',
                         name='Total Recoveries',
                         line=dict(color='deeppink',width=2)),
                          row=1,col=3)    
                           
fig9.add_trace(go.Scatter(x=GlobalTotals.index,y=GlobalTotals['Daily New Cases'],
                         mode='lines',
                         name='Daily New Cases',
                         line=dict(color='springgreen',width=2)),
                          row=2,col=1)
  
fig9.add_trace(go.Scatter(x=GlobalTotals.index,y=GlobalTotals['Daily New Deaths'],
                         mode='lines',
                         name='Daily New Deaths',
                         line=dict(color='orange',width=2)),
                          row=2,col=2)
fig9.add_trace(go.Scatter(x=GlobalTotals.index,y=GlobalTotals['Daily New Recoveries'],
                         mode='lines',
                         name='Daily New Recoveries',
                         line=dict(color='coral',width=2)),
                          row=2,col=3)
fig9.add_trace(go.Scatter(x=GlobalTotals.index,y=GlobalTotals['Active Cases'],
                         mode='lines',
                         name='Active Cases', 
                         line=dict(color='darkturquoise',width=2)),
                          row=3,col=1)
fig9.add_trace(go.Scatter(x=GlobalTotals.index,y=GlobalTotals['Share of Recoveries - Closed Cases'],
                         mode='lines',
                         name='Share of Recoveries - Closed Cases',
                         line=dict(color='mediumvioletred',width=2)),
                          row=3,col=2)
fig9.add_trace(go.Scatter(x=GlobalTotals.index,y=GlobalTotals['Death to Cases Ratio'],
                         mode='lines',
                         name='Death to Cases Ratio',
                         line=dict(color='orchid',width=2)),
                        row=3,col=3)
fig9.update_layout(showlegend=True,margin={"r":0,"l":0,"b":0}, height=700,template='plotly_dark')

#fig3.show()
fig4_heading = html.H2(id='nav-fig4-link', children='Worldwide Comparision Between Different Cases By Subplots(Bar Diagrams)', className='mt-5 pb-3 text-center')
                  
fig4= make_subplots(rows=4, cols=2,shared_xaxes=True,specs=[[{}, {}],[{},{}],[{},{}],[{"colspan": 2}, None]],
                   subplot_titles=('Total Confirmed Cases','Total Deaths','Total Recoveries','Daily New Cases','Daily New Deaths','Daily New Recoveries','Active Cases'))

fig4.add_trace(go.Bar(x=GlobalTotals.index,y=GlobalTotals['Total Confirmed Cases'],
                         #mode='lines+markers',
                         name='Total Confirmed Cases',
                         marker=dict(color='royalblue')),
                          row=1,col=1)
fig4.add_trace(go.Bar(x=GlobalTotals.index,y=GlobalTotals['Total Deaths'],
                         #mode='lines+markers',
                         name='Total Deaths',
                         marker=dict(color='limegreen')),
                          row=1,col=2)
fig4.add_trace(go.Bar(x=GlobalTotals.index,y=GlobalTotals['Total Recoveries'],
                         #mode='lines+markers',
                         name='Total Recoveries',
                         marker=dict(color='yellow')),
                          row=2,col=1)    
fig4.add_trace(go.Bar(x=GlobalTotals.index,y=GlobalTotals['Daily New Cases'],
                         #mode='lines+markers',
                         name='Daily New Cases',
                         marker=dict(color='deeppink')),
                          row=2,col=2)
  
fig4.add_trace(go.Bar(x=GlobalTotals.index,y=GlobalTotals['Daily New Deaths'],
                         #mode='lines+markers',
                         name='Daily New Deaths',
                         marker=dict(color='tomato')),
                          row=3,col=1)
fig4.add_trace(go.Bar(x=GlobalTotals.index,y=GlobalTotals['Daily New Recoveries'],
                         #mode='lines+markers',
                         name='Daily New Recoveries',
                         marker=dict(color='cyan')),
                          row=3,col=2)
fig4.add_trace(go.Bar(x=GlobalTotals.index,y=GlobalTotals['Active Cases'],
                         #mode='lines+markers',
                         name='Active Cases', 
                         marker=dict(color='darkorange')),
                          row=4,col=1)
fig4.update_layout(showlegend=True,title='Comparison Of Each Cases',margin={"r":0,"l":0,"b":0}, height=1000,template='plotly_dark')
end = html.Div(children= [
        html.H3('Sources:'),
        html.Div([html.Span('1. The data is taken from '), dcc.Link('Johns Hopkins University', href='https://github.com/CSSEGISandData/COVID-19')]),
        html.Div([html.Span('2. Build this Dashboard using '), dcc.Link('Plotly', href='https://github.com/CSSEGISandData/COVID-19')]),
        html.Div([html.Span('3. Get the source code from my '), dcc.Link('github repo', href='https://github.com/shreya12-hash/COVID-19-Time-Series-Analysis-Visualization-Dashboard')]),
        #html.Div([html.Span('3. You can read my articel for detail explaination '), dcc.Link('here', href='https://medium.com/@benaikumar2/interactive-covid-19-dashboard-with-plotly-c0da1008b00')]),
        html.H5('Note: Will be updating this Dashboard with more features and better visualization.', style = {'margin-top': '20px', 'margin-bottom': '140px','background_color':'black'})
])


app.layout = html.Div(
     [navbar,
     main_heading,
     what_is_covid,
     world_tally,
      
      wc_heading,
         dcc.Graph(
             id='wc',
             figure=fi_1
         ),
      wd_heading,
         dcc.Graph(
             id='wd',
             figure=fi_2
         ),
      #global_map           
      html.Div(children = [global_map_heading,
          dcc.Graph(
             id='global_graph',
             figure=fig10
         )
        ]
      ),
     html.Div([f1_heading,
                    country_dropdown_1,
                    html.Div(id='country-total'),
         dcc.Graph(
             id='f1'
         )],style={'background-color': '#1e2130'}),
      
      html.Div([f2_heading,
                   country_dropdown_2,
          dcc.Graph(
              id='f2'
          )],style={'background-color': '#1e2130'}),
      f3_heading,
                    country_dropdown_3,
          dcc.Graph(
              id='f3'
          ),
      f4_heading,
                    country_dropdown_4,
          dcc.Graph(
              id='f4'
          ),
      f5_heading,
                    country_dropdown_5,
          dcc.Graph(
              id='f5'
          ),
      f6_heading,
                    country_dropdown_6,
          dcc.Graph(
              id='f6'
          ),
      top_country_heading,
                    top_10_country,
         dcc.Graph(
             id='top-country-graph'
         ),
      cr_heading,
         dcc.Graph(
             id='cr',
             figure=cr
         ),
      fig9_heading,
         dcc.Graph(
             id='fig9',
             figure=fig9
         ),
      fig4_heading,
         dcc.Graph(
             id='fig4',
             figure=fig4
         ),
      
      
    html.Div(children=end,style={'background_color':'black'}),

      html.Div([
    html.Footer(children='Made With 💖 by Shreya Biswas, Only for You'),],style={'background-color': '#0000FF','color':'#f3f5f4','textAlign': 'center','font-weight': 'bold'})
],style={'textAlign': 'center','font-weight':'bold','background-color': '#000000','color':'#f3f5f4'})

if __name__ == '__main__':
    app.run_server(debug=False)

    