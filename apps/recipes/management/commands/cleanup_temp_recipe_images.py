from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.recipes.models import TemporaryRecipeImage


class Command(BaseCommand):
    help = "古い一時レシピ画像を削除"

    def handle(self, *args, **options):
        delete_target_date = timezone.now() - timedelta(hours=24)

        old_images = TemporaryRecipeImage.objects.filter(
            created_at__lt=delete_target_date
        )

        delete_count = old_images.count()

        for image in old_images:
            if image.image:
                image.image.delete(save=False)

            image.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"{delete_count}件の一時画像を削除しました"
            )
        )