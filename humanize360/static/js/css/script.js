function enviarwhats(event) {
    event.preventDefault();
    const nome = document.getElementById('nome_whats').value;
    const msg = document.getElementById('mensagem').value;
    window.open(`https://wa.me/5516994072626?text=Olá! Me chamo ${nome}. ${msg}`, '_blank');
    event.target.reset(); 
}

window.onload = () => { document.getElementById('whatsapp-toggle').checked = false; };
window.onpageshow = (e) => { if (e.persisted) document.getElementById('whatsapp-toggle').checked = false; };