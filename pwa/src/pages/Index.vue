<template>
  <q-page class="container">
    <div class="row" v-if="loaded">
      <div class="col-md-4 col-sm-6 col-xs-12">
        <q-knob
          disable
          v-model="soc"
          show-value
          :thickness="0.22"
          size="20rem"
          :color="socColor"
          track-color="grey-3"
          class="q-ma-md"
        >
          <q-icon name="battery_full" />{{ Math.round(soc) }}%
        </q-knob>
      </div>
      <div class="col-md-4 col-sm-6 col-xs-12">
        <q-knob
          disable
          v-model="hoursRemainingPercentage"
          show-value
          :thickness="0.22"
          size="20rem"
          :color="hoursRemainingColor"
          track-color="grey-3"
          class="q-ma-md"
        >
          <q-icon name="timer" />{{ Math.round(hoursRemaining) }} h
        </q-knob>
      </div>
      <div class="col-md-4 col-sm-6 col-xs-12">
        <q-knob
          disable
          v-model="solarOutputPercentage"
          show-value
          :thickness="0.22"
          size="20rem"
          font-size="3rem"
          color="yellow"
          track-color="grey-3"
          class="q-ma-md"
        >
          <q-icon name="wb_sunny" />{{ Math.round(solarOutputWatts) }} W
        </q-knob>
      </div>
    </div>
    <div class="row" v-if="loaded">
      <div class="col-lg-2 col-md-3 col-sm-4 col-xs-6">
        <q-chip size="xl" icon="power">
        {{ load }} W
        </q-chip>
      </div>
      <div class="col-lg-2 col-md-3 col-sm-4 col-xs-6">
        <q-chip size="xl" :icon="batteryPower > 0 ? 'battery_alert' : 'battery_charging_full'">
        {{ batteryPower }} W
        </q-chip>
      </div>
      <div class="col-lg-2 col-md-3 col-sm-4 col-xs-6">
        <q-chip size="xl" icon="electrical_services" >
        {{ batteryState }}
        </q-chip>
      </div>
      <div class="col-lg-2 col-md-3 col-sm-4 col-xs-6">
        <q-chip size="xl" icon="thermostat" >
        Batt {{ batteryTemp }} °C
        </q-chip>
      </div>
      <div class="col-lg-2 col-md-3 col-sm-4 col-xs-6">
        <q-chip size="xl" icon="thermostat" >
        Inlet {{ inletTemp }} °C
        </q-chip>
      </div>
      <div class="col-lg-2 col-md-3 col-sm-4 col-xs-6">
        <q-chip size="xl" icon="thermostat" >
        Board {{ boardTemp }} °C
        </q-chip>
      </div>

      <div class="col-lg-2 col-md-3 col-sm-4 col-xs-6">
        <q-chip size="xl" icon="today" >
        {{ todaysUsage }} kWh
        </q-chip>
      </div>
      <div class="col-lg-2 col-md-3 col-sm-4 col-xs-6">
        <q-chip size="xl" icon="outlet" >
        Gen {{ acInputToday }} kWh
        </q-chip>
      </div>
      <div v-if="generatorStartedBy !== 'Not Running'" class="col-lg-2 col-md-3 col-sm-4 col-xs-6">
        <q-chip size="xl" icon="outlet" >
        {{ generatorStartedBy }}
        </q-chip>
      </div>
      <div v-if="generatorRunningReason !== 'Not Running'" class="col-lg-2 col-md-3 col-sm-4 col-xs-6">
        <q-chip size="xl" icon="outlet" >
        {{ generatorRunningReason }}
        </q-chip>
      </div>
      <div v-if="generatorCurrentStatus !== 'Not Running'" class="col-lg-2 col-md-3 col-sm-4 col-xs-6">
        <q-chip size="xl" icon="outlet" >
        {{ generatorCurrentStatus }}
        </q-chip>
      </div>
      <div class="col-lg-2 col-md-3 col-sm-4 col-xs-6">
        <q-chip size="xl" icon="outlet" >
        Gen Y {{ acInputYesterday }} kWh
        </q-chip>
      </div>
      <div class="col-lg-2 col-md-3 col-sm-4 col-xs-6">
        <q-chip size="xl" icon="battery_full" >
        Float {{ floatHours }} M
        </q-chip>
      </div>
      <div class="col-lg-2 col-md-3 col-sm-4 col-xs-6">
        <q-chip size="xl" icon="battery_unknown" >
        {{ primaryBatteryVolts }} V
        </q-chip>
      </div>


      <div class="col-lg-2 col-md-3 col-sm-4 col-xs-6">
        <q-chip size="xl" icon="update" >
          {{ lastUpdatedHuman }}
        </q-chip>
      </div>
    </div>
    <!-- <span v-for="stat in stats" v-bind:key="stat.name">
      {{ stat.name }} [{{ stat.description }}] : {{ Math.round(stat.value) }} {{ stat.units
      }}<br />
    </span>  -->
  </q-page>
