/**
 * Learn With Me - Global JavaScript (script.js)
 * =============================================
 * Features:
 * 1. Dark / Light Theme Toggle with LocalStorage persistence.
 * 2. Reading Progress Bar with smooth indicator at top of page.
 * 3. Table of Contents Scrollspy with active section tracking.
 * 4. Copy-to-Clipboard buttons for diagrams and code blocks with visual feedback.
 * 5. Back-to-Top floating button with smooth animated scrolling.
 */

function initAll() {
  initThemeToggle();
  initNavDropdown();
  initReadingProgressBar();
  initBackToTop();
  initTableOfContentsScrollspy();
  initCopyCodeButtons();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initAll);
} else {
  initAll();
}

/* ==========================================================================
   1. Dark / Light Theme Toggle
   ========================================================================== */
function initThemeToggle() {
  const themeToggle = document.getElementById('themeToggle');
  if (!themeToggle) return;

  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const currentTheme = localStorage.getItem('theme') || (prefersDark ? 'dark' : 'light');

  const applyTheme = (theme) => {
    document.documentElement.setAttribute('data-theme', theme);
    themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    themeToggle.setAttribute('aria-label', theme === 'dark' ? 'تفعيل الوضع النهاري' : 'تفعيل الوضع الليلي');
    
    // Update theme-color meta tag if present
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', theme === 'dark' ? '#0f172a' : '#2563eb');
    }
  };

  applyTheme(currentTheme);

  themeToggle.addEventListener('click', () => {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const newTheme = isDark ? 'light' : 'dark';
    applyTheme(newTheme);
    localStorage.setItem('theme', newTheme);
  });
}

/* ==========================================================================
   2. Reading Progress Bar
   ========================================================================== */
function initReadingProgressBar() {
  // Only display progress bar on pages with main content
  const article = document.querySelector('.article-main') || document.querySelector('main');
  if (!article) return;

  let progressBar = document.getElementById('readingProgressBar');
  if (!progressBar) {
    progressBar = document.createElement('div');
    progressBar.id = 'readingProgressBar';
    progressBar.className = 'reading-progress-bar';
    progressBar.setAttribute('aria-hidden', 'true');
    document.body.prepend(progressBar);
  }

  let ticking = false;
  const updateProgress = () => {
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const scrollPos = window.scrollY || window.pageYOffset;
    const progress = docHeight > 0 ? (scrollPos / docHeight) * 100 : 0;
    progressBar.style.width = `${Math.min(100, Math.max(0, progress))}%`;
    ticking = false;
  };

  const onScrollOrResize = () => {
    if (!ticking) {
      window.requestAnimationFrame(updateProgress);
      ticking = true;
    }
  };

  window.addEventListener('scroll', onScrollOrResize, { passive: true });
  window.addEventListener('resize', onScrollOrResize, { passive: true });

  updateProgress();
}

/* ==========================================================================
   3. Back to Top Floating Button
   ========================================================================== */
function initBackToTop() {
  let backBtn = document.getElementById('backToTop');
  if (!backBtn) {
    backBtn = document.createElement('button');
    backBtn.id = 'backToTop';
    backBtn.className = 'back-to-top';
    backBtn.type = 'button';
    backBtn.setAttribute('aria-label', 'العودة لأعلى الصفحة');
    backBtn.setAttribute('title', 'العودة للأعلى');
    backBtn.innerHTML = '↑';
    document.body.appendChild(backBtn);
  }

  let ticking = false;
  const toggleVisibility = () => {
    if (window.scrollY > 350) {
      backBtn.classList.add('visible');
    } else {
      backBtn.classList.remove('visible');
    }
    ticking = false;
  };

  window.addEventListener('scroll', () => {
    if (!ticking) {
      window.requestAnimationFrame(toggleVisibility);
      ticking = true;
    }
  }, { passive: true });

  backBtn.addEventListener('click', () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });

  toggleVisibility();
}

/* ==========================================================================
   4. Table of Contents Scrollspy
   ========================================================================== */
