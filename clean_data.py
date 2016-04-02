import pandas as pd
import numpy as np
import string
from math import floor

class Del:
	def __init__(self, keep=string.digits):
		self.comp = dict((ord(c),c) for c in keep)
	def __getitem__(self, k):
		return self.comp.get(k)

def easy_fix(name):
	df = pd.read_csv("{}.csv".format(name))
	columns = df.keys()

	for column in columns:
		df[column] = df[column].fillna(0)

	df.to_csv("{}_fixed.csv".format(name))

def clean_ebola():
	filename = "ebola.csv"
	df = pd.read_csv(filename)
	df["Split_Word"] = df.apply(
		lambda row : set(row["Indicator"].lower().split()), axis=1)
	df = df.drop(["Indicator"], axis=1)

	indices = df.index
	keep_indices = []
	DROP_WORDS = set(["probable", "suspected", "deaths", "21", "rate"])

	for index in indices:
		cur_row = set(list(df[df.index == index]["Split_Word"])[0])
		intersect = cur_row.intersection(DROP_WORDS)
		if len(intersect) == 0:
			keep_indices.append(index)

	df = df.loc[keep_indices]
	df = df.drop(["Split_Word"], axis=1)

	countries = df["Country"].unique()
	df = df.reindex(df["Date"].sort_values().index)
	df = df.reset_index(drop=True)

	total_change = np.zeros(len(df))
	for country in countries:
		cur_country = df[df["Country"] == country]
		country_indices = cur_country.index
		ebola_change = [df["value"][country_indices[0]]] + [max(0, (df["value"][country_indices[i]] 
			- df["value"][country_indices[i - 1]])) 
			for i in range(1, len(country_indices))]
		for i in range(0, len(country_indices)):
			total_change[country_indices[i]] = ebola_change[i]

	df["Ebola_Change"] = total_change
	df = df.drop(["value"], axis=1)
	df.to_csv("ebola_fixed.csv")

def clean_hiv_cases():
	DD = Del()

	filename = "hiv_cases.csv"
	df = pd.read_csv(filename)
	years = df.keys()[1:]

	for year in years:
		new_year = "new_{}".format(year)
		df[year] = df[year].astype(str)
		df[new_year] = df.apply(
			lambda row : row[year].split('[')[0].translate(DD), axis=1)
		replace_indices = df[df[new_year] == ''].index
		for index in replace_indices:
			df[new_year] = df[new_year].set_value(index, 0)

	df = df.drop(list(years), axis=1)
	df.to_csv("hiv_fixed.csv")

def clean_leprosy():
	filename = "leprosy.csv"
	df = pd.read_csv(filename)
	columns = df.keys()

	for column in columns:
		indices = df[df[column] == "No data"][column].index
		for index in indices:
			df[column] = df[column].set_value(index, 0)

	df.to_csv("leprosy_fixed.csv")

def clean_malaria():
	filename = "malaria.csv"
	df = pd.read_csv(filename)
	columns = df.keys()[1:]

	for column in columns:
		df[column] = df[column].fillna(0)
		df[column] = df[column].astype(str)
		df[column] = df.apply(lambda row : 
			int(row[column].replace(" ", "")), axis=1)

	df.to_csv("malaria_fixed.csv")

def clean_measles():
	easy_fix("measles")

def clean_mumps():
	easy_fix("mumps")

def clean_tuberculosis():
	filename = "tuberculosis.csv"
	df = pd.read_csv(filename)
	columns = df.keys()[2:]

	for column in columns:
	df[column] = df[column].fillna(0)
		df[column] = df[column].astype(str)
		df[column] = df.apply(lambda row : 
			floor(float(row[column].split('[')[0].replace(" ", ""))), axis=1)

	df.to_csv("tuberculosis_fixed.csv")

def main():
	clean_ebola()
	clean_hiv_cases()
	clean_leprosy()
	clean_malaria()
	clean_measles()
	clean_mumps()
	clean_tuberculosis()

if __name__ == "__main__":
	main()