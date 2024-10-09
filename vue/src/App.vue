<template>
  <div id="app">
    <ECharts />
  </div>
</template>

<script>
import ECharts from './components/ShowECharts.vue';

export default {
  name: 'App',
  components: {
    ECharts
  }
};
</script>

<style>
#app {
  text-align: center;
}
</style>
