<template>
  <q-page class="flex flex-center">
    <img
      alt="Quasar logo"
      src="~assets/quasar-logo-full.svg"
    >
  </q-page>
</template>

<script>
export default {
  name: 'PageIndex',
  data () {
    return {
      stats: []
    }

  },
  mounted () {
    this.getData()
  },
  methods: {
    async getData() {
      try {
        const result = await this.$axios.get({}, '/api', {
          auth: {
            username: 'selpi',
            password: 'selpi'
          }
        })
        this.stats = result.data
      }
      finally {
      }
    },
  }
}
</script>
