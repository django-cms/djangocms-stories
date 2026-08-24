(function () {
    function findSelection(select) {
        /* Select2 inserts its container right after the <select>. */
        var container = select.nextElementSibling;
        while (container && !container.classList.contains("select2")) {
            container = container.nextElementSibling;
        }
        return container ? container.querySelector(".select2-selection__rendered") : null;
    }

    function initSortedAutocomplete(select) {
        /* Allow drag-and-drop sorting of a sorted select2 autocomplete widget. */
        var selection = findSelection(select);

        if (!selection || typeof Sortable === "undefined") {
            return;
        }

        if (selection.dataset.sortableInitialized === "true") {
            return;
        }

        selection.dataset.sortableInitialized = "true";

        function closeSelect2() {
            if (window.django && window.django.jQuery) {
                window.django.jQuery(select).select2("close");
                return;
            }
            document.querySelectorAll(".select2-container--open").forEach(function (element) {
                element.classList.remove("select2-container--open");
            });
        }

        function stampChipValues() {
            /* Chips and selected <option>s are in the same order until the user drags.
               Stamp each chip with its option value so we can recover it after reorder. */
            var chips = selection.querySelectorAll(".select2-selection__choice");
            var options = select.options;
            var count = Math.min(chips.length, options.length);
            for (var i = 0; i < count; i++) {
                chips[i].dataset.optionValue = options[i].value;
            }
        }

        new Sortable(selection, {
            animation: 150,
            draggable: ".select2-selection__choice",
            onStart: function () {
                stampChipValues();
                closeSelect2();
            },
            onSort: function () {
                var values = Array.from(selection.querySelectorAll(".select2-selection__choice"))
                    .map(function (chip) { return chip.dataset.optionValue; })
                    .filter(Boolean);

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
    }

    function initializeAll() {
        /* Select2 needs to be initialized before this code runs, so we wait a bit. */
        setTimeout(function () {
            document.querySelectorAll("select.sorted-autocomplete").forEach(initSortedAutocomplete);
        }, 50);
    }

    document.addEventListener("DOMContentLoaded", initializeAll);
})();
