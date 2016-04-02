from bokeh.io import output_file, show, vform
from bokeh.models import (
  GMapPlot, GMapOptions, ColumnDataSource, Circle, DataRange1d, PanTool, WheelZoomTool, BoxSelectTool, HBox
)
from bokeh.models.widgets import Slider
from geopy.geocoders import Nominatim
import csv

# Google Maps plot + options
map_options = GMapOptions(lat=15, lng=0, map_type="satellite", zoom=2)
plot = GMapPlot(
    x_range=DataRange1d(), y_range=DataRange1d(), map_options=map_options, title="Disease Over Time", plot_width=1000, plot_height=650
)

# Read in ebola data
rows = [];
with open('data/ebola.csv', newline='') as ebola_csv:
    ebola_reader = csv.reader(ebola_csv, delimiter=',', quotechar='|')
    for row in ebola_reader:
        rows.append(row)
countries = set([row[0] for row in rows])

# Find latitude and longitude of countries
geolocator = Nominatim();
locations = [geolocator.geocode(c) for c in countries]
lats = []
lons = []
for i in range(0, len(locations)):
    lats.append(locations[i].latitude)
    lons.append(locations[i].longitude)

# Data source
source = ColumnDataSource(
    data=dict(
        lat=lats,
        lon=lons
    )
)

# Add circles
circle = Circle(x="lon", y="lat", size=20, fill_color="blue", fill_alpha=0.8, line_color=None)
plot.add_glyph(source, circle)

# Add plot options
plot.add_tools(PanTool(), WheelZoomTool(), BoxSelectTool())
slider = HBox(Slider(start=2000, end=2016, value=2016, step=1, title="Year"), width=300)

# Output the plot and show it
output_file("disease_visual.html")
layout = vform(slider, plot)
show(layout)
