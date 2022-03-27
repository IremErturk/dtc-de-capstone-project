import pandas as pd
import plotly.express as px
from pyvis.network import Network

column_mappings = {
    # reactions
    "msg_owner": "target",
    "msg_reactor": "source",
    # thread_replies
    "parent_user_id": "target",
    "user": "source",
}


def transform_df(df, intrest_columns):
    df = df[intrest_columns]
    columns = dict((col, column_mappings[col]) for col in intrest_columns)
    df = df.rename(columns=columns)  # size:5043

    # Remove self actions or actions to own messages
    df = df.drop(df[df.target == df.source].index)

    # Find the weights: In oder word #number of connections from source->target
    df = df.groupby(["target", "source"]).size().reset_index(name="weight")

    # Drop rows which has weight less than 10
    df = df.drop(df[df.weight < 10].index)

    return df  # with only source, target


def combine_with_users_data(df, df_users):
    df = pd.merge(df, df_users, how="left", left_on=["target"], right_on=["id"])
    df = df.rename(
        columns={
            "id": "target_id",
            "name": "target_name",
            "real_name": "target_real_name",
        }
    )
    df = pd.merge(df, df_users, how="left", left_on=["source"], right_on=["id"])
    df = df.rename(
        columns={
            "id": "source_id",
            "name": "source_name",
            "real_name": "source_real_name",
        }
    )
    df = df.drop(
        columns=[
            "target_id",
            "source_id",
            "target_real_name",
            "source_real_name",
        ]
    )
    return df  # source, target, weight, source_name, target_name


def connection_distribution(df, name):
    distribution = df.groupby(["weight"]).size().reset_index(name="distribution")

    # drop weight 1 (todo)
    # drop_i = distribution[(distribution.weight == 1)].index
    # distribution = distribution.drop(drop_i)

    fig = px.bar(distribution, x="weight", y="distribution", title="Distribution of #connections on weights")
    # fig.show()
    fig.write_html(f"./images/distribution_{name}.html")


def build_nodes(df, network):
    ids = {}
    source_names = list(df["source_name"].unique())
    target_names = list(df["target_name"].unique())
    unique_nodes = list(set(source_names + target_names))
    for i, node in enumerate(unique_nodes):
        ids[node] = i
        network.add_node(i, label=node)
    return network, unique_nodes, ids


def build_edges(df, network, node_labels, ids):
    # edges = []
    for i, source_node in enumerate(node_labels):
        temp = df.loc[df["source_name"] == source_node]
        temp = temp[["target_name", "weight"]]
        targets_weights = [tuple(x) for x in temp.to_numpy()]
        for tw in targets_weights:
            target_node, weight = ids[tw[0]], tw[1]
            # edge = i, target_node, weight, str(weight)
            network.add_edge(
                i, target_node, value=weight, title=str(weight)
            )  # weight 42
            # edges.append(edge)
    # network.add_edges(edges)
    return network


def build_pyvis_network(df, name):
    network = Network(height="500px", width="900px", directed=True)
    network.barnes_hut(spring_strength=0.006)

    (
        network,
        node_labels,
        label_2_id_mapping,
    ) = build_nodes(df=df, network=network)
    network = build_edges(df, network, node_labels, label_2_id_mapping)

    network.repulsion(node_distance=200, spring_length=200)
    network.show_buttons(filter_=True)
    network.save_graph(f"./images/pyvis_network_{name}.html")


def populate_network(name, df_users, df, intrest_columns):
    df = transform_df(df, intrest_columns)
    df = combine_with_users_data(df, df_users)

    # for analysis perspective
    connection_distribution(df, name)

    build_pyvis_network(df, name)
