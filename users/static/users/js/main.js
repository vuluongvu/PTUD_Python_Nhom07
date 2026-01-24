// Logic chuyển đổi tab (Cần để ở global scope vì được gọi từ onclick trong HTML)
function switchTab(tabName) {
  // Xóa class active ở tất cả tab và form
  document
    .querySelectorAll(".tab-btn")
    .forEach((btn) => btn.classList.remove("active"));
  document
    .querySelectorAll(".form-container")
    .forEach((form) => form.classList.remove("active"));

  // Thêm class active vào tab và form được chọn
  if (tabName === "login") {
    document.querySelector(".tab-btn:nth-child(1)").classList.add("active");
    document.getElementById("form-login").classList.add("active");
  } else {
    document.querySelector(".tab-btn:nth-child(2)").classList.add("active");
    document.getElementById("form-register").classList.add("active");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  // Back to Top Logic
  const backToTopBtn = document.getElementById("backToTop");
  if (backToTopBtn) {
    window.addEventListener("scroll", () => {
      if (window.scrollY > 100) {
        backToTopBtn.classList.add("show");
      } else {
        backToTopBtn.classList.remove("show");
      }
    });
    backToTopBtn.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
});

// Form Validation Logic
const loginInputUsername = document.querySelector("#input-login-username");
const loginInputPassword = document.querySelector("#input-login-password");
const loginForm = document.querySelector("#login-form-element");

//  Kiểm tra xem form có tồn tại không trước khi gắn sự kiện
if (loginForm) {
  loginForm.addEventListener("submit", (e) => {
    e.preventDefault();

    //  Lấy giá trị và TỰ ĐỘNG XÓA sạch mọi khoảng trắng
    const finalUsername = loginInputUsername.value.replace(/\s/g, "");
    const finalPassword = loginInputPassword.value.replace(/\s/g, "");

    //  Kiểm tra null hay ko (sau khi đã xóa khoảng trắng)
    if (!finalUsername || !finalPassword) {
      alert("Vui lòng nhập đầy đủ thông tin đăng nhập");
      return;
    }

    // Kiểm tra valid length
    if (finalUsername.length < 8) {
      alert("Tài khoản phải có ít nhất 8 ký tự");
      return;
    }

    if (finalPassword.length < 8) {
      alert("Mật khẩu phải có ít nhất 8 ký tự");
      return;
    }

    // if Thành công
    alert("Đăng nhập thành công");

    //send đến server check tiếp
  });
}
