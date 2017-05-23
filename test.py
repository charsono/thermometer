from classes import Temperature, Threshold, Thermometer, TemperatureUnit, Direction
import unittest
import sys
import io
from random import randrange


class TemperatureUnitTest(unittest.TestCase):
    def test_convert_string_to_enum(self):
        self.assertEqual(TemperatureUnit.CELCIUS, TemperatureUnit('C'))
        self.assertEqual(TemperatureUnit.FAHRENHEIT, TemperatureUnit('F'))

class TemperatureTest(unittest.TestCase):
    def test_convert_fahrenheit_to_celcius(self):
        self.assertEqual(0, Temperature.convert_fahrenheit_to_celcius(32))
        self.assertEqual(40, Temperature.convert_fahrenheit_to_celcius(104))
        self.assertEqual(-50, Temperature.convert_fahrenheit_to_celcius(-58))

    def test_convert_celcius_to_fahrenheit(self):
        self.assertEqual(32, Temperature.convert_celcius_to_fahrenheit(0))
        self.assertEqual(104, Temperature.convert_celcius_to_fahrenheit(40))
        self.assertEqual(-58, Temperature.convert_celcius_to_fahrenheit(-50))

    def test_format_temperature_1(self):
        store_mode = TemperatureUnit.CELCIUS
        current_mode = TemperatureUnit.FAHRENHEIT
        self.assertEqual(0, Temperature.format_temperature(32, store_mode, current_mode))
        self.assertEqual(40, Temperature.format_temperature(104, store_mode, current_mode))
        self.assertEqual(-50, Temperature.format_temperature(-58, store_mode, current_mode))

    def test_format_temperature_2(self):
        current_mode = TemperatureUnit.CELCIUS
        store_mode = TemperatureUnit.FAHRENHEIT
        
        self.assertEqual(32, Temperature.format_temperature(0, store_mode, current_mode))
        self.assertEqual(104, Temperature.format_temperature(40, store_mode, current_mode))
        self.assertEqual(-58, Temperature.format_temperature(-50, store_mode, current_mode))

    def test_format_temperature_3(self):
        current_mode = TemperatureUnit.FAHRENHEIT
        store_mode = TemperatureUnit.FAHRENHEIT
        
        self.assertEqual(0, Temperature.format_temperature(0, store_mode, current_mode))
        self.assertEqual(40, Temperature.format_temperature(40, store_mode, current_mode))

    def test_format_temperature_4(self):
        current_mode = TemperatureUnit.CELCIUS
        store_mode = TemperatureUnit.CELCIUS
        
        self.assertEqual(0, Temperature.format_temperature(0, store_mode, current_mode))
        self.assertEqual(40, Temperature.format_temperature(40, store_mode, current_mode))
        

class ThresholdTest(unittest.TestCase):
    def test_init(self):
        name = 'test1'
        thresh_val = randrange(0, 10)
        threshold_1 = Threshold(name, thresh_val)

        self.assertEqual(threshold_1.name, name)
        self.assertEqual(threshold_1.thresh_val_c, thresh_val)
        self.assertEqual(threshold_1.thresh_val_f, Temperature.convert_celcius_to_fahrenheit(thresh_val))
        self.assertEqual(threshold_1.direction, Direction.ANY)
        self.assertFalse(threshold_1.reached)

    def test_init_2(self):
        name = 'test1'
        thresh_val = randrange(0, 10)
        direction = Direction.GREATER
        unit = TemperatureUnit.FAHRENHEIT
        threshold_1 = Threshold(name, thresh_val, unit, direction)
        
        self.assertEqual(threshold_1.name, name)
        self.assertEqual(threshold_1.thresh_val_f, thresh_val)
        self.assertEqual(threshold_1.thresh_val_c, Temperature.convert_fahrenheit_to_celcius(thresh_val))
        self.assertEqual(threshold_1.direction, direction)
        self.assertFalse(threshold_1.reached)


