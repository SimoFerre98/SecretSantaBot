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
