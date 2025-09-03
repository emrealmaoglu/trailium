from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import TodoItem, TodoList, TodoSubItem


def _recalc_item_progress(item: TodoItem) -> None:
    total = item.subitems.count()
    done = item.subitems.filter(is_done=True).count()
    pct = (
        100
        if (total == 0 and item.is_done)
        else int(round((done / total) * 100)) if total else (100 if item.is_done else 0)
    )
    if item.progress_cached != pct:
        item.progress_cached = pct
        item.save(update_fields=["progress_cached", "updated_at"])


def _recalc_list_progress(tlist: TodoList) -> None:
    items = tlist.items.all()
    if not items.exists():
        pct = 0
    else:
        pct = int(round(sum(i.progress_cached for i in items) / items.count()))
    if tlist.progress_cached != pct:
        tlist.progress_cached = pct
        tlist.save(update_fields=["progress_cached", "updated_at"])


@receiver([post_save, post_delete], sender=TodoSubItem)
def recalc_on_subitem_change(sender, instance: TodoSubItem, **kwargs):
    _recalc_item_progress(instance.parent)
    _recalc_list_progress(instance.parent.list)


@receiver([post_save, post_delete], sender=TodoItem)
def recalc_on_item_change(sender, instance: TodoItem, **kwargs):
    _recalc_item_progress(instance)
    _recalc_list_progress(instance.list)