class ThermometerTest(unittest.TestCase):
    def setUp(self):
        self.thresholds = [
            Threshold('Freezing', 0.0, unit=TemperatureUnit.CELCIUS),
            Threshold('Boiling', 100.0,  unit=TemperatureUnit.CELCIUS),
            Threshold('Freezing 2', 0.0,  unit=TemperatureUnit.CELCIUS),
            Threshold('Freezing 3', 0.0,  unit=TemperatureUnit.CELCIUS, direction=Direction.GREATER),
            Threshold('Boiling_2', 100.0,  unit=TemperatureUnit.CELCIUS, direction=Direction.LESSER),
            Threshold('Boiling Fahrenheit fail' , 100.0, unit=TemperatureUnit.FAHRENHEIT),
            Threshold('Freezing Fahrenheit', 32.0, unit=TemperatureUnit.FAHRENHEIT, direction=Direction.LESSER)
        ]
        self.therm_c = Thermometer(self.thresholds)
        self.therm_f= Thermometer(self.thresholds, output_unit=TemperatureUnit.FAHRENHEIT)
                                  
        
    def test_set_fluctuations(self):
        self.therm_f.set_fluctuations((0.5, 'C'))
        self.assertTrue(abs(self.therm_f._Thermometer__fluctuations_temp - 0.9) < 1E-5)

        self.therm_c.set_fluctuations((0.9, 'F'))
        self.assertTrue(abs(self.therm_c._Thermometer__fluctuations_temp - 0.5) < 1E-5)

        self.therm_f.set_fluctuations((0.5, 'F'))
        self.assertTrue(abs(self.therm_f._Thermometer__fluctuations_temp - 0.5) < 1E-5)

        self.therm_c.set_fluctuations((0.9, 'C'))
        self.assertTrue(abs(self.therm_c._Thermometer__fluctuations_temp - 0.9) < 1E-5)

    def test_add_threshold_c(self):
        threshold_at_0 = self.therm_c.thresholds[0.0]
        threshold_at_100 = self.therm_c.thresholds[100]

        self.assertEqual(len(threshold_at_0), 4)
        self.assertEqual(len(threshold_at_100), 2)

    def test_add_threshold_f(self):
        threshold_at_0 = self.therm_f.thresholds[32.0]
        threshold_at_100_f = self.therm_f.thresholds[100]
        threshold_at_100_c = self.therm_f.thresholds[212]

        self.assertEqual(len(threshold_at_0), 4)
        self.assertEqual(len(threshold_at_100_f), 1)
        self.assertEqual(len(threshold_at_100_c), 2)

    def test_read_no_fluctuations(self):
        data_points = [(0.5,'C'), (0.0,'C'), (-0.5,'C'), (0.0,'C')]
        result = []
        for dp in data_points:
            result.extend(self.therm_c.read(dp))

        self.assertEqual(len(result), 8)
        self.assertEqual('0.5C', result[0])
        for res in result[1:4]:
            self.assertIn('threshold has been reached at 0.0C', res)
        self.assertEqual('-0.5C', result[4])
        for res in result[5:]:
            self.assertIn('threshold has been reached at 0.0C', res)

    def test_read_fluctuations(self):
        data_points = [(0.5,'C'), (0.0,'C'), (-0.5,'C'), (0.0,'C'), (0.5,'C'), (1.0,'C'), (-0.5,'C'), (0.0,'C')]
        self.therm_c.set_fluctuations((0.5, 'c'))
        
        result = []
        for dp in data_points:
            result.extend(self.therm_c.read(dp))

        self.assertEqual(len(result), 12)
        self.assertEqual('0.5C', result[0])
        for res in result[1:4]:
            self.assertIn('threshold has been reached at 0.0C', res)
        self.assertEqual('-0.5C', result[4])
        self.assertIn('Freezing Fahrenheit threshold has been reached', result[5])
        self.assertEqual('0.5C', result[6])
        for res in result[9:]:
            self.assertIn('threshold has been reached at 0.0C', res)

    def test_read_different_unit_1(self):
        data_points = [(0.5,'C'), (0.0,'C'), (-0.5,'C'), (0.0,'C'), (0.5,'C'), (34,'F'), (-0.5,'C'), (32.0,'F')]
        self.therm_f.set_fluctuations((0.5, 'c'))
        
        result = []
        for dp in data_points:
            result.extend(self.therm_f.read(dp))

        self.assertEqual(len(result), 12)
        self.assertEqual('32.9F', result[0])
        for res in result[1:4]:
            self.assertIn('threshold has been reached at 32.0F', res)
        self.assertEqual('31.1F', result[4])
        self.assertIn('Freezing Fahrenheit threshold has been reached', result[5])
        self.assertEqual('32.9F', result[6])
        for res in result[9:]:
            self.assertIn('threshold has been reached at 32.0F', res)

    def test_read_different_unit_2(self):
        data_points = [(32.9,'F'), (32.0,'F'), (-0.5,'C'), (32.0,'F'), (0.5,'C'), (34,'F'), (-0.5,'C'), (32.0,'F')]
        self.therm_c.set_fluctuations((0.9, 'f'))
        
        result = []
        for dp in data_points:
            result.extend(self.therm_c.read(dp))

        self.assertEqual(len(result), 12)
        self.assertEqual('0.5C', result[0])
        for res in result[1:4]:
            self.assertIn('threshold has been reached at 0.0C', res)
        self.assertEqual('-0.5C', result[4])
        self.assertIn('Freezing Fahrenheit threshold has been reached', result[5])
        self.assertEqual('0.5C', result[6])
        for res in result[9:]:
            self.assertIn('threshold has been reached at 0.0C', res)

    def test_read_change_output_mode(self):
        data_points = [(0.5,'C'), (0.0,'C'), (-0.5,'C'), (0.0,'C'), (0.5,'C'), (1.0,'C'), (-0.5,'C'), (0.0,'C')]
        self.therm_c.set_fluctuations((0.5, 'c'))
        self.therm_c.output_unit = TemperatureUnit.FAHRENHEIT
        
        result = []
        for dp in data_points:
            result.extend(self.therm_c.read(dp))
 
        self.assertEqual(len(result), 12)
        self.assertEqual('32.9F', result[0])
        for res in result[1:4]:
            self.assertIn('threshold has been reached at 32.0F', res)
        self.assertEqual('31.1F', result[4])
        self.assertIn('Freezing Fahrenheit threshold has been reached', result[5])
        self.assertEqual('32.9F', result[6])
        for res in result[9:]:
            self.assertIn('threshold has been reached at 32.0F', res)

    def test_read_invalid_unit(self):
        data_points = [(32.9,'F'), (32.0,'G'), (-0.5,'C')]
        self.therm_c.set_fluctuations((0.9, 'f'))
        
        result = []
        for dp in data_points:
            result.extend(self.therm_c.read(dp))

        self.assertEqual(len(result), 3)
        self.assertEqual('0.5C', result[0])
        self.assertEqual('Invalid Unit', result[1])
        self.assertEqual('-0.5C', result[2])

    def test_remove_threshold(self):
        self.assertEqual(len(self.therm_c.thresholds[0.0]), 4)
        self.assertTrue(self.therm_c.remove_thershold(0.0, TemperatureUnit.CELCIUS, 'Freezing 2'))
        self.assertEqual(len(self.therm_c.thresholds[0.0]), 3)

        data_points = [(0.5,'C'), (0.0,'C'), (-0.5,'C'), (0.0,'C')]
        result = []
        for dp in data_points:
            result.extend(self.therm_c.read(dp))

        self.assertEqual(len(result), 6)
        self.assertEqual('0.5C', result[0])
        for res in result[1:3]:
            self.assertIn('threshold has been reached at 0.0C', res)
        self.assertEqual('-0.5C', result[3])
        for res in result[5:]:
            self.assertIn('threshold has been reached at 0.0C', res)
            
    def test_remove_threshold_fail(self):
        self.assertEqual(len(self.therm_c.thresholds[0.0]), 4)
        self.assertFalse(self.therm_c.remove_thershold(0.0, TemperatureUnit.CELCIUS, 'Test 2'))
        self.assertEqual(len(self.therm_c.thresholds[0.0]), 4)

        self.assertFalse(self.therm_c.remove_thershold(32.0, TemperatureUnit.CELCIUS, 'Test 2'))
     
if __name__ == '__main__':
    unittest.main()
