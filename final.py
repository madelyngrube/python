"""
Class: CS230--Section 01
Name: Maddie Grube
Description: Final Project
I pledge that I have completed the programming assignment independently.
I have not copied the code from a student or any source.
I have not given my code to any student.
Date: 12/8/21
"""
import streamlit as st
import pandas as pd
import pydeck as pdk
from PIL import Image
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import csv
pip install -- upgrade pip

columns = ["stadium", "city", "state", "team", "conference", "capacity", "built", "expanded", "div", "latitude", "longitude"]


#Read CSV into a DataFrame and read Stadium as Index
def read_data():
    global df
    df = pd.read_csv('stadums.csv')
    df.set_index('stadium', inplace = True)
    df.index.name = 'stadium'
    return read_data


#Convert all state abbreviations to state names so the state column is all in the same notation
def statenames():
    global df
    df["state"].replace({"AR": "Arkansas","AZ": "Arizona","AL": "Alabama","AK": "Alaska","CA": "California","CO": "Colorado","CT": "Connecticut",
                         "DE": "Delaware","FL": "Florida","GA": "Georgia","HI": "Hawaii","ID": "Idaho","IL": "Illinois","IN": "Indiana",
                         "IA": "Iowa","KS": "Kansas","KY": "Kentucky","LA": "Louisiana","ME": "Maine","MD": "Maryland","MA": "Massachusetts",
                         "MI": "Michigan","MN": "Minnesota","MS": "Mississippi","MO": "Missouri","MT": "Montana","NE": "Nebraska",
                         "NV": "Nevada","NH": "New Hampshire","NJ": "New Jersey","NM": "New Mexico","NY": "New York","NC": "North Carolina",
                         "ND": "North Dakota","OH": "Ohio","OK": "Oklahoma","OR": "Oregon","PA": "Pennsylvania","RI": "Rhode Island",
                         "SC": "South Carolina","SD": "South Dakota","TN": "Tennessee","TX": "Texas","UT": "Utah","VT": "Vermont",
                         "VA": "Virginia","WA": "Washington","WV": "West Virginia","WI": "Wisconsin","WY": "Wyoming","D.C.": "Washington D.C."},
                        inplace=True)
    return df['state']


#Home Page
def welcome():
    st.title("Welcome to my Project on NCAA Football Stadiums")
    st.text("By: Maddie Grube")
    st.markdown('''Use the navigation bar on the left to access the interactive pages and learn more about
            all the NCAA Football Stadiums.''')


    text = open('stadums.csv').read()
    wordcloud = WordCloud(width = 750, height = 750,
            background_color ='white',
            min_font_size = 20).generate(text)

    # Generate plot
    plt.figure(figsize = (7.5, 7.5), facecolor = None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.show()

    #save wordplot and display (displauys a new wordplot every time you refresh or open it the app again
    plt.savefig('wordcloud.jpg')
    img= Image.open("wordcloud.jpg")
    st.image(img)


#Map Displaying Stadium Locations within the selected state and conference
def interactive_page1():
    global df
    read_data()
    statenames()

    #sort names alphabetically and only return unique values (no repetition of states in the selectbox)
    sortedStates = sorted(df.state.unique())
    st.sidebar.title('Where are stadiums located?')
    state_selection = st.sidebar.selectbox('Select a state', sortedStates)
    division_selection = st.sidebar.radio('Select division',df['div'].unique())

    #Criteria for map of state and division
    st.title(f'{state_selection} NCAA Football Stadiums in the {division_selection} division')
    df = pd.DataFrame(data = df[(df['state'] == state_selection) & (df['div'] == division_selection)])
    if df.empty == True:
            st.write(f'There are no stadiums in {state_selection} in the {division_selection} division.')
    else:
        st.dataframe(df[['city', 'team','latitude', 'longitude']])
        map_df = df[['team','latitude', 'longitude']]
        view_state = pdk.ViewState(latitude = map_df['latitude'].mean(),
                                   longitude = map_df['longitude'].mean(),
                                   zoom=6.5)

        layer = pdk.Layer('ScatterplotLayer',
                      data = map_df,
                      get_position='[longitude,latitude]',
                      get_radius=900,
                      get_color=[255, 0, 0],
                      pickable = True)

        tool_tip = {'html': 'Team:<br/> <b>{team}</br> ', 'style': {'backgroundColor': 'red', 'color': 'white'}}
        map = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                   initial_view_state=view_state,
                   layers=[layer],
                   tooltip=tool_tip)
        st.pydeck_chart(map)

    #Check box to have map only show the stadiums within the selected state, division, AND conference
    more = st.sidebar.checkbox('Would you like to select a specific conference?')
    if more:
        conference_selection = st.sidebar.selectbox('Select Conference', df.conference.unique())
        st.title(f'{state_selection} NCAA Football Stadiums in the {division_selection} division and {conference_selection} conference')
        df = pd.DataFrame(data = df[(df['state'] == state_selection) & (df['div'] == division_selection) & (df['conference'] == conference_selection)])
        st.dataframe(df[['city', 'team', 'latitude', 'longitude']])
        st.map(df)


