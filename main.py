from classes import Direction, Thermometer, Threshold, TemperatureUnit

data_array = [
    (1.5,'C'),
    (1.0,'C'),
    (0.5,'C'),
    (0.0,'C'),
    (-0.5,'C'),
    (0.0,'C'),
    (-0.5,'C'),
    (32,'F'),
    (0.5,'C'),
    (0.0,'C'),
    (1.0,'C'),
    (0.5,'C'),
    (0.0,'C'),
    (-1.0,'C'),
    (0.0,'C'),
    (1.5,'C'),
    (90.0,'C'),
    (95.5,'C'),
    (212.0,'F'),
    (105.5,'C'),
    (100.0,'C'),
    (99.5,'C'),
    (212.0,'F'),
    (99,'C'),
    (100.0,'C')]

thresholds = [
    Threshold('Freezing', 0.0, unit=TemperatureUnit.CELCIUS),
    Threshold('Boiling', 100.0,  unit=TemperatureUnit.CELCIUS),
    Threshold('Freezing 2', 0.0,  unit=TemperatureUnit.CELCIUS),
    Threshold('Freezing 3', 0.0,  unit=TemperatureUnit.CELCIUS, direction=Direction.GREATER),
    Threshold('Boiling_2', 100.0,  unit=TemperatureUnit.CELCIUS, direction=Direction.LESSER),
    Threshold('Boiling Fahrenheit fail' , 100.0, unit=TemperatureUnit.FAHRENHEIT),
    Threshold('Freezing Fahrenheit', 32.0, unit=TemperatureUnit.FAHRENHEIT, direction=Direction.LESSER)
    ]

therm = Thermometer(thresholds, (0.5, 'C'), output_unit=TemperatureUnit.FAHRENHEIT)

for data_pt in data_array:
    result = therm.read(data_pt)
    for r in result:
        print (r)
