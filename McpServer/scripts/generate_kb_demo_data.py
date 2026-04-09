from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
KB_DIR = REPO_ROOT / "kb"


def write_seed_file(filename: str, records: Iterable[dict[str, object]]) -> None:
    path = KB_DIR / filename
    lines = [json.dumps(record, ensure_ascii=True) for record in records]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_account_and_login_records() -> list[dict[str, object]]:
    topics = [
        (
            "Reset password from the sign-in page",
            "Customers can select Forgot password on the sign-in page, enter the email on the account, and complete the emailed verification code before choosing a new password. Password reset links expire after 30 minutes.",
            ["account", "login", "password"],
        ),
        (
            "Unlock an account after repeated failed logins",
            "Accounts are locked for 15 minutes after five failed sign-in attempts in a row. Customers who need immediate access can unlock the account faster by completing a password reset.",
            ["account", "login", "security"],
        ),
        (
            "Update the email address on an account",
            "Customers can change the primary email from Profile Settings. The new email must be verified before it becomes the sign-in address, and order receipts continue going to the old address until verification is complete.",
            ["account", "profile", "email"],
        ),
        (
            "Turn on two-factor authentication",
            "Two-factor authentication can be enabled in Security Settings with an authenticator app or SMS. Backup codes should be downloaded and stored securely before leaving the page.",
            ["account", "security", "2fa"],
        ),
        (
            "Use backup codes when the authenticator app is unavailable",
            "Each account receives ten one-time backup codes when two-factor authentication is enabled. A used code cannot be reused, and customers can generate a fresh set after signing in.",
            ["account", "security", "2fa"],
        ),
        (
            "Sign in with Google or Apple",
            "Social sign-in only works when the Google or Apple email matches the email already stored on the Systemix account. If the email does not match, the customer should sign in with email and password first and link the provider from Settings.",
            ["account", "login", "sso"],
        ),
        (
            "Fix an endless sign-in redirect loop",
            "A redirect loop usually means the browser is blocking third-party cookies or an old session cookie is stuck. Clearing cookies for the store domain and retrying in a private window resolves most cases.",
            ["login", "browser", "troubleshooting"],
        ),
        (
            "Remove a saved payment method from the account",
            "Saved cards can be removed from Wallet after any pending orders finish authorization. Customers cannot delete the only payment method tied to an active subscription until a replacement method is added.",
            ["account", "wallet", "billing"],
        ),
        (
            "Manage delivery addresses in the address book",
            "Up to twenty shipping addresses can be stored in the address book. One address can be marked as default, and apartment or gate notes are saved per address for future orders.",
            ["account", "profile", "shipping"],
        ),
        (
            "Close an account permanently",
            "Permanent account closure removes saved addresses, stored payment tokens, and loyalty history after any open orders or refunds are complete. Customers should download invoices before submitting the closure request.",
            ["account", "privacy", "closure"],
        ),
    ]

    records: list[dict[str, object]] = []
    for index, (title, content, tags) in enumerate(topics, start=1):
        for variant in range(5):
            doc_number = ((index - 1) * 5) + variant + 1
            records.append(
                {
                    "doc_id": f"KB_ACC_{doc_number:03d}",
                    "title": title,
                    "category": "account_and_login",
                    "content": (
                        f"{content} "
                        f"Support note {variant + 1}: "
                        f"{account_support_notes(index, variant)}"
                    ),
                    "tags": tags,
                    "last_updated": f"2026-02-{((doc_number - 1) % 27) + 1:02d}",
                }
            )
    return records


def account_support_notes(topic_index: int, variant: int) -> str:
    notes = [
        "If the customer is traveling, ask them to confirm whether the login attempt came from a new country or network.",
        "Escalate only after verifying the latest confirmation email was delivered successfully and was not filtered to spam.",
        "If the account is shared across a household, confirm who changed the setting most recently before taking action.",
        "When identity documents are required, the review team typically responds within one business day.",
        "If the customer is on a managed corporate domain, advise them to check with the local IT administrator before unlinking sign-in providers.",
    ]
    return notes[(topic_index + variant - 1) % len(notes)]