function initTableOfContentsScrollspy() {
  const tocList = document.querySelector('#toc .toc-list') || document.querySelector('.toc-list');
  if (!tocList) return;

  const tocLinks = Array.from(tocList.querySelectorAll('a[href^="#"]'));
  if (!tocLinks.length) return;

  // Resolve target elements
  const targets = [];
  tocLinks.forEach(link => {
    const targetId = link.getAttribute('href').substring(1);
    const targetEl = document.getElementById(targetId);
    if (targetEl) {
      targets.push({ id: targetId, link, el: targetEl });
    }
  });

  if (!targets.length) return;

  let activeLink = null;
  const headerOffset = 120; // Accounts for sticky header + spacing

  const highlightCurrentSection = () => {
    const scrollPos = window.scrollY + headerOffset;
    let current = targets[0];

    // Bottom of page detection: activate the last section
    const isAtBottom = (window.innerHeight + window.scrollY) >= (document.documentElement.scrollHeight - 40);
    if (isAtBottom) {
      current = targets[targets.length - 1];
    } else {
      for (let i = 0; i < targets.length; i++) {
        const top = targets[i].el.getBoundingClientRect().top + window.scrollY;
        if (top <= scrollPos) {
          current = targets[i];
        } else {
          break;
        }
      }
    }

    if (current && current.link !== activeLink) {
      if (activeLink) activeLink.classList.remove('active');
      current.link.classList.add('active');
      activeLink = current.link;

      // Autoscroll sidebar to keep active TOC item in view
      const sidebar = document.querySelector('.article-sidebar');
      if (sidebar && sidebar.scrollHeight > sidebar.clientHeight) {
        const linkRect = current.link.getBoundingClientRect();
        const sidebarRect = sidebar.getBoundingClientRect();
        if (linkRect.top < sidebarRect.top || linkRect.bottom > sidebarRect.bottom) {
          current.link.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
      }
    }
  };

  let ticking = false;
  window.addEventListener('scroll', () => {
    if (!ticking) {
      window.requestAnimationFrame(() => {
        highlightCurrentSection();
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });

  highlightCurrentSection();
}

/* ==========================================================================
   5. Copy to Clipboard for Diagram & Code Boxes
   ========================================================================== */
function initCopyCodeButtons() {
  const boxes = document.querySelectorAll('.diagram-box, pre');

  boxes.forEach(box => {
    // Avoid duplicate buttons
    if (box.querySelector('.copy-code-btn')) return;

    // Filter out tiny single-character or trivial snippets (e.g. "|" or "/")
    const textContent = box.innerText.trim();
    if (textContent.length < 5 && !textContent.includes('\n')) return;

    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-code-btn';
    copyBtn.type = 'button';
    copyBtn.setAttribute('aria-label', 'نسخ المحتوى');
    copyBtn.innerHTML = '<span>📋</span> <span>نسخ</span>';

    box.style.position = 'relative';
    box.appendChild(copyBtn);

    copyBtn.addEventListener('click', async (e) => {
      e.stopPropagation();

      // Extract text content excluding the copy button itself
      const clone = box.cloneNode(true);
      const btnInClone = clone.querySelector('.copy-code-btn');
      if (btnInClone) btnInClone.remove();
      const textToCopy = clone.innerText.trim();

      try {
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(textToCopy);
        } else {
          // Fallback for non-https or older environments
          const textArea = document.createElement('textarea');
          textArea.value = textToCopy;
          textArea.style.position = 'fixed';
          textArea.style.left = '-9999px';
          document.body.appendChild(textArea);
          textArea.focus();
          textArea.select();
          document.execCommand('copy');
          textArea.remove();
        }

        copyBtn.innerHTML = '<span>✔️</span> <span>تم النسخ</span>';
        copyBtn.classList.add('copied');

        setTimeout(() => {
          copyBtn.innerHTML = '<span>📋</span> <span>نسخ</span>';
          copyBtn.classList.remove('copied');
        }, 2200);
      } catch (err) {
        console.error('Failed to copy: ', err);
        copyBtn.innerHTML = '<span>❌</span> <span>تعذر النسخ</span>';
        setTimeout(() => {
          copyBtn.innerHTML = '<span>📋</span> <span>نسخ</span>';
        }, 2000);
      }
    });
  });
}

/* ==========================================================================
   6. Navigation Dropdown Menu
   ========================================================================== */
function initNavDropdown() {
  const dropdowns = document.querySelectorAll('.nav-dropdown');

  dropdowns.forEach(dropdown => {
    const toggle = dropdown.querySelector('.dropdown-toggle');
    if (!toggle) return;

    toggle.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = dropdown.classList.contains('open');

      // Close all dropdowns
      dropdowns.forEach(d => {
        d.classList.remove('open');
        d.querySelector('.dropdown-toggle')?.setAttribute('aria-expanded', 'false');
      });

      // Toggle current
      if (!isOpen) {
        dropdown.classList.add('open');
        toggle.setAttribute('aria-expanded', 'true');
      }
    });
  });

  // Close when clicking outside
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.nav-dropdown')) {
      dropdowns.forEach(d => {
        d.classList.remove('open');
        d.querySelector('.dropdown-toggle')?.setAttribute('aria-expanded', 'false');
      });
    }
  });

  // Close on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      dropdowns.forEach(d => {
        d.classList.remove('open');
        d.querySelector('.dropdown-toggle')?.setAttribute('aria-expanded', 'false');
      });
    }
  });
}
