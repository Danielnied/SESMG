"""
    Gregor Becker - gregor.becker@fh-muenster.de
"""
from program_files.preprocessing.components import district_heating, \
    district_heating_calculations
import oemof.solph as solph
import dhnx.optimization.oemof_heatpipe as heatpipe
import dhnx.optimization.optimization_models as optimization
from dhnx.network import ThermalNetwork
import pandas


def connect_clustered_dh_to_system(
        oemof_opti_model, busd: dict, thermal_network: ThermalNetwork,
        nodes_data: dict) -> optimization.OemofInvestOptimizationModel:
    """
        Method which creates links to connect the model definition
        based created sinks to the thermal network components created
        before.
        
        NOTE:
        
              1. The calculation of the periodical cost of the
                 clustered heat pipeline is based on the linearization
                 of the heatpipe type due to the iterative approach see
                 parameters sheet.
              2. a distinction between exergy and anergy has not been
                 implemented yet
    
        :param oemof_opti_model: Oemof model holing thermal network
        :type oemof_opti_model:
        :param busd: dictionary containing model definition buses
        :type busd: dict
        :param thermal_network: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_network: ThermalNetwork
        :param nodes_data: dictionary holding the users model \
            definition's data
        :type nodes_data: dict
        
        :return: - **oemof_opti_model** \
            (optimization.OemofInvestOptimizationModel) - model \
            holding dh components
    """
    oemof_opti_model = district_heating.remove_redundant_sinks(
        oemof_opti_model=oemof_opti_model)
    oemof_opti_model = district_heating_calculations.calc_heat_pipe_attributes(
            oemof_opti_model=oemof_opti_model,
            pipe_types=nodes_data["pipe types"])
    # create link to connect consumers heat bus to the dh-system
    for num, consumer in thermal_network.components["consumers"].iterrows():
        # create the bus for the clustered heat network connection point
        bus = solph.Bus(label="clustered_consumers_{}".format(consumer["id"]))
        oemof_opti_model.nodes.append(bus)
        busd["clustered_consumers_{}".format(consumer["id"])] = bus
        # get the clustered consumer link data from the model
        # definition's pipe types sheet
        link = nodes_data["pipe types"].loc[
            nodes_data["pipe types"]["label_3"] == "clustered_consumer_link"]
        # get the thermal network's pipe which connects the
        # investigated consumer to the thermal network
        # TODO liegt hier eine doppelte Kostenbetrachtung vor?
        pipes = thermal_network.components["pipes"]
        pipe = pipes.loc[pipes["to_node"] == "consumers-{}".format(
            consumer["id"])]
        
        # transformer inputs of clustered house connection
        inputs = {
            oemof_opti_model.buses[heatpipe.Label(
                "consumers",
                "heat",
                "bus",
                "consumers-{}".format(consumer["id"]),
                "exergy")]: solph.Flow(
                    investment=solph.Investment(
                        ep_costs=float(link["capex_pipes"]
                                       * pipe["length"][0]),
                        periodical_constraint_costs=float(
                            link["periodical_constraint_costs"]
                            * pipe["length"][0]),
                        maximum=200 * len(consumer["input"]),
                        minimum=0,
                        existing=0,
                        nonconvex=False,
                        fix_constraint_costs=0
                    ),
                    emission_factor=0,
                    variable_costs=0
                )
        }
        
        # create the transformer representing the clustered pipe
        oemof_opti_model.nodes.append(
            solph.Transformer(
                label=(
                    "pipe-clustered{}-".format(consumer["id"])
                    + str(pipe["length"][0])
                ),
                inputs=inputs,
                outputs={
                    busd["clustered_consumers_{}".format(consumer["id"])]:
                        solph.Flow(emission_factor=0, variable_costs=0)
                },
                conversion_factors={
                    busd["clustered_consumers_{}".format(consumer["id"])]: 1
                    - (((15.8689 / 1500) * pipe["length"][0]) / 24.42)
                },
            )
        )
        
        counter = 1
        # get the house station's data from the users model definition
        housestation = nodes_data["pipe types"].loc[
            nodes_data["pipe types"]["label_3"] == "dh_heatstation"]
        # iterate threw all consumers and create the connection between
        # the clustered network bus and the consumer sheat buses
        for consumer_input in consumer["input"]:
            oemof_opti_model.nodes.append(
                solph.Transformer(
                    label="dh_heat_house_station_{}".format(consumer["id"])
                    + "-"
                    + str(consumer_input),
                    inputs={
                        busd[
                            "clustered_consumers_{}".format(consumer["id"])
                        ]: solph.Flow(emission_factor=0, variable_costs=0)
                    },
                    outputs={
                        busd[consumer_input]: solph.Flow(
                            investment=solph.Investment(
                                ep_costs=float(housestation["capex_pipes"]),
                                periodical_constraint_costs=0,
                                minimum=0,
                                maximum=999 * len(consumer["input"]),
                                existing=0,
                                nonconvex=False,
                                fix_constraint_costs=0
                            ),
                            emission_factor=0,
                            variable_costs=0
                        )
                    },
                    conversion_factors={
                        busd[consumer_input]: float(housestation["efficiency"])
                    },
                )
            )
            counter += 1
    return oemof_opti_model


