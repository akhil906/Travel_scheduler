# -*- coding: utf-8 -*-
"""data_mining_project_final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1LaLBQVi0zQK-9fsaWtbj6AEWQSrzjaSi
"""

#pip install ortools

api_key = ''  #input the api key which has access to distancematrix api,place api,nearbysearch api access

import requests

place = input('Please enter the city name: ')
response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+str(place)+"&key="+str(api_key))
resp_json_payload = response.json()
#print(resp_json_payload['results'][0]['geometry']['location'])
lats = resp_json_payload['results'][0]['geometry']['location']['lat']
longs = resp_json_payload['results'][0]['geometry']['location']['lng']
print(str(lats)+' '+str(longs))

import requests
#no_miss = 'San Diego Zoo'
no_miss = input('Please enter the interested place in the city: ')
no_miss_final = no_miss+' '+str(place)
response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+str(no_miss_final)+"&key="+str(api_key))
resp_json_payload = response.json()
#print(resp_json_payload['results'][0]['geometry']['location'])
lats_nomiss = resp_json_payload['results'][0]['geometry']['location']['lat']
longs_nomiss = resp_json_payload['results'][0]['geometry']['location']['lng']
print(str(lats_nomiss)+' '+str(longs_nomiss))

"""The schedule for the tour has been developed by making use of the places api to get the details of the nearest tourist attractions and shopping malls in the city that has been specified.

We start from the place provided by user (we assume that the people would arrive at the destination before the schedule of 9AM) and we search for the shopping places nearest to the zoo so that the users can do shopping in the mall(selected shopping mall as there would be a large collection of stores in the mall and the people can also simultaneously have lunch at the restraunts of their choice in the mall instead of taking them seperately to a restraunt for lunch).

In this code cell below we get the details of the shopping malls and popular tourist destinations in the location provided in the form of a pandas dataframe having the columns

'name' - name of the places
'business_status' - whether it is still operational or closed
'formatted_address' - the address of the places
'rating' - the rating for that particular place indicating if place is good
'user_ratings_total' - number of people who rated which can give a rough idea of how many people visited the place, more reviews might mean more people might visit that place.
'website' - the website of the place which people can check out
'lat' - the latitude of the place
'lng' - longitude of the place
'type' - type of the place like museum,park etc if we are not able to determine this we say that it is a tourist place


"""

import pandas as pd
import numpy as np
import json
from bs4 import BeautifulSoup
import json
import requests
from urllib import request
from sklearn.neighbors import BallTree
from io import StringIO


#url = "https://maps.googleapis.com/maps/api/place/textsearch/json?query=indianapolis+city+point+of+interest&language=en&key="+str(api_key) #url for the google maps api to get popular places in indianapolis
place = str(place).replace(' ','+')
url = "https://maps.googleapis.com/maps/api/place/textsearch/json?query="+str(place)+"+city+point+of+interest&language=en&key="+str(api_key)

#this code has the logic to get and parse the json data
text = request.urlopen(url).read()
s = BeautifulSoup(text,'html.parser')
r=json.loads(s.text)
keys = list(r['results'][0].keys())
data_full = r['results']
length = len(data_full)
print(data_full)
print('\n')

check = ['name','business_status','formatted_address','rating','user_ratings_total','website']
check_plus = ['name','business_status','formatted_address','rating','user_ratings_total','website','lat','lng','type'] #the final list of columns for the popular places
df = pd.DataFrame()

#url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=39.7675746,-86.1796262&radius=3000&type=shopping_mall&key="+str(api_key) #url for google maps api to get list of shopping malls near indianapolis zoo
url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+str(lats_nomiss)+','+str(longs_nomiss)+"&radius=3000&type=shopping_mall&key="+str(api_key)

#this code has the logic to get and parse the json data
text1 = request.urlopen(url).read()
s1 = BeautifulSoup(text1,'html.parser')
malls=json.loads(s1.text)

data_malls = malls['results']
length_malls = len(data_malls)

check_malls = ['name','business_status','formatted_address','rating','user_ratings_total','website']
check_plus_malls = ['name','business_status','formatted_address','rating','user_ratings_total','website','lat','lng','type'] #the final list of columns for the nearby shopping locations

