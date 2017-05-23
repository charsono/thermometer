from enum import Enum

'''
Direction enum to indicate from which direction would a threshold be triggered
'''
class Direction(Enum):
    GREATER = 1
    LESSER = -1
    ANY = 0

    
'''
Listing all acceptable temperature unit
'''
class TemperatureUnit(Enum):
    CELCIUS = 'C'
    FAHRENHEIT = 'F'


'''
Operation that could be done with temperature (i.e convertion)
'''
class Temperature:
    @staticmethod
    def convert_fahrenheit_to_celcius(temperature):
        return (temperature - 32) * 5/9.0

    @staticmethod
    def convert_celcius_to_fahrenheit(temperature):
        return temperature * 9/5.0 + 32

    '''
    Convert temperature to the appropriate format for storing
    '''
    @staticmethod
    def format_temperature(temperature, store_mode, current_mode):
        # Storing mode is in Celcius, but current mode is in Farenheit, so convert to celcius for storing
        if store_mode == TemperatureUnit.CELCIUS and current_mode == TemperatureUnit.FAHRENHEIT:  
            temperature = Temperature.convert_fahrenheit_to_celcius(temperature)
        # Storing mode is in Farenheit, but current mode is in Celcius, so convert to Fahrenheit for storing
        elif store_mode == TemperatureUnit.FAHRENHEIT and current_mode == TemperatureUnit.CELCIUS: 
            temperature = Temperature.convert_celcius_to_fahrenheit(temperature)
            
        return temperature


'''
Represent a Threshold
'''
class Threshold:
    def __init__(self, name, thresh_val, unit=TemperatureUnit.CELCIUS, direction=Direction.ANY):
        self.name = name

        # Store threshold value in both celcius and fahrenheit. If there are more unit, should probably be changed to a dictionary
        if unit == TemperatureUnit.CELCIUS:
            self.thresh_val_c = thresh_val
            self.thresh_val_f = Temperature.convert_celcius_to_fahrenheit(thresh_val)
        else:
            self.thresh_val_f = thresh_val
            self.thresh_val_c = Temperature.convert_fahrenheit_to_celcius(thresh_val)
                        
        self.direction = direction

        # Indicate if threshold has been triggered recently
        self.reached = False


class Thermometer:
    def __init__(self, thresholds=[], fluctuations=(0.0, 'C'), output_unit=TemperatureUnit.CELCIUS,):
        self.__prev_data = None  # Used to store previuos data
        self.__prev_triggered = None  # Used to store the temperature that previouly get triggered
        self.__store_mode = output_unit  # Indicate the storing mode of thermometer, it is set to the first output_unit that was indicated
        
        self.output_unit = output_unit  # Indicate the output unit, this can be change
    
        self.set_fluctuations(fluctuations)

        # Thresholds is in the form of {threshold_value: [All threshold with the same threhold value], ...}
        self.thresholds = {}
        for thresh in thresholds:
            self.add_threshold(thresh)

    '''
    Setting fluctuations temperature, while taking account the unit
    fluctuations = (temperature, unit)
    insignificant changes are changes within +/- temperature
    '''
    def set_fluctuations(self, fluctuations):
        self.__fluctuations_unit= TemperatureUnit(fluctuations[1].upper())
        self.__fluctuations_temp = fluctuations[0]

        # Note the helper function Format temperature could not be used for this, because this is used as a difference between 2 temperature.
        # This means the constant 32 should not be taken into the conversion
        # Storing mode is in Celcius, but input unit is in Farenheit
        if self.__store_mode == TemperatureUnit.CELCIUS and self.__fluctuations_unit == TemperatureUnit.FAHRENHEIT:
            self.__fluctuations_temp = Temperature.convert_fahrenheit_to_celcius(32+ self.__fluctuations_temp)
        # Storing mode is in Farenheit, but input unit is in Celcius
        elif self.__store_mode == TemperatureUnit.FAHRENHEIT and self.__fluctuations_unit == TemperatureUnit.CELCIUS:
            self.__fluctuations_temp = Temperature.convert_celcius_to_fahrenheit(self.__fluctuations_temp) - 32
                                       
    def add_threshold(self, threshold):
        # Set key based on storing mode
        if self.__store_mode == TemperatureUnit.CELCIUS:
            key = threshold.thresh_val_c
        else:
            key = threshold.thresh_val_f
            
        if key not in self.thresholds:
            self.thresholds[key] = [threshold]
        else:
            self.thresholds[key].append(threshold)

    '''
    Remove Threshold based on threshold value and name of threshold
    '''
    def remove_thershold(self, thresh_val, unit, name):
        key = Temperature.format_temperature(thresh_val, self.__store_mode, unit)
        if key not in self.thresholds:
            return False
        else:
            thresholds_at_key =self.thresholds[key]
            for i in range(0, len(thresholds_at_key)):
                threshold = thresholds_at_key[i]
                if threshold.name == name:
                    thresholds_at_key.pop(i)
                    return True
            return False
            
    '''
    Read data_pt and produce output accordingly
    data_pt is in the form (temperature, unit)
    '''
    def read(self, data_pt):
        result = []  # Array of strings that would be printed
        curr_unit = data_pt[1].upper()
        
        if curr_unit not in ['C', 'F']:
            result.append("Invalid Unit")
            return result

        # Convert current temperature to the stored unit
        curr_unit = TemperatureUnit(curr_unit)
        curr_temp = Temperature.format_temperature(data_pt[0], self.__store_mode, curr_unit)
        
        if self.__prev_data is None:
            self.__prev_data = curr_temp

        # Convert output temperature to the output unit
        output_temp = Temperature.format_temperature(curr_temp, self.output_unit, self.__store_mode)
        if curr_temp in self.thresholds:  # Trigger threshold
            for thresh in self.thresholds[curr_temp]:
                #  If temperature is reached from the wrong direction, or is still in fluctuations, dont trigger
                if (thresh.direction == Direction.GREATER and self.__prev_data < curr_temp) or \
                    (thresh.direction == Direction.LESSER and self.__prev_data > curr_temp) or \
                    (thresh.reached and abs(curr_temp-self.__prev_data) - self.__fluctuations_temp <= 1E-5):
                     continue
                else:  # Triggering Threshold
                    s = "%s threshold has been reached at %.1f%s" % (thresh.name, output_temp, self.output_unit.value)
                    result.append(s)
                    thresh.reached = True
                    self.__prev_triggered = curr_temp

        # When curr temperature is not within the fluctuations area of the previously triggered temperature,
        # reset the state of threshold for the next trigger
        elif self.__prev_triggered is not None and abs(curr_temp-self.__prev_triggered) - self.__fluctuations_temp>1E-5:
            for thresh in self.thresholds[self.__prev_triggered]:
                thresh.reached = False
            self.__prev_triggered = None

        # If nothing has been printed, just print the temperature that was read
        if not result:
            s = "%.1f%s" % (output_temp, self.output_unit.value)
            result.append(s)
    
        self.__prev_data = curr_temp  # Update previous data variable
        return result







