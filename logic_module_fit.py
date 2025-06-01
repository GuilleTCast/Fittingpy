import numpy as np
import matplotlib.pyplot as plt
import datetime

class DataHandler:
    '''
    Class to handle data from a file and generate colors for the lines in the plot.

    Attributes:
    ----------------
        data_file (str): Path to the data file.
        data_txt (numpy.ndarray): Data from the file.
        data_color (dict): Dictionary with the RGB values for the colors of the lines.
        color_palettes (dict): Dictionary with the RGB values for the color palettes.

    Methods:
    ----------------
        load_data(file_path): Load data from a file.
        generate_colors(palette, num_lines): Generate colors for the lines in the plot.
    '''

    def __init__(self):
        self.data_file = None
        self.data_txt = None
        self.data_previous = None
        self.data_color = {}
        self.color_palettes = {}

    def version(self) -> str:
        return 'DataHandler version: 0.0.1'

    def load_file(self, file_path) -> tuple[int, str]:
        '''Load data from a file.
        
        Returns a tuple with:
            header_lines (int): Number of header lines in the file.
            delimiter (str): Delimiter used in the file.
        '''
        delimiter = None
        header_lines = 0

        with open(file_path, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                try:
                    delimiter = ',' if ',' in line else '\t'
                    _ = [float(value) for value in line.split(delimiter)]
                    break
                except ValueError:
                    header_lines += 1

        if delimiter is None:
            raise ValueError('Delimiter not found')
        
        return header_lines, delimiter

    def load_data(self, file_path) -> tuple[int, str]:
        '''Load data from a file.
        
        Returns a tuple with:
            header_lines (int): Number of header lines in the file.
            delimiter (str): Delimiter used in the file.
        '''
        header_lines, delimiter = self.load_file(file_path)

        try:
            self.data_txt = np.loadtxt(file_path, delimiter=delimiter, skiprows=header_lines)
            self.data_file = file_path
        except Exception as e:
            raise ValueError(f'Failed to load data: {e}')
        
        return header_lines, delimiter
    
    def add_data(self, file_path) -> tuple[int, str]:
        '''Add data from a file to the existing data.
        
        Returns a tuple with:
            header_lines (int): Number of header lines in the file.
            delimiter (str): Delimiter used in the file.
        '''

        if self.data_file is None:
            raise ValueError('No data loaded yet')
        
        header_lines, delimiter = self.load_file(file_path)

        try:
            new_data_txt = np.loadtxt(file_path, delimiter=delimiter, skiprows=header_lines)
            self.data_txt = np.concatenate((self.data_txt, new_data_txt[:,1:]), axis=1)
            self.data_file = file_path
        except Exception as e:
            raise ValueError(f'Failed to load data: {e}')
        
        return header_lines, delimiter        

    def generate_colors(self, palette, num_lines) -> None:
        '''Generate colors for the lines in the plot.'''
        palettes = {
            'Red': {'Red': np.linspace(0, 1, num_lines), 'Green': np.zeros(num_lines), 'Blue': np.zeros(num_lines)},
            'Green': {'Red': np.zeros(num_lines), 'Green': np.linspace(0, 1, num_lines), 'Blue': np.zeros(num_lines)},
            'Blue': {'Red': np.zeros(num_lines), 'Green': np.zeros(num_lines), 'Blue': np.linspace(0, 1, num_lines)},
            'Thermometer': {'Red': np.linspace(0, 1, num_lines), 'Green': np.zeros(num_lines), 'Blue': np.linspace(1, 0, num_lines)}
        }
        self.data_color = palettes.get(palette, palettes['Thermometer'])

class PlotHandler:
    '''
    Class to handle the plot and update it with the data.

    Attributes:
    ----------------
        fig (matplotlib.figure.Figure): Figure object.
        ax (matplotlib.axes.Axes): Axes object.
        lines (list): List with the lines in the plot.

    Methods:
    ----------------
        setup_plot(): Set up the plot.
        update_plot(data_txt, offset, colors): Update the plot with the data.
    '''

    def __init__(self):
        self.fig: plt.Figure
        self.ax: plt.Axes
        self.fig, self.ax = plt.subplots()
        self.fig.tight_layout()
        self.lines: plt.Line2D
        self.lines = None
        self.setup_plot()

    def version(self) -> str:
        return 'PlotHandler version: 0.0.1'

    def setup_plot(self):
        '''Set up the plot.'''
        self.ax.invert_xaxis()
        self.ax.set_xlabel(r'Wavenumber (cm$^{-1}$)')
        self.ax.set_ylabel('Optical Depth')
        self.fig.subplots_adjust(left=0.12, right=0.98, top=0.92, bottom=0.12)

    def update_plot(self, data_txt, offset, colors=None):
        '''Update the plot with the data.'''
        self.ax.clear()
        x_data = data_txt[:, 0]
        y_data = np.zeros([data_txt.shape[0], data_txt.shape[1] - 1])

        for i in range(0, y_data.shape[1]):
            y_data[:, i] = np.array(data_txt[:, i + 1]) - data_txt[1, i + 1] + offset * i

        self.lines = self.ax.plot(x_data, y_data)
        if colors:
            for i, line in enumerate(self.lines):
                color_line = (colors['Red'][i], colors['Green'][i], colors['Blue'][i])
                line.set_color(color_line)

        self.ax.set_title(title)
        self.ax.invert_xaxis()
        self.ax.set_xlabel(r'Wavenumber (cm$^{-1}$)')
        self.ax.set_ylabel('Optical Depth')
        self.fig.canvas.draw()

    def update_plot(self, data_txt, offset, colors=None, *args, **kwargs):
        '''Update the plot with the data.'''

        x_min, x_max = self.ax.get_xlim()
        y_min, y_max = self.ax.get_ylim()

        self.plot_data(data_txt, offset, colors)

        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        self.fig.canvas.draw()

        

class Logger:
    '''
    Class to log messages to a file.

    Attributes:
    ----------------
        log_file (str): Path to the log file.

    Methods:
    ----------------
        log(message): Log a message to the file.
    '''

    def __init__(self, log_file='error.log'):
        self.log_file = log_file

    def version(self) -> str:
        return 'Logger version: 0.0.1'

    def log(self, message):
        '''Log a message to the file.'''
        with open(self.log_file, 'a') as f:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f'{timestamp}: {message}\n')

    def log_wo_stamp(self, message):
        '''Log a message to the file without timestamp.'''
        with open(self.log_file, 'a') as f:
            f.write(f'{message}\n')
        
    def log_start(self):
        '''Log the start of the application.'''
        self.log_wo_stamp('-' * 100)
        self.log('Application started')

    def log_end(self):
        '''Log the end of the application.'''
        self.log('Application finished')
        self.log_wo_stamp('-' * 100)
