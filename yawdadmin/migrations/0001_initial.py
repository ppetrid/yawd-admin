# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import yawdadmin.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('optionset_label', models.CharField(max_length=50)),
                ('name', yawdadmin.fields.OptionNameField(max_length=50)),
                ('value', models.TextField(null=True)),
                ('lang_dependant', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['optionset_label', 'lang_dependant'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='appoption',
            unique_together=set([('optionset_label', 'name')]),
        ),
    ]
