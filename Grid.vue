<!--
 Copyright (C) 2017-2021  The SymbiFlow Authors.

 Use of this source code is governed by a ISC-style
 license that can be found in the LICENSE file or at
 https://opensource.org/licenses/ISC

 SPDX-License-Identifier: ISC
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
