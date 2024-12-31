from tkinter import *
from tkinter import ttk, filedialog, messagebox
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
        self.master.iconphoto(True, PhotoImage(file='./icon_material/FitPy_icon_128.png'))
        self.master.protocol('WM_DELETE_WINDOW', self.close_app)

        self.data_handler = DataHandler()
        self.plot_handler = PlotHandler()
        self.logger = Logger()

        self.logger.log_start()

        self.offset_var = DoubleVar(value=0)
        self.create_widgets()

    def create_widgets(self):
        '''Create the widgets for the main window.'''
        frame = ttk.Frame(self.master)
        frame.pack(side=LEFT, fill=Y, padx=10, pady=10)

        # Data selection
        data_frame = ttk.LabelFrame(frame, text='Data')
        data_frame.pack(fill=X, pady=5)

        ttk.Button(data_frame, text='Select File', command=self.select_file).pack(pady=5)

        # Offset control
        offset_frame = ttk.LabelFrame(frame, text='Offset')
        offset_frame.pack(fill=X, pady=5)

        ttk.Label(offset_frame, text='Offset:').pack(side=LEFT, padx=5)
        ttk.Entry(offset_frame, textvariable=self.offset_var).pack(side=LEFT, padx=5)

        self.offset_var.trace_add('write', self.update_plot)

        # Color palette
        color_frame = ttk.LabelFrame(frame, text='Colors')
        color_frame.pack(fill=X, pady=5)

        self.color_combobox = ttk.Combobox(color_frame, state='readonly')
        self.color_combobox['values'] = ['Red', 'Green', 'Blue', 'Thermometer']
        self.color_combobox.set('Thermometer')
        self.color_combobox.pack(side=LEFT, padx=5)

        ttk.Button(color_frame, text='Apply', command=self.apply_colors).pack(side=LEFT, padx=5)

        # Plot frame
        plot_frame = ttk.Frame(self.master)
        plot_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

        self.canvas = FigureCanvasTkAgg(self.plot_handler.fig, plot_frame)
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        toolbar.update()

    def select_file(self):
        '''Select the file with the data to plot.'''
        file_path = filedialog.askopenfilename(filetypes=[('Data files', '*.dat'), ('All files', '*.*')])
        if not file_path:
            self.logger.log('No file selected')
            messagebox.showerror('Error', 'No file selected')
            return

        try:
            header_lines, delimiter =self.data_handler.load_data(file_path)
            self.logger.log(f'File loaded: {file_path =}')
            self.logger.log(f'{header_lines=} and {delimiter=}')
            messagebox.showinfo('File Loaded', f'{file_path.split("/")[-1]} loaded successfully.')
            num_lines = self.data_handler.data_txt[:, 1:].shape[1]
            self.data_handler.generate_colors(self.color_combobox.get(), num_lines)
            self.update_plot()
        except Exception as e:
            self.logger.log(f'Failed to load file: {file_path =}')
            self.logger.log(f'Error: {e}')
            messagebox.showerror('Error', f'Failed to load file: {e}')

    def update_plot(self, *args):
        '''Update the plot with the new colors.'''
        try:
            offset = self.offset_var.get()
            self.plot_handler.update_plot(self.data_handler.data_txt, offset, self.data_handler.data_color)
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
