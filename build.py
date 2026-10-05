#!/usr/bin/env python3
"""
Learn With Me - Static Site Generator & Course Automation Script
===============================================================
Automates:
1. Synchronizing Navbars and Footers across all HTML pages.
2. Generating/Updating sitemap.xml & robots.txt with Google Video Search schemas.
3. Synchronizing index.html (quick steps overview & articles grid).
4. Synchronizing linux-roadmap.html (lesson stats, step markers, and CTA buttons).
5. Compiling raw Markdown lessons into rich, SEO-optimized HTML pages.
"""

import os
import re
import json
import html
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = BASE_DIR / "content"
TEMPLATES_DIR = BASE_DIR / "templates"
LESSONS_JSON = CONTENT_DIR / "lessons.json"
LESSONS_DIR = CONTENT_DIR / "lessons"

SITE_URL = "https://learn.jalalmahmoud.online"


def load_lessons():
    """Loads all lessons metadata from content/lessons.json."""
    if not LESSONS_JSON.exists():
        raise FileNotFoundError(f"Missing registry: {LESSONS_JSON}")
    with open(LESSONS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def render_nav_links(current_filename, is_article=False):
    """Renders navbar <li> items with clean dropdown menu for lessons."""
    lessons = load_lessons()
    lines = []
    
    # 1. Home Link
    is_home_active = (current_filename == "index.html")
    lines.append(f'        <li><a href="index.html" class="nav-link{" active" if is_home_active else ""}">الرئيسية</a></li>')
    
    # 2. Roadmap Link
    is_roadmap_active = (current_filename == "linux-roadmap.html")
    lines.append(f'        <li><a href="linux-roadmap.html" class="nav-link{" active" if is_roadmap_active else ""}">خارطة طريق Linux</a></li>')
    
    # 3. Linux Lessons Dropdown Menu
    is_any_lesson_active = any(current_filename == l["filename"] for l in lessons)
    
    dropdown_lines = [
        '        <li class="nav-dropdown">',
        f'          <button class="nav-link dropdown-toggle{" active" if is_any_lesson_active else ""}" type="button" aria-expanded="false" aria-haspopup="true">',
        '            <span>دروس لينكس</span>',
        '            <span class="dropdown-arrow">▾</span>',
        '          </button>',
        '          <div class="dropdown-menu">',
        f'            <div class="dropdown-header">سلسلة مدخل إلى Linux ({len(lessons)} دروس)</div>'
    ]
    
    for l in lessons:
        is_active = (current_filename == l["filename"])
        short = l.get("short_title", l["title"])
        dropdown_lines.append(f'            <a href="{l["filename"]}" class="dropdown-item{" active" if is_active else ""}" data-lesson-id="{l["id"]}">')
        dropdown_lines.append(f'              <span class="dropdown-item-num">{l["id"]:02d}</span>')
        dropdown_lines.append(f'              <div class="dropdown-item-text">')
        dropdown_lines.append(f'                <span class="dropdown-item-title">{l["nav_title"]}</span>')
        dropdown_lines.append(f'                <span class="dropdown-item-sub">{short}</span>')
        dropdown_lines.append(f'              </div>')
        dropdown_lines.append(f'              <span class="dropdown-item-check" title="مكتمل">✓</span>')
        dropdown_lines.append(f'            </a>')
        
    dropdown_lines.append('            <div class="dropdown-divider"></div>')
    dropdown_lines.append('            <a href="linux-roadmap.html" class="dropdown-footer-link">')
    dropdown_lines.append('              <span>استعراض كافة الدروس في خارطة الطريق ←</span>')
    dropdown_lines.append('            </a>')
    dropdown_lines.append('          </div>')
    dropdown_lines.append('        </li>')
    
    lines.append("\n".join(dropdown_lines))
        
    # 4. Article TOC shortcut
    if is_article:
        lines.append('        <li><a href="#toc" class="nav-link">📑 فهرس المقال</a></li>')
        
    return "\n".join(lines)


def render_footer_links():
    """Renders footer <li> links."""
    lessons = load_lessons()
    lines = [
        '          <li><a href="index.html">الرئيسية</a></li>',
        '          <li><a href="linux-roadmap.html">خارطة طريق Linux</a></li>'
    ]
    for lesson in lessons:
        short_title = lesson.get("short_title", lesson["title"])
        lines.append(f'          <li><a href="{lesson["filename"]}">{lesson["nav_title"]}: {short_title}</a></li>')
    return "\n".join(lines)


def update_nav_and_footer_in_file(filepath, is_article=False):
    """Replaces <ul class="nav-menu">...</ul> and <ul class="footer-links">...</ul> in a given HTML file."""
    if not filepath.exists():
        return False
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    filename = filepath.name
    new_nav = render_nav_links(filename, is_article=is_article)
    new_footer = render_footer_links()

    # Replace nav-menu
    nav_pattern = r'(<ul class="nav-menu">)(.*?)(</ul>)'
    content = re.sub(
        nav_pattern,
        lambda m: f'{m.group(1)}\n{new_nav}\n      {m.group(3)}',
        content,
        flags=re.DOTALL
    )

    # Replace nav-actions to include search trigger button
    nav_actions_pattern = r'(<div class="nav-actions">)(.*?)(</div>)'
    new_nav_actions = '''        <button id="searchTriggerBtn" class="search-trigger-btn" type="button" aria-label="بحث سريع في المنصة (Ctrl+K)">
          <span class="search-icon">🔍</span>
          <span class="search-btn-text">بحث...</span>
          <kbd class="search-kbd">Ctrl K</kbd>
        </button>
        <button id="themeToggle" class="theme-toggle-btn" aria-label="تبديل الوضع الليلي">🌙</button>'''
    content = re.sub(
        nav_actions_pattern,
        lambda m: f'{m.group(1)}\n{new_nav_actions}\n      {m.group(3)}',
        content,
        flags=re.DOTALL
    )

    # Replace footer-links
    footer_pattern = r'(<ul class="footer-links">)(.*?)(</ul>)'
    content = re.sub(
        footer_pattern,
        lambda m: f'{m.group(1)}\n{new_footer}\n        {m.group(3)}',
        content,
        flags=re.DOTALL
    )

    # Replace old inline theme toggle script with external script.js
    inline_script_pattern = r'(?:<!-- Theme Toggle.*?-->\s*)?<script>\s*const themeToggle = document\.getElementById\(\'themeToggle\'\);.*?</script>'
    new_script_tag = '<!-- Interactive Enhancements & Theme Script -->\n  <script src="script.js"></script>'
    if re.search(inline_script_pattern, content, flags=re.DOTALL):
        content = re.sub(inline_script_pattern, new_script_tag, content, flags=re.DOTALL)
    elif '<script src="script.js"></script>' not in content:
        content = content.replace('</body>', f'  {new_script_tag}\n</body>')

    # Clean up any leftover duplicate theme comments
    content = content.replace('  <!-- Theme Toggle & Smooth Scroll Script -->\n', '')

    # Ensure article completion button exists in article pages
    if is_article:
        lesson_match = next((l for l in load_lessons() if l["filename"] == filename), None)
        if lesson_match and 'lesson-complete-toggle-btn' not in content:
            lid = lesson_match["id"]
            btn_markup = f'''            <div class="article-completion-action">
              <button class="lesson-complete-toggle-btn" data-lesson-id="{lid}" type="button">
                <span class="btn-check-icon">○</span>
                <span class="btn-check-text">تحديد هذا الدرس كمكتمل في مسارك التعليمي ✅</span>
              </button>
            </div>'''
            cta_inner_pat = r'(<div class="article-footer-cta">.*?</div>\s*)(<div style="display: flex;)'
            content = re.sub(cta_inner_pat, rf'\1{btn_markup}\n            \2', content, flags=re.DOTALL)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        
    return True


def update_lesson_navigation_in_file(filepath, lesson_meta, all_lessons):
    """Updates the .lesson-navigation section in an article HTML file to link correctly to prev/next lessons."""
    if not filepath.exists():
        return False
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lesson_id = lesson_meta["id"]
    prev_lesson = next((l for l in all_lessons if l["id"] == lesson_id - 1), None)
    next_lesson = next((l for l in all_lessons if l["id"] == lesson_id + 1), None)

    if prev_lesson:
        prev_card = f'''            <a href="{prev_lesson['filename']}" class="lesson-nav-card prev">
              <span class="lesson-nav-label">← الدرس السابق ({prev_lesson['nav_title']})</span>
              <span class="lesson-nav-title">{prev_lesson['title']}</span>
            </a>'''
    else:
        prev_card = '''            <a href="linux-roadmap.html" class="lesson-nav-card prev">
              <span class="lesson-nav-label">← خارطة الطريق</span>
              <span class="lesson-nav-title">خارطة طريق ومسار تعلم لينكس</span>
            </a>'''

    if next_lesson:
        next_card = f'''            <a href="{next_lesson['filename']}" class="lesson-nav-card next">
              <span class="lesson-nav-label">{next_lesson['nav_title']} ←</span>
              <span class="lesson-nav-title">{next_lesson['title']}</span>
            </a>'''
    else:
        next_card = '''            <a href="linux-roadmap.html" class="lesson-nav-card next">
              <span class="lesson-nav-label">خارطة الطريق ←</span>
              <span class="lesson-nav-title">استعراض كافة الدروس في خارطة طريق Linux</span>
            </a>'''

    nav_block = f'''          <!-- Previous and Next Lesson Navigation -->
          <div class="lesson-navigation">
{prev_card}
{next_card}
          </div>'''

    nav_pat = r'(?:<!-- Previous and Next Lesson Navigation -->\s*)?<div class="lesson-navigation">.*?</div>'
    if re.search(nav_pat, content, flags=re.DOTALL):
        content = re.sub(nav_pat, nav_block, content, flags=re.DOTALL)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def generate_sitemap():
    """Generates sitemap.xml with full Google video search extension."""
    lessons = load_lessons()
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">',
        '  ',
        '  <!-- Homepage -->',
        '  <url>',
        f'    <loc>{SITE_URL}/</loc>',
        '    <lastmod>2026-10-04</lastmod>',
        '    <changefreq>weekly</changefreq>',
        '    <priority>1.0</priority>',
        '  </url>',
        '  <url>',
        f'    <loc>{SITE_URL}/index.html</loc>',
        '    <lastmod>2026-10-04</lastmod>',
        '    <changefreq>weekly</changefreq>',
        '    <priority>1.0</priority>',
        '  </url>',
        '  ',
        '  <!-- Linux Roadmap -->',
        '  <url>',
        f'    <loc>{SITE_URL}/linux-roadmap.html</loc>',
        '    <lastmod>2026-10-04</lastmod>',
        '    <changefreq>weekly</changefreq>',
        '    <priority>0.9</priority>',
        '  </url>',
        '  '
    ]

    for lesson in lessons:
        lines.append('  <!-- ' + lesson["nav_title"] + ' -->')
        lines.append('  <url>')
        lines.append(f'    <loc>{SITE_URL}/{lesson["filename"]}</loc>')
        lines.append('    <lastmod>2026-10-04</lastmod>')
        lines.append('    <changefreq>monthly</changefreq>')
        lines.append('    <priority>0.85</priority>')
        
        # Add Google Video Schema if video_id exists
        video_id = lesson.get("video_id")
        if video_id:
            lines.append('    <video:video>')
            lines.append(f'      <video:thumbnail_loc>https://img.youtube.com/vi/{video_id}/hqdefault.jpg</video:thumbnail_loc>')
            lines.append(f'      <video:title>{html.escape(lesson["title"])}</video:title>')
            desc = lesson.get("description", lesson["title"])
            lines.append(f'      <video:description>{html.escape(desc)}</video:description>')
            lines.append(f'      <video:player_loc>https://www.youtube.com/embed/{video_id}</video:player_loc>')
            lines.append('      <video:publication_date>2026-10-04</video:publication_date>')
            lines.append('      <video:family_friendly>yes</video:family_friendly>')
            lines.append('    </video:video>')
            
        lines.append('  </url>')
        lines.append('  ')

    lines.append('</urlset>')
    sitemap_path = BASE_DIR / "sitemap.xml"
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Generated {sitemap_path.name} with {len(lessons) + 3} URLs.")


