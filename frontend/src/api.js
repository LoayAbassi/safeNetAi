export async function api(path, body){
  const res = await fetch('/api/' + path, {
    method: body ? 'POST' : 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(localStorage.getItem('token') ? {Authorization: 'Bearer ' + localStorage.getItem('token')} : {})
    },
    body: body ? JSON.stringify(body) : undefined
  })
  if(!res.ok){
    const t = await res.text()
    throw new Error(t || res.statusText)
  }
  return res.json()
}
