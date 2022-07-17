from europi_m import *
import machine
from time import ticks_diff, ticks_ms
from random import randint, uniform, choice

from europi_script import EuroPiScript

'''
Hamlet
author: Sean Bechhofer (github.com/seanbechhofer)
date: 2022-04-16
labels: sequencer, triggers, drums, randomness

A gate and CV sequencer that builds on Nik Ansell's Consequencer. Changes are:
* Slimmed down drum patterns to two instruments, BD/HH
* Two channels of gate and random stepped CV with sparsity control. As
  the sparsity is turned up, notes will drop out of the pattern.

digital_in: clock in
analog_in: sparsity CV

knob_1: sparsity
knob_2: select pre-loaded drum pattern

button_1: Short Press: Play previous CV Pattern. Long Press: Change CV track length multiplier
button_2: Short Press: Generate a new random cv pattern for Tracks 1 and 2. Long Press: Cycle through analogue input modes

output_1: trigger 1 / Bass Drum
output_2: trigger 2 / Hi-Hat
output_3:  
output_4: 
output_5: 
output_6: 

'''

class Hamlet(EuroPiScript):
    def __init__(self):
        self.bd_cv = cv1
        self.sn_cv = cv2
        self.ch_cv = cv3
        self.oh_cv = cv6
        self.cy_cv = cv4
        self.cl_cv = cv5

        # Overclock the Pico for improved performance.
        machine.freq(250_000_000)

        # Initialize sequencer pattern arrays   
        p = pattern()     
        self.BD=p.BD
        self.SN=p.SN
        self.CH=p.CH
        self.OH=p.OH
        self.CY=p.CY
        self.CP=p.CP

        # Initialize variables
        self.drum_step = 0
        self.track_step = 0

        self.trigger_duration_ms = 50
        self.clock_step = 0
        self.pattern = 0
        self.minAnalogInputVoltage = 0.9
        self.randomness = 0
        self.sparsity = 0
        self.analogInputMode = 1 # 1: Randomness, 2: Pattern, 3: CV Pattern
        self.CvPattern = 0
        
        # Generate random CV for cv4-6
        self.track_1 = []
        self.track_2 = []

        self.track_multiplier = 1 # multiplies CV pattern length so we can have 16, 32, 64
        
        self.generateNewRandomCVPattern()

        # Triggered when button 2 is released.
        # Short press: Generate random CV for Tracks 1 and 2
        # Long press: Change operating mode
        @b2.handler_falling
        def b2Pressed():
            
            if ticks_diff(ticks_ms(), b2.last_pressed()) >  300:
                if self.analogInputMode < 3:
                    self.analogInputMode += 1
                else:
                    self.analogInputMode = 1
            else:
                # Move to next cv pattern if one already exists, otherwise create a new one
                self.CvPattern += 1
                if self.CvPattern == len(self.track_1):
                    self.generateNewRandomCVPattern()
            
        # Triggered when button 1 is released
        # Short press: Play previous CV pattern for cv4-6
        # Long press: Not used
        @b1.handler_falling
        def b1Pressed():
            if ticks_diff(ticks_ms(), b1.last_pressed()) >  300:
                if self.track_multiplier >=4:
                    self.track_multiplier = 1
                else:
                    self.track_multiplier *= 2
                pass
            else:
                # Play previous CV Pattern, unless we are at the first pattern
                if self.CvPattern != 0:
                    self.CvPattern -= 1

        # Triggered on each clock into digital input. Output triggers.
        @din.handler
        def clockTrigger():

            self.step_length = len(self.BD[self.pattern])

            # As the randomness value gets higher, the chance of a randomly selected int being lower gets higher
            if randint(0,99) < self.randomness:
                self.bd_cv.value(randint(0, 1))
                self.bd_cv.value(randint(0, 1))
            else:
                # Trigger drums
                self.bd_cv.value(int(self.BD[self.pattern][self.drum_step]))
                self.sn_cv.value(int(self.SN[self.pattern][self.drum_step]))
                self.oh_cv.value(int(self.OH[self.pattern][self.drum_step])) 
                self.ch_cv.value(int(self.CH[self.pattern][self.drum_step]))
                self.cy_cv.value(int(self.CY[self.pattern][self.drum_step]))
                self.cl_cv.value(int(self.CP[self.pattern][self.drum_step]))
            
            # A pattern was selected which is shorter than the current step. Set to zero to avoid an error
            if self.drum_step >= self.step_length:
                self.drum_step = 0 

            track_1_cv, track_1_sparsity = self.track_1[self.CvPattern][self.track_step]
            track_2_cv, track_2_sparsity = self.track_2[self.CvPattern][self.track_step]
            
            # Set track 1 and 2 voltage outputs based on previously
            # generated random pattern and sparsity. CV only changed
            # if sparsity value is above the current control level. So
            # as sparsity increases, notes decrease.
            
            # if track_1_sparsity > self.sparsity:
            #     # self.cv_1.voltage(track_1_cv)
            #     # self.gate_1.on()
            # else:
            #     # self.gate_1.off()
                
            # if track_2_sparsity > self.sparsity:
            #     self.cv_2.voltage(track_2_cv)
            #     self.gate_2.on()
            # else:
            #     self.gate_2.off()

            # Reset clock step at 128 to avoid a HUGE integer if running for a long time
            # over a really long period of time this would look like a memory leak
            if self.clock_step < 128:
                self.clock_step +=1
            else:
                self.clock_step = 0
    
            # Reset step number at step_length -1 as pattern arrays are zero-based
            if self.drum_step < self.step_length - 1:
                self.drum_step += 1
            else:
                self.drum_step = 0

            if self.track_step < (self.step_length * self.track_multiplier) - 1:
                self.track_step += 1
            else:
                self.track_step = 0

                
        @din.handler_falling
        def clockTriggerEnd():
            self.bd_cv.off()
            self.sn_cv.off()
            self.oh_cv.off()
            self.ch_cv.off()
            self.cy_cv.off()
            self.cl_cv.off()

    def generateNewRandomCVPattern(self):
        """Generate new random CV patterns for the voice tracks"""
        self.step_length = len(self.BD[self.pattern])
        # CV patterns are up to 4 times the length of the drum pattern
        patt = (self.generateRandomPattern(self.step_length, 0, 9) +
                  self.generateRandomPattern(self.step_length, 0, 9) +
                  self.generateRandomPattern(self.step_length, 0, 9) +
                  self.generateRandomPattern(self.step_length, 0, 9))
        self.track_1.append(patt)
        patt = (self.generateRandomPattern(self.step_length, 0, 9) +
                  self.generateRandomPattern(self.step_length, 0, 9) +
                  self.generateRandomPattern(self.step_length, 0, 9) +
                  self.generateRandomPattern(self.step_length, 0, 9))
        self.track_2.append(patt)

    def updatePattern(self):
        """Read from knob 2 or CV (if in appropriate mode) and change the drum pattern accordingly"""
        # If mode 2 and there is CV on the analogue input use it, if
        # not use the knob position
        val = 100 * ain.percent()
        if self.analogInputMode == 2 and val > self.minAnalogInputVoltage:
            self.pattern = int((len(self.BD) / 100) * val)
        else:
            self.pattern = k2.read_position(len(self.BD))
        
        self.step_length = len(self.BD[self.pattern])

    def updateCvPattern(self):
        """Read from CV (if in appropriate mode) and change the CV pattern accordingly"""
        # If analogue input mode 3, get the CV pattern from CV input
        if self.analogInputMode != 3:
            return
        else:
            # Get the analogue input voltage as a percentage
            CvpVal = 100 * ain.percent()
            
            # Is there a voltage on the analogue input and are we configured to use it?
            if CvpVal > 0.4:
                # Convert percentage value to a representative index of the pattern array
                self.CvPattern = int((len(self.track_1) / 100) * CvpVal)

               
    def generateRandomPattern(self, length, min, max):
        """Generate a new random pattern"""
        # Returns a list of pairs of value and a sparsity
        self.t=[]
        # Sparsity values are from 1 to length. This means that notes
        # will progressively drop out as sparsity increases. Using
        # random values would give different behaviour.
        # No shuffle in micropython random :-(
        # sparsities = random.shuffle(range(1,length+1))
        count = 0
        sparsities = []
        numbers = list(range(1,length+1))
        while len(numbers) > 0:
                chosen = choice(numbers)
                sparsities.append(chosen)
                numbers.remove(chosen)
        
        for i in range(0, length):
            self.t.append((uniform(0,9),sparsities[i]))
        return self.t

    def updateSparsity(self):
        """Update sparsity value from knob 1"""
        # Don't use Analog input for now
        self.sparsity = k1.read_position(steps=len(self.BD[self.pattern])+1)

    def updateRandomness(self):
        """Read randomness from CV (if in appropriate mode)"""
        # If mode 1 and there is CV on the analogue input use it
        val = 100 * ain.percent()
        if self.analogInputMode == 1 and val > self.minAnalogInputVoltage:
            self.randomness = val
        
    def main(self):
        while True:
            self.updatePattern()
            self.updateSparsity()
            self.updateRandomness()
            self.updateCvPattern()
            self.updateScreen()
            self.reset_timeout = 500
            # If I have been running, then stopped for longer than
            # reset_timeout, reset the steps and clock_step to 0
            if self.clock_step != 0 and ticks_diff(ticks_ms(), din.last_triggered()) > self.reset_timeout:
                self.drum_step = 0
                self.clock_step = 0

    def visualizePattern(self, pattern):
        self.t = pattern
        self.t = self.t.replace('1','o')
        self.t = self.t.replace('0',' ')
        return self.t

    def visualizeTrack(self, track):
        t = ''
        for i in range(0, len(track)):
            track_cv, track_sparsity = track[i]
            if track_sparsity > self.sparsity:
                t += '.'
            else:
                t += ' '
        return t

    def updateScreen(self):
        oled.fill(0)
        
        

        visual_patterns = [
            self.visualizePattern(self.BD[self.pattern]),
            self.visualizePattern(self.SN[self.pattern]),
            self.visualizePattern(self.CH[self.pattern]),
            self.visualizePattern(self.OH[self.pattern]),
            self.visualizePattern(self.CY[self.pattern]),
            self.visualizePattern(self.CP[self.pattern]),
        ]
        
        raw_line = 0
        for v in visual_patterns:
            oled.text(v,0, raw_line ,1)
            raw_line += 8
        
        oled.text(self.visualizeTrack(self.track_1[self.CvPattern]),0,raw_line-4,1)


        low_margine = 8
        
        # Show randomness
        oled.text('R' + str(int(self.randomness)), 4, OLED_HEIGHT-low_margine, 1)

        # Show sparsity
        oled.text('S' + str(int(self.sparsity)), 32, OLED_HEIGHT-low_margine, 1)    


        # Show CV pattern
        oled.text('C' + str(self.CvPattern), 60, OLED_HEIGHT-low_margine, 1)

        # Show CV pattern
        oled.text('x' + str(self.track_multiplier), 80, OLED_HEIGHT-low_margine, 1)

        # Show the analogInputMode
        oled.text('M' + str(self.analogInputMode), 112, OLED_HEIGHT-low_margine, 1)

        oled.show()

