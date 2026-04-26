"""Localized content and route metadata for the Systemix website."""

from __future__ import annotations


SUPPORTED_LANGUAGES = ("en", "he")
DEFAULT_LANGUAGE = "en"
LANGUAGE_COOKIE_NAME = "preferred_language"
LANGUAGE_COOKIE_MAX_AGE = 60 * 60 * 24 * 365

PAGE_TEMPLATES = {
    "home": "home.html",
    "use_cases": "use_cases.html",
    "faq": "faq.html",
    "contact": "contact.html",
}

PAGE_PATHS = {
    "home": {"en": "/", "he": "/he"},
    "use_cases": {"en": "/use-cases", "he": "/he/use-cases"},
    "faq": {"en": "/faq", "he": "/he/faq"},
    "contact": {"en": "/contact", "he": "/he/contact"},
}

PATH_TO_PAGE_KEY = {
    localized_path: page_key
    for page_key, localized_paths in PAGE_PATHS.items()
    for localized_path in localized_paths.values()
}

COMMON_CONTENT = {
    "en": {
        "html_lang": "en",
        "direction": "ltr",
        "brand_name": "Systemix",
        "language_names": {"en": "English", "he": "Hebrew"},
        "language_switcher": "English/Hebrew",
        "nav": {
            "home": "Home",
            "use_cases": "Use Cases",
            "faq": "FAQ",
            "contact": "Contact",
        },
        "footer": {
            "summary": "AI-powered business automation for security-conscious teams.",
            "solutions": "Solutions",
            "faq": "Deployment FAQ",
            "contact_cta": "Start a Conversation",
        },
        "contact_form": {
            "name": "Name",
            "email": "Email",
            "company": "Company",
            "optional": "(optional)",
            "message": "What would you like to talk about?",
            "message_placeholder": "Tell us about the workflow, challenge, or meeting you want to set up.",
            "submit": "Request a Meeting",
            "submitting": "Submitting your inquiry...",
            "sending": "Sending...",
            "validation_name": "Please enter your name.",
            "validation_email": "Please enter a valid email address.",
            "validation_message": "Please share a bit more detail so we can understand the workflow.",
            "error_generic": "Unable to submit the form right now.",
            "success": "Thanks. We’ll review your request and respond shortly.",
            "invalid_submission": "Invalid submission.",
            "rate_limited": "Too many submissions. Please try again later.",
        },
    },
    "he": {
        "html_lang": "he",
        "direction": "rtl",
        "brand_name": "סיסטמיקס",
        "language_names": {"en": "English", "he": "עברית"},
        "language_switcher": "English/Hebrew",
        "nav": {
            "home": "בית",
            "use_cases": "מקרי שימוש",
            "faq": "שאלות נפוצות",
            "contact": "יצירת קשר",
        },
        "footer": {
            "summary": "אוטומציה עסקית מבוססת AI עבור צוותים שמציבים אבטחה ואמינות במקום הראשון.",
            "solutions": "פתרונות",
            "faq": "שאלות על פריסה",
            "contact_cta": "בואו נדבר",
        },
        "contact_form": {
            "name": "שם",
            "email": "אימייל",
            "company": "חברה",
            "optional": "(לא חובה)",
            "message": "על מה תרצו לדבר?",
            "message_placeholder": "ספרו לנו על התהליך, האתגר או סוג הפגישה שתרצו לקיים.",
            "submit": "בקשת פגישה",
            "submitting": "שולחים את הפנייה שלכם...",
            "sending": "שולח...",
            "validation_name": "נא להזין שם.",
            "validation_email": "נא להזין כתובת אימייל תקינה.",
            "validation_message": "ספרו לנו קצת יותר כדי שנבין את התהליך או האתגר.",
            "error_generic": "לא ניתן לשלוח את הטופס כרגע.",
            "success": "תודה. נעבור על הפנייה ונחזור אליכם בהקדם.",
            "invalid_submission": "הפנייה אינה תקינה.",
            "rate_limited": "נשלחו יותר מדי פניות. נסו שוב מאוחר יותר.",
        },
    },
}

