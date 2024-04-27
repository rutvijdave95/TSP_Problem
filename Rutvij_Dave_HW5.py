# import necessary python packages
import pandas as pd
import numpy as np
import random
from haversine import haversine
import altair as alt
from vega_datasets import data
import logging
logging.getLogger("matplotlib.font_manager").disabled = True



def select_random_cities(num_cities):
    # Creating a new dataframe to only work with city names and the longitude/latitude
    traveling_cities = uscities_df[['city', 'lat', 'lng']].copy()
    y = len(traveling_cities)
    # Choosing random cities that the salesman will travel to
    random_cities = random.sample(range(0, y), num_cities)
    cities = traveling_cities.loc[random_cities]
    print(cities)
    return cities


def parse_cities(cities):
    # deconstructing the cities datafarme to creating a tuple of the longtidue/latitude
    cityname = list(cities['city'])
    latitude = list(cities['lat'])
    longitude = list(cities['lng'])
    coordinates = list(zip(latitude, longitude))
    city_coordinates_dict = dict(zip(cityname, coordinates))
    return city_coordinates_dict


def calculateDistance(i, j):
    # Implementing the Haversine package to calculate the distance between two cities in miles
    coordinate1 = i
    coordinate2 = j

    distance = round(haversine(coordinate1, coordinate2, unit='mi'), 1)

    return distance


def proximity_matrix(city_coordinates_dict):
    # lst_cities = city_coordinates_dict.keys()
    city_coordinates = city_coordinates_dict.values()

    # Creating a proximity matrix to determine
    n = len(city_coordinates)

    fluff = round(3.14159 * 3958.8)

    prox_matrix = np.zeros((n, n))
    for i, coord_i in enumerate(city_coordinates):
        for j, coord_j in enumerate(city_coordinates):
            if i == j:
                prox_matrix[i, j] = fluff
            elif i < j:
                prox_matrix[i, j] = fluff
            else:
                dis = calculateDistance(coord_i, coord_j)
                prox_matrix[i, j] = dis

    return prox_matrix


def greedy_algo(city_coordinates_dict):
    # Converting the incoming dictionary in to a list of the keys and values {cityname, (lat, long)}
    lst_cities = list(city_coordinates_dict.keys())
    tour = []
    tour_coordinates = []

    unvisited_cities = lst_cities.copy()
    start = unvisited_cities.pop(0)
    cc_coordinates_start = city_coordinates_dict[start]
    tour.append(start)
    tour_coordinates.append(cc_coordinates_start)

    #Using a while loop to determine the nearest city to the current city
    while (len(unvisited_cities) > 0):
        current_city = tour[-1]
        cc_current = city_coordinates_dict[current_city]

        def distance_from_current_city(city):
            cc_city = city_coordinates_dict[city]
            distance = calculateDistance(cc_current, cc_city)
            return distance

        nearest_city = (min(unvisited_cities, key=distance_from_current_city))
        tour.append(nearest_city)
        tour_coordinates.append(city_coordinates_dict[nearest_city])
        unvisited_cities.remove(nearest_city)


    #appending the starting coordinate to the end so that the salesman returns homes
    se_coord = tour_coordinates[0]
    tour_coordinates.append(se_coord)

    #Using a for loop to calculate the distance traveled
    yy = len(tour_coordinates) - 1
    total_distance = 0
    leg_distance = []
    for i in range(yy):

        city_from = tour_coordinates[i]
        city_to = tour_coordinates[i+1]
        xx = round(calculateDistance(city_from, city_to),1)
        leg_distance.append(xx)
        total_distance += xx

    result = tour, tour_coordinates, total_distance, leg_distance

    return result

def plot_tour(tour, tour_coordinates):
    #Function to create a plot of Barry's travels
    labels = tour
    labels_first = tour[0]
    labels.append(labels_first)
    lats = []
    longs = []

    for lat, long in tour_coordinates:
        lats.append(lat)
        longs.append(long)

    data_ar = pd.DataFrame({'city_name': labels,
                        'lats': lats,
                         'longs': longs})

    last_two_connection = data_ar.iloc[-2:]

    #plt.show()
    us_states = alt.topo_feature(data.us_10m.url, 'states')
    # us map
    base_map = alt.Chart(us_states, title = "Barry's Travels").mark_geoshape(
        fill='lightgray',
        stroke='white'
    ).project('albersUsa')

    # plot the cities
    us_cities = alt.Chart(data_ar).mark_circle(size=100, color='red')\
        .encode(
        longitude='longs:Q',
        latitude='lats:Q',
        tooltip='city_name:N'
    )

    # connect the cities
    us_connections = alt.Chart(data_ar).mark_line(color='blue').encode(
        longitude='longs:Q',
        latitude='lats:Q',
        order=alt.Order('index:O')
    )

    us_connections_last_two = alt.Chart(last_two_connection).mark_line(color='blue').encode(
        longitude='longitude:Q',
        latitude='latitude:Q'
    )

    city_labels = alt.Chart(data_ar).mark_text(
        align='left',
        baseline='bottom',
        dx=7  # Offset to avoid overlapping with the city point
    ).encode(
        longitude='longs:Q',
        latitude='lats:Q',
        text='city_name:N'
    )

    # plot them all
    plot = base_map + us_cities + us_connections + us_connections_last_two + city_labels
    plot.show()
    oo = plot.save("Travel.html")

    return oo



if __name__ == "__main__":
    #While Loop to catch any
    while True:
        try:
            num_cities = int(input("How many cities will our salesman, Barry Allen, travel to?"))
            if num_cities > 1:
                break
        except ValueError:
            print("Your input is not an integer, please provide an integer!")

    uscities_df = pd.read_csv('uscities.csv')
    aa = select_random_cities(num_cities)
    bb = parse_cities(aa)
    dd = proximity_matrix(bb)
    ee, ff, gg, hh = greedy_algo(bb)
    avg_leg = round((sum(hh)/len(hh)),1)
    min_leg = min(hh)
    max_leg = max(hh)
    print("Barry Allen will travel ", round(gg,1), "miles on this trip.")
    print("He will go to the following cities: ", ee)
    print("The average leg of Barry's travels is", avg_leg, " miles.")
    print("The shortest leg of Barry's travels is", min_leg)
    print("The longest leg of Barry's travels is", max_leg)
    plot_tour(ee, ff)