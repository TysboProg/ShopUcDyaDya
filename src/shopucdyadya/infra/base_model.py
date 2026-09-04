from shopucdyadya.infra.mixins.created_at import CreatedAtMixin
from shopucdyadya.infra.mixins.updated_at import UpdatedAtMixin
from shopucdyadya.infra.mixins.uuid_id import UUIDIDMixin


class Base(UUIDIDMixin, CreatedAtMixin, UpdatedAtMixin):
    pass
