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

if (loginForm) {
  loginForm.addEventListener("submit", (e) => {
    const username = $("#input-login-username").value.trim();
    const password = $("#input-login-password").value.trim();
    let hasError = false;

    if (!username || !password) {
      alert("Vui lòng nhập đầy đủ thông tin đăng nhập");
      hasError = true;
    } else if (username.length < 8) {
      alert("Tài khoản phải có ít nhất 8 ký tự");
      hasError = true;
    } else if (password.length < 8) {
      alert("Mật khẩu phải có ít nhất 8 ký tự");
      hasError = true;
    }

    if (hasError) e.preventDefault();
  });
}

// 3. ==== Validate Register ========
const registerForm = $("#register-form-element");

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
      alert("Vui lòng điền đầy đủ thông tin đăng ký!");
      hasError = true;
    }
    // 2. Check định dạng email
    else if (!emailRegex.test(email)) {
      alert("Email không hợp lệ! Vui lòng kiểm tra lại.");
      hasError = true;
    }
    // 3. Check độ dài pass
    else if (password.length < 8) {
      alert("Mật khẩu đăng ký phải có ít nhất 8 ký tự!");
      hasError = true;
    }
    // 4. Check khớp pass
    else if (password !== confirmPass) {
      alert("Mật khẩu nhập lại không khớp!");
      hasError = true;
    }

    if (hasError) e.preventDefault();
  });
}
