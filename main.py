import json
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

from locator import HerokuAppLocatorStrategy, geo_point_to_latitude_and_longitude

# --- Task 1
# The csv file contains data not only related to US states but also to Canadian regions!
df = pd.read_csv("event_data.csv")
assert len(df["id"]) == len(set(df["id"]))
locator_strategy = HerokuAppLocatorStrategy()
df["state"] = list(map(lambda x: locator_strategy.execute(*geo_point_to_latitude_and_longitude(x)), df["geo"]))
df.to_csv("event_data_extended.csv")

# --- Task 2 and 3
# data for the bar charts
df = pd.read_csv("event_data_extended.csv")
n_events_per_state = df.groupby(['state'])["eventValue"].count()
value_per_state = df.groupby(['state'])["eventValue"].sum()
n_events_per_state1 = n_events_per_state.iloc[:26]
n_events_per_state2 = n_events_per_state.iloc[26:]
value_per_state1 = value_per_state.iloc[:26]
value_per_state2 = value_per_state.iloc[26:]

# data for the map charts
us_states = json.load(open("gz_2010_us_040_00_500k.json", "r"))
state_id_map = {}
for feature in us_states["features"]:
    the_id = int(feature['properties']["STATE"])
    feature["id"] = the_id
    state_id_map[feature['properties']["NAME"]] = the_id
df_aggregate = pd.DataFrame(columns=["state", "Value", "Number of events", "id"])
for state in state_id_map.keys():
    if state not in n_events_per_state.index:
        value = 0
        number = 0
    else:
        value = float(value_per_state.loc[state])
        number = float(n_events_per_state.loc[state])
    df_aggregate = pd.concat([
        pd.DataFrame([[state, value, number, state_id_map[state]]], columns=df_aggregate.columns),
        df_aggregate], ignore_index=True)
df_aggregate_us_only = df_aggregate.copy()
df_aggregate_us_only = df_aggregate_us_only.drop(
    df_aggregate_us_only[df_aggregate_us_only["state"] == "Quebec"].index)
df_aggregate_us_only = df_aggregate_us_only.drop(
    df_aggregate_us_only[df_aggregate_us_only["state"] == "British Columbia"].index)
df_aggregate_us_only = df_aggregate_us_only.drop(
    df_aggregate_us_only[df_aggregate_us_only["state"] == "Ontario"].index)
df_aggregate_us_only = df_aggregate_us_only.drop(
    df_aggregate_us_only[df_aggregate_us_only["state"] == 'Manitoba'].index)
df_aggregate_us_only = df_aggregate_us_only.drop(
    df_aggregate_us_only[df_aggregate_us_only["state"] == 'Nova Scotia'].index)

# bar chart - number of events
fig, axes = plt.subplots(2, figsize=(12, 8))
fig.suptitle('Number of events per state')
axes[0].bar(n_events_per_state1.index, n_events_per_state1.values, width=.8, color="#2D96EE")
axes[1].bar(n_events_per_state2.index, n_events_per_state2.values, width=.8, color="#2D96EE")
for ind in [0, 1]:
    axes[ind].set_ylim([0, 300])
    for tick in axes[ind].get_xticklabels():
        tick.set_rotation(70)
    axes[ind].bar_label(axes[ind].containers[0])
fig.tight_layout()
fig.savefig("Number_of_events_per_state.png")
# The graph shows that there is a large discrepancy for the number of applications across states. 9 states contribute
# to more than 50%  of the applications: Florida, Texas, California, Ohio, North Carolina, Virginia, New Jersey,
# Massachusetts, Illinois.
# Only 3 "sates" did not submit any applications Puerto Rico, Vermont, and North Dakota.

# bar chart - total values
fig, axes = plt.subplots(2, figsize=(12, 8))
fig.suptitle('Sum of event values across states')
axes[0].bar(value_per_state1.index, value_per_state1.values, width=.8, color="#EE4F2D")
axes[1].bar(value_per_state2.index, value_per_state2.values, width=.8, color="#EE4F2D")
for ind in [0, 1]:
    axes[ind].set_ylim([0, 2100000])
    axes[ind].grid("on")
    for tick in axes[ind].get_xticklabels():
        tick.set_rotation(70)
    axes[ind].ticklabel_format(axis='y', style='plain')
