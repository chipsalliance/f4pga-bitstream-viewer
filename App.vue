<!--
 Copyright (C) 2017-2021  The SymbiFlow Authors.

 Use of this source code is governed by a ISC-style
 license that can be found in the LICENSE file or at
 https://opensource.org/licenses/ISC

 SPDX-License-Identifier: ISC
-->
<template>
  <div id="app">
    <Chart />
  </div>
</template>

<script>
import Chart from './Bitstream.vue'

export default {
  name: 'app',
  components: {
    Chart
  },
}
</script>
