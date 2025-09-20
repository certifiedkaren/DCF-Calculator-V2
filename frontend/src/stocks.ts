import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 10000,
})

const capmCache = new Map<string, number>()
const baseFcfCache = new Map<string, number>()
const waccCache = new Map<string, number>()
const pastFcfCache = new Map<string, number[]>()

export async function fetchPastFcf(ticker: string): Promise<number[]> {
  if (pastFcfCache.has(ticker)) return pastFcfCache.get(ticker)!
  const { data } = await api.get(`/pastfcf/${ticker}`)
  pastFcfCache.set(ticker, data.pastfcf)
  return data.pastfcf
}

export function calcCagr(series: number[], years: number): number {
  if (series.length < years + 1) throw new Error('Not enough data')
  const end = series[0]
  const start = series[years]
  if (start <= 0 || end <= 0) throw new Error('Non-positive FCF value makes CAGR undefined')
  const cagr = Math.pow(end / start, 1 / years) - 1
  return Math.round(cagr * 100) / 100
}

export async function fetchCapm(ticker: string): Promise<number> {
  if (capmCache.has(ticker)) return capmCache.get(ticker)!
  const { data } = await api.get(`/capm/${ticker}`)
  capmCache.set(ticker, data.capm)
  return data.capm
}

export async function fetchBaseFcf(ticker: string): Promise<number> {
  if (baseFcfCache.has(ticker)) return baseFcfCache.get(ticker)!
  const { data } = await api.get(`/basefcf/${ticker}`)
  baseFcfCache.set(ticker, data.basefcf)
  return data.basefcf
}

export async function fetchWacc(ticker: string, capm: number): Promise<number> {
  const key = `${ticker}:${capm}`
  if (waccCache.has(key)) return waccCache.get(key)!
  const roundedCapm = Number.isFinite(capm) ? capm.toFixed(3) : `${capm}`
  const { data } = await api.get(`/wacc/${ticker}/${roundedCapm}`)
  waccCache.set(key, data.wacc)
  return data.wacc
}

export async function fetchDcf(
  ticker: string,
  payload: {
    base_fcf: number
    growth_rate: number
    perpetual_growth_rate: number
    discount_rate: number
    years: number
  },
) {
  const { data } = await api.post(`/dcf/${ticker}`, payload)
  return data
}

export async function fetchAllForTicker(
  ticker: string,
  opts: {
    growth_rate: number
    perpetual_growth_rate: number
    years: number
  },
) {
  const [capm, base_fcf] = await Promise.all([fetchCapm(ticker), fetchBaseFcf(ticker)])
  const wacc = await fetchWacc(ticker, capm)
  const dcf = await fetchDcf(ticker, {
    base_fcf,
    growth_rate: opts.growth_rate,
    perpetual_growth_rate: opts.perpetual_growth_rate,
    discount_rate: wacc,
    years: opts.years,
  })
  return { capm, base_fcf, wacc, dcf }
}
