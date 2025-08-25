import React from 'react'
import { Link, Outlet, useNavigate } from 'react-router-dom'

export default function App(){
  const nav = useNavigate()
  function logout(){ localStorage.removeItem('token'); nav('/login') }
  return (
    <div style={{fontFamily:'sans-serif', padding:16}}>
      <h2>AI Fraud Detection MVP</h2>
      <nav style={{display:'flex', gap:12}}>
        <Link to="/">Transfer</Link>
        <Link to="/admin">Admin</Link>
        <Link to="/login">Login</Link>
        <button onClick={logout}>Logout</button>
      </nav>
      <hr/>
      <Outlet/>
    </div>
  )
}
