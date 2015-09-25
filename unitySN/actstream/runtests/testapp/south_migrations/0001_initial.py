# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Player'
        db.create_table('testapp_player', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('testapp', ['Player'])

        # Adding model 'Unregistered'
        db.create_table('testapp_unregistered', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('testapp', ['Unregistered'])


    def backwards(self, orm):
        # Deleting model 'Player'
        db.delete_table('testapp_player')

        # Deleting model 'Unregistered'
        db.delete_table('testapp_unregistered')


    models = {
        'actstream.action': {
            'Meta': {'ordering': "(u'-timestamp',)", 'object_name': 'Action'},
            'action_object_content_type': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'blank': 'True', 'to': "orm['contenttypes.ContentType']", 'related_name': "u'action_object'"}),
            'action_object_object_id': ('django.db.models.fields.CharField', [], {'null': 'True', 'blank': 'True', 'max_length': '255', 'db_index': 'True'}),
            'actor_content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'related_name': "u'actor'"}),
            'actor_object_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'data': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'db_index': 'True', 'default': 'True'}),
            'target_content_type': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'blank': 'True', 'to': "orm['contenttypes.ContentType']", 'related_name': "u'target'"}),
            'target_object_id': ('django.db.models.fields.CharField', [], {'null': 'True', 'blank': 'True', 'max_length': '255', 'db_index': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'default': 'datetime.datetime.now'}),
            'verb': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'db_table': "'django_content_type'", 'unique_together': "(('app_label', 'model'),)", 'ordering': "('name',)", 'object_name': 'ContentType'},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'testapp.player': {
            'Meta': {'object_name': 'Player'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'testapp.unregistered': {
            'Meta': {'object_name': 'Unregistered'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['testapp']