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
const errorLoginMessage = $("#login-error-message");

// pattens for errors

function xmarkAndErrorMessage(message) {
  return `<i class="fa-solid fa-xmark"><span>${message}</span></i>`;
}

const errorMessageNullLogin = " Vui lòng nhập đầy đủ thông tin đăng nhập.";
const errorMessageUsername = " Tài khoản phải có ít nhất 8 ký tự.";
const errorMessagePassword = " Mật khẩu phải có ít nhất 8 ký tự.";
const errorMessageEmail = " Email không hợp lệ! Vui lòng kiểm tra lại.";

if (loginForm) {
  loginForm.addEventListener("submit", (e) => {
    const username = $("#input-login-username").value.trim();
    const password = $("#input-login-password").value.trim();
    let hasError = false;

    if (!username || !password) {
      errorLoginMessage.innerHTML = xmarkAndErrorMessage(errorMessageNullLogin);
      errorLoginMessage.classList.add("error-message");
      hasError = true;
    } else if (username.length < 8) {
      errorLoginMessage.innerHTML = xmarkAndErrorMessage(errorMessageUsername);
      errorLoginMessage.classList.add("error-message");
      hasError = true;
    } else if (password.length < 8) {
      errorLoginMessage.innerHTML = xmarkAndErrorMessage(errorMessagePassword);
      errorLoginMessage.classList.add("error-message");
      hasError = true;
    }

    if (hasError) e.preventDefault();
  });
}

// 3. ==== Validate Register ========
const registerForm = $("#register-form-element");
const errorRegisterMessage = $("#register-error-message");

// pattens for errors
const errorMessageNullRegister = " Vui lòng nhập đầy đủ thông tin đăng ký";
const errorMessageConfirmPass = " Mật khẩu nhập lại không khớp!";

if (registerForm) {
  registerForm.addEventListener("submit", (e) => {
    // Lấy giá trị từ các input
    const fullName = $("#reg-fullname").value.trim();
    const email = $("#reg-email").value.trim();
    const password = $("#reg-password").value.trim();
    const confirmPass = $("#reg-confirm-password").value.trim();

    let hasError = false;
    // Regex check email cơ bản
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    // 1. Check trống
    if (!fullName || !email || !password || !confirmPass) {
      if (errorRegisterMessage) {
        errorRegisterMessage.innerHTML = xmarkAndErrorMessage(
          errorMessageNullRegister,
        );
        errorRegisterMessage.classList.add("error-message");
      } else {
        alert(errorMessageNullRegister);
      }
      hasError = true;
    }
    // 2. Check định dạng email
    else if (!emailRegex.test(email)) {
      if (errorRegisterMessage) {
        errorRegisterMessage.innerHTML =
          xmarkAndErrorMessage(errorMessageEmail);
        errorRegisterMessage.classList.add("error-message");
      } else {
        alert(errorMessageEmail);
      }
      hasError = true;
    }
    // 3. Check độ dài pass
    else if (password.length < 8) {
      if (errorRegisterMessage) {
        errorRegisterMessage.innerHTML =
          xmarkAndErrorMessage(errorMessagePassword);
        errorRegisterMessage.classList.add("error-message");
      } else {
        alert(errorMessagePassword);
      }
      hasError = true;
    }
    // 4. Check khớp pass
    else if (password !== confirmPass) {
      if (errorRegisterMessage) {
        errorRegisterMessage.innerHTML = xmarkAndErrorMessage(
          errorMessageConfirmPass,
        );
        errorRegisterMessage.classList.add("error-message");
      } else {
        alert(errorMessageConfirmPass);
      }
      hasError = true;
    }
    if (hasError) e.preventDefault();
  });
}
