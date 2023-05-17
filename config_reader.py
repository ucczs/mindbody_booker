
import yaml

class WorkoutSlot:
    def __init__(self, weekday, hour, type):
        self.weekday = weekday
        self.hour = hour
        self.type = type

    def __str__(self):
        str_return = f"day: {self.weekday}, time: {self.hour}, type: {self.type}"
        return str_return


class BookingConfig:
    EXPECTED_STRUCTURE = {
        'weekday': str,
        'time': str,
        'type': str
    }

    def __init__(self, config_file):
        self.config_file = config_file
        self.desired_slots = []
        self._readInYaml()

    def __str__(self):
        output = ''
        for workout in self.desired_slots:
            output += workout.weekday + ", " + workout.hour + ", " + workout.type + "\n"
        return output

    def _readInYaml(self):
        with open(self.config_file, 'r') as f:
            yaml_data = yaml.safe_load(f)

        if self._checkYamlStructure(yaml_data):
            for item in yaml_data:
                weekday = item['weekday']
                time = item['time']
                exercise_type = item['type']
                new_slot = WorkoutSlot(weekday, time, exercise_type)
                self.desired_slots.append(new_slot)

    def _checkYamlStructure(self, yaml_data):
        for item in yaml_data:
            for key, value_type in BookingConfig.EXPECTED_STRUCTURE.items():
                if key not in item:
                    raise ValueError(f'YAML file is missing required key "{key}"')
                if not isinstance(item[key], value_type):
                    raise TypeError(f'Invalid value type for key "{key}". Expected {value_type}, but got {type(item[key])}')
                
        return True

    def get_booking_of_weekday(self, weekday):
        for desired_slot in self.desired_slots:
            if desired_slot.weekday == weekday:
                return desired_slot
        return None