def build_payment_records() -> list[dict[str, object]]:
    topics = [
        (
            "Accepted cards and digital wallets",
            "Systemix accepts Visa, Mastercard, American Express, Discover, PayPal, Apple Pay, and Google Pay in supported regions. Available methods at checkout depend on billing country and order total.",
            ["payments", "checkout"],
        ),
        (
            "Why a card payment was declined",
            "Card declines are usually caused by address verification mismatches, insufficient funds, card spending controls, or a temporary fraud block from the issuing bank. Customers can retry after confirming billing details.",
            ["payments", "cards", "troubleshooting"],
        ),
        (
            "Authorization holds on preorders",
            "Preorders place a temporary authorization on the payment method when the order is submitted, but the card is only captured when the item is ready to ship. The hold may refresh if the bank releases it before fulfillment.",
            ["payments", "preorder", "billing"],
        ),
        (
            "Download a VAT or tax invoice",
            "Invoices are available from Order History after the payment settles. Business customers can add a VAT or tax ID in Billing Settings so it appears automatically on future invoices.",
            ["payments", "invoice", "tax"],
        ),
        (
            "Use a gift card with another payment method",
            "Gift card balances are applied first and any remaining amount can be paid with an eligible card or wallet. Gift cards cannot be used to buy other gift cards or certain subscription renewals.",
            ["payments", "gift-card"],
        ),
        (
            "Pay in installments",
            "Installment offers appear at checkout only for qualifying carts, supported countries, and approved credit checks. The payment provider decides eligibility and repayment schedule.",
            ["payments", "installments", "checkout"],
        ),
        (
            "What to do when a refund has not reached the bank",
            "Once a refund is issued, card networks typically post it within five to seven business days, while digital wallets may appear sooner. The exact timing depends on the bank or wallet provider.",
            ["payments", "refunds", "timing"],
        ),
        (
            "Change the payment method on an unshipped order",
            "Customers cannot swap the payment method after the order enters warehouse processing. If the order is still in review, support can cancel it so the customer can place a new order with the preferred method.",
            ["payments", "orders", "billing"],
        ),
        (
            "Currency conversion at checkout",
            "Prices may be shown in a local currency estimate, but the final captured amount can still be processed in the store currency depending on the card network and region. The bank may apply a foreign transaction fee.",
            ["payments", "currency", "checkout"],
        ),
        (
            "Resolve duplicate charge concerns",
            "Two pending lines on a statement often mean one is an authorization hold and the other is the final captured charge. Customers should wait for pending items to settle before reporting a true duplicate charge.",
            ["payments", "cards", "billing"],
        ),
    ]

    records: list[dict[str, object]] = []
    for index, (title, content, tags) in enumerate(topics, start=1):
        for variant in range(5):
            doc_number = ((index - 1) * 5) + variant + 1
            records.append(
                {
                    "doc_id": f"KB_PAY_{doc_number:03d}",
                    "title": title,
                    "category": "payments",
                    "content": (
                        f"{content} "
                        f"Operations note {variant + 1}: "
                        f"{payment_support_notes(index, variant)}"
                    ),
                    "tags": tags,
                    "last_updated": f"2026-03-{((doc_number - 1) % 28) + 1:02d}",
                }
            )
    return records


def payment_support_notes(topic_index: int, variant: int) -> str:
    notes = [
        "If the order contains regulated batteries, some wallet methods may disappear because the carrier and region combination changes the payment mix.",
        "For subscription renewals, advise customers to update the payment method before the renewal date because retry windows are limited.",
        "A mismatch between shipping and billing country can trigger extra review even when the card is valid.",
        "When a business invoice is needed urgently, confirm the order status is paid rather than authorized.",
        "Gift card balances are shown in the original purchase currency and converted at checkout using the daily storefront rate.",
    ]
    return notes[(topic_index + variant - 1) % len(notes)]


