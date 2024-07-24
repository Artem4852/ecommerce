let prev = null;
function phoneInput() {
    const phone = document.getElementById('inputPhoneNumber');

    if (prev && prev.length > phone.value.length) {
        phone.value = '';
        prev = null;
        return;
    }
    prev = phone.value;

    let value = phone.value.replace(/\D/g, '');
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

    phone.value = formattedValue;
    prev = phone.value;
}

function codeInput() {
    code = document.getElementById('inputCode');
    console.log(code);
    let valueCode = code.value.replace(/\D/g, '');
    let formattedValueCode = '';
    console.log(valueCode);

    if (valueCode.length > 0) {
        formattedValueCode = valueCode.substring(0, 3);
    }
    if (valueCode.length > 2) {
        formattedValueCode += '-' + valueCode.substring(3, 6);
    }

    code.value = formattedValueCode;
}

function validateForm() {
    const email = document.getElementById('inputEmail').value;
    const phone = document.getElementById('inputPhoneNumber').value;
    const password = document.getElementById('inputPassword').value;
    const confirmPassword = document.getElementById('inputPasswordConfirm').value;

    if (email == "" || !email.includes("@") || !email.includes(".")) {
        document.getElementById("signupButton").innerHTML = "Please enter a valid email address.";
        setTimeout(function () {
            document.getElementById("signupButton").innerHTML = "Sign up";
        }, 2000);
        return false;
    }
    else if (phone == "" || phone.length < 12) {
        document.getElementById("signupButton").innerHTML = "Please enter a valid phone number.";
        setTimeout(function () {
            document.getElementById("signupButton").innerHTML = "Sign up";
        }, 2000);
        return false;
    }
    else if (password == "" || password.length < 8) {
        document.getElementById("signupButton").innerHTML = "Password must be at least 8 characters long.";
        setTimeout(function () {
            document.getElementById("signupButton").innerHTML = "Sign up";
        }, 2000);
        return false;
    }
    else if (password != confirmPassword) {
        document.getElementById("signupButton").innerHTML = "Passwords do not match.";
        setTimeout(function () {
            document.getElementById("signupButton").innerHTML = "Sign up";
        }, 2000);
        return false;
    }
   return [true, email, phone, password];
}

function signup() {
    const output = validateForm();
    if (output[0]) {
        const hashedPassword = CryptoJS.SHA256(output[3]).toString();

        document.getElementById("signupButton").innerHTML = "Sign up";
        document.getElementById("inputEmail").value = "";
        document.getElementById("inputPhoneNumber").value = "";
        document.getElementById("inputPassword").value = "";
        document.getElementById("inputPasswordConfirm").value = "";

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
                document.getElementById("signupButton").innerHTML = "Thanks for signing up!";
                setTimeout(function () {
                    location.href = "/login?next=" + next;
                }, 2000);
            }
            else {
                document.getElementById("signupButton").innerHTML = data.error;
                setTimeout(function () {
                    document.getElementById("signupButton").innerHTML = "Sign up";
                }, 5000);
            }
        })
    }
}

function login() {
    const email = document.getElementById('inputEmail').value;
    const password = document.getElementById('inputPassword').value;
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
            document.getElementById("loginButton").innerHTML = data.error;
            setTimeout(function () {
                document.getElementById("loginButton").innerHTML = "Log in";
            }, 5000);
        }
    });
}

function sendResetCode() {
    const email = document.getElementById('inputEmail').value;

    fetch("/resetPassword", {
        method: "POST",
        body: JSON.stringify({
            email: email
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
            document.getElementById("resetButton").innerHTML = "Reset code sent!";
            setTimeout(function () {
                location.href = "/updatePassword?email=" + email;
            }, 2000);
        }
        else {
            document.getElementById("resetButton").innerHTML = data.error;
            setTimeout(function () {
                document.getElementById("resetButton").innerHTML = "Send reset code";
            }, 5000);
        }
    });
}

function validateReset() {
    const code = document.getElementById('inputCode').value;
    const password = document.getElementById('inputPassword').value;
    const confirmPassword = document.getElementById('inputPasswordConfirm').value;

    if (code == "" || code.length < 6) {
        document.getElementById("resetButton").innerHTML = "Please enter a valid reset code.";
        setTimeout(function () {
            document.getElementById("resetButton").innerHTML = "Update password";
        }, 2000);
        return false;
    }
    else if (password == "" || password.length < 8) {
        document.getElementById("resetButton").innerHTML = "Password must be at least 8 characters long.";
        setTimeout(function () {
            document.getElementById("resetButton").innerHTML = "Update password";
        }, 2000);
        return false;
    }
    else if (password != confirmPassword) {
        document.getElementById("resetButton").innerHTML = "Passwords do not match.";
        setTimeout(function () {
            document.getElementById("resetButton").innerHTML = "Update password";
        }, 2000);
        return false;
    }
    return true;
}

function updatePassword() {
    if (!validateReset()) return;
    url = new URL(window.location.href);
    const email = url.searchParams.get("email");
    const code = document.getElementById('inputCode').value;
    const password = document.getElementById('inputPassword').value;
    const confirmPassword = document.getElementById('inputPasswordConfirm').value;
    if (password != confirmPassword) {
        document.getElementById("resetButton").innerHTML = "Passwords do not match.";
        setTimeout(function () {
            document.getElementById("resetButton").innerHTML = "Update password";
        }, 2000);
        return;
    }

    const hashedPassword = CryptoJS.SHA256(password).toString();

    fetch("/updatePassword", {
        method: "POST",
        body: JSON.stringify({
            email: email,
            code: code,
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
            document.getElementById("resetButton").innerHTML = "Password updated!";
            setTimeout(function () {
                location.href = "/login";
            }, 2000);
        }
        else {
            document.getElementById("resetButton").innerHTML = data.error;
            setTimeout(function () {
                document.getElementById("resetButton").innerHTML = "Update password";
            }, 5000);
        }
    });
}