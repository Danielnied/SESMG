"""
    Christian Klemm - christian.klemm@fh-muenster.de
    Gregor Becker - gregor.becker@fh-muenster.de
"""
import pandas

# columns_of_plotly_table
copt = [
    "ID",
    "type",
    "input 1/kWh",
    "input 2/kWh",
    "output 1/kWh",
    "output 2/kWh",
    "capacity/kW",
    "variable costs/CU",
    "periodical costs/CU",
    "investment/kW",
    "max. invest./kW",
    "constraints/CU",
]


def add_component_to_loc(
    label: str,
    comp_dict: list,
    df_list_of_components: pandas.DataFrame,
    maxinvest="---",
) -> pandas.DataFrame:
    """
        adds the given component with it's parameters to list of
        components (loc)
        
        :param label: str containing the component's label shown in \
            list of components (loc)
        :type label: str
        :param comp_dict: list holding the energy system component's \
            information as specified in the main method collect_data
        :type comp_dict: list
        :param df_list_of_components: DataFrame containing the list of \
            components which will be the components.csv afterwards
        :type df_list_of_components: pandas.DataFrame
        :param maxinvest: str holding the maximum possible investment
        :type maxinvest: str
        
        :return: - **df_list_of_components** (pandas.DataFrame) - \
            DataFrame containing the updated (new added line) list of \
            components which will be the components.csv afterwards
    """
    if str(type(comp_dict[4])) not in ["<class 'float'>", "<class 'int'>"]:
        capacity = max(comp_dict[4])
    else:
        capacity = comp_dict[4]
    # add the new component's line to the list of components dataframe
    df_list_of_components = pandas.concat(
        [
            df_list_of_components,
            pandas.DataFrame(
                [
                    [
                        label,
                        comp_dict[10],
                        round(sum(comp_dict[0]), 2),
                        round(sum(comp_dict[1]), 2),
                        round(sum(comp_dict[2]), 2),
                        round(sum(comp_dict[3]), 2),
                        round(capacity, 2),
                        round(comp_dict[8], 2),
                        round(comp_dict[6], 2),
                        round(comp_dict[5], 2),
                        maxinvest,
                        round(comp_dict[9], 2),
                    ]
                ],
                columns=copt,
            ),
        ]
    )
    return df_list_of_components


def append_flows(
    label: str, comp_dict: list, df_result_table: pandas.DataFrame
) -> pandas.DataFrame:
    """
        In this method, the time series of inflows and outflows as well
        as the capacities of the component (comp_dict) are appended to
        the data structure df_result_table. Here, each time series
        represents a column. This data structure is stored at the end
        of the result processing as file result.csv in the result
        folder of the model definition and represents the basis for the
        plotting in the GUI.
        
        :param label: str containing the component's label shown in \
            list of components (loc)
        :type label: str
        :param comp_dict: list holding the energy system component's \
            information as specified in the main method collect_data
        :type comp_dict: list
        :param df_result_table: DataFrame containing the energy \
            system's flows which will be plotted within the GUI and \
            exported in the result.csv file in the model definition's \
            result folder
        :type df_result_table: pandas.DataFrame
    
        :return: - **df_result_table** (pandas.DataFrame) - \
            DataFrame containing the updated energy system's flows \
            (added new columns) which will be plotted within the GUI \
            and exported in the result.csv file in the model \
            definition's result folder
    """
    flow_type_dict = {
        0: "_input1",
        1: "_input2",
        2: "_output1",
        3: "_output2",
        4: "_capacity",
    }
    dict_of_columns = {}
    # append the components flows to the dict of columns for later
    # plotting within the GUI
    for flow in flow_type_dict:
        if str(type(comp_dict[flow])) not in ["<class 'float'>", "<class 'int'>"]:
            if sum(comp_dict[flow]) != 0:
                dict_of_columns[label + flow_type_dict[flow]] = comp_dict[flow]
    # add the new added columns to the df results table which will be
    # the results.csv in the model definition's result folder
    df_result_table = pandas.concat(
        [df_result_table, pandas.DataFrame(dict_of_columns)], axis=1
    )
    return df_result_table


