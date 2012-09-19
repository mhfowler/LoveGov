# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'UserProfile.bio'
        db.alter_column('modernpolitics_userprofile', 'bio', self.gf('django.db.models.fields.CharField')(max_length=5000, null=True))

    def backwards(self, orm):

        # Changing field 'UserProfile.bio'
        db.alter_column('modernpolitics_userprofile', 'bio', self.gf('django.db.models.fields.CharField')(max_length=500, null=True))

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
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'PUB'", 'max_length': '3'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actions'", 'to': "orm['modernpolitics.UserProfile']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'modernpolitics.addtoscorecardaction': {
            'Meta': {'object_name': 'AddToScorecardAction', '_ormbases': ['modernpolitics.Action']},
            'action_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Action']", 'unique': 'True', 'primary_key': 'True'}),
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'invite_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True'}),
            'politician': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']", 'null': 'True'}),
            'scorecard': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'added_actions'", 'to': "orm['modernpolitics.Scorecard']"})
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
        'modernpolitics.answertally': {
            'Meta': {'object_name': 'AnswerTally'},
            'answer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Answer']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tally': ('django.db.models.fields.IntegerField', [], {})
        },
        'modernpolitics.askedaction': {
            'Meta': {'object_name': 'AskedAction', '_ormbases': ['modernpolitics.Action']},
            'action_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Action']", 'unique': 'True', 'primary_key': 'True'}),
            'politician': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"})
        },
        'modernpolitics.blogentry': {
            'Meta': {'object_name': 'BlogEntry'},
            'category': ('lovegov.modernpolitics.custom_fields.ListField', [], {}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '5000'})
        },
        'modernpolitics.bug': {
            'Meta': {'object_name': 'Bug'},
            'error': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'modernpolitics.calculatedgroup': {
            'Meta': {'object_name': 'CalculatedGroup', '_ormbases': ['modernpolitics.Group']},
            'calculation_type': ('django.db.models.fields.CharField', [], {'default': "'LM'", 'max_length': '2'}),
            'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Group']", 'unique': 'True', 'primary_key': 'True'}),
            'processed': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'processed_by'", 'symmetrical': 'False', 'to': "orm['modernpolitics.UserProfile']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"})
        },
        'modernpolitics.claimprofile': {
            'Meta': {'object_name': 'ClaimProfile'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'politician': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'claimers'", 'to': "orm['modernpolitics.UserProfile']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'claims'", 'to': "orm['modernpolitics.UserProfile']"})
        },
        'modernpolitics.clientanalytics': {
            'Meta': {'object_name': 'ClientAnalytics'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipaddress': ('django.db.models.fields.IPAddressField', [], {'default': "'255.255.255.255'", 'max_length': '15', 'null': 'True'}),
            'load_time': ('django.db.models.fields.IntegerField', [], {}),
            'page': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'modernpolitics.comment': {
            'Meta': {'object_name': 'Comment', '_ormbases': ['modernpolitics.Content']},
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'creator_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'on_content': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': "orm['modernpolitics.Content']"}),
            'root_content': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'root_content'", 'to': "orm['modernpolitics.Content']"}),
            'text': ('django.db.models.fields.TextField', [], {'max_length': '10000'})
        },
        'modernpolitics.committee': {
            'Meta': {'object_name': 'Committee', '_ormbases': ['modernpolitics.Group']},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'committee_type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Group']", 'unique': 'True', 'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Committee']", 'null': 'True'})
        },
        'modernpolitics.committeejoined': {
            'Meta': {'object_name': 'CommitteeJoined', '_ormbases': ['modernpolitics.GroupJoined']},
            'congress_sessions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.CongressSession']", 'symmetrical': 'False'}),
            'groupjoined_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.GroupJoined']", 'unique': 'True', 'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'})
        },
        'modernpolitics.compatabilitylog': {
            'Meta': {'object_name': 'CompatabilityLog'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incompatible': ('lovegov.modernpolitics.custom_fields.ListField', [], {'default': '[]'}),
            'ipaddress': ('django.db.models.fields.IPAddressField', [], {'default': "'255.255.255.255'", 'max_length': '15', 'null': 'True'}),
            'page': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']", 'null': 'True'}),
            'user_agent': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'modernpolitics.congressroll': {
            'Meta': {'object_name': 'CongressRoll'},
            'amendment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'amendment_votes'", 'null': 'True', 'to': "orm['modernpolitics.LegislationAmendment']"}),
            'aye': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'legislation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bill_votes'", 'null': 'True', 'to': "orm['modernpolitics.Legislation']"}),
            'nay': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'nv': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'present': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'}),
            'required': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True'}),
            'roll_number': ('django.db.models.fields.IntegerField', [], {}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.CongressSession']"}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'where': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'modernpolitics.congresssession': {
            'Meta': {'object_name': 'CongressSession'},
            'session': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        'modernpolitics.congressvote': {
            'Meta': {'object_name': 'CongressVote'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'roll': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votes'", 'to': "orm['modernpolitics.CongressRoll']"}),
            'votekey': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'voter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'congress_votes'", 'to': "orm['modernpolitics.UserProfile']"}),
            'votevalue': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        },
        'modernpolitics.content': {
            'Meta': {'object_name': 'Content'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'alias': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '1000'}),
            'calculated_view': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.WorldView']", 'null': 'True', 'blank': 'True'}),
            'commenters': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'commented_on_content'", 'symmetrical': 'False', 'to': "orm['modernpolitics.UserProfile']"}),
            'content_privacy': ('django.db.models.fields.CharField', [], {'default': "'O'", 'max_length': '1'}),
            'created_when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']", 'null': 'True'}),
            'downvotes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'edited_when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'hot_score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_calc': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'in_feed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'in_search': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_answered': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.PhysicalAddress']", 'null': 'True', 'blank': 'True'}),
            'main_image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserImage']", 'null': 'True', 'blank': 'True'}),
            'main_topic': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'maintopic'", 'null': 'True', 'to': "orm['modernpolitics.Topic']"}),
            'num_comments': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'posted_to': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'posted_content'", 'null': 'True', 'to': "orm['modernpolitics.Group']"}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'PUB'", 'max_length': '3'}),
            'rank': ('django.db.models.fields.DecimalField', [], {'default': "'0.0'", 'max_digits': '4', 'decimal_places': '2'}),
            'scale': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'shared_to': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'shared_content'", 'symmetrical': 'False', 'to': "orm['modernpolitics.Group']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'summary': ('django.db.models.fields.TextField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'topics': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.Topic']", 'symmetrical': 'False'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'unique_commenter_ids': ('lovegov.modernpolitics.custom_fields.ListField', [], {'default': '[]'}),
            'upvotes': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'modernpolitics.controllinguser': {
            'Meta': {'object_name': 'ControllingUser', '_ormbases': ['auth.User']},
            'permissions': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserPermission']", 'null': 'True'}),
            'prohibited_actions': ('lovegov.modernpolitics.custom_fields.ListField', [], {'default': '[]'}),
            'user_profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']", 'null': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.createdaction': {
            'Meta': {'object_name': 'CreatedAction', '_ormbases': ['modernpolitics.Action']},
            'action_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Action']", 'unique': 'True', 'primary_key': 'True'}),
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Content']"})
        },
        'modernpolitics.customnotificationsetting': {
            'Meta': {'object_name': 'CustomNotificationSetting'},
            'alerts': ('lovegov.modernpolitics.custom_fields.ListField', [], {}),
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Content']", 'null': 'True'}),
            'email': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']", 'null': 'True'})
        },
        'modernpolitics.deletedaction': {
            'Meta': {'object_name': 'DeletedAction', '_ormbases': ['modernpolitics.Action']},
            'action_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Action']", 'unique': 'True', 'primary_key': 'True'}),
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Content']"})
        },
        'modernpolitics.discussion': {
            'Meta': {'object_name': 'Discussion', '_ormbases': ['modernpolitics.Content']},
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'user_post': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'modernpolitics.districtpoliticiangroup': {
            'Meta': {'object_name': 'DistrictPoliticianGroup', '_ormbases': ['modernpolitics.PoliticianGroup']},
            'politiciangroup_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.PoliticianGroup']", 'unique': 'True', 'primary_key': 'True'}),
            'representatives': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'district_rep_group'", 'symmetrical': 'False', 'to': "orm['modernpolitics.UserProfile']"}),
            'senators': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'district_sen_group'", 'symmetrical': 'False', 'to': "orm['modernpolitics.UserProfile']"})
        },
        'modernpolitics.editedaction': {
            'Meta': {'object_name': 'EditedAction', '_ormbases': ['modernpolitics.Action']},
            'action_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Action']", 'unique': 'True', 'primary_key': 'True'}),
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Content']"})
        },
        'modernpolitics.election': {
            'Meta': {'object_name': 'Election', '_ormbases': ['modernpolitics.Group']},
            'election_date': ('django.db.models.fields.DateTimeField', [], {}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Group']", 'unique': 'True', 'primary_key': 'True'}),
            'office': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Office']", 'null': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'winner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'elections_won'", 'null': 'True', 'to': "orm['modernpolitics.UserProfile']"})
        },
        'modernpolitics.emaillist': {
            'Meta': {'object_name': 'EmailList'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
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
        'modernpolitics.group': {
            'Meta': {'object_name': 'Group', '_ormbases': ['modernpolitics.Content']},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'admin_of'", 'symmetrical': 'False', 'to': "orm['modernpolitics.UserProfile']"}),
            'agreement_threshold': ('django.db.models.fields.IntegerField', [], {'default': '50'}),
            'autogen': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content_by_posting': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'democratic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'full_text': ('django.db.models.fields.TextField', [], {'max_length': '1000'}),
            'government_type': ('django.db.models.fields.CharField', [], {'default': "'traditional'", 'max_length': '30'}),
            'group_content': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'in_groups'", 'symmetrical': 'False', 'to': "orm['modernpolitics.Content']"}),
            'group_privacy': ('django.db.models.fields.CharField', [], {'default': "'O'", 'max_length': '1'}),
            'group_type': ('django.db.models.fields.CharField', [], {'default': "'U'", 'max_length': '1'}),
            'group_view': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.WorldView']"}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_election': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'member_of'", 'symmetrical': 'False', 'to': "orm['modernpolitics.UserProfile']"}),
            'motion_expiration': ('django.db.models.fields.IntegerField', [], {'default': '7'}),
            'num_followers': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_group_content': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_members': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'participation_threshold': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'pinned_content': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'pinned_to'", 'symmetrical': 'False', 'to': "orm['modernpolitics.Content']"}),
            'scorecard': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'group_origins'", 'null': 'True', 'to': "orm['modernpolitics.Scorecard']"}),
            'subscribable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'system': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'modernpolitics.groupfollowaction': {
            'Meta': {'object_name': 'GroupFollowAction', '_ormbases': ['modernpolitics.Action']},
            'action_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Action']", 'unique': 'True', 'primary_key': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Group']"}),
            'modifier': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'modernpolitics.groupjoined': {
            'Meta': {'object_name': 'GroupJoined', '_ormbases': ['modernpolitics.UCRelationship']},
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'declined': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Group']"}),
            'invite_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True'}),
            'invited': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'inviter': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'rejected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'requested': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ucrelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UCRelationship']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.groupjoinedaction': {
            'Meta': {'object_name': 'GroupJoinedAction', '_ormbases': ['modernpolitics.Action']},
            'action_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Action']", 'unique': 'True', 'primary_key': 'True'}),
            'group_joined': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'joined_actions'", 'to': "orm['modernpolitics.GroupJoined']"}),
            'modifier': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'modernpolitics.groupview': {
            'Meta': {'object_name': 'GroupView'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'seen': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'modernpolitics.invitedtoregister': {
            'Meta': {'object_name': 'InvitedToRegister'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invite_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'inviter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"}),
            'notification': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Notification']"})
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
            'bill_introduced': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'bill_number': ('django.db.models.fields.IntegerField', [], {}),
            'bill_relation': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.Legislation']", 'null': 'True', 'symmetrical': 'False'}),
            'bill_subjects': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'subject_bills'", 'null': 'True', 'to': "orm['modernpolitics.LegislationSubject']"}),
            'bill_summary': ('django.db.models.fields.TextField', [], {'max_length': '400000', 'null': 'True'}),
            'bill_type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'bill_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'committees': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'legislation_committees'", 'null': 'True', 'to': "orm['modernpolitics.Committee']"}),
            'congress_body': ('django.db.models.fields.CharField', [], {'default': "'H'", 'max_length': '1'}),
            'congress_session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.CongressSession']"}),
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'full_title': ('django.db.models.fields.CharField', [], {'max_length': '5000', 'null': 'True'}),
            'sponsor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sponsored_legislation'", 'null': 'True', 'to': "orm['modernpolitics.UserProfile']"}),
            'state_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'state_text': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'})
        },
        'modernpolitics.legislationaction': {
            'Meta': {'object_name': 'LegislationAction'},
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'amendment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'amendment_actions'", 'null': 'True', 'to': "orm['modernpolitics.LegislationAmendment']"}),
            'committee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'legislation_activity'", 'null': 'True', 'to': "orm['modernpolitics.Committee']"}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'legislation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'legislation_actions'", 'null': 'True', 'to': "orm['modernpolitics.Legislation']"}),
            'references': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.LegislationReference']", 'symmetrical': 'False'}),
            'state': ('django.db.models.fields.TextField', [], {'max_length': '100', 'null': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'null': 'True'})
        },
        'modernpolitics.legislationamendment': {
            'Meta': {'object_name': 'LegislationAmendment', '_ormbases': ['modernpolitics.Content']},
            'amendment_number': ('django.db.models.fields.IntegerField', [], {}),
            'amendment_type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'amends_sequence': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'congress_session': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'session_amendments'", 'to': "orm['modernpolitics.CongressSession']"}),
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '50000', 'null': 'True'}),
            'legislation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'legislation_amendments'", 'to': "orm['modernpolitics.Legislation']"}),
            'offered_datetime': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'purpose': ('django.db.models.fields.TextField', [], {'max_length': '5000', 'null': 'True'}),
            'sponsor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']", 'null': 'True'}),
            'status_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'status_text': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'modernpolitics.legislationcalendar': {
            'Meta': {'object_name': 'LegislationCalendar', '_ormbases': ['modernpolitics.LegislationAction']},
            'calendar': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'calendar_number': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'legislationaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.LegislationAction']", 'unique': 'True', 'primary_key': 'True'}),
            'under': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
        },
        'modernpolitics.legislationcosponsor': {
            'Meta': {'object_name': 'LegislationCosponsor'},
            'cosponsor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'legislation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'legislation_cosponsors'", 'to': "orm['modernpolitics.Legislation']"})
        },
        'modernpolitics.legislationenacted': {
            'Meta': {'object_name': 'LegislationEnacted', '_ormbases': ['modernpolitics.LegislationAction']},
            'legislationaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.LegislationAction']", 'unique': 'True', 'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
        },
        'modernpolitics.legislationreference': {
            'Meta': {'object_name': 'LegislationReference'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'ref': ('django.db.models.fields.CharField', [], {'max_length': '400'})
        },
        'modernpolitics.legislationsigned': {
            'Meta': {'object_name': 'LegislationSigned', '_ormbases': ['modernpolitics.LegislationAction']},
            'legislationaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.LegislationAction']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.legislationsubject': {
            'Meta': {'object_name': 'LegislationSubject'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'modernpolitics.legislationtopresident': {
            'Meta': {'object_name': 'LegislationToPresident', '_ormbases': ['modernpolitics.LegislationAction']},
            'legislationaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.LegislationAction']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.legislationvote': {
            'Meta': {'object_name': 'LegislationVote', '_ormbases': ['modernpolitics.LegislationAction']},
            'how': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'legislationaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.LegislationAction']", 'unique': 'True', 'primary_key': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'roll': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'suspension': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'vote_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'where': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True'})
        },
        'modernpolitics.lgnumber': {
            'Meta': {'object_name': 'LGNumber'},
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {})
        },
        'modernpolitics.messagedaction': {
            'Meta': {'object_name': 'MessagedAction', '_ormbases': ['modernpolitics.Action']},
            'action_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Action']", 'unique': 'True', 'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'politician': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"})
        },
        'modernpolitics.motion': {
            'Meta': {'object_name': 'Motion', '_ormbases': ['modernpolitics.Content']},
            'above_threshold': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'expiration_date': ('django.db.models.fields.DateTimeField', [], {}),
            'expired': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'full_text': ('django.db.models.fields.TextField', [], {}),
            'government_type': ('django.db.models.fields.CharField', [], {'default': "'traditional'", 'max_length': '30'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Group']"}),
            'moderator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']", 'null': 'True'}),
            'motion_downvotes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'motion_type': ('django.db.models.fields.CharField', [], {'default': "'other'", 'max_length': '30'}),
            'motion_upvotes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'passed': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'modernpolitics.network': {
            'Meta': {'object_name': 'Network', '_ormbases': ['modernpolitics.Group']},
            'extension': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Group']", 'unique': 'True', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'network_type': ('django.db.models.fields.CharField', [], {'default': "'D'", 'max_length': '1'})
        },
        'modernpolitics.news': {
            'Meta': {'object_name': 'News', '_ormbases': ['modernpolitics.Content']},
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'link_clicks': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'link_screenshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'link_summary': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'link_title': ('django.db.models.fields.TextField', [], {'default': "'No title'"})
        },
        'modernpolitics.notification': {
            'Meta': {'object_name': 'Notification'},
            'action': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notifications'", 'to': "orm['modernpolitics.Action']"}),
            'agg_actions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'agg_notifications'", 'symmetrical': 'False', 'to': "orm['modernpolitics.Action']"}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notify_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True'}),
            'notify_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notifications'", 'null': 'True', 'to': "orm['modernpolitics.UserProfile']"}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'PUB'", 'max_length': '3'}),
            'viewed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'modernpolitics.office': {
            'Meta': {'object_name': 'Office', '_ormbases': ['modernpolitics.Content']},
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'governmental': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'representative': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'senator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'tag_offices'", 'symmetrical': 'False', 'to': "orm['modernpolitics.OfficeTag']"}),
            'user_generated': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'modernpolitics.officeheld': {
            'Meta': {'object_name': 'OfficeHeld', '_ormbases': ['modernpolitics.UCRelationship']},
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'congress_sessions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.CongressSession']", 'symmetrical': 'False'}),
            'current': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'election': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'office': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'office_terms'", 'to': "orm['modernpolitics.Office']"}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'ucrelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UCRelationship']", 'unique': 'True', 'primary_key': 'True'}),
            'user_generated': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'modernpolitics.officetag': {
            'Meta': {'object_name': 'OfficeTag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
            'page': ('django.db.models.fields.CharField', [], {'max_length': '5000'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'modernpolitics.party': {
            'Meta': {'object_name': 'Party', '_ormbases': ['modernpolitics.Group']},
            'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Group']", 'unique': 'True', 'primary_key': 'True'}),
            'party_label': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'party_type': ('django.db.models.fields.CharField', [], {'default': "'D'", 'max_length': '1'})
        },
        'modernpolitics.petition': {
            'Meta': {'object_name': 'Petition', '_ormbases': ['modernpolitics.Content']},
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'current': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'finalized': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'full_text': ('django.db.models.fields.TextField', [], {'max_length': '10000'}),
            'goal': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'p_level': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'signers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'petitions'", 'symmetrical': 'False', 'to': "orm['modernpolitics.UserProfile']"})
        },
        'modernpolitics.physicaladdress': {
            'Meta': {'object_name': 'PhysicalAddress'},
            'address_string': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'district': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '30', 'decimal_places': '15'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '30', 'decimal_places': '15'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'})
        },
        'modernpolitics.pinnedaction': {
            'Meta': {'object_name': 'PinnedAction', '_ormbases': ['modernpolitics.Action']},
            'action_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Action']", 'unique': 'True', 'primary_key': 'True'}),
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Content']"}),
            'to_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pinned_to_actions'", 'null': 'True', 'to': "orm['modernpolitics.Group']"})
        },
        'modernpolitics.politiciangroup': {
            'Meta': {'object_name': 'PoliticianGroup', '_ormbases': ['modernpolitics.Group']},
            'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Group']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.poll': {
            'Meta': {'object_name': 'Poll', '_ormbases': ['modernpolitics.Content']},
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'num_questions': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'questions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.Question']", 'symmetrical': 'False'})
        },
        'modernpolitics.question': {
            'Meta': {'object_name': 'Question', '_ormbases': ['modernpolitics.Content']},
            'answers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.Answer']", 'symmetrical': 'False'}),
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'lg_weight': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'num_responses': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'official': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'question_text': ('django.db.models.fields.TextField', [], {'max_length': '500'}),
            'question_type': ('django.db.models.fields.CharField', [], {'default': "'D'", 'max_length': '2'}),
            'questions_hot_score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'relevant_info': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.TextField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'})
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
            'created_when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invite_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True'}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'PUB'", 'max_length': '3'}),
            'relationship_type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'relationships'", 'null': 'True', 'to': "orm['modernpolitics.UserProfile']"})
        },
        'modernpolitics.resetpassword': {
            'Meta': {'object_name': 'ResetPassword'},
            'created_when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email_code': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'userProfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"})
        },
        'modernpolitics.response': {
            'Meta': {'object_name': 'Response', '_ormbases': ['modernpolitics.Content']},
            'answer_tallies': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.AnswerTally']", 'symmetrical': 'False'}),
            'answer_val': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'explanation': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'blank': 'True'}),
            'explanation_comment': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Comment']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'most_chosen_answer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'responses'", 'null': 'True', 'to': "orm['modernpolitics.Answer']"}),
            'most_chosen_num': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Question']"}),
            'total_num': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '50'})
        },
        'modernpolitics.runningforaction': {
            'Meta': {'object_name': 'RunningForAction', '_ormbases': ['modernpolitics.Action']},
            'action_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Action']", 'unique': 'True', 'primary_key': 'True'}),
            'election': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Election']"}),
            'modifier': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'modernpolitics.scorecard': {
            'Meta': {'object_name': 'Scorecard', '_ormbases': ['modernpolitics.Content']},
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'full_text': ('django.db.models.fields.TextField', [], {}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'scorecards'", 'null': 'True', 'to': "orm['modernpolitics.Group']"}),
            'politicians': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.UserProfile']", 'symmetrical': 'False'}),
            'poll': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Poll']"}),
            'scorecard_view': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.WorldView']"})
        },
        'modernpolitics.script': {
            'Meta': {'object_name': 'Script'},
            'command': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
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
        'modernpolitics.sharedaction': {
            'Meta': {'object_name': 'SharedAction', '_ormbases': ['modernpolitics.Action']},
            'action_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Action']", 'unique': 'True', 'primary_key': 'True'}),
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Content']"}),
            'to_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shared_to_actions'", 'null': 'True', 'to': "orm['modernpolitics.Group']"}),
            'to_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']", 'null': 'True'})
        },
        'modernpolitics.signed': {
            'Meta': {'object_name': 'Signed', '_ormbases': ['modernpolitics.UCRelationship']},
            'ucrelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UCRelationship']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.signedaction': {
            'Meta': {'object_name': 'SignedAction', '_ormbases': ['modernpolitics.Action']},
            'action_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Action']", 'unique': 'True', 'primary_key': 'True'}),
            'petition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Petition']"})
        },
        'modernpolitics.stategroup': {
            'Meta': {'object_name': 'StateGroup', '_ormbases': ['modernpolitics.Group']},
            'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Group']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.statepoliticiangroup': {
            'Meta': {'object_name': 'StatePoliticianGroup', '_ormbases': ['modernpolitics.PoliticianGroup']},
            'politiciangroup_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.PoliticianGroup']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.supported': {
            'Meta': {'object_name': 'Supported', '_ormbases': ['modernpolitics.UURelationship']},
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'uurelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UURelationship']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.supportedaction': {
            'Meta': {'object_name': 'SupportedAction', '_ormbases': ['modernpolitics.Action']},
            'action_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Action']", 'unique': 'True', 'primary_key': 'True'}),
            'modifier': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'support': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'support_actions'", 'to': "orm['modernpolitics.Supported']"})
        },
        'modernpolitics.topic': {
            'Meta': {'object_name': 'Topic'},
            'alias': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '30'}),
            'hover': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'parent_topic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Topic']", 'null': 'True'}),
            'selected': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'topic_text': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'modernpolitics.topiccomparison': {
            'Meta': {'object_name': 'TopicComparison'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_q': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'result': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Topic']"})
        },
        'modernpolitics.topicview': {
            'Meta': {'object_name': 'TopicView'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'PUB'", 'max_length': '3'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Topic']"}),
            'view': ('django.db.models.fields.TextField', [], {'max_length': '10000', 'blank': 'True'})
        },
        'modernpolitics.towngroup': {
            'Meta': {'object_name': 'TownGroup', '_ormbases': ['modernpolitics.Group']},
            'group_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Group']", 'unique': 'True', 'primary_key': 'True'})
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
            'invite_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True'}),
            'invited': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'inviter': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'rejected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'requested': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'uurelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UURelationship']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.userfollowaction': {
            'Meta': {'object_name': 'UserFollowAction', '_ormbases': ['modernpolitics.Action']},
            'action_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Action']", 'unique': 'True', 'primary_key': 'True'}),
            'modifier': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'user_follow': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'follow_actions'", 'to': "orm['modernpolitics.UserFollow']"})
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
        'modernpolitics.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'about_me': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'access_token': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'address': ('lovegov.modernpolitics.custom_fields.ListField', [], {'default': '[]'}),
            'age': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'anonymous': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.AnonID']", 'symmetrical': 'False'}),
            'background_tasks': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'blank': 'True'}),
            'bio': ('django.db.models.fields.CharField', [], {'max_length': '5000', 'null': 'True', 'blank': 'True'}),
            'blog_url': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'confirmation_link': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content_notification_setting': ('lovegov.modernpolitics.custom_fields.ListField', [], {}),
            'created_when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currently_in_office': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'custom_notification_settings': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.CustomNotificationSetting']", 'symmetrical': 'False'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'developer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'dob': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'downvotes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'elected_official': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'email_notification_setting': ('lovegov.modernpolitics.custom_fields.ListField', [], {}),
            'ethnicity': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'facebook_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'facebook_profile_url': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'fb_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'finished_tasks': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'blank': 'True'}),
            'first_login': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'first_login_tasks': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'follow_me': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'follow_me'", 'null': 'True', 'to': "orm['modernpolitics.Group']"}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'ghost': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'govtrack_id': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'group_subscriptions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.Group']", 'symmetrical': 'False'}),
            'group_views': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.GroupView']", 'symmetrical': 'False'}),
            'i_follow': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'i_follow'", 'null': 'True', 'to': "orm['modernpolitics.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invite_message': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '10000', 'blank': 'True'}),
            'invite_subject': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '1000', 'blank': 'True'}),
            'last_answered': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'last_page_access': ('django.db.models.fields.IntegerField', [], {'default': '-1', 'null': 'True'}),
            'like_minded': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_origin'", 'null': 'True', 'to': "orm['modernpolitics.CalculatedGroup']"}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.PhysicalAddress']", 'null': 'True'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'networks': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'networks'", 'symmetrical': 'False', 'to': "orm['modernpolitics.Network']"}),
            'nick_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'num_answers': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_articles': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_asked': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_followme': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_groups': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_ifollow': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_logins': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_messages': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_petitions': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_posts': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_signatures': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_supporters': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'old_locations': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'old_users'", 'symmetrical': 'False', 'to': "orm['modernpolitics.PhysicalAddress']"}),
            'parties': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'parties'", 'symmetrical': 'False', 'to': "orm['modernpolitics.Party']"}),
            'party': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'political_role': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'political_statement': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'political_title': ('django.db.models.fields.CharField', [], {'default': "'Citizen'", 'max_length': '100'}),
            'politician': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'primary_role': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.OfficeHeld']", 'null': 'True'}),
            'private_follow': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'profile_image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserImage']", 'null': 'True'}),
            'raw_data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'registration_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.RegisterCode']", 'null': 'True'}),
            'religion': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'running_for': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'runners'", 'null': 'True', 'to': "orm['modernpolitics.Election']"}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'supporters': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'supportees'", 'symmetrical': 'False', 'to': "orm['modernpolitics.UserProfile']"}),
            'temp_location': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'temp_users'", 'null': 'True', 'to': "orm['modernpolitics.PhysicalAddress']"}),
            'twitter_screen_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'twitter_user_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'U'", 'max_length': '1'}),
            'upvotes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'url': ('lovegov.modernpolitics.custom_fields.ListField', [], {'default': '[]'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'userAddress': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserPhysicalAddress']", 'null': 'True'}),
            'user_notification_setting': ('lovegov.modernpolitics.custom_fields.ListField', [], {}),
            'user_title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'view': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.WorldView']"}),
            'website_url': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'})
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
            'num_q': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'optimized': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True'}),
            'result': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'viewA': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'viewa'", 'to': "orm['modernpolitics.WorldView']"}),
            'viewB': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'viewb'", 'to': "orm['modernpolitics.WorldView']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'modernpolitics.voted': {
            'Meta': {'object_name': 'Voted', '_ormbases': ['modernpolitics.UCRelationship']},
            'ucrelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UCRelationship']", 'unique': 'True', 'primary_key': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'modernpolitics.votedaction': {
            'Meta': {'object_name': 'VotedAction', '_ormbases': ['modernpolitics.Action']},
            'action_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Action']", 'unique': 'True', 'primary_key': 'True'}),
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Content']"}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0'})
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