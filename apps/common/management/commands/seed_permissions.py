from django.core.management.base import BaseCommand

from apps.common.models import Permission


PERMISSIONS = [
    # Organization
    ("Organization", "View Organization", "organization.view"),
    ("Organization", "Create Organization", "organization.create"),
    ("Organization", "Update Organization", "organization.update"),
    ("Organization", "Delete Organization", "organization.delete"),

    # Branch
    ("Branch", "View Branch", "branch.view"),
    ("Branch", "Create Branch", "branch.create"),
    ("Branch", "Update Branch", "branch.update"),
    ("Branch", "Delete Branch", "branch.delete"),

    # Role
    ("Role", "View Role", "role.view"),
    ("Role", "Create Role", "role.create"),
    ("Role", "Update Role", "role.update"),
    ("Role", "Delete Role", "role.delete"),

    # Organization Member
    ("Organization Member", "View Member", "member.view"),
    ("Organization Member", "Create Member", "member.create"),
    ("Organization Member", "Update Member", "member.update"),
    ("Organization Member", "Delete Member", "member.delete"),
]


class Command(BaseCommand):

    help = "Seeds default system permissions."

    def handle(self, *args, **options):

        created = 0

        for module, name, code in PERMISSIONS:

            _, is_created = Permission.objects.get_or_create(
                code=code,
                defaults={
                    "module": module,
                    "name": name,
                },
            )

            if is_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{created} permissions created successfully."
            )
        )