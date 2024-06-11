document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("nextButton").addEventListener("click", function() {
        var name = document.getElementById("name").value.trim();
        var phone = document.getElementById("phone").value.trim();
        if (name === "" || phone === "") {
            alert("Please provide your name and phone number.");
        } else {
            // Navigate to the camera page
            window.location.href = "camera.html";
        }
    });

    document.getElementById("termsLink").addEventListener("click", function(event) {
        event.preventDefault();
        document.getElementById("termsPopup").classList.remove("hidden");
    });

    document.getElementById("closePopupButton").addEventListener("click", function() {
        document.getElementById("termsPopup").classList.add("hidden");
    });
});
