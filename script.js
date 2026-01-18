(() => {
  const navToggle = document.getElementById("nav-toggle");
  const navMenu = document.getElementById("nav-menu");
  const header = document.getElementById("header");
  const scrollProgress = document.getElementById("scroll-progress");
  const themeToggle = document.getElementById("theme-toggle");
  const prefersReducedMotionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
  let prefersReducedMotion = prefersReducedMotionQuery.matches;
  prefersReducedMotionQuery.addEventListener?.("change", (e) => {
    prefersReducedMotion = e.matches;
  });

  // --- Theme (dark/light) ---
  const getTheme = () => document.documentElement.getAttribute("data-theme") || "dark";

  const updateThemeIcon = (theme) => {
    if (!themeToggle) return;
    const icon = themeToggle.querySelector("i");
    if (!icon) return;

    // Dark theme -> show sun (switch to light)
    // Light theme -> show moon (switch to dark)
    if (theme === "dark") {
      icon.classList.remove("fa-moon");
      icon.classList.add("fa-sun");
      themeToggle.setAttribute("aria-label", "Switch to light mode");
      themeToggle.title = "Switch to light mode";
    } else {
      icon.classList.remove("fa-sun");
      icon.classList.add("fa-moon");
      themeToggle.setAttribute("aria-label", "Switch to dark mode");
      themeToggle.title = "Switch to dark mode";
    }
  };

  const setTheme = (theme) => {
    document.documentElement.setAttribute("data-theme", theme);
    try { localStorage.setItem("theme", theme); } catch (e) {}
    updateThemeIcon(theme);
  };

  updateThemeIcon(getTheme());

  themeToggle?.addEventListener("click", () => {
    const current = getTheme();
    setTheme(current === "dark" ? "light" : "dark");
  });

  // --- Mobile nav toggle ---
  navToggle.addEventListener("click", () => {
    const isOpen = navMenu.classList.toggle("open");
    navToggle.setAttribute("aria-expanded", String(isOpen));

    const icon = navToggle.querySelector("i");
    if (isOpen) {
      icon.classList.remove("fa-bars");
      icon.classList.add("fa-xmark");
    } else {
      icon.classList.remove("fa-xmark");
      icon.classList.add("fa-bars");
    }
  });

  // Close menu on link click (mobile)
  navMenu.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      if (!navMenu.classList.contains("open")) return;
      navMenu.classList.remove("open");
      navToggle.setAttribute("aria-expanded", "false");

      const icon = navToggle.querySelector("i");
      icon.classList.remove("fa-xmark");
      icon.classList.add("fa-bars");
    });
  });

  // Close menu on Escape
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    if (!navMenu.classList.contains("open")) return;
    navMenu.classList.remove("open");
    navToggle.setAttribute("aria-expanded", "false");
    const icon = navToggle.querySelector("i");
    icon.classList.remove("fa-xmark");
    icon.classList.add("fa-bars");
  });

  // --- Reveal on scroll ---
  const revealElements = document.querySelectorAll(".reveal");
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );
  revealElements.forEach((el) => observer.observe(el));

  // --- Scroll progress + sticky header + parallax + active nav ---
  const sections = document.querySelectorAll("main section[id]");
  const navLinks = document.querySelectorAll("#nav-menu a");

  const updateScrollState = () => {
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    scrollProgress.style.width = progress + "%";

    if (scrollTop > 10) header.classList.add("scrolled");
    else header.classList.remove("scrolled");

    // Parallax blobs (skip when reduced motion is preferred)
    if (!prefersReducedMotion) {
      const ratio = docHeight > 0 ? scrollTop / docHeight : 0;
      const x1 = (ratio - 0.5) * 40;
      const y1 = ratio * 60;
      const x2 = (0.5 - ratio) * 40;
      const y2 = -ratio * 60;

      document.documentElement.style.setProperty("--blob1-x", x1.toFixed(1) + "px");
      document.documentElement.style.setProperty("--blob1-y", y1.toFixed(1) + "px");
      document.documentElement.style.setProperty("--blob2-x", x2.toFixed(1) + "px");
      document.documentElement.style.setProperty("--blob2-y", y2.toFixed(1) + "px");
    } else {
      document.documentElement.style.setProperty("--blob1-x", "0px");
      document.documentElement.style.setProperty("--blob1-y", "0px");
      document.documentElement.style.setProperty("--blob2-x", "0px");
      document.documentElement.style.setProperty("--blob2-y", "0px");
    }

    // Active nav + aria-current
    let currentId = "";
    sections.forEach((section) => {
      const rect = section.getBoundingClientRect();
      const offsetTop = rect.top + window.scrollY;
      if (scrollTop >= offsetTop - 140 && scrollTop < offsetTop + section.offsetHeight - 140) {
        currentId = section.id;
      }
    });

    navLinks.forEach((link) => {
      const hrefId = link.getAttribute("href").replace("#", "");
      const isActive = hrefId === currentId;
      link.classList.toggle("active", isActive);
      if (isActive) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
  };

  window.addEventListener("scroll", updateScrollState);
  window.addEventListener("resize", updateScrollState);
  updateScrollState();

  // --- Contact form -> mailto handler ---
  const contactForm = document.getElementById("contact-form");
  const contactStatus = document.getElementById("contact-status");
  const setStatus = (msg, type) => {
    if (!contactStatus) return;
    contactStatus.textContent = msg;
    contactStatus.className = `form-status ${type || ""}`.trim();
  };

  contactForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    setStatus("Sending...", "");

    const nameRaw = contactForm.name.value.trim();
    const emailRaw = contactForm.email.value.trim();
    const messageRaw = contactForm.message.value.trim();

    const payload = { name: nameRaw, email: emailRaw, message: messageRaw };
    const endpoint = (contactForm.dataset.endpoint || "").trim();

    if (endpoint) {
      try {
        const res = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify(payload),
        });
        if (!res.ok) throw new Error("Network response was not ok");
        contactForm.reset();
        setStatus("Thanks! I received your message and will reply soon.", "success");
        return;
      } catch (err) {
        setStatus("Couldn't send via form. Opening your mail app instead…", "error");
      }
    }

    const name = encodeURIComponent(nameRaw);
    const email = encodeURIComponent(emailRaw);
    const message = encodeURIComponent(messageRaw);
    const subject = `Portfolio contact from ${name || "visitor"}`;
    const body = `Name: ${name}%0D%0AEmail: ${email}%0D%0A%0D%0AMessage:%0D%0A${message}`;
    window.location.href = `mailto:shubhangmishra5@gmail.com?subject=${subject}&body=${body}`;
    setStatus("If your mail app didn't open, please email me directly at shubhangmishra5@gmail.com.", "success");
  });

  // Footer year
  document.getElementById("year").textContent = new Date().getFullYear();
})();
