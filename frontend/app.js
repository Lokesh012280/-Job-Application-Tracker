const API = "";
let token = localStorage.getItem("jobtrack_token") || "";
let page = 1, totalPages = 1, mode = "login", editingId = null;
const $ = (id) => document.getElementById(id);
const statuses = ["SAVED","APPLIED","SCREENING","INTERVIEW","OFFER","ACCEPTED","REJECTED","WITHDRAWN"];
const today = new Date().toISOString().slice(0,10);
$("applied_date").value = today;

function message(id, text, good=false){ const el=$(id); el.textContent=text||""; el.style.color=good?"#138a65":"#c24141"; }
function toast(text){ const el=$("toast");el.textContent=text;el.classList.add("show");setTimeout(()=>el.classList.remove("show"),2600); }
async function api(path, options={}) {
  const headers = {"Content-Type":"application/json", ...(options.headers||{})};
  if(token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(API+path,{...options,headers});
  if(res.status===204) return null;
  const body = await res.json().catch(()=>({detail:"Unexpected server response"}));
  if(!res.ok) throw new Error(body.detail || "Request failed");
  return body;
}
function setMode(next){mode=next;$("loginTab").classList.toggle("active",mode==="login");$("registerTab").classList.toggle("active",mode==="register");$("nameField").classList.toggle("hidden",mode!=="register");$("authSubmit").textContent=mode==="login"?"Login":"Create account";$("password").autocomplete=mode==="login"?"current-password":"new-password";message("authMessage","");}
$("loginTab").onclick=()=>setMode("login");$("registerTab").onclick=()=>setMode("register");
$("authForm").onsubmit=async(e)=>{e.preventDefault();message("authMessage","");try{
  if(mode==="register"){await api("/auth/register",{method:"POST",body:JSON.stringify({name:$("name").value.trim(),email:$("email").value.trim(),password:$("password").value})});message("authMessage","Account created. You can log in now.",true);setMode("login");}
  else{const data=await api("/auth/login",{method:"POST",body:JSON.stringify({email:$("email").value.trim(),password:$("password").value})});token=data.access_token;localStorage.setItem("jobtrack_token",token);await showApp();}
}catch(err){message("authMessage",err.message)}};
$("logoutBtn").onclick=()=>{token="";localStorage.removeItem("jobtrack_token");$("appView").classList.add("hidden");$("authView").classList.remove("hidden");$("userArea").innerHTML='<span class="muted">Keep your search organized</span>';};
async function showApp(){try{const me=await api("/auth/me");$("authView").classList.add("hidden");$("appView").classList.remove("hidden");$("userArea").innerHTML=`<span class="muted">Welcome, <strong>${escapeHtml(me.name)}</strong></span>`;await refreshAll();}catch(e){token="";localStorage.removeItem("jobtrack_token");$("authView").classList.remove("hidden");$("appView").classList.add("hidden");}}
function escapeHtml(v){return String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
async function refreshAll(){await Promise.all([loadDashboard(),loadApplications(),loadUpcoming()]);}
async function loadDashboard(){const d=await api("/dashboard");const cards=[["Total applications",d.total_applications,"All tracked opportunities"],["Interviews",d.interviews,"Applications at interview stage"],["Offers",d.offers,"Offers and accepted"],["Accepted",d.accepted,"Final positive outcomes"],["Interview rate",`${d.interview_rate_percent}%`,"Based on applications + rounds"]];$("stats").innerHTML=cards.map(c=>`<div class="stat-card"><span>${c[0]}</span><strong>${c[1]}</strong><small>${c[2]}</small></div>`).join("");}
async function loadApplications(){const p=new URLSearchParams({page,limit:10,sort:"applied_date",order:"desc"});if($("searchCompany").value.trim())p.set("company",$("searchCompany").value.trim());if($("searchTitle").value.trim())p.set("job_title",$("searchTitle").value.trim());if($("statusFilter").value)p.set("status",$("statusFilter").value);const result=await api("/applications?"+p);totalPages=Math.max(1,result.total_pages);$("pageInfo").textContent=`Page ${page} of ${totalPages} · ${result.total} application${result.total===1?"":"s"}`;$("prevBtn").disabled=page<=1;$("nextBtn").disabled=page>=totalPages;
  if(!result.data.length){$("applicationRows").innerHTML='<tr><td colspan="5" class="empty">No applications yet. Add your first opportunity.</td></tr>';return;}
  $("applicationRows").innerHTML=result.data.map(a=>`<tr><td><div class="company-cell"><strong>${escapeHtml(a.company_name)}</strong><small>${escapeHtml(a.job_title)}</small></div></td><td>${escapeHtml(a.location)}</td><td>${escapeHtml(a.applied_date)}</td><td><span class="status ${a.status}">${a.status}</span></td><td><div class="row-actions"><button class="outline small" onclick="editApplication(${a.id})">Edit</button><button class="outline small" onclick="addNote(${a.id})">Note</button><button class="outline small" onclick="deleteApplication(${a.id})">Delete</button></div></td></tr>`).join("");}
async function loadUpcoming(){const [interviews,followups]=await Promise.all([api("/dashboard/upcoming-interviews"),api("/dashboard/upcoming-followups")]);$("interviewList").innerHTML=interviews.length?interviews.slice(0,5).map(i=>`<div class="list-item"><div><strong>${escapeHtml(i.company_name)} · ${escapeHtml(i.round)}</strong><small>${escapeHtml(i.job_title)}</small></div><span class="list-date">${i.interview_date}${i.interview_time?" · "+String(i.interview_time).slice(0,5):""}</span></div>`).join(""):'<p class="empty">No upcoming interviews.</p>';$("followupList").innerHTML=followups.length?followups.slice(0,5).map(f=>`<div class="list-item"><div><strong>${escapeHtml(f.company_name)}</strong><small>${escapeHtml(f.note||f.job_title||"Follow up with recruiter")}</small></div><span class="list-date">${f.follow_up_date}</span></div>`).join(""):'<p class="empty">No upcoming follow-ups.</p>';}
$("filterBtn").onclick=()=>{page=1;loadApplications().catch(e=>toast(e.message));};$("clearBtn").onclick=()=>{$("searchCompany").value="";$("searchTitle").value="";$("statusFilter").value="";page=1;loadApplications().catch(e=>toast(e.message));};$("prevBtn").onclick=()=>{if(page>1){page--;loadApplications().catch(e=>toast(e.message));}};$("nextBtn").onclick=()=>{if(page<totalPages){page++;loadApplications().catch(e=>toast(e.message));}};
function openDialog(){ $("applicationDialog").showModal(); }
function closeDialog(){ $("applicationDialog").close(); }
$("addBtn").onclick=()=>{editingId=null;$("applicationForm").reset();$("applicationId").value="";$("applied_date").value=today;$("location").value="Hyderabad";$("dialogTitle").textContent="Add application";$("saveApplication").textContent="Save application";message("formMessage","");openDialog();};
$("closeDialog").onclick=closeDialog;$("cancelDialog").onclick=closeDialog;
const formFields={company_name:"company_name",job_title:"job_title",location:"location",employment_type:"employment_type",source:"source",status:"appStatus",applied_date:"applied_date",job_url:"job_url",salary_min:"salary_min",salary_max:"salary_max",description:"description"};
function readApplicationForm(){const v={};for(const [key,id] of Object.entries(formFields)){let value=$(id).value;if(["salary_min","salary_max"].includes(key))value=value===""?null:Number(value);if(["job_url","description"].includes(key)&&!value)value=null;if(key==="job_url"&&value==="")value=null;v[key]=value;}return v;}
async function editApplication(id){try{const a=await api("/applications/"+id);editingId=id;$("dialogTitle").textContent="Edit application";$("saveApplication").textContent="Save changes";message("formMessage","");for(const [key,idField] of Object.entries(formFields))$(idField).value=a[key]??"";openDialog();}catch(e){toast(e.message);}}
window.editApplication=editApplication;
$("applicationForm").onsubmit=async(e)=>{e.preventDefault();try{const payload=readApplicationForm();if(payload.salary_min!==null&&payload.salary_max!==null&&payload.salary_max<payload.salary_min)throw new Error("Maximum salary must be at least minimum salary.");await api(editingId?`/applications/${editingId}`:"/applications",{method:editingId?"PUT":"POST",body:JSON.stringify(payload)});closeDialog();toast(editingId?"Application updated":"Application added");await refreshAll();}catch(err){message("formMessage",err.message);}};
async function deleteApplication(id){if(!confirm("Delete this application and its interviews, notes and follow-ups?"))return;try{await api("/applications/"+id,{method:"DELETE"});toast("Application deleted");await refreshAll();}catch(e){toast(e.message);}}window.deleteApplication=deleteApplication;
async function addNote(id){const content=prompt("Enter a note for this application:");if(!content||!content.trim())return;try{await api(`/applications/${id}/notes`,{method:"POST",body:JSON.stringify({content:content.trim()})});toast("Note saved");}catch(e){toast(e.message);}}window.addNote=addNote;
if(token)showApp();
