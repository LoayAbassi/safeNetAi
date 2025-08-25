import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import App from './App'
import Transfer from './pages/Transfer'
import AdminRisk from './pages/AdminRisk'
import Login from './pages/Login'

createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<App/>}>
        <Route index element={<Transfer/>} />
        <Route path="/admin" element={<AdminRisk/>} />
        <Route path="/login" element={<Login/>} />
      </Route>
    </Routes>
  </BrowserRouter>
)