fig.tight_layout()
fig.savefig("Sum_of_event_values_across_states.png")
# The graph shows that there is a large discrepancy for the total event values across states. 10 states contribute
# to more than 50%  of the applications: North Carolina, Illinois, Ohio, Massachusetts, California, Florida, Texas,
# New Jersey, Virginia and Maryland.

# map chart - number of events
fig = px.choropleth(
    df_aggregate_us_only,
    locations="id",
    geojson=us_states,
    color=df_aggregate_us_only["Number of events"].values,
    scope="usa",
    color_continuous_scale="Viridis",
    hover_name="state",
    hover_data=["Number of events"],
    labels={"color": "Number of events"},
)
fig.write_html("distribution_event_numbers.html")
# Canadian data was left aside because I used a map not accounting for Canada.
# The graph shows that there is a large discrepancy for the number of applications across states. The majority of the
# applications come from the Eastern USA, the West Coast (mostly California) and Texas.

# map chart - total values
fig = px.choropleth(
    df_aggregate_us_only,
    locations="id",
    geojson=us_states,
    color=df_aggregate_us_only["Value"].values,
    scope="usa",
    color_continuous_scale="Viridis",
    hover_name="state",
    hover_data=["Value"],
    labels={"color": "Total value"}
)
fig.show()
fig.write_html("distribution_sum_of_event_values.html")
# Canadian data was left aside because I used a map not accounting for Canada.
# The graph shows that there is a large discrepancy for the total event values across states. The majority of the
# event values come from the Eastern USA, the West Coast (mostly California) and Texas. It is interesting to see that
# states with the most applications do not exactly match being the states bringing the most value.

# --- Task 4
df = pd.read_csv("event_data_extended.csv")
df["created"] = df["created"].apply(lambda x: pd.Timestamp(x[:10]))
sorted_dates = sorted(df["created"].values)
all_dates = pd.date_range(sorted_dates[0], sorted_dates[-1], freq="D")
df_value = df.groupby(['created'])["eventValue"].sum()
df_number = df.groupby(['created'])["eventValue"].count()
df_freq = pd.DataFrame(index=all_dates, columns=["value", "number"])
for date in all_dates:
    if date in df_value.index:
        df_freq.loc[date]["value"] = df_value.loc[date]
        df_freq.loc[date]["number"] = df_number.loc[date]
    else:
        df_freq.loc[date]["value"] = 0
        df_freq.loc[date]["number"] = 0
df_freq['average_value'] = df_freq.loc[:, "value"].rolling(window=7, center=True).mean()
df_freq['average_number'] = df_freq.loc[:, "number"].rolling(window=7, center=True).mean()
reduced_dates = all_dates[3:-3]
df_freq = df_freq.loc[reduced_dates]

fig, axes = plt.subplots(2, 1, figsize=(12, 8))
axes[0].plot(df_freq.index, df_freq["average_number"], color="#2D96EE")
axes[0].set_title('7-day moving average of the number of events')
axes[1].plot(df_freq.index, df_freq["average_value"], color="#EE4F2D")
axes[1].set_title('7-day moving average of the summed event values')
axes[0].set_ylim([0, 90])
axes[1].set_ylim([0, 800000])
for ind in [0, 1]:
    axes[ind].grid("on")
fig.tight_layout()
fig.savefig("Moving_averages_of_event_values_and_numbers.png")

# The graphs show a rapid increase of job application volume in the  increase from the end of August 2022 to the end of
# October 2022 - x2.8 in just two months. The weekly applications values follow the same trend, with an absolute
# increase of a factor 3.3. Overall, the application volume and the value follow the same variations: rapid increase up
# to mid-September - then plateau until end of September - then rapid surge the first week of October - then plateau and
# finally dip until mid-October.
