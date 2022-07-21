from europi_m import *
import machine
from time import ticks_diff, ticks_ms
from random import randint, uniform
from europi_script import EuroPiScript
from bjorklund import bjorklund as eucledian_rhythm

'''
Consequencer_m
author: Luis G (github.com/luisgongod)
date: 
labels: sequencer, triggers, drums, randomness

A gate sequencer that builds on Nik Ansell's Consequencer. 
Inspired by Grids from mutable instruments. 
Can control up 6 instruments, adding sequences for each channel
Perfect to use with something like the Weston Audio AD110

CONTROLS:
knob_1: Randomness
knob_2: Fill, based on euclediaan rhythms


digital_in: clock in
analog_in: CV for Randomness, Fill or Pattern

button_1: 
- Short Press  (<300ms)  : Previous Drum pattern
- Medium Press (>300ms)  : Cycles through clock divisors (1/1, 1/2, 1/4)
- Long Press  (>2000ms)  : ???

button_2:
- Short Press  (<300ms)  : Next Drum pattern
- Medium Press (>300ms)  : Cycles what AIN can CV, (randomness -> fill -> Pattern -> randomness)
- Long Press   (>2000ms) : Toggle option for Random/Fill behaviour mode, 
    &: Random applies only to Filled steps
    |: Random applies to all steps if > 0

output_1: trigger 1 / Bass Drum
output_2: trigger 2 / Snare Drum
output_3: trigger 3 / Hi-Hat
output_4: trigger 4 / Closed-Hat
output_5: trigger 5 / Cymmbal
output_6: trigger 6 / Clap

'''