def generate_robots():
    """Generates robots.txt pointing to sitemap.xml."""
    content = f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n"
    robots_path = BASE_DIR / "robots.txt"
    with open(robots_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {robots_path.name}.")


def sync_index_page():
    """Synchronizes lesson cards in index.html."""
    index_path = BASE_DIR / "index.html"
    if not index_path.exists():
        return

    lessons = load_lessons()
    
    # 1. Quick Steps Grid Cards
    quick_cards = []
    for l in lessons:
        quick_cards.append(f'''          <a href="{l['filename']}" class="card" style="padding: 1rem; background: var(--bg-surface-alt); text-decoration: none;">
            <strong style="color: var(--primary); display: block; margin-bottom: 0.25rem;">{l['short_title']}</strong>
            <span style="font-size: 0.85rem; color: var(--accent); font-weight: 600;">{l['nav_title']} • متاح بالفيديو والمقال</span>
          </a>''')
    quick_cards_html = "\n".join(quick_cards)

    # 2. Main Articles Grid Cards
    article_cards = []
    for l in lessons:
        border_style = f" style=\"border-color: {l.get('border_color', 'var(--primary)')};\""
        article_cards.append(f'''      <!-- {l['nav_title']} Card -->
      <div class="card"{border_style}>
        <div class="card-header">
          <div class="card-icon">{l.get('icon', '📖')}</div>
          <div style="display: flex; gap: 0.5rem; margin-bottom: 0.5rem;">
            <span class="badge badge-accent">{l['nav_title']}</span>
            <span class="badge badge-primary">{l.get('badge_category', 'دروس لينكس')}</span>
          </div>
          <h3 class="card-title">
            <a href="{l['filename']}">{l['title']}</a>
          </h3>
        </div>
        <div class="card-body">
          {l.get('card_desc', l.get('description', ''))}
        </div>
        <div class="card-footer">
          <span style="font-size: 0.85rem; color: var(--text-muted);">⏱️ {l.get('read_time', '20 دقيقة')} • فيديو مصاحب</span>
          <a href="{l['filename']}" class="btn btn-outline btn-sm">اقرأ {l['nav_title']} ←</a>
        </div>
      </div>''')
    article_cards_html = "\n".join(article_cards)

    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace quick steps
    quick_pattern = r'(<h4 style="font-size: 1rem; color: var\(--text-muted\); margin-bottom: 1rem;">محطات سلسلة الدروس السريعة:</h4>\s*<div class="grid grid-3" style="gap: 1rem;">)(.*?)(</div>\s*</div>\s*</div>\s*<!-- Latest Articles Section -->)'
    content = re.sub(
        quick_pattern,
        lambda m: f'{m.group(1)}\n{quick_cards_html}\n        {m.group(3)}',
        content,
        flags=re.DOTALL
    )

    # Replace article grid
    articles_pattern = r'(<div class="grid grid-2">)(.*?)(</div>\s*</main>)'
    content = re.sub(
        articles_pattern,
        lambda m: f'{m.group(1)}\n{article_cards_html}\n    {m.group(3)}',
        content,
        flags=re.DOTALL
    )

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print("Synchronized index.html cards and quick steps.")


def sync_roadmap_page():
    """Synchronizes lesson steps, stats, and CTA buttons in linux-roadmap.html."""
    roadmap_path = BASE_DIR / "linux-roadmap.html"
    if not roadmap_path.exists():
        return

    lessons = load_lessons()
    count = len(lessons)

    with open(roadmap_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update stats numbers
    content = re.sub(r'<div style="font-size: 1\.75rem; font-weight: 800; color: var\(--primary\);">\s*\d+\s*دروس\s*</div>',
                     f'<div style="font-size: 1.75rem; font-weight: 800; color: var(--primary);">{count} دروس</div>', content)
    content = re.sub(r'<div style="font-size: 1\.75rem; font-weight: 800; color: var\(--accent\);">\s*\d+\s*مقالات \+ فيديوهات\s*</div>',
                     f'<div style="font-size: 1.75rem; font-weight: 800; color: var(--accent);">{count} مقالات + فيديوهات</div>', content)

    # 2. Render steps timeline
    steps_html = []
    for l in lessons:
        tags_html = "\n".join([f'              <span class="roadmap-topic-tag">{t}</span>' for t in l.get("tags", [])])
        steps_html.append(f'''        <!-- Step {l['id']}: {l['nav_title']} -->
        <div class="roadmap-step" data-lesson-id="{l['id']}">
          <div class="roadmap-marker">{l['id']}</div>
          <div class="roadmap-content">
            <div class="roadmap-header">
              <div>
                <span class="badge badge-accent">{l.get('badge_accent', f"{l['nav_title']} • متاح الآن 🚀")}</span>
                <h3 class="roadmap-step-title" style="margin-top: 0.5rem;">{l['title']}</h3>
              </div>
              <div style="display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap;">
                <span class="badge badge-primary">المستوى: {l.get('level', 'متوسط')}</span>
                <button class="roadmap-complete-btn" data-lesson-id="{l['id']}" type="button" aria-label="تحديد الدرس كمكتمل">
                  <span class="btn-check-icon">○</span>
                  <span class="btn-check-text">تحديد كمكتمل</span>
                </button>
              </div>
            </div>
            <p>
              {l.get('roadmap_desc', l.get('description', ''))}
            </p>

            <div class="roadmap-article-highlight">
              <div class="roadmap-article-info">
                <div style="display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.4rem; flex-wrap: wrap;">
                  <span class="badge badge-primary">مقال تفصيلي + فيديو 📺</span>
                  <span style="font-size: 0.85rem; color: var(--text-muted);">⏱️ {l.get('read_time', '20 دقيقة')} قراءة</span>
                </div>
                <h4><a href="{l['filename']}" style="color: inherit;">{l['title']}</a></h4>
                <p>
                  يحتوي الدرس على شرح علمي وتطبيقي شامل مدعوم بالرسوم التوضيحية مع فيديو تعليمي عملي مدمج.
                </p>
              </div>
              <div>
                <a href="{l['filename']}" class="btn btn-primary">
                  <span>فتح {l['nav_title']}</span>
                  <span>←</span>
                </a>
              </div>
            </div>

            <div class="roadmap-tags">
{tags_html}
            </div>
          </div>
        </div>''')

    steps_full_html = "\n\n".join(steps_html)

    # 3. Personal Learning Progress Dashboard Card
    dashboard_card_html = f'''      <!-- Personal Learning Progress Dashboard -->
      <div class="progress-dashboard-card" id="roadmapProgressCard">
        <div class="progress-dashboard-top">
          <div class="progress-dashboard-info">
            <span class="progress-icon">🎯</span>
            <div>
              <h3 class="progress-dashboard-title">لوحة تتبع تقدمك في مسار Linux</h3>
              <p class="progress-dashboard-subtitle" id="progressStatusText">أكملت 0 من {count} دروس (0%) بنجاح</p>
            </div>
          </div>
          <div class="progress-badge-wrap">
            <span class="progress-motivation-badge" id="progressMotivationBadge">🌱 خطوتك الأولى تبدأ الآن</span>
            <button class="progress-reset-btn" id="progressResetBtn" type="button" title="إعادة تعيين التقدم">↺</button>
          </div>
        </div>
        <div class="progress-bar-container">
          <div class="progress-bar-track">
            <div class="progress-bar-fill" id="roadmapProgressFill" style="width: 0%;"></div>
          </div>
          <span class="progress-percentage-label" id="progressPercentageLabel">0%</span>
        </div>
      </div>'''

    if 'id="roadmapProgressCard"' not in content:
        content = content.replace('<div class="roadmap-container">', f'{dashboard_card_html}\n\n      <div class="roadmap-container">')
    else:
        content = re.sub(r'أكملت 0 من \d+ دروس', f'أكملت 0 من {count} دروس', content)
    
    # Replace roadmap-container
    steps_pattern = r'(<div class="roadmap-container">)(.*?)(</div>\s*</section>\s*<!-- Call to Action Banner -->)'
    content = re.sub(
        steps_pattern,
        lambda m: f'{m.group(1)}\n\n{steps_full_html}\n\n      {m.group(3)}',
        content,
        flags=re.DOTALL
    )

    # 3. Update bottom CTA buttons
    cta_buttons = []
    for l in lessons:
        grad_style = f" style=\"background: {l.get('btn_gradient', 'linear-gradient(135deg, var(--primary), #1d4ed8)')};\""
        cta_buttons.append(f'''        <a href="{l['filename']}" class="btn btn-primary btn-lg"{grad_style}>
          <span>{l['nav_title']}: {l.get('short_title', l['title'])} ←</span>
        </a>''')
    cta_buttons.append('''        <a href="index.html" class="btn btn-outline btn-lg">
          <span>العودة للرئيسية</span>
        </a>''')
    cta_buttons_html = "\n".join(cta_buttons)

    cta_pattern = r'(<div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">)(.*?)(</div>\s*</section>\s*</main>)'
    content = re.sub(
        cta_pattern,
        lambda m: f'{m.group(1)}\n{cta_buttons_html}\n      {m.group(3)}',
        content,
        flags=re.DOTALL
    )

    with open(roadmap_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Synchronized linux-roadmap.html with {count} steps and updated stats.")


def parse_markdown_to_lesson_html(markdown_text, lesson_meta):
    """
    Parses Markdown content into clean semantic HTML sections with IDs,
    diagram boxes, callout boxes, and comparison tables.
    Returns: (intro_html, body_html, toc_items_list)
    """
    lines = markdown_text.splitlines()
    
    toc_items = []
    body_blocks = []
    intro_blocks = []
    
    in_intro = True
    in_code_block = False
    code_block_lines = []
    code_lang = ""
    
    in_table = False
    table_rows = []
    
    sec_counter = 0

    def flush_table():
        nonlocal in_table, table_rows
        if not in_table or not table_rows:
            in_table = False
            table_rows = []
            return ""
        
        # Build table HTML
        html_rows = []
        is_header = True
        
        table_html = ['          <div class="table-container">', '            <table class="comparison-table">']
        for row in table_rows:
            cols = [c.strip() for c in row.strip("|").split("|")]
            # Check if divider row (e.g. |---|---|)
            if all(set(c).issubset({'-', ':', ' '}) for c in cols if c):
                continue
            
            if is_header:
                table_html.append('              <thead>')
                table_html.append('                <tr>')
                for c in cols:
                    table_html.append(f'                  <th>{parse_inline(c)}</th>')
                table_html.append('                </tr>')
                table_html.append('              </thead>')
                table_html.append('              <tbody>')
                is_header = False
            else:
                table_html.append('                <tr>')
                for idx, c in enumerate(cols):
                    prefix = "<strong>" if idx == 0 else ""
                    suffix = "</strong>" if idx == 0 else ""
                    table_html.append(f'                  <td>{prefix}{parse_inline(c)}{suffix}</td>')
                table_html.append('                </tr>')
        
        if not is_header:
            table_html.append('              </tbody>')
        table_html.append('            </table>')
        table_html.append('          </div>')
        
        in_table = False
        table_rows = []
        return "\n".join(table_html)

    def parse_inline(text):
        # Escape basic HTML chars except intentional tags
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
        text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
        return text

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Handle Code / Diagram blocks
        if stripped.startswith("```"):
            if in_code_block:
                # Flush diagram
                code_content = html.escape("\n".join(code_block_lines))
                block_html = f'          <div class="diagram-box">\n{code_content}\n          </div>'
                if in_intro:
                    intro_blocks.append(block_html)
                else:
                    body_blocks.append(block_html)
                in_code_block = False
                code_block_lines = []
            else:
                if in_table:
                    body_blocks.append(flush_table())
                in_code_block = True
                code_lang = stripped[3:].strip()
                code_block_lines = []
            i += 1
            continue

        if in_code_block:
            code_block_lines.append(line)
            i += 1
            continue

        # Handle Tables
        if stripped.startswith("|") and stripped.endswith("|"):
            in_table = True
            table_rows.append(stripped)
            i += 1
            continue
        elif in_table:
            body_blocks.append(flush_table())

        # Empty lines
        if not stripped:
            i += 1
            continue

        # Raw HTML block pass-through
        if stripped.startswith("<div") or stripped.startswith("<table") or stripped.startswith("<blockquote") or stripped.startswith("<!--"):
            html_lines = []
            while i < len(lines):
                html_lines.append(lines[i])
                if stripped.startswith("<!--") and "-->" in lines[i]:
                    i += 1
                    break
                elif stripped.startswith("<div") and "</div>" in lines[i]:
                    i += 1
                    break
                elif stripped.startswith("<blockquote") and "</blockquote>" in lines[i]:
                    i += 1
                    break
                elif stripped.startswith("<table") and "</table>" in lines[i]:
                    i += 1
                    break
                i += 1
            raw_html = "\n".join(html_lines)
            if in_intro:
                intro_blocks.append(raw_html)
            else:
                body_blocks.append(raw_html)
            continue

        # Headings
        if stripped.startswith("#"):
            match = re.match(r'^(#+)\s*(.*)', stripped)
            level = len(match.group(1))
            heading_text = match.group(2).strip()

            if level == 1 or level == 2:
                # Top level title or main section
                # If it's the very first # title, treat as main article header
                if sec_counter == 0 and in_intro:
                    # Article main heading
                    pass
                else:
                    in_intro = False
                    sec_counter += 1
                    sec_id = f"sec-{sec_counter}"
                    clean_title = re.sub(r'^(?:\d+|[أ-ي]+)\.?\s*(?:[—–\-:]\s*)?', '', heading_text)
                    display_title = f"{sec_counter}. {clean_title}"
                    toc_items.append((sec_id, display_title))
                    hr_prefix = "          <hr>\n\n" if sec_counter > 1 else ""
                    body_blocks.append(f'{hr_prefix}          <!-- Section {sec_counter} -->\n          <h2 id="{sec_id}">{display_title}</h2>')
            elif level >= 3:
                clean_sub = heading_text
                body_blocks.append(f'          <h3 style="margin-top: 1.5rem; color: var(--primary);">{parse_inline(clean_sub)}</h3>')
            i += 1
            continue

        # Horizontal rule
        if stripped in ["---", "***", "___"]:
            if in_intro:
                in_intro = False
            i += 1
            continue

        # GitHub Style Callouts (> [!NOTE], > [!TIP], > [!IMPORTANT], > [!WARNING], > [!CAUTION])
        if stripped.startswith("> [!"):
            m = re.match(r'^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*(.*)', stripped)
            alert_type = m.group(1).upper() if m else "NOTE"
            first_line = m.group(2).strip() if m else ""
            alert_lines = [first_line] if first_line else []
            i += 1
            while i < len(lines) and lines[i].strip().startswith(">"):
                alert_lines.append(lines[i].strip().lstrip("> ").strip())
                i += 1
            alert_text = parse_inline(" ".join(alert_lines))
            icon_map = {
                "NOTE": "💡 إضاءة تاريخية وفلسفية:",
                "TIP": "🎯 فكرة هندسية محورية:",
                "IMPORTANT": "⚠️ نقطة جوهرية ومحورية:",
                "WARNING": "⚠️ تحذير وملاحظة نقدية:",
                "CAUTION": "🛑 تنبيه قانوني وتاريخي:"
            }
            border_color_map = {
                "NOTE": "var(--primary)",
                "TIP": "var(--accent)",
                "IMPORTANT": "var(--accent-orange)",
                "WARNING": "var(--accent-orange)",
                "CAUTION": "#ef4444"
            }
            callout_html = f'''          <div class="callout-box" style="border-right-color: {border_color_map.get(alert_type, 'var(--primary)')};">
            <h4 style="margin-bottom: 0.5rem; color: {border_color_map.get(alert_type, 'var(--primary)')};">{icon_map.get(alert_type, '💡 إضاءة مهمة:')}</h4>
            <p style="margin-bottom: 0; font-size: 1.05rem;">
              {alert_text}
            </p>
          </div>'''
            if in_intro:
                intro_blocks.append(callout_html)
            else:
                body_blocks.append(callout_html)
            continue

        # Blockquote / Standard Quote
        if stripped.startswith(">"):
            quote_text = parse_inline(stripped.lstrip("> ").strip())
            quote_html = f'''          <blockquote style="margin: 1.5rem 0; padding: 1.25rem 1.75rem; border-right: 4px solid var(--primary); background: var(--bg-surface-alt); border-radius: var(--radius-md); font-size: 1.15rem; font-weight: 600; color: var(--text-main);">
            «{quote_text}»
          </blockquote>'''
            if in_intro:
                intro_blocks.append(quote_html)
            else:
                body_blocks.append(quote_html)
            i += 1
            continue

        # Lists (unordered)
        if stripped.startswith("- ") or stripped.startswith("* "):
            list_items = []
            while i < len(lines) and (lines[i].strip().startswith("- ") or lines[i].strip().startswith("* ")):
                item_text = parse_inline(lines[i].strip()[2:].strip())
                list_items.append(f'            <li>{item_text}</li>')
                i += 1
            list_html = '          <ul>\n' + "\n".join(list_items) + '\n          </ul>'
            if in_intro:
                intro_blocks.append(list_html)
            else:
                body_blocks.append(list_html)
            continue

        # Lists (ordered)
        if re.match(r'^\d+\.\s+', stripped):
            list_items = []
            while i < len(lines) and re.match(r'^\d+\.\s+', lines[i].strip()):
                m = re.match(r'^\d+\.\s+(.*)', lines[i].strip())
                item_text = parse_inline(m.group(1).strip())
                list_items.append(f'            <li>{item_text}</li>')
                i += 1
            list_html = '          <ol>\n' + "\n".join(list_items) + '\n          </ol>'
            if in_intro:
                intro_blocks.append(list_html)
            else:
                body_blocks.append(list_html)
            continue

        # Standard Paragraph
        para_text = parse_inline(stripped)
        p_html = f'          <p>\n            {para_text}\n          </p>'
        if in_intro:
            intro_blocks.append(p_html)
        else:
            body_blocks.append(p_html)
        i += 1

    if in_table:
        body_blocks.append(flush_table())

    return "\n\n".join(intro_blocks), "\n\n".join(body_blocks), toc_items


def build_lesson_page(lesson_meta, all_lessons):
    """Compiles a single lesson from Markdown into a rich, SEO-optimized HTML page."""
    template_path = TEMPLATES_DIR / "lesson_template.html"
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    lesson_id = lesson_meta["id"]
    filename = lesson_meta["filename"]
    md_file = LESSONS_DIR / f"lesson-{lesson_id:02d}.md"
    
    if not md_file.exists():
        print(f"Skipping lesson {lesson_id} (No markdown file at {md_file})")
        return False

    with open(md_file, "r", encoding="utf-8") as f:
        md_text = f.read()

    intro_html, body_html, toc_items = parse_markdown_to_lesson_html(md_text, lesson_meta)

    # 1. Table of Contents
    toc_links = ['          <li><a href="#intro">مقدمة الدرس</a></li>',
                 '          <li><a href="#video-section">📺 الفيديو التعليمي المصاحب</a></li>']
    for sec_id, sec_title in toc_items:
        toc_links.append(f'          <li><a href="#{sec_id}">{sec_title}</a></li>')
    toc_html = "\n".join(toc_links)

    # 2. Video Section
    video_id = lesson_meta.get("video_id", "")
    video_caption = lesson_meta.get("video_caption", f"فيديو {lesson_meta['nav_title']}: شرح تطبيقي وعلمي شامل.")
    video_section = f'''          <!-- Embedded YouTube Video Section -->
          <div class="video-wrapper" id="video-section">
            <div class="video-container">
              <iframe 
                src="https://www.youtube.com/embed/{video_id}" 
                title="{lesson_meta['title']}" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                referrerpolicy="strict-origin-when-cross-origin" 
                loading="lazy"
                allowfullscreen>
              </iframe>
            </div>
            <p class="video-caption">
              <span>📺</span> <strong>فيديو {lesson_meta['nav_title']}:</strong> {video_caption}
            </p>
          </div>'''

    # 3. Prev & Next Navigation
    prev_lesson = next((l for l in all_lessons if l["id"] == lesson_id - 1), None)
    next_lesson = next((l for l in all_lessons if l["id"] == lesson_id + 1), None)

    prev_card = ""
    if prev_lesson:
        prev_card = f'''            <a href="{prev_lesson['filename']}" class="lesson-nav-card prev">
              <span class="lesson-nav-label">← الدرس السابق ({prev_lesson['nav_title']})</span>
              <span class="lesson-nav-title">{prev_lesson['title']}</span>
            </a>'''
    else:
        prev_card = '''            <a href="linux-roadmap.html" class="lesson-nav-card prev">
              <span class="lesson-nav-label">← خارطة الطريق</span>
              <span class="lesson-nav-title">خارطة طريق ومسار تعلم لينكس</span>
            </a>'''

    next_card = ""
    if next_lesson:
        next_card = f'''            <a href="{next_lesson['filename']}" class="lesson-nav-card next">
              <span class="lesson-nav-label">{next_lesson['nav_title']} ←</span>
              <span class="lesson-nav-title">{next_lesson['title']}</span>
            </a>'''
    else:
        next_card = '''            <a href="linux-roadmap.html" class="lesson-nav-card next">
              <span class="lesson-nav-label">خارطة الطريق ←</span>
              <span class="lesson-nav-title">استعراض كافة الدروس في خارطة طريق Linux</span>
            </a>'''

    nav_html = f'''          <div class="lesson-navigation">
{prev_card}
{next_card}
          </div>'''

    # 4. Footer CTA
    footer_cta = f'''          <div class="article-footer-cta">
            <div class="article-footer-cta-text">
              <h3>رائع ومذهل! أتممت بنجاح قراءة واستيعاب {lesson_meta['nav_title']} 🎉</h3>
              <p>واصل تقدمك في المسار واكتشف المزيد من أسرار أنظمة التشغيل وهندسة النظم عبر خارطة الطريق!</p>
            </div>
            <div class="article-completion-action">
              <button class="lesson-complete-toggle-btn" data-lesson-id="{lesson_meta['id']}" type="button">
                <span class="btn-check-icon">○</span>
                <span class="btn-check-text">تحديد هذا الدرس كمكتمل في مسارك التعليمي ✅</span>
              </button>
            </div>
            <div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
              <a href="linux-roadmap.html" class="btn btn-primary btn-lg">استعراض خارطة طريق Linux ←</a>
              <a href="index.html" class="btn btn-outline btn-lg">الصفحة الرئيسية</a>
            </div>
          </div>'''

    # 5. Schema.org Structured Data
    canonical_url = f"{SITE_URL}/{filename}"
    schema_dict = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": f"{SITE_URL}/#website",
                "url": f"{SITE_URL}/",
                "name": "Learn With Me",
                "inLanguage": "ar"
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{canonical_url}#breadcrumb",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "الرئيسية", "item": f"{SITE_URL}/index.html"},
                    {"@type": "ListItem", "position": 2, "name": "خارطة طريق Linux", "item": f"{SITE_URL}/linux-roadmap.html"},
                    {"@type": "ListItem", "position": 3, "name": lesson_meta["nav_title"], "item": canonical_url}
                ]
            },
            {
                "@type": "TechArticle",
                "@id": f"{canonical_url}#article",
                "headline": lesson_meta["title"],
                "description": lesson_meta.get("description", ""),
                "inLanguage": "ar",
                "mainEntityOfPage": canonical_url,
                "datePublished": "2026-10-04T08:00:00+00:00",
                "dateModified": "2026-10-04T08:00:00+00:00",
                "author": {"@type": "Person", "name": "Jalal Mahmoud"},
                "publisher": {"@type": "Organization", "name": "Learn With Me", "logo": {"@type": "ImageObject", "url": f"{SITE_URL}/brand-icon.png"}},
                "image": f"{SITE_URL}/icon.png"
            },
            {
                "@type": "VideoObject",
                "@id": f"{canonical_url}#video",
                "name": lesson_meta["title"],
                "description": video_caption,
                "thumbnailUrl": [
                    f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                    f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                ],
                "uploadDate": "2026-10-04T08:00:00+00:00",
                "contentUrl": f"https://www.youtube.com/watch?v={video_id}",
                "embedUrl": f"https://www.youtube.com/embed/{video_id}",
                "inLanguage": "ar"
            }
        ]
    }
    schema_json = json.dumps(schema_dict, ensure_ascii=False, indent=2)

    # 6. Render Header & Footer
    with open(TEMPLATES_DIR / "header.html", "r", encoding="utf-8") as f:
        header_tpl = f.read()
    header_html = header_tpl.replace("{{NAV_LINKS}}", render_nav_links(filename, is_article=True))

    with open(TEMPLATES_DIR / "footer.html", "r", encoding="utf-8") as f:
        footer_tpl = f.read()
    footer_html = footer_tpl.replace("{{FOOTER_LINKS}}", render_footer_links())

    # Replace placeholders
    page_html = template
    replacements = {
        "{{TITLE}}": f"{lesson_meta['title']} | Learn With Me",
        "{{OG_TITLE}}": lesson_meta['title'],
        "{{DESCRIPTION}}": lesson_meta.get("description", ""),
        "{{KEYWORDS}}": ", ".join(lesson_meta.get("tags", ["Linux", "UNIX", "Learn With Me"])),
        "{{CANONICAL_URL}}": canonical_url,
        "{{HEADER}}": header_html,
        "{{BREADCRUMB_CURRENT}}": f"{lesson_meta['nav_title']}: {lesson_meta.get('short_title', lesson_meta['title'])}",
        "{{TOC_ITEMS}}": toc_html,
        "{{BADGE_PRIMARY}}": f"{lesson_meta['nav_title']} في السلسلة 🚀",
        "{{BADGE_CATEGORY}}": lesson_meta.get("badge_category", "تاريخ وتطور النظم"),
        "{{LESSON_HEADING}}": lesson_meta["title"],
        "{{READ_TIME}}": lesson_meta.get("read_time", "20 دقيقة"),
        "{{AUDIENCE}}": "مهندسو برمجيات، معماريو نظم، ومحبو تاريخ وتطور الحوسبة",
        "{{INTRO_CONTENT}}": intro_html,
        "{{VIDEO_SECTION}}": video_section,
        "{{ARTICLE_BODY}}": body_html,
        "{{LESSON_NAVIGATION}}": nav_html,
        "{{FOOTER_CTA}}": footer_cta,
        "{{FOOTER}}": footer_html,
        "{{SCHEMA_JSON}}": schema_json
    }

    for placeholder, val in replacements.items():
        page_html = page_html.replace(placeholder, val)

    out_file = BASE_DIR / filename
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(page_html)

    print(f"Compiled lesson page: {out_file.name}")
    return True


