from tkinter import *
from tkinter import ttk, filedialog, messagebox, scrolledtext
import numpy as np
from scipy.signal import savgol_filter
from scipy.ndimage import gaussian_filter1d
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from logic_module_fit import DataHandler, PlotHandler, Logger

class FitConfApp:
    '''
    Top level class for the application.

    Attributes:
    ----------------
        master (Tk): Main window.
        data_handler (DataHandler): Data handler object.
        plot_handler (PlotHandler): Plot handler object.
        logger (Logger): Logger object.
        offset_var (DoubleVar): Variable for the offset value.
        color_combobox (ttk.Combobox): Combobox for the color palette.
        canvas (FigureCanvasTkAgg): Canvas for the plot.

    Methods:
    ----------------
        create_widgets: Create the widgets for the main window.
        select_file: Select the file with the data to plot.
        update_plot: Update the plot with the new colors.
        applied_colors: Apply the colors to the plot.

    '''

    def __init__(self, master: Tk):
        self.master = master
        self.master.title('Fittingpy - IR and Decolvolution Tool')
        self.master.iconphoto(True, PhotoImage(file='./icon_material/FitPy_icon_32.png'))
        self.master.protocol('WM_DELETE_WINDOW', self.close_app)

        self.data_handler = DataHandler()
        self.plot_handler = PlotHandler()
        self.logger = Logger()

        self.logger.log_start()
        self.log_version()

        self.offset_var = DoubleVar(value=0)
        self.create_widgets()

    def __version__(self) -> str:
        return 'Fittingpy version: 0.0.1'

    def log_version(self):
        '''Return the version of the Application and DataHandler.'''
        self.logger.log(self.__version__())
        self.logger.log(self.data_handler.version())
        self.logger.log(self.plot_handler.version())
        self.logger.log(self.logger.version())

    def create_widgets(self):
        '''Create the widgets for the main window.'''
        frame = ttk.Frame(self.master)
        frame.pack(side=LEFT, fill=Y, padx=10, pady=10)

        # Data selection
        data_frame = ttk.LabelFrame(frame, text='Data')
        data_frame.pack(fill=X, pady=5)

        self.load_data_btn = ttk.Button(data_frame, text='Select File', command=self.select_file, width=15)
        self.load_data_btn.pack(side=LEFT, padx= 5, pady=5)
        
        self.add_data_btn = ttk.Button(data_frame, text='Add File', command=self.add_file, width=15)
        self.add_data_btn.pack(side=RIGHT, padx= 5, pady=5)
        self.add_data_btn.config(state='disabled')

        # Offset control
        offset_frame = ttk.LabelFrame(frame, text='Offset')
        offset_frame.pack(fill=X, pady=5)

        self.offset_entry = ttk.Entry(offset_frame, textvariable=self.offset_var)
        self.offset_entry.pack(padx=10, pady=10)
        self.offset_entry.config(state='disabled')

        self.offset_var.trace_add('write', self.update_plot)

        # Color palette
        color_frame = ttk.LabelFrame(frame, text='Colors')
        color_frame.pack(fill=X, pady=5)

        self.color_combobox = ttk.Combobox(color_frame, state='readonly')
        self.color_combobox['values'] = ['Red', 'Green', 'Blue', 'Thermometer']
        self.color_combobox.set('Thermometer')
        self.color_combobox.pack(side=LEFT, padx=5, pady=10)
        self.color_combobox.config(state='disabled')

        ttk.Button(color_frame, text='Apply', command=self.apply_colors).pack(side=LEFT, padx=5)

        # Plot frame
        plot_frame = ttk.Frame(self.master)
        plot_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

        self.canvas = FigureCanvasTkAgg(self.plot_handler.fig, plot_frame)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        toolbar.update()

    def apply_baseline(self):
        '''Apply the baseline correction.'''
        x_data = self.data_handler.data_txt[:, 0]
        y_data = self.data_handler.data_txt[:, 1:]

        try:
            baseline_points = [float(i.strip()) for i in self.baseline_points.get('1.0', 'end-1c').strip().split(',')]
            baseline_points.sort(reverse=True)
            self.baseline_points.delete('1.0', 'end')
            self.baseline_points.insert('1.0', ', '.join(map(str, baseline_points)))
            baseline_points.insert(0, x_data[0])
            self.logger.log(f'Baseline points applied: {baseline_points}')

            baseline_index = [np.argmin(np.abs(x_data - point)) for point in baseline_points]
            baseline_values = y_data[baseline_index, :]

            baseline = np.zeros_like(y_data)

            for i in range(baseline_values.shape[1]):
                for index in range(1, len(baseline_index)):
                    elements = baseline_index[index] - baseline_index[index-1]
                    bl_y = np.linspace(baseline_values[index-1, i], baseline_values[index, i], elements)

                    baseline[baseline_index[index - 1]:baseline_index[index], i] = bl_y
                
            # Subtract the baseline from the data
            y_data -= baseline
            self.data_handler.data_txt[:, 1:] = y_data
            self.logger.log('Baseline correction applied successfully.')

            self.update_plot()

        except ValueError as e:
            self.logger.log(f'Error applying baseline: {e}')
            messagebox.showerror('Error', f'Invalid baseline points: {e}')

    def apply_smooth(self):
        '''Apply smoothing to the data.'''

        if self.data_handler.data_previous is None:
            self.data_handler.data_previous = self.data_handler.data_txt.copy()

        case = self.smooth_combobox.get()

        if case == 'None':
            y_data = self.data_handler.data_previous[:, 1:]
            self.logger.log('No smoothing applied.')
        elif case == 'Savitzky-Golay':
            window_size = self.smooth_smt.get()
            if window_size % 2 == 0:
                window_size += 1
            window_size = max(3, window_size)  # Ensure minimum window size
            y_data = savgol_filter(self.data_handler.data_previous[:, 1:], window_size, polyorder=2, axis=0)
            self.logger.log(f'Savitzky-Golay smoothing applied with window size {window_size}.')
        elif case == 'Gaussian':
            sigma = 1.0
            y_data = gaussian_filter1d(self.data_handler.data_previous[:, 1:], sigma=sigma, axis=0)
            self.logger.log(f'Gaussian smoothing applied with sigma {sigma}.')
        elif case == 'Moving Average':
            window_size = self.smooth_smt.get()
            if window_size < 1:
                window_size = 1
            y_data = np.convolve(self.data_handler.data_previous[:, 1:], np.ones(window_size)/window_size, mode='valid')
            # Adjust the shape to match the original data
            y_data = np.pad(y_data, (window_size//2, window_size//2), mode='edge')
            self.logger.log(f'Moving Average smoothing applied with window size {window_size}.')

        self.data_handler.data_txt[:, 1:] = y_data
        self.logger.log('Smoothing applied successfully.')

        self.update_plot()


    def apply_undo(self):
        '''Undo the last operation.'''
        if self.data_handler.data_previous is not None:
            self.data_handler.data_txt = self.data_handler.data_previous.copy()
            self.data_handler.data_previous = None

            self.logger.log('Undo operation applied successfully.')
            self.update_plot()
        else:
            self.logger.log('No previous data to undo.')
            messagebox.showinfo('Undo', 'No previous data to undo.')
        

    def select_file(self):
        '''Select the file with the data to plot.'''
        file_path = filedialog.askopenfilename(filetypes=[('Data files', '*.dat'), ('All files', '*.*')])
        self.file_path = file_path
        if not file_path:
            self.logger.log('No file selected')
            messagebox.showerror('Error', 'No file selected')
            return

        try:
            header_lines, delimiter =self.data_handler.load_data(file_path)
            self.logger.log(f'File loaded: {file_path =}')
            self.logger.log(f'{header_lines=} and {delimiter=}')
            messagebox.showinfo('File Loaded', f'{file_path.split("/")[-1]} loaded successfully.')
            self.add_data_btn.config(state='normal')
            self.offset_entry.config(state='normal')
            self.color_combobox.config(state='normal')
            self.apply_color_btn.config(state='normal')
            num_lines = self.data_handler.data_txt[:, 1:].shape[1]
            self.data_handler.generate_colors(self.color_combobox.get(), num_lines)
            self.start_plot()
        except Exception as e:
            self.logger.log(f'Failed to load file: {file_path =}')
            self.logger.log(f'Error: {e}')
            messagebox.showerror('Error', f'Failed to load file: {e}')

    def update_plot(self, *args):
        '''Update the plot with the new colors.'''
        try:
            offset = self.offset_var.get()
            self.plot_handler.update_plot(self.data_handler.data_txt, offset, self.file_path.split("/")[-1], self.data_handler.data_color)
            self.logger.log(f'Plot updated with offset {offset =}')
        except Exception as e:
            self.logger.log(f'Failed to update plot: {e}')
            messagebox.showerror('Error', f'Failed to update plot: {e}')

    def apply_colors(self):
        '''Apply the colors to the plot.'''
        palette = self.color_combobox.get()
        num_lines = self.data_handler.data_txt[:, 1:].shape[1] if self.data_handler.data_txt is not None else 0
        self.data_handler.generate_colors(palette, num_lines)
        self.update_plot()
        self.logger.log(f'Colors applied: {palette =}')

    def close_app(self):
        '''Clear the graph and closes the application.'''
        self.logger.log_end()
        plt.close('all')  # Cierra todas las figuras de Matplotlib
        self.master.quit()
        self.master.destroy()    # Cierra la ventana de Tkinter
