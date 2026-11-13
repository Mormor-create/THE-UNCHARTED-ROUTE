/* ==========================================================================
   THE UNCHARTED ROUTE
   Gallery
   ========================================================================== */

(function () {
    "use strict";


    document.addEventListener(
        "DOMContentLoaded",
        function () {

            initGalleryFilters();
            initLightbox();

        }
    );


    /* ======================================================================
       Gallery Filters
       ====================================================================== */

    function initGalleryFilters() {

        const filters =
            document.querySelectorAll(
                "[data-gallery-filter]"
            );

        const items =
            document.querySelectorAll(
                "[data-gallery-item]"
            );

        if (
            !filters.length ||
            !items.length
        ) {
            return;
        }


        filters.forEach(
            function (filter) {

                filter.addEventListener(
                    "click",
                    function () {

                        const category =
                            filter.dataset.galleryFilter;


                        filters.forEach(
                            function (button) {

                                button.classList.remove(
                                    "active"
                                );

                            }
                        );


                        filter.classList.add(
                            "active"
                        );


                        items.forEach(
                            function (item) {

                                const itemCategory =
                                    item.dataset.galleryCategory;


                                if (
                                    category === "all" ||
                                    itemCategory === category
                                ) {

                                    item.classList.remove(
                                        "hidden"
                                    );

                                } else {

                                    item.classList.add(
                                        "hidden"
                                    );

                                }

                            }
                        );

                    }
                );

            }
        );

    }


    /* ======================================================================
       Lightbox
       ====================================================================== */

    function initLightbox() {

        const galleryImages =
            document.querySelectorAll(
                "[data-lightbox]"
            );

        if (!galleryImages.length) {
            return;
        }


        let currentIndex = 0;


        const lightbox =
            document.createElement("div");

        lightbox.className =
            "route-lightbox";


        lightbox.innerHTML = `
            <div class="route-lightbox-backdrop"></div>

            <div
                class="route-lightbox-content"
                role="dialog"
                aria-modal="true"
                aria-label="Image viewer"
            >

                <button
                    type="button"
                    class="route-lightbox-close"
                    aria-label="Close image viewer"
                >
                    &times;
                </button>

                <button
                    type="button"
                    class="route-lightbox-prev"
                    aria-label="Previous image"
                >
                    &#10094;
                </button>

                <img
                    class="route-lightbox-image"
                    src=""
                    alt=""
                >

                <button
                    type="button"
                    class="route-lightbox-next"
                    aria-label="Next image"
                >
                    &#10095;
                </button>

                <div
                    class="route-lightbox-caption"
                ></div>

            </div>
        `;


        document.body.appendChild(
            lightbox
        );


        const image =
            lightbox.querySelector(
                ".route-lightbox-image"
            );

        const caption =
            lightbox.querySelector(
                ".route-lightbox-caption"
            );

        const closeButton =
            lightbox.querySelector(
                ".route-lightbox-close"
            );

        const previousButton =
            lightbox.querySelector(
                ".route-lightbox-prev"
            );

        const nextButton =
            lightbox.querySelector(
                ".route-lightbox-next"
            );

        const backdrop =
            lightbox.querySelector(
                ".route-lightbox-backdrop"
            );


        function showImage(index) {

            if (!galleryImages.length) {
                return;
            }


            if (index < 0) {
                index =
                    galleryImages.length - 1;
            }


            if (
                index >=
                galleryImages.length
            ) {
                index = 0;
            }


            currentIndex = index;


            const galleryImage =
                galleryImages[currentIndex];


            const source =
                galleryImage.dataset.lightbox ||
                galleryImage.src;


            const alt =
                galleryImage.getAttribute(
                    "alt"
                ) || "";


            const imageCaption =
                galleryImage.dataset.caption ||
                alt;


            image.src = source;

            image.alt = alt;

            caption.textContent =
                imageCaption;

        }


        function openLightbox(index) {

            showImage(index);

            lightbox.classList.add(
                "open"
            );

            document.body.classList.add(
                "lightbox-open"
            );

        }


        function closeLightbox() {

            lightbox.classList.remove(
                "open"
            );

            document.body.classList.remove(
                "lightbox-open"
            );

            image.src = "";

        }


        galleryImages.forEach(
            function (galleryImage, index) {

                galleryImage.addEventListener(
                    "click",
                    function () {

                        openLightbox(index);

                    }
                );

            }
        );


        closeButton.addEventListener(
            "click",
            closeLightbox
        );


        backdrop.addEventListener(
            "click",
            closeLightbox
        );


        previousButton.addEventListener(
            "click",
            function () {

                showImage(
                    currentIndex - 1
                );

            }
        );


        nextButton.addEventListener(
            "click",
            function () {

                showImage(
                    currentIndex + 1
                );

            }
        );


        document.addEventListener(
            "keydown",
            function (event) {

                if (
                    !lightbox.classList.contains(
                        "open"
                    )
                ) {
                    return;
                }


                if (event.key === "Escape") {

                    closeLightbox();

                }


                if (event.key === "ArrowLeft") {

                    showImage(
                        currentIndex - 1
                    );

                }


                if (event.key === "ArrowRight") {

                    showImage(
                        currentIndex + 1
                    );

                }

            }
        );

    }

})();