def get_forks_street_section_wise(nodes_data: dict, forks: pandas.DataFrame
                                  ) -> dict:
    """
        Within this method all perpendicular foot points within one
        street section are collected to create the clustered foot point
        later on.
        
        :param nodes_data: dictionary holding the users model \
            definition's data
        :type nodes_data: dict
        :param forks: DataFrame holding the unclustered thermal \
            networks' forks
        :type forks: pandas.DataFrame
        
        :return: - **forks_street** (dict) - dict holding the \
            combination of the street label and a list of it's \
            connected forks
    """
    # put all forks of a given street part to forks_street dict
    forks_street = {}
    active_streets = nodes_data["district heating"].loc[
        nodes_data["district heating"]["active"] == 1]
    # iterate threw all active street section's given in the district
    # heating spreadsheet
    for index, street in active_streets.iterrows():
        # iterate threw all forks and search the ones with matching
        # street label
        street_forks = []
        for num, fork in forks.iterrows():
            if fork["street"] == street["label"]:
                street_forks.append(fork["id"])
        # update the dict holding the combination of the street label
        # and a list of it's connected forks
        forks_street.update({street["label"]: street_forks})

    return forks_street


def get_pipe_lengths_street_section_wise(forks_street: dict, 
                                         thermal_network: ThermalNetwork,
                                         pipes: pandas.DataFrame
                                         ) -> (ThermalNetwork, dict):
    """
        Within this method all pipe lengths connected to an
        investigated street section are collected. The not longer used
        pipes are deleted afterwards.
    
        :param forks_street: dict holding the combination of the \
            street label and a list of it's connected forks
        :type forks_street: dict
        :param thermal_network: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_network: ThermalNetwork
        :param pipes: DataFrame holding the unclustered thermal \
            networks' pipes
        :type pipes: pandas.DataFrame
        
        :return: - **thermal_network** (ThermalNetwork) - DHNx \
                    ThermalNetwork instance used to create the \
                    components of the thermal network for the energy \
                    system. Within this method the not longer used \
                    pipes were deleted.
                - **streets_pipe_length** - dictionary holding the \
                    combination of a street section's label and a list \
                    of all pipes that were connected to the \
                    investigated street section
    """
    streets_pipe_length = {}
    # get the length of all pipes connecting street part to consumer of
    # a given street part and put them to streets_pipe_length
    for street in forks_street:
        if forks_street[street]:
            num = 0
            # iterate threw the forks of the studied street section
            # (street) change the integer id to forks-<ID>
            for fork in forks_street[street]:
                forks_street[street][num] = "forks-{}".format(fork)
                num += 1
            # iterate threw all of the energy systems' pipes searching
            # pipes connecting a consumer with one of the forks of the
            # previously created dictionary
            for num, pipe in pipes.iterrows():
                # from node in the created list and to node contains
                # consumers
                if pipe["from_node"] in forks_street[street] \
                        and "consumers" in pipe["to_node"]:
                    # create the list which will be added to the
                    # collection dictionary (street_pipe_length)
                    pipe_part = [pipe["id"], pipe["from_node"],
                                 pipe["to_node"], pipe["length"]]
                    if street not in streets_pipe_length:
                        streets_pipe_length.update({street: [pipe_part]})
                    else:
                        streets_pipe_length[street].append(pipe_part)
                    thermal_network.components["pipes"] = \
                        thermal_network.components["pipes"].drop(
                                index=pipe["id"])
    return thermal_network, streets_pipe_length