def build_shipping_records() -> list[dict[str, object]]:
    topics = [
        (
            "Standard and expedited delivery windows",
            "Standard delivery normally arrives in three to five business days after dispatch, while expedited shipping usually arrives in one to two business days for in-stock items. Remote locations can take longer.",
            ["shipping", "delivery"],
        ),
        (
            "How to read tracking status updates",
            "Tracking statuses like label created, in transit, out for delivery, and delivery attempt each describe a different carrier milestone. A label created status alone does not mean the package has reached the carrier.",
            ["shipping", "tracking"],
        ),
        (
            "Change the shipping address after checkout",
            "Address changes are possible only before the order is released to the warehouse. Once picking starts, the package must usually be intercepted through the carrier or returned after delivery.",
            ["shipping", "orders", "address"],
        ),
        (
            "Split shipments for multi-item orders",
            "Large orders may ship in multiple boxes when items come from different warehouses or have different readiness dates. Each shipment receives its own tracking number and can arrive on different days.",
            ["shipping", "orders", "tracking"],
        ),
        (
            "Missing package marked as delivered",
            "Customers should first check building mailrooms, reception desks, parcel lockers, and nearby entrances before opening a claim. Delivery photos and GPS scans can help confirm the drop-off location.",
            ["shipping", "claims", "delivery"],
        ),
        (
            "Preorder release and dispatch timing",
            "Preorder items ship when inventory reaches the warehouse and all payment checks are complete. Release-day orders can still move in batches across several business days if volume is unusually high.",
            ["shipping", "preorder", "orders"],
        ),
        (
            "International customs and duties",
            "Customs duties and local taxes depend on the destination country, item value, and shipping service. Some routes collect duties at checkout while others require payment to the carrier before delivery.",
            ["shipping", "international", "customs"],
        ),
        (
            "Cancel or edit an order",
            "Orders can be canceled or edited only during the short review window after placement. Personalized items, same-day dispatch orders, and shipped orders cannot be edited.",
            ["orders", "shipping", "cancellation"],
        ),
        (
            "Backordered items in an order",
            "Backordered items reserve the customer’s place in line but do not always delay in-stock items. The storefront shows an updated estimated ship date as inventory becomes available.",
            ["orders", "inventory", "shipping"],
        ),
        (
            "Carrier delivery attempts and holds",
            "If delivery fails, the carrier may attempt redelivery or hold the parcel at a pickup point for several days. Unclaimed packages are usually returned to the warehouse and refunded after inspection.",
            ["shipping", "carrier", "delivery"],
        ),
    ]

    records: list[dict[str, object]] = []
    for index, (title, content, tags) in enumerate(topics, start=1):
        for variant in range(5):
            doc_number = ((index - 1) * 5) + variant + 1
            records.append(
                {
                    "doc_id": f"KB_SHIP_{doc_number:03d}",
                    "title": title,
                    "category": "shipping_and_orders",
                    "content": (
                        f"{content} "
                        f"Fulfillment note {variant + 1}: "
                        f"{shipping_support_notes(index, variant)}"
                    ),
                    "tags": tags,
                    "last_updated": f"2026-01-{((doc_number - 1) % 28) + 1:02d}",
                }
            )
    return records


def shipping_support_notes(topic_index: int, variant: int) -> str:
    notes = [
        "Weather alerts and carrier strikes can extend the estimate without changing the original checkout promise immediately.",
        "If the order includes lithium batteries, customers should expect an extra handoff scan before the parcel shows movement.",
        "Apartment delivery issues are reduced when the customer adds a buzzer code in the second address line.",
        "For business addresses, weekend delivery options may disappear even when the postal code supports Saturday service.",
        "If the package is held at customs for more than five business days, support should verify the consignee phone number on the shipment.",
    ]
    return notes[(topic_index + variant - 1) % len(notes)]


def build_returns_records() -> list[dict[str, object]]:
    topics = [
        (
            "Standard return window",
            "Most unopened products can be returned within 30 days of delivery for a refund to the original payment method. The item should include original accessories and packaging where possible.",
            ["returns", "policy"],
        ),
        (
            "Return policy for opened electronics",
            "Opened electronics can usually be returned within 14 days if they are in good condition, but missing accessories or cosmetic damage may reduce the refund. Warranty service applies after the return window closes.",
            ["returns", "electronics", "policy"],
        ),
        (
            "Refund timing after a return is delivered",
            "Once the return reaches the warehouse, inspection normally takes one to three business days. The refund is then issued, and banks usually post it within another five to seven business days.",
            ["refunds", "returns", "timing"],
        ),
        (
            "Items that cannot be returned",
            "Digital gift cards, downloadable content, hygiene products with broken seals, and personalized items are not eligible for standard returns unless they arrive defective or incorrect.",
            ["returns", "policy", "exceptions"],
        ),
        (
            "Exchange an item for a different size or color",
            "Direct exchanges are supported only in regions where the replacement item can be reserved immediately. If the preferred option is unavailable, the original order should be returned and reordered.",
            ["returns", "exchange", "orders"],
        ),
        (
            "Return shipping label instructions",
            "Customers can print a prepaid label from the returns portal when the order qualifies for seller-paid return shipping. The package should be dropped off before the label expiration date shown in the portal.",
            ["returns", "shipping", "labels"],
        ),
        (
            "Report a damaged or defective item",
            "Defective items should be reported with photos of the product, packaging, and shipping label within seven days of delivery. Support may offer troubleshooting, replacement parts, or a replacement order before requesting a return.",
            ["returns", "damage", "warranty"],
        ),
        (
            "Partial refunds and restocking fees",
            "Partial refunds may apply when returned items are incomplete, heavily used, or missing original accessories. Some opened premium electronics also carry a published restocking fee in supported regions.",
            ["refunds", "returns", "fees"],
        ),
        (
            "Return a gift order",
            "Gift recipients can start a return with the order number and shipping postal code, then receive store credit or an exchange without exposing the purchaser’s payment details.",
            ["returns", "gift-orders"],
        ),
        (
            "Late return exceptions",
            "Late returns are reviewed case by case for holiday extensions, documented carrier delays, or warranty-to-return conversions approved by support. Approval is not guaranteed after the standard window ends.",
            ["returns", "exceptions", "policy"],
        ),
    ]

    records: list[dict[str, object]] = []
    for index, (title, content, tags) in enumerate(topics, start=1):
        for variant in range(5):
            doc_number = ((index - 1) * 5) + variant + 1
            records.append(
                {
                    "doc_id": f"KB_RET_{doc_number:03d}",
                    "title": title,
                    "category": "returns_and_refunds",
                    "content": (
                        f"{content} "
                        f"Returns note {variant + 1}: "
                        f"{returns_support_notes(index, variant)}"
                    ),
                    "tags": tags,
                    "last_updated": f"2026-02-{((doc_number - 1) % 27) + 1:02d}",
                }
            )
    return records


