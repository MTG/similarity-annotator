'use strict';

/*
 * Purpose:
 *   Combines all the components of the interface. Creates each component, gets task
 *   data, updates components. When the user submits their work this class gets the workers
 *   annotations and other data and submits to the backend
 * Dependencies:
 *   AnnotationStages (src/annotation_stages.js), PlayBar & WorkflowBtns (src/components.js), 
 *   HiddenImg (src/hidden_image.js), colormap (colormap/colormap.min.js) , Wavesurfer (lib/wavesurfer.min.js)
 * Globals variable from other files:
 *   colormap.min.js:
 *       magma // color scheme array that maps 0 - 255 to rgb values
 *    
 */
function UrbanEars() {
    this.wavesurfer;
    this.wavesurferRef;
    this.playBar;
    this.playBarRef;
    this.stages;
    this.stagesRef;
    this.workflowBtns;
    this.workflowBtnsRef;
    this.currentTask;
    this.taskStartTime;
    this.soundReady = false;
    this.refReady = false;
    this.currentMoveId = null;
    this.currentMoveSection = null;
    // Boolean, true if currently sending http post request 
    this.sendingResponse = false;

    // Create color map for spectrogram
    var spectrogramColorMap = colormap({
        colormap: magma,
        nshades: 256,
        format: 'rgb',
        alpha: 1
    });

    // Create wavesurfer (audio visualization component)
    var height = 128;
    this.wavesurfer = Object.create(WaveSurfer);
    this.wavesurfer.init({
        container: '.audio_visual',
        waveColor: '#FF00FF',
        progressColor: '#FF00FF',
        // For the spectrogram the height is half the number of fftSamples
        fftSamples: height * 2,
        height: height,
        colorMap: spectrogramColorMap
    });

    this.wavesurferRef = Object.create(WaveSurfer);
    this.wavesurferRef.init({
        container: '.audio_visual_ref',
        waveColor: '#FF00FF',
        progressColor: '#FF00FF',
        // For the spectrogram the height is half the number of fftSamples
        fftSamples: height * 2,
        height: height,
        colorMap: spectrogramColorMap
    });
    var labelsRef = Object.create(WaveSurfer.Labels);
    labelsRef.init({
        wavesurfer: this.wavesurferRef,
        container: '.labels_ref'
    });
    
    // Create labels (labels that appear above each region)
    var labels = Object.create(WaveSurfer.Labels);
    labels.init({
        wavesurfer: this.wavesurfer,
        container: '.labels'
    });


    // Create the play button and time that appear below the wavesurfer
    this.playBar = new PlayBar(this.wavesurfer, '.play_bar');
    this.playBar.create();
    this.playBarRef = new PlayBar(this.wavesurferRef, '.play_bar_ref');
    this.playBarRef.create();

    // Create the annotation stages that appear below the wavesurfer. The stages contain tags 
    // the users use to label a region in the audio clip
    this.stagesRef = new AnnotationStages(this.wavesurferRef);
    this.stagesRef.create();

    // Create Workflow btns (submit and exit)
    this.workflowBtnsRef = new WorkflowBtns();
    this.workflowBtnsRef.create();


    // Create the annotation stages that appear below the wavesurfer. The stages contain tags 
    // the users use to label a region in the audio clip
    this.stages = new AnnotationStages(this.wavesurfer, null, this.wavesurferRef);
    this.stages.create();

    // Create Workflow btns (submit and exit)
    this.workflowBtns = new WorkflowBtns();
    this.workflowBtns.create();


    this.addEvents();
    
    var my = this;
    var slider = document.querySelector('#slider');
    slider.oninput = function () {
        var zoomLevel = Number(slider.value);
          my.wavesurfer.zoom(zoomLevel);
    };
 
    var sliderRef = document.querySelector('#slider_ref');
    sliderRef.oninput = function () {
        var zoomLevel = Number(sliderRef.value);
          my.wavesurferRef.zoom(zoomLevel);
    };
}

