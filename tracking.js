/** Shared conversion tracking for Sangkan Clean */
(function () {
    window.trackEvent = function (eventName, params) {
        if (typeof gtag === 'function') {
            gtag('event', eventName, params || {});
        }
    };

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('a[href^="tel:"]').forEach(function (el) {
            el.addEventListener('click', function () {
                trackEvent('click_phone', { event_category: 'contact' });
            });
        });

        document.querySelectorAll('a[href*="line.me"]').forEach(function (el) {
            el.addEventListener('click', function () {
                trackEvent('click_line', { event_category: 'contact' });
            });
        });

        var calcBtn = document.getElementById('serviceType');
        if (calcBtn) {
            calcBtn.addEventListener('change', function () {
                trackEvent('calculator_change', { event_category: 'engagement' });
            });
        }

        var quoteForm = document.getElementById('quoteForm');
        if (quoteForm) {
            quoteForm.addEventListener('submit', function () {
                trackEvent('quote_form_submit', { event_category: 'lead' });
            });
        }
    });
})();
