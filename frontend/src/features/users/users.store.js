import { createStore } from '../../store/createStore'
import { usersApi } from './users.api'
export const useUsers = createStore([
  (set,get)=>({
    items:[], error:'',
    async refresh(){ try{ set({items: await usersApi.list(), error:''}) }catch(e){ set({error:e.message}) } },
    async createOne(u){ await usersApi.create(u); await get().refresh() },
    async updateOne(id,u){ await usersApi.put(id,u); await get().refresh() },
    async deleteOne(id){ await usersApi.del(id); await get().refresh() },
    async getOne(id){ return usersApi.get(id) }
  })
])
