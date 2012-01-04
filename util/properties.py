import json

def json_property(field):
    def getter(obj):
        assert getattr(obj, field.name), "Object %s did not have a value for %s" % (obj.key().name(), field.name)
        json = getattr(obj, field.name)
        result = json.loads(json)
        return result

    def setter(obj, value):
        json = json.dumps(value)
        setattr(obj, field.name, json)
        assert getattr(obj, field.name), "Object %s did not have a value for %s" % (obj.key().name(), field.name)

    return property(getter, setter)

