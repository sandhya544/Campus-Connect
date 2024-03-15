// script.js

// Function to close the alert after a delay
function closeAlertWithDelay() {
    setTimeout(function () {
        var alert = document.getElementById('myAlert');
        alert.style.transition = 'opacity 2s';
        alert.style.opacity = 0;
        setTimeout(function () {
            alert.style.display = 'none';
        }, 2000);
    }, 4000);
}

// Call the function when the DOM is ready
document.addEventListener("DOMContentLoaded", function () {
    closeAlertWithDelay();
});