def get_street_sections_consumers_information(streets_pipe_length: dict,
                                              thermal_network: ThermalNetwork,
                                              consumers: pandas.DataFrame
                                              ) -> (ThermalNetwork, dict):
    """
        Within this method all consumer information of consumers
        connected to an investigated street section are collected.
        The not longer used consumers are deleted afterwards.
    
        :param streets_pipe_length: dictionary holding the combination \
            of a street section's label and a list of all pipes that \
            were connected to the investigated street section
        :type streets_pipe_length: dict
        :param thermal_network: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_network: ThermalNetwork
        :param consumers: DataFrame holding the unclustered thermal \
            networks' consumers
        :type consumers: pandas.DataFrame
        
        :return: - **thermal_network** (ThermalNetwork) - DHNx \
                    ThermalNetwork instance used to create the \
                    components of the thermal network for the energy \
                    system. Within this method the not longer used \
                    consumers were deleted.
                - **streets_consumer** - dictionary holding the \
                    combination of a street section's label and a list \
                    of consumer information of all consumers that were \
                    connected to the investigated street section
    
    """
    # get consumer information of a given street part
    streets_consumer = {}
    for street in streets_pipe_length:
        counter, lat, lon = 0, 0, 0
        inputs = []
        # iterate threw the collected street consumers' information
        for street_consumer in streets_pipe_length[street]:
            # search fot the corresponding consumer
            for num, consumer in consumers.iterrows():
                if street_consumer[2] == "consumers-{}".format(consumer["id"]):
                    counter += 1
                    lat += consumer["lat"]
                    lon += consumer["lon"]
                    inputs.append(consumer["input"])
                    thermal_network.components[
                        "consumers"
                    ] = thermal_network.components["consumers"].drop(
                            index=consumer["id"]
                    )
        # collect the consumers information streetwise
        streets_consumer.update({street: [counter, lat, lon, inputs]})
        
    return thermal_network, streets_consumer


def clear_thermal_network_dataframes(thermal_network: ThermalNetwork
                                     ) -> ThermalNetwork:
    """
        Remove the not longer used pipes and forks of the unclustered
        thermal network to create the new ones afterwards.
        
        :param thermal_network: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_network: ThermalNetwork
        
        :return: **thermal_network** (ThermalNetwork) - DHNx \
            ThermalNetwork instance used to create the components of \
            the thermal network for the energy system. Within this \
            method the not longer used forks and pipes were deleted.
    """
    # clear pipes Dataframe
    for num, pipe in thermal_network.components["pipes"].iterrows():
        thermal_network.components["pipes"] = \
            thermal_network.components["pipes"].drop(index=num)
    
    # clear forks Dataframe
    for num, fork in thermal_network.components["forks"].iterrows():
        thermal_network.components["forks"] = \
            thermal_network.components["forks"].drop(index=num)
    thermal_network.components["forks"] = \
        thermal_network.components["forks"].reset_index(drop=True)
    
    return thermal_network


