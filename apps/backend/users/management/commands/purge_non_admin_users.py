import logging

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import models, transaction
from social.models import Album, Comment, Follow, Like, Photo, Post
from todos.models import TodoItem, TodoList, TodoSubItem

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "🚨 DANGER: Permanently delete all non-admin users and their related content. Use --dry-run first!"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Show what would be deleted without actually deleting (RECOMMENDED FIRST)",
        )
        parser.add_argument(
            "--keep",
            action="append",
            default=[],
            help="Usernames or emails to preserve (can be used multiple times)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            default=False,
            help="Skip confirmation prompt (use with extreme caution)",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        keep_list = options["keep"]
        force = options["force"]

        # Safety check
        if not dry_run and not force:
            self.stdout.write(
                self.style.WARNING(
                    "🚨 DANGER: This will permanently delete all non-admin users!"
                )
            )
            self.stdout.write("This operation cannot be undone.")

            # Count what will be deleted
            deletion_summary = self.get_deletion_summary(keep_list)
            self.display_summary(deletion_summary, dry_run=True)

            confirm = input('\nType "PURGE_NON_ADMIN_USERS" to confirm: ')
            if confirm != "PURGE_NON_ADMIN_USERS":
                self.stdout.write(self.style.ERROR("Operation cancelled."))
                return

        try:
            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS("🔍 DRY RUN MODE - No data will be deleted")
                )
                deletion_summary = self.get_deletion_summary(keep_list)
                self.display_summary(deletion_summary, dry_run=True)
            else:
                self.stdout.write(self.style.WARNING("🚨 PURGING NON-ADMIN USERS..."))
                deletion_summary = self.purge_users(keep_list)
                self.display_summary(deletion_summary, dry_run=False)

                # Log the operation
                logger.warning(
                    f"PURGE_NON_ADMIN_USERS executed. "
                    f'Deleted {deletion_summary["users"]} users and {deletion_summary["total_related"]} related objects. '
                    f'Kept: {deletion_summary["kept_users"]}'
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error during purge: {str(e)}"))
            logger.error(f"PURGE_NON_ADMIN_USERS failed: {str(e)}")
            raise CommandError(f"Purge failed: {str(e)}")

    def get_deletion_summary(self, keep_list):
        """Get summary of what would be deleted"""
        # Users to preserve
        preserved_users = self.get_preserved_users(keep_list)
        preserved_user_ids = list(preserved_users.values_list("id", flat=True))

        # Users to delete
        users_to_delete = User.objects.exclude(id__in=preserved_user_ids)

        # Count related objects
        summary = {
            "users": users_to_delete.count(),
            "posts": Post.objects.filter(user__in=users_to_delete).count(),
            "comments": Comment.objects.filter(user__in=users_to_delete).count(),
            "likes": Like.objects.filter(user__in=users_to_delete).count(),
            "albums": Album.objects.filter(user__in=users_to_delete).count(),
            "photos": Photo.objects.filter(album__user__in=users_to_delete).count(),
            "follows": Follow.objects.filter(
                models.Q(follower__in=users_to_delete)
                | models.Q(followed__in=users_to_delete)
            ).count(),
            "todo_lists": TodoList.objects.filter(user__in=users_to_delete).count(),
            "todo_items": TodoItem.objects.filter(
                list__user__in=users_to_delete
            ).count(),
            "todo_sub_items": TodoSubItem.objects.filter(
                parent__list__user__in=users_to_delete
            ).count(),
            "kept_users": preserved_users.count(),
            "kept_usernames": list(preserved_users.values_list("username", flat=True)),
        }

        summary["total_related"] = (
            summary["posts"]
            + summary["comments"]
            + summary["likes"]
            + summary["albums"]
            + summary["photos"]
            + summary["follows"]
            + summary["todo_lists"]
            + summary["todo_items"]
            + summary["todo_sub_items"]
        )

        return summary

    def get_preserved_users(self, keep_list):
        """Get users that should be preserved"""
        preserved = User.objects.filter(is_superuser=True)

        if keep_list:
            # Add users from keep_list (by username or email)
            keep_users = User.objects.filter(
                models.Q(username__in=keep_list) | models.Q(email__in=keep_list)
            )
            preserved = preserved | keep_users

        return preserved.distinct()

    def purge_users(self, keep_list):
        """Actually delete the users and related content"""
        with transaction.atomic():
            # Get users to preserve
            preserved_users = self.get_preserved_users(keep_list)
            preserved_user_ids = list(preserved_users.values_list("id", flat=True))

            # Get users to delete
            users_to_delete = User.objects.exclude(id__in=preserved_user_ids)

            # Delete in proper order to handle CASCADE relationships
            # First, delete objects that might have PROTECT relationships

            # Delete follows (both as follower and followed)
            Follow.objects.filter(
                models.Q(follower__in=users_to_delete)
                | models.Q(followed__in=users_to_delete)
            ).delete()

            # Delete likes
            Like.objects.filter(user__in=users_to_delete).delete()

            # Delete comments
            Comment.objects.filter(user__in=users_to_delete).delete()

            # Delete photos (albums will cascade)
            Photo.objects.filter(album__user__in=users_to_delete).delete()

            # Delete albums
            Album.objects.filter(user__in=users_to_delete).delete()

            # Delete todo sub-items
            TodoSubItem.objects.filter(parent__list__user__in=users_to_delete).delete()

            # Delete todo items
            TodoItem.objects.filter(list__user__in=users_to_delete).delete()

            # Delete todo lists
            TodoList.objects.filter(user__in=users_to_delete).delete()

            # Delete posts
            Post.objects.filter(user__in=users_to_delete).delete()

            # Finally, delete the users
            deleted_count = users_to_delete.count()
            users_to_delete.delete()

            # Get final summary
            return self.get_deletion_summary(keep_list)

    def display_summary(self, summary, dry_run):
        """Display deletion summary"""
        mode = "WOULD DELETE" if dry_run else "DELETED"

        self.stdout.write(f"\n📊 {mode} SUMMARY:")
        self.stdout.write("=" * 50)

        # Users
        self.stdout.write(f'👥 Users: {summary["users"]}')

        # Social content
        self.stdout.write("\n📱 Social Content:")
        self.stdout.write(f'  📝 Posts: {summary["posts"]}')
        self.stdout.write(f'  💬 Comments: {summary["comments"]}')
        self.stdout.write(f'  ❤️  Likes: {summary["likes"]}')
        self.stdout.write(f'  📸 Albums: {summary["albums"]}')
        self.stdout.write(f'  🖼️  Photos: {summary["photos"]}')
        self.stdout.write(f'  🔗 Follows: {summary["follows"]}')

        # Todos
        self.stdout.write("\n✅ Todo Content:")
        self.stdout.write(f'  📋 Lists: {summary["todo_lists"]}')
        self.stdout.write(f'  ☑️  Items: {summary["todo_items"]}')
        self.stdout.write(f'  🔸 Sub-items: {summary["todo_sub_items"]}')

        # Totals
        self.stdout.write("\n📈 Totals:")
        self.stdout.write(f'  🎯 Total Related Objects: {summary["total_related"]}')
        self.stdout.write(
            f'  💾 Total Storage Impact: ~{summary["total_related"] * 0.1:.1f} MB'
        )

        # Preserved users
        self.stdout.write(f'\n🛡️  Preserved Users: {summary["kept_users"]}')
        if summary["kept_usernames"]:
            self.stdout.write(f'  📝 Usernames: {", ".join(summary["kept_usernames"])}')

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\n⚠️  This is a DRY RUN. No data was actually deleted."
                )
            )
            self.stdout.write("To actually delete, run without --dry-run flag.")
        else:
            self.stdout.write(self.style.SUCCESS("\n✅ Purge completed successfully!"))
            self.stdout.write(
                f'Deleted {summary["users"]} users and {summary["total_related"]} related objects.'
            )
