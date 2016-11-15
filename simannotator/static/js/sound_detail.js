var tempId = 0;
function getTempId(){ return tempId++;}
// function to generate random colors
function g() {
  return Math.floor(Math.random() * 255);
}
function callServer(action, segment, url, cb){
  var xhr = new XMLHttpRequest();
  xhr.responseType = 'json';
  xhr.onreadystatechange = function() {
      if (xhr.readyState == XMLHttpRequest.DONE ) {
         if (xhr.status == 200) {
             cb(xhr.response);
         }
         else if (xhr.status == 400) {
            alert('There was an error 400');
         }
      }
  };

  xhr.open("POST", url, true);
  data = segment;
  data.action = action;
  xhr.send(JSON.stringify(data));
}
function getAnnotations(theUrl){
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", theUrl, false ); // false for synchronous request
    xmlHttp.send( null );
    return JSON.parse(xmlHttp.responseText);
}
function selectSegment(container, tId, segment, sId, sName){
  var inp = container.querySelectorAll(".name-txt");
  if (inp.length > 0) {
    inp[0].value = sName;
  }
  container.setAttribute("data-selected", sId);
  // If we are in a reference tier, then save the object to access from the events of the other element
  if (container.classList.contains('reference')) {
    reference[tId] = segment;
    var display = document.getElementById('selected-section-ref-'+tId);
    if (display != null) {
      if (segment != null){
        display.style.display = "block";
      } else {
        display.style.display = "none";
      }
      display.querySelector('.sel-name').innerHTML = sName;
    }
  }else{
    var display = container.querySelectorAll('.selected-section')[0];
    if (segment != null){
      display.style.display = "block";
    } else {
      display.style.display = "none";
    }
    display.querySelector('.sel-name').innerHTML = sName;
  }
}
var delayedEdit = [];
var delayedTextEdit = [];
var reference = {};
var reference_colors = {};
(function(Peaks){
  var tiers = document.getElementsByClassName('tier');
  for (var i = 0; i < tiers.length; i++) {
    var container = tiers[i];
    var url = container.getAttribute('data-action-url');
    var urlAnnotations = container.getAttribute('data-annotations-url');

    // parameters to create new waveform for annotation tier
    var options = {
      container: container.getElementsByClassName('waveform-visualiser-container')[0],
      mediaElement: document.querySelector("#"+container.getAttribute('data-audio')).querySelector('audio'),
      dataUri: {
        arraybuffer: container.getAttribute('data-waveform'),
      },
      zoomAdapter: 'static',
      height: 40,
      keyboard: false,
      segments: []
    };


    var rsp = getAnnotations(urlAnnotations);
    if (rsp.status == 'success') {
      var tId = container.getAttribute('data-tier-id')
      for (var j = 0; j < rsp.annotations.length; j++){
        var segment = {
          id: rsp.annotations[j].annotation_id,
          startTime: parseFloat(rsp.annotations[j].startTime),
          endTime: parseFloat(rsp.annotations[j].endTime),
          labelText: rsp.annotations[j].name,
          editable: true,
          color: 'rgba(' + g() + ', ' + g() + ', ' + g() + ', 1)'
        }
        
        if (container.classList.contains('reference')) {
          segment['editable'] = false;
          if  (!(tId in reference_colors)) {
            reference_colors[tId] = {};
          }
          reference_colors[tId][rsp.annotations[j].annotation_id] = segment['color']; 
        }
        if (rsp.annotations[j].referenceId != null) {
            if (tId in reference_colors){
              segment['color'] = reference_colors[tId][rsp.annotations[j].referenceId]; 
            }
            segment['referenceId'] = rsp.annotations[j].referenceId; 
        }
        options.segments.push(segment);
      }
    }
    // instantiate Peaks.js annotator
    var peaksInstance = Peaks.init(options);
    
    peaksInstance.on('user_seek.*', (function(container, tier){
      return function(currTime){
        var tId = container.getAttribute('data-tier-id')
        var segments = tier.segments.getSegments();
        var shown = false;
        for (var i = 0; i < segments.length; i++) {
          if (currTime >= segments[i].startTime && currTime <= segments[i].endTime){
            selectSegment(container, tId, segments[i], segments[i].id, segments[i].labelText);
            shown = true;
          }
        }
        if (!shown) {
          selectSegment(container, tId, null, '', '');
        }
      }
    })(container, peaksInstance));

    // By ajax update data of edited segment annotation
    peaksInstance.on('segments.dragged', (function(tier){
      return function(segment){
        segment.annotation_id = segment.id;
        for (var i = 0; i < delayedEdit.length; i++) {
          window.clearTimeout(delayedEdit[i]);
          delayedEdit.splice(i, 1);
        }
        delayedEdit.push(setTimeout(function(){
            callServer('edit', segment, url, function(response){});
            tier.zoom.reset(); // Hack while I dont't find a better way to fix colors on segments
        }, 1000));
      }
    })(peaksInstance));

    // Add new similarity segment to the current tier, also store the annotation in the database
    var addBtn = container.querySelectorAll(".add-simil-segment");
    if (addBtn.length > 0) {
      addBtn[0].addEventListener("click", function (container, tier, actionUrl) {
        return function(){
          var tId = container.getAttribute('data-tier-id')
          var otherSegment = reference[tId];
          var has_reference = false;
          var segments = tier.segments.getSegments();
          if (otherSegment != null){
            for (var i = 0; i< segments.length; i++){
              if (segments[i].referenceId == otherSegment.id) {
                has_reference = true;
              }
            }
            if (!has_reference){
              var startTime = otherSegment.startTime;
              var endTime = otherSegment.endTime;
              var auxId = getTempId();
              var segment = {
                startTime: startTime,
                endTime: endTime,
                editable: true,
                id: auxId,
                referenceId: otherSegment.id,
                color: otherSegment.color
              };
              tier.segments.add(segment);
              callServer('add', segment, actionUrl, function(response){
                if (response.status == 'success'){
                  var segments = tier.segments.getSegments();
                  for (var i = 0; i< segments.length; i++){
                    if (segments[i].id == auxId){
                      segments[i].id = response.annotation_id;
                      segments[i].referenceId = otherSegment.id;
                      container.setAttribute("data-selected", segments[i].id);
                    }
                  }
                }
              });
            }
          }
        }
      }(container, peaksInstance, url));
    }


    // Add new segment to the current tier, also store the annotation in the database
    var addBtn = container.querySelectorAll(".add-segment");
    if (addBtn.length > 0) {
      addBtn[0].addEventListener("click", function (tier, actionUrl) {
        return function(){
          var currTime = tier.time.getCurrentTime()
          var segments = tier.segments.getSegments();
          for (var i = 0; i < segments.length; i++) {
            if (currTime >= segments[i].startTime && currTime <= segments[i].endTime){
              currTime = segments[i].endTime;
            }
          }
          var auxId = getTempId();
          var segment = {
            startTime: currTime,
            endTime: currTime + 1,
            editable: true,
            id: auxId,
            color: 'rgba(' + g() + ', ' + g() + ', ' + g() + ', 1)'
          };
          tier.segments.add(segment);
          callServer('add', segment, actionUrl, function(response){
            if (response.status == 'success'){
              var segments = tier.segments.getSegments();
              for (var i = 0; i< segments.length; i++){
                if (segments[i].id == auxId){
                  segments[i].id = response.annotation_id;
                  container.setAttribute("data-selected", segments[i].id);
                }
              }
            }
          });
        }
      }(peaksInstance, url));
    }

    // Remove a segment, also remove it from the database
    var removeBtn  = container.querySelectorAll(".remove-point");
    if (removeBtn.length > 0) {
      removeBtn[0].addEventListener("click", function (container, tier, actionUrl) {
        return function(){
          var segments = tier.segments.getSegments();
          var currTime = tier.time.getCurrentTime();
          for (var i = 0; i < segments.length; i++) {
            if (currTime >= segments[i].startTime && currTime <= segments[i].endTime){
              var id = segments[i].id;
              selectSegment(container, container.getAttribute('data-tier-id'), null, '', '');
              callServer('remove', {annotation_id: id}, actionUrl, (function(remove_id){
                return function(response){
                  if (response.status == 'success' ){
                    tier.segments.removeById(remove_id);
                  }
                }
              })(id));
            }
          }
        }
      }(container, peaksInstance, url));
    }
    
    var nameInp  = container.querySelectorAll(".name-txt");
    if (nameInp.length > 0) {
      nameInp[0].oninput = (function(container, tier){
        return function(event) {

          for (var i = 0; i < delayedTextEdit.length; i++) {
            window.clearTimeout(delayedTextEdit[i]);
            delayedTextEdit.splice(i, 1);
          }
          segment = container.getAttribute('data-selected');
          segments = tier.segments.getSegments();
          if (segment) {
            for (var i = 0; i < segments.length; i++) {
              if (segments[i].id == segment){
                segments[i].labelText = this.value;
                segment = segments[i];
                segment.annotation_id = segments[i].id;
              }
            }
            delayedTextEdit.push(setTimeout((function(url, segment){
              return function(){  
                callServer('edit', segment, url, function(response){});
              }
            })(url, segment), 1000));
          }
        }
      })(container, peaksInstance);
      nameInp[0].onpropertychange = nameInp[0].oninput; // for IE8
    
    }
  }
})(peaks);

