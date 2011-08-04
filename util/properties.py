from django.utils import simplejson

def json_property(field):
    def getter(obj):
        assert getattr(obj, field.name), "Object %s did not have a value for %s" % (obj.key().name(), field.name)
        json = getattr(obj, field.name)
        result = simplejson.loads(json)
        return result

    def setter(obj, value):
        json = simplejson.dumps(value)
        setattr(obj, field.name, json)
        assert getattr(obj, field.name), "Object %s did not have a value for %s" % (obj.key().name(), field.name)

    return property(getter, setter)

