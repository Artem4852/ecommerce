function submitMessage() {
    const name = document.getElementById('inputName').value;
    const email = document.getElementById('inputEmail').value;
    const subject = document.getElementById('inputSubject').value;
    const message = document.getElementById('inputMessage').value;

    const button = document.getElementById('buttonContact');

    if (name === '' || email === '' || subject === '' || message === '') {
        button.innerHTML = 'Please fill all fields';
        setTimeout(() => {
            button.innerHTML = 'Send Message';
        }, 2000);
    }

    fetch('/submitMessage', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ "name": name, "email": email, "subject": subject, "message": message })
    })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                button.innerHTML = 'An error occurred';
                setTimeout(() => {
                    button.innerHTML = 'Send Message';
                }, 2000);
            }
            else {
                button.innerHTML = 'Message sent';
                document.getElementById('inputName').value = '';
                document.getElementById('inputEmail').value = '';
                document.getElementById('inputSubject').value = '';
                document.getElementById('inputMessage').value = '';
                setTimeout(() => {
                    button.innerHTML = 'Send Message';
                }, 2000);
            }
        });
}