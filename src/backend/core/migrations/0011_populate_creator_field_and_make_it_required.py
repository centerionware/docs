# Generated by Django 5.1.2 on 2024-11-09 11:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations
from django.db.models import F, ForeignKey, Subquery, OuterRef, Q


def set_creator_from_document_access(apps, schema_editor):
    """
    Populate the `creator` field for existing Document records.

    This function assigns the `creator` field using the existing
    DocumentAccess entries. We can be sure that all documents have at
    least one user with "owner" role. If the document has several roles,
    it should take the entry with the oldest date of creation.

    The update is performed using efficient bulk queries with Django's
    Subquery and OuterRef to minimize database hits and ensure performance.

    Note: After running this migration, we quickly modify the schema to make
    the `creator` field required.
    """
    Document = apps.get_model("core", "Document")
    DocumentAccess = apps.get_model("core", "DocumentAccess")

    # Update `creator` using the "owner" role
    owner_subquery = DocumentAccess.objects.filter(
        document=OuterRef('pk'),
        user__isnull=False,
        role='owner',
    ).order_by('created_at').values('user_id')[:1]

    Document.objects.filter(
        creator__isnull=True
    ).update(creator=Subquery(owner_subquery))


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_add_field_creator_to_document'),
    ]

    operations = [
        migrations.RunPython(set_creator_from_document_access, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='document',
            name='creator',
            field=ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='documents_created', to=settings.AUTH_USER_MODEL),
        ),
    ]
