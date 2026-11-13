/* ==========================================================================
   THE UNCHARTED ROUTE
   Animations
   ========================================================================== */

(function () {
    "use strict";


    document.addEventListener(
        "DOMContentLoaded",
        function () {

            initScrollAnimations();
            initStaggeredAnimations();

        }
    );


    /* ======================================================================
       Scroll Reveal
       ====================================================================== */

    function initScrollAnimations() {

        const elements =
            document.querySelectorAll(
                "[data-reveal]"
            );

        if (!elements.length) {
            return;
        }


        if (
            !("IntersectionObserver" in window)
        ) {

            elements.forEach(
                function (element) {

                    element.classList.add(
                        "is-visible"
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

                            entry.target.classList.add(
                                "is-visible"
                            );

                            observer.unobserve(
                                entry.target
                            );

                        }
                    );

                },
                {
                    threshold: 0.12,
                    rootMargin: "0px 0px -40px 0px"
                }
            );


        elements.forEach(
            function (element) {

                observer.observe(element);

            }
        );

    }


    /* ======================================================================
       Staggered Elements
       ====================================================================== */

    function initStaggeredAnimations() {

        const groups =
            document.querySelectorAll(
                "[data-stagger]"
            );

        if (!groups.length) {
            return;
        }


        groups.forEach(
            function (group) {

                const children =
                    group.querySelectorAll(
                        "[data-stagger-item]"
                    );

                children.forEach(
                    function (child, index) {

                        child.style.setProperty(
                            "--route-stagger-delay",
                            `${index * 80}ms`
                        );

                        child.classList.add(
                            "route-stagger-item"
                        );

                    }
                );

            }
        );

    }

})();