#code to get the details of the nearby tourist destination in indianapolis from the places api
count = 0
for j in range(length):
    data = data_full[j]
    temp = {}
    for i in check:    
        if i in keys:
            if i=='formatted_address':
                print(data[i])
            try:
                temp[i]=data[i]
            except Exception as e:
                temp[i] = ' '
    lat = ''
    long = ''
    try:
        geo = data['geometry']
        location = geo['location']
        lat = location['lat']            #to get the latitude of the location
        lng = location['lng']            #to get longitude of the location
        
        temp['lat'] = str(lat)
        temp['lng'] = str(lng)
    except Exception as e:
        temp['lat'] = ''
        temp['lng'] = ''

    flag=0
    for k in data['types']:
        if k in ['tourist_attraction','point_of_interest','establishment']:
            continue
        else:
            temp['type']=k
            flag=1
    if flag==0:
        temp['type']='tour'
        
    url_dummy = "https://maps.googleapis.com/maps/api/place/details/json?place_id="+str(data["place_id"])+"&key="+str(api_key)  #geting extra details of the location from the places api
    text2 = request.urlopen(url_dummy).read()
    s2 = BeautifulSoup(text2,'html.parser')
    r2=json.loads(s2.text)
    #print(r2['result']['website'])    
    try:
        temp["website"] = r2['result']["website"]
    except Exception as e:
        temp["website"] = ' '
    
    if count==0:
        df = pd.DataFrame(temp,columns = check_plus,index=[0])   #creating the dataframe initially
        count=count+1
    else:
        df1 = pd.DataFrame(temp,columns = check_plus,index=[0])  #appending the dataframe with new rows
        df = pd.concat([df, df1])
print(df)

#code to get the details of the nearby shopping malls near indianapolis zoo from the places api
for j in range(0,length_malls):
    data = data_malls[j]
    temp = {}
    for i in check_malls:    
        if i in keys:
            #print(data[i]) 
            try:
                if data[i]==None:
                    temp[i]=' '
                temp[i]=data[i]
            except Exception as e:
                temp[i]=' '
    lat = ''
    long = ''
    try:
        geo = data['geometry']
        location = geo['location']
        lat = location['lat']           #to get the latitude of the location
        lng = location['lng']           #to get longitude of the location
        
        temp['lat'] = str(lat)
        temp['lng'] = str(lng)
    except Exception as e:
        temp['lat'] = ''
        temp['lng'] = ''
    
    url_dummy = "https://maps.googleapis.com/maps/api/place/details/json?place_id="+str(data["place_id"])+"&key="+str(api_key)  #geting extra details of the location from the places api
    text2 = request.urlopen(url_dummy).read()
    s2 = BeautifulSoup(text2,'html.parser')
    r2=json.loads(s2.text)
    
    try:
        temp["formatted_address"] = r2['result']["formatted_address"]
    except Exception as e:
        temp["formatted_address"] = ' '
    try:
        temp["website"] = r2['result']["website"]
    except Exception as e:
        temp["website"] = ' '
        
    temp['type'] = 'shopping'    
    df1 = pd.DataFrame(temp,columns = check_plus_malls,index=[0])    
    df = pd.concat([df, df1])                 #appending the dataframe with new rows

df.set_index('name', inplace=True)       #setting the index as the name column for easy retrieval of data
df

#In this step we are getting the nearest shopping malls to our locations and to do this we are making use of KNN and BallTree in order to get the nearest points based on the haversine distance between the latitude and longitudes of the places. Later on we would be using this for further analysis.
# referenced from https://stackoverflow.com/questions/61952561/how-do-i-find-the-neighbors-of-points-containing-coordinates-in-python and modified to fit our use case

dfm = df[df['type']=='shopping']
dfm = dfm[['lat','lng']]
dfm['lat'] = dfm['lat'].astype(float)
dfm['lng'] = dfm['lng'].astype(float)

dfm['new_name'] = dfm.index
dfm.index = range(0,len(dfm['lat']))
dfm

#making use of the BallTree and haversine distances to get the nearest shopping malls
tree = BallTree(np.deg2rad(dfm[['lat', 'lng']].values), metric='haversine')
df_nomiss = pd.DataFrame({'lat':lats_nomiss,'lng':longs_nomiss},index=[0])

