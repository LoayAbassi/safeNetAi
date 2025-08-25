import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function AdminRisk(){
  const [thresholds,setThresholds]=useState([])
  const [saving,setSaving]=useState(false)

  useEffect(()=>{ api('risk/thresholds').then(setThresholds) },[])

  async function save(){
    setSaving(true)
    await Promise.all(thresholds.map(t=>fetch(`/api/risk/thresholds/${t.id}/`,{
      method:'PUT', headers:{'Content-Type':'application/json', ...(localStorage.getItem('token') ? {Authorization: 'Bearer ' + localStorage.getItem('token')} : {})}, body:JSON.stringify({id:t.id,key:t.key,value:Number(t.value)})
    })))
    setSaving(false)
  }

  return (
    <div>
      <h3>Admin Risk Controls</h3>
      {thresholds.map((t,i)=>(
        <div key={t.id} style={{display:'flex', gap:8, alignItems:'center'}}>
          <b style={{width:180}}>{t.key}</b>
          <input value={t.value} onChange={e=>{
            const v=[...thresholds]; v[i]={...v[i], value:e.target.value}; setThresholds(v)
          }}/>
        </div>
      ))}
      <button onClick={save} disabled={saving}>{saving?'Saving...':'Save'}</button>
    </div>
  )
}
