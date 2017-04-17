import networkx as nx
import json


def make_graph(growth_rates, similarity=None, correlations=None):
    """ Make a graph of the interaction network.

    Parameters
    ----------
    growth_rates : pandas.DataFrame
        Each element is a path to a single species model file
    similarity : pandas.DataFrame
        Path to output folder where community model JSON file is saved
    correlations : list of tuple
        Each

    Returns
    -------
    networkx.Graph
        Graph representation of interaction network
    """

    # supposedly, width can be an array of floats, add as edge attribute

    # Each node is colored a shade of gray based on the similarity of
    # the OTU to the corresponding NCBI genome.
    node_colors = dict()
    if similarity is not None:
        for index, row in similarity.iterrows():
            if row['SIMILARITY'] >= 99.0:
                node_colors[row['GENOME_ID']] = "#3d3d3d"
            elif row['SIMILARITY'] >= 95.0:
                node_colors[row['GENOME_ID']] = "#4a4a4a"
            elif row['SIMILARITY'] >= 90.0:
                node_colors[row['GENOME_ID']] = "#565656"
            elif row['SIMILARITY'] >= 70.0:
                node_colors[row['GENOME_ID']] = "#636363"
            elif row['SIMILARITY'] >= 50.0:
                node_colors[row['GENOME_ID']] = "#707070"
            else:
                node_colors[row['GENOME_ID']] = "#d9d9d9"

    # The thickness of each edge is set based on the correlation between the
    # two OTUs in the pair.
    edge_width = dict()
    if correlations is not None:
        # The similarity data frame is needed to translate OTU IDs to genome IDS.
        if similarity is None:
            raise ValueError('A similarity DataFrame must be provided when correlations are provided')
        for corr in correlations:
            # Translate OTU ID to genome ID.
            a_id = similarity.loc[similarity['OTU_ID'] == corr[0]].iloc[0]['GENOME_ID']
            if a_id not in edge_width:
                edge_width[a_id] = dict()
            b_id = similarity.loc[similarity['OTU_ID'] == corr[1]].iloc[0]['GENOME_ID']
            if b_id not in edge_width:
                edge_width[b_id] = dict()

            # Set width based on correlation value.
            if corr[2] >= 0.99:
                width = 5.0
            elif corr[2] >= 0.90:
                width = 4.5
            elif corr[2] >= 0.70:
                width = 4.0
            elif corr[2] >= 0.50:
                width = 3.5
            elif corr[2] >= 0.00:
                width = 3.0
            elif corr[2] >= -0.10:
                width = 2.5
            elif corr[2] >= -0.50:
                width = 2.0
            elif corr[2] >= -0.70:
                width = 1.5
            else:
                width = 1.0

            # Order of growth rates data frame is non-deterministic so include
            # width value indexed in both orders.
            edge_width[a_id][b_id] = width
            edge_width[b_id][a_id] = width

    # For each interaction, create the nodes and an edge between them.
    graph = nx.Graph()
    for index, row in growth_rates.iterrows():
        # Add a node for the first organism in the pair.
        try:
            color = node_colors[row['A_ID']]
        except KeyError:
            color = '#e0e0e0'
        graph.add_node(row['A_ID'], {'color': color})

        # Add a node for the second organism in the pair.
        try:
            color = node_colors[row['B_ID']]
        except KeyError:
            color = '#e0e0e0'
        graph.add_node(row['B_ID'], {'color': color})

        # Classify the interaction between the two species to set the color
        # of the edge between the two nodes.
        if row['TYPE'] == 'Mutualism':
            color = '#2ca02c'  # Green
        elif row['TYPE'] == 'Parasitism':
            color = '#d62728'  # Red
        elif row['TYPE'] == 'Commensalism':
            color = '#2ca02c'  # Green
        elif row['TYPE'] == 'Competition':
            color = '#d62728'  # Red
        elif row['TYPE'] == 'Neutralism':
            color = '#c7c7c7'  # Gray
        elif row['TYPE'] == 'Amensalism':
            color = '#d62728'  # Red
        else:
            color = '#c7c7c7'  # Gray

        # Set the width of the edge based on the correlation between the
        # two species. A higher correlation gets a thicker edge.
        if len(edge_width) > 0:
            try:
                width = edge_width[row['A_ID']][row['B_ID']]
            except KeyError:
                width = 2.0
        else:
            width = 2.0

        # Add an edge between the two nodes.
        graph.add_edge(row['A_ID'], row['B_ID'], {'color': color, 'width': width})

    return graph


def plot_graph(graph):
    """ Plot a graph using a circular layout.

    Parameters
    ----------
    graph : networkx.Graph
        Graph representation of interaction network
    """

    # Draw the graph using circular layout.
    edge_widths = nx.get_edge_attributes(graph, 'width')
    edge_colors = nx.get_edge_attributes(graph, 'color')
    node_colors = nx.get_node_attributes(graph, 'color')
    nx.draw_circular(graph, with_labels=True, width=edge_widths.values(),
                     edgelist=edge_colors.keys(), edge_color=edge_colors.values(),
                     nodelist=node_colors.keys(), node_color=node_colors.values())
    return


