import os.path

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
        self.x = None
        self.data = None
        self.labels = None
        self.min_value = 0
        self.max_value = 0

        self.first_point = True
        self.start_line = None
        self.temp_coords = []
        self.colors = {-1: 'black', 0: 'blue', 1: 'red', 2: 'green', 3: 'magenta', 4: 'orange', 5: 'cyan'}
        self.cb_classes = ["-1 (None)", "0 (Blue)", "1 (Red)", "2 (Green)", "3 (Magenta)", "4 (Orange)", "5 (Cyan)"]

        self.default_save_path = os.path.join(".", "")

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

    @staticmethod
    def _find_nearest(array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return array[idx], idx

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
        return coords, classes

    def _midmouseclick(self, event):
        if self.is_data_loaded:
            if event.button == 2:
                if event.xdata is not None:
                    x_click = event.xdata
                    x_nearest, x_idx = self._find_nearest(self.x, x_click)
                    # print(f'x_click, x_nearest[x_idx] = {x_click}, {x_nearest}[{x_idx}]')
                    self._update_labels(x_idx)

    def _update_labels(self, x_idx: int):
        """
        Update labels list after two clicks on time series plot.
        :param x_idx: Index of click nearest coordinate from X array
        """
        class_label = int(self.class_var.get().split(' ')[0])
        if self.first_point:
            self.temp_coords.append(x_idx)
            self.first_point = False
            self.start_line = self.ax.axvline(self.x[x_idx], color=self.colors[class_label], linestyle='--')
            self._update_plot()
        else:
            self.temp_coords.append(x_idx)
            self.temp_coords.sort()
            self.labels[self.temp_coords[0]:self.temp_coords[1] + 1] = class_label
            # print(self.labels)
            self.start_line.remove()
            self._update_plot()
            self.temp_coords = []
            self.first_point = True

    def _update_plot(self):
        xlim, ylim = self.ax.get_xlim(), self.ax.get_ylim()
        for p in reversed(self.ax.patches):
            p.remove()
        coords, classes = self._get_coords_for_classes(self.labels)
        # print(f"channel_coords: {coords}")
        # print(f"channel_classes: {classes}")

        for j in range(len(coords)):
            if classes[j] != -1:
                end_point = len(self.labels) - 1
                if j != len(coords) - 1:
                    end_point = coords[j + 1] - 1
                # print(f"{coords[j]} - {end_point}")

                class_rect_shift_start = 0
                if coords[j] == 0:
                    class_rect_shift_start = 0.5 * (self.x[coords[j] + 1] - self.x[coords[j]])
                else:
                    class_rect_shift_start = 0.5 * (self.x[coords[j]] - self.x[coords[j] - 1])
                class_rect_shift_end = 0
                if end_point == len(self.labels) - 1:
                    class_rect_shift_end = 0.5 * (self.x[end_point] - self.x[end_point - 1])
                else:
                    class_rect_shift_end = 0.5 * (self.x[end_point + 1] - self.x[end_point])

                rectangle = Rectangle(xy=(self.x[coords[j]] - class_rect_shift_start,
                                          self.min_value),
                                      width=self.x[end_point] - self.x[coords[j]] +
                                            class_rect_shift_start + class_rect_shift_end,
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
            types = [("NumPy file", "*.npy")]
            initialdir = os.path.join(*self.default_save_path.split(os.sep)[:-1])
            initialfile = self.default_save_path.split(os.sep)[-1]
            file = filedialog.asksaveasfile(title="Save Labels",
                                            initialdir=initialdir,
                                            initialfile=initialfile,
                                            defaultextension=".npy",
                                            filetypes=types)
            if file:
                fname = file.name
                np.save(fname, self.labels)
                file.close()

    def load_target_data(self, x: np.ndarray, data: np.ndarray):
        self.x = x
        self.data = data
        self.max_value = np.max(data)
        self.min_value = np.min(data)
        self.labels = np.full((x.shape[0],), -1)
        self.is_data_loaded = True

    def get_ax(self):
        return self.ax

    def show(self):
        self.root.mainloop()

    def set_default_save_path(self, path):
        self.default_save_path = path


if __name__ == "__main__":
    tslw = TimeSeriesLabellerWindow()
    ax = tslw.get_ax()

    x_for_labelling = np.linspace(0, 16.3, 15) + 7.5
    data_for_labelling = np.random.rand(15)

    additional_x = np.linspace(0, 30, 30)
    additional_data = np.sin(2 * np.pi * additional_x) / 2 + 0.5

    ax.plot(additional_x, additional_data, label="sin", color="red", linestyle="--")
    ax.plot(x_for_labelling, data_for_labelling, label="rand", color="blue", marker='o')
    ax.legend()

    tslw.load_target_data(x_for_labelling, data_for_labelling)
    tslw.show()
