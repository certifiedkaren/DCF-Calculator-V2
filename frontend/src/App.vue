<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

// don't hardcode later
const ticker = 'msft'
const growthRate = 0.15
const years = 7
const perpetual_growth_rate = 0.025

const fetchData = async () => {
  try {
    const capmRes = await axios.get(`http://127.0.0.1:8000/capm/${ticker}`)
    const capm = capmRes.data.capm

    const waccRes = await axios.get(`http://127.0.0.1:8000/wacc/${ticker}/${capm}`)
    const wacc = waccRes.data.wacc

    const basefcfRes = await axios.get(`http://127.0.0.1:8000/basefcf/${ticker}`)
    const basefcf = basefcfRes.data.basefcf

    const dcfRes = await axios.post(`http://127.0.0.1:8000/dcf/${ticker}`, {
      ticker: ticker,
      base_fcf: basefcf,
      growth_rate: growthRate,
      perpetual_growth_rate: perpetual_growth_rate,
      discount_rate: wacc,
      years: years,
    })

    console.log('DCF result:', dcfRes.data)
  } catch (err) {
    console.error('Error fetching data:', err)
  }
}
</script>

<template>
  <div class="min-h-screen text-white">
    <div class="flex justify-center">
      <h1 class="text-3xl">DCF Calculator</h1>
    </div>
    <button class="px-4 py-2 bg-blue-400 rounded hover:bg-blue-500" @click="fetchData()">
      get data
    </button>
  </div>
</template>

<style scoped></style>
