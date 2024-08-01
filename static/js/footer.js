function changeLanguage(lang) {
    fetch('/changeLanguage', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ lang: lang })
    })
    .then(res => {
        if (res.ok) {
            window.location.reload();
        }
    });
}