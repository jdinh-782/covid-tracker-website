from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
import csv
from datetime import datetime


# data from 1/22/20 -> 5/2/2021
df = pd.read_csv("time_series_covid_19_confirmed_US.csv")
df = pd.DataFrame(df)

# cleaning data (keep only what is needed for purposes)
df = df.drop(['UID', 'Country_Region', 'iso2', 'iso3', 'code3', 'Lat', 'Long_', 'FIPS'], axis=1)

# renaming "Admin2" to "County" for easier referencing
df = df.rename(columns={"Admin2": "County"})
print(df)

# grab a county
counties = df.loc[df['Province_State'] == 'California']
print(f"\n\nCalifornia Counties\n{counties}")

# picking a specific county (Los Angeles County)
county = counties.iloc[29]  # Los Angeles index is 18
county_dict = pd.Series.to_dict(county)
county_dict = dict(county_dict)

county_location = county_dict['Combined_Key']

key_list = ['County', 'Province_State', 'Combined_Key']
[county_dict.pop(key) for key in key_list]

# clean data to create csv file for only the dates and cases of the county
print(f"\n")

dates = list(county_dict.keys())
cases = list(county_dict.values())

new_date_list = []

for i in range(0, len(dates)):
    year = ""
    month = ""
    day = ""
    counter = 0

    for c in dates[i]:
        if c == '/':
            counter += 1
        if counter == 0:
            month += c
        elif counter == 1 and c != '/':
            day += c
        elif counter == 2 and c != '/':
            year += c

    if year == '20':
        year = "2020"
    elif year == '21':
        year = "2021"

    # indicates month is just 1 digit without a leading 0
    if len(month) == 1:
        month = '0' + month

    new_date = f"{year}-{month}-{day}"

    new_date_list.append(new_date)
    # print(new_date)

# print(new_date_list)


# write to new csv file with data for specified county
with open("cases_by_date.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Date", "Number of Cases"])

    index = 0

    for i in range(0, len(new_date_list)):
        writer.writerow([new_date_list[i], cases[i]])


# visualize data into a graph using matplotlib
county_df = pd.read_csv("cases_by_date.csv", index_col="Date", parse_dates=True)
county_df = pd.DataFrame(county_df)
print(f"Total Cases for {county_location}")
print(county_df)

fig, ax = plt.subplots()

fig.set_figwidth(16)
fig.set_figheight(12)

plt.plot(county_df.index, county_df['Number of Cases'], marker='|', color='#4287f5', label="COVID-19 Cases Per Day")
plt.plot([], [], marker='*', color='black', label="Total COVID-19 Cases")

plt.title(f"Total COVID-19 Cases in {county_location} (1/2020-5/2021)", fontsize=18, weight='bold')

plt.xlabel("Year-Month", fontsize=18, weight='bold')
plt.ylabel("Cases", fontsize=18, weight='bold')

plt.ticklabel_format(axis="y", style="plain")
plt.xticks(fontsize=14)
plt.yticks(fontsize=20)

plot_dates = ['2020-03-01', '2020-05-01', '2020-07-01', '2020-09-01', '2020-11-01', '2021-01-01', '2021-03-01']
dates = [datetime.strptime(x, '%Y-%m-%d') for x in plot_dates]

for i in range(0, len(plot_dates)):
    num_of_cases = county_df.loc[plot_dates[i]][0]
    plt.annotate(f"*{plot_dates[i]}: {num_of_cases}", (dates[i], num_of_cases), textcoords="offset points",
                 xytext=(0, 10), ha='center', weight='bold', fontsize=14, wrap=True)

plt.grid()
plt.legend(loc="upper left", fancybox=True, shadow=True, borderpad=1, framealpha=1, prop={'size': 22})

# fig.show()
fig.savefig(f"total_cases_line_plot_{county_location}.png")

# calculate averages of new cases per day
averages_dict = dict()

for i in range(1, len(new_date_list)):
    average_cases = abs(int(cases[i]) - int(cases[i - 1]))
    averages_dict[new_date_list[i]] = average_cases

averages_df = pd.DataFrame(averages_dict.items())
print(f"\n\nAverage Cases for {county_location}")
print(averages_df)

# create graph of average cases
fig, ax = plt.subplots()

fig.set_figwidth(24)
fig.set_figheight(10)

plt.plot(averages_df.index, averages_df[1], marker='|', color='#4287f5', label="New COVID-19 Cases Per Day")
plt.plot([], [], marker='*', color='black', label="Total New COVID-19 Cases")

plt.title(f"New COVID-19 Cases Per Day in {county_location} (1/2020-5/2021)", fontsize=18, weight='bold')

positions = (0, 144, 223, 300, 343, 378, 454)
x_labels = ('2020-01-23', '2020-06-15', '2020-09-01', '2020-11-18', '2021-01-01', '2021-02-04', '2021-04-21')
plt.xticks(positions, x_labels, fontsize=14)
plt.yticks(fontsize=20)

plt.xlabel("Date", fontsize=18, weight='bold')
plt.ylabel("Cases", fontsize=18, weight='bold')

x_labels = ('2020-01-23', '2020-06-15', '2020-09-1', '2020-11-18', '2021-01-1', '2021-02-4', '2021-04-21')
for i in range(0, len(x_labels)):
    plt.text(x=positions[i], y=averages_dict.get(x_labels[i]), s=f"*{averages_dict.get(x_labels[i])}", fontsize=20)

plt.grid()
plt.legend(loc="upper left", fancybox=True, shadow=True, borderpad=1, framealpha=1, prop={'size': 22})

# fig.show()
fig.savefig(f"average_cases_line_plot_{county_location}.png")


# if __name__ == "__main__":
#     # flask process
#     app = Flask(__name__)
#     app.debug = True
#
#     @app.route('/')
#     def index():
#         return render_template("index.html")
#
#     app.run()
