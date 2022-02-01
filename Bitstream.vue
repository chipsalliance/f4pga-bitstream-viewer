<!--
 Copyright 2017-2022 F4PGA Authors

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.

 SPDX-License-Identifier: Apache-2.0
-->
<template>
  <div class="example">
    <h3>Bitstream map:</h3>
    <apexcharts width="2400" height="3200" type="heatmap" :options="chartOptions" :series="series" v-on:dataPointSelection="dataPointSelected"></apexcharts>
    <modal v-if="showModal" v-on:close="showModal = false" v-bind:frameAddr="frameAddr" v-bind:gridx="gridx" v-bind:gridy="gridy"></modal>
  </div>
</template>
<script>
  import VueApexCharts from 'vue-apexcharts'
  import modal from './Popup.vue'
  export default {
    name: 'Chart',
    components: {
      apexcharts: VueApexCharts,
      modal,
    },
    methods: {
      dataPointSelected: function(e, chart, opts) {
        this.frameAddr = opts.w.config.series[opts.seriesIndex].data[opts.dataPointIndex].address;
        this.gridx = opts.w.config.series[opts.seriesIndex].data[opts.dataPointIndex].x
        this.gridy = opts.w.config.series[opts.seriesIndex].name
        this.showModal = true;
      }
    },
    data: function() {
      return {
        showModal: false,
        frameAddr: '',
        gridx: -1,
        gridy: -1,
        chartOptions: {
          chart: {
            type: 'heatmap',
            id: 'heatmap',
            animations: { enabled: false },
          },
          plotOptions: { heatmap: { colorScale: { ranges: [ {from: -1, to: -1, name: 'Unknown', color: '#ff0000'},{from: 0, to: 0, name: 'Empty', color: '#f2f2f2'},{from: 1, to: 1, name: 'Used', color: '#128FD9'} ] } } },
          colors: ["#008FFB"],
          dataLabels: {
            enabled: false,
          },
          grid: { position: 'front', xaxis: { lines: { show: false } }, yaxis: { lines: { show: false } } },
          xaxis: { tickAmount: 'dataPoints', tickPlacement: 'on' },
          tooltip: {
            enabled: true,
            y: {
              formatter: function(value, { seriesIndex, dataPointIndex, w }) {
                let point = w.config.series[seriesIndex].data[dataPointIndex]
                return (
                  'Grid: ' + point.x + ' @ ' + w.config.series[seriesIndex].name
                );
              },
              title: { formatter: () => '' },
            }
          }
        },
        series: [
          { name: 0, data: [{ x: 0, y: 0, address: '0x00000000' }]},
        ],
      }
    },
    mounted: function() {
      const body = () => import('./bitstreamData.json')
      body().then(data => this.$children[0].updateSeries(data.data, false))
    },
  }
</script>
