# -*- coding: utf-8 -*-
"""
    Functions for creating an oemof energy system.

    Christian Klemm - christian.klemm@fh-muenster.de
"""
import pandas
import logging
from program_files.preprocessing.import_weather_data \
    import import_open_fred_weather_data
from oemof.solph import EnergySystem
import random
pandas.options.mode.chained_assignment = None


def import_model_definition(filepath: str, delete_units=True) -> dict:
    """
        Imports data from a spreadsheet model definition file.
    
        The excel sheet has to contain the following sheets:
    
            - energysystem
            - buses
            - transformers
            - sinks
            - sources
            - storages
            - links
            - time series
            - weather data
            - competition constraints
            - insulation
            - district heating
            - pipe types
    
        :param filepath: path to excel model definition file
        :type filepath: str
        :param delete_units: boolean which defines rather the unit \
            row in the imported spreadsheets is removed or not
        :type delete_units: bool
    
        :raises: - **FileNotFoundError** - excel spreadsheet not found
    
        :return: - **nodes_data** (dict) - dictionary containing excel sheets
    """
    # creates nodes from excel sheet
    try:
        xls = pandas.ExcelFile(filepath)
    except FileNotFoundError:
        raise FileNotFoundError("Problem importing model definition file.")
    
    nodes_data = {
        "buses": xls.parse("buses"),
        "energysystem": xls.parse("energysystem"),
        "sinks": xls.parse("sinks"),
        "links": xls.parse("links"),
        "sources": xls.parse("sources"),
        "timeseries": xls.parse("time series", parse_dates=["timestamp"]),
        "transformers": xls.parse("transformers"),
        "storages": xls.parse("storages"),
        "weather data": xls.parse("weather data", parse_dates=["timestamp"]),
        "competition constraints": xls.parse("competition constraints"),
        "insulation": xls.parse("insulation"),
        "district heating": xls.parse("district heating"),
        "pipe types": xls.parse("pipe types")
    }
    if delete_units:
        # delete spreadsheet row within technology or units specific
        # parameters
        for index in nodes_data.keys():
            if index not in ["timeseries", "weather data"] \
                    and len(nodes_data[index]) > 0:
                nodes_data[index] = nodes_data[index].drop(index=0)
    
    # returns logging info
    logging.info("\t Spreadsheet scenario successfully imported.")
    # if the user imported coordinates for the OpenFred weather data
    # download the import algorithm is triggered
    if nodes_data["energysystem"].loc[1, "weather data lat"] \
            not in ["None", "none"]:
        logging.info("\t Start import weather data")
        lat = nodes_data["energysystem"].loc[1, "weather data lat"]
        lon = nodes_data["energysystem"].loc[1, "weather data lon"]
        nodes_data = import_open_fred_weather_data(nodes_data, lat, lon)
    # returns nodes data
    return nodes_data


