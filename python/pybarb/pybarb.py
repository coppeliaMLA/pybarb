import requests
import json
import pandas as pd
import numpy as np
import sqlalchemy
import plotly.graph_objs as go


class BarbAPI:
    """
    A class for connecting to the Barb API and making queries.

    Attributes:
        api_key (str): The API key for accessing the Barb API.
        connected (bool): Whether the API is currently connected.

    Methods:
        connect: Connect to the Barb API.
        query: Make a query to the Barb API.
    """

    def __init__(self, api_key: str):
        """
        Initializes a new instance of the BarbAPI class.

        Args:
            api_key (str): The API key for accessing the Barb API.
        """
        self.api_key = api_key
        self.api_root = "https://barb-api.co.uk/api/v1/"
        self.connected = False
        self.headers = None

    def connect(self):
        """
        Connects to the Barb API.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        # Code to connect to the Barb API
        self.connected = True

        # Code to get an access token from the Barb API
        token_request_url = self.api_root + "auth/token/"
        response = requests.post(token_request_url, data=self.api_key)
        access_token = json.loads(response.text)['access']
        self.headers = {'Authorization': 'Bearer {}'.format(access_token)}

    def get_station_code(self, station_name):
        api_url = f"{self.api_root}stations/"
        r = requests.get(url=api_url, headers=self.headers)
        api_data = r.json()
        station_code = [s["station_code"]
                        for s in api_data if station_name.lower() == s['station_name'].lower()]
        if len(station_code) == 1:
            station_code = station_code[0]
        else:
            raise Exception(f"Station name {station_name} not found.")
        return station_code

    def get_panel_code(self, panel_region):
        api_url = f"{self.api_root}panels/"
        r = requests.get(url=api_url, headers=self.headers)
        api_data = r.json()
        panel_code = [s["panel_code"]
                      for s in api_data if panel_region.lower() == s['panel_region'].lower()]
        if len(panel_code) == 1:
            panel_code = panel_code[0]
        else:
            raise Exception(f"Panel name {panel_region} not found.")
        return panel_code

    def programme_ratings(self, min_transmission_date, max_transmission_date, station=None, panel=None, consolidated=True, last_updated_greater_than=None, use_reporting_days=True, limit=5000):
        """
        Gets the programme ratings for a given date range.

            Args:
                min_transmission_date (str): The start date for the query. Format: YYYY-MM-DD
                max_transmission_date (str): The end date for the query. Format: YYYY-MM-DD
                station (str): The name of the station to query. If None, all stations are queried.
                panel (str): The name of the panel to query. If None, all panels are queried.
                consolidated (bool): Whether to return consolidated data.
                limit (int): The maximum number of results to return. Default is 5000.

            Returns:
                BarbAPI: The BarbAPI object.
        """

        # The query parameters
        params = {"min_transmission_date": min_transmission_date, "max_transmission_date": max_transmission_date,
                  "station_code": self.get_station_code(station), "panel_code": self.get_panel_code(panel), "consolidated": consolidated, "last_updated_greater_than": last_updated_greater_than, "use_reporting_days": use_reporting_days, "limit": limit}

        api_response_data = self.query_event_endpoint(
            "programme_ratings", params)

        return ProgrammeRatingsResultSet(api_response_data)

    def advertising_spots(self, min_transmission_date, max_transmission_date, station=None, panel=None, advertiser=None,
                          buyer=None, consolidated=True, standardise_audiences=None, use_reporting_days=True,
                          last_updated_greater_than=None, limit=5000):

        # The query parameters
        params = {"min_transmission_date": min_transmission_date, "max_transmission_date": max_transmission_date,
                  "station_code": self.get_station_code(station), "panel_code": self.get_panel_code(panel),
                  "advertiser": advertiser, "buyer": buyer, "consolidated": consolidated,
                  "standardise_audiences": standardise_audiences, "use_reporting_days": use_reporting_days, "last_updated_greater_than": last_updated_greater_than,
                  "limit": limit}

        api_response_data = self.query_event_endpoint(
            "advertising_spots", params)

        return AdvertisingSpotsResultSet(api_response_data)

    def audiences_by_time(self, min_transmission_date, max_transmission_date, time_period_length, viewing_status, station=None, panel=None,
                          use_polling_days=True, last_updated_greater_than=None, limit=5000):

        # The query parameters
        params = {"min_transmission_date": min_transmission_date, "max_transmission_date": max_transmission_date,
                  "station_code": self.get_station_code(station), "panel_code": self.get_panel_code(panel),
                  "time_period_length": time_period_length, "viewing_status": viewing_status,
                  "use_polling_days": use_polling_days, "last_updated_greater_than": last_updated_greater_than,
                  "limit": limit}

        api_response_data = self.query_event_endpoint(
            "audiences_by_time", params)

        return AudiencesByTimeResultSet(api_response_data)

    def query_event_endpoint(self, endpoint, parameters):
        api_url = f"{self.api_root}{endpoint}"
        r = requests.get(url=api_url, params=parameters, headers=self.headers)
        r_json = r.json()
        api_response_data = {"endpoint": "programme_ratings",
                             "events": r_json["events"],
                             "audience_categories": r_json["audience_categories"]}
        while r.headers.__contains__("X-Next"):
            x_next_url = r.headers["X-Next"]
            r = requests.get(url=x_next_url, headers=self.headers)
            r_json = r.json()
            api_response_data["events"].append(r_json["events"])
            api_response_data["audience_categories"].append(
                r_json["audience_categories"])

        return api_response_data


class APIResultSet:

    def __init__(self, api_response_data: dict):
        """
        Initializes a new instance of the BarbAPI class.

        Args:
            api_key (str): The API key for accessing the Barb API.
        """

        self.api_response_data = api_response_data

    def to_dataframe(self):
        """
        Converts the API response data into a pandas dataframe.

        Returns:
            pandas.DataFrame: A dataframe containing the API response data.

        """
        raise NotImplementedError()
    
    def ts_plot(self):
        """
        Converts the API response data into a pandas dataframe.

        Returns:
            pandas.DataFrame: A dataframe containing the API response data.

        """
        raise NotImplementedError()

    def to_csv(self, file_name):
        self.to_dataframe().to_csv(file_name, index=False)

    def to_excel(self, file_name):
        self.to_dataframe().to_excel(file_name, index=False)

    def to_json(self, file_name):
        with open(file_name, 'w') as f:
            json.dump(self.api_response_data, f)

    def to_sql(self, connection_string, table_name):
        df = self.to_dataframe()
        engine = sqlalchemy.create_engine(connection_string)
        df.to_sql(table_name, engine, if_exists='replace', index=False)

    def audience_pivot(self):
        df = self.to_dataframe()
        entity = 'programme_name' if 'programme_name' in df.columns else 'clearcast_commercial_title' if 'clearcast_commercial_title' in df.columns else 'activity'
        df = pd.pivot_table(df, index=['panel_region', 'station_name', 'date_of_transmission', entity], columns='audience_name', values='audience_size_hundreds', aggfunc=np.sum).fillna(0)
        return df
    
    def ts_plot(self):
        df = self.audience_pivot().reset_index()
        traces = []
        for i, col in enumerate(df.columns[4:]):
            # set the visible attribute to False for all traces except the first one
            visible = i == 0
            traces.append(go.Scatter(x=df['date_of_transmission'], y=df[col], name=col, visible=visible))


        # create the layout for the chart
        layout = go.Layout(title='Audience by time',
                        xaxis=dict(title='Date'),
                        yaxis=dict(title='Value'),
                        showlegend=False,
                        updatemenus=[dict(
                            buttons=[{'label': col, 'method': 'update', 'args': [{'visible': [col == trace.name for trace in traces]}]} for col in df.columns[4:]],
                            direction='down',
                            #showactive=True
                        )])

        # create the figure with the traces and layout
        fig = go.Figure(data=traces, layout=layout)

        # display the chart
        return fig



class ProgrammeRatingsResultSet(APIResultSet):

    def to_dataframe(self, pivot_audiences=True):
        """
        Converts the API response data into a pandas dataframe.

        Returns:
            pandas.DataFrame: A dataframe containing the API response data.

        """

        # Loop through the events and then the audiences within the events
        df = []
        for e in self.api_response_data['events']:
            prog_name = e['programme_content']['content_name'] if 'programme_content' == "None" else e['transmission_log_programme_name'].title()
            for v in e['audience_views']:
                df.append({'panel_region': e['panel']['panel_region'],
                           'station_name': e['station']['station_name'],
                           'programme_name': prog_name,
                           'programme_type': e['programme_type'],
                           'programme_start_datetime': e['programme_start_datetime']['standard_datetime'],
                           'programme_duration_minutes': e['programme_duration'],
                           'spans_normal_day': e['spans_normal_day'],
                           'uk_premiere': e['uk_premier'],
                           'broadcaster_premiere': e['broadcaster_premier'],
                           'programme_repeat': e['repeat'],
                           'episode_number': e['episode']['episode_number'] if 'episode' in e else None,
                           'episode_name': e['episode']['episode_name'] if 'episode' in e else None,
                           'genre': e['genre'] if 'genre' in e else None,
                           'platforms': ", ".join(e['platforms']),
                           'audience_code': v['audience_code'],
                           'audience_size_hundreds': v['audience_size_hundreds']})
        # Convert the result into a data frame
        df = pd.DataFrame(df)

        # Format the transmission_time_period as a pandas datetime
        df['programme_start_datetime'] = pd.to_datetime(
            df['programme_start_datetime'])
        df['date_of_transmission'] = df['programme_start_datetime'].dt.date

        # Add the audience category names. We have a temporary problem with duplicates in this data set hence the dropping of duplicates.
        audience_categories_df = pd.DataFrame(
            self.api_response_data['audience_categories']).drop_duplicates(subset=['audience_code'])
        df = df.merge(audience_categories_df, how="left",
                      on="audience_code").drop("audience_code", axis=1)

        return df
    



class AdvertisingSpotsResultSet(APIResultSet):

    def to_dataframe(self, pivot_audiences=True):

        # Loop through the events and then the audiences within the events
        spot_data = []
        for e in self.api_response_data['events']:
            for v in e['audience_views']:
                spot_data.append({'panel_region': e['panel']['panel_region'],
                                  'station_name': e['station']['station_name'],
                                  'spot_type': e['spot_type'],
                                  'spot_start_datetime': e['spot_start_datetime']['standard_datetime'],
                                  'spot_duration': e['spot_duration'],
                                  'preceding_programme_name': e['preceding_programme_name'],
                                  'succeeding_programme_name': e['succeeding_programme_name'],
                                  'break_type': e['break_type'],
                                  'position_in_break': e['position_in_break'],
                                  'broadcaster_spot_number': e['broadcaster_spot_number'],
                                  'commercial_number': e['commercial_number'],
                                  'clearcast_commercial_title': e['clearcast_information']['clearcast_commercial_title'] if e['clearcast_information'] is not None else None,
                                  'clearcast_match_group_code': e['clearcast_information']['match_group_code'] if e['clearcast_information'] is not None else None,
                                  'clearcast_match_group_name': e['clearcast_information']['match_group_name'] if e['clearcast_information'] is not None else None,
                                  'clearcast_buyer_code': e['clearcast_information']['buyer_code'] if e['clearcast_information'] is not None else None,
                                  'clearcast_buyer_name': e['clearcast_information']['buyer_name'] if e['clearcast_information'] is not None else None,
                                  'clearcast_advertiser_code': e['clearcast_information']['advertiser_code'] if e['clearcast_information'] is not None else None,
                                  'clearcast_advertiser_name': e['clearcast_information']['advertiser_name'] if e['clearcast_information'] is not None else None,
                                  'campaign_approval_id': e['campaign_approval_id'],
                                  'sales_house_name': e['sales_house']['sales_house_name'],
                                  'platforms': ", ".join(e['platforms']),
                                  'audience_code': v['audience_code'],
                                  'audience_size_hundreds': v['audience_size_hundreds']})
        # Convert the result into a data frame
        spot_data = pd.DataFrame(spot_data)

        # Format the transmission_time_period as a pandas datetime
        spot_data['spot_start_datetime'] = pd.to_datetime(
            spot_data['spot_start_datetime'])
        spot_data['date_of_transmission'] = spot_data['spot_start_datetime'].dt.date

        # Add the audience category names. We have a temporary problem with duplicates in this data set hence the dropping of duplicates.
        audience_categories_df = pd.DataFrame(
            self.api_response_data['audience_categories']).drop_duplicates(subset=['audience_code'])
        spot_data = spot_data.merge(
            audience_categories_df, how="left", on="audience_code").drop("audience_code", axis=1)

        return spot_data


class AudiencesByTimeResultSet(APIResultSet):

    def to_dataframe(self, pivot_audiences=True):

        # Loop through the events and then the audiences within the events
        audience_data = []
        for e in self.api_response_data['events']:
            for v in e['audience_views']:
                audience_data.append({'panel_region': e['panel']['panel_region'],
                                      'station_name': e['station']['station_name'],
                                      'date_of_transmission': e['date_of_transmission'],
                                      'activity': e['activity'],
                                      'transmission_time_period_start': e['transmission_time_period_start']['standard_datetime'],
                                      'platforms': ", ".join(e['platforms']),
                                      'audience_code': v['audience_code'],
                                      'audience_size_hundreds': v['audience_size_hundreds']})
        # Convert the result into a data frame

        audience_data = pd.DataFrame(audience_data)
        
        # Format the transmission_time_period as a pandas datetime
        audience_data['transmission_time_period_start'] = pd.to_datetime(audience_data['transmission_time_period_start'])

        # Add the audience category names. We have a temporary problem with duplicates in this data set hence the dropping of duplicates.
        audience_categories_df = pd.DataFrame(self.api_response_data['audience_categories']).drop_duplicates(subset=['audience_code'])
        audience_data = audience_data.merge(audience_categories_df, how="left", on="audience_code").drop("audience_code", axis=1)

        return audience_data

