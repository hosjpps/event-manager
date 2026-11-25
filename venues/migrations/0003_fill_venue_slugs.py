from django.db import migrations

from venues.slugs import make_slug


def fill_slugs(apps, schema_editor):
    Venue = apps.get_model("venues", "Venue")
    for venue in Venue.objects.all():
        venue.slug = make_slug(venue.name, venue.pk)
        venue.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("venues", "0002_venue_slug_is_large"),
    ]

    operations = [
        migrations.RunPython(fill_slugs, migrations.RunPython.noop),
    ]
