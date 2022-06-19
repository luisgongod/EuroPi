"""
Modified from diagnotic.py to be used with the europi_dev board.
Use with original in lib/europi.py

"""

# from machine import ADC
from time import sleep
from machine import Pin
from europi import OLED_HEIGHT, OLED_WIDTH, b1, b2, cv1, cv2, cv3, cv4, cv5, cv6, din, k1, k2, oled
from europi import AnalogueInput, Knob, DigitalInput


# from europi_script import EuroPiScript
LOW = 0
HIGH = 1

class Mux():    
    def __init__(self, pin, address_A_pin, address_B_pin, address_C_pin):
        self.pin = pin
        self.address_A_pin = Pin(address_A_pin, Pin.OUT) 
        self.address_B_pin = Pin(address_B_pin, Pin.OUT)
        self.address_C_pin = Pin(address_C_pin, Pin.OUT)       
        
        self.address_A_pin.value(LOW)
        self.address_B_pin.value(LOW)
        self.address_C_pin.value(LOW)       
                        
    
    # Set address (0-8) from pin (A-C),
    def set_channel(self, channel):
        self.address_A_pin.value(channel & 0b00000001)
        self.address_B_pin.value(channel & 0b00000010)
        self.address_C_pin.value(channel & 0b00000100)



class MuxAnalogueInput():
    """
    modified/copy AnalogInput class to work with the mux
    the methods are the same as the original class, but change of channel of the Mux is done before calling each method
    ¯\_(ツ)_/¯ calibration works on this? I don't know.    
    """
    

    def __init__(self, mux,channel):
        self.analogueInput = AnalogueInput(mux.pin)
        self.mux = mux
        self.channel = channel

    def percent(self):
        self.mux.set_channel(self.channel)        
        return self.analogueInput.percent()

    def read_voltage(self):
        self.mux.set_channel(self.channel)        
        return self.analogueInput.read_voltage()

class MuxKnob():
    """
    modified Knob class to work with the mux
    the methods are the same as the original Knob class, but change of channel of the Mux is done before calling each method
    ¯\_(ツ)_/¯ calibration works on this? I don't know.    
    """

    def __init__(self, mux, channel):
        self.knob = Knob(mux.pin)
        self.mux = mux
        self.channel = channel

    def percent(self):
        self.mux.set_channel(self.channel)        
        return self.knob.percent()

    def read_position(self):
        self.mux.set_channel(self.channel)        
        return self.knob.read_position()



def main():

    m0 = Mux(26,7,8,9)
    #Knob channels (left to right) 3,2,1,0
    mk1 = MuxKnob(m0,3)
    mk2 = MuxKnob(m0,2)
    mk3 = MuxKnob(m0,1)
    mk4 = MuxKnob(m0,0)
    
    #AnalogIn channels (left to right) 5,7,4,6
    ma1 = MuxAnalogueInput(m0,5)
    ma2 = MuxAnalogueInput(m0,7)
    ma3 = MuxAnalogueInput(m0,4)
    ma4 = MuxAnalogueInput(m0,6)
    din2 = DigitalInput(6)

    while True:

        oled.fill(0)
        
        channel = 0

        # display the input values
        #display.text('Hello World', 0, 0, 1)    # draw some text at x=0, y=0, colour=1
        # oled.text(f"ain: {ain.read_voltage():5.2f}v ch:{channel}", 2, 3, 1)
        oled.text(f"k1: {k1.read_position():2}  k2: {k2.read_position():2}", 2, 13, 1)
        oled.text(f"d1{din2.value()} b1{b1.value()} b2{b2.value()} d2{din.value()}", 2, 23, 1)
        oled.text(f"Ks:{mk1.read_position():2} {mk2.read_position():2} {mk3.read_position():2} {mk4.read_position():2}", 2, 33, 1)
        oled.text(f"As:{ma1.read_voltage():5.2f} {ma2.read_voltage():5.2f}", 2, 43, 1)
        oled.text(f"As:{ma3.read_voltage():5.2f} {ma4.read_voltage():5.2f}", 2, 53, 1)

        # show the screen boundaries
        oled.rect(0, 0, OLED_WIDTH, OLED_HEIGHT, 1)
        oled.show()

        sleep(0.1)


if __name__ == "__main__":
    main()







