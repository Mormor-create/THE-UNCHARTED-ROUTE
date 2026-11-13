/* ==========================================================================
   THE UNCHARTED ROUTE
   Global Application JavaScript
   ========================================================================== */

(function () {
    "use strict";


    document.addEventListener(
        "DOMContentLoaded",
        function () {

            initDismissibleAlerts();
            initCurrentYear();
            initLazyImages();
            initSmoothAnchors();
            initFormLoadingStates();

        }
    );


    /* ======================================================================
       Dismissible Alerts
       ====================================================================== */

    function initDismissibleAlerts() {

        const alerts =
            document.querySelectorAll(
                "[data-dismissible]"
            );

        alerts.forEach(function (alert) {

            const closeButton =
                alert.querySelector(
                    "[data-dismiss]"
                );

            if (!closeButton) {
                return;
            }

            closeButton.addEventListener(
                "click",
                function () {

                    alert.style.opacity = "0";

                    alert.style.transform =
                        "translateY(-8px)";

                    setTimeout(
                        function () {

                            alert.remove();

                        },
                        200
                    );

                }
            );

        });

    }


    /* ======================================================================
       Current Year
       ====================================================================== */

    function initCurrentYear() {

        const yearElements =
            document.querySelectorAll(
                "[data-current-year]"
            );

        const currentYear =
            new Date().getFullYear();

        yearElements.forEach(
            function (element) {

                element.textContent =
                    currentYear;

            }
        );

    }


    /* ======================================================================
       Lazy Images
       ====================================================================== */

    function initLazyImages() {

        const images =
            document.querySelectorAll(
                "img[data-src]"
            );

        if (!images.length) {
            return;
        }


        if (
            !("IntersectionObserver" in window)
        ) {

            images.forEach(
                function (image) {

                    image.src =
                        image.dataset.src;

                    image.removeAttribute(
                        "data-src"
                    );

                }
            );

            return;
        }


        const observer =
            new IntersectionObserver(
                function (entries, observer) {

                    entries.forEach(
                        function (entry) {

                            if (
                                !entry.isIntersecting
                            ) {
                                return;
                            }

                            const image =
                                entry.target;

                            image.src =
                                image.dataset.src;

                            image.removeAttribute(
                                "data-src"
                            );

                            observer.unobserve(
                                image
                            );

                        }
                    );

                },
                {
                    rootMargin: "200px"
                }
            );


        images.forEach(
            function (image) {

                observer.observe(image);

            }
        );

    }


    /* ======================================================================
       Smooth Anchor Scrolling
       ====================================================================== */

    function initSmoothAnchors() {

        const anchors =
            document.querySelectorAll(
                'a[href^="#"]'
            );

        anchors.forEach(function (anchor) {

            anchor.addEventListener(
                "click",
                function (event) {

                    const targetId =
                        anchor.getAttribute(
                            "href"
                        );

                    if (
                        !targetId ||
                        targetId === "#"
                    ) {
                        return;
                    }

                    const target =
                        document.querySelector(
                            targetId
                        );

                    if (!target) {
                        return;
                    }

                    event.preventDefault();

                    target.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });

                }
            );

        });

    }


    /* ======================================================================
       Form Loading States
       ====================================================================== */

    function initFormLoadingStates() {

        const forms =
            document.querySelectorAll(
                "form[data-loading-form]"
            );

        forms.forEach(function (form) {

            form.addEventListener(
                "submit",
                function () {

                    const submitButton =
                        form.querySelector(
                            'button[type="submit"], input[type="submit"]'
                        );

                    if (!submitButton) {
                        return;
                    }

                    submitButton.disabled = true;

                    submitButton.dataset.originalText =
                        submitButton.textContent;

                    if (
                        submitButton.tagName ===
                        "BUTTON"
                    ) {

                        submitButton.textContent =
                            "Sending...";

                    }

                }
            );

        });

    }

})();