def prepare_loc(
    comp_dict: dict,
    df_result_table: pandas.DataFrame,
    df_list_of_components: pandas.DataFrame,
) -> (pandas.DataFrame, float, float, float, pandas.DataFrame):
    """
        In this method, on the one hand, the components as well as
        their flows are added to the list of components (loc) and to
        the df_result_table and, on the other hand, the costs
        (variable and periodic) as well as emissions of the energy
        system are balanced.
        
        :param comp_dict: dictionary holding the energy systems' \
            components data e.g. investment, periodical costs, etc.
        :type comp_dict: dict
        :param df_result_table: DataFrame containing the energy \
            system's flows which will be plotted within the GUI and \
            exported in the result.csv file in the model definition's \
            result folder
        :type df_result_table: pandas.DataFrame
        :param df_list_of_components: DataFrame containing the list of \
            components which will be the components.csv afterwards
        :type df_list_of_components: pandas.DataFrame
        
        :return: - **df_list_of_components** (pandas.DataFrame) - \
                    DataFrame containing the list of components which \
                    will be the components.csv afterwards
                 - **total_periodical_costs** (float) - total \
                    periodical costs of the considered energy system
                 - **total_variable_costs** (float) - total \
                    variable costs of the considered energy system
                 - **total_constrain_costs** (float) - total \
                    constraint costs of the considered energy system
                 - **df_list_of_components** (pandas.DataFrame) - \
                    DataFrame containing the energy system's flows \
                    which will be plotted within the GUI and exported \
                    in the result.csv file in the model definition's \
                    result folder
    """
    # clear the old values
    total_periodical_costs = 0
    total_variable_costs = 0
    total_constraint_costs = 0
    # iterate threw all components add their flows to the results.csv
    # and it's parameters to the list of components (loc)
    for label in comp_dict:
        df_result_table = append_flows(
            label=str(label),
            comp_dict=comp_dict[label],
            df_result_table=df_result_table,
        )
        df_list_of_components = add_component_to_loc(
            label=label,
            comp_dict=comp_dict[label],
            df_list_of_components=df_list_of_components,
            maxinvest=comp_dict[label][7],
        )
        total_periodical_costs += comp_dict[label][6]
        total_variable_costs += comp_dict[label][8]
        total_constraint_costs += comp_dict[label][9]

    return (
        df_list_of_components,
        total_periodical_costs,
        total_variable_costs,
        total_constraint_costs,
        df_result_table,
    )


def prepare_data(
    comp_dict: dict, total_demand: float, nodes_data: dict
) -> (pandas.DataFrame, float, float, float, pandas.DataFrame, float):
    """
        This method is the main method of data preparation for
        subsequent export and/or display in the GUI of the energy
        system's result data.
    
        :param comp_dict: dictionary holding the energy systems' \
            components data e.g. investment, periodical costs, etc.
        :type comp_dict: dict
        :param total_demand: float holding the energy systems final \
            energy demand calculated based on the energy systems' sinks
        :type total_demand: float
        :param nodes_data: dictionary containing data from excel \
                model definition file
        :type nodes_data: dict
        
        :return: - **df_list_of_components** (pandas.DataFrame) - \
                    DataFrame containing the list of components which \
                    will be the components.csv afterwards
                 - **total_periodical_costs** (float) - total \
                    periodical costs of the considered energy system
                 - **total_variable_costs** (float) - total \
                    variable costs of the considered energy system
                 - **total_constrain_costs** (float) - total \
                    constraint costs of the considered energy system
                 - **df_list_of_components** (pandas.DataFrame) - \
                    DataFrame containing the energy system's flows \
                    which will be plotted within the GUI and exported \
                    in the result.csv file in the model definition's \
                    result folder
                 - **total_demand** (float) - total final energy \
                    demand of the considered energy system
    """
    df_list_of_components = pandas.DataFrame(columns=copt)
    df_result_table = pandas.DataFrame()
    # iterate threw all the energy systems' components
    for label in comp_dict.copy():
        # reduce the energy system's final energy demand by the flow of
        # the insulation measures source components
        if "insulation" in label:
            total_demand -= sum(comp_dict[label][2])
            comp_dict[label][-1] = "insulation"
        # get rid of non investable components like the ambient sources
        # of heat pumps
        elif "high_temp" in label or "low_temp" in label:
            comp_dict.pop(label)
        # handling the investment structure of solar thermal collector
        # component
        elif "collector" in label and label[:-10] in list(
            nodes_data["sources"]["label"]
        ):
            for i in range(0, 3):
                comp_dict[label[:-10]][i] = comp_dict[label][i]
            comp_dict[label[:-10]][8] = comp_dict[label][8]
            comp_dict[label[:-10]][9] += comp_dict[label][9]
            comp_dict.pop(label)
    # after updating the comp_dict data structure prepare the result
    # dataframes
    (
        df_list_of_components,
        total_periodical_costs,
        total_variable_costs,
        total_constraint_costs,
        df_result_table,
    ) = prepare_loc(
        comp_dict=comp_dict,
        df_result_table=df_result_table,
        df_list_of_components=df_list_of_components,
    )
    return (
        df_list_of_components,
        total_periodical_costs,
        total_variable_costs,
        total_constraint_costs,
        df_result_table,
        total_demand,
    )
