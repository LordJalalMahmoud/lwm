# Learn With Me 🐧

> **منصة تعليمية عربية متخصصة في هندسة النظم، لينكس، وتقنيات السحابة والـ DevOps.**  
> رابط المنصة الرسمي: [learn.jalalmahmoud.online](https://learn.jalalmahmoud.online/)

---

## 🌟 نظرة عامة (Overview)

منصة **Learn With Me** تقدم خرائط طريق تفاعلية مبسطة ومقالات تقنية عميقة ومصادر تعلم متدرجة تأخذ بيدك من المبادئ الأولية لأنظمة التشغيل والعتاد، وحتى إدارة أضخم مراكز البيانات والحوسبة السحابية.

جميع الدروس مدعومة بالمقالات التفصيلية، المخططات المعمارية، وجداول المقارنة، مع فيديوهات شرح تطبيقي مدمجة.

---

## 🗺️ مسار خارطة طريق Linux (المتاح حتى الإصدار v1.0.0)

| رقم الدرس | عنوان الدرس | الموضوع الرئيسي | الفيديو المصاحب |
| :---: | :--- | :--- | :---: |
| **01** | [فهم ماهية Linux: ما هو لينكس؟ وكيف يعمل؟](what-is-linux.html) | النواة، إدارة العمليات والذاكرة والعتاد | [شاهد الفيديو 📺](https://www.youtube.com/watch?v=hX2YySECa88) |
| **02** | [فهم كيف يختلف Linux عن الأنظمة الأخرى](linux-vs-other-os.html) | مقارنة مع ويندوز وماك، وفلسفة FOSS | [شاهد الفيديو 📺](https://www.youtube.com/watch?v=0EKHPkXOkPs) |
| **03** | [استكشاف تاريخ Linux](history-of-linux.html) | من UNIX و MINIX إلى رسالة تورفالدس 1991 | [شاهد الفيديو 📺](https://www.youtube.com/watch?v=S__Biw-Uqp8) |
| **04** | [ثقافة وفلسفة UNIX في Bell Labs](unix-philosophy.html) | الأدوات الصغيرة، الأنابيب، ولغة C | [شاهد الفيديو 📺](https://www.youtube.com/watch?v=vElO0pup3zI) |
| **05** | [تجارية UNIX: من مختبرات بيل لنظام تجاري](unix-commercialization.html) | تفكيك احتكار AT&T وظهور System V | [شاهد الفيديو 📺](https://www.youtube.com/watch?v=pfG5hVw3UmM) |
| **06** | [وصول Berkeley Software Distribution (BSD)](berkeley-software-distribution.html) | ولادة BSD، دور TCP/IP، وانقسام UNIX | [شاهد الفيديو 📺](https://www.youtube.com/watch?v=T7cdhddZ6r0) |
| **07** | [مختبر UNIX وتحول يونكس إلى مشروع تجاري](unix-laboratory.html) | قصة USL، معايير POSIX و SVID، ونشأة مسار Linux و FSF | [شاهد الفيديو 📺](https://www.youtube.com/watch?v=o6g7CbdUJ9A) |

---

## 🚀 المميزات التقنية للمنصة

* **تصميم عصري متجاوب بالكامل:** يدعم اللغة العربية (RTL) مع خط Cairo و JetBrains Mono.
* **الوضع الليلي والنهاري (Dark / Light Mode):** تبديل سلس مع حفظ التفضيل في `localStorage`.
* **فهرس محتويات تفاعلي جانبي (TOC):** وصول سريع لجميع فقرات ومحاور الدروس.
* **تحسين محركات البحث القياسي (Advanced SEO):**
  * وسوم Open Graph و Twitter Cards لمشاركة احترافية على منصات التواصل.
  * بيانات منظمة (Schema.org / JSON-LD) تتضمن `TechArticle` و `VideoObject` و `BreadcrumbList`.
  * خريطة موقع محدثة آلياً [sitemap.xml](sitemap.xml) مدعومة بخريطة بحث الفيديو (Google Video Search).
  * ملف توجيه الروبوتات [robots.txt](robots.txt).

---

## 🛠️ بنية المشروع ونظام الأتمتة (Build System)

الموقع مبني بنظام HTML ثابت (Static HTML) خفيف وسريع الاستجابة بدون أي اعتماديات ثقيلة، ومدعوم بنظام أتمتة داخلي مبني بلغة بايثون:

```text
Learn with me/
├── content/
│   ├── lessons.json             # سجل البيانات المركزي لكافة الدروس
│   └── lessons/                 # ملفات المحتوى بصيغة Markdown
│       └── lesson-06.md
├── templates/                   # القوالب القابلة لإعادة الاستخدام
│   ├── header.html              # شريط التنقل الموحد
│   ├── footer.html              # التذييل وسكربت الثيم
│   └── lesson_template.html     # القالب الرئيسي لصفحات الدروس
├── build.py                     # سكربت البناء والأتمتة السريع
├── style.css                    # ملف التنسيقات الرئيسي
├── index.html                   # الصفحة الرئيسية
├── linux-roadmap.html           # صفحة خارطة الطريق
├── sitemap.xml                  # خريطة الموقع
└── robots.txt                   # تعليمات محركات البحث
```

### تشغيل سكربت البناء

لتحديث القوائم والتذييلات وخريطة الموقع والصفحة الرئيسية وخارطة الطريق في جزء من الثانية:

```bash
python3 build.py
```

لإعادة بناء درس محدد من ملف Markdown الخاص به:

```bash
python3 build.py --compile 6
```

---

## 💻 التشغيل والمعاينة محلياً (Local Preview)

يمكنك معاينة الموقع على جهازك عبر أي خادم محلي خفيف:

```bash
# باستخدام بايثون المدمج
python3 -m http.server 8000
```
ثم افتح المتصفح على: `http://localhost:8000`

---

## 📦 سجل الإصدار (Release v1.0.0)

يمثل الإصدار **v1.0.0** الانطلاقة الرسمية للمنصة متضمنة:
* إطلاق أول 6 دروس تأسيسية ومعمارية في خارطة طريق لينكس مدعومة بالفيديوهات.
* إطلاق نظام القوالب والأتمتة الداخلي لتسريع وتسهيل نشر المحتوى.
* تكامل تام مع محركات البحث وتوافق 100% مع معايير الويب وسرعة التحميل.
* ربط النطاق المخصص `learn.jalalmahmoud.online` عبر GitHub Pages.

---

**حقوق النشر &copy; 2026 - Learn With Me**  
تطوير وإشراف: **جلال محمود**
