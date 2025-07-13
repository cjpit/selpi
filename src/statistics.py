from muster import Muster
from memory import variable
from datetime import datetime




class Statistics():
    def __init__(self):
        self.__muster = Muster()
        self.__scale_variables = [
            variable.create('CommonScaleForAcVolts'),
            variable.create('CommonScaleForAcCurrent'),
            variable.create('CommonScaleForDcVolts'),
            variable.create('CommonScaleForDcCurrent'),
            variable.create('CommonScaleForTemperature'),
            variable.create('CommonScaleForInternalVoltages'),
        ]
        self.__variables = [
            variable.create('CombinedKacoAcPowerHiRes'),
            variable.create('LoadAcPower'),
            variable.create('ACLoadkWhTotalAcc'),
            variable.create('BatteryVolts'),
            variable.create('DCBatteryPower'),
            variable.create('Shunt1Name'),
            variable.create('Shunt1Power'),
            variable.create('Shunt2Name'),
            variable.create('Shunt2Power'),
            variable.create('Heatsink1Temp'),
            variable.create('Heatsink2Temp'),
            variable.create('ControlBoardTemp'),
            variable.create('BatteryTemperature'),
            variable.create('TransformerTemp'),
            variable.create('InletTemp'),
            variable.create('FanSpeed'),
            variable.create('BattOutToday'),
            variable.create('BattInToday'),
            variable.create('BattNetToday'),
            variable.create('BattInYesterday'),
            variable.create('BattOutYesterday'),
            variable.create('absorb'),
            variable.create('bulk'),
            variable.create('float'),
            variable.create('BattSocPercent'),
            variable.create('LoadAccumulatedToday'),
            variable.create('PercentageSolarOutput'),
            variable.create("GeneratorStartReason"),
            variable.create("GeneratorRunningReason"),
            variable.create("GeneratorStatus"),

        ]
        self.__scales = None
        self.__duskTodayAC = -1
        self.__duskYesterdayAC = -1
        self.__duskDaysToRecharge = -1

    def __update(self, variables):
        # opportunistically request scales if they're missing during another
        # request
        if not self.__scales:
            variables = variables + self.__scale_variables

        self.__muster.update(variables)

    def get(self):
        self.__update(self.__variables)
        stats = []
        for var in self.__variables:
            stats.append({
                "description": variable.MAP[var.get_name()][variable.DESCRIPTION],
                "name": var.get_name(),
                "value": var.get_value(self.scales),
                "units": variable.MAP[var.get_name()][variable.UNITS],
            })
            if (datetime.now().hour == 16 and datetime.now().minute in [0, 1, 2]) or (datetime.now().hour > 16 and self.__duskTodayAC == -1):
                if self.__duskTodayAC != -1:
                    self.__duskYesterdayAC = self.__duskTodayAC
                self.__duskTodayAC = self.__variables[27].get_value(self.scales)
                self.__duskDaysToRecharge = self.__variables[29].get_value(self.scales)

        stats.append({
                "description": "AC Input Dusk Today",
                "name": "ACInputDuskToday",
                "value": self.__duskTodayAC,
                "units": "Wh",
        })

        stats.append({
            "description": "AC Input Dusk Yesterday",
            "name": "ACInputDuskYesterday",
            "value": self.__duskYesterdayAC,
            "units": "Wh",
        })

        stats.append({
            "description": "Dusk Days to Recharge",
            "name": "DuskDaysToRecharge",
            "value": self.__duskDaysToRecharge,
            "units": "Days",
        })

        return stats

    @property
    def scales(self):
        if not self.__scales:
            self.__scales = {}
            for variable in self.__scale_variables:
                self.__scales[variable.get_name()] = variable.get_value([])
        return self.__scales


