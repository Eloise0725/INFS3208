from django.core.management.base import BaseCommand, CommandError
from lessons.models import SchoolTerm, CustomUser as User


class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.filter(is_staff=False, is_superuser=False).delete()
        SchoolTerm.objects.all().delete()