def generate_search_index():
    """Generates search-index.json containing all lessons, sections, headings, and tags."""
    lessons = load_lessons()
    index_items = []

    # 1. Homepage & Roadmap entries
    index_items.append({
        "type": "page",
        "lessonId": 0,
        "lessonTitle": "الرئيسية",
        "title": "الصفحة الرئيسية | منصة Learn With Me",
        "url": "index.html",
        "desc": "منصة تعليمية متخصصة تقدم خرائط طريق ومقالات تقنية شاملة لاحتراف لينكس وهندسة الأنظمة والـ DevOps.",
        "tags": ["الرئيسية", "Learn With Me", "دورات", "مسارات"]
    })
    index_items.append({
        "type": "page",
        "lessonId": 0,
        "lessonTitle": "خارطة الطريق",
        "title": "خارطة طريق ومسار تعلم Linux المنهجي",
        "url": "linux-roadmap.html",
        "desc": "خارطة طريق تفاعلية متكاملة لتعلم واحتراف نظام التشغيل لينكس خطوة بخطوة مع متتبع إنجاز شخصي.",
        "tags": ["Roadmap", "خارطة طريق", "مسار لينكس", "تتبع التقدم"]
    })

    # 2. Lessons & sections
    for l in lessons:
        index_items.append({
            "type": "lesson",
            "lessonId": l["id"],
            "lessonTitle": l["nav_title"],
            "title": f"{l['nav_title']}: {l['title']}",
            "url": l["filename"],
            "desc": l.get("description", ""),
            "tags": l.get("tags", [])
        })

        hf = BASE_DIR / l["filename"]
        if hf.exists():
            html_content = hf.read_text(encoding="utf-8")
            toc_match = re.search(r'<ul class="toc-list">(.*?)</ul>', html_content, re.DOTALL)
            if toc_match:
                links = re.findall(r'<a href="(#[^"]+)">(.*?)</a>', toc_match.group(1))
                for anchor, text in links:
                    if anchor not in ["#intro", "#video-section"]:
                        clean_text = re.sub(r'<.*?>', '', text).strip()
                        index_items.append({
                            "type": "section",
                            "lessonId": l["id"],
                            "lessonTitle": l["nav_title"],
                            "title": clean_text,
                            "url": f"{l['filename']}{anchor}",
                            "desc": f"{l['nav_title']} • {clean_text}",
                            "tags": l.get("tags", [])
                        })

    out_file = BASE_DIR / "search-index.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(index_items, f, ensure_ascii=False, indent=2)
    print(f"Generated search-index.json with {len(index_items)} searchable targets.")


