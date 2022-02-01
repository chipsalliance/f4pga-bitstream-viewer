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
    <vue-good-table :columns="columns" :rows="rows" max-height="1100px" />
  </div>
</template>

<script>
import 'vue-good-table/dist/vue-good-table.css'
  import { VueGoodTable } from 'vue-good-table';
  export default {
    name: 'gridinfo',
    components: {
      VueGoodTable
    },
    props: [ 'frameAddr', 'gridx', 'gridy' ],
    data: function() {
      return {
      columns: [
        {
          label: 'Bit',
          field: 'bitname',
        },
        {
          label: 'Feature',
          field: 'feature',
        },
      ],
      rows: [],

      }
    },
    mounted: function() {
      const body = () => import('./grid/grid_' + this.gridx + '_' + this.gridy + '.json')
      var rowsdata = []
      body().then(data =>
        {
          for (var key in data) {
            var bitname = data[key].bitname
            var feature = data[key].feature
            if (bitname && feature) {
              rowsdata.push({bitname: bitname, feature: feature})
            }
          }
        }
      )
      this.rows = rowsdata
    },
  }
</script>
