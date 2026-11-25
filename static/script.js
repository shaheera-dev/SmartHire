

const searchInput = document.getElementById("searchInput");
const statusFilter = document.getElementById("statusFilter");
const locationFilter = document.getElementById("locationFilter");

function filterApplications() {

    if (!searchInput || !statusFilter || !locationFilter) {
        return;
    }

    const search = searchInput.value.toLowerCase();
    const status = statusFilter.value.toLowerCase();
    const location = locationFilter.value.toLowerCase();

    document.querySelectorAll(".applications tbody tr").forEach(row => {

        const cells = row.querySelectorAll("td");

        if (cells.length < 6) return;

        const company = cells[0].textContent.toLowerCase();
        const position = cells[1].textContent.toLowerCase();
        const jobLocation = cells[2].textContent.toLowerCase();
        const jobStatus = cells[4].textContent.toLowerCase();

        const matches =
            (company.includes(search) || position.includes(search)) &&
            jobStatus.includes(status) &&
            jobLocation.includes(location);

        row.style.display = matches ? "" : "none";
    });
}

function resetFilters() {

    if (!searchInput || !statusFilter || !locationFilter) {
        return;
    }

    searchInput.value = "";
    statusFilter.value = "";
    locationFilter.value = "";

    filterApplications();
}

if (searchInput) {
    searchInput.addEventListener("input", filterApplications);
}

if (statusFilter) {
    statusFilter.addEventListener("change", filterApplications);
}

if (locationFilter) {
    locationFilter.addEventListener("input", filterApplications);
}



// LOGIN PASSWORD SHOW / HIDE

function toggleLoginPassword() {

    const passwordInput =
        document.getElementById("login-password");

    const toggleButton =
        document.querySelector(".login-toggle-password");

    if (!passwordInput || !toggleButton) {
        return;
    }

    if (passwordInput.type === "password") {

        passwordInput.type = "text";
        toggleButton.textContent = "🙈";
        toggleButton.setAttribute("aria-label", "Hide password");
        toggleButton.setAttribute("aria-pressed", "true");

    } else {

        passwordInput.type = "password";
        toggleButton.textContent = "👁";
        toggleButton.setAttribute("aria-label", "Show password");
        toggleButton.setAttribute("aria-pressed", "false");

    }
}



// REGISTER PASSWORD SHOW / HIDE
function toggleRegisterPassword() {

    const passwordInput =
        document.getElementById("register-password");

    const toggleButton =
        document.querySelector(
            "#register-password + .login-toggle-password"
        );

    if (!passwordInput || !toggleButton) {
        return;
    }

    if (passwordInput.type === "password") {

        passwordInput.type = "text";
        toggleButton.textContent = "🙈";
        toggleButton.setAttribute("aria-label", "Hide password");
        toggleButton.setAttribute("aria-pressed", "true");

    } else {

        passwordInput.type = "password";
        toggleButton.textContent = "👁";
        toggleButton.setAttribute("aria-label", "Show password");
        toggleButton.setAttribute("aria-pressed", "false");

    }
}
