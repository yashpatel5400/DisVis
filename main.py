from bokeh.io import output_file, show, vform, hplot
from bokeh.models import (
  GMapPlot, GMapOptions, ColumnDataSource, Circle, DataRange1d, PanTool, WheelZoomTool, HoverTool, HBox, CustomJS
)
from bokeh.models.widgets import Slider
from bokeh.plotting import figure, show, output_file
from bokeh.document import Document

import csv, json
import os
import requests
import numpy as np
import pandas as pd

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

def make_legend(color_disease):
    output_file("legend.html")
    x = np.linspace(0, 4*np.pi, 100)
    y = np.sin(x)

    p = figure(width=275, height=275)
    for key in color_disease:
        p.circle(x, y, legend=key, 
            fill_color=color_disease[key], size=20, fill_alpha=0.35)
    p.legend.orientation = "bottom_left"

    p.axis.visible = None
    p.legend.glyph_height = 25
    p.legend.glyph_width = 100
    p.legend.legend_spacing = 10
    p.legend.legend_padding = 0

    p.logo = None
    p.toolbar_location = None

    return p

# Google Maps plot + options
styles = json.dumps([{"featureType":"all","elementType":"labels.text.fill","stylers":[{"color":"#ffffff"}]},{"featureType":"all","elementType":"labels.text.stroke","stylers":[{"color":"#000000"},{"lightness":13}]},{"featureType":"administrative","elementType":"geometry.fill","stylers":[{"color":"#000000"}]},{"featureType":"administrative","elementType":"geometry.stroke","stylers":[{"color":"#144b53"},{"lightness":14},{"weight":1.4}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#08304b"}]},{"featureType":"poi","elementType":"geometry","stylers":[{"color":"#0c4152"},{"lightness":5}]},{"featureType":"road.highway","elementType":"geometry.fill","stylers":[{"color":"#000000"}]},{"featureType":"road.highway","elementType":"geometry.stroke","stylers":[{"color":"#0b434f"},{"lightness":25}]},{"featureType":"road.arterial","elementType":"geometry.fill","stylers":[{"color":"#000000"}]},{"featureType":"road.arterial","elementType":"geometry.stroke","stylers":[{"color":"#0b3d51"},{"lightness":16}]},{"featureType":"road.local","elementType":"geometry","stylers":[{"color":"#000000"}]},{"featureType":"transit","elementType":"all","stylers":[{"color":"#146474"}]},{"featureType":"water","elementType":"all","stylers":[{"color":"#021019"}]}])
map_options = GMapOptions(lat=15, lng=0, map_type="roadmap",
    zoom=2, styles=styles)

# Read in disease data
color_disease = {
    "hiv": "red",
    "leprosy": "yellow",
    "malaria": "teal",
    "measles": "blue",
    "mumps": "pink",
    "tuberculosis": "purple"
}

p = make_legend(color_disease)

year = '2000'
plot = GMapPlot(
    x_range=DataRange1d(), y_range=DataRange1d(), map_options=map_options, 
    title="{} Infectious Spread".format(year), plot_width=900, plot_height=600, title_text_color={"value": "#ffffff"}, webgl=True
)
for disease in color_disease:
    print(disease)
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

    if year not in disease_data:
        continue

    # Data source
    if disease == 'hiv':
        disease = disease.upper()
    else:
        disease = disease.title()
    source = ColumnDataSource(data=dict(lat=lats, lon=lons, disease=disease,
        country=disease_data['countries'], diseaseData=disease_data, cases=disease_data[year]))

    # Add circles + hover
    hover = HoverTool(tooltips=[
        ("Disease", "@disease"),
        ("Country", "@country"),
        ("# of Cases", "@cases")
    ])

    cases = source.data['cases']
    diseaseData = source.data['diseaseData']
    lat = source.data['lat']
    lon = source.data['lon']
    country = source.data['country']
    disease = source.data['disease']

    source_df = pd.DataFrame(index=range(0, len(country)),columns=source.data.keys())
    source_df['cases'] = cases
    source_df['diseaseData'] = diseaseData[year]
    source_df['lat'] = lat
    source_df['lon'] = lon
    source_df['country'] = country
    source_df['disease'] = disease

    indices = list(source_df.index)
    for index in indices:
        CASE_SCALE = 500000
        cur_test = list(source_df[source_df.index == index]["cases"])[0]
        if type(cur_test).__module__ == np.__name__ or (len(cur_test) == 0):
            cases = 0
        else: cases = int(source_df[source_df.index == index]["cases"])
        circle = Circle(x="lon", y="lat", size=20 * cases/CASE_SCALE, 
            fill_color=color_disease[disease.lower()], fill_alpha=0.35, line_color=None)
        plot.add_glyph(ColumnDataSource(ColumnDataSource.from_df(
            source_df[source_df.index == index])), circle)

# Add plot options + slider
plot.add_tools(PanTool(), WheelZoomTool(), hover)
callback = CustomJS(args=dict(source=source), code="""
        var data = source.get('data');
        var year = cb_obj.get('value');
        data['cases'] = data['diseaseData'][year];
        source.trigger('change');
    """)
slider = HBox(Slider(start=2000, end=2016, value=2003, step=1, title="Year", callback=callback), width=300)

# Output the plot and show it
output_file("./visuals/disease_visual{}.html".format(year))
plot.logo = None
plot.toolbar_location = None

pl = hplot(plot, p)
show(pl)

doc = Document()
doc.add(pl)