def returns_support_notes(topic_index: int, variant: int) -> str:
    notes = [
        "If the return barcode does not scan at drop-off, the customer should request a manual acceptance receipt before leaving.",
        "Bundles refunded at the item level may reduce the promotional discount carried by the kept item.",
        "Luxury packaging can be omitted from a partial refund only if the accessory set remains complete.",
        "For gift returns, store credit is issued to a digital card tied to the recipient email address.",
        "Items replaced under warranty are not automatically eligible for a second return window unless local law requires it.",
    ]
    return notes[(topic_index + variant - 1) % len(notes)]


def build_product_usage_records() -> list[dict[str, object]]:
    products = [
        ("Smart Vacuum X2", "robot vacuum"),
        ("Smart Vacuum X2 Pro", "robot vacuum"),
        ("AirPure 360", "air purifier"),
        ("AirPure 360 Max", "air purifier"),
        ("HomeHub Mini", "smart home hub"),
        ("HomeHub Max", "smart home hub"),
        ("ThermaSense S4", "smart thermostat"),
        ("ThermaSense S4 Plus", "smart thermostat"),
        ("Doorbell Cam One", "video doorbell"),
        ("Doorbell Cam Pro", "video doorbell"),
        ("Outdoor Cam Lite", "security camera"),
        ("Outdoor Cam Flood", "security camera"),
        ("MopMate R1", "robot mop"),
        ("MopMate R1 Plus", "robot mop"),
        ("PetFeeder Connect", "automatic pet feeder"),
        ("PetFeeder Connect Duo", "automatic pet feeder"),
        ("SleepLight Halo", "smart sleep lamp"),
        ("SleepLight Halo Kids", "smart sleep lamp"),
        ("FitBand Pulse", "fitness tracker"),
        ("FitBand Pulse Pro", "fitness tracker"),
    ]
    scenarios = [
        (
            "initial setup",
            "To complete initial setup, open the Systemix mobile app, add the product, connect it to a 2.4 GHz Wi-Fi network if required, and wait for firmware verification to finish before closing the app.",
            ["setup", "mobile-app"],
        ),
        (
            "connectivity troubleshooting",
            "If the device goes offline, confirm the home router is broadcasting the expected band, move the product closer to the router for testing, and restart the device before removing it from the app.",
            ["troubleshooting", "wifi"],
        ),
        (
            "firmware update guidance",
            "Firmware updates should be installed while the device is plugged in or above the minimum battery threshold. The app displays release notes and prevents feature changes until the update completes.",
            ["firmware", "maintenance"],
        ),
        (
            "battery and charging behavior",
            "Charging times vary by model, but most units should rest on the dock or charger until the status light turns solid. Dirty charging contacts, cold rooms, and low-power USB adapters can slow the charge.",
            ["battery", "charging"],
        ),
        (
            "app notifications and alerts",
            "Push notifications can be managed per device in the app. Customers can choose critical alerts only, all alerts, or scheduled quiet hours so routine notifications pause overnight.",
            ["mobile-app", "notifications"],
        ),
        (
            "cleaning and routine maintenance",
            "Regular maintenance keeps the product accurate and quiet. Filters, brushes, water tanks, lenses, or sensors should be cleaned using the instructions for the specific model and only with approved materials.",
            ["maintenance", "care"],
        ),
        (
            "voice assistant integration",
            "Voice assistant setup requires linking the Systemix account to the supported assistant platform and granting the requested device permissions. Device nicknames should be short and distinct for better recognition.",
            ["integration", "voice"],
        ),
        (
            "privacy and data controls",
            "Privacy controls in the app let customers review cloud recording settings, telemetry sharing, and device-level permissions. Some diagnostics must remain enabled for remote troubleshooting and safety alerts.",
            ["privacy", "settings"],
        ),
        (
            "performance optimization tips",
            "Performance improves when the product is placed according to the setup guide, the app stays current, and environmental conditions stay within the supported temperature and humidity range listed for the model.",
            ["optimization", "best-practices"],
        ),
        (
            "factory reset steps",
            "A factory reset should be used only after basic troubleshooting fails because it clears local preferences and may require the device to be paired again. Customers should remove the product from the app only after the reset starts.",
            ["troubleshooting", "reset"],
        ),
    ]

    records: list[dict[str, object]] = []
    for product_index, (product_name, product_family) in enumerate(products, start=1):
        for scenario_index, (scenario_name, content, tags) in enumerate(scenarios, start=1):
            doc_number = ((product_index - 1) * len(scenarios)) + scenario_index
            records.append(
                {
                    "doc_id": f"KB_PROD_{doc_number:03d}",
                    "title": f"{product_name} - {scenario_name.title()}",
                    "category": "product_usage",
                    "content": (
                        f"{product_name} is a {product_family}. {content} "
                        f"Model-specific note: {product_specific_note(product_name, scenario_index)}"
                    ),
                    "tags": ["product_usage", product_family.replace(' ', "-"), *tags],
                    "last_updated": f"2026-03-{((doc_number - 1) % 28) + 1:02d}",
                }
            )
    return records


