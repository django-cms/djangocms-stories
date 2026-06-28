/*
 * Progressive enhancement for the tag field: turn the plain <select multiple>
 * rendered by djangocms_stories.tag_autosuggest.TagAutoSuggest into a Select2
 * field with free tagging and AJAX-backed suggestions. Uses the jQuery/Select2
 * bundled with Django's admin. Replaces the django-taggit-autosuggest widget.
 */
(function () {
    "use strict";

    function initOne($, element) {
        var $el = $(element);
        if ($el.data("select2-initialised")) {
            return;
        }
        $el.data("select2-initialised", true);

        var options = {
            tags: true,
            tokenSeparators: [","],
            width: "element",
            placeholder: $el.data("placeholder") || "",
            allowClear: false,
            createTag: function (params) {
                var term = $.trim(params.term);
                if (term === "") {
                    return null;
                }
                return { id: term, text: term };
            }
        };

        var ajaxUrl = $el.data("ajax-url");
        if (ajaxUrl) {
            options.ajax = {
                url: ajaxUrl,
                dataType: "json",
                delay: 200,
                data: function (params) {
                    return { q: params.term };
                },
                processResults: function (data) {
                    return {
                        results: (data.results || []).map(function (name) {
                            return { id: name, text: name };
                        })
                    };
                }
            };
            options.minimumInputLength = 1;
        }

        $el.select2(options);
    }

    function init($, root) {
        // Skip the hidden inline empty-form template (its fields carry the
        // "__prefix__" placeholder); initialising it would clone a broken
        // Select2 into every newly added row.
        $(root || document)
            .find(".djangocms-stories-tag-autosuggest")
            .not("[name*=__prefix__]")
            .each(function () {
                initOne($, this);
            });
    }

    var $ = (window.django && window.django.jQuery) || window.jQuery;
    if (!$) {
        return;
    }
    $(function () {
        init($);

        // Django's admin dispatches "formset:added" (a native DOM event since
        // Django 4.1) whenever a new inline row is inserted. Upgrade any tag
        // field in the freshly added row, e.g. for inline admins.
        document.addEventListener("formset:added", function (event) {
            init($, event.target);
        });
    });
})();
