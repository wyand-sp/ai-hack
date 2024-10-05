document.getElementById('submitBtn').addEventListener('click', function() {
    const excludeDomain = document.getElementById('excludeDomain').checked;
    const seconds = document.getElementById('secondsDropdown').value;

    console.log('Exclude Domain:', excludeDomain);
    console.log('Seconds After Storing:', seconds);
    // Add logic to store this config or send it to the background script here
    alert("Not implemented");
});