<script setup lang="ts">
import { PlusIcon, MinusIcon } from '@heroicons/vue/20/solid'
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { fetchCapm, fetchBaseFcf, fetchWacc, fetchDcf, fetchPastFcf, calcCagr } from './stocks'

const ticker = ref('msft')
const input = ref('')
const price = ref(0)
const growthRate = ref(0.15)
const years = ref(7)
const perpetualGrowthRate = ref(0.025)
const discountRate = ref(0)
const marginOfSafety = ref(0.3)

const result = ref<any>(null)
const error = ref('')

const saveInput = () => {
  ticker.value = input.value
  input.value = ''
}

const fetchPrice = async () => {
  const currentPrice = await axios.get(`http://127.0.0.1:8000/price/${ticker.value}`)
  price.value = currentPrice.data.currentprice
}

const fetchDiscountRate = async () => {
  const capm = await fetchCapm(ticker.value)
  const wacc = await fetchWacc(ticker.value, capm)
  discountRate.value = wacc
}

const fetchData = async () => {
  try {
    const basefcf = await fetchBaseFcf(ticker.value)
    const data = await fetchDcf(ticker.value, {
      base_fcf: basefcf,
      growth_rate: growthRate.value,
      perpetual_growth_rate: perpetualGrowthRate.value,
      discount_rate: discountRate.value,
      years: years.value,
    })
    result.value = data.base_case
  } catch (err: any) {
    error.value = err.message ?? 'Something went wrong'
  }
}

const handleConfirm = async () => {
  saveInput()
  await fetchPrice()
  await fetchDiscountRate()
  await fetchData()

  const fcfs = await fetchPastFcf(ticker.value)
  const cagr1y = calcCagr(fcfs, 1)
  const cagr5y = calcCagr(fcfs, 5)
  const cagr10y = calcCagr(fcfs, 10)
  console.log({ cagr1y, cagr5y, cagr10y })
}
</script>

<template>
  <div class="min-h-screen text-white">
    <div class="flex flex-col items-center space-y-4">
      <h1 class="text-3xl font-bold">DCF Calculator</h1>
      <div class="flex justify-center space-x-4">
        <p class="text-lg">{{ ticker }}</p>
        <input type="text" placeholder="Search Ticker" v-model="input" class="border" />
        <button class="rounded bg-gray-400 px-3 py-1" @click="handleConfirm">Search</button>
      </div>

      <div class="flex justify-center space-x-4">
        <p class="text-lg">Stock Price</p>
        <p class="text-lg">${{ price }}</p>
      </div>

      <div class="flex justify-center space-x-4">
        <p class="text-lg">Discount Rate</p>
        <p class="text-lg">{{ discountRate }}%</p>
      </div>

      <div class="grid grid-cols-3 gap-4 mt-4">
        <div class="flex flex-col space-y-2 rounded-lg border p-4">
          <p class="text-lg text-center font-bold">Growth Stage</p>
          <div class="flex justify-center space-x-4">
            <p class="text-lg">Years</p>
            <div class="flex justify-center">
              <button class="px-2 py-0.5 bg-gray-400 rounded">
                <minus-icon class="size-3 text-black"></minus-icon>
              </button>
              <span class="text-lg">{{ years }}</span>
              <button class="px-2 py-0.5 bg-gray-400 rounded text-black">
                <plus-icon class="size-3"></plus-icon>
              </button>
            </div>
          </div>

          <div class="flex justify-center space-x-4">
            <p class="text-lg">Growth Rate</p>
            <div class="flex justify-center">
              <button class="px-2 py-0.5 bg-gray-400 rounded">
                <minus-icon class="size-3 text-black"></minus-icon>
              </button>
              <span class="text-lg">{{ growthRate }}%</span>
              <button class="px-2 py-0.5 bg-gray-400 rounded text-black">
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
              <button class="px-2 py-0.5 bg-gray-400 rounded">
                <minus-icon class="size-3 text-black"></minus-icon>
              </button>
              <span class="text-lg">{{ perpetualGrowthRate }}%</span>
              <button class="px-2 py-0.5 bg-gray-400 rounded text-black">
                <plus-icon class="size-3"></plus-icon>
              </button>
            </div>
          </div>
        </div>

        <div class="flex flex-col space-y-2 ml-8 rounded-lg border p-4">
          <p class="text-lg font-bold">Past FCF Growth Rate</p>
          <div class="space-y-2">
            <p class="flex justify-between text-lg">
              <span>10y</span>
              <span>0%</span>
            </p>
            <p class="flex justify-between text-lg">
              <span>5y</span>
              <span>0%</span>
            </p>
            <p class="flex justify-between text-lg">
              <span>YTD</span>
              <span>0%</span>
            </p>
          </div>
        </div>
      </div>

      <div class="border rounded-lg p-10 divide-y divide-white space-y-6 mt-4">
        <div class="flex justify-center space-x-4">
          <p class="text-lg">Stock Price</p>
          <p class="text-lg">${{ price }}</p>
        </div>
        <div class="flex justify-center space-x-4">
          <p class="text-lg">Fair Value</p>
          <p class="text-lg">${{ result }}</p>
        </div>
        <div class="flex justify-center space-x-4">
          <p class="text-lg">Margin of Safety</p>
          <p class="text-lg">{{ marginOfSafety }}%</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
