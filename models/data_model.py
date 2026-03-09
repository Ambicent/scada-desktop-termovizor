from typing import Dict


class Pump:
    def __init__(self, name: str):
        self.name = name
        self.status = "Остановка"
        self.pressure_in = 0.0
        self.pressure_out = 0.0


class Boiler:
    def __init__(self, name: str):
        self.name = name
        self.status = "Остановка"
        self.temperature = 0.0
        self.temp_return = 0.0
        self.pressure_supply = 0.0
        self.pressure_return = 0.0
        self.bunker_level = 0.0


class NetworkCircuit:
    def __init__(self):
        self.pump1 = Pump("Насос 1")
        self.pump2 = Pump("Насос 2")
        self.pressure_before = 0.0
        self.pressure_after = 0.0
        self.temp_supply = 0.0
        self.temp_return = 0.0


class DataModel:
    def __init__(self):
        self.boilers: Dict[int, Boiler] = {
            i: Boiler(f"Котёл {i}") for i in range(1, 4)
        }
        self.dymososy = {
            1: Pump("Дымосос 1"),
            2: Pump("Дымосос 2"),
        }
        self.kotlovoy = {
            f"pump{i}": Pump(f"Насос {i}") for i in range(1, 4)
        }
        self.network = NetworkCircuit()
        self.outdoor_temperature = 0.0
