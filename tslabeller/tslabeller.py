import numpy as np

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class TimeSeriesLabellerWindow:
    def __init__(self):
        self.is_data_loaded = False
        self.data = None
        self.labels = None
        self.min_value = 0
        self.max_value = 0

        self.first_point = True
        self.start_line = None
        self.temp_coords = []
        self.colors = {0: 'blue', 1: 'red', 2: 'green', 3: 'magenta', 4: 'orange', 5: 'cyan'}
        self.cb_classes = ["-1 (None)", "0 (Blue)", "1 (Red)", "2 (Green)", "3 (Magenta)", "4 (Orange)", "5 (Cyan)"]

        self.w = 1500
        self.h = 850
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.title("TimeSeriesLabellerGUI")
        self.root.protocol('WM_DELETE_WINDOW', self._main_window_was_closed)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(str(self.w) + "x" + str(self.h) + "+"
                           + str(int((screen_width - self.w) / 2)) + "+" + str(int((screen_height - self.h) / 2)))

        self.lbl_y_min = ttk.Label(text="Classes #")
        self.lbl_y_min.place(x=10, y=10)

        self.class_var = tk.StringVar(value=self.cb_classes[0])
        self.combobox = ttk.Combobox(values=self.cb_classes, textvariable=self.class_var)
        self.combobox.place(x=10, y=30)

        self.btn_save_labels = ttk.Button(text="Save labels", command=self._save_labels)
        self.btn_save_labels.place(x=200, y=20)

        self.fig, self.ax = plt.subplots(figsize=(15, 7))
        self.fig.canvas.mpl_connect('button_press_event', self._midmouseclick)
        self.frame_plot = tk.Frame(self.root)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_plot)
        self.canvas.get_tk_widget().pack()
        self.canvas.draw()
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.frame_plot, pack_toolbar=True)
        self.toolbar.pan()
        self.toolbar.update()
        self.frame_plot.place(x=0, y=60)

        style = ttk.Style(self.root)
        style.theme_use('clam')

    def _main_window_was_closed(self):
        plt.close(self.fig)
        self.root.destroy()

    def _midmouseclick(self, event):
        if self.is_data_loaded:
            if event.button == 2:
                x = int(event.xdata)
                print(f'x = {x}')
                x = 0 if x < 0 else x
                x = len(self.data) if x > len(self.data) else x
                self._update_labels(x)

    def _update_labels(self, x_coordinate: int):
        """
        Update labels list after two clicks on time series plot.
        :param x_coordinate: Coordinate X of click place
        """
        if self.first_point:
            self.temp_coords.append(x_coordinate)
            self.first_point = False
            self.start_line = self.ax.axvline(x_coordinate, color='r', linestyle='--')
            self._update_plot()
        else:
            self.temp_coords.append(x_coordinate)
            class_label = int(self.class_var.get().split(' ')[0])
            self.labels[self.temp_coords[0]:self.temp_coords[1]] = class_label
            self.start_line.remove()
            self._update_plot()
            self.temp_coords = []
            self.first_point = True

    @staticmethod
    def _get_coords_for_classes(labels: np.ndarray) -> tuple[list, list]:
        """
        Returns two arrays that contain the coordinates of the beginning and end of the time series samples classes.
        :param labels: Array with labels for each sample in time series
        :return: Coordinates of the beginning of classes, classes labels
        """
        coords = []
        classes = []
        coords.append(0)
        classes.append(labels[0])
        i = 1
        while i < len(labels):
            if labels[i] != classes[-1]:
                coords.append(i)
                classes.append(labels[i])
            i += 1
        coords.append(i - 1)
        classes.append(labels[i - 1])
        return coords, classes

    def _update_plot(self):
        xlim, ylim = self.ax.get_xlim(), self.ax.get_ylim()
        for p in reversed(self.ax.patches):
            p.remove()
        coords, classes = self._get_coords_for_classes(self.labels)
        print(f"channel_coords: {coords}")
        print(f"channel_classes: {classes}")

        for j in range(len(coords) - 1):
            if classes[j] != -1:
                rectangle = Rectangle(xy=(coords[j], self.min_value),
                                      width=coords[j + 1] - coords[j],
                                      height=self.max_value - self.min_value,
                                      facecolor=self.colors[classes[j]],
                                      alpha=0.3)
                self.ax.add_patch(rectangle)

        self.ax.set_xlim(left=xlim[0], right=xlim[1])
        self.ax.set_ylim(bottom=ylim[0], top=ylim[1])
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def _save_labels(self):
        if self.labels is not None:
            types = [("npy", "*.npy")]
            file = filedialog.asksaveasfile(title="Save Labels",
                                            initialdir=".",
                                            defaultextension=".npy",
                                            filetypes=types)
            if file:
                fname = file.name
                np.save(fname, self.labels)
                file.close()

    def load_data(self, data: np.ndarray):
        self.data = data
        self.max_value = np.max(data)
        self.min_value = np.min(data)
        self.labels = np.full((data.shape[0],), -1)
        self.is_data_loaded = True

    def get_ax(self):
        return self.ax


if __name__ == "__main__":
    tsl = TimeSeriesLabellerWindow()
    ax = tsl.get_ax()

    main_array = np.random.rand(500)
    additional_array = np.sin(2 * np.pi * np.linspace(0, 500, 500)) / 2 + 0.5
    ax.plot(main_array, label="rand", color="blue")
    ax.plot(additional_array, label="sin", color="red")
    ax.legend()

    tsl.load_data(main_array)
    tsl.root.mainloop()
