import { useState } from 'react'
import AppShell from './app/AppShell'
import PoliciesPanel from './features/policies/PoliciesPanel'
import UsersPanel from './features/users/UsersPanel'
import EvaluatePanel from './features/evaluate/EvaluatePanel'

export default function App(){
  const [tab,setTab] = useState(0) // 0:policies, 1:users, 2:evaluate
  return (
    <AppShell navIndex={tab} onNavChange={setTab}>
      {tab===0 && <PoliciesPanel/>}
      {tab===1 && <UsersPanel/>}
      {tab===2 && <EvaluatePanel/>}
    </AppShell>
  )
}
