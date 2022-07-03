from distutils.util import change_root
import pytest

from contrib.europi_m import k1, k2, MAX_UINT16, mks,mas,AnalogueReader

from mock_hardware_m import MockHardware

#Mux knobs
@pytest.mark.parametrize(
    "value, expected",
    [
        (0, 1.0000),
        (MAX_UINT16 / 4, 0.7500),
        (MAX_UINT16 / 3, 0.6667),
        (MAX_UINT16 / 2, 0.5000),
        (MAX_UINT16, 0.0000),

    ]
)
def test_Muxknob_percent(mockHardware: MockHardware, value, expected):
    for i in range(len(mks)):
        mockHardware.set_mux_ADC_u16_value(mks[i], value)
        assert round(mks[i]._knob.percent(), 4) == expected # 4: precision


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, 99),
        (MAX_UINT16 / 4, 74),
        (MAX_UINT16 / 3, 66),
        (MAX_UINT16 / 2, 49),
        (MAX_UINT16, 0),
    ],
)
def test_Muxknob_read_position(mockHardware: MockHardware, value, expected):
     for i in range(len(mks)):
        mockHardware.set_mux_ADC_u16_value(mks[i], value)
        assert mks[i]._knob.read_position() == expected 

def test_knobs_are_independent(mockHardware: MockHardware):
    mockHardware.set_mux_ADC_u16_value(mks[0], 0)
    mockHardware.set_mux_ADC_u16_value(mks[1], MAX_UINT16/4)
    mockHardware.set_mux_ADC_u16_value(mks[2], MAX_UINT16/2)
    mockHardware.set_mux_ADC_u16_value(mks[3], MAX_UINT16)
    
    assert mks[0]._knob.percent() == 1.0
    assert round(mks[1]._knob.percent(),2) == 0.75
    assert round(mks[2]._knob.percent(),2) == 0.5
    assert mks[3]._knob.percent() == 0.0



# Mux Analogue Input


@pytest.fixture
def analogueReader():
    return AnalogueReader(pin=1)  # actual pin value doesn't matter


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, 0.0000),
        (MAX_UINT16 / 4, 0.2500),
        (MAX_UINT16 / 3, 0.3333),
        (MAX_UINT16 / 2, 0.5000),
        (MAX_UINT16, 1.0000),
    ],
)
def test_MuxIn_percent(mockHardware: MockHardware, analogueReader, value, expected):
    for i in range(len(mas)):
        mockHardware.set_ADC_u16_value(mas[i]._analogue_input, value)
        assert round(mas[i]._analogue_input.percent(), 2) == expected # 4: precision

@pytest.mark.parametrize(
    "value, expected",
    [
        (0, 0),
        (MAX_UINT16 / 4, 25),
        (MAX_UINT16 / 3, 33),
        (MAX_UINT16 / 2, 50),
        (MAX_UINT16, 99),
    ],
)
def test_MuxIn_range(mockHardware: MockHardware, analogueReader, value, expected):
    for i in range(len(mas)):
        mockHardware.set_ADC_u16_value(mas[i]._analogue_input, value)
        assert mas[i]._analogue_input.range() == expected


@pytest.mark.parametrize(
    "values, value, expected",
    [
        ([i for i in range(10)], 0, 0),
        ([i for i in range(10)], MAX_UINT16 / 4, 2),
        ([i for i in range(10)], MAX_UINT16 / 3, 3),
        ([i for i in range(10)], MAX_UINT16 / 2, 5),
        ([i for i in range(10)], MAX_UINT16, 9),
        (["a", "b"], 0, "a"),
        (["a", "b"], MAX_UINT16, "b"),
    ],
)
def test_MuxIn_choice(mockHardware: MockHardware, analogueReader, values, value, expected):
    for i in range(len(mas)):

        mockHardware.set_ADC_u16_value(mas[i]._analogue_input, value)

        assert mas[i]._analogue_input.choice(values) == expected