query_lats = df_nomiss['lat']
query_lons = df_nomiss['lng']

#using the knn inorder to get the shopping malls in the nearest vicinity to the locations
distances, indices = tree.query(np.deg2rad(np.c_[query_lats, query_lons]), k = len(dfm['lat']))

r_km = 6371
distance_matrix1 = {} #this has the nearest shopping malls to the locations which we can use for further analysis later
for name, d, ind in zip(dfm['new_name'], distances, indices):  
  for i, index in enumerate(ind):    
    distance_matrix1[dfm['new_name'][i]] = d[i]*r_km

"""Next we are calculating the distance matrix or the distance/driving time from a point to all other points in consideration and only the operational places are added to avoid surprises as we dont want to include non operational places and find out that it is closed on visiting the place."""

#this code is to get the distance matrix or the distance/driving time from a point to all other points in consideration and only the operational places are added to avoid surprises
distance_matrix = pd.DataFrame({},columns=list(df[df['business_status']=='OPERATIONAL'].index),index=list(df[df['business_status']=='OPERATIONAL'].index))

#creating empty distance matrix to be populated later
x = list(distance_matrix.columns)
print(x)
for i in x:
    distance_matrix[i]=''
distance_matrix

"""Next we are calculating the distance matrix by making use of the distance matrix api to get the driving time in between 2 points which we are placing the distance matrix so that we can get a rough idea on how much time commute takes from the places and provide an optimal path for the journey so that we can cover more places in relatively lesser times.

The distance from a place to itself is taken as 1 minute here as we are considering 1 minute as a buffer time to reach different places in the location and is the value returned from the distance matrix api. If needed we can also change this to 0 minutes.
"""

count=0
for i in list(distance_matrix.index):
    for j in list(distance_matrix.columns):
        try:
            if distance_matrix[i][j]!='':
                distance_matrix.at[i,j] = distance_matrix[i][j]
                continue
        except Exception as e:
            continue
        
        lat = list(df[df.index.str.startswith(i)]['lat'])
        lng = list(df[df.index.str.startswith(i)]['lng'])
        lat1 = list(df[df.index.str.startswith(j)]['lat'])
        lng1 = list(df[df.index.str.startswith(j)]['lng'])

        print(str(lat[0])+' '+str(lng[0]))
        print(str(lat[0])+' '+str(lng[0]))

        try:
            #the call to distance matrix api and parsing the data we get from there in order to construct the distance matrix
            url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins="+str(lat[0])+","+str(lng[0])+"&destinations="+str(lat1[0])+","+str(lng1[0])+"&key="+str(api_key)

            text = request.urlopen(url).read()
            s = BeautifulSoup(text,'html.parser')
            
            distance=json.loads(s.text)              
            
            distance_matrix.at[i,j] = str(distance['rows'][0]['elements'][0]['duration']['text'])
        except Exception as e:
            print("error")
distance_matrix

"""Next step is to select the most popular places we can visit. We are assuming that the place would be good if it has a good average rating from a large number of people which can tell 2 things.

1. The place is actually good if it has a good average rating
2. The place is visited by many people if it has a large number of ratings
So inorder to remove bias in the ratings we are making sure that we consider the rating of the place only if has more than 2000 ratings( there might be some smaller places which are actually much more better and have a fewer reviews but we are ignoring these for now, like we are following the words of the majority in this case).

We are also making sure that we select a place from each of the place types so that we dont end up taking people to similar places like to 2 museums etc on a single day so that we can maintain diversity in the tour schedule.
"""

df.loc[df.rating == ' ', 'rating'] = '0.0'
df.loc[df.user_ratings_total == ' ', 'user_ratings_total'] = '0'
df_schedule = pd.DataFrame()

for i in list(set(list(df['type']))):
    if 'office' in i or 'store' in i:
        continue
    df1 = df[df['type']==i]
    df1 = df1[df1['user_ratings_total'].astype(int)>2000]  #filtering out places with less than 2000 reviews
    df1 = df1[df1['rating'].astype(float)>4.0]             #selecting a place with more than 4 star review
    
    df2 = df1.sort_values(['rating'],ascending=False)
    df3 = df2.sort_values(['user_ratings_total'],ascending=False)
    try:
      df4 = df3[df3.index.str.startswith(list(df3.index)[0])]   #selecting the best place with the maximum rating by sorting it on both the ratings and the number of ratings to reduce bias
    except Exception as e:
      continue
    print(df4)
    df_schedule = pd.concat([df_schedule, df4])
