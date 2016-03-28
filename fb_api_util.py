import fb_api


class LookupMetadata(fb_api.LookupType):
    version = "v2.5"

    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('fb_metadata', cls.url('%s?metadata=1' % object_id)),
        ]

    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (fb_api.USERLESS_UID, object_id, 'OBJ_METADATA')


def filter_by_type(fbl, id_list, obj_type):
    metadatas = fbl.get_multi(LookupMetadata, id_list)
    ids = [x['fb_metadata']['id'] for x in metadatas if x['fb_metadata']['metadata']['type'] == obj_type]
    return ids
