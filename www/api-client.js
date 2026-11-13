// Minimal client bridge for BioLearn Plus. Set API_BASE to your deployed API origin.
const API_BASE = "http://localhost:8000";
async function apiRequest(path, {method="GET", token, body}={}) {
  const response = await fetch(`${API_BASE}${path}`, {
    method, headers: {"Content-Type":"application/json", ...(token?{Authorization:`Bearer ${token}`}:{})},
    ...(body!==undefined?{body:JSON.stringify(body)}:{})
  });
  const data = await response.json().catch(()=>({detail:"Unexpected response"}));
  if(!response.ok) throw new Error(data.detail || `API error ${response.status}`);
  return data;
}
const BioLearnAPI = {
  lessons: (grade) => apiRequest(`/lessons${grade?`?grade=${encodeURIComponent(grade)}`:""}`),
  lesson: (id) => apiRequest(`/lessons/${encodeURIComponent(id)}`),
  login: (username,password) => apiRequest("/auth/login",{method:"POST",body:{username,password}}),
  register: (username,password) => apiRequest("/auth/register",{method:"POST",body:{username,password}}),
  saveProgress: (token,entry) => apiRequest("/progress",{method:"POST",token,body:entry}),
  progress: (token) => apiRequest("/progress",{token}),
  importLessons: (token,records) => apiRequest("/admin/import",{method:"POST",token,body:records})
};
