URL = window.URL || window.webkitURL;

let gumStream;
//This is a variable (stream) for getUserMedia()
var rec;
//obiekt dla biblioteki recorder.js
let input;
//MediaStreamAudioSourceNode we'll be recording
// shim for AudioContext when it's not avb.
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext = new AudioContext;
//new audio context to help with recording, what audio context do is a kind of "controlling" audio stream, i guess
var startButton = document.getElementById("startButton");
var stopButton = document.getElementById("stopButton");
//now I'm adding events to my buttons
startButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);

//now whole app will work based on 3 functions: start, stop recording and kinda post data to server

function startRecording(){
    console.log("Start button clicked");

    var constraints = {
        audio: true,
        video: false
    }
    //disabling the start button until we get a success or fail from getUserMedia
    startButton.disabled = true;
    stopButton.disabled = false;

    //What we generally need now is that user will allow us to use his microphone
    navigator.mediaDevices.getUserMedia(constraints).then(function(stream){
        console.log("getUserMedia() -> success. Stream created. Initializing recorder...");

        //again new AudioContext after mediastream is created
        audioContext = new AudioContext();

        //updating the "log" of measurement
        //document.getElementById("formats").innerHTML="Format: szybkosc probkowania: "+audioContext.sampleRate/1000+" kHz";

        //assign stream for later purposes
        gumStream = stream;

        //use the stream
        input = audioContext.createMediaStreamSource(stream);

        //creating the recorder.js object, for the measurement purposes, one channel is enough
        rec = new Recorder(input, {numChannels: 1});

        //start recording process
        rec.record();
        console.log("Recording started");

    }).catch(function (err) {
        //if record function fails, enable start button
        startButton.disabled = false;
        stopButton.disabled = true;
    });

}

function stopRecording(){
    console.log("StopButton clicked.");
    //stopButton.disabled = true;
    startButton.disabled = false;

    //tell the recorder to stop
    rec.stop();

    //stop microphone access
	gumStream.getAudioTracks()[0].stop();

	// generating blob file with a downloading link
    rec.exportWAV(createDownloadLink);

}

function createDownloadLink(blob){
    var xhr=new XMLHttpRequest();
    //creating a wave filename being a current date
    var filename = new Date().toISOString();
    xhr.onload=function(e) {
      if(this.readyState === 4) {
          console.log("Server returned: ",e.target.responseText);
          document.write(xhr.responseText);
      }
    };
    var fd = new FormData();
    fd.append("audio_data", blob, filename);
    xhr.open("POST","/upload",true);
    xhr.send(fd);
    console.log("request done.");
    console.log("let's go.");
/*
    //URL of object
    var url = URL.createObjectURL(blob);


    //playable content in HTML page
    var au = document.createElement('audio');

    //list of recordings
    var li = document.createElement('li');

    //link to the recording
    var link = document.createElement('a');


    //adding controls to playable content:
    au.controls = true;
    au.src = url;

    //link used to save the file on client's disk
    link.href = url;
    link.download = filename + ".wav";
    link.innerHTML = "Save to disk";

    //adding new audio element to the list
    li.appendChild(au);

    //adding filename to the list
    li.appendChild(document.createTextNode(filename+".wav")); */

    // add the save to disk link to the list
 //   li.appendChild(link);

//	li.appendChild(document.createTextNode (" "))//add a space in between

	//add the li element to the ol
	//recordingsList.appendChild(li);
    /*
	var xhr=new XMLHttpRequest();
    //creating a wave filename being a current date
    var filename = new Date().toISOString();
    xhr.onload=function(e) {
      if(this.readyState === 4) {
          console.log("Server returned: ",e.target.responseText);
          document.write(xhr.responseText);
      }
    };
    var fd = new FormData();
    fd.append("audio_data", blob, filename);
    xhr.open("POST","/upload",true);
    xhr.send(fd); */


}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}