class Consequencer(EuroPiScript):
    def __init__(self):
        # Overclock the Pico for improved performance.
        machine.freq(250_000_000)

        ###################################################### M exclusive:
        mk1._set_channel()

        # Initialize sequencer pattern arrays   
        p = pattern()     
        self.BD=p.BD
        self.SN=p.SN
        self.HH=p.HH
        self.OH=p.OH
        self.CY=p.CY
        self.CL=p.CL

        self.AIN_MODE = ['Random', 'Fill', 'Pattern']
        self.CLOCK_DIVISORS = [1, 2, 4]        

        # Initialize variables
        self.step = 0
        self.trigger_duration_ms = 50
        self.clock_step = 0
        self.clock_divisor = 0
        self.pattern = 0
        self.random_HH = False
        self.minAnalogInputVoltage = 0.9 # Minimum voltage for analog input to be considered
        self.randomness = 0
        self.analogInputMode = 1 # initial mode 0: Randomness, 1: Pattern, 2: Fill #BUG: out of bounds when = 2
        self.rand_fill_mode = 0 #  0: Random && Fill, 1: Random >> Fill
        self.CvPattern = 0
        self.reset_timeout = 500
        
        self.step_length = len(self.BD[self.pattern])

        self.fill = []
        
        # Calculate the longest pattern length to be used when generating random sequences
        self.maxStepLength = len(max(self.BD, key=len))
      

        # Triggered when button 2 is released.
        # - Short Press  (<300ms)  : Next Drum pattern
        # - Medium Press (>300ms)  : Cycles what AIN can CV, (randomness -> fill -> Pattern -> randomness)
        # - Long Press   (>2000ms) : Toggle option for Random/Fill behaviour mode, 
        @b2.handler_falling
        def b2Pressed():
            #Toggle Random/Fill mode
            # if more modes are added, this will need to be updated
            #     &: Random applies only to Filled steps
            #     |: Random applies to all steps if > 0
            if ticks_diff(ticks_ms(), b2.last_pressed()) >  2000:
                self.rand_fill_mode = not(self.rand_fill_mode)
            
            # AIN CV mode
            elif ticks_diff(ticks_ms(), b2.last_pressed()) >  300:
                self.analogInputMode = self.analogInputMode + 1
                if self.analogInputMode >= len(self.AIN_MODE):
                    self.analogInputMode = 0
            
            #next drum pattern
            else:
                self.pattern = (self.pattern + 1) 
                if self.pattern >= len(self.BD):
                    self.pattern = 0
                
                self.step_length = len(self.BD[self.pattern])
            
            
            
        # - Short Press  (<300ms)  : Previous Drum pattern
        # - Medium Press (>300ms)  : Cycles through clock divisors (1/1, 1/2, 1/4)
        # - Long Press   (>2000ms) : ???
        @b1.handler_falling
        def b1Pressed():
            if ticks_diff(ticks_ms(), b1.last_pressed()) >  2000:
                pass
            
            # clock divisor
            elif ticks_diff(ticks_ms(), b1.last_pressed()) >  300:
                self.clock_divisor = (self.clock_divisor + 1) % len(self.CLOCK_DIVISORS)
            
            #prev drum pattern
            else:
                self.pattern = (self.pattern - 1) 
                if self.pattern < 0:
                    self.pattern = len(self.BD)-1
                self.step_length = len(self.BD[self.pattern])
            

        # Triggered on each clock into digital input. Output triggers.
        @din.handler
        def clockTrigger():

            # function timing code. Leave in and activate as needed
            #t = time.ticks_us()
            
            self.step_length = len(self.BD[self.pattern])
            
            # A pattern was selected which is shorter than the current step. Set to zero to avoid an error
            if self.step >= self.step_length:
                self.step = 0             

            if self.randomness == 0:
                cv1.value(int(self.BD[self.pattern][self.step])*self.fill[self.step])
                cv2.value(int(self.SN[self.pattern][self.step])*self.fill[self.step])                    
                cv3.value(int(self.HH[self.pattern][self.step])*self.fill[self.step])
                cv4.value(int(self.OH[self.pattern][self.step])*self.fill[self.step])                    
                cv5.value(int(self.CY[self.pattern][self.step])*self.fill[self.step])                    
                cv6.value(int(self.CL[self.pattern][self.step])*self.fill[self.step])                                        

            else: # randomness > 0
                if self.rand_fill_mode == 0: # Random over Fill
                    cv1.value(randint(0, 1))
                    cv2.value(randint(0, 1))
                    cv3.value(randint(0, 1))
                    cv4.value(randint(0, 1))
                    cv5.value(randint(0, 1))
                    cv6.value(randint(0, 1))
    
                else:# Random && Fill                     
                    cv1.value(int(self.BD[self.pattern][self.step])*self.fill[self.step]*randint(0, 1))
                    cv2.value(int(self.SN[self.pattern][self.step])*self.fill[self.step]*randint(0, 1))                    
                    cv3.value(int(self.HH[self.pattern][self.step])*self.fill[self.step]*randint(0, 1))
                    cv4.value(int(self.OH[self.pattern][self.step])*self.fill[self.step]*randint(0, 1))                    
                    cv5.value(int(self.CY[self.pattern][self.step])*self.fill[self.step]*randint(0, 1))                    
                    cv6.value(int(self.CL[self.pattern][self.step])*self.fill[self.step]*randint(0, 1))                                        
             
            # Incremenent the clock step
            self.clock_step +=1
            self.step += 1

            # function timing code. Leave in and activate as needed
            #delta = time.ticks_diff(time.ticks_us(), t)
            #print('Function {} Time = {:6.3f}ms'.format('clockTrigger', delta/1000))

        @din.handler_falling
        def clockTriggerEnd():
            cv1.off()
            cv2.off()
            cv3.off()
            cv4.off()
            cv5.off()
            cv6.off()


        
    def getParams(self):

        val = ain.percent()
        extra_random = 0
        extra_fill = 0
        extra_pattern = 0

        # if self.analogInputMode == 0 and val > self.minAnalogInputVoltage:


        if self.analogInputMode == 0: #Random
            extra_random = int(val*100) # 0-100
            pass
        elif self.analogInputMode == 1: #Fill
            extra_fill = round(val*self.step_length)-1 # 0-step_length
            pass
        elif self.analogInputMode == 2: # Pattern
            extra_pattern = round(val*len(self.BD))-1 # 0- number of patterns
            self.pattern = (extra_pattern + self.pattern)%len(self.BD)
            self.step_length = len(self.BD[self.pattern])
            
        #TOCHECK:
        self.randomness = min(k1.read_position() + extra_random,99)

        nfill =  min(k2.read_position(self.step_length) + extra_fill,self.step_length-1)  

        self.fill = eucledian_rhythm(self.step_length,nfill)

    
        val = 100 * ain.percent()
        self.randomness = val

        # if  self.AIN_MODE[self.analogInputMode] == "Pattern" and val > self.minAnalogInputVoltage:
        #     self.pattern = int((len(self.BD) / 100) * val)
        # else:
        #     self.pattern = k2.read_position(len(self.BD))
        
        
        #fill based on the amount of eucledian fill         
        # if self.analogInputMode != 3:
        #     return
        # else:
        #     # Get the analogue input voltage as a percentage of fill

            
                
        # Get Pattern from AIN    
        # If mode 2 and there is CV on the analogue input use it, if not use the knob position
        return

        
        # val = 100 * ain.percent()
            

    # def generateRandomPattern(self, length, min, max):
    #     self.t=[]
    #     for i in range(0, length):
    #         self.t.append(uniform(0,9))
    #     return self.t



    def main(self):
        while True:
            self.getParams()            
            self.updateScreen()
            # If I have been running, then stopped for longer than reset_timeout, reset the steps and clock_step to 0
            if self.clock_step != 0 and ticks_diff(ticks_ms(), din.last_triggered()) > self.reset_timeout:
                self.step = 0
                self.clock_step = 0

    def visualizePattern(self, pattern):
        self.t = pattern
        self.t = self.t.replace('1','.')
        self.t = self.t.replace('0',' ')
        return self.t
    
    def visualizeFill(self, fillpattern):
        filltext = ''
        for i in range(0, len(fillpattern)):
            if fillpattern[i] == 1:
                filltext += '-'
            else:
                filltext += ' '
        return filltext
    
    def downarrow(pos,color = 1):  
        x= 8*pos +1
        
        for i in range(6):
            oled.pixel(x+i,0,color)
        for i in range(4):
            oled.pixel(x+i+1,1,color)
        for i in range(2):
            oled.pixel(x+i+2,2,color)



    
    def displayPattern(self):
                # Show selected pattern visually
        spacing = 3
        col_size = int(OLED_WIDTH / 16)
        oled.text(self.visualizePattern(self.BD[self.pattern]), 0, spacing*0, 1)
        oled.text(self.visualizePattern(self.SN[self.pattern]), 0, spacing*1, 1)
        oled.text(self.visualizePattern(self.HH[self.pattern]), 0, spacing*2, 1)
        oled.text(self.visualizePattern(self.OH[self.pattern]), 0, spacing*3, 1)
        oled.text(self.visualizePattern(self.CY[self.pattern]), 0, spacing*4, 1)
        oled.text(self.visualizePattern(self.CL[self.pattern]), 0, spacing*5, 1)
        
        oled.rect((self.step-1)*col_size, 0, col_size, OLED_HEIGHT-18, 1)
            
        # oled.text("^", (self.step-1)*col_size, OLED_HEIGHT-18, 1)
        oled.text(self.visualizeFill(self.fill), 0, OLED_HEIGHT-18, 1)

    def updateScreen(self):
        # oled.clear() - dont use this, it causes the screen to flicker!
        oled.fill(0)
 
        # Show selected pattern visually
        # spacing = 7
        # col_size = int(OLED_WIDTH / 16)
        # oled.text(self.visualizePattern(self.BD[self.pattern]), 0, spacing*0, 1)
        # oled.text(self.visualizePattern(self.SN[self.pattern]), 0, spacing*1, 1)
        # oled.text(self.visualizePattern(self.HH[self.pattern]), 0, spacing*2, 1)
        # oled.text(self.visualizePattern(self.OH[self.pattern]), 0, spacing*3, 1)
        # oled.text(self.visualizePattern(self.CY[self.pattern]), 0, spacing*4, 1)
        # oled.text(self.visualizePattern(self.CL[self.pattern]), 0, spacing*5, 1)
        
        # oled.rect((self.step-1)*col_size, 0, col_size, OLED_HEIGHT-18, 1)
            
        # oled.text("^", (self.step-1)*col_size, OLED_HEIGHT-18, 1)
        # oled.text(self.visualizeFill(self.fill), 0, OLED_HEIGHT-18, 1)
        self.displayPattern()
        self.downarrow(self.step)
        
        

        # Show randomness
        bottom_spacing = 8
        #         ' R99 F16 P42 &4 '        
        oled.text('             ' + str(int(self.rand_fill_mode))+str(self.CLOCK_DIVISORS[self.clock_divisor]), 0, OLED_HEIGHT-bottom_spacing, 1)
        oled.text('         P' + str(self.pattern), 0, OLED_HEIGHT-bottom_spacing, 1)
        oled.text('     F' + str(sum(self.fill)), 0, OLED_HEIGHT-bottom_spacing, 1)        
        oled.text(' R' + str(int(self.randomness)), 0, OLED_HEIGHT-bottom_spacing, 1)

        
        oled.rect(self.analogInputMode*32+8, OLED_HEIGHT-bottom_spacing, 24, bottom_spacing, 1)
        

        oled.show()
    
    def visualizeTrack(self, track):
        t = ''
        for i in range(0, len(track)):
            track_cv, track_sparsity = track[i]
            if track_sparsity > self.sparsity:
                t += '.'
            else:
                t += ' '
        return t

