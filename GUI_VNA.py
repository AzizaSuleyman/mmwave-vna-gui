# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 19:41:52 2020

@author: Aziza
"""

import numpy as np
import tkinter as tk
import datetime as dt
import tkinter.font as tkFont
from PIL import ImageTk, Image
import pandas as pd
import math

import matplotlib.figure as figure
import matplotlib.animation as animation
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from redpitaya_VNA import RedPitaya
import SC_VNA

class VNA(tk.Tk):
    def __init__(self, tasks=None):
        super().__init__()
        self.title("Mm-wave VNA")
        self.geometry("1800x1200")
        self.input_frame = tk.Frame(self, width=1800, height=150, bg="light blue")
        self.input_frame.pack(side = tk.TOP, fill=tk.X, expand=False)
        self.fit_frame = tk.Frame(self, width=1800, height=100, bg="white")
        self.fit_frame.pack(side = tk.TOP, fill=tk.X, expand=False) 

        self.dfont = None
        # Create dynamic font for  text
        self.dfont = tkFont.Font(size=12, family='helvetica', weight='bold')
        self.dfontPlotTitle = tkFont.Font(size=20, family='helvetica', weight='bold')

        # Frame for the plots
        self.plot_frame_IQ = tk.Frame(self, width=1200, height=350, bg="white")
        self.plot_frame_IQ.pack(side = tk.TOP,fill=tk.X, expand=False)
        
        # Frame for the plots
        self.plot_frame_mag = tk.Frame(self, width=1200, height=350, bg="white")
        self.plot_frame_mag.pack(side = tk.TOP,fill=tk.X, expand=False)
         # Frame for fits
        self.plot_frame_IQ.columnconfigure(2, weight=1)
        self.plot_frame_IQ.rowconfigure(2, weight=1)
        # Frame for fits
        self.plot_frame_mag.columnconfigure(2, weight=1)
        self.plot_frame_mag.rowconfigure(2, weight=1)
        # Variables for holding temperature data
        self.freq_center_mm = tk.DoubleVar()
        self.freq_center_mw = tk.DoubleVar()
        self.freq_span_mm = tk.DoubleVar()
        self.freq_span_mw = tk.DoubleVar()
        self.freq_step_mw = tk.DoubleVar()
        self.button_updateScan = tk.Button(self.input_frame, text="Update Scan",
                                        command=self.update_SC, bg='light pink', width=10,font = self.dfont)
        
        # Create widgets
        self.entry_freq_center_mm = tk.Entry(self.input_frame, width=10,
                                            textvariable=self.freq_center_mm)
        self.label_center_mm = tk.Label(self.input_frame, 
                                       text="Center Frequency", font = self.dfont, bg="light blue")
        self.label_center_GHz = tk.Label(self.input_frame, text="GHz", font = self.dfont, bg="light blue")
        self.entry_freq_span_mm = tk.Entry(self.input_frame, width=10,
                                          textvariable=self.freq_span_mm)
        self.label_span_mm = tk.Label(self.input_frame, text="Span Frequency", font = self.dfont, bg="light blue")
        self.label_span_GHz = tk.Label(self.input_frame, text="GHz", font = self.dfont, bg="light blue")
        self.label_SignalCore = tk.Label(self.input_frame,
                                         text="SignalCore Frequencies", font = self.dfont, bg="light blue")
        self.label_freq_center_mw = tk.Label(self.input_frame,
                                            textvariable=self.freq_center_mw, font = self.dfont, bg="light blue")
        self.label_freq_span_mw = tk.Label(self.input_frame,
                                          textvariable=self.freq_span_mw, font = self.dfont, bg="light blue")
        self.label_SC_span_GHz = tk.Label(self.input_frame, text="GHz", font = self.dfont, bg="light blue")
        self.label_SC_center_GHz = tk.Label(self.input_frame, text="GHz", font = self.dfont, bg="light blue")
        self.img = ImageTk.PhotoImage(Image.open("5G_1.png").resize((170, 120), Image.ANTIALIAS))
        self.label_5G = tk.Label(self.input_frame, image =self.img)

        # Lay out widgets
        self.entry_freq_center_mm.grid(row=0, column=1, columnspan=1, padx=5, pady=5)
        self.entry_freq_span_mm.grid(row=0, column=4, columnspan=1, padx=5, pady=5)
        self.label_center_mm.grid(row=0, column=0, columnspan=1, padx=5, pady=5)
        self.label_center_GHz.grid(row=0, column=2, columnspan=1, padx=5, pady=5)
        self.label_span_mm.grid(row=0, column=3, columnspan=1, padx=5, pady=5)
        
        self.label_5G.place(x = 1000, y = 5)
        self.label_span_GHz.grid(row=0, column=5, columnspan=1, padx=5, pady=5)
        self.label_SignalCore.grid(row=1, column=0, columnspan=1, padx=5, pady=5)
        self.label_freq_center_mw.grid(row=1, column=1, columnspan=1, padx=5, pady=5)
        self.label_freq_span_mw.grid(row=1, column=4, columnspan=1, padx=5, pady=5)
        self.label_SC_center_GHz.grid(row=1, column=2, columnspan=1, padx=5, pady=5)
        self.label_SC_span_GHz.grid(row=1, column=5, columnspan=1, padx=5, pady=5)
        self.button_updateScan.grid(row=2, column=2, columnspan=1, padx=5, pady=5)


# =============================================================================
#         # Parameters and global variables
#         # Parameters
#         self.update_interval = 1000 # Time (ms) between polling/animation updates
#         self.max_elements = 1440     # Maximum number of elements to store in plot lists
# =============================================================================
        # Declare global variables
        self.canvas = None
        self.ax1_mag = None
        self.ax1_Q = None
        self.ax1_I = None
        self.ax1_phase = None
        # Global variable to remember various states
        self.fullscreen = False
        self.fit_visible = False

        # Place cursor in entry box by default
        self.entry_freq_center_mm.focus()

        # Create figure for plotting
        self.fig_I = figure.Figure(figsize=(8, 3.5))
        self.fig_I.subplots_adjust(left=0.1, right=0.8)
        self.ax1_I = self.fig_I.add_subplot(1, 1, 1)

        # Instantiate a new set of axes that shares the same x-axis
        self.ax2_I = self.ax1_I.twinx()

         # Create figure for plotting
        self.fig_Q = figure.Figure(figsize=(8, 3.5))
        self.fig_Q.subplots_adjust(left=0.1, right=0.8)
        self.ax1_Q = self.fig_Q.add_subplot(1, 1, 1)

        # Instantiate a new set of axes that shares the same x-axis
        self.ax2_Q = self.ax1_Q.twinx()    

        # Create figure for plotting
        self.fig_mag = figure.Figure(figsize=(8, 3.5))
        self.fig_mag.subplots_adjust(left=0.1, right=0.8)
        self.ax1_mag = self.fig_mag.add_subplot(1, 1, 1)

        # Instantiate a new set of axes that shares the same x-axis
        self.ax2_mag = self.ax1_mag.twinx()

        # Create figure for plotting
        self.fig_phase = figure.Figure(figsize=(8, 3.5))
        self.fig_phase.subplots_adjust(left=0.1, right=0.8)
        self.ax1_phase = self.fig_phase.add_subplot(1, 1, 1)

        # Instantiate a new set of axes that shares the same x-axis
        self.ax2_phase = self.ax1_phase.twinx()
        
        #s is array with fit parameters
        self.s = []

         # Create a Tk Canvas widget out of our figure
        self.canvas_I = FigureCanvasTkAgg(self.fig_I, master=self.plot_frame_IQ)
        self.canvas_plot_I = self.canvas_I.get_tk_widget()

        self.canvas_Q = FigureCanvasTkAgg(self.fig_Q, master=self.plot_frame_IQ)
        self.canvas_plot_Q = self.canvas_Q.get_tk_widget()

        # Create a Tk Canvas widget out of our figure
        self.canvas_mag = FigureCanvasTkAgg(self.fig_mag, master=self.plot_frame_mag)
        self.canvas_plot_mag = self.canvas_mag.get_tk_widget()

        self.canvas_phase = FigureCanvasTkAgg(self.fig_phase, master=self.plot_frame_mag)
        self.canvas_plot_phase = self.canvas_phase.get_tk_widget()
        
        #Labels for plots
        self.label_Iplot = tk.Label(self.plot_frame_IQ, width = 10,
                                       text="I Plot", bg='white', font=self.dfontPlotTitle)
        self.label_Qplot = tk.Label(self.plot_frame_IQ, width = 10,
                                       text="Q Plot", bg='white', font=self.dfontPlotTitle)
        self.label_Magplot = tk.Label(self.plot_frame_mag, width = 10,
                                       text="Mag Plot", bg='white', font=self.dfontPlotTitle)
        self.label_Phaseplot = tk.Label(self.plot_frame_mag, width = 10,
                                       text="Phase Plot", bg='white', font=self.dfontPlotTitle)
        
        self.Qc = tk.DoubleVar()
        self.Qi = tk.DoubleVar()
        self.fres = tk.DoubleVar()
        self.a = tk.DoubleVar()
        self.b = tk.DoubleVar()
        self.saveName = tk.StringVar()
        self.avg = tk.IntVar(value = 1)
        self.dnu = tk.DoubleVar()

        # Global  variables for SC
        self.N_POINTS = 120
        self.dwell_time = 20*500 #us
        self.scan_time = self.N_POINTS*self.dwell_time

        # Create other supporting widgets
        self.label_Qc = tk.Label(self.fit_frame, text='Q coupling:', 
                                 bg='white', font = self.dfont)
        self.entry_Qc = tk.Entry(self.fit_frame, width=10,
                                            textvariable=self.Qc)
        self.label_Qi = tk.Label(self.fit_frame, text='Q internal:',
                                 bg='white', font = self.dfont)
        self.entry_Qi = tk.Entry(self.fit_frame, width=10,
                                            textvariable=self.Qi)
        self.label_fres = tk.Label(self.fit_frame, text='Resonance frequency:',
                                   bg='white', font = self.dfont)
        self.entry_fres = tk.Entry(self.fit_frame, width=10,
                                            textvariable=self.fres)
        self.label_a = tk.Label(self.fit_frame, text='a + ib:', bg='white', font = self.dfont)
        self.entry_a = tk.Entry(self.fit_frame, width=10,
                                            textvariable=self.a)
        self.entry_b = tk.Entry(self.fit_frame, width=10,
                                            textvariable=self.b)
        self.label_saveName = tk.Label(self.fit_frame, text='Save File name:',
                                 bg='white', font = self.dfont)
        self.entry_saveName = tk.Entry(self.fit_frame, width=30,
                                            textvariable=self.saveName)
        self.label_avg = tk.Label(self.fit_frame, text='Navg:',
                                 bg='white', font = self.dfont)
        self.entry_avg = tk.Entry(self.fit_frame, width=10,
                                            textvariable=self.avg)
        self.label_dnu = tk.Label(self.fit_frame, text='Asymmetry:',
                                  bg='white', font = self.dfont)
        self.entry_dnu = tk.Entry(self.fit_frame, width=10,
                                            textvariable=self.dnu)

        self.button_quit = tk.Button(self.fit_frame,
                                     text="Quit",
                                     command=self.destroy, width=10, font = self.dfont)
        self.button_measure = tk.Button(self.fit_frame, bg='light pink',
                                     text="Measure", command=self.measure, width=10, font = self.dfont)
        # self.button_trigger = tk.Button(self.fit_frame, bg='light pink',
        #                              text="Trigger", command=self.trigger, width=10, font = self.dfont)                             
        self.button_saveData = tk.Button(self.fit_frame, bg='light pink',
                                     text="Save Data", command=self.saveData, width=10, font = self.dfont)

        self.button_fit = tk.Button(self.fit_frame, bg='light green', 
                                     text="Fit",
                                     command=self.fit,  width=10, font = self.dfont)
        # Lay out widgets in a grid in the frame
        self.label_Qc.grid(row=0, column=0, columnspan=1, padx=5, pady=5)
        self.entry_Qc.grid(row=0, column=1, columnspan=1, padx=5, pady=5)
        self.label_Qi.grid(row=0, column=3, columnspan=1, padx=5, pady=5)
        self.entry_Qi.grid(row=0, column=4, columnspan=1, padx=5, pady=5)
        self.label_fres.grid(row=1, column=0, columnspan=1, padx=5, pady=5)
        self.entry_fres.grid(row=1, column=1, columnspan=1, padx=5, pady=5)
        self.label_a.grid(row=1, column=3, columnspan=1, padx=5, pady=5)
        self.entry_a.grid(row=1, column=4, columnspan=1, padx=5, pady=5)
        self.entry_b.grid(row=1, column=5, columnspan=1, padx=5, pady=5)
        self.label_avg.grid(row=0, column=11, columnspan=1, padx=5, pady=5)
        self.entry_avg.grid(row=0, column=12, columnspan=1, padx=5, pady=5)
        self.label_saveName.grid(row=0, column=13, columnspan=1, padx=5, pady=5)
        self.entry_saveName.grid(row=0, column=14, columnspan=5, padx=5, pady=5)
        self.label_dnu.grid(row=2, column=0, columnspan=1, padx=5, pady=5)
        self.entry_dnu.grid(row=2, column=1, columnspan=1, padx=5, pady=5)
        self.button_fit.grid(row=2, column=4, columnspan=1, padx=5, pady=5)
        self.button_measure.grid(row=2, column=12, columnspan=1, padx=5, pady=5)
        # self.button_trigger.grid(row=2, column=14, columnspan=1, padx=5, pady=5)
        self.button_saveData.grid(row=2, column=14, columnspan=1, padx=5, pady=5)
        self.button_quit.grid(row=2, column=20, columnspan=1, padx=5, pady=5)
        
        self.canvas_plot_I.grid(row=1, column=0, rowspan=20, columnspan=20)
        self.canvas_plot_Q.grid(row=1, column=30, rowspan=20, columnspan=20)
        self.canvas_plot_mag.grid(row=30, column=0, rowspan=20, columnspan=20)
        self.canvas_plot_phase.grid(row=30, column=30, rowspan=20, columnspan=20)
        
        self.label_Iplot.grid(row=0, column=0, columnspan=1, padx=5, pady=1)
        self.label_Qplot.grid(row=0, column=30, columnspan=1, padx=5, pady=1)
        self.label_Magplot.grid(row=29, column=0, columnspan=1, padx=5, pady=1)
        self.label_Phaseplot.grid(row=29, column=30, columnspan=1, padx=5, pady=1)

        #initialize red pitaya and SigncalCore        
        self.rp = RedPitaya()
        SC_VNA.start()

        # Make it so that the grid cells expand out to fill window
        for i in range(0, 5):
            self.plot_frame_IQ.rowconfigure(i, weight=1)
        for i in range(0, 5):
            self.plot_frame_IQ.columnconfigure(i, weight=1)
        for i in range(0, 5):
            self.plot_frame_mag.rowconfigure(i, weight=1)
        for i in range(0, 5):
            self.plot_frame_mag.columnconfigure(i, weight=1)

        # Bind F11 to toggle fullscreen and ESC to end fullscreen
        self.bind('<F11>', self.toggle_fullscreen)
        self.bind('<Escape>', self.end_fullscreen)

        # Have the resize() function be called every time the window is resized
        self.bind('<Configure>', self.resize)

        # Call empty _destroy function on exit to prevent segmentation fault
        self.bind("<Destroy>", self._destroy)

    # Updates SC with new values for the scan to be triggered (using Measure)
    def update_SC(self, event=None):
        try:
            val_center = self.freq_center_mm.get()
            self.freq_center_mw.set(val_center/6)
            val_span = self.freq_span_mm.get()
            self.freq_span_mw.set(val_span/6)
        except:
            pass
        self.freq_center_sc = round(self.freq_center_mw.get()*10**9)
        self.freq_span_sc = round(self.freq_span_mw.get()*10**9)
        self.freq_step_sc = round(self.freq_span_mw.get()*10**9/self.N_POINTS)
        print(self.freq_center_sc, self.freq_span_sc, self.freq_step_sc)
        SC_VNA.update_scan( self.freq_center_sc, self.freq_span_sc,  self.freq_step_sc, self.dwell_time)
        
        
    # triggers the redpitaya and signal cores and immediately measure with the rp, and displays the plot
    def measure(self):
        # generate a trigger signal from red pitaya
        #redpitaya_VNA.trigger_out()       
        self.IQ = None
        self.I = []
        self.Q = []
        # Update data to display temperature and light values        
        for i in range(1, self.avg.get()+1):    
            try:
                self.IQ = self.rp.measure_all(self.scan_time)
            except:
                pass
            self.I = self.I + self.IQ[1]
            self.Q = self.Q + self.IQ[0]
        
        self.I = [x/self.avg.get() for x in self.I]
        self.Q = [x/self.avg.get() for x in self.Q]
        
        self.x_axis = self.freq_center_mm.get() - self.freq_span_mm.get()/2 + self.freq_span_mm.get()*np.array(range(0, len(self.I)))/len(self.I)
        
        # I plot
        color = 'tab:red'
        self.ax1_I.clear()
        self.ax1_I.set_ylabel('In phase Data S11', color=color)
        self.ax1_I.tick_params(axis='y', labelcolor=color)
        self.ax1_I.plot(self.x_axis, self.I, linewidth=2, color=color, alpha=0.3)
        # self.ax1_I.fill_between(self.x_axis, self.I, linewidth=2, color=color, alpha=0.3)
        self.canvas_I.draw()
        
        # Q plot
        color = 'tab:red'
        self.ax1_Q.clear()
        self.ax1_Q.set_ylabel('Quadrature Data S11', color=color)
        self.ax1_Q.tick_params(axis='y', labelcolor=color)
        # self.ax1_Q.fill_between(self.x_axis, self.Q, linewidth=2, color=color, alpha=0.3)
        self.ax1_Q.plot(self.x_axis, self.Q, linewidth=2, color=color, alpha=0.3)
        self.canvas_Q.draw()
        
        Z = self.I + np.multiply(1j ,self.Q)
        self.mag = np.abs(Z)
        self.log = 20*np.log10(np.abs(Z))
        self.phase =  np.angle(Z)
        
        # mag plot
        color = 'tab:red'
        self.ax1_mag.clear()
        self.ax1_mag.set_ylabel('Log Data S11', color=color)
        self.ax1_mag.tick_params(axis='y', labelcolor=color)
        self.ax1_mag.plot(self.x_axis, self.log , linewidth=2, color=color, alpha=0.3)
        # self.ax1_mag.fill_between(self.x_axis, self.mag, linewidth=2, color=color, alpha=0.3)
        self.canvas_mag.draw()
        
        # phase plot
        color = 'tab:red'
        self.ax1_phase.clear()
        self.ax1_phase.set_ylabel('Phase Data S11', color=color)
        self.ax1_phase.tick_params(axis='y', labelcolor=color)
        self.ax1_phase.plot(self.x_axis, self.phase, linewidth=2, color=color, alpha=0.3)
        # self.ax1_phase.fill_between(self.x_axis, self.phase, linewidth=2, color=color, alpha=0.3)
        self.canvas_phase.draw()
    
    # def trigger(self):
    #     self.rp.trigger_out()
    #     print('triggered')
    # Toggle the light plot
    def fit(self):
        # Toggle plot and axis ticks/label

        self.s = [self.Qc.get(), self.Qi.get(), self.fres.get(), self.a.get(), self.b.get(), self.dnu.get()]
        self.mag_fit = self.FabryPerotMag()
        self.fit_visible = not self.fit_visible
        self.color = 'tab:blue'
        self.ax2_mag.clear()
        self.ax2_mag.set_ylabel('Fit, S11', color=self.color)
        self.ax2_mag.tick_params(axis='y', labelcolor=self.color)
        self.ax2_mag.plot(self.x_axis, self.mag_fit, linewidth=2, color=self.color)
        self.ax2_mag.get_lines()[0].set_visible(self.fit_visible)
        self.ax2_mag.get_yaxis().set_visible(self.fit_visible)
        self.canvas_mag.draw()
    
        self.phase_fit = self.FabryPerotPhase()
        self.ax2_phase.clear()
        self.ax2_phase.set_ylabel('Fit, S11', color=self.color)
        self.ax2_phase.tick_params(axis='y', labelcolor=self.color)
        self.ax2_phase.plot(self.x_axis, self.phase_fit, linewidth=2, color=self.color)   
        self.ax2_phase.get_lines()[0].set_visible(self.fit_visible)
        self.ax2_phase.get_yaxis().set_visible(self.fit_visible)
        self.canvas_phase.draw()
        
    # Save Data 
    def saveData(self):
        a = self.x_axis
        b = self.I
        c = self.Q
        df = pd.DataFrame({"Freq, GHz" : a, "I" : b, "Q" : c})
        df.to_csv("C:/Users/Aziza/Dropbox/AzizaOnly/Instruments/VNAcodeGUI/SavedVNAdata/CenterFreq_" 
                  + str(self.freq_center_mm.get()) +"GHz_Span_" + 
                  str(self.freq_span_mm.get()) + "GHz_Avg_" + 
                  str(self.avg.get()) + "_" +  self.saveName.get() + ".csv", index=False)
        
    # Toggle fullscreen
    def toggle_fullscreen(self, event=None):
        # Toggle between fullscreen and windowed modes
        self.fullscreen = not self.fullscreen
        self.attributes('-fullscreen', self.fullscreen)
        self.resize(None)   

    # Return to windowed mode
    def end_fullscreen(self, event=None):

        # Turn off fullscreen mode
        self.fullscreen = False
        self.attributes('-fullscreen', False)
        self.resize(None)

    # Automatically resize font size based on window size
    def resize(self, event=None):
        
        # Resize font based on frame height (minimum size of 12)
        # Use negative number for "pixels" instead of "points"
        self.new_size = -max(12, int((self.plot_frame_IQ.winfo_height() / 15)))
        #self.dfont.configure(size=self.new_size)
    
    # Dummy function prevents segfault
    def _destroy(self, event):
         pass

    def FabryPerotMag(self):
        numerator = self.s[0] - self.s[1] + 2*1j*self.s[0]*self.s[1]*((np.array(self.x_axis) - (self.s[2]+ self.s[5]))/(self.s[2]+ self.s[5])+self.s[5]/self.s[2])
        denominator = self.s[0] + self.s[1] + 2*1j*self.s[0]*self.s[1]*((np.array(self.x_axis) - (self.s[2]+ self.s[5]))/(self.s[2]+ self.s[5]))
        Erefl = (self.s[3]+1j*self.s[4])*(numerator/denominator)
        magFabry = np.abs(Erefl)**2
        return magFabry

    def FabryPerotPhase(self):
        numerator = self.s[0] - self.s[1] + 2*1j*self.s[0]*self.s[1]*((np.array(self.x_axis) - (self.s[2]+ self.s[5]))/(self.s[2]+ self.s[5])+self.s[5]/self.s[2])
        denominator = self.s[0] + self.s[1] + 2*1j*self.s[0]*self.s[1]*((np.array(self.x_axis) - (self.s[2]+ self.s[5]))/(self.s[2]+ self.s[5]))
        Erefl = (self.s[3]+1j*self.s[4])*(numerator/denominator)
        phaseFabry = np.angle(Erefl) 
        return phaseFabry
        

if __name__ == "__main__":
    vna = VNA()
vna.mainloop()