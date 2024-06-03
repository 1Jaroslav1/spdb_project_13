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


def calculate_cumulative_distances(points):
    distances = [0]
    for i in range(1, len(points)):
        # Calculate geodesic distance between points[i-1] and points[i]
        distance = geodesic(points[i-1], points[i]).km
        distances.append(distances[-1] + distance)
    return distances


def interpolate_points(points, num_points=100):
    lons = [point[0] for point in points]
    lats = [point[1] for point in points]

    # Calculate cumulative distances and convert to normalized t values
    distances = calculate_cumulative_distances(points)
    t = np.array(distances) / distances[-1]  # Normalize distances into t values

    # Create cubic spline interpolations for longitude and latitude
    cs_lon = CubicSpline(t, lons)
    cs_lat = CubicSpline(t, lats)

    t_new = np.linspace(0, 1, num_points)

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

            inter_lon, inter_lat = interpolate_points([dep_coords, cur_coords, arr_coords])

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

        fig.update_geos(
            scope="europe",
        )
        fig.update_layout(
            title='Real-Time Flight Positions',
            geo=dict(
                showland=True,
                landcolor="rgb(243, 243, 243)",
                showcountries=True,
                countrycolor="Black"
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
            if airport and airport["success"]:
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
