function newsletterSignUp() {
    email = document.getElementById("newsletter-email").value;
    if (email == "" || !email.includes("@") || !email.includes(".")) {
        document.getElementById("newsletter-button").innerHTML = "Please enter a valid email address.";
        setTimeout(function () {
            document.getElementById("newsletter-button").innerHTML = "Sign me up";
        }, 2000);
    }
    else {
        document.getElementById("newsletter-button").innerHTML = "Sign me up";
        document.getElementById("newsletter-email").value = "";
        fetch("/newsletter-signup", {
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
                document.getElementById("newsletter-button").innerHTML = "Thanks for subscribing!";
                setTimeout(function () {
                    document.getElementById("newsletter-button").innerHTML = "Sign me up";
                }, 2000);
            }
        })
    }
}