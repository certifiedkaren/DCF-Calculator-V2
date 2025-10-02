<script setup lang="ts">
import { ref, computed } from 'vue'
import { fetchEps } from '../stocks'
import { Line } from 'vue-chartjs'
import {
  Chart,
  LineElement,
  PointElement,
  LinearScale,
  TimeScale,
  Tooltip,
  Legend,
  Filler,
  Title,
  CategoryScale,
} from 'chart.js'

import 'chartjs-adapter-date-fns'

Chart.register(
  LineElement,
  PointElement,
  LinearScale,
  TimeScale,
  Tooltip,
  Legend,
  Filler,
  Title,
  CategoryScale,
)

const earnings = ref<[string, number][]>()

const sorted = computed(() =>
  earnings.value
    ? [...earnings.value].sort((a, b) => new Date(a[0]).getTime() - new Date(b[0]).getTime())
    : [],
)

const labels = computed(() => sorted.value.map(([d]) => new Date(d)))
const values = computed(() => sorted.value.map(([, v]) => v))

const data = computed(() => ({
  labels: labels.value,
  datasets: [
    {
      label: 'EPS',
      data: values.value,
      fill: false,
      tension: 0.25,
      pointRadius: 2,
      borderWidth: 2,
      borderColor: '#3b82f6',
      backgroundColor: '#3b82f6',
    },
  ],
}))

const options = {
  responsive: true,
  maintainAspectRatio: false,
  animation: { duration: 300 },
  scales: {
    x: {
      type: 'time' as const,
      time: {},
      ticks: { maxRotation: 0, autoSkip: true, color: '#9ca3af' },
      grid: {
        color: 'rgba(255, 255, 255, 0.1)',
      },
    },
    y: {
      beginAtZero: false,
      ticks: {
        callback: (v: number) => `${v.toFixed(2)}`,
        color: '#9ca3af',
      },
      grid: {
        color: 'rgba(255, 255, 255, 0.1)',
      },
      title: {
        display: true,
        text: 'EPS',
        color: '#9ca3af',
      },
    },
  },
  plugins: {
    title: {
      display: true,
      text: 'Quarterly EPS',
      color: 'white',
    },
    tooltip: {
      intersect: false,
      mode: 'index' as const,
      callbacks: {
        title: (items: any[]) => {
          const d = items[0].parsed.x
          return new Date(d).toLocaleDateString()
        },
        label: (ctx: any) => `${ctx.dataset.label}: ${ctx.parsed.y}`,
      },
    },
    legend: {
      display: true,
      labels: {
        color: 'white',
      },
    },
  },
}

const ticker = ref('')
const input = ref('')
const error = ref('')
const loading = ref(false)

const saveInput = () => {
  if (input.value) {
    ticker.value = input.value.toUpperCase()
    input.value = ''
  }
}

const getEps = async () => {
  if (!ticker.value) return
  error.value = ''
  earnings.value = undefined
  try {
    const eps = await fetchEps(ticker.value)
    earnings.value = eps
  } catch (err: any) {
    error.value = err?.message ?? 'Something Went Wrong'
  }
}

const handleConfirm = async () => {
  saveInput()
  if (!ticker.value) return
  loading.value = true

  try {
    await getEps()
  } catch (err: any) {
    error.value = 'Failed to fetch data. Please check the ticker and try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen p-4 sm:p-6 md:p-8 text-white bg-zinc-950">
    <div class="max-w-4xl mx-auto flex flex-col items-center space-y-6">
      <h1 class="text-4xl font-bold tracking-tight">Earnings Per Share (EPS)</h1>
      <div class="flex items-center space-x-2">
        <input
          type="text"
          placeholder="Enter Ticker (e.g., AAPL)"
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

      <div v-if="loading" class="text-lg text-zinc-400">Loading chart...</div>
      <div v-if="error" class="text-lg text-red-500 bg-red-900/20 px-4 py-2 rounded-md">
        {{ error }}
      </div>
      <div v-if="ticker && !loading && !error" class="text-2xl font-semibold text-zinc-200">
        {{ ticker }}
      </div>
    </div>

    <div
      v-if="earnings && !loading"
      class="mt-8 max-w-5xl mx-auto h-96 rounded-xl bg-white/5 p-4 shadow-2xl ring-1 ring-white/10"
    >
      <Line :data="data" :options="options" />
    </div>
    <div v-if="!earnings && !loading && !error && ticker" class="mt-8 text-center text-zinc-500">
      No data available for the specified ticker.
    </div>
  </div>
</template>
