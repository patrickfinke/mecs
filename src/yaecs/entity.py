from uuid import uuid4 as _uuid4

def _generate_new_entity_id():
    uuid = _uuid4()
    entity = Entity(uuid.int)
    return entity

class Entity(str):
    def __repr__(self):
        return f"Entity({self})"

