let sidebar = document.querySelector(".sidebar");
let closeBtn = document.querySelector("#btn");
closeBtn.addEventListener("click", () => {
    sidebar.classList.toggle("open");
    menuBtnChange();//calling the function(optional)
});

// following are the code to change sidebar button(optional)
function menuBtnChange() {
    if (sidebar.classList.contains("open")) {
        closeBtn.classList.replace("bx-menu", "bx-menu-alt-right");//replacing the icons class
    } else {
        closeBtn.classList.replace("bx-menu-alt-right", "bx-menu");//replacing the icons class
    }
}


// // Add an event listener to the button
// button.addEventListener("click", function () {
//     // Toggle the 'open' class on the sidebar
//     sidebar.classList.toggle("open");
//
//     // Log the current class list of the sidebar
//     console.log(sidebar.classList);
// });


// Function to show the SweetAlert confirmation dialog for deleting a harta
function deleteHarta(bil) {
    Swal.fire({
        title: 'Are you sure?',
        text: "You won't be able to revert this!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Setuju!'
    }).then((result) => {
        if (result.isConfirmed) {
            Swal.fire(
                'Deleted!',
                'Harta Berjaya Dipadam!',
                'success'
            ).then(() => {
                // If user confirms, trigger the form submission for deleting the harta
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '/delete_harta/' + bil;
                document.body.appendChild(form);
                form.submit();
            });
        }
    });
}


function deleteUser(bil) {
    Swal.fire({
        title: 'Are you sure?',
        text: "You won't be able to revert this!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Setuju!'
    }).then((result) => {
        if (result.isConfirmed) {
            Swal.fire(
                'Deleted!',
                'Pengguna Berjaya Dipadam!',
                'success'
            ).then(() => {
                // If user confirms, trigger the form submission for deleting the harta
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '/delete_user/' + bil;
                document.body.appendChild(form);
                form.submit();
            });
        }
    });
}


// Function to show draft data in the draft modal
function showDraftData() {
    $("#draft_jenis").text($("#draftForm select[name='jenis']").val());
    $("#draft_tahun").text($("#draftForm input[name='tahun']").val());
    $("#draft_no_fail").text($("#draftForm input[name='failNo']").val());
    $("#draft_namaPasangan").text($("#draftForm input[name='namaPasangan']").val());
    $("#draft_kategori").text($("#draftForm input[name='kategori']").val());
}

function showDraftAdminHartaData() {
    $("#draft_email").text($("#draftForm select[name='email']").val());
    $("#draft_jenis").text($("#draftForm select[name='jenis']").val());
    $("#draft_tahun").text($("#draftForm input[name='tahun']").val());
    $("#draft_no_fail").text($("#draftForm input[name='failNo']").val());
    $("#draft_namaPasangan").text($("#draftForm input[name='namaPasangan']").val());
    $("#draft_kategori").text($("#draftForm input[name='kategori']").val());
}

function showDraftDataPengguna() {
    $("#draft_email").text($("#draftForm input[name='email']").val());
    $("#draft_password").text($("#draftForm input[name='password']").val());
    $("#draft_name").text($("#draftForm input[name='name']").val());
    $("#draft_nric").text($("#draftForm input[name='nric']").val());
}

function updateViewFileLink() {
    var fileInput = document.getElementById('file');
    var viewFileLink = document.getElementById('draft_file');

    if (fileInput.files.length > 0) {
        // Get the selected file
        var selectedFile = fileInput.files[0];

        // Set the href attribute of the "View File" link to the file's object URL
        viewFileLink.href = URL.createObjectURL(selectedFile);

        // Open the link in a new tab/window when clicked
        viewFileLink.onclick = function () {
            window.open(viewFileLink.href, '_blank');
        };
    } else {
        // If no file is selected, reset the link
        viewFileLink.href = '#';
        viewFileLink.onclick = null;
    }
}

// Function to preview the file before submitting
function previewFile() {
    var fileInput = document.getElementById("file");
    var file = fileInput.files[0];

    if (file) {
        try {
            // Open a new window or tab to view the file
            window.open(URL.createObjectURL(file), '_blank');
        } catch (error) {
            console.error("Error previewing file:", error);
            alert("Error previewing file. Please try again.");
        }
    } else {
        alert("No file selected for preview.");
    }
}

// Function to save data to the database
function saveData() {
    try {
        // Perform the form submit here, e.g., using AJAX
        $("#draftForm").submit();
    } catch (error) {
        console.error("Error saving data:", error);
        alert("Error saving data. Please try again.");
    }
}

// Show draft data modal when preview button is clicked
$("#draftModal").on("show.bs.modal", function () {
    showDraftData();
});

// Clear draft data modal when closed
$("#draftModal").on("hidden.bs.modal", function () {
    $("#draft_tahun").text("");
    $("#draft_no_fail").text("");
    $("#draft_namaPasangan").text("");
    $("#draft_kategori").text("");
});


const logoutUrl = "{{ logout_url }}";

function showConfirmationDialog() {
    const swalWithBootstrapButtons = Swal.mixin({
        customClass: {
            confirmButton: "btn btn-success",
            cancelButton: "btn btn-danger"
        },
        buttonsStyling: false
    });

    swalWithBootstrapButtons.fire({
        title: "Log keluar?",
        text: "Anda akan di log keluar!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Log keluar!",
        cancelButtonText: "Batal!",
        reverseButtons: true
    }).then((result) => {
        if (result.isConfirmed) {
            showSuccessDialog();
            window.location.href = logoutUrl;
        } else if (result.dismiss === Swal.DismissReason.cancel) {
            showCancelledDialog();
        }
    });
}


function showSuccessDialog() {
    Swal.fire({
        title: "Log keluar!",
        text: "Anda telah log keluar.",
        icon: "success"
    });
}

function showCancelledDialog() {
    Swal.fire({
        title: "Batal",
        text: "",
        icon: "error"
    });
}

// Code for JavaScript to start a timer when the page loads or when the user logs in.
// Reset the timer whenever there is user activity.

var logoutTimer;

function resetLogoutTimer() {
    clearTimeout(logoutTimer);
    logoutTimer = setTimeout(logout, 15 * 60 * 1000);  // 15 minutes timeout (adjust as needed)
}

function logout() {
    // Implement logout logic here, e.g., redirect to logout route
    window.location.href = "/logout";
}

// Start the timer on page load
document.addEventListener("DOMContentLoaded", function () {
    resetLogoutTimer();
});

// Reset the timer on user activity
document.addEventListener("mousemove", resetLogoutTimer);
document.addEventListener("keydown", resetLogoutTimer);
// Add more events based on your application's interactivity


$(document).ready(function () {
    $("#selectEmail").change(function () {
        var email = $(this).val();
        $.ajax({
            url: '/get_username',
            data: {'email': email},
            type: 'POST',
            success: function (response) {
                $("#username").html(response);
            },
            error: function (error) {
                console.log(error);
            }
        });
    });
});


function password_show_hide() {
    var x = document.getElementById("password");
    var show_eye = document.getElementById("show_eye");
    var hide_eye = document.getElementById("hide_eye");
    hide_eye.classList.remove("d-none");
    if (x.type === "password") {
        x.type = "text";
        show_eye.style.display = "none";
        hide_eye.style.display = "block";
    } else {
        x.type = "password";
        show_eye.style.display = "block";
        hide_eye.style.display = "none";
    }
}