def import_model_definition_montecarlo(current_run: int, montecarlo_section_runs: int,
                            montecarlo_section: int,
                            filepath: str, result_path:str, delete_units=True) -> dict:
    """
        Imports data from a spreadsheet model definition file and
        variates parameters. Returns the data needed to start a
        simulation if the selected section is carried out, returns
        None to skip the rest of runs if not.
    
        The excel sheet has to contain the following sheets:
    
            - energysystem
            - buses
            - transformers
            - sinks
            - sources
            - storages
            - links
            - time series
            - weather data
            - competition constraints
            - insulation
            - district heating
            - pipe types
        
        [...]
        
        :param filepath: path to excel model definition file
        :type filepath: str
        :param delete_units: boolean which defines rather the unit \
            row in the imported spreadsheets is removed or not
        :type delete_units: bool
    
        :raises: - **FileNotFoundError** - excel spreadsheet not found
    
        :return: - **nodes_data** (dict) - dictionary containing excel sheets
    """
    # creates nodes from excel sheet
    try:
        xls = pandas.ExcelFile(filepath)
           
    except FileNotFoundError:
        raise FileNotFoundError("Problem importing model definition file.")
   
    # varies buses, if no building is connected to the 
    # district heating, the grid will be deactivated
    buses_varied = xls.parse("buses")
    
    connected_buildings = 0
    for i, index in buses_varied["district heating conn."][1:].items():
        if buses_varied["sector"][i] == "heat":
            index = random.randint(0,1)
            buses_varied["district heating conn."][i] = index
            connected_buildings += index
            logging.info("House connection: " + str(buses_varied["district heating conn."][i]))

    for i, index in buses_varied["district heating conn."][1:].items():
        if buses_varied["sector"][i] == "central_heat":
            if connected_buildings != 0:
                buses_varied["district heating conn."][i] = "dh-system"
            else:
                buses_varied["district heating conn."][i] = 0
            logging.info("District heating connection: " +str(buses_varied["district heating conn."][i]))

    # varies sources
    sources_varied = xls.parse("sources")
    sources = xls.parse("sources")
    
    for i, index in sources_varied["min. investment capacity"][1:].items():
        index = random.randint(0 , sources["max. investment capacity"][i])
        sources_varied["min. investment capacity"][i] = index
        sources_varied["max. investment capacity"][i] = sources_varied["min. investment capacity"][i]
        logging.info("Sources: " + str(index))

    
    # varies transformers
    transformers_varied = xls.parse("transformers")
    transformers = xls.parse("transformers")
    for i, index in transformers_varied["min. investment capacity"][1:].items():
        index = random.randint(0 , transformers["max. investment capacity"][i])
        transformers_varied["min. investment capacity"][i] = index
        transformers_varied["max. investment capacity"][i] = transformers_varied["min. investment capacity"][i]
        logging.info("Transformers: " + str(index))

    # varies storages
    storages_varied = xls.parse("storages")
    storages = xls.parse("storages")
    for i, index in storages_varied["min. investment capacity"][1:].items():
        index = random.randint(0 , storages["max. investment capacity"][i])
        storages_varied["min. investment capacity"][i] = index
        storages_varied["max. investment capacity"][i] = storages_varied["min. investment capacity"][i]
        logging.info("Storages: " + str(index))

    # varies links
    links_varied = xls.parse("links")
    links = xls.parse("links")
    for i, index in links_varied["min. investment capacity"][1:].items():
        index = random.randint(0 , links_varied["max. investment capacity"][i])
        links_varied["min. investment capacity"][i] = index
        links_varied["max. investment capacity"][i] = links_varied["min. investment capacity"][i]
        logging.info("Links: " + str(index))

    # varies insulation and its area   
    insulation_varied = xls.parse("insulation")
    insulation = xls.parse("insulation")
    
    for i, index in insulation_varied["existing with costs"][1:].items():
        index = random.randint(0,1)
        insulation_varied["existing with costs"][i] = index
        logging.info("Insulation: " + str(index))
    for i, index in insulation_varied["area"][1:].items():
        index = random.uniform(0 , insulation["area"][i])
        insulation_varied["area"][i] = index
        logging.info("Insulation area: " + str(index))

    # activates district heating if
    # at least one house connection is available
    district_heating = xls.parse("district heating")
    
    for i, index in district_heating["active"][1:].items():
        if connected_buildings != 0:
            district_heating["active"][i] = 1
        else:
            district_heating["active"][i] = 0   
        logging.info("District heating: " + str(district_heating["active"][i]))
    
    
    # read and return varied data if current run is in the selected section
    if current_run >= montecarlo_section_runs * (montecarlo_section-1) and \
    current_run < montecarlo_section_runs * montecarlo_section:
    
        nodes_data = {
        "buses": buses_varied,
        "energysystem": xls.parse("energysystem"),
        "sinks": xls.parse("sinks"),
        "links": links_varied,
        "sources": sources_varied,
        "timeseries": xls.parse("time series", parse_dates=["timestamp"]),
        "transformers": transformers_varied,
        "storages": storages_varied,
        "weather data": xls.parse("weather data", parse_dates=["timestamp"]),
        "competition constraints": xls.parse("competition constraints"),
        "insulation": insulation_varied,
        "district heating": district_heating,
        "pipe types": xls.parse("pipe types")
        }
        
        if delete_units:
            # delete spreadsheet row within technology or units specific
            # parameters
            for index in nodes_data.keys():
                if index not in ["timeseries", "weather data"] \
                        and len(nodes_data[index]) > 0:
                    nodes_data[index] = nodes_data[index].drop(index=0)

        # returns logging info
        logging.info("\t Spreadsheet scenario successfully imported.")
        # if the user imported coordinates for the OpenFred weather data
        # download the import algorithm is triggered
        if nodes_data["energysystem"].loc[1, "weather data lat"] \
                not in ["None", "none"]:
            logging.info("\t Start import weather data")
            lat = nodes_data["energysystem"].loc[1, "weather data lat"]
            lon = nodes_data["energysystem"].loc[1, "weather data lon"]
            nodes_data = import_open_fred_weather_data(nodes_data, lat, lon)
   
        # save changed files as a separate sheet
        path = result_path + "/montecarlo_used_parameters.xlsx"
        writer = pandas.ExcelWriter(path, engine='xlsxwriter')
        nodes_data['buses'].to_excel(writer, sheet_name='buses')
        nodes_data['sources'].to_excel(writer, sheet_name='sources')
        nodes_data['transformers'].to_excel(writer, sheet_name='transformers')
        nodes_data['storages'].to_excel(writer, sheet_name='storages')
        nodes_data['links'].to_excel(writer, sheet_name='links')
        nodes_data['insulation'].to_excel(writer, sheet_name='insulation')
        nodes_data['district heating'].to_excel(writer, sheet_name='district heating')
        writer.close()
   
    else:
        
        # skips not selected runs
        nodes_data={}
        
    # returns nodes data
    return nodes_data


