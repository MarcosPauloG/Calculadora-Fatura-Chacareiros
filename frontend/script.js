const names = [
  'SALVADOR CASER NETTO','CHRISTIRSON PAULA DE ARAUJO','FLAVIO VIDAL','MILKA VIANA FALCAO',
  'GIRLEY NOGUEIRA DE JESUS (Cha-12)','FERNANDO ANDRÉ DE SOUZA (Cha-16)','OSMAIR TELES BUENO',
  'WEVERTON NUNES DA SILVA','LUCIANE FERREIRA','PAULO MARCOS DIAS (Cha-13)'
];
const rows = document.getElementById('rows');
const result = document.getElementById('result');
let currentUser = null;

function addRow(nome) {
  const div = document.createElement('div');
  div.className = 'row4';
  div.innerHTML = `<input value="${nome}" /><input type="number" placeholder="Leitura"/><input placeholder="URL foto Drive"/><input type="number" placeholder="Leitura anterior"/>`;
  rows.appendChild(div);
}
names.forEach(addRow);
document.getElementById('dataUnica').valueAsDate = new Date();

document.getElementById('themeBtn').onclick = () => {
  const root = document.documentElement;
  root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
};

document.getElementById('loginBtn').onclick = async () => {
  const payload = { username: username.value, password: password.value };
  const r = await fetch('/api/login', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)});
  const data = await r.json();
  if (!r.ok) return alert(data.detail || 'Erro no login');
  currentUser = data;
  loginInfo.textContent = `Bem-vindo(a), ${data.nome}`;
  if (data.must_change_password) {
    changePassCard.hidden = false;
  } else {
    appCard.hidden = false;
    if (data.role === 'admin') adminCard.hidden = false;
  }
};

document.getElementById('changePassBtn').onclick = async () => {
  const r = await fetch('/api/change-password', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({
    username: currentUser.username, current_password: currentPass.value, new_password: newPass.value
  })});
  const data = await r.json();
  if (!r.ok) return alert(data.detail || 'Erro');
  alert('Senha alterada com sucesso');
  changePassCard.hidden = true;
  appCard.hidden = false;
  if (currentUser.role === 'admin') adminCard.hidden = false;
};

document.getElementById('saveBulk').onclick = async () => {
  const itens = [...rows.querySelectorAll('.row4')].map(r => {
    const [nome, leituraAtual, fotoUrl, leituraAnterior] = r.querySelectorAll('input');
    return { nome: nome.value, leitura_atual: leituraAtual.value, foto_url: fotoUrl.value, leitura_anterior: leituraAnterior.value };
  });
  const payload = { data_leitura: dataUnica.value, referencia: referencia.value || 'N/A', itens, n8n_webhook_url: n8nWebhook.value || null };
  const resp = await fetch('/api/readings/bulk', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)});
  const data = await resp.json();
  alert(data.message || 'Salvo');
};

document.getElementById('calc').onclick = async () => {
  const participantes = [...rows.querySelectorAll('.row4')].map((r) => {
    const [nome, leituraAtual, _, leituraAnterior] = r.querySelectorAll('input');
    return { nome: nome.value, leitura_anterior: Number(leituraAnterior.value), leitura_atual: Number(leituraAtual.value) };
  });
  const payload = {
    referencia: referencia.value || 'N/A',
    data_leitura: dataUnica.value,
    valor_total: Number(valorTotal.value),
    leitura_geral_anterior: Number(geralAnterior.value),
    leitura_geral_atual: Number(geralAtual.value),
    participantes,
  };
  const resp = await fetch('/api/rateio', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)});
  const data = await resp.json();
  if (!resp.ok) return alert(data.detail || 'Erro');
  result.textContent = JSON.stringify(data, null, 2);
  resultCard.hidden = false;
};

document.getElementById('resetBtn').onclick = async () => {
  const payload = { admin_user: currentUser.username, admin_password: adminPass.value, target_user: targetUser.value };
  const resp = await fetch('/api/admin/reset-password', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)});
  const data = await resp.json();
  if (!resp.ok) return alert(data.detail || 'Erro');
  alert(`Senha resetada para padrão: ${data.temp_password}`);
};
