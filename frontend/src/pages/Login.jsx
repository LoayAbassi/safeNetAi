import React, { useState } from 'react'

export default function Login(){
  const [username,setUsername]=useState('')
  const [password,setPassword]=useState('')
  async function login(){
    const res = await fetch('/api/auth/login',{
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({username,password})
    })
    const data = await res.json()
    if(data.access){ localStorage.setItem('token', data.access); window.location.href='/' }
    else alert('login failed')
  }
  return (
    <div>
      <h3>Login</h3>
      <input placeholder="username" value={username} onChange={e=>setUsername(e.target.value)} />
      <input placeholder="password" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
      <button onClick={login}>Login</button>
    </div>
  )
}
