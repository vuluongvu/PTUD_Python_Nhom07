// @ts-nocheck
/*
  DJANGO STATIC FILE: main.js
  Path: static/js/main.js
*/
document.addEventListener("DOMContentLoaded", () => {
  let currentSlide = 0;
  const slides = document.querySelectorAll(".slide");

  if (slides.length > 0) {
    // @ts-ignore
    function moveSlide(n) {
      slides[currentSlide].classList.remove("active");
      currentSlide = (currentSlide + n + slides.length) % slides.length;
      slides[currentSlide].classList.add("active");
    }

    // Tự động chuyển slide sau 5 giây
    setInterval(() => moveSlide(1), 5000);
  }

  // --- SEARCH AUTOCOMPLETE ---
  const searchInputs = document.querySelectorAll(".search-box input");
  const sampleData = [
    "MacBook Air M1",
    "MacBook Pro M2",
    "Laptop Gaming Asus",
    "Acer Nitro 5",
    "Dell XPS 13",
    "LG Gram 2023",
    "iPhone 15 Pro Max",
    "Samsung Galaxy S24",
    "Chuột Logitech G102",
    "Bàn phím cơ",
    "Tai nghe Gaming",
    "Màn hình Dell Ultrasharp",
    "RAM 8GB DDR4",
    "SSD 512GB NVMe",
    "VGA RTX 3060",
    "Mainboard B660",
  ];

  searchInputs.forEach((input) => {
    // Tạo box gợi ý nếu chưa có
    // @ts-ignore
    let suggestionBox = input.parentElement.querySelector(
      ".search-suggestions",
    );
    if (!suggestionBox) {
      suggestionBox = document.createElement("div");
      suggestionBox.className = "search-suggestions";
      // @ts-ignore
      input.parentElement.appendChild(suggestionBox);
    }

    // Xử lý sự kiện nhập liệu
    input.addEventListener("input", (e) => {
      // @ts-ignore
      const value = e.target.value.toLowerCase().trim();
      suggestionBox.innerHTML = "";

      if (value.length > 0) {
        const filtered = sampleData.filter((item) =>
          item.toLowerCase().includes(value),
        );

        if (filtered.length > 0) {
          filtered.forEach((item) => {
            const div = document.createElement("div");
            div.className = "suggestion-item";
            div.innerHTML = `<i class="fa-solid fa-magnifying-glass"></i> ${item}`;
            div.addEventListener("click", () => {
              // @ts-ignore
              input.value = item;
              suggestionBox.classList.remove("show");
            });
            suggestionBox.appendChild(div);
          });
          suggestionBox.classList.add("show");
        } else {
          suggestionBox.classList.remove("show");
        }
      } else {
        suggestionBox.classList.remove("show");
      }
    });

    // Ẩn khi click ra ngoài
    document.addEventListener("click", (e) => {
      // @ts-ignore
      if (!input.contains(e.target) && !suggestionBox.contains(e.target)) {
        suggestionBox.classList.remove("show");
      }
    });

    // Hiện lại khi focus nếu có text
    input.addEventListener("focus", () => {
      // @ts-ignore
      if (input.value.trim().length > 0) {
        input.dispatchEvent(new Event("input"));
      }
    });
  });

  // --- PRODUCT DETAIL LOGIC ---
  // 1. Chọn Option (Màu sắc / Cấu hình)
  const optBtns = document.querySelectorAll(".opt-btn");
  optBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      // @ts-ignore
      this.parentElement
        .querySelectorAll(".opt-btn")
        // @ts-ignore
        .forEach((b) => b.classList.remove("active"));
      // @ts-ignore
      this.classList.add("active");
    });
  });

  // 2. Đổi ảnh (Global function để dùng trong onclick HTML)
  // @ts-ignore
  window.changeImage = function (element, src) {
    // @ts-ignore
    document.getElementById("mainImage").src = src;
    document
      .querySelectorAll(".thumb-item")
      .forEach((item) => item.classList.remove("active"));
    element.classList.add("active");
  };

  // 3. Đánh giá sao (Review Stars)
  const starInputs = document.querySelectorAll(".star-input i");
  starInputs.forEach((star, index) => {
    star.addEventListener("click", () => {
      // Reset tất cả
      starInputs.forEach((s) => {
        s.classList.remove("selected");
        s.classList.replace("fa-solid", "fa-regular");
      });
      // Active các sao từ đầu đến index được chọn
      for (let i = 0; i <= index; i++) {
        starInputs[i].classList.add("selected");
        starInputs[i].classList.replace("fa-regular", "fa-solid");
      }
    });
  });

  // --- MOBILE FILTER SIDEBAR ---
  const filterBtn = document.querySelector(".mobile-filter-btn");
  const sidebar = document.querySelector(".sidebar");
  const overlay = document.querySelector(".sidebar-overlay");
  const closeSidebarBtn = document.querySelector(".sidebar-close");

  if (filterBtn && sidebar && overlay && closeSidebarBtn) {
    function toggleSidebar() {
      // @ts-ignore
      sidebar.classList.toggle("open");
      // @ts-ignore
      overlay.classList.toggle("active");
      // @ts-ignore
      document.body.style.overflow = sidebar.classList.contains("open")
        ? "hidden"
        : "";
    }

    filterBtn.addEventListener("click", toggleSidebar);
    closeSidebarBtn.addEventListener("click", toggleSidebar);
    overlay.addEventListener("click", toggleSidebar);
  }

  // --- MOBILE MAIN MENU ---
  const btnMobileMenu = document.querySelector(".btn-mobile-menu");
  const mobileMenu = document.querySelector(".mobile-menu");
  const menuOverlay = document.querySelector(".mobile-menu-overlay");
  const closeMenuBtn = document.querySelector(".mobile-menu-close");

  if (btnMobileMenu && mobileMenu && menuOverlay && closeMenuBtn) {
    function toggleMenu() {
      // @ts-ignore
      mobileMenu.classList.toggle("open");
      // @ts-ignore
      menuOverlay.classList.toggle("active");
      // @ts-ignore
      document.body.style.overflow = mobileMenu.classList.contains("open")
        ? "hidden"
        : "";
    }

    btnMobileMenu.addEventListener("click", toggleMenu);
    closeMenuBtn.addEventListener("click", toggleMenu);
    menuOverlay.addEventListener("click", toggleMenu);
  }

  // --- BACK TO TOP ---
  const backToTopBtn = document.getElementById("backToTop");

  if (backToTopBtn) {
    window.addEventListener("scroll", () => {
      if (window.scrollY > 300) {
        backToTopBtn.classList.add("show");
      } else {
        backToTopBtn.classList.remove("show");
      }
    });

    backToTopBtn.addEventListener("click", () => {
      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    });
  }

  // --- CHECKOUT PAYMENT SELECTION ---
  const paymentOptions = document.querySelectorAll(".payment-option");
  if (paymentOptions.length > 0) {
    paymentOptions.forEach((option) => {
      option.addEventListener("click", () => {
        paymentOptions.forEach((opt) => opt.classList.remove("active"));
        option.classList.add("active");
        const radio = option.querySelector("input[type='radio']");
        if (radio) radio.checked = true;
      });
    });
  }
});
