import json
# честно украдено с
# https://blog.mosthege.net/2016/11/12/json-deserialization-of-nested-objects/
 
class JsonConvert(object):
    mappings = {}
     
    @classmethod
    def class_mapper(cls, d):
        for keys, kls in cls.mappings.items():
            if keys.issuperset(d.keys()):   # are all required arguments present?
                return kls(**d)
        else:
            # Raise exception instead of silently returning None
            raise ValueError('Unable to find a matching class for object: {!s}'.format(d))
     
    @classmethod
    def complex_handler(cls, Obj):
        if hasattr(Obj, '__dict__'):
            return Obj.__dict__
        else:
            raise TypeError('Object of type %s with value of %s is not JSON serializable' % (type(Obj), repr(Obj)))
 
    @classmethod
    def register(cls, kls):
        cls.mappings[frozenset(tuple([attr for attr,val in kls().__dict__.items()]))] = kls
        return kls
 
    @classmethod
    def toJSON(cls, obj):
        return json.dumps(obj.__dict__, default=cls.complex_handler, indent=4)
 
    @classmethod
    def fromJSON(cls, json_str):
        return json.loads(json_str, object_hook=cls.class_mapper)
     
    @classmethod
    def toFile(cls, obj, path):
        with open(path, 'w') as jfile:
            jfile.writelines([cls.ToJSON(obj)])
        return path
 
    @classmethod
    def fromFile(cls, filepath):
        result = None
        with open(filepath, 'r') as jfile:
            result = cls.FromJSON(jfile.read())
        return result