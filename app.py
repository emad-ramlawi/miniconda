import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_design_kit as ddk
import dash_snapshots
import plotly.express as px

import datetime
import os
import redis

app = dash.Dash(__name__)
server = app.server
app.title = "SEC Sample 3"

# Save snapshots to Postgres on Dash Enterprise or SQLite locally
# Note - if you are saving to Postgres, you'll need to create & link a Postgres database on Dash Enterprise
# os.environ["SNAPSHOT_DATABASE_URL"] = os.environ.get(
#     "DATABASE_URL", "sqlite:///walkthrough_1.db"
# )
# If you want to save to Redis instead, write:
os.environ["REDIS_URL"] = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379")

snap = dash_snapshots.DashSnapshots(app)
celery_instance = snap.celery_instance
redis_instance = redis.StrictRedis.from_url(
    os.environ.get("REDIS_URL", "redis://127.0.0.1:6379"), decode_responses=True
)

app.config["suppress_callback_exceptions"] = True


def info_card(url, snapshots=False):
    snap_line = "\n"
    if snapshots:
        snap_line = "1. Run a celery worker using the command from the Procfile.\n"

    return ddk.Card(
        children=[
            ddk.CardHeader(title="To use this app as a template"),
            dcc.Markdown(
                """The steps for deploying this sample app can be found [here]("https://gitlab.midas.maystreet.com/markeyp/midas-user-documenation/-blob/master/Plotly-Dash%20Visualization%20Tools/README.md").
Make sure to use the correct app name."""
            ),
        ]
    )


def header():
    menu = [
        dcc.Link("Home", href=app.get_relative_path("/")),
        dcc.Link("Archive", href=app.get_relative_path("/archive")),
    ]

    return ddk.Header(
        style={"height": "80px", "margin-bottom": "0%"},
        children=[
            ddk.Logo(src=app.get_asset_url("logo.png"), style={"height": "60px"}),
            ddk.Title("PDF Report"),
            ddk.Menu(children=menu),
        ],
    )


app.layout = ddk.App(
    [
        header(),
        info_card(
            "https://gitlab.midas.maystreet.com/plotly-apps/sec-sample-3",
            snapshots=True,
        ),
        ddk.Block(id="content"),
        dcc.Location(id="url", refresh=False),
    ]
)


def gen_report(city, time):
    return ddk.Report(
        display_page_numbers=True,
        children=[
            ddk.Page(
                children=[
                    html.Div(
                        f"Weekly Report - {city}",
                        style={"marginTop": "2in", "fontSize": "28px"},
                    ),
                    html.H4(time.strftime("%A, %B %-d, %Y")),
                    ddk.PageFooter("Not for redistribution"),
                ],
                style={"backgroundColor": "var(--accent)", "color": "white"},
            ),
            ddk.Page(
                [
                    html.H1(f"Quarterly Earnings - {city}"),
                    ddk.Block(
                        width=50,
                        margin=5,
                        children=[
                            ddk.Graph(
                                figure=px.scatter(ddk.datasets.bubble(), x="x1", y="y1")
                            )
                        ],
                    ),
                    ddk.Block(
                        width=50,
                        margin=5,
                        children=[
                            ddk.Graph(
                                figure=px.scatter(ddk.datasets.bubble(), x="x2", y="y2")
                            )
                        ],
                    ),
                    html.H2(f"Expected Returns - {city}"),
                    ddk.Block(
                        width=50,
                        margin=5,
                        children=[
                            ddk.Graph(
                                figure=px.scatter(ddk.datasets.bubble(), x="x2", y="y2")
                            )
                        ],
                    ),
                    ddk.Block(
                        width=50,
                        margin=5,
                        children=[
                            ddk.Graph(
                                figure=px.scatter(ddk.datasets.bubble(), x="x1", y="y1")
                            )
                        ],
                    ),
                    ddk.PageFooter(
                        """
                                    Past Performance Is No Guarantee of Future Results.
                                """
                    ),
                ]
            ),
            ddk.Page(
                [
                    html.H1(f"Historical Performance - {city}"),
                    html.P(
                        """
                    At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis
                    praesentium voluptatum deleniti atque corrupti quos dolores et quas.
                    """
                        * 6,
                        style={"columnCount": 3},
                    ),
                    ddk.Block(
                        children=[
                            ddk.Graph(
                                figure={
                                    "data": [
                                        {
                                            "x": ddk.datasets.timeseries()["x1"],
                                            "y": ddk.datasets.timeseries()["y1"],
                                            "name": "Model 1",
                                        },
                                        {
                                            "x": ddk.datasets.timeseries()["x2"],
                                            "y": ddk.datasets.timeseries()["y2"],
                                            "name": "Model 2",
                                        },
                                    ]
                                }
                            )
                        ]
                    ),
                    ddk.PageFooter("DO NOT DISTRIBUTE"),
                ]
            ),
        ],
    )


