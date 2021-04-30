# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 18:46:54 2020
@author: Aziza
"""

import sys
import redpitaya_scpi as scpi
import time

class RedPitaya:

    def __init__(self):    
        self.rp_s = scpi.scpi(sys.argv[1])

    def measure_all(self, scan_time):
        scan = 65536
        I =[]
        Q =[]
        self.rp_s.tx_txt('ACQ:DEC ' + str(scan)) # 65536
        self.rp_s.tx_txt('ACQ:AVG ON')
        self.rp_s.tx_txt('ACQ:START')
        time.sleep(4)
        self.rp_s.tx_txt('ACQ:TRIG EXT_NE')
        self.rp_s.tx_txt('ACQ:TRIG:EXT:LEV 0')
        self.rp_s.tx_txt('ACQ:TRIG:DLY 8192')
        while 1:
            self.rp_s.tx_txt('ACQ:TRIG:STAT?')
            if self.rp_s.rx_txt() == 'TD':
                break
        self.rp_s.tx_txt('ACQ:SOUR1:DATA?')  
        buff_string = self.rp_s.rx_txt()
        buff_string = buff_string.strip('{}\n\r').replace("  ", "").split(',')
        #print(buff_string)
        I = list(map(float, buff_string[1:len(buff_string)]))
    
        self.rp_s.tx_txt('ACQ:SOUR2:DATA?')      
        buff_string = self.rp_s.rx_txt()
        buff_string = buff_string.strip('{}\n\r').replace("  ", "").split(',')
        Q = list(map(float, buff_string[1:len(buff_string)]))
        self.rp_s.tx_txt('ACQ:STOP')
        return I, Q

    def trigger_out(self):
        wave_form = 'square'
        offset = -1
        freq = 0.5
        ampl = 1

        self.rp_s.tx_txt('GEN:RST')
        self.rp_s.tx_txt('SOUR1:FUNC ' + str(wave_form).upper())
        self.rp_s.tx_txt('SOUR1:FREQ:FIX ' + str(freq))
        self.rp_s.tx_txt('SOUR1:VOLT:OFFS ' + str(offset))
        self.rp_s.tx_txt('SOUR1:VOLT ' + str(ampl))

        #Enable output
        self.rp_s.tx_txt('OUTPUT1:STATE ON')
        # self.rp_s.tx_txt('DIG:PIN:DIR OUT,DIO2_N')
        # self.rp_s.tx_txt('DIG:PIN:DIR OUT,DIO2_P')
        # # high
        # self.rp_s.tx_txt('DIG:PIN DIO2_N,1')
        # self.rp_s.tx_txt('DIG:PIN DIO2_P,0')
        # # to low for triggering SignalCore 
        # self.rp_s.tx_txt('DIG:PIN DIO2_N,0')
        # self.rp_s.tx_txt('DIG:PIN DIO2_P,0')
        # time.sleep(0.2)
        # #raise back up
        # self.rp_s.tx_txt('DIG:PIN DIO2_N,1')
        # self.rp_s.tx_txt('DIG:PIN DIO2_P,0')