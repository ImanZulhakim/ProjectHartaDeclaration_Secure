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


// Function to show the SweetAlert confirmation dialog for deleting a harta
function deleteHarta(bil) {
    Swal.fire({
        title: 'Adakah anda pasti?',
        text: "Anda tidak akan dapat mengembalikan info harta pengguna!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Setuju!'
    }).then((result) => {
        if (result.isConfirmed) {
            Swal.fire(
                'Dipadam!',
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
        title: 'Adakah anda pasti?',
        text: "Anda tidak akan dapat mengembalikan info pengguna!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Setuju!'
    }).then((result) => {
        if (result.isConfirmed) {
            Swal.fire(
                'Dipadam!',
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
    if (validateRequiredFields()) {
        showDraftData();
        showDraftAdminHartaData();
        showDraftDataPengguna();

    } else {
        // Use SweetAlert instead of the normal alert
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Sila isi semua info yang diperlukan sebelum melihatnya.',
        });

        // Prevent the modal from being shown
        $(this).modal("hide");
    }
});

// Clear draft data modal when closed
$("#draftModal").on("hidden.bs.modal", function () {
    $("#draft_tahun").text("");
    $("#draft_no_fail").text("");
    $("#draft_namaPasangan").text("");
    $("#draft_kategori").text("");
});

// Function to validate required fields
function validateRequiredFields() {
    var requiredFields = $("#draftForm [required]");
    var emptyFields = [];

    requiredFields.each(function () {
        if ($(this).val().trim() === "") {
            emptyFields.push($(this).attr("name"));
        }
    });

    if (emptyFields.length > 0) {
        return false;
    } else {
        return true;
    }
}


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


function validateAndSubmit(rowId) {
    var tahun = $("#modaledit" + rowId + " input[name='tahun']").val();
    var failNo = $("#modaledit" + rowId + " input[name='failNo']").val();
    var namaPasangan = $("#modaledit" + rowId + " input[name='namaPasangan']").val();
    var jenis = $("#modaledit" + rowId + " select[name='jenis']").val();
    var kategori = $("#modaledit" + rowId + " input[name='kategori']:checked").val();
    var file = $("#modaledit" + rowId + " input[name='file']").val();

    if (tahun.trim() === "" || failNo.trim() === "" || namaPasangan.trim() === "" || jenis === undefined || kategori === undefined) {
        // Use SweetAlert to display an error message
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Sila isi semua info sebelum anda kemas kini!',
        });
    } else {

        if (!validateYearUpdate(rowId)) {
            return;
        }
        // If all required fields are filled, submit the form
        $("#modaledit" + rowId + " form").submit();
    }
}

function validateAndSubmitUser(rowId) {
    var email = $("#modaledit" + rowId + " input[name='email']").val();
    var password = $("#modaledit" + rowId + " input[name='password']").val();
    var name = $("#modaledit" + rowId + " input[name='name']").val();
    var nric = $("#modaledit" + rowId + " input[name='nric']").val();

    if (email.trim() === "" || password.trim() === "" || name.trim() === "" || nric.trim() === "") {
        // Use SweetAlert to display an error message
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Sila isi semua info sebelum anda kemas kini!',
        });
    } else {
        // If all required fields are filled, submit the form
        $("#modaledit" + rowId + " form").submit();
    }
}

function validateAndPreview() {
    var tahun = $("#draftForm input[name='tahun']").val();
    var failNo = $("#draftForm input[name='failNo']").val();
    var namaPasangan = $("#draftForm input[name='namaPasangan']").val();
    var jenis = $("#draftForm select[name='jenis']").val();
    var kategori = $("#draftForm input[name='kategori']:checked").val();
    var file = $("#draftForm input[name='file']").val();

    if (tahun.trim() === "" || failNo.trim() === "" || namaPasangan.trim() === "" || jenis === null || kategori === undefined || file === "") {
        // Use SweetAlert to display an error message
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Sila isi semua info yang diperlukan sebelum melihatnya.',
        });
    } else {
        if (!validateYear()) {
            return;
        }
        // If all required fields are filled, proceed with preview
        showDraftData();
        $("#draftModal").modal("show");
    }
}

function validateAndPreviewAdmin() {
    var email = $("#draftForm select[name='email']").val();
    var tahun = $("#draftForm input[name='tahun']").val();
    var failNo = $("#draftForm input[name='failNo']").val();
    var namaPasangan = $("#draftForm input[name='namaPasangan']").val();
    var jenis = $("#draftForm select[name='jenis']").val();
    var kategori = $("#draftForm input[name='kategori']:checked").val();
    var file = $("#draftForm input[name='file']").val();

    if (email === null || tahun.trim() === "" || failNo.trim() === "" || namaPasangan.trim() === "" || jenis === null || kategori === undefined || file === "") {
        // Use SweetAlert to display an error message
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Sila isi semua info yang diperlukan sebelum melihatnya.',
        });
    } else {
        if (!validateYear()) {
            return;
        }
        // If all required fields are filled, proceed with preview
        showDraftAdminHartaData();
        $("#draftModal").modal("show");
    }
}

function validateAndPreviewUser() {
    var email = $("#draftForm select[name='email']").val();
    var password = $("#draftForm input[name='password']").val();
    var name = $("#draftForm input[name='name']").val();
    var nric = $("#draftForm input[name='nric']").val();

    if (email === null || password.trim() === "" || name.trim() === "" || nric.trim() === "") {
        // Use SweetAlert to display an error message
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Sila isi semua info yang diperlukan sebelum melihatnya.',
        });
    } else {
        // If all required fields are filled, proceed with preview
        showDraftDataPengguna();
        $("#draftModal").modal("show");
    }
}

function validateYear() {
    var yearInput = $("#draftForm input[name='tahun']").val();
    var isValidYear = /^\d{4}$/.test(yearInput);

    if (!isValidYear) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Sila masukkan angka 4-digit untuk tahun (e.g. 2024).',
        });
        return false;
    }

    return true;
}

function validateYearUpdate(rowId) {
    var yearInput = $("#modaledit" + rowId + " input[name='tahun']").val();
    var isValidYear = /^\d{4}$/.test(yearInput);

    if (!isValidYear) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Sila masukkan angka 4-digit untuk tahun (e.g. 2024).',
        });
        return false;
    }

    return true;
}
