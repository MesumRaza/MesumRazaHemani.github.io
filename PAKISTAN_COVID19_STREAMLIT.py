import streamlit as st

from plotly.subplots import make_subplots
from plotly.graph_objs import *
import plotly.graph_objects as go
from matplotlib import cm

import pandas as pd
import json
import urllib.request

st.set_page_config(layout="wide")

dataset_url='https://docs.google.com/spreadsheets/d/e/2PACX-1vSMkjH9YrDqpF0a5YX2cwIoX7uLSf61jqgy0h1PBXYRmw-d1iiu6Hy0uF6ANOEcbZHE-sReZbZgPxXf/pubhtml?gid=1522509296&single=true'

df=pd.read_html(dataset_url,header=1)[0][1:].iloc[:, 2:]
	
df['Date']=pd.to_datetime(df['Date']).dt.date

df_latest=df[df['Date']==df['Date'].max()]

def create_kpi(val,text,format,color,header_size,value_size):
	return (go.Indicator(
        value = val,
        title= {"text":text,"font":{"size":15}},
        number={'valueformat':format,"font":{"size":50,"family":'Times New Roman',"color": color}}
    ))
	
def return_kpi_grid(df,day_diff):

	header1_fig = make_subplots(rows=1, cols=7,specs=[[{'type': 'domain'}]*7])
	
	if day_diff>0:
		temp_df=df.groupby('Date').agg('sum').reset_index().sort_values(by='Date').diff(periods=day_diff).iloc[-1]
	else:
		temp_df=df.groupby('Date').agg('sum').reset_index().sort_values(by='Date').iloc[-1]

	header1_fig.add_trace(
		create_kpi(temp_df['Cumulative'].sum(),'Suspected Cases',',.0f','#7f7f7f',15,50), row=1, col=1
	)

	header1_fig.add_trace(
		create_kpi(temp_df['Cumulative tests performed'].sum(),'Test Performed',',.0f','#7f7f7f',15,50), row=1, col=2
	)

	header1_fig.add_trace(
		create_kpi(temp_df['Cumulative Test positive'].sum(),'Test Postive',',.0f','#7f7f7f',15,50), row=1, col=3
	)

	header1_fig.add_trace(
		create_kpi(temp_df['Still admitted'].sum(),'Still Admitted',',.0f','#7f7f7f',15,50), row=1, col=4
	)

	header1_fig.add_trace(
		create_kpi(temp_df['Home Quarantine'].sum(),'Home Quarantine',',.0f','#7f7f7f',15,50), row=1, col=6
	)

	header1_fig.add_trace(
		create_kpi(temp_df['Discharged'].sum(),'Total Recovered',',.0f','#7f7f7f',15,50), row=1, col=5
	)

	header1_fig.add_trace(
		create_kpi(temp_df['Expired'].sum(),'Total Expired',',.0f','#7f7f7f',15,50), row=1, col=7
	)

	header1_fig.update_xaxes(showticklabels=False)
	header1_fig.update_yaxes(showticklabels=False)
	header1_fig.update_layout(Layout(
		paper_bgcolor='rgba(0,0,0,0)',
		plot_bgcolor='rgba(0,0,0,0)'
	),autosize=True,width=100,height=100)
	
	return header1_fig

labels = df.groupby('Date')['Cumulative Test positive'].sum().reset_index().sort_values(by='Date')['Date'].values
values = df.groupby('Date')['Cumulative Test positive'].sum().reset_index().sort_values(by='Date')['Cumulative Test positive'].diff(periods=1).values
data = [go.Bar(
   x = labels,
   y = values,
   marker={'color': values,'colorscale': 'ylorrd'}
)]
bar1_fig = go.Figure(data=data)

bar1_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',autosize=False,width=300,height=500)

labels = df.groupby('Date')['Cumulative tests performed'].sum().reset_index().sort_values(by='Date')['Date'].values
values = df.groupby('Date')['Cumulative tests performed'].sum().reset_index().sort_values(by='Date')['Cumulative tests performed'].diff(periods=1).values
data = [go.Bar(
   x = labels,
   y = values,
   marker={'color': values,'colorscale': 'ylorrd'}
)]
bar2_fig = go.Figure(data=data)

bar2_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',autosize=False,width=300,height=500)

url = "https://raw.githubusercontent.com/MesumRaza/MesumRazaHemani.github.io/main/PAKISTAN_PROVINCE_FINAL_2020_GEO.json"
response = urllib.request.urlopen(url)
pakistan_geojson = json.loads(response.read())
	
from geojson_rewind import rewind

pakistan_geojson=rewind(pakistan_geojson, rfc7946=False)

def transform_region(i):
	switcher={
			"AJK":'Azad Kashmir',
			"Balochistan":'Balochistan',
			"GB":'Gilgit Baltistan',
			"ICT":'Islamabad',
			"KP":'KPK',
			"Punjab":'Punjab',
			"Sindh":'Sindh'
		 }		 
	return switcher.get(i,"Invalid day of week")

