function goBack() {
    window.history.back();
}

function copyToClipboard() {
    var copyText = document.getElementById("eventShareLink");
    copyText.select();
    copyText.setSelectionRange(0, 99999);
    document.execCommand("copy");
    alert("Copied the link: " + copyText.value);
}

function aos_init() {
    AOS.init({
        duration: 800,
        easing: 'slide',
        once: true,
        mirror: false
    });
}
window.addEventListener('load', () => {
aos_init();
});
