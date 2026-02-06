"""Small common widgets used accross the application."""

from ipywidgets import HTML, HBox, Label, Layout


class LoadingWidget(HBox):
    """Widget for displaying a loading spinner."""

    def __init__(self, message="Loading", **kwargs):
        super().__init__(
            children=[
                Label(message),
                HTML(
                    value="<i class='fa fa-spinner fa-spin fa-2x fa-fw'/>",
                    layout=Layout(margin="12px 0 6px"),
                ),
            ],
            layout=Layout(
                justify_content="center",
                align_items="center",
                **kwargs.pop("layout", {}),
            ),
            **kwargs,
        )
        self.add_class("loading")
