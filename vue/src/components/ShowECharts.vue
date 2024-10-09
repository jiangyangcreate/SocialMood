<template>
  <div class="chart-container">
    <div class="chart-row">
      <div ref="barChart" class="chart"></div>
      <div ref="pieChart" class="chart"></div>
    </div>
    <div class="chart-row">
      <div ref="lineChart" class="chart"></div>
      <div ref="wordCloudChart" class="chart"></div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import 'echarts-wordcloud';
import { barChartData } from '../data/barChartData';
import { pieChartData } from '../data/pieChartData';
import { lineChartData } from '../data/lineChartData';
import { wordCloudData } from '../data/wordCloudData';

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
        title: { text: '舆情情感分析', left: 'center' },
        tooltip: { trigger: 'axis' },
        legend: { data: ['正面', '负面'], top: 'bottom' },
        xAxis: { 
          type: 'category', 
          data: barChartData.map(item => item.category) 
        },
        yAxis: { type: 'value' },
        series: [
          {
            name: '正面',
            type: 'bar',
            data: barChartData.map(item => item.positive),
            itemStyle: { color: '#91cc75' }
          },
          {
            name: '负面',
            type: 'bar',
            data: barChartData.map(item => item.negative),
            itemStyle: { color: '#ee6666' }
          }
        ]
      };
      chart.setOption(option);
    },
    initPieChart() {
      const chart = echarts.init(this.$refs.pieChart);
      const option = {
        title: { text: '舆情影响占比', left: 'center' },
        tooltip: { trigger: 'item' },
        legend: {
          orient: 'horizontal',
          bottom: 'bottom',
          left: 'center'
        },
        series: [
          {
            name: 'Share',
            type: 'pie',
            radius: '50%',
            data: pieChartData,
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
        title: { text: '舆情变化图', left: 'center' },
        tooltip: { trigger: 'axis' },
        legend: { data: ['舆情指数'], top: 'bottom' },
        xAxis: { 
          type: 'category', 
          data: lineChartData.map(item => item.date)
        },
        yAxis: { type: 'value' },
        series: [{ 
          name: '舆情指数', 
          type: 'line', 
          data: lineChartData.map(item => item.value)
        }]
      };
      chart.setOption(option);
    },
    initWordCloudChart() {
      const chart = echarts.init(this.$refs.wordCloudChart);
      const option = {
        title: { text: '舆情词云图', left: 'center' },
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
            data: wordCloudData
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
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.chart-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  width: 100%;
}

.chart {
  width: 100%;
  height: 400px;
  margin-bottom: 20px;
}

@media (min-width: 768px) {
  .chart {
    width: calc(50% - 10px);
    margin-right: 20px;
  }

  .chart:nth-child(2n) {
    margin-right: 0;
  }
}
</style>