def define_energy_system(nodes_data: dict) -> EnergySystem:
    """
        Creates an energy system with the parameters defined in the
        given .xlsx-file. The file has to contain a sheet called
        "energysystem", which has to be structured as follows:
    
        +-------------------+-------------------+-------------------+
        |start_date         |end_date           |temporal resolution|
        +-------------------+-------------------+-------------------+
        |YYYY-MM-DD hh:mm:ss|YYYY-MM-DD hh:mm:ss|h                  |
        +-------------------+-------------------+-------------------+
    
        :param nodes_data: dictionary containing data from excel model \
            definition file
        :type nodes_data: dict
        
        :return: **esys** (oemof.solph.Energysystem) - oemof energy \
            system
    """
    # fix pyomo error while using the streamlit gui
    import pyutilib.subprocess.GlobalData
    pyutilib.subprocess.GlobalData.DEFINE_SIGNAL_HANDLERS_DEFAULT = False
    
    # Importing energysystem parameters from the scenario
    row = next(nodes_data["energysystem"].iterrows())[1]
    temp_resolution = row["temporal resolution"]
    timezone = row["timezone"]
    start_date = row["start date"]
    end_date = row["end date"]
    
    # creates time index
    datetime_index = pandas.date_range(start=start_date,
                                       end=end_date,
                                       freq=temp_resolution)
    
    # initialisation of the energy system
    esys = EnergySystem(timeindex=datetime_index)
    # setting the index column for time series and weather data
    for sheet in ["timeseries", "weather data"]:
        # defines a time series
        nodes_data[sheet].set_index("timestamp", inplace=True)
        nodes_data[sheet].index = \
            pandas.to_datetime(nodes_data[sheet].index.values, utc=True)
        nodes_data[sheet].index = \
            pandas.to_datetime(nodes_data[sheet].index).tz_convert(timezone)
    
    # returns logging info
    logging.info(
            "Date time index successfully defined:\n start date:          "
            + str(start_date)
            + ",\n end date:            "
            + str(end_date)
            + ",\n temporal resolution: "
            + str(temp_resolution)
    )
    
    # returns oemof energy system as result of this function
    return esys
