function confirmBooking() {

    return confirm(
        "Are you sure you want to book this slot?"
    );
}


function confirmCancel() {

    return confirm(
        "Are you sure you want to cancel this booking?"
    );
}


document.addEventListener(
    "DOMContentLoaded",
    function () {

        const today =
            new Date().toISOString().split("T")[0];


        const dateInput =
            document.getElementById("dateInput");

        if (dateInput) {

            dateInput.setAttribute(
                "min",
                today
            );
        }


        const adminDate =
            document.getElementById("adminDate");

        if (adminDate) {

            adminDate.setAttribute(
                "min",
                today
            );
        }

    }
);