def build_all(compile_all=False, compile_ids=None):
    """Main build process."""
    print("=" * 60)
    print("🚀 Starting Learn With Me Automated Site Build...")
    print("=" * 60)

    lessons = load_lessons()
    print(f"Loaded {len(lessons)} lessons from {LESSONS_JSON.name}")

    # 1. Compile Markdown lessons only when needed
    for l in lessons:
        out_html = BASE_DIR / l["filename"]
        md_file = LESSONS_DIR / f"lesson-{l['id']:02d}.md"
        
        should_compile = False
        if compile_all:
            should_compile = True
        elif compile_ids and l["id"] in compile_ids:
            should_compile = True
        elif not out_html.exists():
            should_compile = True

        if should_compile and md_file.exists():
            build_lesson_page(l, lessons)

    # 2. Synchronize navigation and footers across all HTML pages
    all_html_files = sorted(list(BASE_DIR.glob("*.html")))
    for hf in all_html_files:
        is_article = (hf.name not in ["index.html", "linux-roadmap.html"])
        update_nav_and_footer_in_file(hf, is_article=is_article)
        if is_article:
            matching_lesson = next((l for l in lessons if l["filename"] == hf.name), None)
            if matching_lesson:
                update_lesson_navigation_in_file(hf, matching_lesson, lessons)
    print(f"Updated header navigation, footers & lesson navigation across {len(all_html_files)} HTML pages.")

    # 3. Synchronize index.html and linux-roadmap.html
    sync_index_page()
    sync_roadmap_page()

    # 4. Generate sitemap.xml, robots.txt, and search-index.json
    generate_sitemap()
    generate_robots()
    generate_search_index()

    print("=" * 60)
    print("✨ Site build completed successfully in fractions of a second!")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    compile_all = "--compile-all" in sys.argv
    compile_ids = []
    
    if "--compile" in sys.argv:
        idx = sys.argv.index("--compile")
        if idx + 1 < len(sys.argv):
            try:
                compile_ids.append(int(sys.argv[idx + 1]))
            except ValueError:
                pass

    build_all(compile_all=compile_all, compile_ids=compile_ids)
