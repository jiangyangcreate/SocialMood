<template>
  <div class="chart-container">
    <div ref="barChart" class="chart"></div>
    <div ref="pieChart" class="chart"></div>
    <div ref="lineChart" class="chart"></div>
    <div ref="wordCloudChart" class="chart"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import 'echarts-wordcloud';

export default {
  name: 'ECharts',
  mounted() {
    this.initBarChart();
    this.initPieChart();
    this.initLineChart();
    this.initWordCloudChart();
  },
  methods: {
    initBarChart() {
      const chart = echarts.init(this.$refs.barChart);
      const option = {
        title: { text: 'Sales Data', left: 'center' },
        tooltip: { trigger: 'axis' },
        legend: { data: ['Sales'], top: 'bottom' },
        xAxis: { type: 'category', data: ['A', 'B', 'C', 'D', 'E'] },
        yAxis: { type: 'value' },
        series: [{ name: 'Sales', type: 'bar', data: [5, 20, 36, 10, 10] }]
      };
      chart.setOption(option);
    },
    initPieChart() {
      const chart = echarts.init(this.$refs.pieChart);
      const option = {
        title: { text: 'Market Share', left: 'center' },
        tooltip: { trigger: 'item' },
        legend: { orient: 'vertical', left: 'left' },
        series: [
          {
            name: 'Share',
            type: 'pie',
            radius: '50%',
            data: [
              { value: 40, name: 'A' },
              { value: 20, name: 'B' },
              { value: 30, name: 'C' },
              { value: 10, name: 'D' }
            ],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      };
      chart.setOption(option);
    },
    initLineChart() {
      const chart = echarts.init(this.$refs.lineChart);
      const option = {
        title: { text: 'Weekly Sales', left: 'center' },
        tooltip: { trigger: 'axis' },
        legend: { data: ['Sales'], top: 'bottom' },
        xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
        yAxis: { type: 'value' },
        series: [{ name: 'Sales', type: 'line', data: [150, 230, 224, 218, 135, 147, 260] }]
      };
      chart.setOption(option);
    },
    initWordCloudChart() {
      const chart = echarts.init(this.$refs.wordCloudChart);
      const option = {
        title: { text: 'Technology Popularity', left: 'center' },
        series: [
          {
            type: 'wordCloud',
            shape: 'circle',
            sizeRange: [12, 50],
            rotationRange: [-90, 90],
            textStyle: {
              normal: {
                color: function () {
                  return 'rgb(' + [
                    Math.round(Math.random() * 160),
                    Math.round(Math.random() * 160),
                    Math.round(Math.random() * 160)
                  ].join(',') + ')';
                }
              }
            },
            data: [
              { name: 'Vue', value: 10000 },
              { name: 'ECharts', value: 6181 },
              { name: 'JavaScript', value: 4386 },
              { name: 'HTML', value: 4055 },
              { name: 'CSS', value: 2467 }
            ]
          }
        ]
      };
      chart.setOption(option);
    }
  }
};
</script>

<style scoped>
.chart-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.chart {
  width: 600px;
  height: 400px;
  margin-bottom: 20px;
}
</style>
