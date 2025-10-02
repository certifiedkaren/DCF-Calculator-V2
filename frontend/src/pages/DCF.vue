<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import axios from 'axios'
import { fetchCapm, fetchBaseFcf, fetchWacc, fetchDcf, fetchPastFcf, calcCagr } from '../stocks'

const ticker = ref('')
const input = ref('')
const price = ref(0)
const growthRate = ref(0.15)
const years = ref(7)
const perpetualGrowthRate = ref(0.025)
const discountRate = ref(0)
const marginOfSafety = ref(0.3)

const cagr1y = ref(0)
const cagr5y = ref(0)
const cagr10y = ref(0)

const loading = ref(false)

const growthRatePercent = computed({
  get: () => +(growthRate.value * 100).toFixed(2),
  set: (val: number) => {
    const v = isFinite(val) ? val : 0
    growthRate.value = v / 100
  },
})

const perpetualGrowthRatePercent = computed({
  get: () => +(perpetualGrowthRate.value * 100).toFixed(2),
  set: (val: number) => {
    const v = isFinite(val) ? val : 0
    perpetualGrowthRate.value = v / 100
  },
})

const discountRatePercent = computed({
  get: () => +(discountRate.value * 100).toFixed(2),
  set: (val: number) => {
    const v = isFinite(val) ? val : 0
    discountRate.value = v / 100
  },
})

const result = ref<any>(null)
const error = ref('')

const saveInput = () => {
  if (input.value) {
    ticker.value = input.value
    input.value = ''
  }
}

const calculateDcf = async () => {
  if (!ticker.value) return
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
    result.value = null
  }
}

watch([growthRate, years, perpetualGrowthRate, discountRate], () => {
  if (result.value !== null) {
    calculateDcf()
  }
})

const handleConfirm = async () => {
  saveInput()
  if (!ticker.value) return

  loading.value = true
  error.value = ''

  try {
    const [priceData, capm, pastFcf] = await Promise.all([
      axios.get(`http://127.0.0.1:8000/price/${ticker.value}`),
      fetchCapm(ticker.value),
      fetchPastFcf(ticker.value),
    ])

    const wacc = await fetchWacc(ticker.value, capm)
    price.value = priceData.data.currentprice
    discountRate.value = wacc

    try {
      cagr1y.value = calcCagr(pastFcf, 1)
    } catch {
      cagr1y.value = 0
    }
    try {
      cagr5y.value = calcCagr(pastFcf, 5)
    } catch {
      cagr5y.value = 0
    }
    try {
      cagr10y.value = calcCagr(pastFcf, 10)
    } catch {
      cagr10y.value = 0
    }

    await calculateDcf()
  } catch (err: any) {
    error.value = 'Failed to fetch data. Please check the ticker and try again.'
    price.value = 0
    discountRate.value = 0
    result.value = null
    cagr1y.value = 0
    cagr5y.value = 0
    cagr10y.value = 0
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen text-white">
    <div class="flex flex-col items-center space-y-4">
      <h1 class="text-3xl font-bold">DCF Calculator</h1>
      <div class="flex justify-center space-x-4">
        <!-- <p class="text-lg">{{ ticker }}</p> -->
        <input
          type="text"
          placeholder="Search Ticker"
          v-model="input"
          @keyup.enter="handleConfirm"
          class="w-48 rounded-md border border-zinc-600 bg-zinc-800 px-3 py-2 text-white placeholder-zinc-400 focus:border-blue-500 focus:ring-blue-500"
        />
        <button
          class="rounded-md bg-blue-600 px-5 py-2 font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-offset-2 focus-visible:outline-blue-600"
          @click="handleConfirm"
        >
          Search
        </button>
      </div>

      <div v-if="loading" class="text-lg">Loading...</div>
      <div v-if="error" class="text-lg text-red-500">{{ error }}</div>
      <div v-if="result && !loading && !error" class="text-xl">{{ ticker }}</div>
      <template v-if="!loading && result">
        <div class="flex justify-center space-x-4">
          <p class="text-lg">Stock Price</p>
          <p class="text-lg">${{ price }}</p>
        </div>

        <div class="flex justify-center space-x-4">
          <p class="text-lg">Discount Rate</p>
          <div class="flex justify-center">
            <input
              type="number"
              v-model.number="discountRatePercent"
              class="w-16 text-center bg-gray-800 text-white"
              step="1"
            />
          </div>
        </div>

        <div class="grid grid-cols-3 gap-4 mt-4">
          <div class="flex flex-col space-y-2 rounded-lg border p-4">
            <p class="text-lg text-center font-bold">Growth Stage</p>
            <div class="flex justify-center space-x-4">
              <p class="text-lg">Years</p>
              <div class="flex justify-center">
                <input
                  type="number"
                  v-model="years"
                  class="w-16 text-center bg-gray-800 text-white"
                />
              </div>
            </div>

            <div class="flex justify-center space-x-4">
              <p class="text-lg">Growth Rate</p>
              <div class="flex justify-center">
                <input
                  type="number"
                  v-model.number="growthRatePercent"
                  class="w-16 text-center bg-gray-800 text-white"
                  step="1"
                />
              </div>
            </div>
          </div>

          <div class="flex flex-col space-y-2 ml-8 rounded-lg border p-4">
            <p class="text-lg text-center font-bold">Terminal Stage</p>
            <div class="flex justify-center space-x-4">
              <p class="text-lg">Growth Rate</p>
              <div class="flex justify-center">
                <input
                  type="number"
                  v-model.number="perpetualGrowthRatePercent"
                  class="w-20 text-center bg-gray-800 text-white"
                  step="0.5"
                />
              </div>
            </div>
          </div>

          <div class="flex flex-col space-y-2 ml-8 rounded-lg border p-4">
            <p class="text-lg font-bold">Past FCF Growth Rate</p>
            <div class="space-y-2">
              <p class="flex justify-between text-lg">
                <span>10y</span>
                <span>{{ (cagr10y * 100).toFixed(0) }}%</span>
              </p>
              <p class="flex justify-between text-lg">
                <span>5y</span>
                <span>{{ (cagr5y * 100).toFixed(0) }}%</span>
              </p>
              <p class="flex justify-between text-lg">
                <span>1y</span>
                <span>{{ (cagr1y * 100).toFixed(0) }}%</span>
              </p>
            </div>
          </div>
        </div>

        <div class="border rounded-lg p-10 divide-y divide-white space-y-6 mt-4">
          <div class="flex justify-center space-x-4">
            <p class="text-lg">Stock Price</p>
            <p class="text-lg">${{ price.toFixed(2) }}</p>
          </div>
          <div class="flex justify-center space-x-4">
            <p class="text-lg">Fair Value</p>
            <p class="text-lg">${{ result.toFixed(2) }}</p>
          </div>
          <div class="flex justify-center space-x-4">
            <p class="text-lg">Margin of Safety</p>
            <p class="text-lg">{{ marginOfSafety * 100 }}%</p>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
