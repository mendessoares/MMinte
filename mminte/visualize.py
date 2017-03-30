import networkx as nx
import json


def make_graph(growth_rates, similarity=None):
    """ Make a graph of the interaction network.

    """

    # supposedly, width can be an array of floats, add as edge attribute

    # Each node is colored a shade of gray based on the similarity of
    # the OTU to the corresponding NCBI genome. The second field in the
    # similarity tuple is the NCBI genome ID and the third field is the
    # percent similarity.
    node_colors = dict()
    if similarity:
        for sim in similarity:
            if sim[2] >= 99.00:
                node_colors[sim[1]] = "#3d3d3d"
            elif sim[2] >= 95.00:
                node_colors[sim[1]] = "#4a4a4a"
            elif sim[2] >= 90.00:
                node_colors[sim[1]] = "#565656"
            elif sim[2] >= 70.00:
                node_colors[sim[1]] = "#636363"
            elif sim[2] >= 50.00:
                node_colors[sim[1]] = "#707070"
            else:
                node_colors[sim[1]] = "#d9d9d9"

    graph = nx.Graph()
    for index, row in growth_rates.iterrows():
        try:
            color = node_colors[row['A_ID']]
        except KeyError:
            color = '#e0e0e0'
        graph.add_node(row['A_ID'], {'color': color})
        try:
            color = node_colors[row['B_ID']]
        except KeyError:
            color = '#e0e0e0'
        graph.add_node(row['B_ID'], {'color': color})
        if row['TYPE'] == 'Mutualism':
            color = '#2ca02c'
        elif row['TYPE'] == 'Parasitism':
            color = '#d62728'
        elif row['TYPE'] == 'Commensalism':
            color = '#2ca02c'
        elif row['TYPE'] == 'Competition':
            color = '#d62728'
        elif row['TYPE'] == 'Neutralism':
            color = '#c7c7c7'
        elif row['TYPE'] == 'Amensalism':
            color = '#d62728'
        else:
            color = '#c7c7c7'
        graph.add_edge(row['A_ID'], row['B_ID'], {'color': color})

    return graph


def plot_graph(graph):
    """ Plot a graph using a circular layout.

    """

    edge_colors = nx.get_edge_attributes(graph, 'color')
    node_colors = nx.get_node_attributes(graph, 'color')
    nx.draw(graph, with_labels=True, width=1.0,
            edgelist=edge_colors.keys(), edge_color=edge_colors.values(),
            nodelist=node_colors.keys(), node_color=node_colors.values())
    return


def make_d3_source(growth_rates, json_file, similarity=None, correlation=None):
    """ Make the data file for D3 visualization. """

    # @todo Both similarity and correlation must be specified or neither

    # Each node is colored a shade of gray based on the similarity of
    # the OTU to the corresponding NCBI genome. The second field in the
    # similarity tuple is the NCBI genome ID and the third field is the
    # percent similarity. The group number is translated to a color when
    # displayed in the browser.
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

    link_value = dict()
    if correlation is not None:
        for corr in correlation:
            a_id = similarity.loc[similarity['OTU_ID'] == corr[0]].iloc[0]['GENOME_ID']
            if a_id not in link_value:
                link_value[a_id] = dict()
            b_id = similarity.loc[similarity['OTU_ID'] == corr[1]].iloc[0]['GENOME_ID']
            if b_id not in link_value:
                link_value[b_id] = dict()
            link_value[a_id][b_id] = corr[2]
            link_value[b_id][a_id] = corr[2]

    # Go through the data frame, links need to be in terms of index positions in nodes list.
    nodes = dict()
    node_list = list()
    link_list = list()
    for index, row in growth_rates.iterrows():
        if row['A_ID'] not in nodes:
            try:
                group = node_group[row['A_ID']]
            except KeyError:
                group = 6
            node_list.append({'name': row['A_ID'], 'group': group})
            nodes[row['A_ID']] = len(node_list) - 1
        if row['B_ID'] not in nodes:
            try:
                group = node_group[row['B_ID']]
            except KeyError:
                group = 6
            node_list.append({'name': row['B_ID'], 'group': group})
            nodes[row['B_ID']] = len(node_list) - 1
        interaction = 10
        # Where 0 is neutral, 1 is negative, 2 is positive, 10 is unknown
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

        # value
        if len(link_value) > 0:
            try:
                corr_value = link_value[row['A_ID']][row['B_ID']]
                if corr_value >= 0.99:  # correlation value
                    value = 1
                elif corr_value >= 0.90:
                    value = 2
                elif corr_value >= 0.70:
                    value = 3
                elif corr_value >= 0.50:
                    value = 4
                elif corr_value >= 0.00:
                    value = 5
                elif corr_value >= -0.10:
                    value = 6
                elif corr_value >= -0.50:
                    value = 7
                elif corr_value >= -0.70:
                    value = 8
                else:
                    value = 9
            except KeyError:
                value = 5
        else:
            value = 5

        link_list.append({'source': nodes[row['A_ID']], 'target': nodes[row['B_ID']],
                          'interaction': interaction, 'value': value})
    graph_data = {'nodes': node_list, 'links': link_list}
    json.dump(graph_data, open(json_file, 'w'))
    return
