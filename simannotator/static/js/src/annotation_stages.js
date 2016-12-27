'use strict';

/*
 * Purpose:
 *   The view the user sees when no region has been seleted
 * Dependencies:
 *   jQuey, urban-ears.css
 */
function StageOneView() {
    this.dom = null;
}

StageOneView.prototype = {
    // Create dom
    create: function() {
        var my = this;
        var container = $('<div>');

        // This btn is for the region online creation mode, not currently appended to the stage one view
        var button = $('<button>', {
            class: 'btn btn_start',
            text: 'CLICK TO START A NEW ANNOTATION',
        });
        button.click(function () {
            $(my).trigger('start-annotation');
        });

        var time = Util.createSegmentTime();

        time.hide();

        this.dom = container.append([time]);
    },

    // Update start and end times. Enable the 'CLICK TO START A NEW ANNOTATION' if the audio is playing
    update: function(start, end, enableCreate) {
        $('.start', this.dom).val(Util.secondsToString(start));
        $('.end', this.dom).val(Util.secondsToString(end));
        $('.btn_start', this.dom).prop('disabled', !enableCreate);
    },
};

/*
 * Purpose:
 *   The view the user sees when they are creating an annotation in online mode,
 *   (the region grows as the audio plays). This view is not used if the current version
 *   of the interface
 * Dependencies:
 *   jQuey, urban-ears.css
 */
function StageTwoView() {
    this.dom = null;
}

StageTwoView.prototype = {
    // Create dom
    create: function() {
        var my = this;
        var container = $('<div>');
        var button = $('<button>', {
            class: 'btn btn_stop',
            text: 'CLICK TO END ANNOTATION',
        });
        button.click(function () {
            $(my).trigger('stop-annotation');
        });

        var time = Util.createSegmentTime();
        
        this.dom = container.append([button, time]);
    },

    // Update start, end and duration times
    update: function(region) {
        $('.start', this.dom).val(Util.secondsToString(region.start));
        $('.end', this.dom).val(Util.secondsToString(region.end));
        $('.duration', this.dom).val(Util.secondsToString(region.end - region.start));
    },
};

/*
 * Purpose:
 *   The view the user sees when they have a region selected
 * Dependencies:
 *   jQuey, urban-ears.css
 */
function StageThreeView() {
    this.dom = null;
    this.editOptionsDom = null;
    this.colors = ['rgba(236,0,251,0.4)', 'rgba(39,117,243,0.4)', 'rgba(33,177,4,0.4)'];
}

