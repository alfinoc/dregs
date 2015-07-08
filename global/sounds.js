// Maps custom event attribute to JS event.
var SOUND_EVENTS = {
   'audio-click': 'click',
   'audio-hover': 'mouseover'
}

window.onload = function() {
   attachSoundEventHandlers();
}

function partial(fn, var_args) {
   var args = Array.prototype.slice.call(arguments, 1);
   return function() {
      var newArgs = args.slice();
      newArgs.push.apply(newArgs, arguments);
      return fn.apply(this, newArgs);
   };
};

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
   var onend = function() {
      playing = false;
   };
   var next = 0;
   var sounds = files.map(partial(howlGetter, onend));
   return function() {
      if (!playing) {
         playing = true;
         sounds[next++ % sounds.length]().play();
      }
   }
}

/*
Returns a function that, when called, returns a Howl sound object. Repeated calls
will return the same object, and the onend function supplied on the first call
will be called when the sound object finishes playing.
*/
function howlGetter(onend, file) {
   var howl = null;
   return function() {
      return howl || new Howl({
         urls: [file],
         volume: 1,
         onend: onend
      });
   }
}