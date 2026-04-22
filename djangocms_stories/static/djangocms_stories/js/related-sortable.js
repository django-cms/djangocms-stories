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
                    var $jq = window.django && window.django.jQuery;
                    var chips = Array.from(selection.querySelectorAll(".select2-selection__choice"));
                    var values = chips
                        .map(function (chip) {
                            var data = $jq ? $jq(chip).data("data") : null;
                            return data ? String(data.id) : null;
                        })
                        .filter(function (v) { return v !== null; });

                    var optionsByValue = {};
                    Array.from(select.options).forEach(function (option) {
                        optionsByValue[option.value] = option;
                    });

                    values.forEach(function (value) {
                        var option = optionsByValue[value];
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