class pattern:

    # Initialize pattern lists
    BD=[]
    SN=[]
    HH=[]
    OH=[]
    CY=[]
    CL=[]

    # African Patterns
    #0
    # BD.append("10110000001100001011000000110000")
    # SN.append("10001000100010001010100001001010")
    # HH.append("00001011000010110000101100001011") 

    # BD.append("10101010101010101010101010101010")
    # SN.append("00001000000010000000100000001001")
    # HH.append("10100010101000101010001010100000")

    # BD.append("11000000101000001100000010100000")
    # SN.append("00001000000010000000100000001010")
    # HH.append("10111001101110011011100110111001")

    # BD.append("10001000100010001000100010001010")
    # SN.append("00100100101100000010010010110010")
    # HH.append("10101010101010101010101010101011")

    # BD.append("00101011101000111010001110100010")
    # SN.append("00101011101000111010001110100010")
    # HH.append("00001000000010000000100000001000")

    # BD.append("10101111101000111010001110101000")
    # SN.append("10101111101000111010001110101000")
    # HH.append("00000000101000001010000010100010")

    # BD.append("10110110000011111011011000001111")
    # SN.append("10110110000011111011011000001111")
    # HH.append("11111010001011111010001110101100")

    # BD.append("10010100100101001001010010010100")
    # SN.append("00100010001000100010001000100010")
    # HH.append("01010101010101010101010101010101")

    # 0,1,1,2,3,5,8,12
    #9
    # BD.append("0101011011101111")
    # SN.append("1010100100010000")
    # HH.append("1110100100010000")

    # Add patterns
    # BD.append("1000100010001000")
    # SN.append("0000000000000000")
    # HH.append("0000000000000000")

    # BD.append("1000100010001000")
    # SN.append("0000000000000000")
    # HH.append("0010010010010010")

    # BD.append("1000100010001000")
    # SN.append("0000100000000000")
    # HH.append("0010010010010010")

    # BD.append("1000100010001000")
    # SN.append("0000100000001000")
    # HH.append("0010010010010010")

    # BD.append("1000100010001000")
    # SN.append("0000100000000000")
    # HH.append("0000000000000000")

    # BD.append("1000100010001000")
    # SN.append("0000100000001000")
    # HH.append("0000000000000000")

    # BD.append("1000100010001000")
    # SN.append("0000100000001000")
    # HH.append("0000100010001001")

    # BD.append("1000100010001000")
    # SN.append("0000100000001000")
    # HH.append("0101010101010101")

    # BD.append("1000100010001000")
    # SN.append("0000000000000000")
    # HH.append("1111111111111111")

    # BD.append("1000100010001000")
    # SN.append("0000100000001000")
    # HH.append("1111111111111111")

    # BD.append("1000100010001000")
    # SN.append("0000100000000000")
    # HH.append("0001000000000000")

    # BD.append("1000100010001000")
    # SN.append("0000100000000000")
    # HH.append("0001001000000000")

    # Source: https://docs.google.com/spreadsheets/d/19_3BxUMy3uy1Gb0V8Wc-TcG7q16Amfn6e8QVw4-HuD0/edit#gid=0
    #22
    # BD.append("1000000010000000")
    # SN.append("0000100000001000")
    # HH.append("1010101010101010")

    # BD.append("1010001000100100")
    # SN.append("0000100101011001")
    # HH.append("0000000100000100")

    # BD.append("1000000110000010")
    # SN.append("0000100000001000")
    # HH.append("1010101110001010")

    # BD.append("1100000100110000")
    # SN.append("0000100000001000")
    # HH.append("1010101010101010")

    # BD.append("1000000110100000")
    # SN.append("0000100000001000")
    # HH.append("0010101010101010")

    # BD.append("1010000000110001")
    # SN.append("0000100000001000")
    # HH.append("1010101010101010")

    # BD.append("1000000110100001")
    # SN.append("0000100000001000")
    # HH.append("0000100010101011")

    # BD.append("1001001010000000")
    # SN.append("0000100000001000")
    # HH.append("0000100000001000")

    # BD.append("1010001001100000")
    # SN.append("0000100000001000")
    # HH.append("1010101010001010")

    # BD.append("1010000101110001")
    # SN.append("0000100000001000")
    # HH.append("1010101010001010")

    # End external patterns
    #32
    # BD.append("1100000001010000")
    # SN.append("0000101000001000")
    # HH.append("0101010101010101")
    # OH.append("0000000000000000")
    # CY.append("0000000000000000")
    # CL.append("0000000000000000")

    # BD.append("1100000001010000")
    # SN.append("0000101000001000")
    # HH.append("1111111111111111")
    # OH.append("0000000000000000")
    # CY.append("0000000000000000")
    # CL.append("0000000000000000")

    # BD.append("1001001001000100")
    # SN.append("0001000000010000")
    # HH.append("0101110010011110")
    # OH.append("0000000000000000")
    # CY.append("0000000000000000")
    # CL.append("0000000000000000")

    # BD.append("1001001001000100")
    # SN.append("0001000000010000")
    # HH.append("1111111111111111")
    # OH.append("0000000000000000")
    # CY.append("0000000000000000")
    # CL.append("0000000000000000")

    # Be warned patterns < 16 steps can sound disjointed when using CV to select the pattern!

    # BD.append("10010000010010")
    # SN.append("00010010000010")
    # HH.append("11100110111011")

    # BD.append("1001000001001")
    # SN.append("0001001000001")
    # HH.append("1110011011101")

    # BD.append("100100000100")
    # SN.append("000100100000")
    # HH.append("111001101110")

    # BD.append("10010000010")
    # SN.append("00010010000")
    # HH.append("11100110111")

    # BD.append("10010000010")
    # SN.append("00010010000")
    # HH.append("11111010011")

    # BD.append("1001000010")
    # SN.append("0001000000")
    # HH.append("1111101101")

    # BD.append("100100010")
    # SN.append("000100000")
    # HH.append("111110111")

    # BD.append("10010010")
    # SN.append("00010000")
    # HH.append("11111111")

    # BD.append("1001001")
    # SN.append("0001000")
    # HH.append("1111111")

    # BD.append("100100")
    # SN.append("000100")
    # HH.append("111111")

    # BD.append("10000")
    # SN.append("00001")
    # HH.append("11110")

    # BD.append("1000")
    # SN.append("0000")
    # HH.append("1111")


    # BD.append("100")
    # SN.append("000")
    # HH.append("111")

    #49 extras:
    BD.append("1000")
    SN.append("0100")
    HH.append("0010")
    OH.append("0001")
    CY.append("0000")
    CL.append("0100")
    

    BD.append("1000100010010010")
    SN.append("0100010001000100")
    HH.append("1010101010101010")
    OH.append("0001000100010100")
    CY.append("0110000000000000")
    CL.append("0000000010000101")

if __name__ == '__main__':
    # Reset module display state.
    [cv.off() for cv in cvs]
    dm = Consequencer()
    dm.main()


