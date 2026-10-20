// main.js — students will add JavaScript here as features are built

// Close the post-registration card and reveal the (empty) sign-up form again.
document.querySelectorAll("[data-auth-notice-close]").forEach(function (button) {
    button.addEventListener("click", function () {
        button.closest("[data-auth-notice]").remove();
        var form = document.querySelector("[data-auth-form]");
        if (form) {
            form.hidden = false;
        }
    });
});

// Clear a server-side form error as soon as the user edits any field.
document.querySelectorAll(".auth-card form").forEach(function (form) {
    form.addEventListener("input", function () {
        var error = form.closest(".auth-card").querySelector(".auth-error");
        if (error) {
            error.remove();
        }
    });
});

// Show/hide the password typed in the field next to the toggle button.
document.querySelectorAll("[data-password-toggle]").forEach(function (button) {
    button.addEventListener("click", function () {
        var input = button.closest(".password-field").querySelector("input");
        var show = input.type === "password";
        input.type = show ? "text" : "password";
        button.setAttribute("aria-pressed", show ? "true" : "false");
        button.setAttribute("aria-label", show ? "Hide password" : "Show password");
    });
});

// Confirm-password must be typed by hand: block pasting and dropping text into it.
document.querySelectorAll("[data-no-paste]").forEach(function (input) {
    ["paste", "drop"].forEach(function (eventName) {
        input.addEventListener(eventName, function (event) {
            event.preventDefault();
        });
    });
});
