import fb_api

from logic import event_smart_classifier

batch_lookup = CommonBatchLookup(None, None)
batch_lookup.lookup_event(event_id)
batch_lookup.finish_loading()
event_data = batch_lookup.data_for_event(event_id)

#event_data = event_data['info']

print event_smart_classifier.predict_types_for_event(fb_event)