df_latest['Region']=df_latest['Region'].apply(transform_region)
	 
import plotly.express as px	
map_fig = px.choropleth(df_latest,geojson=pakistan_geojson,locations='Region',color='Cumulative Test positive',color_continuous_scale='ylorrd',range_color=(0, df_latest['Cumulative Test positive'].max()),featureidkey="properties.NAME_1",projection="mercator")

map_fig.update_geos(fitbounds="locations", visible=False)
map_fig.update_layout(geo=dict(bgcolor= 'rgba(0,0,0,0)'))
map_fig.update_traces(colorbar_xanchor='left')
map_fig.update_layout(autosize=False,width=750,height=400,margin=dict(t=0, b=0, l=0, r=0))
									
pak_image='https://m.media-amazon.com/images/I/5140h-Yo5nL._SL1028_.jpg'

# st.title("PAKISTAN COVID-19 DASHBOARD (OPEN SOURCE - MADE WITH LOVE OF STREAMLIT <3 )")

# with st.beta_container():

	# for col in st.beta_columns(5):
		# col.plotly_chart(create_kpi2())

st.title("PAKISTAN COVID-19 DASHBOARD (OPEN SOURCE - MADE WITH LOVE OF STREAMLIT <3 )")
		
with st.beta_container():

	col1, col2= st.beta_columns((1,4))
	
	col1.image(pak_image, use_column_width=True)

	with col2.beta_container():
		st.header("Displaying Pakistan Data : Cumulative Statistics as of : "+str(df['Date'].max()))
		st.plotly_chart(return_kpi_grid(df,0), use_container_width=True)
	with col2.beta_container():
		st.header("On : "+str(df['Date'].max()))
		st.plotly_chart(return_kpi_grid(df,1), use_container_width=True)

with st.beta_container():

	strip_col1, strip_kpi_1, strip_kpi_2, strip_kpi_3= st.beta_columns((6,1,1,1))
	
	strip_col1.subheader('Disclaimer')
	strip_col1.write("""
	
	1. Reported data may contain errors and omissions from the actual data or facts involved. Please refer Governmental Datasources directly for decision making.

	2. The use of visualization implies that you agree to relieve creator from any legal obligations arising direct or remote due to usage of data or reporting.""")
	
	strip_kpi_1.plotly_chart(go.Figure(create_kpi(df_latest['Cumulative Test positive'].sum()/df_latest['Cumulative tests performed'].sum(),'Test Postive Rate %',',.2%','#000000',20,80)).update_layout(autosize=True,width=150,height=150))
	
	strip_kpi_2.plotly_chart(go.Figure(create_kpi(df_latest['Discharged'].sum()/df_latest['Cumulative Test positive'].sum(),'Recovery %',',.2%','#00D30D',20,80)).update_layout(autosize=True,width=150,height=150))
	
	strip_kpi_3.plotly_chart(go.Figure(create_kpi(df_latest['Expired'].sum()/df_latest['Cumulative Test positive'].sum(),'Fatality Rate %',',.2%','#FC2D00',20,80)).update_layout(autosize=True,width=150,height=150))
		
with st.beta_container():
	col3, col4= st.beta_columns(2)
	
	col3.header("Cumulative Tests Performed (DoD)")
	col3.plotly_chart(bar1_fig, use_container_width=True)
	
	col4.header("Cumulative Tests Positive (DoD)")
	col4.plotly_chart(bar2_fig, use_container_width=True)
	
	
with st.beta_container():
	col5, col6= st.beta_columns((2,3))
	
	col5.header("Cumulative Test Postive By Region")
	col5.plotly_chart(map_fig, use_column_width=True)
	
	col6.header("Regional Statistics (Heatmap)")
	
	df_latest_subset=df_latest[['Region','Cumulative','Cumulative tests performed','Cumulative Test positive','Discharged','Expired']].assign(Test_Positive=df_latest['Cumulative Test positive']/df_latest['Cumulative tests performed'],\
	Fatality_Rate=df_latest['Expired']/df_latest['Cumulative Test positive']).set_index('Region')
	
	df_latest_subset=df_latest_subset[['Cumulative','Cumulative tests performed','Cumulative Test positive','Test_Positive','Discharged','Expired','Fatality_Rate']].sort_values(by='Cumulative Test positive', ascending=False)
	
	col6.table(
	df_latest_subset.style
		.background_gradient(cmap='YlOrRd',subset=df_latest_subset.columns.difference(['Region']))
		.format('{0:,.0f}',subset=df_latest_subset.columns.difference(['Region']))
		.format('{0:,.2%}',subset=['Test_Positive','Fatality_Rate'])
		.set_properties(**{'text-align': 'center'})			
	)
	
	#col6.plotly_chart(table_fig,use_column_width=True)