def product_specific_note(product_name: str, scenario_index: int) -> str:
    notes = [
        f"{product_name} keeps the previous room, schedule, or comfort profile data in the cloud until the customer removes the device from the app.",
        f"{product_name} may take up to ten minutes to appear as online after the first firmware sync finishes.",
        f"{product_name} works best when accessories and consumables are genuine Systemix parts sized for the exact model.",
        f"{product_name} should not be reset while a recording, cleaning cycle, dispensing schedule, or guided calibration is in progress.",
        f"{product_name} surfaces advanced settings only after the mobile app confirms the customer is signed in as the device owner.",
    ]
    return notes[(scenario_index - 1) % len(notes)]


def build_bad_docs_records() -> list[dict[str, object]]:
    return [
        {
            "doc_id": "KB_BAD_001",
            "title": "Outdated promotional return policy",
            "category": "bad_docs",
            "content": "Promotional items are always non-returnable, even when they arrive damaged. This statement is outdated and should never be used for customer support.",
            "tags": ["deprecated", "returns"],
            "last_updated": "2025-12-01",
        },
        {
            "doc_id": "KB_BAD_002",
            "title": "Conflicting delivery promise",
            "category": "bad_docs",
            "content": "Every international order arrives within two business days. This statement conflicts with current carrier and customs rules and exists only as a negative example.",
            "tags": ["deprecated", "shipping"],
            "last_updated": "2025-12-15",
        },
        {
            "doc_id": "KB_BAD_003",
            "title": "Incorrect password lockout threshold",
            "category": "bad_docs",
            "content": "Accounts lock after three failed sign-in attempts. This was superseded by the five-attempt policy and should not be seeded into the live knowledge base.",
            "tags": ["deprecated", "account"],
            "last_updated": "2025-11-20",
        },
    ]


def main() -> None:
    KB_DIR.mkdir(exist_ok=True)
    write_seed_file("account_and_login.txt", build_account_and_login_records())
    write_seed_file("payments.txt", build_payment_records())
    write_seed_file("shipping_and_orders.txt", build_shipping_records())
    write_seed_file("returns_and_refunds.txt", build_returns_records())
    write_seed_file("product_usage.txt", build_product_usage_records())
    write_seed_file("bad_docs.txt", build_bad_docs_records())


if __name__ == "__main__":
    main()
