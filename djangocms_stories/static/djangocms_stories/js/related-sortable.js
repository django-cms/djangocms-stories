(function () {
    function initializeRelatedSortable() {
        /* Allow drag-and-drop sorting of the related posts select2 widget. */
        /* Select2 needs to be initialized before this code runs, so we wait a bit after DOMContentLoaded. */
        setTimeout(() => {
            var selection = document.querySelector("#id_related + .select2 .select2-selection__rendered");
            var select = document.querySelector("#id_related");

            if (!selection || !select || typeof Sortable === "undefined") {
                return;
            }

            if (selection.dataset.sortableInitialized === "true") {
                return;
            }

            selection.dataset.sortableInitialized = "true";

            function closeRelatedSelect2() {
            if (window.django && window.django.jQuery) {
                window.django.jQuery(select).select2("close");
                return;
            }
            document.querySelectorAll(".select2-container--open").forEach(function (element) {
                element.classList.remove("select2-container--open");
            });
            }

            new Sortable(selection, {
                animation: 150,
                draggable: ".select2-selection__choice",
                onStart: function () {
                    closeRelatedSelect2();
                },
                onSort: function () {
                    var labels = Array.from(selection.querySelectorAll(".select2-selection__choice"))
                    .map(function (element) {
                        return element.getAttribute("title");
                    })
                    .filter(Boolean);

                    var options = Array.from(select.options);

                    labels.forEach(function (label) {
                    var option = options.find(function (candidate) {
                        return candidate.text === label;
                    });
                    if (option) {
                        select.appendChild(option);
                    }
                    });

                    select.dispatchEvent(new Event("change", { bubbles: true }));
                },
            });

        }, 50);
    }

    document.addEventListener("DOMContentLoaded", initializeRelatedSortable);
})();