df_schedule

#next we are just getting the subset of the distance matrix for the final list of places that we have selected from the step above so that we can plot the optimal path

distance_schedule = distance_matrix[df_schedule.index]
distance_schedule_final = distance_schedule[pd.DataFrame(distance_schedule.index.tolist()).isin(df_schedule.index).any(1).values]
distance_schedule_final = distance_schedule_final[list(distance_schedule_final.index)]
distance_schedule_final

#getting a numpy array so that we can pass it to the algorithms solving the travelling salesman problem
distance_array = distance_schedule_final.to_numpy()
distance_array

#converting the matrix values to intergers to get the optimal path
distance_array_final = []
for i in distance_array:
    temp = []
    for j in i:
        temp.append(int(j.split(' ')[0]))
    distance_array_final.append(temp)
distance_array_final

"""Next we are making use of Google OR tools inorder to implement the travelling salesman problem. We are using this inorder to get the optimal path from a starting location back to the same location and covering all the given locations and with a minimum cost( cost here is time so we make sure that we are covering all the places and coming back to start point in minimum cost).

We are planning to return back to the start point or the Indianapolis Zoo as it is the nearest to the bus station and airport and hence making it easy for the students to reach home in Indianapolis or also in other states by catching a flight(if we think this tour is done during the last day of the session before all students leave home).

More details on the travelling salesman problem is here https://en.wikipedia.org/wiki/Travelling_salesman_problem

The code from below has been taken from the tutorial/documentation of OR tools and I found it better as it gives the most optimal solution for the travelling salesman problem in comparision to we writing the solution ourselves.
"""

import ortools
from ortools.constraint_solver import pywrapcp
m = pywrapcp.RoutingIndexManager(len(distance_array_final),1, 0) #here 1 is that we all want to move in same direction and not like we have 2 cars and we want to split people in 2 of them and move seperately since students all would be going at once the parameter value here is 1.
# 0 parameter above means that we are starting from the point 0 in the numpy array or Indianapolis Zoo
routing = pywrapcp.RoutingModel(m)

def distance_callback(from_index, to_index):    
    from_node = m.IndexToNode(from_index)
    to_node = m.IndexToNode(to_index)
    return distance_array_final[from_node][to_node]

transit_callback_index = routing.RegisterTransitCallback(distance_callback)

routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

#the code to get the most optimal path so that the time/cost is least
def print_solution(manager, routing, solution):    
    index = routing.Start(0)    
    plan_output = ''
    route_distance = 0
    while not routing.IsEnd(index):
        plan_output += ' {} ->'.format(manager.IndexToNode(index))
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
    plan_output += ' {}\n'.format(manager.IndexToNode(index))
    return plan_output

solution = routing.SolveWithParameters(search_parameters)
if solution:
    x = print_solution(m, routing, solution)

#list of all the places that we need to visit and the order in which we need to visit, we are also returning back to the zoo at the end
final_places = []
places = list(distance_schedule_final.index)
for i in (x.strip('\n').split('->')):
  final_places.append(places[int(i)])
final_places

df_schedule_ordered = df[['formatted_address','rating','user_ratings_total','website','type']].copy()
df_schedule_ordered = df_schedule_ordered.loc[final_places[:-1]]
df_schedule_ordered

"""Next we develop the schedule based on the order of the places that we plan on visiting and we also add these extra attributes to get a precise understanding of the time.

in_time* - approximate time we reach the place
out_time* - approximate time at which we need to return to the car/bus
time_at_venue - time that we spend in the place
journey_time - time taken to reach the place from the previous place
Here journey_time is time taken to reach the place from the previous place or the journey_time for X is the journey time to X from the previous place Y.

We are also putting a buffer of 10 minutes at each location so that we can accomodate the time taken for onboarding and deboarding the passengers and waiting for any people who are late to board the bus. So if we enter the place at 2PM and time spent there is 2 hours then out_time or time to reach the bus is 4PM but we start at 4:10PM to next place to give some time so that we can wait for people to come and board the bus/car and be ready. So the in_time of the next place would be out_time+10minutes+journey_time_from_place_to_nextplace

We are giving the following times at each place:

Normal Places - 1hr 30min
Lunch&Shopping - 2hr

We can also change these as per the need.


"""

