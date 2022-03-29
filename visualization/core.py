import plotly.express as px
import plotly.graph_objects as go


def create_messages_bar_chart(root_messages, thead_replies):
    fig = px.histogram(root_messages, x="date", y="events", histfunc="avg", title="Histogram on Date Axes")
    fig.update_traces(xbins_size="M1")
    fig.update_xaxes(showgrid=True, dtick="M1", tickformat="%b\n%Y")
    fig.update_xaxes(hoverformat="%d-%m-%Y")
    fig.update_layout(bargap=0.10)
    fig.add_trace(go.Scatter(mode="markers", x=root_messages["date"], y=root_messages["events"], name="messages_daily",
                            hovertemplate='%{x} <br> Events: %{y}'))
    fig.add_trace(go.Scatter(mode="markers", x=thead_replies["date"], y=thead_replies["events"], name="thread_replies_daily",
                            hovertemplate='%{x} <br> Events: %{y}'))
    
    fig.write_html(f"./images/messages_counts.html")
    print(f"The figure for message creation Overtime is created ....")



def reaction_hotness(reactions):
    reactions_counts = reactions.groupby(['name']).size().reset_index(name='count') 
    reactions_counts = reactions_counts.sort_values(by=['count'], ascending=False)

    fig = px.bar(reactions_counts.head(10), x="name", y="count", title="Most Popular 10 Emojis")
    fig.write_html(f"./images/most_used_reactions.html")
    print(f"The figure for most used 10 reactions is created ....")



