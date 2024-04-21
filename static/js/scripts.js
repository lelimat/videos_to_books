document.getElementById('processForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission
    document.getElementById('loader').style.display = 'block';
    
    const formData = new FormData(this);
    fetch('/start_process', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        document.getElementById('loader').style.display = 'none';
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('loader').style.display = 'none';
    });
});


function addInput() {
    var container = document.getElementById("inputContainer");
    container.innerHTML += '<div class="control has-icons-left"> \
                                <input type="text" name="link[]" oninput="validateUrl()" placeholder="Enter URL ( youtube.com/... or youtu.be/...)"> \
                                <input type="number" name="start_hour[]" placeholder="hh" min="0" max="23"> \
                                <input type="number" name="start_minute[]" placeholder="mm" min="0" max="59"> \
                                <input type="number" name="start_second[]" placeholder="ss" min="0" max="59"> \
                                <input type="number" name="end_hour[]" placeholder="hh" min="0" max="23"> \
                                <input type="number" name="end_minute[]" placeholder="mm" min="0" max="59"> \
                                <input type="number" name="end_second[]" placeholder="ss" min="0" max="59"><br> \
                                <br> \
                                <span class="icon is-small is-left"> \
                                    <i class="fas fa-link"></i> \
                                </span> \
                            </div>';
}

function validateTimes() {
    var startHours = document.getElementsByName('start_hour[]');
    var startMinutes = document.getElementsByName('start_minute[]');
    var startSeconds = document.getElementsByName('start_second[]');
    var endHours = document.getElementsByName('end_hour[]');
    var endMinutes = document.getElementsByName('end_minute[]');
    var endSeconds = document.getElementsByName('end_second[]');

    for (var i = 0; i < startHours.length; i++) {
        var startTime = startHours[i].value * 3600 + startMinutes[i].value * 60 + startSeconds[i].value;
        var endTime = endHours[i].value * 3600 + endMinutes[i].value * 60 + endSeconds[i].value;

        if (endTime < startTime) {
            alert("End time must be greater than or equal to start time.");
            return false;
        }
    }
    return true;
}

function isValidYoutubeVideoUrl(url) {
    const regex = /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)[a-zA-Z0-9_-]{11}$/;
    return regex.test(url);
}

function validateUrl() {
    var url = document.getElementById('youtubeUrl').value;
    var message = isValidYoutubeVideoUrl(url) ? "Valid YouTube Video URL" : "Invalid YouTube Video URL";
    document.getElementById('result').textContent = message;
}