def make_d3_source(growth_rates, json_file, similarity=None, correlations=None):
    """ Make the JSON data file for D3 visualization of interaction network. 
    
    Parameters
    ----------
    growth_rates : pandas.DataFrame
        Results of growth rate calculations
    json_file : str
        Path to file where JSON representation of interaction network is saved
    similarity : pandas.DataFrame, optional
        Similarity information with OTU ID, genome ID, and percent similarity of match
    correlations : list of tuple, optional
        Each tuple has first OTU ID (str), second OTU ID (str), and correlations value (float)
    """

    # Each node is colored a shade of gray based on the similarity of
    # the OTU to the corresponding NCBI genome. The group number is
    # translated to a color when displayed in the browser.
    node_group = dict()
    if similarity is not None:
        for index, row in similarity.iterrows():
            if row['SIMILARITY'] >= 99.:
                node_group[row['GENOME_ID']] = 1
            elif row['SIMILARITY'] >= 95.:
                node_group[row['GENOME_ID']] = 2
            elif row['SIMILARITY'] >= 90.:
                node_group[row['GENOME_ID']] = 3
            elif row['SIMILARITY'] >= 70.:
                node_group[row['GENOME_ID']] = 4
            elif row['SIMILARITY'] >= 50.:
                node_group[row['GENOME_ID']] = 5
            else:
                node_group[row['GENOME_ID']] = 6

    # The thickness of each edge is set based on the correlation between the
    # two OTUs in the pair. The width value is translated to a thickness when
    # displayed in the browser.
    link_value = dict()
    if correlations is not None:
        # The similarity data frame is needed to translate OTU IDs to genome IDS.
        if similarity is None:
            raise ValueError('A similarity DataFrame must be provided when correlations are provided')
        for corr in correlations:
            # Translate OTU ID to genome ID.
            a_id = similarity.loc[similarity['OTU_ID'] == corr[0]].iloc[0]['GENOME_ID']
            if a_id not in link_value:
                link_value[a_id] = dict()
            b_id = similarity.loc[similarity['OTU_ID'] == corr[1]].iloc[0]['GENOME_ID']
            if b_id not in link_value:
                link_value[b_id] = dict()

            # Set width value based on correlation value.
            if corr[2] >= 0.99:
                width_value = 1
            elif corr[2] >= 0.90:
                width_value = 2
            elif corr[2] >= 0.70:
                width_value = 3
            elif corr[2] >= 0.50:
                width_value = 4
            elif corr[2] >= 0.00:
                width_value = 5
            elif corr[2] >= -0.10:
                width_value = 6
            elif corr[2] >= -0.50:
                width_value = 7
            elif corr[2] >= -0.70:
                width_value = 8
            else:
                width_value = 9

            # Order of growth rates data frame is non-deterministic so include
            # width value indexed in both orders.
            link_value[a_id][b_id] = width_value
            link_value[b_id][a_id] = width_value

    # For each interaction, create the nodes and an edge (or link) between them.
    nodes = dict()
    node_list = list()
    link_list = list()
    for index, row in growth_rates.iterrows():
        # Add a node for the first organism in the pair.
        if row['A_ID'] not in nodes:
            try:
                group = node_group[row['A_ID']]
            except KeyError:
                group = 6
            node_list.append({'name': row['A_ID'], 'group': group})
            nodes[row['A_ID']] = len(node_list) - 1

        # Add a node for the second organism in the pair.
        if row['B_ID'] not in nodes:
            try:
                group = node_group[row['B_ID']]
            except KeyError:
                group = 6
            node_list.append({'name': row['B_ID'], 'group': group})
            nodes[row['B_ID']] = len(node_list) - 1

        # Classify the interaction between the two species which is used to
        # set the color of the edge between the two nodes. A value of 0 is
        # neutral, 1 is negative, 2 is positive, and 10 is unknown.
        if row['TYPE'] == 'Mutualism':
            interaction = 2
        elif row['TYPE'] == 'Parasitism':
            interaction = 1
        elif row['TYPE'] == 'Commensalism':
            interaction = 2
        elif row['TYPE'] == 'Competition':
            interaction = 1
        elif row['TYPE'] == 'Neutralism':
            interaction = 0
        elif row['TYPE'] == 'Amensalism':
            interaction = 1
        else:
            interaction = 10

        # Set the width of the edge based on the correlation between the
        # two species. A higher correlation gets a thicker edge.
        if len(link_value) > 0:
            try:
                width_value = link_value[row['A_ID']][row['B_ID']]
            except KeyError:
                width_value = 5
        else:
            width_value = 5

        # Add an edge between the two nodes.
        link_list.append({'source': nodes[row['A_ID']], 'target': nodes[row['B_ID']],
                          'interaction': interaction, 'value': width_value})

    # Store the JSON for the interaction network in a file.
    json.dump({'nodes': node_list, 'links': link_list}, open(json_file, 'w'))

    return