UrbanEars.prototype = {
    addWaveSurferEvents: function() {
        var my = this;

        // function that moves the vertical progress bar to the current time in the audio clip
        var updateProgressBarRef = function () {
            var progress = my.wavesurferRef.getCurrentTime() / my.wavesurferRef.getDuration();
            my.wavesurferRef.seekTo(progress);
        };

        var moveNextSection = function (movedSection) {
            var segments = my.stages.getAnnotations();
            var moveNext = false;
            segments.sort(function(a, b){return a.start-b.start});
            segments.forEach(function(segment){
                if (moveNext && Math.abs(my.currentMoveSection.end - segment.start) < 0.1 ) {
                    var length = segment.end - segment.start;
                    var next = my.wavesurfer.regions.list[segment.id];
                    next.start = movedSection.end;
                    next.end= movedSection.end + length;
                    next.updateRender();
                    my.wavesurfer.fireEvent('region-updated', next);
                    moveNext = false;
                }else if (Math.abs(my.currentMoveSection.start - segment.end) < 0.1 ) {
                    var length = segment.end - segment.start;
                    var prev = my.wavesurfer.regions.list[segment.id];
                    prev.end = movedSection.start;
                    prev.updateRender();
                    my.wavesurfer.fireEvent('region-updated', prev);
                }else if (segment.id == my.currentMoveId){
                    moveNext = true;
                }
            });
            my.currentMoveId = null;
        };

        var moveStart = function (section) {
            if (my.currentMoveId != section.id){
              my.currentMoveId = section.id;
              my.currentMoveSection = {end: section.end, start: section.start};
            }
        };
        
        // function that moves the vertical progress bar to the current time in the audio clip
        var updateProgressBar = function () {
            var progress = my.wavesurfer.getCurrentTime() / my.wavesurfer.getDuration();
            my.wavesurfer.seekTo(progress);
        };
        
        // Update vertical progress bar to the currentTime when the sound clip is 
        // finished or paused since it is only updated on audioprocess
        this.wavesurferRef.on('pause', updateProgressBarRef);
        this.wavesurferRef.on('finish', updateProgressBarRef);    
        this.wavesurfer.on('pause', updateProgressBar);
        this.wavesurfer.on('finish', updateProgressBar);    
        this.wavesurfer.on('region-update-end', moveNextSection);    
        this.wavesurfer.on('region-updated', moveStart);    

        // When a new sound file is loaded into the wavesurfer update the  play bar, update the 
        // annotation stages back to stage 1, update when the user started the task, update the workflow buttons.
        // Also if the user is suppose to get hidden image feedback, append that component to the page
        this.wavesurferRef.on('ready', function () {
            my.refReady = true;
            my.loadSegments();
        });
        
        // When a new sound file is loaded into the wavesurfer update the  play bar, update the 
        // annotation stages back to stage 1, update when the user started the task, update the workflow buttons.
        // Also if the user is suppose to get hidden image feedback, append that component to the page
        this.wavesurfer.on('ready', function () {
           my.soundReady = true;
           my.loadSegments();
        });

    },
 
    createSegment: function(){
      var my = this;
      var currTime = my.wavesurfer.getCurrentTime();
      var segments = my.stages.getAnnotations();
      segments.sort(function(a, b){return a.start-b.start});
      var lastEnd = 0;
      var added = false;
      segments.forEach(function(section){
          if (added == false && section.start > currTime && lastEnd != section.start){
            var region = my.wavesurfer.addRegion({
              start: lastEnd,
              end: section.start,
            });
            my.stagesRef.createRegionSwitchToStageThree(region);
            added = true;
          }else if (added == false && section.start < currTime && section.end > currTime) {
            var region = my.wavesurfer.addRegion({
              start: currTime,
              end: section.end,
            });
            my.stagesRef.createRegionSwitchToStageThree(region);
            var oldSection =  my.wavesurfer.regions.list[section.id];
            oldSection.end = currTime;
            oldSection.updateRender();
            my.wavesurfer.fireEvent('region-updated', oldSection);
            added = true;
          }
          lastEnd = section.end;
      });
      if (added === false) {
          if (currTime > lastEnd) {
              var region = my.wavesurfer.addRegion({
                  start: lastEnd,
                  end: currTime,
              });
              my.stagesRef.createRegionSwitchToStageThree(region);
          }
          else {
              var region = my.wavesurfer.addRegion({
                  start: lastEnd,
                  end: lastEnd + 1,
              });
              my.stagesRef.createRegionSwitchToStageThree(region);
          }
      }

    },
    loadSegments: function(){
      var my = this;
      if (this.refReady && this.soundReady){
          my.playBarRef.update();
          my.stagesRef.updateStage(1);
          
          my.currentTask.segments_ref.forEach(function(section){
          
            var region = my.wavesurferRef.addRegion({
              start: section.start,
              end: section.end,
              id: section.id,
              drag: false,
              resize: false,
              canDelete: false,
              annotation: section.annotation,
            });
            my.stagesRef.createRegionSwitchToStageThree(region);
          
          });
          my.playBar.update();
          my.currentTask.segments.forEach(function(section){
          var values = {
            start: section.start,
            end: section.end,
            id: section.id,
            annotation: section.annotation,
            similValue: section.similValue,
            similarity: section.similarity
          }; 
          var region = my.wavesurfer.addRegion(values);
          if (section.reference != null){
            region.regionRef = my.wavesurferRef.regions.list[section.reference];
          }
          my.stages.createRegionSwitchToStageThree(region);
        });
        my.stages.updateStage(1);
        my.updateTaskTime();
        my.workflowBtns.update();
      }
    },

    updateTaskTime: function() {
        this.taskStartTime = new Date().getTime();
    },

    // Event Handler, if the user clicks submit annotations call submitAnnotations
    addWorkflowBtnEvents: function() {
        $(this.workflowBtns).on('submit-annotations', this.submitAnnotations.bind(this));
    },

    addEvents: function() {
        this.addWaveSurferEvents();
        this.addWorkflowBtnEvents();
    },

    // Update the task specific data of the interfaces components
    update: function() {
        var my = this;
        var mainUpdate = function() {

            // Update the different tags the user can use to annotate, also update the solutions to the
            // annotation task if the user is suppose to recieve feedback
            var similaritySegment= my.currentTask.similaritySegment;
            var annotationTags = my.currentTask.annotationTags;
            var recordingIndex = my.currentTask.recordingIndex || 1;
            var numRecordings = my.currentTask.numRecordings || 1;
            var alwaysShowTags = my.currentTask.alwaysShowTags;
            my.stages.reset(
                similaritySegment,
                annotationTags,
                alwaysShowTags
            );

            // Update clip & time tracker of Header
            $('#recording-index').html(recordingIndex);
            $('#time-remaining').html((numRecordings - recordingIndex) * 1.5 + 5); // e.g. each clip should take 1.5 minutes, and all post-annotation tasks 5 mins.

            // Update the visualization type and the feedback type and load in the new audio clip
            my.wavesurfer.params.visualization = my.currentTask.visualization; // invisible, spectrogram, waveform
            my.wavesurfer.params.feedback = my.currentTask.feedback; // hiddenImage, silent, notify, none 
            my.wavesurfer.load(my.currentTask.url);
            my.wavesurferRef.params.visualization = my.currentTask.visualization; // invisible, spectrogram, waveform
            my.wavesurferRef.params.feedback = my.currentTask.feedback; // hiddenImage, silent, notify, none 
            my.wavesurferRef.load(my.currentTask.url_ref);
        };

        // Just update task specific data right away
        mainUpdate();
    },

    // Update the interface with the next task's data
    loadNextTask: function() {
        var my = this;
        $.getJSON(dataUrl)
        .done(function(data) {
            my.currentTask = data.task;
            my.update();
        });
    },

    // Collect data about users annotations and submit it to the backend
    submitAnnotations: function() {
        // Check if all the regions have been labeled before submitting
        if (this.stages.annotationDataValidationCheck()) {
            if (this.sendingResponse) {
                // If it is already sending a post with the data, do nothing
                return;
            }
            this.sendingResponse = true;
            // Get data about the annotations the user has created
            var content = {
                annotations: this.stages.getAnnotations(),
            };

            this.post(content);
        }
    },

    // Make POST request, passing back the content data. On success load in the next task
    post: function (content) {
        console.log("This post will fail since this is a frontend demo.");
        console.log("Here is the data about the annotation task");
        console.log(content);
        var my = this;
        $.ajax({
            type: 'POST',
            url: dataUrl,
            data: JSON.stringify(content),
            contentType: "application/json; charset=utf-8",
        })
        .done(function(data) {
            if (data.status == "success" && nextUrl != 'None') {
              window.location = nextUrl;
            }else if(data.status == "success"){
                Message.notifyAlert('Successfully saved all the changes, that was the last Tier.'); 
            }
        })
        .fail(function() {
            alert('Error: Unable to Submit Annotations');
        })
        .always(function() {
            // No longer sending response
            my.sendingResponse = false;
        });
    }

};

function main() {
    // Create all the components
    var urbanEars = new UrbanEars();
    document.onkeypress = function(event) {
      if(document.activeElement.className != 'annotation_inp' && event.keyCode == 'i'.charCodeAt(0)){
        urbanEars.createSegment();
      }
    }

    // Load the first audio annotation task
    urbanEars.loadNextTask();
}
main();