StageThreeView.prototype = {
    // Create dom
    create: function() {
        var my = this;
        var container = $('<div>');

        var message = $('<div>', {
            class: 'stage_3_message'
        });

        var time = Util.createSegmentTime();

        time.show();

        var tagContainer = $('<div>', {
            class: 'tag_container',
        });
        
        this.dom = container.append([message, time, tagContainer]);
    },

    // Replace the annotation elements with the new elements that contain the
    // options in the lists like annotationTags
    updateTagContents: function(similaritySegment, annotationTags) {
        $('.tag_container', this.dom).empty();
        var similarity = this.createSimilarityOptions(similaritySegment);
        // For now the only support type is text input
        var annotation = this.createAnnotationType(annotationTags);
        $('.tag_container', this.dom).append([similarity, annotation]);
    },

    // Create proximity tag elements
    createSimilarityOptions: function(similaritySegment) {
        if (similaritySegment.length === 0) { return; }
        var my = this;

        var similarity = $('<div>');
        var similarityLabel = $('<div>', {
            class: 'stage_3_label',
            text: 'Is similarity measure:',
        });

        var similarityContainer = $('<div>', {
            class: 'similarity_options'
        });

        similaritySegment.forEach(function (optionName, index) {
            var option = $('<button>', {
                class: 'similarity_option btn',
                text: optionName,
            });
            // When a option is clicked fire the 'change-tag' event with what option it is and
            // colour that option is associated with
            option.click(function () {
                $(my).trigger(
                    'change-tag', 
                    [{similarity: optionName, color: my.colors[index]}]
                );
            });
            similarityContainer.append(option);
        });

        return similarity.append([similarityLabel, similarityContainer]);
    },


    // Create annotation elements
    createAnnotationType: function(annotationTags) {
        var my = this;

        var annotation = $('<div>');
        var annotationLabel = $('<div>', {
            class: 'stage_3_label',
            text: 'Name:',
        });

        var annotationContainer = $('<div>', {
            class: 'annotation_container'
        });

        var tagsContainer = $('<div>');
        annotationContainer.append(tagsContainer);

        var input = $('<input>', {
            class: 'annotation_inp',
        });

        annotationTags.forEach(function (tagName) {
            var tag = $('<button>', {
                class: 'annotation_tag btn',
                text: tagName,
            });
            tag.click(function () {
                input.val(tagName);
            });
            tagsContainer.append(tag);
        });

        var similValueLabel = $('<div>', {
            class: 'stage_3_label',
            text: 'Value:',
        });

        var similValueContainer = $('<div>', {
            class: 'simil_value_container'
        });
        var input2 = $('<input>', {
            class: 'simil-val-inp',
        });
        var btn = $('<button>', {
            class: 'annotation_tag btn',
            text: 'Done',
        });

        // When a proximity tag is clicked fire the 'change-tag' event with what annotation tag it is
        btn.click(function () {
            $(my).trigger('change-tag', [{annotation: input.val(), similValue: input2.val()}]);
        });
        annotationContainer.append(input);
        annotationContainer.append(btn);
        similValueContainer.append(similValueLabel);
        similValueContainer.append(input2);

        return annotation.append([similValueContainer, annotationLabel, annotationContainer]);
    },

    // Update stage 3 dom with the current regions data
    update: function(region) {
        this.updateTime(region);
        this.updateSelectedTags(region);
    },

    // Update the start, end and duration elements to match the start, end and duration
    // of the selected region
    updateTime: function(region) {
        $('.start', this.dom).val(Util.secondsToString(region.start));
        $('.end', this.dom).val(Util.secondsToString(region.end));
        $('.duration', this.dom).val(Util.secondsToString(region.end - region.start));
    },

    // Update the elements of the proximity and annotation tags to highlight
    // which tags match the selected region's current annotation and proximity
    updateSelectedTags: function(region) {
        $('.similarity_option', this.dom).removeClass('selected');
        $('.annotation_inp', this.dom).val('');
        $('.simil-val-inp', this.dom).val('');
        $('.simil_value_container', this.dom).hide();

        if (region.similValue) {
            $('.simil-val-inp', this.dom).val(region.similValue);
        }

        if (region.annotation) {
            $('.annotation_inp', this.dom).val(region.annotation);
        }

        if (region.similarity) {
            var selectedTags = $('.similarity_option', this.dom).filter(function () {
              return this.innerHTML === region.similarity;
            });
            selectedTags.addClass('selected');
            if (region.similarity == 'yes'){
              $('.simil_value_container', this.dom).show();
            }
        }
    }
};

/*
 * Purpose:
 *   Control the workflow of annotating regions.
 * Dependencies:
 *   jQuey, urban-ears.css, Wavesurfer (lib/wavesurfer.js), Message (src/message.js)
 */
function AnnotationStages(wavesurfer, hiddenImage, wavesurferRef, editEnable) {
    this.currentStage = 0;
    this.currentRegion = null;
    this.stageOneView = new StageOneView();
    this.stageTwoView = new StageTwoView();
    this.stageThreeView = new StageThreeView();
    this.wavesurferRef = wavesurferRef;
    this.wavesurfer = wavesurfer;
    this.hiddenImage = hiddenImage;
    this.deletedAnnotations = [];
    this.city = '';
    this.previousF1Score = 0;
    this.events = [];
    this.alwaysShowTags = false;
    this.editEnable = editEnable;

    // These are not reset, since they should only be shown for the first clip
    this.shownTagHint = false;
    this.shownSelectHint = false;
}

