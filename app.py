import requests
import pandas as pd
import streamlit as st
import plotly.express as px

@st.cache(allow_output_mutation=True)
def get_data():
    """ Fetch Data from API """
    
    resp = requests.get('https://api.covid19india.org/v4/timeseries.json')
    df = pd.DataFrame(resp.json())
    return df

df = get_data()

def get_total_data(li,d):
    """ Fetches and organises the data for covid cases in each state of India """
    
    dt=[]
    des=[]
    
    for col in li:
        if col=='KL':
            for dat in df[col]['dates'].items():
                dt.append(dat[0])
                try:
                    des.append(dat[1]['total'][d])
                except:
                    des.append('NaN')
            df2 = pd.concat([pd.DataFrame(dt,columns=['Date']), pd.DataFrame(des,columns=['KL'])],axis=1)
        
        dt2=[]
        des2=[]
        if col != 'KL':   
            df3 = pd.DataFrame()
            for dat in df[col]['dates'].items():
                dt2.append(dat[0])
                try:
                    des2.append(dat[1]['total'][d])
                except:
                    des2.append('NaN')
            df3 = pd.concat([pd.DataFrame(dt2,columns=['Date']), pd.DataFrame(des2,columns=[col])],axis=1)
            
            df2 = pd.merge_ordered(df2,df3,on='Date')
            
    return df2
       
###### Data Extraction and Cleaning ###########
    
dicti = {'KL':'Kerala','AN':'Andaman & Nicobar','AP':'Andra Pradesh','AR':'Arunachal Pradesh','AS':'Assam','BR':'Bihar',
         'CH':'Chandigarh','CT':'Chhatisgarh','DL':'Delhi','DN':'Daman & Diu','GA':'Goa','GJ':'Gujarat','HP':'Himachal Pradesh',
         'HR':'Hariyana','JH_x':'Jharkhand','JK_x':'Jammu & Kashmir','KA_x':'Karnataka','LA_x':'Ladakh','MH_x':'Maharashtra',
         'ML_x':'Meghalaya','MN_x':'Manipur','MP_x':'Madhya Pradesh','MZ_x':'Mizoram','NL_x':'Nagaland','OR':'Odisha',
         'PB':'Punjab','PY':'Puducherry','RJ':'Rajasthan','SK':'Sikkim','TG':'Telangana','TN':'Tamil Nadu','TR':'Tripura',
         'TT':'India','UP':'Uttar Pradesh','UT':'Uttarakhand','WB':'West Bengal'}

to_drop = ['JH_y','JK_y','KA_y','LA_y', 'MH_y',
       'ML_y', 'MN_y', 'MP_y', 'MZ_y', 'NL_y','UN']

to_select = ['KL','AN', 'AP', 'AR', 'AS', 'BR', 'CH', 'CT', 'DL', 'DN', 'GA', 'GJ',
             'HP','HR','JH', 'JK', 'KA', 'LA', 'MH', 'ML', 'MN', 'MP', 'MZ', 'NL',
             'JH', 'JK', 'KA', 'LA', 'MH', 'ML', 'MN', 'MP', 'MZ', 'NL', 'OR', 'PB', 
             'PY', 'RJ', 'SK', 'TG', 'TN', 'TR', 'TT', 'UN', 'UP', 'UT','WB']
        
df2 = get_total_data(to_select,'confirmed')
confirm2 = df2.set_index('Date') 
confirm = df2.drop(to_drop, axis = 1).rename(columns=dicti).replace('NaN',0)
total_c = confirm[['India']]
          
deaths = get_total_data(to_select,'deceased')
deaths2 = deaths.set_index('Date')
deaths = deaths.drop(to_drop,axis=1).rename(columns=dicti).replace('NaN',0)
total_d = deaths[['India']]

recovery = get_total_data(to_select,'recovered')
recovery2 = recovery.set_index('Date')  
recovery = recovery.drop(to_drop, axis = 1).rename(columns=dicti).replace('NaN',0)
total_r = recovery[['India']]

test = get_total_data(to_select,'tested')
test['Date'] = pd.to_datetime(test['Date'])
test2 = test.set_index('Date')
test = test.drop(to_drop, axis = 1).rename(columns=dicti).replace('NaN',0)
total_t = test[['India']]

total_c = total_c.rename(columns={'India': 'confirm'}) 
total_d = total_d.rename(columns={'India': 'deaths'})
total_r = total_r.rename(columns={'India': 'recovery'})
total_t = total_t.rename(columns={'India':'tests'}) 
total = pd.concat([confirm['Date'],total_c,total_d,total_r,total_t],axis=1)
total = total.replace('NaN',0) 
total['active'] = (total['confirm'] - total['recovery']) - total['deaths']

lis = list(dicti.values())
con = total.iloc[-1,1]
deat = total.iloc[-1,2]
reco = total.iloc[-1,3]
tes = total.iloc[-1,4]
act = total.iloc[-1,5]
table = pd.concat([pd.Series(con),pd.Series(deat),pd.Series(reco),pd.Series(act),pd.Series(tes)],axis=1)
table = table.rename(columns={0:'Confirmed',1:'Deaths',2:'Recovery',3:'Active',4:'Tests'}).set_index('Confirmed')

################# STREAMLIT #######################

st.title('Covid-19 Dashboard India')
st.sidebar.header('EXPLORE DASHBOARD')
st.sidebar.markdown(""" <ul>
                        <li>India : Total cases in India Timeline</li>
                        <li>Statewise : Analysis according to states </li>
                        <li>Analysis between a time period</li>
                        </ul>
                    """, unsafe_allow_html=True)

