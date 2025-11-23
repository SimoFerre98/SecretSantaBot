document.addEventListener('DOMContentLoaded', () => {
    const tg = window.Telegram.WebApp;

    // Inizializza la WebApp
    tg.expand();
    tg.MainButton.textColor = '#FFFFFF';
    tg.MainButton.color = '#0f5132';

    // Elementi UI
    const userNameEl = document.getElementById('userName');
    const userAvatarEl = document.getElementById('userAvatar');
    const wishlistInput = document.getElementById('wishlistInput');
    const saveBtn = document.getElementById('saveWishlistBtn');

    // Dati utente (Mock se non siamo su Telegram)
    const user = tg.initDataUnsafe.user || {
        first_name: "Ospite",
        username: "guest",
        photo_url: null
    };

    // Popola UI
    userNameEl.textContent = user.first_name;
    if (user.photo_url) {
        userAvatarEl.innerHTML = `<img src="${user.photo_url}" style="width:100%;height:100%;border-radius:50%">`;
    }

    // Funzione per caricare i gruppi
    function loadGroups() {
        const groupListEl = document.getElementById('groupList');
        groupListEl.innerHTML = '<div class="group-item" style="justify-content: center;"><span>Caricamento...</span></div>';

        fetch('/api/groups')
            .then(response => response.json())
            .then(groups => {
                groupListEl.innerHTML = ''; // Pulisci

                if (Object.keys(groups).length === 0) {
                    groupListEl.innerHTML = '<div class="group-item"><span>Nessun gruppo trovato.</span></div>';
                    return;
                }

                for (const [id, group] of Object.entries(groups)) {
                    const item = document.createElement('div');
                    item.className = 'group-item';
                    item.style.cursor = 'pointer'; // Indica che è cliccabile

                    const nameSpan = document.createElement('span');
                    nameSpan.textContent = group.name;

                    const badge = document.createElement('span');
                    badge.className = 'badge';
                    if (group.visibility === 'private') {
                        badge.textContent = '🔒 Privato';
                        badge.style.background = '#6c757d';
                        badge.style.color = 'white';
                    } else {
                        badge.textContent = '🔓 Pubblico';
                        badge.style.background = '#28a745';
                        badge.style.color = 'white';
                    }

                    item.appendChild(nameSpan);
                    item.appendChild(badge);

                    // Gestione click per unirsi
                    item.addEventListener('click', () => {
                        let accessCode = null;
                        if (group.visibility === 'private') {
                            accessCode = prompt(`Inserisci il codice di accesso per "${group.name}":`);
                            if (accessCode === null) return; // Annullato
                        }

                        // Chiama API per unirsi
                        const currentUser = window.Telegram.WebApp.initDataUnsafe.user || { first_name: "Ospite" };

                        fetch('/api/join', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                group_id: id,
                                user_name: currentUser.first_name,
                                access_code: accessCode
                            })
                        })
                            .then(res => res.json())
                            .then(data => {
                                if (data.success) {
                                    window.Telegram.WebApp.showAlert(data.message);
                                    // Aggiorna UI o ricarica
                                    loadGroups();
                                } else {
                                    window.Telegram.WebApp.showAlert("❌ " + data.message);
                                }
                            })
                            .catch(err => {
                                console.error("Errore join:", err);
                                window.Telegram.WebApp.showAlert("Errore di connessione.");
                            });
                    });

                    groupListEl.appendChild(item);
                }
            })
            .catch(err => {
                console.error("Errore caricamento gruppi:", err);
                groupListEl.innerHTML = '<div class="group-item"><span>Errore caricamento.</span></div>';
            });
    }

    // Carica i gruppi all'avvio
    loadGroups();

    // Bottone refresh
    const refreshBtn = document.getElementById('refreshGroupsBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            loadGroups();
        });
    }

    // Gestione salvataggio Wishlist
    saveBtn.addEventListener('click', () => {
        const wish = wishlistInput.value;
        if (wish.trim() === "") {
            tg.showAlert("Scrivi qualcosa prima di salvare!");
            return;
        }

        // Simulazione salvataggio (qui si chiamerebbe un'API backend)
        tg.MainButton.setText("Desiderio Salvato!");
        tg.MainButton.show();

        // Feedback visivo
        saveBtn.textContent = "✅ Salvato!";
        saveBtn.style.backgroundColor = "#198754";
        setTimeout(() => {
            saveBtn.textContent = "Salva Desiderio";
            saveBtn.style.backgroundColor = "";
        }, 2000);

        // Invia dati al bot (chiude la webview e manda i dati)
        // tg.sendData(JSON.stringify({action: "save_wishlist", wish: wish}));
    });

    // Gestione tema
    if (tg.colorScheme === 'dark') {
        document.documentElement.style.setProperty('--card-bg', 'rgba(30, 30, 30, 0.9)');
        document.documentElement.style.setProperty('--text-color', '#fff');
    }
});
