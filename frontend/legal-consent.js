(function(){
 if(!Auth.isLoggedIn()){window.location.href='index.html';return;}
 const form=document.getElementById('legalConsentForm');
 const msg=document.getElementById('message');
 function show(t,c){msg.textContent=t;msg.className='message show '+c;}
 Api.get('/privacy/legal-status').then(s=>{if(s.complete)window.location.href='dashboard.html';}).catch(e=>show(e.message,'error'));
 form.addEventListener('submit',async e=>{
  e.preventDefault();
  const terms=Boolean(document.getElementById('legalTerms').checked);
  const privacy=Boolean(document.getElementById('legalPrivacy').checked);
  if(!terms||!privacy){show('É necessário confirmar os dois documentos.','error');return;}
  const btn=form.querySelector('button[type="submit"]');btn.disabled=true;
  try{await Api.post('/privacy/accept-legal',{terms_accepted:terms,privacy_acknowledged:privacy});window.location.href='dashboard.html';}
  catch(err){show(err.message,'error');btn.disabled=false;}
 });
})();
