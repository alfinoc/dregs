// Maps custom event attribute to JS event.
var SOUND_EVENTS = {
   'audio-click': 'click',
   'audio-hover': 'mouseover'
}

window.onload = function() {
   attachSoundEventHandlers();
}

/*
Attaches event handlers to all elements on the page with audio event attributes.
*/
function attachSoundEventHandlers() {
   for (var attr in SOUND_EVENTS) {
      var elts = document.querySelectorAll('*[' + attr + ']');
      for (var i = elts.length - 1; i >= 0; i--) {
         var files = elts[i].getAttribute(attr).split(',');
         if (files.length > 0) {
            elts[i].addEventListener(SOUND_EVENTS[attr], playCB(files));
         }
      }
   }
}

/*
Returns a callback that plays a sound file in 'files' on every call, starting with
the first file and looping back around after all files are played. Only begins
playing a file if no file is already playing.
*/
function playCB(files) {
   var playing = false;
   var next = 0;
   var sounds = files.map(function(file) {
      return new Howl({
         urls: [file],
         volume: 1,
         onend: function() {
            playing = false;
         }
      });
   });
   return function() {
      if (!playing) {
         playing = true;
         sounds[next++ % sounds.length].play();
      }
   }
}
