document.addEventListener("DOMContentLoaded", function () {
    const slides = document.querySelectorAll(".slide");
    let index = 0;

    if (slides.length === 0) return;

    setInterval(() => {
        slides[index].classList.remove("active");
        index = (index + 1) % slides.length;
        slides[index].classList.add("active");
    }, 4000);
});

document.addEventListener("DOMContentLoaded", function() {

    const menu = document.querySelector(".nav-left");
    const closeBtn = document.querySelector(".close-btn");
    const sidebar = document.getElementById("sidebar");

    if (menu && sidebar) {
        menu.addEventListener("click", function() {
            sidebar.classList.add("active");
        });
    }

    if (closeBtn && sidebar) {
        closeBtn.addEventListener("click", function() {
            sidebar.classList.remove("active");
        });
    }

});