#initializing the extra columns
df_schedule_ordered['activity'] = ''
df_schedule_ordered['in_time*'] = ''
df_schedule_ordered['out_time*'] = ''
df_schedule_ordered['time_at_venue*'] = ''
df_schedule_ordered['journey_time*'] = ''
count= 0 
for i in range(len(final_places)-1):
  if count==0:    
    df_schedule_ordered.loc[df_schedule_ordered.index.str.startswith(final_places[i]),'in_time*'] = '9 AM'
    df_schedule_ordered.loc[df_schedule_ordered.index.str.startswith(final_places[i]),'out_time*'] = '10:30 AM'
    df_schedule_ordered.loc[df_schedule_ordered.index.str.startswith(final_places[i]),'time_at_venue*'] = '1hr 30min'
    df_schedule_ordered.loc[df_schedule_ordered.index.str.startswith(final_places[i]),'journey_time*'] = '0 min'
    df_schedule_ordered.loc[df_schedule_ordered.index.str.startswith(final_places[i]),'activity'] = 'tour'
    count=count+1
  else:
    time_temp = list(df_schedule_ordered[df_schedule_ordered.index.str.startswith(final_places[i-1])]['out_time*'])[0]
    time_hours = int(time_temp.split(' ')[0].split(':')[0])      #getting the hours value
    time_minutes = int(time_temp.split(' ')[0].split(':')[1])    #getting the minutes value 
    temp_final = time_minutes+10+int(distance_matrix[final_places[i-1]][final_places[i]].split(' ')[0])  #getting the final time adding the 10min buffer and journey time 
    
    hours_final = (time_hours+int(temp_final//60))%12     #calculating the hour value of the in_time of the place
    if hours_final == 0:
      hours_final = 12                                    #replace 0 with 12 if the time is 12PM
    minutes_final = temp_final%60
    if minutes_final<10:
      minutes_final = '0'+str(minutes_final)             #padding the minutes with 0 if the minutes value is 2 we make it 02 with padding
    final_time = str(hours_final)+":"+str(minutes_final)+" PM"   #calculating final in_time and we are assuming it is always PM as we are starting at 9AM and spending 3.5 hours at zoo

    if list(df_schedule_ordered.loc[df_schedule_ordered.index.str.startswith(final_places[i])]['type']=='shopping')[0]:
      buffer = 120
      time_words = '2hr'
      activity = 'lunch&shopping'
    else:
      buffer = 90
      time_words = '1hr 30min'
      activity = 'tour'
    
    #code to calculate the out_time for the place based on the type of the venue and we do the same calculations as we did for the in_time like padding minutes making 0 hour as 12 etc
    out_hours = (hours_final+int(buffer//60))%12
    if out_hours == 0:
      out_hours = 12
    extra = (int(minutes_final)+int(buffer%60))//60        #if the hour changes to next hour because of the minutes add the extra hour value to the out_time
    if extra>0:
      out_hours=out_hours+extra
    out_minutes = (int(minutes_final)+int(buffer%60))%60
    if out_minutes<10:
      out_minutes = '0'+str(out_minutes)
    out_time = str(out_hours)+":"+str(out_minutes)+" PM"

    df_schedule_ordered.loc[df_schedule_ordered.index.str.startswith(final_places[i]),'in_time*'] = final_time
    df_schedule_ordered.loc[df_schedule_ordered.index.str.startswith(final_places[i]),'out_time*'] = out_time
    df_schedule_ordered.loc[df_schedule_ordered.index.str.startswith(final_places[i]),'time_at_venue*'] = time_words
    df_schedule_ordered.loc[df_schedule_ordered.index.str.startswith(final_places[i]),'journey_time*'] = distance_matrix[final_places[i-1]][final_places[i]]
    df_schedule_ordered.loc[df_schedule_ordered.index.str.startswith(final_places[i]),'activity'] = activity
df_schedule_ordered

df_schedule_ordered.to_csv('final_schedule.csv')
