from bokeh.io import output_file, show, vform
from bokeh.models import (
  GMapPlot, GMapOptions, ColumnDataSource, Circle, DataRange1d, PanTool, WheelZoomTool, HoverTool, HBox, CustomJS
)
from bokeh.models.widgets import Slider
import csv, json
import os
import requests

# Read in csv data
def readInData(csvString):
    # dataDict is a dictionary that stores: {'countries': '...', 'years': '...', '2016': {'U.S.A.': 2000}, ...}
    dataDict = {}
    rows = []
    years = [str(i) for i in range(2000, 2017)]
    with open(csvString, newline='') as csvFile:
        diseaseReader = csv.reader(csvFile, delimiter=',', quotechar='|')
        for row in diseaseReader:
            rows.append(row)

    countries = []
    for year in years:
        dataDict[year] = []
    for row in rows[1:]:
        country = row[0]
        countries.append(country)
        for year in range(2000, 2017):
            if (rows[0].count(str(year)) > 0):
                i = rows[0].index(str(year))
                dataDict[str(year)].append(row[i])
            else:
                dataDict[str(year)].append(0)
        
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
map_options = GMapOptions(lat=15, lng=0, map_type="roadmap",
    zoom=2, styles=styles)
plot = GMapPlot(
    x_range=DataRange1d(), y_range=DataRange1d(), map_options=map_options, 
    title="", plot_width=1200, plot_height=600, title_text_color={"value": "#ffffff"}
)

# Read in HIV data
color_disease = {
    "hiv": "red",
    "leprosy": "yellow",
    "malaria": "teal",
    #"measles": "blue",
    "mumps": "pink",
    #"tuberculosis": "purple"
}

for disease in color_disease:
    disease_data = readInData('./data/{}.csv'.format(disease))

    # Find latitude and longitude of countries
    lats = []
    lons = []
    if not os.path.exists("./{}_lats_cache.csv".format(disease)):
        for c in disease_data['countries']:
            r = requests.get("http://open.mapquestapi.com/nominatim/v1/search.php?key=5cMOU7Rg4xRCH27pndm8YalfVXG1Rc4P&format=json&q=" + c)
            if (len(r.json()) > 0):
                lats.append(r.json()[0]['lat'])
                lons.append(r.json()[0]['lon'])
            else:
                print(c) # this shouldn't occur, so fix it when it does
        write_cache("./{}_lats_cache.csv".format(disease), lats)
        write_cache("./{}_lons_cache.csv".format(disease), lons)
    else:
        lats = read_cache("./{}_lats_cache.csv".format(disease))
        lons = read_cache("./{}_lons_cache.csv".format(disease))

    # Data source
    # the year should come from the slider
    # the cases should come from the disease data
    source = ColumnDataSource(data=dict(lat=lats, lon=lons, 
        country=disease_data['countries']))
    # source = ColumnDataSource(data=dict(lat=lats, lon=lons, title="HIV", country="", year=2013, cases=disease_data['2013']))

    # Add circles + hover
    hover = HoverTool(tooltips=[
        ("Country", "@country"),
        ("# of Cases", "@cases")
    ])
    circle = Circle(x="lon", y="lat", size=20, 
        fill_color=color_disease[disease], fill_alpha=0.25, line_color=None)
    plot.add_glyph(source, circle)

# for i in range(0, len(locations)):
#     # Data source
#     source = ColumnDataSource(data=dict(lat=[locations[i].latitude], lon=[locations[i].longitude]))

#     # Add circles
#     circle = Circle(x="lon", y="lat", size=20, fill_color="red", fill_alpha=0.7, line_color=None)
#     plot.add_glyph(source, circle)

# def update(attrname, old, new):
#     source.data.cases = hivData[str(new)]
#     print(attrname, old, new)

# Add plot options + slider
plot.add_tools(PanTool(), WheelZoomTool(), hover)
# callback = CustomJS(args=dict(source=source), code="""
#         var data = source.get('data');
#         var year = cb_obj.get('value');
slider = HBox(Slider(start=2000, end=2016, value=2013, step=1, title="Year"), width=300)

# Output the plot and show it
output_file("disease_visual.html")
layout = vform(plot, slider)
show(layout)
