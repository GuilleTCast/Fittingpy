import numpy as np
import matplotlib.pyplot as plt
import datetime
from tkinter import simpledialog

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
        self.data_color = {}
        self.color_palettes = {}
        self.original_data = np.array([])
        self.smooth_data = np.array([])
        self.smooth_original = np.array([])
        self.intensity_units = str()
        self.data_baseline = np.array([])

    def version(self) -> str:
        return 'DataHandler version: 0.1.2'

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
            self.original_data = self.convert_data(self.data_txt)

            self.data_file = file_path
        except Exception as e:
            raise ValueError(f'Failed to load data: {e}')
        
        return header_lines, delimiter
    
    def add_data(self, file_path) -> tuple[int, str, str]:
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
            new_data_converted = self.convert_data(new_data_txt)
            if new_data_converted.shape[0] != self.original_data.shape[0]:
                raise ValueError('New data has different number of lines than the original data')
            
            self.data_txt = np.column_stack((self.data_txt, new_data_converted[:,1:]))
            self.original_data = np.column_stack((self.original_data, new_data_converted[:,1:]))
            self.data_file = file_path
        except Exception as e:
            raise ValueError(f'Failed to load data: {e}')
        
        return header_lines, delimiter
    
    def convert_data_txt(self, data) -> np.ndarray:
        data_converted = self.convert_data(data)
        return data_converted

    def generate_colors(self, palette, num_lines) -> None:
        '''Generate colors for the lines in the plot.'''
        palettes = {
            'Red': {'Red': np.linspace(0, 1, num_lines), 'Green': np.zeros(num_lines), 'Blue': np.zeros(num_lines)},
            'Green': {'Red': np.zeros(num_lines), 'Green': np.linspace(0, 1, num_lines), 'Blue': np.zeros(num_lines)},
            'Blue': {'Red': np.zeros(num_lines), 'Green': np.zeros(num_lines), 'Blue': np.linspace(0, 1, num_lines)},
            'Thermometer': {'Red': np.linspace(0, 1, num_lines), 'Green': np.zeros(num_lines), 'Blue': np.linspace(1, 0, num_lines)}
        }
        self.data_color = palettes.get(palette, palettes['Thermometer'])

    def convert_data(self, data) -> np.ndarray:
        '''Convert the data to the format needed for the plot.'''
        x_data = np.array(data[:, 0])
        y_data = np.array(data[:, 1:])

        
        factor = 1
        intensity_unit = self.intensity_units.upper()

        if intensity_unit == 'ABSORBANCE':
            # absorbance to optical depth
            factor = np.log(10)
        elif intensity_unit == 'TRANSMITTANCE':
            # transmittance to optical depth
            factor = -np.log(10)
        elif intensity_unit == 'OPTICAL DEPTH':
            # transmittance to optical depth
            factor = 1

        y_data = np.array(y_data) * factor

        print(f'Shape of x_data: {x_data.shape}')
        print(f'Shape of y_data: {y_data.shape}')

        return np.column_stack((x_data, y_data))

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
        self.lines: plt.Line2D
        self.lines = None
        self.setup_plot()

    def version(self) -> str:
        return 'PlotHandler version: 0.0.2'

    def setup_plot(self):
        '''Set up the plot.'''
        self.ax.invert_xaxis()
        self.ax.set_xlabel(r'Wavenumber (cm$^{-1}$)')
        self.ax.set_ylabel('Optical Depth')
        self.fig.subplots_adjust(left=0.12, right=0.98, top=0.92, bottom=0.12)

    def update_plot(self, data_txt, offset, title, colors=None, intensity_units: str='OPTICAL DEPTH'):
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
