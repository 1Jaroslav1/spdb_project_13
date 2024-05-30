from api import API
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from dotenv import load_dotenv
from geopy.distance import geodesic
import numpy as np
from utils import read_airport_codes, save_file
from scipy.interpolate import CubicSpline
import pandas as pd
import plotly.graph_objects as go
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
DEPLATA = "BHX"
LIMIT = 20

api = API(API_KEY)
airports_filepath = 'cache_cities.json'

app = Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='dynamic-graph'),
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # 1 minute
        n_intervals=0
    )
])

# def update_map(df):
#     if not df.empty:
#         fig = go.Figure(data=go.Scattergeo(
#             lon=df['geography.longitude'],
#             lat=df['geography.latitude'],
#             text=df['flight.iataNumber'],
#             marker=dict(
#                 size=10,
#                 color='blue',
#                 line_color='rgb(40,40,40)',
#                 line_width=0.5,
#                 sizemode='diameter'
#             )
#         ))
#         fig.update_geos(
#             visible=True,
#             projection_type="orthographic",
#             scope="europe",
#             showcountries=True,
#             countrycolor="Black",
#             showsubunits=True, subunitcolor="Blue",
#             showland=True,
#             landcolor="rgb(243, 243, 243)",
#         )
#         fig.update_layout(
#             title='Real-Time Flight Positions',
#             margin={"r": 0, "t": 0, "l": 0, "b": 0}
#         )
#
#         fig.show()

# def update_map(df, known_airports):
#     if not df.empty:
#         # Prepare lists for departure and arrival coordinates
#         dep_lons, dep_lats, arr_lons, arr_lats = [], [], [], []
#         for index, row in df.iterrows():
#             dep_airport = known_airports.get(row['departure.iataCode'])
#             arr_airport = known_airports.get(row['arrival.iataCode'])
#             if dep_airport:
#                 dep_lons.append(dep_airport['longitudeAirport'])
#                 dep_lats.append(dep_airport['latitudeAirport'])
#             if arr_airport:
#                 arr_lons.append(arr_airport['longitudeAirport'])
#                 arr_lats.append(arr_airport['latitudeAirport'])
#
#         # Plot current flight positions
#         fig = go.Figure(data=go.Scattergeo(
#             lon=df['geography.longitude'],
#             lat=df['geography.latitude'],
#             text=df['flight.iataNumber'],
#             mode='markers',
#             marker=dict(
#                 size=7,
#                 color='red',
#                 symbol='circle'
#             )
#         ))
#
#         # Add departure and arrival points to the map
#         if dep_lons and dep_lats:
#             fig.add_trace(go.Scattergeo(
#                 lon=dep_lons,
#                 lat=dep_lats,
#                 mode='markers',
#                 marker=dict(
#                     size=5,
#                     color='green',
#                     symbol='triangle-up'
#                 ),
#                 name='Departure'
#             ))
#
        # if arr_lons and arr_lats:
        #     fig.add_trace(go.Scattergeo(
        #         lon=arr_lons,
        #         lat=arr_lats,
        #         mode='markers',
        #         marker=dict(
        #             size=5,
        #             color='blue',
        #             symbol='triangle-down'
        #         ),
        #         name='Arrival'
        #     ))
#
#         fig.update_geos(
#             projection_type="natural earth"
#         )
#         fig.update_layout(
#             title='Real-Time Flight Positions',
#             geo=dict(
#                 showcountries=True,
#                 countrycolor="Black"
#             ),
#             margin={"r": 0, "t": 0, "l": 0, "b": 0}
#         )
#         fig.show()


# def update_map(df, known_airports):
#     if not df.empty:
#         fig = go.Figure()
#
#         # Loop through each flight to add markers and lines
#         for index, row in df.iterrows():
#             # Fetch the airport data for departure and arrival
#             dep_airport = known_airports.get(row['departure.iataCode'])
#             arr_airport = known_airports.get(row['arrival.iataCode'])
#             current_lon, current_lat = row['geography.longitude'], row['geography.latitude']
#
#             # Check if airport data is available to plot the lines
#             if dep_airport and arr_airport:
#                 # Add lines from departure to current flight position to arrival
#                 fig.add_trace(go.Scattergeo(
#                     lon=[dep_airport['longitudeAirport'], current_lon, arr_airport['longitudeAirport']],
#                     lat=[dep_airport['latitudeAirport'], current_lat, arr_airport['latitudeAirport']],
#                     mode="lines+markers",
#                     line=dict(width=1, color='blue', dash="dot"),
#                     marker=dict(
#                         size=5,
#                         color='blue',
#                         symbol='triangle-down'
#                     ),
#                     opacity=0.6
#                 ))
#
#             # Add markers for current position
#             fig.add_trace(go.Scattergeo(
#                 lon=[current_lon],
#                 lat=[current_lat],
#                 text=row['flight.iataNumber'],
#                 mode='markers',
#                 marker=dict(
#                     size=7,
#                     color='red',
#                     symbol='circle'
#                 )
#             ))
#
#         # Set geo and layout properties
#         fig.update_geos(
#             projection_type="natural earth",
#             showcountries=True,
#             countrycolor="Black"
#         )
#         fig.update_layout(
#             title='Real-Time Flight Positions',
#             geo=dict(
#                 showland=True,
#                 landcolor="rgb(243, 243, 243)"
#             ),
#             margin={"r": 0, "t": 0, "l": 0, "b": 0}
#         )
#
#         # Display the figure
#         fig.show()

