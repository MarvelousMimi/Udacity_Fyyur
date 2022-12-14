$(document).ready(function() {
    "use strict";
    

    /**
     * @description Prevent characters or string aside number in phone number input field
     */
    $("#phone").on("keypress keyup blur", function (event) {
        $(this).val(
            $(this)
            .val()
            .replace(/[^\d].+/, "")
        );
        if (event.which < 48 || event.which > 57) {
            event.preventDefault();
        }
    });
});