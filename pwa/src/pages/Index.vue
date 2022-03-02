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
          <q-icon name="battery_full" />{{ soc }}%
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
        {{ todaysUsage }} Wh
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


export default {
  name: "PageIndex",
  data() {
    return {
      stats: [],
      loaded: false,
      batterySize: 15000,
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
      return this.stat("LoadAccumulatedToday")
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
    load() {
      return this.stat("LoadAcPower")
    },
    batteryPower() {
      return this.stat("DCBatteryPower")
    },
    solarOutputPercentage() {
      return this.stat("PercentageSolarOutput")
    },
    solarOutputWatts() {
      return this.stat("CombinedKacoAcPowerHiRes")
    },
    soc() {
      return this.stat("BattSocPercent")
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
      let percentageLeft = this.stat("BattSocPercent") - this.shutdownPercentage
      let wattsLeft = this.batterySize * percentageLeft / 100
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
  },
};
</script>
