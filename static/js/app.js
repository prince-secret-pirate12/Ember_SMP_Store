function toast(msg){const d=document.createElement('div');d.className='flash';d.style.cssText='position:fixed;right:20px;bottom:20px;z-index:99';d.textContent=msg;document.body.appendChild(d);setTimeout(()=>d.remove(),1800)}
function copyIP(){navigator.clipboard.writeText(document.getElementById('ip').textContent);toast('Server IP copied!')}
function copyText(id){navigator.clipboard.writeText(document.getElementById(id).textContent);toast('Copied!')}
function confirmReset(form){const x=prompt('This is a destructive admin action. Type RESET to confirm.');if(x==='RESET'){form.querySelector('[name=confirm]').value='RESET';return true}return false}
