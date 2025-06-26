from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Label
from textual_plotext import PlotextPlot
from asyncio import create_subprocess_exec
import asyncio

GET_PKTS = "sudo /home/andrea/onic-driver/utility/ioctl -c 3 -w 1"
GET_BATCH_SIZE = "sudo /home/andrea/onic-driver/utility/ioctl -c 10"

MAX_PLOT_POINTS = 30  # Number of points to display in the plot

previous_batch_size = 4
change_batch_size = [(0, 0)] * MAX_PLOT_POINTS  # Initialize with (0, 0) to indicate no change


BATCH_LINE_COLOR = ["red", "green", "orange"]

class LivePacketsApp(App[None]):
    CSS = "Screen { align: center middle; }"

    def compose(self) -> ComposeResult:
        # yield Header(show_clock=True)
        with Container(id="main-container"):
            yield PlotextPlot(id="plot")

    async def on_mount(self) -> None:
        plot = self.query_one(PlotextPlot)
        plot.plt.title("Throughput Monitor")
        plot.plt.xlabel("Time (s)")
        plot.plt.ylabel("Packets/s (in millions)")

        self.data = [0.0] * MAX_PLOT_POINTS
        self.set_interval(1, self.update_plot)

    async def update_plot(self) -> None:
        global previous_batch_size, change_batch_size
        proc_n_pkts = await create_subprocess_exec(
            *GET_PKTS.split(),
            stdout=asyncio.subprocess.PIPE,
        )

        proc_batch_size = await create_subprocess_exec(
            *GET_BATCH_SIZE.split(),
            stdout=asyncio.subprocess.PIPE,
        )

        # retrieve number of packets
        n_pkts = await proc_n_pkts.stdout.readline()
        if not n_pkts:
            return
        try:
            val = int("".join(filter(str.isdigit, n_pkts.decode())))
        except ValueError:
            val = 0

        # retrieve batch size
        batch_size = await proc_batch_size.stdout.readline()
        if not batch_size:
            return
        try:
            batch_size = int("".join(filter(str.isdigit, batch_size.decode())))
        except ValueError:
            batch_size = 1

        val_millions = round(val / 1_000_000, 2)
        self.data.append(val_millions)

        if len(self.data) > MAX_PLOT_POINTS:
            self.data = self.data[-MAX_PLOT_POINTS:]
            change_batch_size = change_batch_size[-MAX_PLOT_POINTS:]

        plot = self.query_one("#plot", PlotextPlot)
        plot.plt.clear_data()
        plot.plt.plot(self.data, marker="dot", color="blue", label="Packets")

        if any(change_batch_size):
            for i in range(len(change_batch_size)):
                if change_batch_size[i][0] != 0:
                    plot.plt.vline(coordinate=i, color=BATCH_LINE_COLOR[change_batch_size[i][1] - 2] , xside="right")
                    plot.plt.text(
                        f"{change_batch_size[i][0]} ⟶ {change_batch_size[i][1]}",
                        x=i,
                        y=43,
                        color=BATCH_LINE_COLOR[change_batch_size[i][1] - 2],
                        style="bold",
                    )
        if previous_batch_size != batch_size:
            change_batch_size.append((previous_batch_size, batch_size))
            previous_batch_size = batch_size
        else:
            change_batch_size.append((0, 0))

        max_val = 45
        nice_max = ((max_val * 1.1) // 1) + 1  # Arrotonda verso l’alto
        step = round(nice_max / 5, 2)  # 5 intervalli = 6 ticks

        yticks = [round(i * step, 2) for i in range(6)]
        formatted_yticks = [f"{y:.1f}M" if y > 0 else "0" for y in yticks]

        plot.plt.ylim(0, yticks[-1])  # Questo è essenziale
        plot.plt.yticks(yticks, formatted_yticks)
        plot.plt.xticks([])

        label = f"{self.data[-1]}M Packets/s \n Batch Size: {batch_size}"

        plot.plt.text(
            label,
            x=MAX_PLOT_POINTS - 2,
            y=3,
            color="white",
            style="bold",
        )

        plot.refresh()


if __name__ == "__main__":
    LivePacketsApp().run()
