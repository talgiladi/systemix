You are a senior full-stack engineer and UI/UX designer. Your task is to design and implement a production-ready website for a company called "Systemix".

## 🧭 OVERALL GOAL

Build a futuristic-looking but highly professional and trustworthy website for a company specializing in AI-driven automation systems for businesses.

The design must balance:

* Futuristic / AI-driven visuals
* Enterprise-grade trust and reliability
* Clean, minimal, non-gimmicky UX

Avoid anything that looks like a toy, template, or startup cliché.

---

## 🧱 TECHNICAL REQUIREMENTS

* Language: Python
* Framework: FastAPI (preferred) or Flask
* Frontend: HTML + CSS + minimal JavaScript (no heavy frameworks unless necessary)
* Structure:

  * Separate backend and frontend logic
  * Use templates (Jinja2 if Flask/FastAPI)
  * Modular, clean architecture

Project structure example:

* /app

  * main.py
  * routes/
  * services/
  * templates/
  * static/

    * css/
    * js/
    * media/

---

## 🎨 DESIGN REQUIREMENTS

### Style:

* Futuristic but serious (think enterprise AI, not sci-fi fantasy)
* Dark theme preferred (deep blues, blacks, subtle gradients)
* Smooth animations (no flashy transitions)
* Clean typography, high readability

### Background:

* Use subtle moving background GIFs or animations
* Themes should imply:

  * automation
  * data flow
  * networks
  * AI decision-making

DO NOT overload performance:

* Optimize GIF size or use CSS/JS animation alternatives if possible

---

## 📄 REQUIRED PAGES

### 1. Home Page (/)

Sections:

* Hero section:

  * Title: "Systemix"
  * Subtitle: AI-powered business automation
  * Short value proposition

* Core messaging:

  * Automating complex workflows
  * Increasing efficiency
  * Reducing operational cost

* Key pillars:

  * Smart AI Systems
  * Secure by Design
  * Reliable Execution

* Visual sections with animated background

---

### 2. Use Cases & Projects (/use-cases)

Include:

* Realistic business scenarios:

  * CRM automation
  * Email processing agents
  * Knowledge chatbot systems
  * Internal workflow automation

Each use case should include:

* Problem
* Solution
* Outcome (efficiency gain, cost reduction)

---

### 3. FAQ (/faq)

Include practical, business-oriented questions:

* What is an AI agent?
* Is this secure?
* Can it integrate with our systems?
* What happens if the system fails?
* How long does implementation take?

Answers should emphasize:

* reliability
* control
* security
* real-world deployment

---

## 📩 CONTACT FORM

Requirements:

* Present as:

  * floating button OR header link (not intrusive)
* Clicking opens modal or dedicated section

Fields:

* Name
* Email
* Company (optional)
* Message

On submit:

* Call a backend function:
  handle_contact_submission(name, email, company, message)

IMPORTANT:

* Do NOT implement this function logic
* Just define and call it

Include:

* basic validation
* clean UX feedback

---

## 🔐 SECURITY & QUALITY

* Sanitize all inputs
* Prevent basic injection attacks
* No inline unsafe JS
* Separate concerns properly
* Use environment config where needed

---

## ⚙️ ADDITIONAL FEATURES

* Responsive design (mobile + desktop)
* SEO-friendly structure
* Clean navigation bar
* Reusable components

Optional:

* Simple logging for requests
* Basic rate limiting placeholder

---

## 📦 OUTPUT REQUIREMENTS

Provide:

1. Full project structure
2. All Python backend code
3. HTML templates
4. CSS (well-organized)
5. Minimal JS
6. Instructions to run locally

Code must be:

* clean
* readable
* production-oriented (not demo-level)

---

## 🚫 WHAT TO AVOID

* No placeholder lorem ipsum
* No generic “AI will change the world” text
* No overuse of animations
* No heavy frontend frameworks unless absolutely needed

---

## 🎯 FINAL GOAL

The result should look like a company that:

* can handle enterprise clients
* builds serious systems
* understands AI deeply
* values reliability and security

Not a hackathon project.

Generate the full implementation.
