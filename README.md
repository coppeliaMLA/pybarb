# barb_api
A public repository containing code packages and notebook examples for interacting with [BARB's web API](https://barb-api.co.uk/api-docs).

## About Barb

Barb is the industry’s standard for understanding what people watch.

Barb's hybrid approach integrates people-based panel data with census-level online viewing data. Barb's methodology enables us to deliver inclusive measurement of total identified viewing across all broadcast, VOD and video-sharing platforms, delivered onto and consumed via multiple platforms and devices.

As the past, present and future of total viewing measurement, Barb is uniquely placed to empower transformation of the UK TV and advertising ecosystem, through integrated audience data and actionable insights.

## About the Barb API

The Barb Application Programming Interface (API) enables Barb subscribers and underwriters to access Barb data directly for ingestion into internal tools and systems.

There are three main endpoints available:

- GET: /audiences_by_time - Audience sizes for various time periods by day, station and panel

- GET: /programme_ratings - Audience ratings data for broadcasted content by day, station and panel

- GET: /advertising_spots - Get the audience ratings data for advertising spots by day, station and panel

There are additional endpoints for users to look up Stations, Panel numbers, Advertisers and Media buying agencies for use with the main endpoints.

The data in the API are enriched with metadata from Barb and Clearcast on programmes and adverts.

## What's in this repository?

### pybarb

pybarb is a python package for interacting with the Barb API. It allows you to connect to an API endpoint, query it, and convert the results into a number of formats including pandas dataframes and csv, excel and json files. It also allows you to write the results to a database using SQLAlchemy. 

- [The package code](https://github.com/coppeliaMLA/barb_api/tree/pyBARB_dev/python/pybarb)
- [The getting started guide](http://www.coppelia.io/barb_api/python/pybarb/getting_started.html)
- The code documentation

#### Installing pybarb

pybarb is available on pip and can be installed by running:

```
pip install pybarb
```

### Other resources

This repository also contains

- Jupyter notebooks demonstrating how the Barb API can be accessed in python without using pybarb
- Some geofiles that may be useful for plotting maps using the data accessible with the API

## If you are more of an R user...

Then check out Neil's [baRb](https://github.com/neilc-itv/baRb) repository!


