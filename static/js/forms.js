document.getElementById('input-phone-number').addEventListener('input', function (e) {
    let value = e.target.value.replace(/\D/g, '');
    let formattedValue = '';

    if (value.length > 0) {
        formattedValue += '+' + value.substring(0, 3);
    }
    if (value.length > 2) {
        formattedValue += ' (' + value.substring(3, 5);
    }
    if (value.length > 4) {
        formattedValue += ') ' + value.substring(5, 8);
    }
    if (value.length > 7) {
        formattedValue += ' ' + value.substring(8, 12);
    }

    e.target.value = formattedValue;
});

function validateForm() {
    const email = document.getElementById('input-email').value;
    const phone = document.getElementById('input-phone-number').value;
    const password = document.getElementById('input-password').value;
    const confirmPassword = document.getElementById('input-password-confirm').value;

    if (email == "" || !email.includes("@") || !email.includes(".")) {
        document.getElementById("signup-button").innerHTML = "Please enter a valid email address.";
        setTimeout(function () {
            document.getElementById("signup-button").innerHTML = "Sign up";
        }, 2000);
        return false;
    }
    else if (phone == "" || phone.length < 12) {
        document.getElementById("signup-button").innerHTML = "Please enter a valid phone number.";
        setTimeout(function () {
            document.getElementById("signup-button").innerHTML = "Sign up";
        }, 2000);
        return false;
    }
    else if (password == "" || password.length < 8) {
        document.getElementById("signup-button").innerHTML = "Password must be at least 8 characters long.";
        setTimeout(function () {
            document.getElementById("signup-button").innerHTML = "Sign up";
        }, 2000);
        return false;
    }
    else if (password != confirmPassword) {
        document.getElementById("signup-button").innerHTML = "Passwords do not match.";
        setTimeout(function () {
            document.getElementById("signup-button").innerHTML = "Sign up";
        }, 2000);
        return false;
    }
   return [true, email, phone, password];
}

function signup() {
    const output = validateForm();
    if (output[0]) {
        const hashedPassword = CryptoJS.SHA256(output[3]).toString();

        document.getElementById("signup-button").innerHTML = "Sign up";
        document.getElementById("input-email").value = "";
        document.getElementById("input-phone-number").value = "";
        document.getElementById("input-password").value = "";
        document.getElementById("input-password-confirm").value = "";

        const url = new URL(window.location.href);
        const next = url.searchParams.get("next");

        fetch("/signup", {
            method: "POST",
            body: JSON.stringify({
                email: output[1],
                phone: output[2],
                password: hashedPassword,
                next: next
            }),
            headers: {
                "Content-Type": "application/json"
            }
        }).then(response => {
            if (response.ok) {
                return response.json();
            }
        }).then(data => {
            if (data.success) {
                document.getElementById("signup-button").innerHTML = "Thanks for signing up!";
                setTimeout(function () {
                    location.href = "/login?next=" + next;
                }, 2000);
            }
            else {
                document.getElementById("signup-button").innerHTML = data.error;
                setTimeout(function () {
                    document.getElementById("signup-button").innerHTML = "Sign up";
                }, 5000);
            }
        })
    }
}

function login() {
    const email = document.getElementById('input-email').value;
    const password = document.getElementById('input-password').value;
    const hashedPassword = CryptoJS.SHA256(password).toString();

    const url = new URL(window.location.href);
    const next = url.searchParams.get("next");

    fetch("/login", {
        method: "POST",
        body: JSON.stringify({
            email: email,
            password: hashedPassword
        }),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(response => {
        if (response.ok) {
            return response.json();
        }
    }).then(data => {
        if (data.success) {
            if (next && next != "null") location.href = "/"+next;
            else location.href = "/";
        }
        else {
            document.getElementById("login-button").innerHTML = data.error;
            setTimeout(function () {
                document.getElementById("login-button").innerHTML = "Log in";
            }, 5000);
        }
    });
}