class pattern:

    # Initialize pattern lists
    BD=[]
    SN=[]
    CH=[]
    OH=[]
    CY=[]
    CP=[]

     # Add patterns. This is a smaller number of patterns than in the
    # original Consequencer.
    
    # BD.append("0000000000000000")
    # HH.append("0000000000000000")
    # SN.append("0000000000000000")
    # OH.append("0000000000000000")
    # CY.append("0000000000000000")
    # CP.append("0000000000000000")

    # BD.append("1000100010001000")
    # HH.append("0000000000000000")
    # SN.append("0000000000000000")
    # OH.append("0000000000000000")
    # CY.append("0000000000000000")
    # CP.append("0000000000000000")

    BD.append("1000100010001000")
    SN.append("0100010001000100")
    CH.append("0010001000100010")
    OH.append("0000100010001000")
    CY.append("0000000000000000")
    CP.append("0000000100000101")

    BD.append("1001001010001000")
    SN.append("0000010000111000")
    CH.append("0010001000100011")
    OH.append("0000110110000000")
    CY.append("0000001010000000")
    CP.append("0001000000100000")

    # BD.append("1000100010001000")
    # HH.append("0111011101110111")
    # SN.append("0000000000000000")
    # OH.append("0000000000000000")
    # CY.append("0000000000000000")
    # CP.append("0000000000000000")

    # BD.append("1000100010001000")
    # HH.append("1111111111111111")
    # SN.append("0000000000000000")
    # OH.append("0000000000000000")
    # CY.append("0000000000000000")
    # CP.append("0000000000000000")

    # BD.append("0000000000000000")
    # HH.append("0010001000100010")
    # SN.append("0000000000000000")
    # OH.append("0000000000000000")
    # CY.append("0000000000000000")
    # CP.append("0000000000000000")

    # BD.append("1000100010001000")
    # HH.append("0000000001111111")
    # SN.append("0000000000000000")
    # OH.append("0000000000000000")
    # CY.append("0000000000000000")
    # CP.append("0000000000000000")

    # BD.append("0000000000000000")
    # HH.append("1111111011111110")
    # SN.append("0000000000000000")
    # OH.append("0000000000000000")
    # CY.append("0000000000000000")
    # CP.append("0000000000000000")

    # BD.append("1000100010010100")
    # HH.append("1111111011101110")
    # SN.append("0000000000000000")
    # OH.append("0000000000000000")
    # CY.append("0000000000000000")
    # CP.append("0000000000000000")

    # BD.append("1000001100100000")
    # HH.append("1111111111111111")
    # SN.append("0000000000000000")
    # OH.append("0000000000000000")
    # CY.append("0000000000000000")
    # CP.append("0000000000000000")

    # BD.append("1000100010001000")
    # HH.append("1111101111111101")
    # SN.append("0000000000000000")
    # OH.append("0000000000000000")
    # CY.append("0000000000000000")
    # CP.append("0000000000000000")

    # BD.append("1000100010010100")
    # HH.append("0010001000100011")
    # SN.append("0000000000000000")
    # OH.append("0000000000000000")
    # CY.append("0000000000000000")
    # CP.append("0000000000000000")

    # BD.append("1000100010010010")
    # HH.append("0000000000000000")
    # SN.append("0000000000000000")
    # OH.append("0000000000000000")
    # CY.append("0000000000000000")
    # CP.append("0000000000000000")

    # BD.append("1000100010010010")
    # HH.append("0010001000100010")
    # SN.append("0000000000000000")
    # OH.append("0000000000000000")
    # CY.append("0000000000000000")
    # CP.append("0000000000000000")

if __name__ == '__main__':
    # Reset module display state.
    oled.fill(0)
    [cv.off() for cv in cvs]
    hm = Hamlet()
    hm.main()



