import React, { useState, useEffect } from 'react'
import { api } from '../api'

export default function Transfer(){
  const [accounts,setAccounts] = useState([])
  const [accountId,setAccountId] = useState('')
  const [toIban,setToIban] = useState('')
  const [amount,setAmount] = useState('')
  const [result,setResult] = useState(null)

  useEffect(()=>{
    api('me/accounts').then(setAccounts).catch(()=>{})
  },[])

  async function getLoc(){
    return new Promise((resolve,reject)=>navigator.geolocation.getCurrentPosition(resolve,reject))
  }

  async function onQuote(){
    const loc = await getLoc().catch(()=>null)
    const payload = { account_id:Number(accountId), to_iban:toIban, amount:Number(amount), currency:'TND' }
    if(loc){ payload.lat=loc.coords.latitude; payload.lng=loc.coords.longitude }
    const r = await api('transactions/quote', payload)
    setResult(r)
  }

  async function onInitiate(){
    const loc = await getLoc().catch(()=>null)
    const payload = { account_id:Number(accountId), to_iban:toIban, amount:Number(amount), currency:'TND' }
    if(loc){ payload.lat=loc.coords.latitude; payload.lng=loc.coords.longitude }
    const r = await api('transactions/initiate', payload)
    setResult(r)
  }

  return (
    <div>
      <h3>Transfer</h3>
      <div>
        <label>Account</label>
        <select value={accountId} onChange={e=>setAccountId(e.target.value)}>
          <option value="">-- choose --</option>
          {accounts.map(a=> <option key={a.id} value={a.id}>{a.iban} ({a.balance})</option>)}
        </select>
      </div>
      <div><input placeholder="To IBAN" value={toIban} onChange={e=>setToIban(e.target.value)} /></div>
      <div><input placeholder="Amount" value={amount} onChange={e=>setAmount(e.target.value)} /></div>
      <button onClick={onQuote}>Quote</button>
      <button onClick={onInitiate}>Initiate</button>
      {result && <pre>{JSON.stringify(result,null,2)}</pre>}
    </div>
  )
}