</template>

<script>
import human from 'human-time'
import { date } from 'quasar'

function round(value, precision) {
    var multiplier = Math.pow(10, precision || 0);
    return Math.round(value * multiplier) / multiplier;
}


export default {
  name: "PageIndex",
  data() {
    return {
      stats: [],
      loaded: false,
      batterySize: 17000,
      shutdownPercentage: 10,
      lastUpdate: Date.now(),
      lastUpdatedHuman: '',
    };
  },
  computed: {
    boardTemp() {
      return this.stat("ControlBoardTemp")
    },
    inletTemp() {
      return this.stat("InletTemp")
    },
    todaysUsage() {
      return Math.round(this.stat("LoadAccumulatedToday") / 1000)
    },

    batteryTemp() {
      return this.stat("BatteryTemperature")
    },
    batteryState() {
      let result = ""
      if (this.stat("bulk") > 0) {
        result = "Bulk"
      } else {
        if (this.stat("absorb") > 0) {
          result = "Absorb"
        } else {
          if (this.stat("float") > 0) {
            result = "Float"
          }
        }
      }
      return result
    },

    primaryBatterySOC() {
      return this.stat("BattSocPercent")
    },
    primaryBatteryVolts() {
      return this.statfloat("BatteryVolts")
    },
    load() {
      return this.stat("LoadAcPower")
    },
    batteryPower() {
      return this.stat("DCBatteryPower")
    },
    solarOutputPercentage() {
      return this.stat("PercentageSolarOutput")
    },
    acInputToday() {
      return Math.round( this.stat("ACInputToday") / 1000)
    },
    acInputYesterday() {
      return Math.round(this.stat("ACInputYesterday") / 1000)
    },
    batteryVolts() {
      return this.statfloat("BatteryVolts")
    },
    daysToRecharge() {
      return this.stat("DaysToRecharge")
    },
    floatHours() {
      return this.stat("FloatHours")
    },
    acInputDuskToday() {
      return this.stat("ACInputDuskToday")
    },
    acInputDuskYesterday() {
      return this.stat("ACInputDuskYesterday")
    },
    duskDaysToRecharge() {
      return this.stat("DuskDaysToRecharge")
    },
    solarOutputWatts() {
      return this.stat("CombinedKacoAcPowerHiRes")
    },
    totalPrimaryKwhAvail() {
      return this.batterySize * ((100 - this.shutdownPercentage) / 100)
    },
    generatorStartedBy() {
      return this.generatorReason(this.stat("GeneratorStartReason"))
    },
    generatorRunningReason() {
      return this.generatorReason(this.stat("GeneratorRunningReason"))
    },
    generatorCurrentStatus() {
      return this.generatorStatus(this.stat("GeneratorStatus"))
    },
    soc() {
      const totalKwhAvail = this.totalPrimaryKwhAvail
      const primaryKwhAvail  = this.totalPrimaryKwhAvail * this.stat("BattSocPercent") / 100

      const actualKWHAvail = primaryKwhAvail
      return actualKWHAvail / totalKwhAvail * 100
    },
    socColor() {
      let result = "primary";
      if (this.loaded) {
        let soc = this.soc;
        if (soc < 50) {
          result = "orange";
        }
        if (soc < 30) {
          result = "red";
        }
        if (soc > 50) {
          result = "green";
        }
      }
      return result;
    },
    hoursRemainingColor() {
      let result = "primary";
      if (this.loaded) {
        if (this.hoursRemaining < 8) {
          result = "red";
        }
        if (this.hoursRemaining < 12) {
          result = "orange";
        }
        if (this.hoursRemaining > 12) {
          result = "green";
        }
      }
      return result;
    },
    hoursRemaining() {

      let wattsLeft = (this.totalPrimaryKwhAvail) * this.soc / 100
      let hoursRemaining = wattsLeft / (this.batteryPower > 0 ? this.batteryPower : 100)
      if (hoursRemaining > 24)  {
        hoursRemaining = 24
      }
      return hoursRemaining
    },
    hoursRemainingPercentage() {
      return Math.round(this.hoursRemaining / 24 * 100)
    }
  },
  mounted() {
    this.getData()
  },
  created() {
    this.interval = setInterval(() => this.getData(), 1000*30)
  },
  beforeDestroy() {
    clearInterval(this.interval)
  },

  methods: {
    async getData() {
      this.lastUpdatedHuman = human((Date.now() - this.lastUpdate) / 1000)
      try {
        const result = await this.$axios.get("/api/", {});
        this.stats = result.data;
        this.loaded = true;
        this.lastUpdate = Date.now()
      } finally {
      }
    },
    generatorStatus(code) {
      switch (code)
      {
        case 0:
          return "Not Running";
        case 1:
          return "Running";
        case 2:
          return "Low Fuel";
        case 3:
          return "No Fuel";
        case 4:
          return "Fault";
        case 5:
          return "Not Available";
        case 6:
          return "Starting";
        case 7:
          return "Retry Pause";
        case 8:
          return "Stopping";
        case 9:
          return "Disabled";
        case 10:
          return "AC Source Present";
        default:
          return "Unknown"
      }
    },
    generatorReason(code) {
      switch (code)
      {
        case 0:
          return "Not Running";
        case 1:
          return "Front Panel";
        case 2:
          return "Remote Run Request";
        case 3:
          return "Run Schedule";
        case 4:
          return "Hi Inverter Temp.";
        case 5:
          return "Impending Inverter Shutdown";
        case 6:
          return "Synchronisation Fault";
        case 7:
          return "State of Charge";
        case 8:
          return "Low Battery Volts";
        case 9:
          return "Battery Mid Point Voltage Error";
        case 10:
          return "Equalising Battery";
        case 11:
          return "Hi AC Load";
        case 12:
          return "Generator Exercise";
        case 13:
          return "Generator Available";
        case 14:
          return "Generator Fault";
        case 15:
          return "Minimum Runtime";
        case 16:
          return "Generator Lock Out Active";
        case 17:
          return "Battery Float";
        case 18:
          return "Cooling Down";
        case 19:
          return "Confirmed Start";
        case 20:
          return "Manual";
        case 21:
          return "AC Source Present";
        case 22:
          return "Disabled";
        case 23:
          return "Support Mode";
        case 24:
          return "Equalise";
        case 25:
          return "Battery Load";
        case 29:
          return "Warming Up";
        default:
          return ""
      }
    },
    stat(name) {
      let result = this.stats.filter(function (item) {
        return item.name === name
      })
      if (result && result.length > 0) {
        return Math.round(result[0].value);
      } else {
        return 0
      }
    },
    statfloat(name) {
      let result = this.stats.filter(function (item) {
        return item.name === name
      })
      if (result && result.length > 0) {
        return round(result[0].value,2);
      } else {
        return 0
      }
    },
  },
};
</script>
