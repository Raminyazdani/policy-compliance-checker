import { create } from 'zustand'
export const createStore = (slices) => create((set,get) => {
  const bound = {}
  for (const fn of slices) Object.assign(bound, fn(set,get))
  return bound
})
