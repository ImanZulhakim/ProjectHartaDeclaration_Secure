// scripts.js
const sidebar = document.querySelector(".sidebar");
const closeBtn = document.querySelector("#btn");

closeBtn.addEventListener("click", () => {
  sidebar.classList.toggle("open");
  menuBtnChange();
});

function menuBtnChange() {
  if (sidebar.classList.contains("open")) {
    closeBtn.classList.replace("bx-menu", "bx-menu-alt-right");
  } else {
    closeBtn.classList.replace("bx-menu-alt-right", "bx-menu");
  }
}

function loadCustomersPage() {
  const homeSection = document.querySelector('.home-section');
  homeSection.innerHTML = ''; // Clear the existing content
  fetch('/customers') // Flask route for the customer page
    .then(response => response.text())
    .then(data => homeSection.innerHTML = data)
    .catch(error => console.log(error));
}
