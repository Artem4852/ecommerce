function newsletterSignUp() {
    email = document.getElementById("newsletterEmail").value;
    if (email == "" || !email.includes("@") || !email.includes(".")) {
        document.getElementById("newsletterButton").innerHTML = translations['invalidEmail'][lang];
        setTimeout(function () {
            document.getElementById("newsletterButton").innerHTML = translations['singUpNewsletter'][lang];
        }, 2000);
    }
    else {
        document.getElementById("newsletterButton").innerHTML = translations['singUpNewsletter'][lang];
        document.getElementById("newsletterEmail").value = "";
        fetch("/newsletterSignup", {
            method: "POST",
            body: JSON.stringify({ email: email }),
            headers: {
                "Content-Type": "application/json"
            }
        }).then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error("Request failed.");
        }).then(data => {
            if (data.success) {
                document.getElementById("newsletterButton").innerHTML = translations['thanksSubscribing'][lang];
                setTimeout(function () {
                    document.getElementById("newsletterButton").innerHTML = translations['singUpNewsletter'][lang];
                }, 2000);
            }
        })
    }
}