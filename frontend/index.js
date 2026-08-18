(function(){
const loginForm=document.getElementById('loginForm');
const registerForm=document.getElementById('registerForm');
const forgotForm=document.getElementById('forgotForm');
const resetForm=document.getElementById('resetForm');
const formTitle=document.getElementById('formTitle');
const formSubtitle=document.getElementById('formSubtitle');
const switchLine=document.getElementById('switchLine');
const forgotLine=document.getElementById('forgotLine');
const forgotBtn=document.getElementById('forgotBtn');
const messageBox=document.getElementById('message');
const todosOsFormularios=[loginForm,registerForm,forgotForm,resetForm];
let mode='login';let resetToken=null;
const params=new URLSearchParams(window.location.search);
const verifyToken=params.get('verify_token');resetToken=params.get('reset_token');

if(Auth.isLoggedIn()&&!verifyToken&&!resetToken){window.location.href='dashboard.html';return;}

function showMessage(text,type){messageBox.textContent=text;messageBox.className='message show '+type;}
function clearMessage(){messageBox.className='message';messageBox.textContent='';}
function setLoading(form,loading,text){
 const button=form.querySelector('button[type="submit"]');if(!button)return;
 const label=button.querySelector('.btn-label');
 if(!button.dataset.originalText&&label)button.dataset.originalText=label.textContent;
 button.disabled=loading;if(label)label.textContent=loading?text:button.dataset.originalText;
}
document.querySelectorAll('.password-toggle').forEach(button=>{
 button.addEventListener('click',()=>{
   const target=document.getElementById(button.dataset.target);if(!target)return;
   const mostrando=target.type==='text';target.type=mostrando?'password':'text';
   button.textContent=mostrando?'Mostrar':'Ocultar';
 });
});
function conectarSwitchButton(){
 const btn=document.getElementById('switchBtn');if(!btn)return;
 btn.addEventListener('click',()=>setMode(mode==='login'?'register':'login'));
}
function setMode(newMode){
 mode=newMode;clearMessage();todosOsFormularios.forEach(f=>f.classList.remove('active'));forgotLine.style.display='none';
 if(mode==='login'){loginForm.classList.add('active');formTitle.textContent='Bem-vindo de volta';formSubtitle.textContent='Entre com sua conta para continuar';switchLine.innerHTML='Ainda não tem conta? <button type="button" id="switchBtn">Criar cadastro</button>';forgotLine.style.display='block';}
 else if(mode==='register'){registerForm.classList.add('active');formTitle.textContent='Criar cadastro';formSubtitle.textContent='Preencha os dados para começar';switchLine.innerHTML='Já tem conta? <button type="button" id="switchBtn">Fazer login</button>';}
 else if(mode==='forgot'){forgotForm.classList.add('active');formTitle.textContent='Esqueci minha senha';formSubtitle.textContent='Informe seu e-mail para receber o link de redefinição';switchLine.innerHTML='Lembrou a senha? <button type="button" id="switchBtn">Fazer login</button>';}
 else {resetForm.classList.add('active');formTitle.textContent='Criar nova senha';formSubtitle.textContent='Digite sua nova senha de acesso';switchLine.innerHTML='Lembrou a senha? <button type="button" id="switchBtn">Fazer login</button>';}
 conectarSwitchButton();
}
conectarSwitchButton();
forgotBtn.addEventListener('click',()=>setMode('forgot'));

registerForm.addEventListener('submit',async e=>{
 e.preventDefault();clearMessage();
 const name=document.getElementById('registerName').value.trim();
 const email=document.getElementById('registerEmail').value.trim().toLowerCase();
 const password=document.getElementById('registerPassword').value;
 const confirm=document.getElementById('registerPasswordConfirm').value;
 const acceptedTerms=document.getElementById('legalAccept').checked;
 if(!acceptedTerms){showMessage('Leia e aceite os Termos de Uso e declare ciência da Política de Privacidade para criar a conta.','error');return;}
 if(password!==confirm){showMessage('As senhas não coincidem.','error');return;}
 if(password.length<6){showMessage('A senha precisa ter pelo menos 6 caracteres.','error');return;}
 try{setLoading(registerForm,true,'Criando conta...');await Api.post('/auth/register',{name,email,password,accepted_terms:true,terms_version:'1.0-2026-08-18',privacy_version:'1.0-2026-08-18'},{auth:false});showMessage('Conta criada! Enviamos um link de confirmação para o seu e-mail. Verifique também a caixa de spam.','success');registerForm.reset();setTimeout(()=>setMode('login'),2500);}
 catch(err){showMessage(err.message,'error');}finally{setLoading(registerForm,false);}
});

loginForm.addEventListener('submit',async e=>{
 e.preventDefault();clearMessage();
 const email=document.getElementById('loginEmail').value.trim().toLowerCase();
 const password=document.getElementById('loginPassword').value;
 try{
  setLoading(loginForm,true,'Entrando...');
  const {access_token}=await Api.login(email,password);
  const me=await Api.get('/users/me',{headers:{Authorization:`Bearer ${access_token}`}});
  Auth.saveSession({name:me.name,email:me.email,token:access_token});
  window.location.href='dashboard.html';
 }catch(err){
  showMessage(err.message,'error');
  if(err.message&&err.message.toLowerCase().includes('confirme seu e-mail')){
   try{await Api.post('/auth/resend-verification',{email},{auth:false});showMessage(err.message+' Reenviamos o link de confirmação para o seu e-mail.','error');}catch(_){}
  }
 }finally{setLoading(loginForm,false);}
});

forgotForm.addEventListener('submit',async e=>{
 e.preventDefault();clearMessage();
 const email=document.getElementById('forgotEmail').value.trim().toLowerCase();
 try{setLoading(forgotForm,true,'Enviando...');await Api.post('/auth/forgot-password',{email},{auth:false});showMessage('Se esse e-mail estiver cadastrado, enviamos um link para redefinir a senha. Verifique sua caixa de entrada.','success');forgotForm.reset();}
 catch(err){showMessage(err.message,'error');}finally{setLoading(forgotForm,false);}
});

resetForm.addEventListener('submit',async e=>{
 e.preventDefault();clearMessage();
 const novaSenha=document.getElementById('resetPassword').value;
 const confirmacao=document.getElementById('resetPasswordConfirm').value;
 if(novaSenha!==confirmacao){showMessage('As senhas não coincidem.','error');return;}
 if(novaSenha.length<6){showMessage('A senha precisa ter pelo menos 6 caracteres.','error');return;}
 if(!resetToken){showMessage('Link inválido. Solicite a redefinição novamente.','error');return;}
 try{setLoading(resetForm,true,'Salvando...');await Api.post('/auth/reset-password',{token:resetToken,new_password:novaSenha},{auth:false});showMessage('Senha redefinida com sucesso! Faça login com a nova senha.','success');resetForm.reset();resetToken=null;window.history.replaceState({},'','index.html');setTimeout(()=>setMode('login'),1800);}
 catch(err){showMessage(err.message,'error');}finally{setLoading(resetForm,false);}
});

if(resetToken){setMode('reset');}
else if(verifyToken){
 setMode('login');showMessage('Confirmando seu e-mail...','success');
 Api.post('/auth/verify-email',{token:verifyToken},{auth:false})
 .then(()=>{showMessage('E-mail confirmado com sucesso! Já pode fazer login.','success');window.history.replaceState({},'','index.html');})
 .catch(err=>{showMessage(err.message,'error');window.history.replaceState({},'','index.html');});
}else setMode('login');
})();