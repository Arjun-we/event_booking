// ─── EmailJS Configuration ────────────────────────────────────────────────────
// Two services: one per Gmail account connected in EmailJS dashboard
const EMAILJS_SERVICE_VENDOR   = 'service_9no3cy3';  // Vendor Gmail  (DEFAULT)
const EMAILJS_SERVICE_CUSTOMER = 'service_y5ldcxp';  // Customer Gmail
const EMAILJS_TEMPLATE_BOOKING = 'template_05e41mt'; // customer → vendor  (new booking)
const EMAILJS_TEMPLATE_CONFIRM = 'template_7xom01g'; // vendor   → customer (booking confirmed)

// ─── Wait for EmailJS to be ready ────────────────────────────────────────────
function waitForEmailJS(callback, maxAttempts = 10, attempt = 0) {
    if (typeof emailjs !== 'undefined') {
        callback();
    } else if (attempt < maxAttempts) {
        setTimeout(() => waitForEmailJS(callback, maxAttempts, attempt + 1), 500);
    } else {
        console.error('❌ EmailJS failed to load after multiple attempts');
    }
}

// ─── Generic send helper ──────────────────────────────────────────────────────
// Template variables used by BOTH templates:
//   {{to_email}}   → recipient address  (To Email field)
//   {{name}}       → sender's name      (used in body: "A message by {{name}}")
//   {{email}}      → sender's email     (Reply To field)
//   {{from_name}}  → sender's name      (From Name field)
//   {{message}}    → email body text
function _sendEmail(serviceId, templateId, toEmail, toName, fromEmail, fromName, message) {
    if (typeof emailjs === 'undefined') {
        console.error('❌ EmailJS not loaded.');
        return Promise.resolve(false);
    }

    // Validate email addresses before sending
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(toEmail)) {
        console.error('❌ Invalid recipient email:', toEmail);
        return Promise.resolve(false);
    }
    if (!emailRegex.test(fromEmail)) {
        console.error('❌ Invalid sender email:', fromEmail);
        return Promise.resolve(false);
    }

    // Match variable names exactly as defined in the EmailJS templates
    const emailParams = {
        to_email:  toEmail.trim().toLowerCase(),   // {{to_email}}  → To Email field
        name:      fromName,                        // {{name}}      → body: "A message by {{name}}"
        email:     fromEmail.trim().toLowerCase(),  // {{email}}     → Reply To field
        from_name: fromName,                        // {{from_name}} → From Name field
        message:   message                          // {{message}}   → body content
    };

    console.log('📤 Sending email via EmailJS...');
    console.log('   Service:',  serviceId);
    console.log('   Template:', templateId);
    console.log('   To:',       emailParams.to_email);
    console.log('   From:',     emailParams.email);

    return emailjs.send(serviceId, templateId, emailParams)
        .then(response => {
            console.log('✅ Email sent! Status:', response.status, response.text);
            return true;
        })
        .catch(error => {
            console.error('❌ Email failed!');
            console.error('   Status:', error.status);
            console.error('   Text:',   error.text);
            return false;
        });
}

// ─── Customer → Vendor: New Booking Notification ──────────────────────────────
// Uses Vendor Gmail service (service_9no3cy3) — sends from Vendor Gmail to vendor's inbox
function sendCustomerConfirmEmail(customerEmail, customerName, vendorEmail, vendorName) {
    const message = `${customerName} has just submitted a booking request for your services!\n\nCustomer Email: ${customerEmail}\n\nPlease log in to your dashboard to confirm or cancel this booking.`;
    return _sendEmail(EMAILJS_SERVICE_VENDOR, EMAILJS_TEMPLATE_BOOKING, vendorEmail, vendorName, customerEmail, customerName, message);
}

// ─── Vendor → Customer: Booking Confirmed Notification ───────────────────────
// Uses Customer Gmail service (service_y5ldcxp) — sends from Customer Gmail to customer's inbox
function sendVendorConfirmEmail(vendorEmail, vendorName, customerEmail, customerName) {
    const message = `Great news! ${vendorName} has confirmed your booking.\n\nVendor Email: ${vendorEmail}\n\nYour event is all set. Thank you for using Event Planner!`;
    return _sendEmail(EMAILJS_SERVICE_CUSTOMER, EMAILJS_TEMPLATE_CONFIRM, customerEmail, customerName, vendorEmail, vendorName, message);
}

// ─── Handle vendor Confirm button click ──────────────────────────────────────
function confirmVendorBooking(event, url, vendorName, vendorEmail, customerEmail, customerName) {
    event.preventDefault();
    console.log('🔔 Vendor confirm clicked');
    console.log('   Vendor:', vendorName, vendorEmail);
    console.log('   Customer:', customerName, customerEmail);

    if (!vendorEmail || !customerEmail) {
        console.warn('⚠️ Missing email addresses — redirecting without email');
        window.location.href = url;
        return;
    }

    sendVendorConfirmEmail(vendorEmail, vendorName, customerEmail, customerName)
        .then(() => {
            setTimeout(() => { window.location.href = url; }, 600);
        });
}

// ─── Page Load & Event Listeners ─────────────────────────────────────────────

// Auto-dismiss flash alerts
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(function () { alert.remove(); }, 500);
        }, 4000);
    });

    // Set min date for booking date inputs
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    dateInputs.forEach(function (input) {
        if (!input.getAttribute('min')) {
            input.setAttribute('min', today);
        }
    });
});
