function newsletterSignUp() {
    email = document.getElementById("newsletterEmail").value;
    if (email == "" || !email.includes("@") || !email.includes(".")) {
        document.getElementById("newsletterButton").innerHTML = "Please enter a valid email address.";
        setTimeout(function () {
            document.getElementById("newsletterButton").innerHTML = "Sign me up";
        }, 2000);
    }
    else {
        document.getElementById("newsletterButton").innerHTML = "Sign me up";
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
                document.getElementById("newsletterButton").innerHTML = "Thanks for subscribing!";
                setTimeout(function () {
                    document.getElementById("newsletterButton").innerHTML = "Sign me up";
                }, 2000);
            }
        })
    }
}