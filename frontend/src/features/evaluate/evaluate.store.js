import { createStore } from '../../store/createStore'
import { evaluateApi } from './evaluate.api'
export const useEvaluate = createStore([
  (set)=>({
    rows:[], error:'',
    async refresh(){ try{ set({rows: await evaluateApi.run(), error:''}) }catch(e){ set({error:e.message}) } }
  })
])