PAGE_CONTENT = {
    "home": {
        "en": {
            "page_title": "Systemix | AI-Powered Business Automation",
            "page_description": "Systemix designs secure, reliable AI automation systems for modern business operations.",
            "eyebrow": "Enterprise AI Automation",
            "headline": "Systemix",
            "hero_subtitle": "AI-powered business automation built for measurable efficiency, operational resilience, and executive trust.",
            "hero_body": "We design automation systems that reduce repetitive workload, coordinate complex workflows, and create dependable operational capacity without sacrificing oversight.",
            "primary_cta": "Discuss Your Workflow",
            "secondary_cta": "Explore Use Cases",
            "metrics_label": "Business outcomes",
            "metrics": [
                {"value": "38%", "copy": "Average reduction in manual process time across orchestrated workflows."},
                {"value": "24/7", "copy": "Operational continuity for intake, triage, routing, and knowledge retrieval."},
                {"value": "100%", "copy": "Human visibility into critical automations, exceptions, and approvals."},
            ],
            "panel_label": "System Overview",
            "panel_title": "Reliable orchestration for business-critical processes",
            "panel_points": [
                "Multi-step workflow execution with exception handling",
                "Secure integrations across CRM, email, docs, and internal tools",
                "Audit-ready event trails and human approval checkpoints",
            ],
            "signal_tiles": [
                {"label": "Workflow State", "value": "Stable"},
                {"label": "Decision Layer", "value": "AI + Rules"},
                {"label": "Security Posture", "value": "Hardened"},
                {"label": "Operator Control", "value": "Visible"},
            ],
            "value_eyebrow": "Core Messaging",
            "value_title": "Automation that removes drag without introducing fragility",
            "value_cards": [
                {
                    "title": "Automating complex workflows",
                    "copy": "We map fragmented operational sequences into governed systems that classify, route, decide, and escalate with consistent behavior.",
                },
                {
                    "title": "Increasing efficiency",
                    "copy": "Systemix reduces queue time, handoff delays, and repetitive execution so teams can spend time where judgment matters most.",
                },
                {
                    "title": "Reducing operational cost",
                    "copy": "Automation is designed around cost-to-serve, resolution speed, and process quality so efficiency gains show up in real operations.",
                },
            ],
            "pillars_eyebrow": "Key Pillars",
            "pillars_title": "Built for organizations that need speed and certainty",
            "pillars": [
                {
                    "number": "01",
                    "title": "Smart AI Systems",
                    "copy": "Models are applied where they create leverage: triage, extraction, reasoning, drafting, and contextual decision support.",
                },
                {
                    "number": "02",
                    "title": "Secure by Design",
                    "copy": "We scope access tightly, preserve control points, and architect integrations to align with enterprise security expectations.",
                },
                {
                    "number": "03",
                    "title": "Reliable Execution",
                    "copy": "Every automation layer is shaped around predictable outcomes, fallback handling, and transparent operator oversight.",
                },
            ],
            "narrative_eyebrow": "Deployment Mindset",
            "narrative_title": "Serious systems for real environments",
            "narrative_copy": "Systemix is focused on applied AI for organizations that need stronger throughput, sharper response times, and dependable control over the systems carrying that work.",
            "narrative_link": "See how we approach security, rollout, and failure handling",
        },
        "he": {
            "page_title": "סיסטמיקס | אוטומציה עסקית מבוססת AI",
            "page_description": "סיסטמיקס מתכננת מערכות אוטומציה מבוססות AI באופן מאובטח, יציב ומדויק עבור פעילות עסקית מודרנית.",
            "eyebrow": "אוטומציה ארגונית מבוססת AI",
            "headline": "סיסטמיקס",
            "hero_subtitle": "אוטומציה עסקית מבוססת AI שנבנית כדי לייצר יעילות מדידה, חוסן תפעולי ואמון ניהולי.",
            "hero_body": "אנחנו מתכננים מערכות אוטומציה שמפחיתות עבודה ידנית חוזרת, מתאמות תהליכים מורכבים, ומייצרות יכולת תפעולית יציבה בלי לוותר על שליטה ובקרה.",
            "primary_cta": "בואו נדבר על התהליך שלכם",
            "secondary_cta": "למקרי השימוש",
            "metrics_label": "תוצאות עסקיות",
            "metrics": [
                {"value": "38%", "copy": "ירידה ממוצעת בזמן עבודה ידני בתהליכים שעברו אורקסטרציה."},
                {"value": "24/7", "copy": "רציפות תפעולית בקליטה, מיון, ניתוב ושליפת ידע."},
                {"value": "100%", "copy": "שקיפות אנושית מלאה באוטומציות קריטיות, חריגים ואישורים."},
            ],
            "panel_label": "מבט על המערכת",
            "panel_title": "אורקסטרציה אמינה לתהליכים עסקיים קריטיים",
            "panel_points": [
                "ביצוע תהליכים רב-שלביים עם טיפול בחריגים",
                "אינטגרציות מאובטחות ל-CRM, אימייל, מסמכים וכלים פנימיים",
                "תיעוד מלא לאודיט ונקודות אישור אנושיות",
            ],
            "signal_tiles": [
                {"label": "מצב התהליך", "value": "יציב"},
                {"label": "שכבת החלטה", "value": "AI + חוקים"},
                {"label": "מצב אבטחה", "value": "מוקשח"},
                {"label": "שליטת מפעיל", "value": "גלויה"},
            ],
            "value_eyebrow": "המסר המרכזי",
            "value_title": "אוטומציה שמסירה עומס בלי להכניס שבריריות",
            "value_cards": [
                {
                    "title": "אוטומציה לתהליכים מורכבים",
                    "copy": "אנחנו ממפים רצפים תפעוליים מפוצלים למערכות נשלטות שמסווגות, מנתבות, מחליטות ומסלימות באופן עקבי.",
                },
                {
                    "title": "שיפור יעילות",
                    "copy": "סיסטמיקס מקצרת זמני המתנה, מצמצמת עיכובי handoff ומפחיתה ביצוע חוזר כדי שהצוות יתמקד במה שבאמת דורש שיקול דעת.",
                },
                {
                    "title": "צמצום עלות תפעולית",
                    "copy": "האוטומציה נבנית סביב עלות שירות, מהירות פתרון ואיכות תהליך, כך שהשיפור ניכר בפעילות עצמה ולא רק במצגת.",
                },
            ],
            "pillars_eyebrow": "עמודי התווך",
            "pillars_title": "נבנה לארגונים שצריכים גם מהירות וגם ודאות",
            "pillars": [
                {
                    "number": "01",
                    "title": "מערכות AI חכמות",
                    "copy": "אנחנו מיישמים מודלים בדיוק היכן שהם מייצרים ערך: מיון, חילוץ מידע, ניתוח, ניסוח ותמיכה בקבלת החלטות בהקשר.",
                },
                {
                    "number": "02",
                    "title": "מאובטח כבר מהתכנון",
                    "copy": "אנחנו מצמצמים הרשאות, שומרים על נקודות שליטה, ובונים אינטגרציות בהתאם לדרישות האבטחה של ארגונים רציניים.",
                },
                {
                    "number": "03",
                    "title": "ביצוע שאפשר לסמוך עליו",
                    "copy": "כל שכבת אוטומציה מעוצבת סביב תוצאות צפויות, מנגנוני fallback ובקרה שקופה למפעילים.",
                },
            ],
            "narrative_eyebrow": "גישת ההטמעה",
            "narrative_title": "מערכות רציניות לסביבות אמיתיות",
            "narrative_copy": "סיסטמיקס מתמקדת ב-AI יישומי עבור ארגונים שצריכים יותר תפוקה, זמני תגובה חדים יותר ושליטה אמינה במערכות שנושאות את העבודה הזו.",
            "narrative_link": "כך אנחנו ניגשים לאבטחה, לעלייה לאוויר ולטיפול בכשלים",
        },
    },
    "use_cases": {
        "en": {
            "page_title": "Use Cases | Systemix",
            "page_description": "Explore practical AI automation use cases, from CRM orchestration to internal knowledge systems.",
            "eyebrow": "Use Cases & Projects",
            "headline": "Practical AI automation for high-friction business processes",
            "intro": "Each implementation is designed around a real operational bottleneck: reduce manual effort, shorten cycle time, and keep humans in control when exceptions matter.",
            "cases": [
                {
                    "eyebrow": "CRM Automation",
                    "title": "Unify lead intake, qualification, and routing",
                    "problem_label": "Problem",
                    "problem": "Sales teams lose time cleaning records, routing leads manually, and reconciling duplicate entries across inbound channels.",
                    "solution_label": "Solution",
                    "solution": "Systemix deploys an AI-assisted qualification layer that normalizes lead data, scores intent, updates CRM records, and routes priority opportunities automatically.",
                    "outcome_label": "Outcome",
                    "outcome": "Faster follow-up, cleaner records, and a shorter path from inbound inquiry to owner assignment with fewer dropped opportunities.",
                },
                {
                    "eyebrow": "Email Processing Agents",
                    "title": "Turn inbox volume into structured action",
                    "problem_label": "Problem",
                    "problem": "Operational teams spend hours reviewing, categorizing, and forwarding repetitive inbound email requests with inconsistent prioritization.",
                    "solution_label": "Solution",
                    "solution": "We implement inbox agents that classify requests, extract key fields, draft responses, create tickets, and escalate sensitive cases to the right human owner.",
                    "outcome_label": "Outcome",
                    "outcome": "Higher response speed, lower queue pressure, and more consistent service levels across repetitive inbound workflows.",
                },
                {
                    "eyebrow": "Knowledge Chatbot Systems",
                    "title": "Give teams trustworthy access to internal knowledge",
                    "problem_label": "Problem",
                    "problem": "Employees waste time searching across fragmented documentation, policies, and tribal knowledge when time-sensitive questions arise.",
                    "solution_label": "Solution",
                    "solution": "Systemix builds retrieval-backed knowledge assistants grounded in approved internal sources, with citation logic and escalation paths when confidence is low.",
                    "outcome_label": "Outcome",
                    "outcome": "Faster onboarding, shorter answer cycles, and more consistent policy interpretation without depending on a single expert.",
                },
                {
                    "eyebrow": "Internal Workflow Automation",
                    "title": "Coordinate multi-step operations across teams and tools",
                    "problem_label": "Problem",
                    "problem": "Approvals, handoffs, and recurring operations often span email, spreadsheets, chat, and line-of-business tools with low visibility and frequent delay.",
                    "solution_label": "Solution",
                    "solution": "We orchestrate event-driven flows that move work between systems, enforce approval checkpoints, and surface exceptions before they become operational drift.",
                    "outcome_label": "Outcome",
                    "outcome": "Less operational friction, clearer ownership, and a reliable execution layer for recurring business processes.",
                },
            ],
        },
        "he": {
            "page_title": "מקרי שימוש | סיסטמיקס",
            "page_description": "גלו מקרי שימוש פרקטיים לאוטומציה מבוססת AI, מאורקסטרציית CRM ועד מערכות ידע פנימיות.",
            "eyebrow": "מקרי שימוש ופרויקטים",
            "headline": "אוטומציית AI פרקטית לתהליכים עסקיים עם הרבה חיכוך",
            "intro": "כל הטמעה נבנית סביב צוואר בקבוק תפעולי אמיתי: להפחית עבודה ידנית, לקצר זמני מחזור, ולהשאיר בני אדם בשליטה כשחריגים באמת חשובים.",
            "cases": [
                {
                    "eyebrow": "אוטומציית CRM",
                    "title": "לאחד קליטת לידים, סינון וניתוב",
                    "problem_label": "האתגר",
                    "problem": "צוותי מכירות מאבדים זמן על ניקוי נתונים, ניתוב ידני של לידים והתמודדות עם כפילויות שמגיעות מערוצי כניסה שונים.",
                    "solution_label": "הפתרון",
                    "solution": "סיסטמיקס מטמיעה שכבת סינון מבוססת AI שמנרמלת נתוני לידים, מדרגת כוונת רכישה, מעדכנת רשומות ב-CRM ומנתבת הזדמנויות בעדיפות גבוהה אוטומטית.",
                    "outcome_label": "התוצאה",
                    "outcome": "מעקב מהיר יותר, נתונים נקיים יותר ודרך קצרה יותר מפנייה נכנסת להקצאת בעלים, עם פחות הזדמנויות שנופלות בין הכיסאות.",
                },
                {
                    "eyebrow": "סוכני עיבוד אימייל",
                    "title": "להפוך עומס בתיבת הדואר לפעולה מסודרת",
                    "problem_label": "האתגר",
                    "problem": "צוותים תפעוליים מבזבזים שעות על מעבר ידני על אימיילים חוזרים, קטלוג שלהם והעברה הלאה בלי סדר עדיפויות עקבי.",
                    "solution_label": "הפתרון",
                    "solution": "אנחנו מטמיעים סוכני inbox שמסווגים פניות, מחלצים שדות מרכזיים, מציעים מענה, פותחים קריאות ומסלימים מקרים רגישים לאדם הנכון.",
                    "outcome_label": "התוצאה",
                    "outcome": "זמן תגובה טוב יותר, פחות עומס תורי עבודה ורמת שירות עקבית יותר בתהליכי אימייל חוזרים.",
                },
                {
                    "eyebrow": "מערכות צ'אט-בוט לידע",
                    "title": "לתת לצוות גישה אמינה לידע הפנימי",
                    "problem_label": "האתגר",
                    "problem": "עובדים מבזבזים זמן בחיפוש בין מסמכים מפוזרים, נהלים וידע לא פורמלי כשעולות שאלות דחופות.",
                    "solution_label": "הפתרון",
                    "solution": "סיסטמיקס בונה עוזרי ידע מבוססי שליפה שמחוברים למקורות פנימיים מאושרים, עם ציטוטים ומסלולי הסלמה כשמידת הוודאות נמוכה.",
                    "outcome_label": "התוצאה",
                    "outcome": "חפיפה מהירה יותר, זמני תשובה קצרים יותר ופרשנות עקבית יותר לנהלים, בלי להיות תלויים במומחה אחד.",
                },
                {
                    "eyebrow": "אוטומציה לתהליכים פנימיים",
                    "title": "לתאם תהליכים מרובי שלבים בין צוותים וכלים",
                    "problem_label": "האתגר",
                    "problem": "אישורים, handoff-ים ופעולות שחוזרות על עצמן נפרשים לעיתים על אימייל, גיליונות, צ'אט וכלי ליבה עסקיים, עם מעט שקיפות והרבה עיכובים.",
                    "solution_label": "הפתרון",
                    "solution": "אנחנו מתזמרים תהליכים מונעי אירועים שמעבירים עבודה בין מערכות, שומרים על נקודות אישור ומציפים חריגים לפני שהם הופכים לסטייה תפעולית.",
                    "outcome_label": "התוצאה",
                    "outcome": "פחות חיכוך תפעולי, בעלות ברורה יותר ושכבת ביצוע אמינה לתהליכים עסקיים שחוזרים שוב ושוב.",
                },
            ],
        },
    },
    "faq": {
        "en": {
            "page_title": "FAQ | Systemix",
            "page_description": "Answers to practical questions about deployment, security, integrations, and AI system reliability.",
            "eyebrow": "FAQ",
            "headline": "Answers for teams evaluating applied AI in production",
            "intro": "These are the questions that matter in real deployments: security, integration scope, reliability, and how implementation behaves when conditions change.",
            "items": [
                {
                    "question": "What is an AI agent?",
                    "answer": "An AI agent is a software component that can interpret inputs, make bounded decisions, and take defined actions across your systems. In practice, it behaves like a governed workflow operator, not an unbounded autonomous actor.",
                },
                {
                    "question": "Is this secure?",
                    "answer": "Security is built into system design, not added later. Access is scoped to the minimum required level, sensitive actions can require explicit approval, and integrations are designed to preserve auditability and control.",
                },
                {
                    "question": "Can it integrate with our systems?",
                    "answer": "Yes. Most deployments connect to common business platforms such as CRMs, email systems, document repositories, ticketing tools, and internal databases. We design around your actual stack instead of forcing a generic workflow.",
                },
                {
                    "question": "What happens if the system fails?",
                    "answer": "Reliable systems include fallback behavior. We define exception handling, human escalation, retry logic, and visibility into failure states so the business process remains understandable and recoverable.",
                },
                {
                    "question": "How long does implementation take?",
                    "answer": "Timeline depends on process complexity and integration depth, but focused use cases often move from discovery to first production-ready workflow in a matter of weeks, not quarters. The priority is safe rollout, not rushed scope.",
                },
            ],
        },
        "he": {
            "page_title": "שאלות נפוצות | סיסטמיקס",
            "page_description": "תשובות לשאלות פרקטיות על הטמעה, אבטחה, אינטגרציות ואמינות של מערכות AI.",
            "eyebrow": "שאלות נפוצות",
            "headline": "תשובות לצוותים שבוחנים AI יישומי בסביבת ייצור",
            "intro": "אלה השאלות שבאמת חשובות בהטמעות אמיתיות: אבטחה, עומק האינטגרציה, אמינות ואיך המערכת מתנהגת כשהתנאים משתנים.",
            "items": [
                {
                    "question": "מהו סוכן AI?",
                    "answer": "סוכן AI הוא רכיב תוכנה שמסוגל לפרש קלטים, לקבל החלטות בתוך גבולות ברורים ולבצע פעולות מוגדרות במערכות שלכם. בפועל הוא מתנהג כמו מפעיל תהליך נשלט, לא כמו ישות אוטונומית בלי גבולות.",
                },
                {
                    "question": "האם זה מאובטח?",
                    "answer": "אבטחה נבנית כחלק מהתכנון, לא כתוספת מאוחרת. ההרשאות מצומצמות למינימום הנדרש, פעולות רגישות יכולות לדרוש אישור מפורש, והאינטגרציות מתוכננות כך שישמרו על בקרה ואפשרות לאודיט.",
                },
                {
                    "question": "האם זה יכול להשתלב עם המערכות שלנו?",
                    "answer": "כן. רוב ההטמעות מתחברות לפלטפורמות עסקיות נפוצות כמו CRM, מערכות אימייל, מאגרי מסמכים, כלי טיקטים ומאגרי מידע פנימיים. אנחנו מתכננים סביב הסטאק האמיתי שלכם ולא כופים תהליך גנרי.",
                },
                {
                    "question": "מה קורה אם המערכת נכשלת?",
                    "answer": "מערכות אמינות כוללות התנהגות fallback. אנחנו מגדירים טיפול בחריגים, הסלמה לאדם, לוגיקת retry ושקיפות למצבי כשל, כך שהתהליך העסקי יישאר מובן וניתן לשחזור.",
                },
                {
                    "question": "כמה זמן לוקחת ההטמעה?",
                    "answer": "משך הזמן תלוי במורכבות התהליך ובעומק האינטגרציה, אבל במקרי שימוש ממוקדים אפשר לעבור מגילוי לציר עבודה ראשון מוכן לייצור בתוך שבועות ולא רבעונים. העדיפות היא עלייה בטוחה לאוויר, לא ריצה מהירה מדי.",
                },
            ],
        },
    },
    "contact": {
        "en": {
            "page_title": "Contact | Systemix",
            "page_description": "Schedule a meeting with Systemix or contact us to discuss secure AI automation for your business.",
            "eyebrow": "Contact Systemix",
            "headline": "Set up a meeting and let’s map the right automation path.",
            "hero_subtitle": "Whether you’re exploring your first AI workflow or replacing fragile manual processes, we can help you identify the best place to start.",
            "hero_body": "Share the bottlenecks your team is dealing with, the systems involved, and the kind of outcome you want. We’ll use that to prepare a focused conversation around rollout options, operational fit, and where automation can create the most value.",
            "highlights_label": "Why reach out",
            "highlights": [
                {
                    "title": "Meeting-ready",
                    "copy": "Tell us your goals and we’ll shape the discussion around the workflows that matter most.",
                },
                {
                    "title": "Practical guidance",
                    "copy": "We can talk through automation opportunities, rollout risks, and what a secure implementation could look like.",
                },
                {
                    "title": "Clear next steps",
                    "copy": "You’ll leave with a sharper sense of scope, priorities, and whether Systemix is the right fit.",
                },
            ],
            "panel_label": "Start the conversation",
            "panel_title": "Book a meeting or send us a note.",
            "panel_copy": "If you already know the process you want to improve, include that in your message. If you’re still figuring it out, that’s fine too. We’re happy to start with the pain points and work backward from there.",
            "panel_points": [
                "Discovery calls around workflow automation and AI operations",
                "Discussions for teams evaluating security, oversight, and rollout complexity",
                "Early-stage conversations for companies that want a sensible first implementation",
            ],
        },
        "he": {
            "page_title": "יצירת קשר | סיסטמיקס",
            "page_description": "קבעו פגישה עם סיסטמיקס או צרו קשר כדי לדבר על אוטומציית AI מאובטחת לעסק שלכם.",
            "eyebrow": "צרו קשר עם סיסטמיקס",
            "headline": "קובעים פגישה וממפים יחד את מסלול האוטומציה הנכון.",
            "hero_subtitle": "בין אם אתם בוחנים תהליך AI ראשון ובין אם אתם מחליפים תהליכים ידניים שבירים, נוכל לעזור לכם לזהות את נקודת ההתחלה הנכונה.",
            "hero_body": "שתפו אותנו בצווארי הבקבוק שהצוות שלכם מתמודד איתם, במערכות שמעורבות ובתוצאה שאתם רוצים להשיג. על בסיס זה נבנה שיחה ממוקדת על אפשרויות הטמעה, התאמה תפעולית והמקום שבו אוטומציה יכולה לייצר הכי הרבה ערך.",
            "highlights_label": "למה לפנות אלינו",
            "highlights": [
                {
                    "title": "מוכנים לפגישה",
                    "copy": "ספרו לנו מה המטרות שלכם ואנחנו נכוון את השיחה לתהליכים שהכי חשובים לכם.",
                },
                {
                    "title": "הכוונה פרקטית",
                    "copy": "אפשר לדבר על הזדמנויות לאוטומציה, סיכוני הטמעה ואיך ייראה יישום מאובטח ונכון.",
                },
                {
                    "title": "צעדים הבאים ברורים",
                    "copy": "תצאו עם תמונה חדה יותר של ההיקף, סדרי העדיפויות והאם סיסטמיקס היא ההתאמה הנכונה.",
                },
            ],
            "panel_label": "פותחים את השיחה",
            "panel_title": "קבעו פגישה או שלחו לנו הודעה.",
            "panel_copy": "אם כבר ברור לכם איזה תהליך אתם רוצים לשפר, כתבו זאת בהודעה. ואם אתם עדיין מחדדים את הכיוון, גם זה בסדר גמור. אפשר להתחיל מכאבי העבודה וללכת אחורה עד להגדרת הפתרון.",
            "panel_points": [
                "שיחות discovery סביב אוטומציית תהליכים ו-AI תפעולי",
                "שיחות לצוותים שבוחנים אבטחה, בקרה ומורכבות rollout",
                "שיחות התחלתיות לחברות שרוצות הטמעה ראשונה הגיונית",
            ],
        },
    },
}
