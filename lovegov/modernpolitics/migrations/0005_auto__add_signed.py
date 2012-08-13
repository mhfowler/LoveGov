# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Signed'
        db.create_table('modernpolitics_signed', (
            ('ucrelationship_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.UCRelationship'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('modernpolitics', ['Signed'])


    def backwards(self, orm):
        # Deleting model 'Signed'
        db.delete_table('modernpolitics_signed')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'modernpolitics.action': {
            'Meta': {'object_name': 'Action'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifier': ('django.db.models.fields.CharField', [], {'default': "'D'", 'max_length': '1'}),
            'must_notify': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'PUB'", 'max_length': '3'}),
            'relationship': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Relationship']", 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'verbose': ('django.db.models.fields.TextField', [], {}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'modernpolitics.aggregateresponse': {
            'Meta': {'object_name': 'AggregateResponse', '_ormbases': ['modernpolitics.Response']},
            'answer_avg': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '4', 'decimal_places': '2'}),
            'response_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Response']", 'unique': 'True', 'primary_key': 'True'}),
            'responses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.AggregateTuple']", 'symmetrical': 'False'}),
            'total': ('django.db.models.fields.IntegerField', [], {}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.UserProfile']", 'symmetrical': 'False'})
        },
        'modernpolitics.aggregatetuple': {
            'Meta': {'object_name': 'AggregateTuple'},
            'answer_val': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tally': ('django.db.models.fields.IntegerField', [], {})
        },
        'modernpolitics.anonid': {
            'Meta': {'object_name': 'AnonID'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'modernpolitics.answer': {
            'Meta': {'object_name': 'Answer'},
            'answer_text': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'modernpolitics.attending': {
            'Meta': {'object_name': 'Attending', '_ormbases': ['modernpolitics.UCRelationship']},
            'choice': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'declined': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'invited': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'inviter': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'rejected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'requested': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ucrelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UCRelationship']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.basicinfo': {
            'Meta': {'object_name': 'BasicInfo'},
            'address': ('lovegov.beta.modernpolitics.custom_fields.ListField', [], {}),
            'dob': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'ethnicity': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invite_message': ('django.db.models.fields.CharField', [], {'default': '"LoveGov Alpha is now up and running! We would really appreciate it if you logged in and test run the features of our site. Please keep in mind that Alpha only contains a portion of the functionality intended for the Brown/RISD beta, so you will see us regularly adding new features over the next month. If you encounter any problems while using our siteor just want to send us comments then please don\'t hesitate to contact us - we want to hear your opinions!"', 'max_length': '10000', 'blank': 'True'}),
            'invite_subject': ('django.db.models.fields.CharField', [], {'default': "'Welcome to LoveGov Alpha'", 'max_length': '1000', 'blank': 'True'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'nick_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'party': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'political_role': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'profile_image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserImage']", 'null': 'True'}),
            'religion': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'blank': 'True'}),
            'url': ('lovegov.beta.modernpolitics.custom_fields.ListField', [], {}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'})
        },
        'modernpolitics.bug': {
            'Meta': {'object_name': 'Bug'},
            'error': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'modernpolitics.comment': {
            'Meta': {'object_name': 'Comment', '_ormbases': ['modernpolitics.Content']},
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'creator_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'on_content': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': "orm['modernpolitics.Content']"}),
            'root_content': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'root_content'", 'to': "orm['modernpolitics.Content']"}),
            'text': ('django.db.models.fields.TextField', [], {'max_length': '1000'})
        },
        'modernpolitics.commented': {
            'Meta': {'object_name': 'Commented', '_ormbases': ['modernpolitics.UCRelationship']},
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Comment']"}),
            'ucrelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UCRelationship']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.committee': {
            'Meta': {'object_name': 'Committee'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.ElectedOfficial']", 'through': "orm['modernpolitics.CommitteeMember']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Committee']", 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        'modernpolitics.committeemember': {
            'Meta': {'object_name': 'CommitteeMember'},
            'committee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Committee']"}),
            'electedOfficial': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.ElectedOfficial']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.CongressSessions']"})
        },
        'modernpolitics.congressroll': {
            'Meta': {'object_name': 'CongressRoll'},
            'amendment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.LegislationAmendment']", 'null': 'True'}),
            'aye': ('django.db.models.fields.IntegerField', [], {}),
            'bill': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Legislation']", 'null': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nay': ('django.db.models.fields.IntegerField', [], {}),
            'nv': ('django.db.models.fields.IntegerField', [], {}),
            'options': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.RollOption']", 'symmetrical': 'False'}),
            'present': ('django.db.models.fields.IntegerField', [], {}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'required': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'roll_number': ('django.db.models.fields.IntegerField', [], {}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.CongressSessions']"}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {}),
            'voters': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.ElectedOfficial']", 'through': "orm['modernpolitics.VotingRecord']", 'symmetrical': 'False'}),
            'where': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        'modernpolitics.congresssessions': {
            'Meta': {'object_name': 'CongressSessions'},
            'people': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.ElectedOfficial']", 'symmetrical': 'False'}),
            'session': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        'modernpolitics.content': {
            'Meta': {'object_name': 'Content'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'alias': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '30'}),
            'calculated_view': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.WorldView']", 'null': 'True'}),
            'created_when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"}),
            'downvotes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_calc': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'in_feed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'in_search': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'level': ('django.db.models.fields.CharField', [], {'default': "'F'", 'max_length': '1'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserPhysicalAddress']", 'null': 'True'}),
            'main_image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserImage']", 'null': 'True'}),
            'main_topic': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'maintopic'", 'null': 'True', 'to': "orm['modernpolitics.Topic']"}),
            'num_comments': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'PUB'", 'max_length': '3'}),
            'rank': ('django.db.models.fields.DecimalField', [], {'default': "'0.0'", 'max_digits': '4', 'decimal_places': '2'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'summary': ('django.db.models.fields.TextField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'topics': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.Topic']", 'symmetrical': 'False'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'upvotes': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'modernpolitics.controllinguser': {
            'Meta': {'object_name': 'ControllingUser', '_ormbases': ['auth.User']},
            'permissions': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserPermission']", 'null': 'True'}),
            'user_profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']", 'null': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.created': {
            'Meta': {'object_name': 'Created', '_ormbases': ['modernpolitics.UCRelationship']},
            'ucrelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UCRelationship']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.customnotificationsetting': {
            'Meta': {'object_name': 'CustomNotificationSetting'},
            'alerts': ('lovegov.beta.modernpolitics.custom_fields.ListField', [], {}),
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Content']", 'null': 'True'}),
            'email': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']", 'null': 'True'})
        },
        'modernpolitics.debate': {
            'Meta': {'object_name': 'Debate', '_ormbases': ['modernpolitics.Content']},
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'debate_when': ('django.db.models.fields.DateTimeField', [], {}),
            'full_descript': ('django.db.models.fields.TextField', [], {'max_length': '10000'}),
            'moderator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'moderator'", 'to': "orm['modernpolitics.UserProfile']"})
        },
        'modernpolitics.debatejoined': {
            'Meta': {'object_name': 'DebateJoined', '_ormbases': ['modernpolitics.UCRelationship']},
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'debate': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Persistent']"}),
            'declined': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'invited': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'inviter': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'rejected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'requested': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ucrelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UCRelationship']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.debatemessage': {
            'Meta': {'object_name': 'DebateMessage', '_ormbases': ['modernpolitics.Content']},
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'debate_side': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '3000'}),
            'message_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Debate']"}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'modernpolitics.debateresult': {
            'Meta': {'object_name': 'DebateResult'},
            'debate': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'modernpolitics.debaters': {
            'Meta': {'object_name': 'Debaters', '_ormbases': ['modernpolitics.UCRelationship']},
            'side': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'ucrelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UCRelationship']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.debatevoted': {
            'Meta': {'object_name': 'DebateVoted', '_ormbases': ['modernpolitics.UCRelationship']},
            'ucrelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UCRelationship']", 'unique': 'True', 'primary_key': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'modernpolitics.deleted': {
            'Meta': {'object_name': 'Deleted', '_ormbases': ['modernpolitics.UCRelationship']},
            'ucrelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UCRelationship']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.edited': {
            'Meta': {'object_name': 'Edited', '_ormbases': ['modernpolitics.UCRelationship']},
            'ucrelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UCRelationship']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.electedofficial': {
            'Meta': {'object_name': 'ElectedOfficial', '_ormbases': ['modernpolitics.UserProfile']},
            'bioguide_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'govtrack_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'metavid_id': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True'}),
            'official_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'os_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'pvs_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'twitter_id': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True'}),
            'userprofile_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UserProfile']", 'unique': 'True', 'primary_key': 'True'}),
            'youtube_id': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True'})
        },
        'modernpolitics.emaillist': {
            'Meta': {'object_name': 'EmailList'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'modernpolitics.event': {
            'Meta': {'object_name': 'Event', '_ormbases': ['modernpolitics.Content']},
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'datetime_of_event': ('django.db.models.fields.DateTimeField', [], {}),
            'full_text': ('django.db.models.fields.TextField', [], {'max_length': '10000'})
        },
        'modernpolitics.feed': {
            'Meta': {'object_name': 'Feed'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.FeedItem']", 'symmetrical': 'False'})
        },
        'modernpolitics.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'feedback': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'modernpolitics.feeditem': {
            'Meta': {'object_name': 'FeedItem'},
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Content']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rank': ('django.db.models.fields.IntegerField', [], {})
        },
        'modernpolitics.filtersetting': {
            'Meta': {'object_name': 'FilterSetting'},
            'algo': ('django.db.models.fields.CharField', [], {'default': "'D'", 'max_length': '1'}),
            'alias': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '30'}),
            'by_topic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'by_type': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'days': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'hot_window': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'similarity': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'topic_weights': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.TopicWeight']", 'symmetrical': 'False'}),
            'type_weights': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.TypeWeight']", 'symmetrical': 'False'})
        },
        'modernpolitics.followed': {
            'Meta': {'object_name': 'Followed', '_ormbases': ['modernpolitics.UCRelationship']},
            'ucrelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UCRelationship']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.forum': {
            'Meta': {'object_name': 'Forum', '_ormbases': ['modernpolitics.Content']},
            'children': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'children'", 'symmetrical': 'False', 'to': "orm['modernpolitics.Content']"}),
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parent'", 'null': 'True', 'to': "orm['modernpolitics.Content']"})
        },
        'modernpolitics.group': {
            'Meta': {'object_name': 'Group', '_ormbases': ['modernpolitics.Content']},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'admin'", 'symmetrical': 'False', 'to': "orm['modernpolitics.UserProfile']"}),
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'democratic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'full_text': ('django.db.models.fields.TextField', [], {'max_length': '1000'}),
            'group_bestfeed': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'groupbest'", 'symmetrical': 'False', 'to': "orm['modernpolitics.FeedItem']"}),
            'group_content': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'ongroup'", 'symmetrical': 'False', 'to': "orm['modernpolitics.Content']"}),
            'group_hotfeed': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'grouphot'", 'symmetrical': 'False', 'to': "orm['modernpolitics.FeedItem']"}),
            'group_newfeed': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'groupnew'", 'symmetrical': 'False', 'to': "orm['modernpolitics.FeedItem']"}),
            'group_privacy': ('django.db.models.fields.CharField', [], {'default': "'O'", 'max_length': '1'}),
            'group_type': ('django.db.models.fields.CharField', [], {'default': "'U'", 'max_length': '1'}),
            'group_view': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.WorldView']"}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'member'", 'symmetrical': 'False', 'to': "orm['modernpolitics.UserProfile']"}),
            'system': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'modernpolitics.groupjoined': {
            'Meta': {'object_name': 'GroupJoined', '_ormbases': ['modernpolitics.UCRelationship']},
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'declined': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Group']"}),
            'invited': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'inviter': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'rejected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'requested': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ucrelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UCRelationship']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.involved': {
            'Meta': {'object_name': 'Involved'},
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Content']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'involvement': ('django.db.models.fields.IntegerField', [], {}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'modernpolitics.legislation': {
            'Meta': {'object_name': 'Legislation', '_ormbases': ['modernpolitics.Content']},
            'bill_number': ('django.db.models.fields.IntegerField', [], {}),
            'bill_relation': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.Legislation']", 'null': 'True', 'symmetrical': 'False'}),
            'bill_session': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'bill_status': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.LegislationStatus']", 'unique': 'True'}),
            'bill_summary': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'bill_type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'bill_updated': ('django.db.models.fields.DateTimeField', [], {}),
            'committees': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.Committee']", 'null': 'True', 'through': "orm['modernpolitics.LegislationCommittee']", 'symmetrical': 'False'}),
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'cosponsors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.ElectedOfficial']", 'through': "orm['modernpolitics.LegislationCosponsor']", 'symmetrical': 'False'}),
            'introduced_datetime': ('django.db.models.fields.DateField', [], {}),
            'sponsor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sponsor_id'", 'null': 'True', 'to': "orm['modernpolitics.ElectedOfficial']"}),
            'state_datetime': ('django.db.models.fields.DateField', [], {}),
            'state_text': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'subjects': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.LegislationSubjects']", 'symmetrical': 'False'})
        },
        'modernpolitics.legislationaction': {
            'Meta': {'object_name': 'LegislationAction'},
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'bill': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Legislation']"}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'refer_committee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Committee']", 'null': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True'})
        },
        'modernpolitics.legislationamendment': {
            'Meta': {'object_name': 'LegislationAmendment'},
            'amends_sequence': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'chamber': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'committee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Committee']", 'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '50000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'legislation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Legislation']", 'null': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'offered_datetime': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'purpose': ('django.db.models.fields.TextField', [], {'max_length': '5000'}),
            'session': ('django.db.models.fields.IntegerField', [], {}),
            'sponsor_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.ElectedOfficial']", 'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'status_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'modernpolitics.legislationcalendar': {
            'Meta': {'object_name': 'LegislationCalendar', '_ormbases': ['modernpolitics.LegislationAction']},
            'calendar': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'calendar_number': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'legislationaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.LegislationAction']", 'unique': 'True', 'primary_key': 'True'}),
            'under': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
        },
        'modernpolitics.legislationcommittee': {
            'Meta': {'object_name': 'LegislationCommittee'},
            'activity': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'committee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Committee']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'legislation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Legislation']"})
        },
        'modernpolitics.legislationcosponsor': {
            'Meta': {'object_name': 'LegislationCosponsor'},
            'elected_official': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.ElectedOfficial']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'joined': ('django.db.models.fields.DateField', [], {}),
            'legislation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Legislation']"})
        },
        'modernpolitics.legislationenacted': {
            'Meta': {'object_name': 'LegislationEnacted', '_ormbases': ['modernpolitics.LegislationAction']},
            'legislationaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.LegislationAction']", 'unique': 'True', 'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
        },
        'modernpolitics.legislationreflabel': {
            'Meta': {'object_name': 'LegislationRefLabel'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.LegislationAction']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'ref': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        },
        'modernpolitics.legislationsigned': {
            'Meta': {'object_name': 'LegislationSigned', '_ormbases': ['modernpolitics.LegislationAction']},
            'legislationaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.LegislationAction']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.legislationstatus': {
            'Meta': {'object_name': 'LegislationStatus'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'how': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'roll': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'status_text': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'where': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True'})
        },
        'modernpolitics.legislationsubjects': {
            'Meta': {'object_name': 'LegislationSubjects'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term_name': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'modernpolitics.legislationtitle': {
            'Meta': {'object_name': 'LegislationTitle'},
            'bill': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Legislation']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'title_as': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'title_type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'modernpolitics.legislationtopresident': {
            'Meta': {'object_name': 'LegislationToPresident', '_ormbases': ['modernpolitics.LegislationAction']},
            'legislationaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.LegislationAction']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.legislationvote': {
            'Meta': {'object_name': 'LegislationVote', '_ormbases': ['modernpolitics.LegislationAction']},
            'how': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True'}),
            'legislationaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.LegislationAction']", 'unique': 'True', 'primary_key': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'roll': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'suspension': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'vote_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'where': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True'})
        },
        'modernpolitics.lgnumber': {
            'Meta': {'object_name': 'LGNumber'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {})
        },
        'modernpolitics.linked': {
            'Meta': {'object_name': 'Linked'},
            'association_strength': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'from_content': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fcontent'", 'to': "orm['modernpolitics.Content']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link_bonus': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'link_strength': ('django.db.models.fields.IntegerField', [], {}),
            'to_content': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tcontent'", 'to': "orm['modernpolitics.Content']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'modernpolitics.lovegov': {
            'Meta': {'object_name': 'LoveGov'},
            'anon_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']", 'null': 'True'}),
            'average_rating': ('django.db.models.fields.IntegerField', [], {'default': '50'}),
            'average_votes': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'best_filter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bestfilter'", 'null': 'True', 'to': "orm['modernpolitics.FilterSetting']"}),
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'default_filter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'defaultfilter'", 'null': 'True', 'to': "orm['modernpolitics.FilterSetting']"}),
            'default_image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserImage']", 'null': 'True'}),
            'hot_filter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'hotfilter'", 'null': 'True', 'to': "orm['modernpolitics.FilterSetting']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lovegov_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'anonuser'", 'null': 'True', 'to': "orm['modernpolitics.Group']"}),
            'lovegov_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'lovegovuser'", 'null': 'True', 'to': "orm['modernpolitics.UserProfile']"}),
            'new_filter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'newfilter'", 'null': 'True', 'to': "orm['modernpolitics.FilterSetting']"}),
            'worldview': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.WorldView']", 'null': 'True'})
        },
        'modernpolitics.lovegovsetting': {
            'Meta': {'object_name': 'LoveGovSetting'},
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'setting': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'modernpolitics.message': {
            'Meta': {'object_name': 'Message', '_ormbases': ['modernpolitics.Content']},
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'debater': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'modernpolitics.motion': {
            'Meta': {'object_name': 'Motion', '_ormbases': ['modernpolitics.Content']},
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'full_text': ('django.db.models.fields.TextField', [], {}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Group']"}),
            'motion_type': ('django.db.models.fields.CharField', [], {'default': "'O'", 'max_length': '1'})
        },
        'modernpolitics.motionvoted': {
            'Meta': {'object_name': 'MotionVoted', '_ormbases': ['modernpolitics.UCRelationship']},
            'ucrelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UCRelationship']", 'unique': 'True', 'primary_key': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        'modernpolitics.myaction': {
            'Meta': {'object_name': 'MyAction'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Action']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rank': ('django.db.models.fields.IntegerField', [], {})
        },
        'modernpolitics.mycontent': {
            'Meta': {'object_name': 'MyContent'},
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Content']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rank': ('django.db.models.fields.IntegerField', [], {})
        },
        'modernpolitics.mypeople': {
            'Meta': {'object_name': 'MyPeople'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"}),
            'rank': ('django.db.models.fields.IntegerField', [], {})
        },
        'modernpolitics.network': {
            'Meta': {'object_name': 'Network', '_ormbases': ['modernpolitics.Group']},
            'extension': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Group']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'modernpolitics.news': {
            'Meta': {'object_name': 'News', '_ormbases': ['modernpolitics.Content']},
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'link_screenshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'link_summary': ('django.db.models.fields.TextField', [], {'default': "''"})
        },
        'modernpolitics.nextquestion': {
            'Meta': {'object_name': 'NextQuestion'},
            'answer_value': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'from_question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fquestion'", 'to': "orm['modernpolitics.Question']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'relevancy': ('django.db.models.fields.IntegerField', [], {}),
            'to_question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tquestion'", 'to': "orm['modernpolitics.Question']"})
        },
        'modernpolitics.notification': {
            'Meta': {'object_name': 'Notification'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Action']", 'null': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ignored': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modifier': ('django.db.models.fields.CharField', [], {'default': "'D'", 'max_length': '1'}),
            'notify_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notifywho'", 'to': "orm['modernpolitics.UserProfile']"}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'PUB'", 'max_length': '3'}),
            'requires_action': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tally': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'trig_content': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'trigcontent'", 'null': 'True', 'to': "orm['modernpolitics.Content']"}),
            'trig_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'griguser'", 'null': 'True', 'to': "orm['modernpolitics.UserProfile']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'notifyagg'", 'symmetrical': 'False', 'to': "orm['modernpolitics.UserProfile']"}),
            'verbose': ('django.db.models.fields.TextField', [], {}),
            'viewed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'modernpolitics.pageaccess': {
            'Meta': {'object_name': 'PageAccess'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'duration': ('django.db.models.fields.TimeField', [], {'null': 'True'}),
            'exit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipaddress': ('django.db.models.fields.IPAddressField', [], {'default': "'255.255.255.255'", 'max_length': '15', 'null': 'True'}),
            'left': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'login': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'page': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'modernpolitics.persistent': {
            'Meta': {'object_name': 'Persistent', '_ormbases': ['modernpolitics.Content']},
            'affirmative': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'negative'", 'null': 'True', 'to': "orm['modernpolitics.UserProfile']"}),
            'allotted_debate_delta': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'allotted_expiration_delta': ('django.db.models.fields.IntegerField', [], {'default': '10080'}),
            'allotted_response_delta': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'debate_expiration_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'debate_finish_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'debate_finished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'debate_start_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'debate_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'moderator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'themoderator'", 'null': 'True', 'to': "orm['modernpolitics.UserProfile']"}),
            'negative': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'affirmative'", 'null': 'True', 'to': "orm['modernpolitics.UserProfile']"}),
            'possible_users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'possible'", 'symmetrical': 'False', 'to': "orm['modernpolitics.UserProfile']"}),
            'resolution': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'statements': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.Message']", 'symmetrical': 'False'}),
            'turn_current': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'turn_lasttime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'turns_elapsed': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'turns_total': ('django.db.models.fields.IntegerField', [], {'default': '6'}),
            'votes_affirmative': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'votes_negative': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'voting_finished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'winner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'thewinner'", 'null': 'True', 'to': "orm['modernpolitics.UserProfile']"})
        },
        'modernpolitics.petition': {
            'Meta': {'object_name': 'Petition', '_ormbases': ['modernpolitics.Content']},
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'finalized': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'full_text': ('django.db.models.fields.TextField', [], {'max_length': '10000'}),
            'signers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'petitions'", 'symmetrical': 'False', 'to': "orm['modernpolitics.UserProfile']"})
        },
        'modernpolitics.photoalbum': {
            'Meta': {'object_name': 'PhotoAlbum', '_ormbases': ['modernpolitics.Content']},
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'photos': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.UserImage']", 'symmetrical': 'False'})
        },
        'modernpolitics.politician': {
            'Meta': {'object_name': 'Politician', '_ormbases': ['modernpolitics.UserProfile']},
            'office_seeking': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'party': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'userprofile_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UserProfile']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.profilepage': {
            'Meta': {'object_name': 'ProfilePage'},
            'bio': ('django.db.models.fields.TextField', [], {'max_length': '5000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'my_activity': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.MyAction']", 'symmetrical': 'False'}),
            'my_content': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.MyContent']", 'symmetrical': 'False'}),
            'my_people': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.MyPeople']", 'symmetrical': 'False'}),
            'my_views': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.TopicView']", 'symmetrical': 'False'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"})
        },
        'modernpolitics.qordered': {
            'Meta': {'object_name': 'qOrdered'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Question']"}),
            'rank': ('django.db.models.fields.IntegerField', [], {})
        },
        'modernpolitics.question': {
            'Meta': {'object_name': 'Question', '_ormbases': ['modernpolitics.Content']},
            'answers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.Answer']", 'symmetrical': 'False'}),
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'lg_weight': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'official': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'question_text': ('django.db.models.fields.TextField', [], {'max_length': '500'}),
            'question_type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'relevant_info': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'})
        },
        'modernpolitics.questiondiscussed': {
            'Meta': {'object_name': 'QuestionDiscussed'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_comments': ('django.db.models.fields.IntegerField', [], {}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Question']"})
        },
        'modernpolitics.questionordering': {
            'Meta': {'object_name': 'QuestionOrdering'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'questions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.qOrdered']", 'symmetrical': 'False'})
        },
        'modernpolitics.registercode': {
            'Meta': {'object_name': 'RegisterCode'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code_text': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'expiration_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'modernpolitics.relationship': {
            'Meta': {'object_name': 'Relationship'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'PUB'", 'max_length': '3'}),
            'relationship_type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'frel'", 'to': "orm['modernpolitics.UserProfile']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'modernpolitics.representative': {
            'Meta': {'object_name': 'Representative', '_ormbases': ['modernpolitics.ElectedOfficial']},
            'district': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'electedofficial_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.ElectedOfficial']", 'unique': 'True', 'primary_key': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'})
        },
        'modernpolitics.resetpassword': {
            'Meta': {'object_name': 'ResetPassword'},
            'email_code': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'userProfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"})
        },
        'modernpolitics.response': {
            'Meta': {'object_name': 'Response', '_ormbases': ['modernpolitics.Content']},
            'answer_val': ('django.db.models.fields.IntegerField', [], {}),
            'answers': ('lovegov.beta.modernpolitics.custom_fields.ListField', [], {'default': '[]'}),
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Question']"}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '5'})
        },
        'modernpolitics.rolloption': {
            'Meta': {'object_name': 'RollOption'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'modernpolitics.script': {
            'Meta': {'object_name': 'Script'},
            'command': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'modernpolitics.selectman': {
            'Meta': {'object_name': 'SelectMan', '_ormbases': ['modernpolitics.ElectedOfficial']},
            'electedofficial_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.ElectedOfficial']", 'unique': 'True', 'primary_key': 'True'}),
            'represents': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'modernpolitics.senator': {
            'Meta': {'object_name': 'Senator', '_ormbases': ['modernpolitics.ElectedOfficial']},
            'classNum': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'electedofficial_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.ElectedOfficial']", 'unique': 'True', 'primary_key': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'})
        },
        'modernpolitics.sentemail': {
            'Meta': {'object_name': 'SentEmail'},
            'from_email': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'to_email': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'modernpolitics.shared': {
            'Meta': {'object_name': 'Shared', '_ormbases': ['modernpolitics.UCRelationship']},
            'share_groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.Group']", 'symmetrical': 'False'}),
            'share_users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.UserProfile']", 'symmetrical': 'False'}),
            'ucrelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UCRelationship']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.signed': {
            'Meta': {'object_name': 'Signed', '_ormbases': ['modernpolitics.UCRelationship']},
            'ucrelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UCRelationship']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.topic': {
            'Meta': {'object_name': 'Topic'},
            'alias': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '30'}),
            'forum': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Forum']", 'null': 'True'}),
            'hover': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'parent_topic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Topic']", 'null': 'True'}),
            'selected': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'topic_text': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'modernpolitics.topiccomparison': {
            'Meta': {'object_name': 'TopicComparison'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_q': ('django.db.models.fields.IntegerField', [], {}),
            'result': ('django.db.models.fields.IntegerField', [], {}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Topic']"})
        },
        'modernpolitics.topicview': {
            'Meta': {'object_name': 'TopicView'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'PUB'", 'max_length': '3'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Topic']"}),
            'view': ('django.db.models.fields.TextField', [], {'max_length': '10000', 'blank': 'True'})
        },
        'modernpolitics.topicweight': {
            'Meta': {'object_name': 'TopicWeight'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Topic']"}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '100'})
        },
        'modernpolitics.typeweight': {
            'Meta': {'object_name': 'TypeWeight'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '100'})
        },
        'modernpolitics.ucrelationship': {
            'Meta': {'object_name': 'UCRelationship', '_ormbases': ['modernpolitics.Relationship']},
            'content': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'trel'", 'to': "orm['modernpolitics.Content']"}),
            'relationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Relationship']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.us_condistr': {
            'Meta': {'object_name': 'US_ConDistr'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'state': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.US_State']", 'unique': 'True'})
        },
        'modernpolitics.us_counties': {
            'Meta': {'object_name': 'US_Counties'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'state': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.US_State']", 'unique': 'True'})
        },
        'modernpolitics.us_state': {
            'Meta': {'object_name': 'US_State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'modernpolitics.usercomparison': {
            'Meta': {'object_name': 'UserComparison', '_ormbases': ['modernpolitics.ViewComparison']},
            'userA': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'a'", 'to': "orm['modernpolitics.UserProfile']"}),
            'userB': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'b'", 'to': "orm['modernpolitics.UserProfile']"}),
            'viewcomparison_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.ViewComparison']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.userfollow': {
            'Meta': {'object_name': 'UserFollow', '_ormbases': ['modernpolitics.UURelationship']},
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'declined': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fb': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'invited': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'inviter': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'rejected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'requested': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'uurelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UURelationship']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.usergroup': {
            'Meta': {'object_name': 'UserGroup', '_ormbases': ['modernpolitics.Group']},
            'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Group']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.userimage': {
            'Meta': {'object_name': 'UserImage', '_ormbases': ['modernpolitics.Content']},
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'})
        },
        'modernpolitics.useripaddress': {
            'Meta': {'object_name': 'UserIPAddress'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipaddress': ('django.db.models.fields.IPAddressField', [], {'default': "'255.255.255.255'", 'max_length': '15'}),
            'locID': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"})
        },
        'modernpolitics.userpermission': {
            'Meta': {'object_name': 'UserPermission'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission_type': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'modernpolitics.userphysicaladdress': {
            'Meta': {'object_name': 'UserPhysicalAddress'},
            'address_string': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'district': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '30', 'decimal_places': '15'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '30', 'decimal_places': '15'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'user': ('django.db.models.fields.IntegerField', [], {}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'})
        },
        'modernpolitics.userpost': {
            'Meta': {'object_name': 'UserPost', '_ormbases': ['modernpolitics.Content']},
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'full_text': ('django.db.models.fields.TextField', [], {'max_length': '10000'})
        },
        'modernpolitics.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'about_me': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'access_token': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'anonymous': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.AnonID']", 'symmetrical': 'False'}),
            'basicinfo': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.BasicInfo']", 'null': 'True', 'blank': 'True'}),
            'blog_url': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'confirmation_link': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content_notification_setting': ('lovegov.beta.modernpolitics.custom_fields.ListField', [], {}),
            'custom_notification_settings': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.CustomNotificationSetting']", 'symmetrical': 'False'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'debate_record': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.DebateResult']", 'symmetrical': 'False'}),
            'developer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'email_notification_setting': ('lovegov.beta.modernpolitics.custom_fields.ListField', [], {}),
            'evolve': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'facebook_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'facebook_profile_url': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'filter_setting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.FilterSetting']", 'null': 'True'}),
            'first_login': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'follow_me': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'follow_me'", 'null': 'True', 'to': "orm['modernpolitics.Group']"}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'i_follow': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'i_follow'", 'null': 'True', 'to': "orm['modernpolitics.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'last_answered': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'last_page_access': ('django.db.models.fields.IntegerField', [], {'default': '-1', 'null': 'True'}),
            'my_feed': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'newfeed'", 'symmetrical': 'False', 'to': "orm['modernpolitics.FeedItem']"}),
            'my_history': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'history'", 'symmetrical': 'False', 'to': "orm['modernpolitics.Content']"}),
            'my_involvement': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.Involved']", 'symmetrical': 'False'}),
            'network': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Network']", 'null': 'True'}),
            'private_follow': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'privileges': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'priv'", 'symmetrical': 'False', 'to': "orm['modernpolitics.Content']"}),
            'raw_data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'registration_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.RegisterCode']", 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'userAddress': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserPhysicalAddress']", 'null': 'True'}),
            'user_notification_setting': ('lovegov.beta.modernpolitics.custom_fields.ListField', [], {}),
            'user_type': ('django.db.models.fields.CharField', [], {'default': "'G'", 'max_length': '1'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'view': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.WorldView']"}),
            'website_url': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'modernpolitics.userresponse': {
            'Meta': {'object_name': 'UserResponse', '_ormbases': ['modernpolitics.Response']},
            'explanation': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'blank': 'True'}),
            'responder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"}),
            'response_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Response']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.uspresident': {
            'Meta': {'object_name': 'USPresident', '_ormbases': ['modernpolitics.ElectedOfficial']},
            'electedofficial_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.ElectedOfficial']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.uurelationship': {
            'Meta': {'object_name': 'UURelationship', '_ormbases': ['modernpolitics.Relationship']},
            'relationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Relationship']", 'unique': 'True', 'primary_key': 'True'}),
            'to_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tuser'", 'to': "orm['modernpolitics.UserProfile']"})
        },
        'modernpolitics.validemail': {
            'Meta': {'object_name': 'ValidEmail'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'modernpolitics.validemailextension': {
            'Meta': {'object_name': 'ValidEmailExtension'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'extension': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'modernpolitics.viewcomparison': {
            'Meta': {'object_name': 'ViewComparison'},
            'bytopic': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.TopicComparison']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_q': ('django.db.models.fields.IntegerField', [], {}),
            'result': ('django.db.models.fields.IntegerField', [], {}),
            'viewA': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'viewa'", 'to': "orm['modernpolitics.WorldView']"}),
            'viewB': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'viewb'", 'to': "orm['modernpolitics.WorldView']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'modernpolitics.voted': {
            'Meta': {'object_name': 'Voted', '_ormbases': ['modernpolitics.UCRelationship']},
            'ucrelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UCRelationship']", 'unique': 'True', 'primary_key': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'modernpolitics.votingrecord': {
            'Meta': {'object_name': 'VotingRecord'},
            'amendment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.LegislationAmendment']", 'null': 'True'}),
            'bill': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Legislation']", 'null': 'True'}),
            'electedofficial': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.ElectedOfficial']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'roll': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.CongressRoll']"}),
            'votekey': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'votevalue': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'modernpolitics.widgetaccess': {
            'Meta': {'object_name': 'WidgetAccess'},
            'host': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'which': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'modernpolitics.worldview': {
            'Meta': {'object_name': 'WorldView'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'responses': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.Response']", 'symmetrical': 'False'})
        }
    }

    complete_apps = ['modernpolitics']