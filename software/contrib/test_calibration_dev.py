#test_calibration_dev.py
#bug found! inverted values of voltage reading, Sample = 0xffff - Sample 
#INPUT_CALIBRATION_VALUES=[65532, 60981, 54945, 48837, 42690, 36745, 30566, 24562, 18436, 12323, 6346]

from time import sleep
from machine import Pin, ADC, PWM, freq
from europi_dev import oled, b1, b2, m0, ma1,ma2, ma3, ma4
cv1 = PWM(Pin(19))#most left in dev
ain = ADC(Pin(26, Pin.IN, Pin.PULL_DOWN))

#readings=[65532, 6346]
readings=[392,65532]

m0.set_channel(ma1.channel)
        
SAMPLE_SIZE = 128
def sample():
    readings = []
    for reading in range(SAMPLE_SIZE):
        readings.append(ain.read_u16())
                
    return (0xffff - round(sum(readings) / SAMPLE_SIZE))


new_readings = [readings[0]]
m = (readings[1] - readings[0]) / 10
c = readings[0]
for x in range(1, 10):
    new_readings.append(round((m * x) + c))
new_readings.append(readings[1])
readings = new_readings
print(readings)


output_duties = [0]
duty = 0
cv1.duty_u16(duty)
reading = sample()
print("first sample",reading)

#[65532, 59613, 53695, 47776, 41858, 35939, 30020, 24102, 18183, 12265, 6346]
#TODO: Calibratron for all outputs        
if 1:
    for index, expected_reading in enumerate(readings[1:]):
        print("expect reading", expected_reading)
        while abs(reading - expected_reading) > 0.002 and reading < expected_reading:
            cv1.duty_u16(duty)        
            duty += 10
            reading = sample()
            
            if duty>=0xffff:
                break
            
            #print("\tsample",reading)
        #sleep(0.5)
        print(reading, duty)
        output_duties.append(duty)
        #oled.centre_text(f"Calibrating...\n{index+1}V")

print(output_duties)
#with open(CALIBRATION_FILE, "a+") as file:
 #   values = ", ".join(map(str, output_duties))
  #  file.write(f"\nOUTPUT_CALIBRATION_VALUES=[{values}]")

