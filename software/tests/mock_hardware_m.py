from machine import ADC, Pin

from contrib.europi_m import AnalogueReader, DigitalReader,MuxAnalogueInput,MuxKnob


class MockHardware:
    """A class used in tests to stand in for actual EuroPi hardware. Allows a test to set the values for various
    hardware components, such as the position of a knob. Then a test can run a script and assert the script's behavior.
    """

    def __init__(self, monkeypatch):
        self._monkeypatch = monkeypatch
        self._adc_pin_values = {}
        self._digital_pin_values = {}

        self._patch()

    def _patch(self):
        self._monkeypatch.setattr(ADC, "read_u16", lambda pin: self._adc_pin_values[pin])
        self._monkeypatch.setattr(Pin, "value", lambda pin: self._digital_pin_values[pin])

    def set_ADC_u16_value(self, reader: AnalogueReader, value: int):
        """Sets the value that will be returned by a call to `read_u16` on the given AnalogueReader."""
        self._adc_pin_values[reader.pin] = value

    def set_digital_value(self, reader: DigitalReader, value: bool):
        """Sets the value that will be returned by a call to `value` on the given DigitalReader."""
        self._digital_pin_values[reader.pin] = not value


    def set_mux_ADC_u16_value(self, reader: MuxKnob, value: int):
        """Sets the value that will be returned by a call to `read_u16` on the given mux(knob or Input) AnalogueReader."""
        self._adc_pin_values[reader._knob.pin] = value

    # def set_mux_address_pins(self, reader: Mux, value: int):
    #     """Sets the value that will be returned by a call to `value` on the given Mux's address pins."""
    #     self._digital_pin_values[reader.address_A_pin] = (value & 0b00000001)
    #     self._digital_pin_values[reader.address_B_pin] = (value & 0b00000010)
    #     self._digital_pin_values[reader.address_C_pin] = (value & 0b00000100)
