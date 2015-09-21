# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'uploadedImage'
        db.create_table(u'userprofiles_uploadedimage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=300, null=True, blank=True)),
        ))
        db.send_create_signal(u'userprofiles', ['uploadedImage'])

        # Adding model 'Activities'
        db.create_table(u'userprofiles_activities', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('activity', self.gf('django.db.models.fields.CharField')(max_length=200L)),
        ))
        db.send_create_signal(u'userprofiles', ['Activities'])

        # Adding model 'UserProfile'
        db.create_table(u'userprofiles_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['roleapp.Role'])),
            ('aboutMe', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('displayName', self.gf('django.db.models.fields.CharField')(max_length=45L, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=45L, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=45L, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=45L, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=45L, blank=True)),
            ('thumbnailURL', self.gf('django.db.models.fields.CharField')(default='/static/main/img/user.png', max_length=200L, db_column='thumbnailURL', blank=True)),
            ('studies', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('birthday', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('favouriteFood', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('favouriteSport', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=45L, blank=True)),
            ('interests', self.gf('django.db.models.fields.CharField')(max_length=45L, blank=True)),
        ))
        db.send_create_signal(u'userprofiles', ['UserProfile'])

        # Adding M2M table for field activities on 'UserProfile'
        m2m_table_name = db.shorten_name(u'userprofiles_userprofile_activities')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm[u'userprofiles.userprofile'], null=False)),
            ('activities', models.ForeignKey(orm[u'userprofiles.activities'], null=False))
        ))
        db.create_unique(m2m_table_name, ['userprofile_id', 'activities_id'])


    def backwards(self, orm):
        # Deleting model 'uploadedImage'
        db.delete_table(u'userprofiles_uploadedimage')

        # Deleting model 'Activities'
        db.delete_table(u'userprofiles_activities')

        # Deleting model 'UserProfile'
        db.delete_table(u'userprofiles_userprofile')

        # Removing M2M table for field activities on 'UserProfile'
        db.delete_table(db.shorten_name(u'userprofiles_userprofile_activities'))


    models = {
        u'actstream_old.action': {
            'Meta': {'ordering': "('-timestamp',)", 'object_name': 'Action'},
            'action_object_content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'action_object'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'action_object_object_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'actor_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actor'", 'to': u"orm['contenttypes.ContentType']"}),
            'actor_object_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'data': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'target_content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'target'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'target_object_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'verb': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'relationships': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'related_to'", 'symmetrical': 'False', 'through': u"orm['relationships.Relationship']", 'to': u"orm['auth.User']"}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'relationships.relationship': {
            'Meta': {'ordering': "('created',)", 'unique_together': "(('from_user', 'to_user', 'status', 'site'),)", 'object_name': 'Relationship'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from_users'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "'relationships'", 'to': u"orm['sites.Site']"}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['relationships.RelationshipStatus']"}),
            'to_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to_users'", 'to': u"orm['auth.User']"}),
            'weight': ('django.db.models.fields.FloatField', [], {'default': '1.0', 'null': 'True', 'blank': 'True'})
        },
        u'relationships.relationshipstatus': {
            'Meta': {'ordering': "('name',)", 'object_name': 'RelationshipStatus'},
            'from_role': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'from_role'", 'null': 'True', 'to': u"orm['roleapp.Role']"}),
            'from_slug': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'login_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'symmetrical_slug': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'to_role': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'to_role'", 'null': 'True', 'to': u"orm['roleapp.Role']"}),
            'to_slug': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'verb': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'roleapp.role': {
            'Meta': {'object_name': 'Role'},
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '100L', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50L', 'null': 'True'})
        },
        u'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'userprofiles.activities': {
            'Meta': {'object_name': 'Activities'},
            'activity': ('django.db.models.fields.CharField', [], {'max_length': '200L'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'userprofiles.uploadedimage': {
            'Meta': {'object_name': 'uploadedImage'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'})
        },
        u'userprofiles.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'aboutMe': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'activities': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['userprofiles.Activities']", 'symmetrical': 'False', 'blank': 'True'}),
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'displayName': ('django.db.models.fields.CharField', [], {'max_length': '45L', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '45L', 'blank': 'True'}),
            'favouriteFood': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'favouriteSport': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '45L', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interests': ('django.db.models.fields.CharField', [], {'max_length': '45L', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '45L', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '45L', 'blank': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['roleapp.Role']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '45L', 'blank': 'True'}),
            'studies': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'thumbnailURL': ('django.db.models.fields.CharField', [], {'default': "'/static/main/img/user.png'", 'max_length': '200L', 'db_column': "'thumbnailURL'", 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['userprofiles']