#Display table with the data of stadiums built within the selected year. Select Checkbox to see which of these stadiums were expanded.
def interactive_page2():
    global df
    read_data()
    statenames()

    #Criteria for dataframe based on when stadiums were built
    st.sidebar.title("When stadiums were built in each year?")
    year_built = st.sidebar.slider('Select a year', min_value=1895, max_value=2014)
    st.title(f'NCAA Football Stadiums built in {year_built}')
    df = pd.DataFrame(data = df[(df['built'] == year_built)])
    dfSorted = df.sort_index()
    if df.empty == True:
            st.write(f'No stadiums were built in {year_built}.')
    else:
        st.dataframe(dfSorted[['state', 'team', 'built']])

    #Checkbox to display which of these stadiums were expanded
    expand = st.sidebar.checkbox('Check to see which of these stadiums were expanded')
    if expand:
        df = pd.DataFrame(data = df[(df['built'] == year_built) & (~df['expanded'].isnull())])
        dfSorted = df.sort_index()
        if df.empty == True:
            st.write(f'No stadiums built in {year_built} were expanded.')
        else:
            st.dataframe(dfSorted[['state', 'team', 'built', 'expanded']])


#Line chart of varying capacities based on user input
def interactive_page3():
    global df
    read_data()
    statenames()

    #Sort states alphabetically
    sortedStates = sorted(df.state.unique())
    st.sidebar.title("What are the capacities of stadiums?")

    #Criteria for graph based on state and division input
    state_choice = st.sidebar.multiselect('Select state(s)', sortedStates)
    division = st.sidebar.text_input("Enter a division: fbs or fcs")
    graph = st.sidebar.selectbox("Would you like to see a:", ('Bar chart', 'Line chart'))
    st.title('NCAA Football Stadiums Capacities')
    df = pd.DataFrame(data = df[(df['div'] == division) & (df['state'].isin(state_choice))])

    #Check if the dataframe is empty by on user selection. If not return the graph.
    if df.empty == True:
        st.write(f'There are no stadiums in both the {state_choice} conference and {division} division.')
    else:
        chart_data = pd.DataFrame(df[(df['div'] == division) & (df['state'].isin(state_choice))],
        columns=['capacity'])

        #User can choose between a bar chart and a line chart
        if graph == 'Bar chart':
            st.write("Bar Chart of Stadium Capacities",", ".join([stadium.capitalize() for stadium in chart_data]))
            fig = px.bar(df, y=df['capacity'], barmode='group')
            st.plotly_chart(fig)
        if graph == 'Line chart':
            st.write("Line Chart of Stadium Capacities",", ".join([stadium.capitalize() for stadium in chart_data]))
            fig = px.line(df, y=df['capacity'])
            st.plotly_chart(fig)


#Conclusion Page
def end():
    st.title("You've reached the end!")
    if st.button("Click here!"):
        st.balloons()


#Navigation
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", ["Welcome", "Stadium Locations", "Stadiums Built and Expanded", "Stadium Capacities", "Conclusion"])
if selection == "Welcome":
    welcome()
if selection == "Stadium Locations":
    interactive_page1()
if selection == "Stadiums Built and Expanded":
    interactive_page2()
if selection == "Stadium Capacities":
    interactive_page3()
if selection == "Conclusion":
    end()