def main_view():
    return ddk.Block(
        [
            ddk.Block(
                [
                    ddk.ControlCard(
                        [
                            ddk.ControlItem(
                                dcc.Dropdown(
                                    options=[
                                        {"label": i, "value": i}
                                        for i in ["NYC", "Montreal", "LA"]
                                    ],
                                    value="LA",
                                    id="cities",
                                ),
                            ),
                            ddk.ControlItem(
                                html.Button(id="run", children="Run", n_clicks=0)
                            ),
                        ],
                    ),
                    ddk.ControlCard(
                        [
                            ddk.ControlItem(
                                html.Button(
                                    "Take Snapshot", id="take-snapshot", n_clicks=0
                                )
                            ),
                            ddk.ControlItem(html.Div(id="take-snapshot-status")),
                        ],
                    ),
                ],
                width=25,
            ),
            # This is the container that we will "snapshot"
            ddk.Block(
                id="snapshot-container",
                style=dict(overflowY="scroll", height=700, width=900),
                children=gen_report("LA", datetime.datetime.now()),
            ),
        ]
    )


# As we've seen before, wrapping functions code with two decorators
# `@celery_instance.task` &
# `@snap.snapshot_async_wrapper(save_pdf=True)`
# will save the snapshot and save a PDF in a separate process managed
# by celery.
# The wrapped function (in this case `save_snapshot`) needs to return
# a Dash component - this component will be saved by the
# `@snap.snapshot_async_wrapper()` decorator.
# In this example, `save_snapshot` is really simple: it just returns the
# same dash component that was passed to it. We write this as a separate
# function just in order to generate a PDF of the snapshot.
# While this function itself won't take very long to run, saving the PDF
# can take up to 30 seconds, which is why we always generate the PDFs
# asynchronously.
@celery_instance.task
@snap.snapshot_async_wrapper(save_pdf=True)
def save_snapshot(children):
    return children


@app.callback(
    Output("take-snapshot-status", "children"),
    [Input("take-snapshot", "n_clicks")],
    [State("snapshot-container", "children")],
)
def take_snapshot(n_clicks, children):
    if n_clicks > 0:
        # as before - pass in the name of the function and that
        # function's arguments.
        # `snapshot_save_async` will pass the function over to
        # the Celery process and then immediately return.
        snap.snapshot_save_async(save_snapshot, children)
        return "Saved"


@app.callback(
    Output("snapshot-container", "children"),
    [Input("run", "n_clicks_timestamp")],
    [State("cities", "value")],
)
def update_report(n_clicks_timestamp, city):
    # When the "live view" of the app loads,
    # the button will not have been
    # clicked and `n_clicks_timestamp` will be
    # initialized as `None`
    if n_clicks_timestamp is not None:
        return gen_report(city, datetime.datetime.now())
    raise dash.exceptions.PreventUpdate


def archive():
    return html.Div(
        [
            snap.ArchiveTable(),
        ]
    )


def view_snapshot(snapshot_id):
    snapshot_content = snap.snapshot_get(snapshot_id)
    # Return the snapshot directly or include snapshot
    # in some other content
    return html.Div(
        [
            html.Div("Loading snapshot {}".format(snapshot_id)),
            html.Div(snapshot_content),
        ]
    )


@app.callback(Output("content", "children"), [Input("url", "pathname")])
def display_content(pathname):
    page_name = app.strip_relative_path(pathname)
    if not page_name:
        return main_view()
    elif page_name == "archive":
        return archive()
    elif page_name.startswith("snapshot-"):
        return view_snapshot(page_name)
    else:
        return "404"


if __name__ == "__main__":
    app.run_server(debug=True)