AnnotationStages.prototype = {
    // Create the different stages dom and append event handlers
    create: function() {
        // Add events
        this.addStageOneEvents();
        this.addStageTwoEvents();
        this.addStageThreeEvents();
        this.addWaveSurferEvents();

        // Create dom
        this.stageOneView.create();
        this.stageTwoView.create();
        this.stageThreeView.create();

    },

    // Extract the important information from a region object
    getAnnotationData: function(region) {
        var regionData = {
            'id': region.id,
            'start': region.start,
            'end': region.end,
            'annotation': region.annotation
        };
        regionData.similarity = region.similarity;
        if (region.regionRef != null) {
            regionData.reference = region.regionRef.id;
            regionData.similValue = region.similValue;
        }
        return regionData;
    },

    // Return an array of all the annotations the user has made for this clip
    getAnnotations: function() {
        var annotationData = [];
        if (this.wavesurfer.regions) {
            for (var region_id in this.wavesurfer.regions.list) {
                var region = this.wavesurfer.regions.list[region_id];
                annotationData.push(this.getAnnotationData(region));
            }
        }
        return annotationData;
    },

    // Return an array of all the annotations the user has created and then deleted for this clip
    getDeletedAnnotations: function() {
        var annotationData = [];
        var length = this.deletedAnnotations.length;
        for (var i = 0; i < length; ++i) {
            annotationData.push(this.getAnnotationData(this.deletedAnnotations[i]));
        }
        return annotationData;
    },

    // Check that all the annotations have the required tags, if not alert the user
    annotationDataValidationCheck: function() {
        if (this.wavesurfer.regions) {
            for (var region_id in this.wavesurfer.regions.list) {
                var region = this.wavesurfer.regions.list[region_id];
                if (region.similarity == 'yes' && (region.regionRef == null)) {
                  Message.notifyAlert('Make shure to select a similarity section'); 
                  return false;
                }else if (region.similarity == 'yes'){
                  if (region.similValue === '' || isNaN(region.similValue)){
                    Message.notifyAlert('Make shure the annotations is a valid number for similarity segments'); 
                    return false;
                  }
                }else if (region.annotation === '') {
                    Message.notifyAlert('Make sure all your annotations have a name!'); 
                    return false;
                }
            }
        }
        return true;
    },

    // Switch the currently selected region
    swapRegion: function(newStage, region) {
        // Disable drag and resize editing for the old current region. 
        // Also remove the highlight of the label and region border
        if (this.currentRegion) {
            this.currentRegion.update({drag: false, resize: false});
            if (this.wavesurferRef) {
              $(this.currentRegion.element).removeClass('current_region');
              $(this.currentRegion.annotationLabel.element).removeClass('current_label');
            }else{
              $(this.currentRegion.element).removeClass('current_region_ref');
              $(this.currentRegion.annotationLabel.element).removeClass('current_label_ref');
            }
        }
        if (this.currentRegion && this.currentRegion.regionRef != null) {
            $(this.currentRegion.regionRef.element).removeClass('current_region_ref');
            $(this.currentRegion.regionRef.annotationLabel.element).removeClass('current_label_ref');
        } 
        
        // If the user is switch to stage 3, enable drag and resize editing for the new current region. 
        // Also highlight the label and region border
        if (region) {
            if (newStage === 2) {
                region.update({drag: false, resize: false});
            } else if (newStage === 3) {
                region.update({drag: true, resize: true});
                $('.current_region_ref').removeClass('current_region_ref');
                $('.current_label_ref').removeClass('current_label_ref');
                if (this.wavesurferRef) {
                  $(region.element).addClass('current_region');
                  $(region.annotationLabel.element).addClass('current_label');
                }else{
                  $(region.element).addClass('current_region_ref');
                  $(region.annotationLabel.element).addClass('current_label_ref');
                }
            }
           
        }
        this.currentRegion = region;
    },

    // Switch stages and the current region
    updateStage: function(newStage, region) {
        // Swap regions 
        this.swapRegion(newStage, region);

        if (this.wavesurferRef || this.editEnable){
          // Update the dom of which ever stage the user is switching to
          var newContent = null;
          if (this.alwaysShowTags){
              newContent = this.stageThreeView.dom;
          } else {
              if (newStage === 1) {
                  this.stageOneView.update(null, null, this.wavesurfer.isPlaying());
                  newContent = this.stageOneView.dom;
              } else if (newStage === 2) {
                  this.stageTwoView.update(region);
                  newContent = this.stageTwoView.dom;
              } else if (newStage === 3) {
                  this.stageThreeView.update(region);
                  newContent = this.stageThreeView.dom;
              }
          }


          if (newContent) {
              // Update current stage
              this.currentStage = newStage;

              // Detach the previous stage dom and append the updated stage dom to the stage container
              var container = $('.creation_stage_container');
              if (this.alwaysShowTags) {
                  container.hide(10, function(){
                      container.children().detach();
                      container.append(newContent).show();
                  });
              } else {
                  container.fadeOut(10, function(){
                      container.children().detach();
                      container.append(newContent).fadeIn();
                  });          
              }
          }
          // Alert the user of a hint
          this.hint();
        }
    },

    // Alert users of hints about how to use the interface
    hint: function() {
        if (this.wavesurfer.regions && Object.keys(this.wavesurfer.regions.list).length === 1) {
            if (this.currentStage === 1 && !this.shownSelectHint) {
                // If the user deselects a region for the first time and have not seen this hint,
                // alert them on how to select and deselect a region
                Message.notifyHint('Double click on a segment to select or deselect it.');
                this.shownSelectHint = true;
            }
            if (this.currentStage === 3 && !this.shownTagHint) {
                // When the user makes a region for the first time, if they have not seen this hint,
                // alert them on how to annotate a region
                Message.notifyHint('Select a tag to annotation the segment.');
                this.shownTagHint = true;
            }
        }
    },

    // Reset the field values (except for hint related fields)
    clear: function() {
        this.currentStage = 0;
        this.currentRegion = null;
        this.wavesurfer.clearRegions();
        this.events = [];
        this.deletedAnnotations = [];
        this.alwaysShowTags = false;
    },

    // Reset field values and update the proximity tags, annotation tages and annotation 
    reset: function(similaritySegment, annotationTags, alwaysShowTags) {
        this.clear();
        // Update all Tags' Contents
        this.alwaysShowTags = alwaysShowTags || false;
        this.updateContentsTags(similaritySegment, annotationTags);
    },

    // Update stage 3 dom with new proximity tags and annotation tags
    updateContentsTags: function(similaritySegment, annotationTags) {
        this.stageThreeView.updateTagContents(
            similaritySegment,
            annotationTags
        );
    },

    // Event Handler: For online creation mode, in stage 2 the current region's size grows as the audio plays
    updateEndOfRegion: function() {
        var current = this.wavesurfer.getCurrentTime();
        if (this.currentStage === 2 && current > this.currentRegion.end) {
            this.currentRegion.update({
                end: current
            });
            this.stageTwoView.update(this.currentRegion);
        }
    },

    // Event Handler: when the user finishes drawing the region, track the action and 
    // select the new region and switch to stage 3 so the user can tag the region
    createRegionSwitchToStageThree: function(region) {
        if (region !== this.currentRegion) {
            this.trackEvent('offline-create', region.id, null, region.start, region.end);
            this.updateStage(3, region);
        }
    },

    // Event handler: Called when a region is selected by dbl clicking the region or its label
    switchToStageThree: function(region) {
        if (region !== this.currentRegion) {
            this.trackEvent('select-for-edit', region.id);
            this.updateStage(3, region);
            if (region.regionRef != null) {
              $('.current_region_ref').removeClass('current_region_ref');
              $('.current_label_ref').removeClass('current_label_ref');
              
              $(region.regionRef.element).addClass('current_region_ref');
              $(region.regionRef.annotationLabel.element).addClass('current_label_ref');
            }
        } else {
            this.trackEvent('deselect', region.id);
            this.updateStage(1);
        }
    },
    
    changedSelectionOnRef: function(region) {
        if (this.currentRegion != null && this.currentRegion.similarity == 'yes') {
          region.update({color: this.currentRegion.color});
          this.currentRegion.regionRef = region;
        }
    },

    // Event Handler: Update stage 3 dom with the the current region's data when the region data
    // has been changed
    updateStartEndStageThree: function() {
        if (this.currentStage === 3) {
            this.stageThreeView.updateTime(this.currentRegion);
        }
    },

    // Event handler: called when the a region is draged or resized, adds action to event list
    trackMovement: function(region, event, type) {
        if (this.currentStage === 3) {
            this.giveFeedback();
            this.trackEvent('region-moved-' + type, this.currentRegion.id, null, this.currentRegion.start, this.currentRegion.end);
        }
    },

    // Event handler: called when there is audio progress. Updates the online creation
    // button if the audio is playing
    updateStageOne: function() {
        if (this.currentStage === 1) {
            this.stageOneView.update(
                null,
                null, 
                this.wavesurfer.isPlaying()
            );
        }
    },

    // Event handler: Update stage one view region's start, end and duration as the user draws the region
    updateStageOneWhileCreating: function(region) {
        if (this.currentStage === 1) {
            this.stageOneView.update(
                region.start,
                region.end,
                this.wavesurfer.isPlaying()
            );
        }
    },

    // Event Handler: For online creation mode, called when the user clicks start creating annotation
    // Creates a region and switches to stage 2 where the region grows as the audio plays
    startAnnotation: function() {
        var region = this.wavesurfer.addRegion({
            start: this.wavesurfer.getCurrentTime(),
            end: this.wavesurfer.getCurrentTime(),
        });
        this.updateStage(2, region);
    },

    // Event Handler: For online creation mode, called when the user clicks stop creating annotation.
    // Switches to stage 3 where the user can annotate the newly created region
    stopAnnotation: function() {
        if (this.wavesurfer.isPlaying()) {
            this.wavesurfer.pause();
        }
        this.trackEvent('online-create', this.currentRegion.id, null, this.currentRegion.start, this.currentRegion.end);
        this.updateStage(3, this.currentRegion);
    },

    // Event Handler: called when region is deleted
    deleteAnnotation: function(region) {
        // update f1 score and give the user feedback
        this.giveFeedback();
        // Add the action to the event list
        this.trackEvent('delete', region.id);
        // Add the region to the deleted list
        this.deletedAnnotations.push(region);
        // If that region was currently selected, switch back to stage 1
        if (region === this.currentRegion) {
            this.updateStage(1);
        }
    },

    // Event handler: called when a region's tags are added or changed
    updateRegion: function(event, data) {
        var annotationEventType = null;
        var similarityEventType = null;

        // Determine if the tags where added for the first time or just changed
        if ((data.annotation && data.annotation !== this.currentRegion.annotation) ||
           (data.similValue && data.similValue != this.currentRegion.similValue)){
            annotationEventType = this.currentRegion.annotation ? 'change' : 'add';
        }
        if (data.similarity && data.similarity !== this.currentRegion.similarity) {
            similarityEventType = this.currentRegion.similarity ? 'change' : 'add';
        }

        // Update the current region with the tag data
        this.currentRegion.update(data);
        // Give feedback if these tags improve the user's f1 score
        this.giveFeedback();

        // Track tag change / add events
        if (annotationEventType) {
            this.trackEvent(
                annotationEventType + '-annotation-label',
                this.currentRegion.id,
                this.currentRegion.annotation
            );
        }
        
        if (similarityEventType) {
            if (this.currentRegion.similarity == 'yes') {
              Message.notifyHint('Double click on a segment of the Reference Sound.');
            }
            this.trackEvent(
                similarityEventType + '-similarity-label',
                this.currentRegion.id,
                this.currentRegion.similarity
            );
        }
        // If the region has all its required tags, deselect the region and go back to stage 1
        if (this.currentRegion.annotation != "" && 
            (this.currentRegion.similarity == 'no' || this.currentRegion.regionRef)){
            this.updateStage(1);
        }
    },

    // Helper function, called when the user makes changes that will affect their f1 score
    // If the user has some type of feed back, update the f1 score and notify the user of their progress
    giveFeedback: function() {
        if (this.wavesurfer.params.feedback !== 'none') {
            var newF1Score = this.computeF1Score();
            if (this.wavesurfer.params.feedback === 'notify') {
                this.notify(newF1Score);
            } else if (this.wavesurfer.params.feedback === 'hiddenImage') {
                this.hiddenImage.resetCover();
                this.notify(newF1Score);
                this.showImage(newF1Score);
            }
            // For silent feedback just update the f1score
            // After we checked if the user has improved and recieved feedback, replace f1 score
            this.previousF1Score = newF1Score;
        }
    },

    // Notify the user if their f1 score is increasing
    notify: function(f1Score) {
        if (f1Score > this.previousF1Score) {
            Message.notifyPositive();
        } else if (f1Score < this.previousF1Score) {
            Message.notifyNegative();
        }
    },

    // Show a percentage of the hiddenImage
    showImage: function(f1Score) {
        this.hiddenImage.showRandomParts(f1Score);
    },

    // Return true if the user should have the city revealed to them
    aboveThreshold: function() {
        var hasFeedback = this.wavesurfer.params.feedback === 'hiddenImage' ||
                          this.wavesurfer.params.feedback === 'notify';
        return hasFeedback && this.previousF1Score >= 0.65;
    },


    // Event Handler: triggered when region is first started to be created, adds action to event list
    trackBeginingOfRegionCreation: function(region) {
        this.trackEvent('start-to-create', region.id);
    },

    // Event Handler: triggered when region is first started to be created
    // switch back to stage one while the user drags to finish creating the region
    switchToStageOneOnCreate: function() {
        if (this.currentStage !== 1) {
            this.updateStage(1);
        }
    },

    // Adds event tracking object to events list
    trackEvent: function(eventString, regionId, regionLabel, regionStart, regionEnd) {
        var eventData = {
            event: eventString,
            time: new Date().getTime(),
            region_id: regionId
        };
        // If the region's current label is passed in, append it to the event data
        if (regionLabel) {
            eventData.region_label = regionLabel;
        }

        if (regionStart) {
            eventData.region_start = regionStart;
        }

        if (regionEnd) {
            eventData.region_end = regionEnd;
        }
        // If the user has silent, notify, or hiddenImage feedback, recored the 
        // current f1 score with the event data
        if (this.wavesurfer.params.feedback !== 'none') {
            eventData.f1 = this.previousF1Score;
            eventData.number_tiles = (this.wavesurfer.params.feedback === 'hiddenImage') ?
                                        Math.floor(this.previousF1Score * 10) : 0;
        }
        this.events.push(eventData);
    },

    // Return a list of actions the user took while annotating this clip
    getEvents: function() {
        // Return shallow copy
        return this.events.slice();
    },

    // Event handler: triggered when a region is played, adds this action to the event list
    trackPlayRegion: function(region) {
        this.trackEvent('play-region', region.id);
    },

    // Attach event handlers for wavesurfer events
    addWaveSurferEvents: function() {
       if (this.wavesurferRef || this.editEnable) {
          this.wavesurfer.enableDragSelection();
          this.wavesurfer.on('region-update-end', this.trackMovement.bind(this));
          this.wavesurfer.on('region-update-end', this.createRegionSwitchToStageThree.bind(this));
          this.wavesurfer.on('region-update-end', this.updateStartEndStageThree.bind(this));
          this.wavesurfer.on('region-updated', this.updateStartEndStageThree.bind(this));
          this.wavesurfer.on('region-updated', this.updateStageOneWhileCreating.bind(this));
          this.wavesurfer.on('region-updated', this.stageThreeView.updateSelectedTags.bind(this));
          this.wavesurfer.on('region-created', this.trackBeginingOfRegionCreation.bind(this));
          this.wavesurfer.on('region-created', this.switchToStageOneOnCreate.bind(this));
          this.wavesurfer.on('region-removed', this.deleteAnnotation.bind(this));
          if (this.wavesurferRef) {
              this.wavesurferRef.on('region-dblclick', this.changedSelectionOnRef.bind(this));
              this.wavesurferRef.on('label-dblclick', this.changedSelectionOnRef.bind(this));
          } 
       }
        this.wavesurfer.on('region-dblclick', this.switchToStageThree.bind(this));
        this.wavesurfer.on('label-dblclick', this.switchToStageThree.bind(this));
        this.wavesurfer.on('audioprocess', this.updateEndOfRegion.bind(this));
        this.wavesurfer.on('audioprocess', this.updateStageOne.bind(this));
        this.wavesurfer.on('pause', this.updateEndOfRegion.bind(this));
        this.wavesurfer.on('region-play', this.trackPlayRegion.bind(this));
    },

    // Attach event handlers for stage one events
    addStageOneEvents: function() {
        $(this.stageOneView).on('start-annotation', this.startAnnotation.bind(this));
    },

    // Attach event handlers for stage two events
    addStageTwoEvents: function() {
        $(this.stageTwoView).on('stop-annotation', this.stopAnnotation.bind(this));
    },

    // Attach event handlers for stage three events
    addStageThreeEvents: function() {
        $(this.stageThreeView).on('change-tag', this.updateRegion.bind(this));
    },   
};