def calculate_cumulative_distances(points):
    distances = [0]  # Start with 0 for the first point
    for i in range(1, len(points)):
        # Calculate geodesic distance between points[i-1] and points[i]
        distance = geodesic(points[i-1], points[i]).km
        distances.append(distances[-1] + distance)  # Add to cumulative total
    return distances


def interpolate_points(points, num_points=100):
    # Extract longitude and latitude from the points
    lons = [point[0] for point in points]
    lats = [point[1] for point in points]

    # Calculate cumulative distances and convert to normalized t values
    distances = calculate_cumulative_distances(points)
    t = np.array(distances) / distances[-1]  # Normalize distances into t values

    # Create cubic spline interpolations for longitude and latitude
    cs_lon = CubicSpline(t, lons)
    cs_lat = CubicSpline(t, lats)

    # Generate t values for the interpolated points
    t_new = np.linspace(0, 1, num_points)

    # Interpolate points using the cubic spline
    interpolated_lons = cs_lon(t_new)
    interpolated_lats = cs_lat(t_new)

    return interpolated_lons, interpolated_lats


def update_map(df, known_airports):
    fig = go.Figure()
    if not df.empty:
        for index, row in df.iterrows():
            dep_airport = known_airports.get(row['departure.iataCode'])
            dep_lon, dep_lat = dep_airport['longitudeAirport'], dep_airport['latitudeAirport']
            arr_airport = known_airports.get(row['arrival.iataCode'])
            arr_lon, arr_lat = arr_airport['longitudeAirport'], arr_airport['latitudeAirport']
            current_lon, current_lat = row['geography.longitude'], row['geography.latitude']

            dep_coords = (dep_lon, dep_lat)
            cur_coords = (current_lon, current_lat)
            arr_coords = (arr_lon, arr_lat)

            # Generate interpolated points along the curve
            inter_lon, inter_lat = interpolate_points([dep_coords, cur_coords, arr_coords])

            # Plot the flight path
            fig.add_trace(go.Scattergeo(
                lon=inter_lon,
                lat=inter_lat,
                text=f"Flight: {dep_airport['nameCountry']}->{arr_airport['nameCountry']}<br>Airline: {row['airline.iataCode']}",
                mode="lines",
                line=dict(width=1, color='blue', dash="dot"),
                opacity=0.6,
                name=f"{dep_airport['nameCountry']}->{arr_airport['nameCountry']}"
            ))

            fig.add_trace(go.Scattergeo(
                lon=[arr_lon],
                lat=[arr_lat],
                text=f"Iata code: {arr_airport['codeIataAirport']}<br>Airport Name: {arr_airport['nameAirport']}<br>Country: {arr_airport['nameCountry']}<br>Phone: {arr_airport['phone']}",
                mode='markers',
                marker=dict(
                    size=5,
                    color='blue',
                    symbol='triangle-down'
                ),
                name=f"{arr_airport['nameAirport']}|{arr_airport['nameCountry']}"
            ))

            fig.add_trace(go.Scattergeo(
                lon=[dep_lon],
                lat=[dep_lat],
                text=f"Iata code: {dep_airport['codeIataAirport']}<br>Airport Name: {dep_airport['nameAirport']}<br>Country: {dep_airport['nameCountry']}<br>Phone: {dep_airport['phone']}",
                mode='markers',
                marker=dict(
                    size=5,
                    color='green',
                    symbol='triangle-up'
                ),
                name=f"{dep_airport['nameAirport']}|{dep_airport['nameCountry']}"
            ))

            fig.add_trace(go.Scattergeo(
                lon=[current_lon],
                lat=[current_lat],
                text=row['flight.iataNumber'],
                mode='markers',
                marker=dict(
                    size=5,
                    color='red',
                    symbol='circle'
                ),
                name=row['flight.iataNumber']
            ))

        # Set map and layout properties
        fig.update_geos(
            scope="europe",
        )
        fig.update_layout(
            title='Real-Time Flight Positions',
            geo=dict(
                showland=True,
                landcolor="rgb(243, 243, 243)"
            ),
            margin={"r": 0, "t": 0, "l": 0, "b": 0}
        )

    return fig


def get_data(api, airports_filepath):
    known_airports = read_airport_codes(airports_filepath)
    flights = api.fetch_flight_data(DEPLATA, LIMIT)

    for flight in flights:
        if flight['departure']['iataCode'] not in known_airports:
            print(flight['departure']['iataCode'])
            airport = api.get_airport_details(flight['departure']['iataCode'])
            print(airport)
            if airport["success"]:
                data = airport["data"]
                known_airports[data["codeIataAirport"]] = data
            else:
                flights.remove(flight)
        if flight['arrival']['iataCode'] not in known_airports:
            print(flight['arrival']['iataCode'])
            airport = api.get_airport_details(flight['arrival']['iataCode'])
            print(airport)
            if airport["success"]:
                data = airport["data"]
                known_airports[data["codeIataAirport"]] = data
            else:
                flights.remove(flight)

    save_file(airports_filepath, known_airports)

    df = pd.json_normalize(flights)

    return df, known_airports


@app.callback(
    Output('dynamic-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def main(n):
    df, known_airports = get_data(api, airports_filepath)
    return update_map(df, known_airports)


if __name__ == "__main__":
    app.run_server(debug=True)
