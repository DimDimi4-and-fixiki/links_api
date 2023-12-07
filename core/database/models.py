from tortoise import fields
from tortoise.expressions import Q
from tortoise.models import Model

__all__ = ['Site']


class Site(Model):
    id = fields.UUIDField(pk=True, description='Уникальный идентификатор')
    url = fields.TextField(description='URL веб-сайта')
    visited_at = fields.FloatField(description='Время посещения веб-сайта с начала эпохи')
    created_at = fields.DatetimeField(auto_now_add=True, description='Дата создания записи')

    @classmethod
    async def get_by_time_interval(cls, from_time: int, to_time: int) -> list['Site']:
        """Выбрать ссылки из временного промежутка
        Args:
            from_time: Начало временного интервала
            to_time: Конец временного интервала
        """
        return await cls.filter(Q(visited_at__gte=from_time) & Q(visited_at__lte=to_time))
