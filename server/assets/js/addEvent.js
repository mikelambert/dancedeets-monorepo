/**
 * Copyright 2016 DanceDeets.
 *
 * @flow
 */

import jQuery from 'jquery';
import './common';

global.$ = global.jQuery = jQuery;

function addEvent() {
  const element = jQuery(this);
  const id = element.attr('id').replace('button-', '');

  element.text('Adding...');
  jQuery
    .ajax({
      method: 'POST',
      url: `/events_add?ajax=1&event_id=${id}`,
    })
    .done(() => {
      const liEvent = jQuery(`#event-${id}`);
      liEvent.addClass('ui-disabled');
      liEvent.removeClass('ui-selectable').removeClass('ui-selected');
    })
    .done(() => {
      element.text('Add Event');
    });
  return false;
}

function validateAdd() {
  if (jQuery('#event_id_form').val() || jQuery('#event_url_form').val()) {
    return true;
  } else {
    alert(
      'Please select one of your events to add, or enter the URL of the event you wish to add.'
    );
    return false;
  }
}

jQuery(document).ready(() => {
  jQuery('#add-by-url').click(validateAdd);
  jQuery('#add-events').click(event => {
    const selectees = jQuery('.ui-selectable', '#add-events');
    selectees.filter('.ui-selected').each((index, target) => {
      jQuery(target).removeClass('ui-selected');
    });
    jQuery(event.target)
      .parents()
      .addBack()
      .filter('.ui-selectable')
      .each((index, target) => {
        jQuery(target).addClass('ui-selected');
        const id = jQuery(target).data('id');
        jQuery('#event_url_form').val(`https://www.facebook.com/events/${id}`);
        jQuery('#event_id_form').val(id);
      });
  });
  jQuery('#add-events li').each((index, target) => {
    const outerDiv = jQuery('<div class="add-button">');
    outerDiv.append(jQuery('<div class="whiten"></div>'));
    const id = jQuery(target).data('id');
    outerDiv.append(
      jQuery(
        '<button type="button" class="btn btn-primary" style="margin-left:60px; margin-top: 0.75em">Add Event</button>'
      )
        .attr('id', `button-${id}`)
        .on('click', addEvent)
    );
    jQuery(target).append(outerDiv);
  });
});
