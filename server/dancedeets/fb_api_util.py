import fb_api


class LookupMetadata(fb_api.LookupType):
    @classmethod
    def get_lookups(cls, object_id):
        return [
            ('fb_metadata', cls.url('%s' % object_id, metadata='1')),
        ]

    @classmethod
    def cache_key(cls, object_id, fetching_uid):
        return (fb_api.USERLESS_UID, object_id, 'OBJ_METADATA')


def filter_by_type(fbl, id_list, obj_type):
    metadatas = fbl.get_multi(LookupMetadata, id_list)
    ids = [x['fb_metadata']['id'] for x in metadatas if not x['empty'] and x['fb_metadata']['metadata']['type'] == obj_type]
    return ids
