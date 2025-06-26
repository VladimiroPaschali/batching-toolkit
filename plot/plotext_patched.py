from __future__ import annotations
from typing import Literal, List, Tuple, Optional

from rich.text import Text
from textual.app import RenderResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.color import Color

from .plot import Plot, PlotextThemeName, _rgbify_theme, _sequence
from plotext._dict import themes as _themes


class PlotextPlot(Widget):
    """A Plotext plot display widget **with optional annotations**.

    This widget wraps a :class:`plotext.Plot` instance and adds a simple, high‑level
    annotation API so that you can place text labels at data‑space positions on the
    canvas.

    Example
    -------
    ```python
    plot_widget = PlotextPlot()
    ax = plot_widget.plt
    ax.plot(x, y)
    plot_widget.annotate(5, 2.4, "local max →")
    ```
    """

    DEFAULT_CSS = """
    PlotextPlot {
        width: 1fr;
        height: 1fr;
    }
    """

    # ---------------------------------------------------------------------
    # Public reactive attributes
    # ---------------------------------------------------------------------

    theme: reactive[Literal["auto"] | PlotextThemeName] = reactive("auto")
    """The theme to use for the plot.

    If set to ``"auto"`` the theme will be dynamically generated based on the
    current theme of the Textual app.

    Note that this will just alter the background and foreground colors of the
    plot to match the current Textual theme, not the colors of the plotted graph.

    If set to a specific Plotext theme name, that theme will be used.
    """

    # ---------------------------------------------------------------------
    # Construction
    # ---------------------------------------------------------------------

    def __init__(
        self,
        *,
        name: str | None = None,
        id: str | None = None,  # pylint:disable=redefined-builtin
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialise the Plotext plot widget.

        Parameters
        ----------
        name:
            The name of the Plotext plot widget.
        id:
            The ID of the Plotext plot widget in the DOM.
        classes:
            The CSS classes of the Plotext plot widget.
        disabled:
            Whether the Plotext plot widget is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._plot: Plot = Plot()

        # Keep track of annotations as a list of tuples so we can re‑apply them
        # on every render without accumulating duplicates inside the underlying
        # Plot object.
        self._annotations: List[Tuple[float, float, str, Optional[str]]] = []

    # ---------------------------------------------------------------------
    # Life‑cycle hooks
    # ---------------------------------------------------------------------

    def on_mount(self) -> None:
        """Set up the plot and register to theme change events."""
        # Subscribe to theme‑changed signals so that we can regenerate the
        # background/foreground colours when the surrounding Textual theme
        # changes.
        self.app.theme_changed_signal.subscribe(
            self, lambda theme: self._register_theme(theme.name)
        )
        self._register_theme(self.app.theme)

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------

    @property
    def plt(self) -> Plot:
        """Return the wrapped :class:`plotext.Plot` instance.

        Whereas normally Plotext‑using code would do something like::

            import plotext as plt
            plt.plot(...)

        you should instead use this ``plt`` property in place of the module‑level
        ``plotext`` import so that everything is routed through the widget's
        internal state.
        """
        return self._plot

    # --------------------------- Annotation API ---------------------------

    def annotate(
        self,
        x: float | int,
        y: float | int,
        label: str,
        *,
        color: str | None = None,
    ) -> None:
        """Add a text annotation at data coordinates *(x, y)*.

        Parameters
        ----------
        x, y:
            The data‑space coordinates at which to place the annotation.
        label:
            The text label to draw.
        color:
            Optional colour name (any value accepted by *plotext*) for the
            annotation text. If *None*, Plotext's default is used.
        """
        self._annotations.append((x, y, label, color))
        self.refresh(layout=False)

    def clear_annotations(self) -> None:
        """Remove **all** stored annotations and refresh the widget."""
        self._annotations.clear()
        # Plotext stores text annotations internally, so we need to clear them
        # from the underlying plot as well; otherwise re‑rendering would show
        # stale annotations.
        if hasattr(self._plot, "clear"):
            # Newer versions of plotext expose .clear(); fall back gracefully
            # if not available.
            try:
                self._plot.clear("text")  # type: ignore[arg‑type]
            except Exception:  # pragma: no cover  pylint: disable=broad‑except
                pass
        self.refresh(layout=False)

    # ---------------------------------------------------------------------
    # Rendering
    # ---------------------------------------------------------------------

    def render(self) -> RenderResult:
        """Render the plot to a Rich :class:`~rich.text.Text` object."""
        # Ensure the underlying plot matches our current geometry before drawing.
        self._plot.plotsize(self.size.width, self.size.height)
        # Belt‑and‑braces call (see link in original comment for context).
        self._plot._set_size(self.size.width, self.size.height)  # pylint:disable=protected‑access

        # Apply theme (auto or explicit).
        plotext_theme_name = self._get_plotext_theme_name(self.app.theme)
        self._plot.theme(plotext_theme_name)

        # ------------------------------------------------------------------
        # Apply stored annotations *every* frame. We must re‑add them because
        # we call ``self._plot.clear("text")`` in ``clear_annotations()`` which
        # wipes them from the underlying Plot object.
        # ------------------------------------------------------------------
        if self._annotations:
            # Remove any previously added annotations from the underlying plot to
            # avoid duplicates. Unfortunately the public Plotext API does not
            # provide a fine‑grained way to do this, so we resort to a protected
            # member if present.
            if hasattr(self._plot, "_figure") and hasattr(self._plot._figure, "texts"):
                self._plot._figure.texts.clear()  # type: ignore[attr‑defined]

            for x, y, label, colour in self._annotations:
            # Plotext's API expects the *text* first, *then* x and y coordinates.
                if colour is None:
                    self._plot.text(label, x, y)
                else:
                    self._plot.text(label, x, y, color=colour)

        # Build plot and wrap into Rich.Text
        return Text.from_ansi(self._plot.build())

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------

    def _register_theme(self, app_theme_name: str) -> None:
        """Register (or re‑register) a Textual theme with Plotext if required."""
        # If we're not in auto‑theme mode there's nothing to do.
        if self.theme != "auto":
            return

        plotext_theme_name = self._get_plotext_theme_name(app_theme_name)
        app_theme_variables = self.app.theme_variables

        # Only (re)register if we haven't done so already.
        if plotext_theme_name not in _themes:
            _themes[plotext_theme_name] = _rgbify_theme(
                Color.parse(app_theme_variables.get("surface")).rgb,
                Color.parse(app_theme_variables.get("surface")).rgb,
                Color.parse(app_theme_variables.get("foreground")).rgb,
                "default",
                _sequence,
            )
        self.refresh()

    def _get_plotext_theme_name(self, app_theme_name: str) -> str:
        """Return the Plotext theme identifier to use for the current frame."""
        if self.theme == "auto":
            return f"textual-auto-{app_theme_name}"
        else:
            # ``self.theme`` is already a valid Plotext theme identifier.
            return self.theme
