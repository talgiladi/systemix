const modal = document.querySelector("[data-contact-modal]");
const openButtons = document.querySelectorAll("[data-open-contact]");
const closeButton = document.querySelector("[data-close-contact]");
const form = document.querySelector("[data-contact-form]");
const feedback = document.querySelector("[data-form-feedback]");

const setFeedback = (message, state) => {
    if (!feedback) {
        return;
    }
    feedback.textContent = message;
    feedback.classList.remove("is-error", "is-success");
    if (state) {
        feedback.classList.add(state);
    }
};

const openModal = () => {
    if (!modal) {
        return;
    }
    modal.hidden = false;
    document.body.classList.add("modal-open");
    const firstField = modal.querySelector("input, textarea");
    if (firstField) {
        firstField.focus();
    }
};

const closeModal = () => {
    if (!modal) {
        return;
    }
    modal.hidden = true;
    document.body.classList.remove("modal-open");
};

openButtons.forEach((button) => {
    button.addEventListener("click", openModal);
});

if (closeButton) {
    closeButton.addEventListener("click", closeModal);
}

if (modal) {
    modal.addEventListener("click", (event) => {
        if (event.target === modal) {
            closeModal();
        }
    });
}

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && modal && !modal.hidden) {
        closeModal();
    }
});

const validateForm = (formData) => {
    const name = formData.get("name")?.toString().trim() || "";
    const email = formData.get("email")?.toString().trim() || "";
    const message = formData.get("message")?.toString().trim() || "";
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (name.length < 2) {
        return "Please enter your name.";
    }
    if (!emailPattern.test(email)) {
        return "Please enter a valid email address.";
    }
    if (message.length < 20) {
        return "Please share a bit more detail so we can understand the workflow.";
    }
    return "";
};

if (form) {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const formData = new FormData(form);
        const validationError = validateForm(formData);

        if (validationError) {
            setFeedback(validationError, "is-error");
            return;
        }

        const submitButton = form.querySelector(".form-submit");
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = "Sending...";
        }

        setFeedback("Submitting your inquiry...", "");

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

            setFeedback(payload.message, "is-success");
            form.reset();
            window.setTimeout(() => {
                closeModal();
                setFeedback("", "");
            }, 1200);
        } catch (error) {
            setFeedback(error.message || "Unable to submit the form right now.", "is-error");
        } finally {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = "Send Inquiry";
            }
        }
    });
}
