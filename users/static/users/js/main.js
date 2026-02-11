const $ = document.querySelector.bind(document);
const $$ = document.querySelectorAll.bind(document);

// 1. ===== Chuyển Tab =======
function switchTab(tabName) {
  // Xóa class active
  $$(".tab-btn").forEach((btn) => btn.classList.remove("active"));
  $$(".form-container").forEach((form) => form.classList.remove("active"));

  // Thêm class active
  if (tabName === "login") {
    $("#tab-login").classList.add("active");
    $("#form-login").classList.add("active");
  } else {
    $("#tab-register").classList.add("active");
    $("#form-register").classList.add("active");
  }
}

// 2. ===== Validate Login =======
const loginForm = $("#login-form-element");

const errorMessageNullLogin = " Vui lòng nhập đầy đủ thông tin đăng nhập.";
const errorMessageUsername = " Tài khoản phải có ít nhất 8 ký tự.";
const errorMessageEmail = " Email không hợp lệ! Vui lòng kiểm tra lại.";

if (loginForm) {
  loginForm.addEventListener("submit", (e) => {
    const username = $("#input-login-username").value.trim();
    const password = $("#input-login-password").value.trim();

    if (!username || !password) {
      e.preventDefault(); // Ngăn form gửi đi
      Swal.fire("Chưa hợp lệ", errorMessageNullLogin, "warning");
    } else if (username.length < 8) {
      e.preventDefault();
      Swal.fire("Chưa hợp lệ", errorMessageUsername, "warning");
    } else if (password.length < 8) {
      e.preventDefault();
      Swal.fire("Chưa hợp lệ", "Mật khẩu phải có ít nhất 8 ký tự.", "warning");
    }
  });
}

// 3. ==== Validate Register ========
const registerForm = $("#register-form-element");
const errorRegisterMessage = $("#register-error-message");

// pattens for errors
const errorMessageNullRegister = " Vui lòng nhập đầy đủ thông tin đăng ký";
const errorMessagePassword = " Mật khẩu cần ít nhất 8 ký tự.";
const errorMessageConfirmPass = " Mật khẩu nhập lại không khớp!";

if (registerForm) {
  registerForm.addEventListener("submit", (e) => {
    // Lấy giá trị từ các input
    const fullName = $("#reg-fullname").value.trim();
    const email = $("#reg-email").value.trim();
    const password = $("#reg-password").value.trim();
    const confirmPass = $("#reg-confirm-password").value.trim();

    // Regex check email cơ bản
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    // 1. Check trống
    if (!fullName || !email || !password || !confirmPass) {
      e.preventDefault();
      Swal.fire("Chưa hợp lệ", errorMessageNullRegister, "warning");
    }
    // 2. Check định dạng email
    else if (!emailRegex.test(email)) {
      e.preventDefault();
      Swal.fire("Chưa hợp lệ", errorMessageEmail, "warning");
    }
    // 3. Check độ dài pass
    else if (password.length < 8) {
      e.preventDefault();
      Swal.fire("Chưa hợp lệ", errorMessagePassword, "warning");
    }
    // 4. Check khớp pass
    else if (password !== confirmPass) {
      e.preventDefault();
      Swal.fire("Chưa hợp lệ", errorMessageConfirmPass, "warning");
    }
  });
}
