const forms = document.querySelectorAll("[data-contact-form]");

const setFeedback = (form, message, state) => {
    const feedback = form.querySelector("[data-form-feedback]");
    if (!feedback) {
        return;
    }
    feedback.textContent = message;
    feedback.classList.remove("is-error", "is-success");
    if (state) {
        feedback.classList.add(state);
    }
};

const validateForm = (form, formData) => {
    const name = formData.get("name")?.toString().trim() || "";
    const email = formData.get("email")?.toString().trim() || "";
    const message = formData.get("message")?.toString().trim() || "";
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (name.length < 2) {
        return form.dataset.validationName || "Please enter your name.";
    }
    if (!emailPattern.test(email)) {
        return form.dataset.validationEmail || "Please enter a valid email address.";
    }
    if (message.length < 20) {
        return form.dataset.validationMessage || "Please share a bit more detail so we can understand the workflow.";
    }
    return "";
};

forms.forEach((form) => {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const formData = new FormData(form);
        const validationError = validateForm(form, formData);

        if (validationError) {
            setFeedback(form, validationError, "is-error");
            return;
        }

        const submitButton = form.querySelector(".form-submit");
        const idleLabel = submitButton?.dataset.idleLabel || submitButton?.textContent || "Send Inquiry";
        const loadingLabel = submitButton?.dataset.loadingLabel || "Sending...";
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = loadingLabel;
        }

        setFeedback(form, form.dataset.statusSubmitting || "Submitting your inquiry...", "");

        try {
            const response = await fetch("/contact", {
                method: "POST",
                body: formData,
                headers: {
                    Accept: "application/json",
                },
            });

            const payload = await response.json();
            if (!response.ok) {
                throw new Error(payload.detail || "Something went wrong. Please try again.");
            }

            setFeedback(form, payload.message, "is-success");
            form.reset();
        } catch (error) {
            setFeedback(form, error.message || form.dataset.errorGeneric || "Unable to submit the form right now.", "is-error");
        } finally {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = idleLabel;
            }
        }
    });
});
