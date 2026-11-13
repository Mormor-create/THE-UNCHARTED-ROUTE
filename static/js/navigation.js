/* ==========================================================================
   THE UNCHARTED ROUTE
   Navigation
   ========================================================================== */

(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        initMobileNavigation();
        initActiveNavigation();
    });


    /* ======================================================================
       Mobile Navigation
       ====================================================================== */

    function initMobileNavigation() {

        const menuButton =
            document.getElementById("mobile-menu-button");

        const mobileMenu =
            document.getElementById("mobile-menu");

        if (!menuButton || !mobileMenu) {
            return;
        }

        const menuLinks =
            mobileMenu.querySelectorAll("a");


        function openMenu() {

            mobileMenu.classList.remove("hidden");

            mobileMenu.classList.add("open");

            menuButton.setAttribute(
                "aria-expanded",
                "true"
            );

            menuButton.setAttribute(
                "aria-label",
                "Close navigation menu"
            );

            document.body.classList.add(
                "navigation-open"
            );
        }


        function closeMenu() {

            mobileMenu.classList.remove("open");

            mobileMenu.classList.add("hidden");

            menuButton.setAttribute(
                "aria-expanded",
                "false"
            );

            menuButton.setAttribute(
                "aria-label",
                "Open navigation menu"
            );

            document.body.classList.remove(
                "navigation-open"
            );
        }


        function toggleMenu() {

            const isOpen =
                menuButton.getAttribute(
                    "aria-expanded"
                ) === "true";

            if (isOpen) {
                closeMenu();
            } else {
                openMenu();
            }
        }


        menuButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                toggleMenu();
            }
        );


        /* Close when navigation link is selected */

        menuLinks.forEach(function (link) {

            link.addEventListener(
                "click",
                function () {

                    closeMenu();
                }
            );

        });


        /* Close when Escape is pressed */

        document.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Escape") {

                    const isOpen =
                        menuButton.getAttribute(
                            "aria-expanded"
                        ) === "true";

                    if (isOpen) {
                        closeMenu();
                    }
                }
            }
        );


        /* Close when clicking outside */

        document.addEventListener(
            "click",
            function (event) {

                const isOpen =
                    menuButton.getAttribute(
                        "aria-expanded"
                    ) === "true";

                if (!isOpen) {
                    return;
                }

                const clickedInsideMenu =
                    mobileMenu.contains(event.target);

                const clickedButton =
                    menuButton.contains(event.target);

                if (
                    !clickedInsideMenu &&
                    !clickedButton
                ) {
                    closeMenu();
                }
            }
        );


        /* Reset navigation when returning to desktop */

        window.addEventListener(
            "resize",
            function () {

                if (window.innerWidth >= 768) {
                    closeMenu();
                }
            }
        );

    }


    /* ======================================================================
       Active Navigation
       ====================================================================== */

    function initActiveNavigation() {

        const currentPath =
            window.location.pathname;

        const navigationLinks =
            document.querySelectorAll(
                "[data-nav-link]"
            );

        if (!navigationLinks.length) {
            return;
        }


        navigationLinks.forEach(function (link) {

            const href =
                link.getAttribute("href");

            if (!href) {
                return;
            }

            let linkPath;

            try {

                linkPath =
                    new URL(
                        href,
                        window.location.origin
                    ).pathname;

            } catch (error) {

                return;
            }


            if (
                linkPath === currentPath ||
                (
                    linkPath !== "/" &&
                    currentPath.startsWith(linkPath)
                )
            ) {

                link.classList.add("active");

                link.setAttribute(
                    "aria-current",
                    "page"
                );

            } else {

                link.classList.remove("active");

                link.removeAttribute(
                    "aria-current"
                );
            }

        });

    }

})();