def clustering_dh_network(nodes_data: dict, thermal_network: ThermalNetwork
                          ) -> ThermalNetwork:
    """
        Using this method, a spatial clustering of the thermal network
        is carried out based on the road sections entered by the user.
        
        :param thermal_network: DHNx ThermalNetwork instance used to \
            create the components of the thermal network for the \
            energy system.
        :type thermal_network: ThermalNetwork
        :param nodes_data: dictionary holding the users model \
            definition's data
        :type nodes_data: dict
        
        :return: - **thermal_network** (ThermalNetwork) - DHNx \
            ThermalNetwork instance used to create the components of \
            the thermal network for the energy system.
    """
    # create a local copy of the thermal network components dataframes
    forks = thermal_network.components["forks"].copy()
    pipes = thermal_network.components["pipes"].copy()
    consumers = thermal_network.components["consumers"].copy()
    
    forks_street = get_forks_street_section_wise(nodes_data=nodes_data,
                                                 forks=forks)
        
    thermal_network, streets_pipe_length = \
        get_pipe_lengths_street_section_wise(
            forks_street=forks_street,
            thermal_network=thermal_network,
            pipes=pipes
        )
                    
    thermal_network, streets_consumer = \
        get_street_sections_consumers_information(
            streets_pipe_length=streets_pipe_length,
            thermal_network=thermal_network,
            consumers=consumers
        )
        
    thermal_network = clear_thermal_network_dataframes(
        thermal_network=thermal_network)
    
    counter = 0
    
    # calc the summed length of consumer pipes of a given street path
    for street in streets_pipe_length:
        # length = 0
        # for i in streets_pipe_length[street]:
        #    length += i[3]
        streets_pipe_length.update({street: sum(streets_pipe_length[street])})
    
    street_sections = district_heating.convert_dh_street_sections_list(
        street_sec=nodes_data["district heating"].copy()
    )
    
    # create the clustered consumer and its fork and pipe
    for street in streets_consumer:
        # add consumer to thermal network components (dummy
        # because cut from system after creating dhnx components
        new_consumer = pandas.DataFrame(
            [pandas.Series(
                data={
                    "id": "consumers-{}".format(counter),
                    "lat": float(streets_consumer[street][1]
                                 / streets_consumer[street][0]),
                    "lon": float(streets_consumer[street][2]
                                 / streets_consumer[street][0]),
                    "component_type": "Consumer",
                    "P_heat_max": 1,
                    "input": streets_consumer[street][3],
                    "label": "",
                    "street": street,
                    "length": streets_pipe_length[street],
                }
            )]
        )
        thermal_network.components["consumers"] = pandas.concat(
            [thermal_network.components["consumers"], new_consumer]
        )
        # calculate the foot point of the new clustered consumer
        foot_point = district_heating_calculations.get_nearest_perp_foot_point(
            {
                "lat": float(streets_consumer[street][1]
                             / streets_consumer[street][0]),
                "lon": float(streets_consumer[street][2]
                             / streets_consumer[street][0]),
            },
            street_sections,
            counter,
            "consumers",
        )
        # add the pipe to the clustered consumer to the list of pipes
        new_pipe_part = pandas.DataFrame(
            [pandas.Series(
                data={
                    "id": "pipe-{}".format(
                        len(thermal_network.components["pipes"])
                    ),
                    "from_node": "forks-{}".format(foot_point[0][10:-5]),
                    "to_node": "consumers-{}".format(counter),
                    "length": foot_point[3],
                    "component_type": "Pipe",
                }
            )]
        )
        thermal_network.components["pipes"] = pandas.concat(
            [
                thermal_network.components["pipes"],
                new_pipe_part
            ]
        )
        # create fork of the new calculated foot point
        thermal_network = district_heating.create_fork(
            point=foot_point,
            label=foot_point[0][10:-5],
            thermal_net=thermal_network)
        counter += 1

    street_sections = district_heating.convert_dh_street_sections_list(
        street_sec=nodes_data["district heating"].copy()
    )
    
    thermal_network = district_heating.create_intersection_forks(
        street_sec=nodes_data["district heating"],
        thermal_net=thermal_network)
    thermal_network = district_heating.create_producer_connection_point(
        buses=nodes_data["buses"],
        road_sections=street_sections,
        thermal_net=thermal_network)
    thermal_network = district_heating.create_supply_line(
        streets=nodes_data["district heating"],
        thermal_net=thermal_network)
    
    return district_heating.adapt_dhnx_style(thermal_net=thermal_network,
                                             cluster_dh=False)
