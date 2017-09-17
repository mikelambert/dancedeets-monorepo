import json


def json_property(field):
    def getter(obj):
        assert getattr(obj, field.name), "Object %s did not have a value for %s" % (obj.key().name(), field.name)
        json_data = getattr(obj, field.name)
        result = json.loads(json_data)
        return result

    def setter(obj, value):
        # We sort so that strings are compare-able for changes
        json_data = json.dumps(value, sort_keys=True)
        setattr(obj, field.name, json_data)
        assert getattr(obj, field.name), "Object %s did not have a value for %s" % (obj.key().name(), field.name)

    return property(getter, setter)
