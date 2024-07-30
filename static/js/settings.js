const inputs = document.querySelectorAll('input');
const selects = document.querySelectorAll('select');

inputs.forEach(input => {
    input.addEventListener('blur', function (event) {
        const value = event.target.value;
        let name = event.target.name;
        name = name.replace(/-./g, match => match.charAt(1).toUpperCase());
        const data = { [name]: value };

        fetch('/updateSettings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
    });
});

selects.forEach(select => {
    select.addEventListener('change', function (event) {
        const value = event.target.value;
        let name = event.target.name;
        name = name.replace(/-./g, match => match.charAt(1).toUpperCase());
        const data = { [name]: value };

        fetch('/updateSettings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
    });
});

function check(id) {
    document.getElementById(id).classList.toggle('disabled');
    const checked = !document.getElementById(id).classList.contains('disabled');
    const name = id.replace('inputCheck', '').replace(/-./g, match => match.charAt(1).toUpperCase());
    const data = { [name]: checked };

    fetch('/updateSettings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
}