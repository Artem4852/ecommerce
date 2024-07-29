function toggleUserMenu() {
    var userMenu = document.getElementById("userNav");
    userMenu.classList.toggle("hidden");
}

addEventListener("click", function (event) {
    var userMenu = document.getElementById("userNav");
    if (event.target.parentElement.id !== "menuToggle" && !userMenu.classList.contains("hidden")) {
        userMenu.classList.add("hidden");
    }
});

function toggleMobileNav() {
    document.getElementById("mobileNav").classList.toggle("hidden");
}