st.sidebar.subheader('Select an option')
radio = st.sidebar.radio('',['India Total','Statewise','For Particular Time'])

if radio == 'India Total':
    
    st.markdown("""     <div style='background-color:white;padding:10px'>
                    <h4 style='color:black'><i> About Dashboard </style></h4>
                        <ol>
                        <li>Explore more options from sidebar on top left</li>
                        <li>Developed with Python only </li>
                        <li>Hover over plots for more Detailed Information</li>
                        </ol>
                    """, unsafe_allow_html=True)
    st.table(table)     
    def plot_bar_ind(data,y1,title):
            """Plots the Stacked Bar chart for overall cases in Country"""
            
            fig = px.bar(data, x ='Date', y = y1, title=title,height=400,width=700,barmode='stack',labels={'value':'Total Cases'})
            fig.update_layout(title_font_color='green',title_font_family="Courier New",legend_title_font_color='green',
            title={
            'text': title,
            'y':0.9,
            'x':0.45,
            'xanchor': 'center',
            'yanchor': 'top'})
            st.plotly_chart(fig)
            
    plot_bar_ind(total[40:],['active','deaths','recovery'],'Covid-19 Timeline India')  
    
    def plot_line_ind(data1, y1, title):
            """Plots Line chart for overall cases in Country"""
            
            fig = px.line(data1, x ='Date', y = y1, title=title,height=400,width=700,labels={'value':'Total Cases'})
            fig.layout.plot_bgcolor='white'
            fig.update_layout(title_font_color='blue',title_font_family="Courier New",legend_title_font_color='green',
            title={
            'text': title,
            'y':0.9,
            'x':0.45,
            'xanchor': 'center',
            'yanchor': 'top'})
            #fig.layout.paper_bgcolor='#fff'
            st.plotly_chart(fig)
            
            st.subheader('Covid-19 Data India (last 10 Days)')
            st.table(data1.set_index('Date')[-10:])
    plot_line_ind(total[40:],['active','deaths','recovery'],'Line Chart Showing Covid-19 Timeline') 
    
if radio == 'Statewise':
    st.subheader('Select Data')
    fetch = st.selectbox(' ',['Confirmed Cases','Deaths','Recoveries','Tests'])

    def figure_plot_state(data,states,title,color):
        """Plots data for Active, Deceased, Recovered and Total Tests for the States selected"""
         
        data = data[20:]
        data = data.fillna(0)
        data = data.replace('NaN',0)
        fig = px.line(data,x=data.Date, y=states, title=title,height=500,width=700,labels={'value':title})#, hover_name='Date')#,color=data[stu])
        fig.update_layout(title_font_color=color,title_font_family="Courier New",legend_title_font_color=color,
        title={
            'text': title,
            'y':0.9,
            'x':0.45,
            'xanchor': 'center',
            'yanchor': 'top'})
        st.plotly_chart(fig)
        st.subheader(f'{title} Data'.format(title))
        data = data.set_index('Date')
        st.table(data[states][-10:])
        
    try:
        states = st.multiselect('  ',lis,default=['Rajasthan','Delhi','Maharashtra'])
    except:
        st.write('Select State')
        
    if fetch=='Confirmed Cases':
        figure_plot_state(confirm,states,'Confirmed Cases','blue')
    elif fetch=='Deaths':
        figure_plot_state(deaths,states,'Deaths','red')
    elif fetch=='Recoveries':
        figure_plot_state(recovery,states,'Recovery','green')
    elif fetch=='Tests':
        figure_plot_state(test,states,'Total Tests','blue')
        

if radio == 'For Particular Time':
    st.markdown("""     <ul>
                        <li>End Date should be greater than Start Date</li>
                        <li>Select Checkbox to Visualize and Analyze</li>
                        </ul>
                    """, unsafe_allow_html=True)
     
    date_1 = st.sidebar.selectbox('Start Date',confirm.Date)  
    date_2 = st.sidebar.selectbox('End Date',confirm.Date)   
       
    def plot_line_time(data2, y1, title):
        """Plots Data for a Particular time period selected"""
        
        fig = px.line(data2, x =data2.Date, y = y1, title=title,height=400,width=700,labels={'value':'Total Cases'})
        fig.update_layout(title_font_color='green',title_font_family="Courier New",legend_title_font_color='green',
        title={
            'text': title,
            'y':0.9,
            'x':0.45,
            'xanchor': 'center',
            'yanchor': 'top'})
        #fig.layout.plot_bgcolor='white'
        #fig.layout.paper_bgcolor='#fff'
        st.plotly_chart(fig)
        st.subheader('Data for selected Dates')
        st.dataframe(data2.set_index('Date')[y1])
    
    confirm3 = confirm.copy()
    if st.sidebar.checkbox('Visualize'):
        st.subheader('Select States')
        states_time = st.multiselect('',lis,default=['Rajasthan','Delhi','Maharashtra'])
    
        if date_1 < date_2:
            plot_line_time(confirm3[(confirm3['Date'] >= date_1) & (confirm3['Date']<=date_2)],states_time,f'Timeline from {date_1} to {date_2}'.format(date_1,date_2)) 
        else:
            st.header('End Date is Smaller than Start Date.....')
                
st.sidebar.success('author : @Koshal')     
    
