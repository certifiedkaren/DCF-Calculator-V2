<script setup lang="ts">
import { PlusIcon, MinusIcon } from '@heroicons/vue/20/solid'
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
    <div class="flex flex-col items-center space-y-4">
      <h1 class="text-3xl font-bold">DCF Calculator</h1>
      <div class="flex justify-center space-x-4">
        <p class="text-lg">MSFT</p>
        <input type="text" placeholder="Search Ticker" class="border" />
      </div>

      <div class="flex justify-center space-x-4">
        <p class="text-lg">Stock Price</p>
        <p class="text-lg">$300.00</p>
      </div>

      <div class="flex justify-center space-x-4">
        <p class="text-lg">Discount Rate</p>
        <p class="text-lg">10%</p>
      </div>

      <div class="grid grid-cols-2 gap-4 mt-4">
        <div class="flex flex-col space-y-2 rounded-lg border p-4">
          <p class="text-lg text-center font-bold">Growth Stage</p>
          <div class="flex justify-center space-x-4">
            <p class="text-lg">Years</p>
            <div class="flex justify-center">
              <button class="px-2 py-0.5 bg-purple-300 rounded">
                <minus-icon class="size-3 text-black"></minus-icon>
              </button>
              <span class="text-lg">10</span>
              <button class="px-2 py-0.5 bg-purple-300 rounded text-black">
                <plus-icon class="size-3"></plus-icon>
              </button>
            </div>
          </div>

          <div class="flex justify-center space-x-4">
            <p class="text-lg">Growth Rate</p>
            <div class="flex justify-center">
              <button class="px-2 py-0.5 bg-purple-300 rounded">
                <minus-icon class="size-3 text-black"></minus-icon>
              </button>
              <span class="text-lg">15%</span>
              <button class="px-2 py-0.5 bg-purple-300 rounded text-black">
                <plus-icon class="size-3"></plus-icon>
              </button>
            </div>
          </div>
        </div>

        <div class="flex flex-col space-y-2 ml-8 rounded-lg border p-4">
          <p class="text-lg text-center font-bold">Terminal Stage</p>
          <div class="flex justify-center space-x-4">
            <p class="text-lg">Growth Rate</p>
            <div class="flex justify-center">
              <button class="px-2 py-0.5 bg-purple-300 rounded">
                <minus-icon class="size-3 text-black"></minus-icon>
              </button>
              <span class="text-lg">15%</span>
              <button class="px-2 py-0.5 bg-purple-300 rounded text-black">
                <plus-icon class="size-3"></plus-icon>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="border rounded-lg p-10 divide-y divide-white space-y-6 mt-4">
        <div class="flex justify-center space-x-4">
          <p class="text-lg">Stock Price</p>
          <p class="text-lg">$300.00</p>
        </div>
        <div class="flex justify-center space-x-4">
          <p class="text-lg">Fair Value</p>
          <p class="text-lg">$200.00</p>
        </div>
        <div class="flex justify-center space-x-4">
          <p class="text-lg">Margin of Safety</p>
          <p class="text-lg">30%</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
