// Get access to the camera
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
   navigator.mediaDevices.getUserMedia({ video: true }).then(function (stream) {
      var video = document.getElementById('video');
      video.srcObject = stream;
      video.play();
   });
}

// Elements for taking the snapshot
var canvas = document.getElementById('canvas');
var context = canvas.getContext('2d');
var video = document.getElementById('video');
var snapButton = document.getElementById('snap');
var resultImg = document.getElementById('result');

// Trigger photo take
snapButton.addEventListener('click', function () {
   context.drawImage(video, 0, 0, 640, 480);
   var dataURL = canvas.toDataURL('image/jpeg');
   fetch('/upload_photo', {
      method: 'POST',
      headers: {
         'Content-Type': 'application/json'
      },
      body: JSON.stringify({ image: dataURL })
   })
      .then(response => response.json())
      .then(data => {
         resultImg.src = data.image;
         resultImg.style.display = 'block';
      });
});
