<template>
  <q-layout view="hHh lpR fFf">

    <q-page-container>
      <router-view />
      v {{ version }}
    </q-page-container>
  </q-layout>
</template>

<script>
import { version } from '../../package.json'



export default {
  name: 'MainLayout',
  data () {
    return {
      version: version
    }
  }
}
</script>
