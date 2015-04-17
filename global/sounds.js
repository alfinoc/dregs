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
         elts[i].addEventListener(SOUND_EVENTS[attr],
                                  playCB(elts[i].getAttribute(attr)));
      }
   }
}

/*
Returns a callback that begins playing the given sound file as long as it is
not already playing.
*/
function playCB(file) {
   var playing = false;
   var sound = new Howl({
      urls: [file],
      onend: function() {
         playing = false;
      }
   })
   return function() {
      if (!playing) {
         playing = true;
         sound.play();
      }
   }
}
