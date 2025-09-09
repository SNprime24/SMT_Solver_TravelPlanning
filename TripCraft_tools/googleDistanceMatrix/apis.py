import requests
from utils.func import extract_before_parenthesis
import re
import json
import os
from requests.exceptions import SSLError
import time
import sys
import pandas as pd
import numpy as np
from z3 import *

# This tool refers to the "DistanceMatrix" in the paper. Considering this data obtained from Google API, we consistently use this name in the code. 
# Please be assured that this will not influence the experiment results shown in the paper. 

def extract_before_parenthesis(s):
    match = re.search(r'^(.*?)\([^)]*\)', s)
    return match.group(1) if match else s

class GoogleDistanceMatrix:
    def __init__(self, subscription_key: str="") -> None:
        self.gplaces_api_key: str = subscription_key
        self.data =  pd.read_csv('TripCraft_database\distance_matrix\city_distances_times_full.csv')
        print("OSM_DistanceMatrix loaded.")



    def run_check(self, origin, destination):
        response = self.data[(self.data['origin'] == origin) & (self.data['destination'] == destination)]
        if len(response) > 0:
            if response['duration_min'].values[0] is None or response['distance_km'].values[0] is None or response['duration_min'].values[0] is np.nan or response['distance_km'].values[0] is np.nan:
                    return f'Driving is not feasible from {origin} to {destination}'
            else:
                return f'Driving exists from {origin} to {destination}'
        else:
            return f'Driving is not feasible from {origin} to {destination}'



    def run_search(self, origin):
        response = self.data[(self.data['origin'] == origin)]
        if len(response) > 0:
            return np.unique(np.array(response['destination']))
        else:
            return f'Driving is not feasible from {origin}'



    def run(self, origin, destination, mode='driving'):
        origin = extract_before_parenthesis(origin)
        destination = extract_before_parenthesis(destination)
        info = {"origin": origin, "destination": destination,"cost": None, "duration": None, "distance": None}
        response = self.data[(self.data['origin'] == origin) & (self.data['destination'] == destination)]
        if len(response) > 0:
                if response['duration_min'].values[0] is None or response['distance_km'].values[0] is None or np.isnan(response['duration_min'].values[0]) or np.isnan(response['distance_km'].values[0]):
                    return "No valid information."
                info["duration"] = response['duration_min'].values[0]
                info["distance"] = response['distance_km'].values[0]
                # print(info["duration"],type(info["duration"]))
                # print(info["distance"],type(info["distance"]))
                if 'driving' in mode:
                    # info["cost"] = int(eval(info["distance"].replace("km","").replace(",","")) * 0.05)
                    info["cost"] = int(info["distance"]*0.05)
                elif mode == "taxi":
                    # info["cost"] = int(eval(info["distance"].replace("km","").replace(",","")))
                    info["cost"] = int(info["distance"])
                if int(info["duration"])> 1440 :
                    return "No valid information."
                return f"{mode}, from {origin} to {destination}, duration: {info['duration']}, distance: {info['distance']}, cost: {info['cost']}"

        # return f"{mode}, from {origin} to {destination}, no valid information."   
        return "No valid information."




    def run_for_evaluation(self, origin, destination, mode='driving'):
        origin = extract_before_parenthesis(origin)
        destination = extract_before_parenthesis(destination)
        info = {"origin": origin, "destination": destination,"cost": None, "duration": None, "distance": None}
        response = self.data[(self.data['origin'] == origin) & (self.data['destination'] == destination)]
        if len(response) > 0:
                if response['duration_min'].values[0] is None or response['distance_km'].values[0] is None or response['duration_min'].values[0] is np.nan or response['distance_km'].values[0] is np.nan:
                    return info
                info["duration"] = response['duration_min'].values[0]
                info["distance"] = response['distance_km'].values[0]

                
                if int(info["duration"])< 1440:
                    if 'driving' in mode:
                        # info["cost"] = int(eval(info["distance"].replace("km","").replace(",","")) * 0.05)
                        info["cost"] = int(info["distance"]*0.05)
                    elif mode == "taxi":
                        # info["cost"] = int(eval(info["distance"].replace("km","").replace(",","")))
                        info["cost"] = int(info["distance"])
                        
                return info

        return info 




    def run_online(self, origin, destination, mode="driving"):
        # mode in ['driving','taxi','walking', 'distance','transit']
        endpoint = "https://maps.googleapis.com/maps/api/distancematrix/json"

        params = {
            "origins": origin,
            "destinations": destination,
            "mode": mode if mode=="taxi" else "driving",
            "key": self.gplaces_api_key
        }

        while True:
            try:
                response = requests.get(endpoint, params=params)
                break
            except SSLError:
                time.sleep(30)

        data = response.json()
        info = {"origin": origin, "destination": destination,"cost": None, "duration": None, "distance": None}
        if data['status'] == "OK":
            element = data['rows'][0]['elements'][0]
            if element['status'] == "OK":
                info["duration"] = element['duration']['text']
                info["distance"] = element['distance']['text']
                if 'driving' in mode:
                    info["cost"] = int(eval(info["distance"].replace("km","").replace(",","")) * 0.05)
                elif mode == "taxi":
                    info["cost"] = int(eval(info["distance"].replace("km","").replace(",","")))
                # if 'day' in info["duration"]:
                #     return "No valid information."
                return f"{mode}, from {origin} to {destination}, duration: {info['duration']}, distance: {info['distance']}, cost: {info['cost']}"

        return "No valid information."   




    def run_for_annotation(self, origin, destination, mode="driving"):
        # mode in ['driving','taxi','walking', 'distance','transit']
        endpoint = "https://maps.googleapis.com/maps/api/distancematrix/json"

        params = {
            "origins": extract_before_parenthesis(origin),
            "destinations": extract_before_parenthesis(destination),
            "mode": mode if mode!="taxi" else "driving",
            "key": self.gplaces_api_key
        }
        
        response = requests.get(endpoint, params=params)
        data = response.json()
        info = {}
        if data['status'] == "OK":
            element = data['rows'][0]['elements'][0]
            if element['status'] == "OK":
                info["duration"] = element['duration']['text']
                info["distance"] = element['distance']['text']
                info["cost"] = None
                if 'driving' in mode:
                    info["cost"] = int(eval(info["distance"].replace("km","").replace(",","")) * 0.05)
                elif mode == "taxi":
                    info["cost"] = int(eval(info["distance"].replace("km","").replace(",","")))
        else:
            info = {"duration": "N/A", "distance": "N/A", "cost": "N/A", "Hint":"Please check the input."}
        return info



    def run_for_all_cities(self, origin, all_cities, cities_list):
        """Search for flights by origin, destination, and departure date."""
        cities = copy.deepcopy(cities_list)
        cities.insert(0, origin)
        all_cities = copy.deepcopy(all_cities)
        all_cities.insert(0, origin)

        results = Array('driving', IntSort(), IntSort(), IntSort(), RealSort()) # origin_city destination_city [distance duration cost length] information

        for i, ori in enumerate(cities):
            if i!= len(cities)-1:
                destination = cities[i+1]
            else:
                destination = cities[0]

            result = self.data[self.data["origin"] == ori]
            result = result[result["destination"] == destination]

            if len(result) != 0 and (type(np.array(result)[0][3])==str or not math.isnan(np.array(result)[0][3])) and int(np.array(result)[0][3])< 1440:
                duration = int(np.array(result)[0][3]) 
                distance = int(np.array(result)[0][2])
                results = Store(results, all_cities.index(ori), all_cities.index(destination), 0, distance)
                results = Store(results, all_cities.index(ori), all_cities.index(destination), 1, duration)
                results = Store(results, all_cities.index(ori), all_cities.index(destination), 2, distance * 0.05)
                results = Store(results, all_cities.index(ori), all_cities.index(destination), 3, 1)
            else:
                results = Store(results, all_cities.index(ori), all_cities.index(destination), 3, -1)
        return results



    def get_info(self, info, i, j, key):
        element = ['Distance', 'Duration', 'Price', 'Length']
        if type(i) == str and type(j) == str:
            i = 0
            j = 1
        elif type(i) == str:
            i = 0
            j += 1
        elif type(j) == str:
            j = 0
            i += 1
        else:
            i += 1
            j += 1
        info_key = Select(info, i, j, element.index(key))
        length = Select(info, i, j, 3)
        return info_key, length
