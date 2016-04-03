from bokeh.io import output_file, show, vform
from bokeh.models import (
  GMapPlot, GMapOptions, ColumnDataSource, Circle, DataRange1d, PanTool, WheelZoomTool, HoverTool, HBox
)
from bokeh.models.widgets import Slider
from geopy.geocoders import Nominatim
import csv, json
import os
import requests

# Read in csv data
def readInData(csvString):
    dataDict = {}
    rows = []
    years = []
    with open(csvString, newline='') as csvFile:
        diseaseReader = csv.reader(csvFile, delimiter=',', quotechar='|')
        for row in diseaseReader:
            rows.append(row)

    countries = []
    for year in rows[0][1:]:
        years.append(year)
        dataDict[year] = {}
    for row in rows[1:]:
        country = row[0]
        countries.append(country)
        for i in range(0, len(row) - 1):
            dataDict[years[i]][country] = row[i+1]
        
    dataDict['countries'] = countries
    dataDict['years'] = years
    return dataDict

def write_cache(filename, array):
    cache = open(filename, 'w')
    writer = csv.writer(cache)
    for values in array:
        writer.writerow(values)
    cache.close()

def read_cache(filename):
    cache_return = []
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) != 0:
                cache_return.append(float("".join(row)))
    return cache_return

# Google Maps plot + options
styles = json.dumps([{"featureType":"all","elementType":"labels.text.fill","stylers":[{"color":"#ffffff"}]},{"featureType":"all","elementType":"labels.text.stroke","stylers":[{"color":"#000000"},{"lightness":13}]},{"featureType":"administrative","elementType":"geometry.fill","stylers":[{"color":"#000000"}]},{"featureType":"administrative","elementType":"geometry.stroke","stylers":[{"color":"#144b53"},{"lightness":14},{"weight":1.4}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#08304b"}]},{"featureType":"poi","elementType":"geometry","stylers":[{"color":"#0c4152"},{"lightness":5}]},{"featureType":"road.highway","elementType":"geometry.fill","stylers":[{"color":"#000000"}]},{"featureType":"road.highway","elementType":"geometry.stroke","stylers":[{"color":"#0b434f"},{"lightness":25}]},{"featureType":"road.arterial","elementType":"geometry.fill","stylers":[{"color":"#000000"}]},{"featureType":"road.arterial","elementType":"geometry.stroke","stylers":[{"color":"#0b3d51"},{"lightness":16}]},{"featureType":"road.local","elementType":"geometry","stylers":[{"color":"#000000"}]},{"featureType":"transit","elementType":"all","stylers":[{"color":"#146474"}]},{"featureType":"water","elementType":"all","stylers":[{"color":"#021019"}]}])
map_options = GMapOptions(lat=15, lng=0, map_type="roadmap", zoom=2, styles=styles)
plot = GMapPlot(
    x_range=DataRange1d(), y_range=DataRange1d(), map_options=map_options, title="", plot_width=1200, plot_height=600, title_text_color={"value": "#ffffff"}, title_text_font_size={"field": "0pt"}, toolbar_location=None, background_fill="black"
)

# Read in HIV data
hivData = readInData('data/hiv.csv')
print(hivData['countries'])
# print(hivData)

# Read in ebola data
# ebolaData = readInData('data/ebola.csv')
# rows = [];
# with open('data/ebola.csv', newline='') as ebola_csv:
#     ebola_reader = csv.reader(ebola_csv, delimiter=',', quotechar='|')
#     for row in ebola_reader:
#         rows.append(row)
# countries = set([row[0] for row in rows])

# Find latitude and longitude of countries
geolocator = Nominatim();
lats = []
lons = []

if not os.path.exists("./lats_cache.csv"):
    for c in hivData['countries']:
        r = requests.get("http://open.mapquestapi.com/nominatim/v1/search.php?key=5cMOU7Rg4xRCH27pndm8YalfVXG1Rc4P&format=json&q=" + c)
        if (len(r.json()) > 0):
            lats.append(r.json()[0]['lat'])
            lons.append(r.json()[0]['lon'])
        else:
            print(c) # this shouldn't occur, so fix it when it does
    write_cache("lats_cache.csv", lats)
    write_cache("lons_cache.csv", lons)
else:
    lats = read_cache("lats_cache.csv")
    lons = read_cache("lons_cache.csv")

# Data source
# the year should come from the slider
# the cases should come from the disease data
source = ColumnDataSource(data=dict(lat=lats, lon=lons, country=hivData['countries']))
# source = ColumnDataSource(data=dict(lat=lats, lon=lons, title="HIV", country="", year=2013, cases=hivData['2013']))

# Add circles + hover
hover = HoverTool(tooltips=[
    ("Country","@country")
])
# hover = HoverTool(tooltips=[
#     ("Disease","@title"),
#     ("Country", "@country"),
#     ("Year", "@year"),
#     ("# of Cases", "@cases")
# ])
circle = Circle(x="lon", y="lat", size=20, fill_color="red", fill_alpha=0.7, line_color=None)
plot.add_glyph(source, circle)

# for i in range(0, len(locations)):
#     # Data source
#     source = ColumnDataSource(data=dict(lat=[locations[i].latitude], lon=[locations[i].longitude]))

#     # Add circles
#     circle = Circle(x="lon", y="lat", size=20, fill_color="red", fill_alpha=0.7, line_color=None)
#     plot.add_glyph(source, circle)

# Add plot options
plot.add_tools(PanTool(), WheelZoomTool(), hover)
slider = HBox(Slider(start=2000, end=2016, value=2016, step=1, title="Year"), width=300)

# Output the plot and show it
output_file("disease_visual.html")
layout = vform(slider, plot)
show(layout)
