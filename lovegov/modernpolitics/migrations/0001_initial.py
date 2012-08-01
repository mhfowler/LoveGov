# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserPhysicalAddress'
        db.create_table('modernpolitics_userphysicaladdress', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.IntegerField')()),
            ('address_string', self.gf('django.db.models.fields.CharField')(max_length=500, null=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=20, null=True)),
            ('longitude', self.gf('django.db.models.fields.DecimalField')(max_digits=30, decimal_places=15)),
            ('latitude', self.gf('django.db.models.fields.DecimalField')(max_digits=30, decimal_places=15)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('district', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('modernpolitics', ['UserPhysicalAddress'])

        # Adding model 'Topic'
        db.create_table('modernpolitics_topic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('alias', self.gf('django.db.models.fields.CharField')(default='default', max_length=30)),
            ('topic_text', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('parent_topic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Topic'], null=True)),
            ('forum', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Forum'], null=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True)),
            ('hover', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True)),
            ('selected', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True)),
        ))
        db.send_create_signal('modernpolitics', ['Topic'])

        # Adding model 'Content'
        db.create_table('modernpolitics_content', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('privacy', self.gf('django.db.models.fields.CharField')(default='PUB', max_length=3)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.UserProfile'])),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.UserPhysicalAddress'], null=True)),
            ('level', self.gf('django.db.models.fields.CharField')(default='F', max_length=1)),
            ('alias', self.gf('django.db.models.fields.CharField')(default='default', max_length=30)),
            ('in_feed', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('in_search', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('in_calc', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('main_topic', self.gf('django.db.models.fields.related.ForeignKey')(related_name='maintopic', null=True, to=orm['modernpolitics.Topic'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('summary', self.gf('django.db.models.fields.TextField')(max_length=500, null=True, blank=True)),
            ('created_when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('main_image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.UserImage'], null=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('calculated_view', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.WorldView'], null=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=20)),
            ('rank', self.gf('django.db.models.fields.DecimalField')(default='0.0', max_digits=4, decimal_places=2)),
            ('upvotes', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('downvotes', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('num_comments', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('modernpolitics', ['Content'])

        # Adding M2M table for field topics on 'Content'
        db.create_table('modernpolitics_content_topics', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('content', models.ForeignKey(orm['modernpolitics.content'], null=False)),
            ('topic', models.ForeignKey(orm['modernpolitics.topic'], null=False))
        ))
        db.create_unique('modernpolitics_content_topics', ['content_id', 'topic_id'])

        # Adding model 'UserImage'
        db.create_table('modernpolitics_userimage', (
            ('content_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Content'], unique=True, primary_key=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal('modernpolitics', ['UserImage'])

        # Adding model 'BasicInfo'
        db.create_table('modernpolitics_basicinfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile_image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.UserImage'], null=True)),
            ('middle_name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('nick_name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('dob', self.gf('django.db.models.fields.DateField')(null=True)),
            ('address', self.gf('lovegov.beta.modernpolitics.custom_fields.ListField')()),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2, blank=True)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=15, blank=True)),
            ('url', self.gf('lovegov.beta.modernpolitics.custom_fields.ListField')()),
            ('religion', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('ethnicity', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('party', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('political_role', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('invite_message', self.gf('django.db.models.fields.CharField')(default="LoveGov Alpha is now up and running! We would really appreciate it if you logged in and test run the features of our site. Please keep in mind that Alpha only contains a portion of the functionality intended for the Brown/RISD beta, so you will see us regularly adding new features over the next month. If you encounter any problems while using our siteor just want to send us comments then please don't hesitate to contact us - we want to hear your opinions!", max_length=10000, blank=True)),
            ('invite_subject', self.gf('django.db.models.fields.CharField')(default='Welcome to LoveGov Alpha', max_length=1000, blank=True)),
        ))
        db.send_create_signal('modernpolitics', ['BasicInfo'])

        # Adding model 'Involved'
        db.create_table('modernpolitics_involved', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Content'])),
            ('involvement', self.gf('django.db.models.fields.IntegerField')()),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('modernpolitics', ['Involved'])

        # Adding model 'FeedItem'
        db.create_table('modernpolitics_feeditem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Content'])),
            ('rank', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('modernpolitics', ['FeedItem'])

        # Adding model 'DebateResult'
        db.create_table('modernpolitics_debateresult', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('debate', self.gf('django.db.models.fields.IntegerField')()),
            ('result', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('modernpolitics', ['DebateResult'])

        # Adding model 'CustomNotificationSetting'
        db.create_table('modernpolitics_customnotificationsetting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Content'], null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.UserProfile'], null=True)),
            ('email', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('alerts', self.gf('lovegov.beta.modernpolitics.custom_fields.ListField')()),
        ))
        db.send_create_signal('modernpolitics', ['CustomNotificationSetting'])

        # Adding model 'TopicWeight'
        db.create_table('modernpolitics_topicweight', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('topic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Topic'])),
            ('weight', self.gf('django.db.models.fields.IntegerField')(default=100)),
        ))
        db.send_create_signal('modernpolitics', ['TopicWeight'])

        # Adding model 'TypeWeight'
        db.create_table('modernpolitics_typeweight', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('weight', self.gf('django.db.models.fields.IntegerField')(default=100)),
        ))
        db.send_create_signal('modernpolitics', ['TypeWeight'])

        # Adding model 'FilterSetting'
        db.create_table('modernpolitics_filtersetting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('alias', self.gf('django.db.models.fields.CharField')(default='default', max_length=30)),
            ('similarity', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('days', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('by_topic', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('by_type', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('algo', self.gf('django.db.models.fields.CharField')(default='D', max_length=1)),
            ('hot_window', self.gf('django.db.models.fields.IntegerField')(default=2)),
        ))
        db.send_create_signal('modernpolitics', ['FilterSetting'])

        # Adding M2M table for field topic_weights on 'FilterSetting'
        db.create_table('modernpolitics_filtersetting_topic_weights', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('filtersetting', models.ForeignKey(orm['modernpolitics.filtersetting'], null=False)),
            ('topicweight', models.ForeignKey(orm['modernpolitics.topicweight'], null=False))
        ))
        db.create_unique('modernpolitics_filtersetting_topic_weights', ['filtersetting_id', 'topicweight_id'])

        # Adding M2M table for field type_weights on 'FilterSetting'
        db.create_table('modernpolitics_filtersetting_type_weights', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('filtersetting', models.ForeignKey(orm['modernpolitics.filtersetting'], null=False)),
            ('typeweight', models.ForeignKey(orm['modernpolitics.typeweight'], null=False))
        ))
        db.create_unique('modernpolitics_filtersetting_type_weights', ['filtersetting_id', 'typeweight_id'])

        # Adding model 'RegisterCode'
        db.create_table('modernpolitics_registercode', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code_text', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('expiration_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('modernpolitics', ['RegisterCode'])

        # Adding model 'UserProfile'
        db.create_table('modernpolitics_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('about_me', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('facebook_id', self.gf('django.db.models.fields.BigIntegerField')(unique=True, null=True, blank=True)),
            ('access_token', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('facebook_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('facebook_profile_url', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('website_url', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('blog_url', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=255, null=True, blank=True)),
            ('date_of_birth', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('raw_data', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('user_type', self.gf('django.db.models.fields.CharField')(default='G', max_length=1)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=500, null=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('registration_code', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.RegisterCode'], null=True)),
            ('confirmed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('confirmation_link', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('first_login', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('developer', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('basicinfo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.BasicInfo'], null=True, blank=True)),
            ('view', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.WorldView'])),
            ('network', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Network'], null=True)),
            ('userAddress', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.UserPhysicalAddress'], null=True)),
            ('last_answered', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('i_follow', self.gf('django.db.models.fields.related.ForeignKey')(related_name='i_follow', null=True, to=orm['modernpolitics.Group'])),
            ('follow_me', self.gf('django.db.models.fields.related.ForeignKey')(related_name='follow_me', null=True, to=orm['modernpolitics.Group'])),
            ('private_follow', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('last_page_access', self.gf('django.db.models.fields.IntegerField')(default=-1, null=True)),
            ('filter_setting', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.FilterSetting'], null=True)),
            ('evolve', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('user_notification_setting', self.gf('lovegov.beta.modernpolitics.custom_fields.ListField')()),
            ('content_notification_setting', self.gf('lovegov.beta.modernpolitics.custom_fields.ListField')()),
            ('email_notification_setting', self.gf('lovegov.beta.modernpolitics.custom_fields.ListField')()),
            ('my_connections', self.gf('django.db.models.fields.IntegerField')(default=-1)),
        ))
        db.send_create_signal('modernpolitics', ['UserProfile'])

        # Adding M2M table for field debate_record on 'UserProfile'
        db.create_table('modernpolitics_userprofile_debate_record', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['modernpolitics.userprofile'], null=False)),
            ('debateresult', models.ForeignKey(orm['modernpolitics.debateresult'], null=False))
        ))
        db.create_unique('modernpolitics_userprofile_debate_record', ['userprofile_id', 'debateresult_id'])

        # Adding M2M table for field my_involvement on 'UserProfile'
        db.create_table('modernpolitics_userprofile_my_involvement', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['modernpolitics.userprofile'], null=False)),
            ('involved', models.ForeignKey(orm['modernpolitics.involved'], null=False))
        ))
        db.create_unique('modernpolitics_userprofile_my_involvement', ['userprofile_id', 'involved_id'])

        # Adding M2M table for field my_history on 'UserProfile'
        db.create_table('modernpolitics_userprofile_my_history', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['modernpolitics.userprofile'], null=False)),
            ('content', models.ForeignKey(orm['modernpolitics.content'], null=False))
        ))
        db.create_unique('modernpolitics_userprofile_my_history', ['userprofile_id', 'content_id'])

        # Adding M2M table for field privileges on 'UserProfile'
        db.create_table('modernpolitics_userprofile_privileges', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['modernpolitics.userprofile'], null=False)),
            ('content', models.ForeignKey(orm['modernpolitics.content'], null=False))
        ))
        db.create_unique('modernpolitics_userprofile_privileges', ['userprofile_id', 'content_id'])

        # Adding M2M table for field my_feed on 'UserProfile'
        db.create_table('modernpolitics_userprofile_my_feed', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['modernpolitics.userprofile'], null=False)),
            ('feeditem', models.ForeignKey(orm['modernpolitics.feeditem'], null=False))
        ))
        db.create_unique('modernpolitics_userprofile_my_feed', ['userprofile_id', 'feeditem_id'])

        # Adding M2M table for field custom_notification_settings on 'UserProfile'
        db.create_table('modernpolitics_userprofile_custom_notification_settings', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm['modernpolitics.userprofile'], null=False)),
            ('customnotificationsetting', models.ForeignKey(orm['modernpolitics.customnotificationsetting'], null=False))
        ))
        db.create_unique('modernpolitics_userprofile_custom_notification_settings', ['userprofile_id', 'customnotificationsetting_id'])

        # Adding model 'UserPermission'
        db.create_table('modernpolitics_userpermission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('permission_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('modernpolitics', ['UserPermission'])

        # Adding model 'ControllingUser'
        db.create_table('modernpolitics_controllinguser', (
            ('user_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
            ('permissions', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.UserPermission'], null=True)),
            ('user_profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.UserProfile'], null=True)),
        ))
        db.send_create_signal('modernpolitics', ['ControllingUser'])

        # Adding model 'Action'
        db.create_table('modernpolitics_action', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('privacy', self.gf('django.db.models.fields.CharField')(default='PUB', max_length=3)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.UserProfile'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('modifier', self.gf('django.db.models.fields.CharField')(default='D', max_length=1)),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('relationship', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Relationship'], null=True)),
            ('must_notify', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('verbose', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('modernpolitics', ['Action'])

        # Adding model 'Notification'
        db.create_table('modernpolitics_notification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('privacy', self.gf('django.db.models.fields.CharField')(default='PUB', max_length=3)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.UserProfile'])),
            ('verbose', self.gf('django.db.models.fields.TextField')()),
            ('notify_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='notifywho', to=orm['modernpolitics.UserProfile'])),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('viewed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ignored', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('requires_action', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Action'], null=True)),
            ('tally', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('trig_content', self.gf('django.db.models.fields.related.ForeignKey')(related_name='trigcontent', null=True, to=orm['modernpolitics.Content'])),
            ('trig_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='griguser', null=True, to=orm['modernpolitics.UserProfile'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('modifier', self.gf('django.db.models.fields.CharField')(default='D', max_length=1)),
        ))
        db.send_create_signal('modernpolitics', ['Notification'])

        # Adding M2M table for field users on 'Notification'
        db.create_table('modernpolitics_notification_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('notification', models.ForeignKey(orm['modernpolitics.notification'], null=False)),
            ('userprofile', models.ForeignKey(orm['modernpolitics.userprofile'], null=False))
        ))
        db.create_unique('modernpolitics_notification_users', ['notification_id', 'userprofile_id'])

        # Adding model 'ElectedOfficial'
        db.create_table('modernpolitics_electedofficial', (
            ('userprofile_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.UserProfile'], unique=True, primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1, null=True)),
            ('official_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('govtrack_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('pvs_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('os_id', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('bioguide_id', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('metavid_id', self.gf('django.db.models.fields.CharField')(max_length=150, null=True)),
            ('youtube_id', self.gf('django.db.models.fields.CharField')(max_length=150, null=True)),
            ('twitter_id', self.gf('django.db.models.fields.CharField')(max_length=150, null=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True)),
        ))
        db.send_create_signal('modernpolitics', ['ElectedOfficial'])

        # Adding model 'Politician'
        db.create_table('modernpolitics_politician', (
            ('userprofile_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.UserProfile'], unique=True, primary_key=True)),
            ('party', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('office_seeking', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('modernpolitics', ['Politician'])

        # Adding model 'CongressSessions'
        db.create_table('modernpolitics_congresssessions', (
            ('session', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
        ))
        db.send_create_signal('modernpolitics', ['CongressSessions'])

        # Adding M2M table for field people on 'CongressSessions'
        db.create_table('modernpolitics_congresssessions_people', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('congresssessions', models.ForeignKey(orm['modernpolitics.congresssessions'], null=False)),
            ('electedofficial', models.ForeignKey(orm['modernpolitics.electedofficial'], null=False))
        ))
        db.create_unique('modernpolitics_congresssessions_people', ['congresssessions_id', 'electedofficial_id'])

        # Adding model 'SelectMan'
        db.create_table('modernpolitics_selectman', (
            ('electedofficial_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.ElectedOfficial'], unique=True, primary_key=True)),
            ('represents', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal('modernpolitics', ['SelectMan'])

        # Adding model 'Senator'
        db.create_table('modernpolitics_senator', (
            ('electedofficial_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.ElectedOfficial'], unique=True, primary_key=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2, null=True)),
            ('classNum', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal('modernpolitics', ['Senator'])

        # Adding model 'Representative'
        db.create_table('modernpolitics_representative', (
            ('electedofficial_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.ElectedOfficial'], unique=True, primary_key=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2, null=True)),
            ('district', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal('modernpolitics', ['Representative'])

        # Adding model 'USPresident'
        db.create_table('modernpolitics_uspresident', (
            ('electedofficial_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.ElectedOfficial'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('modernpolitics', ['USPresident'])

        # Adding model 'Committee'
        db.create_table('modernpolitics_committee', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Committee'], null=True)),
        ))
        db.send_create_signal('modernpolitics', ['Committee'])

        # Adding model 'CommitteeMember'
        db.create_table('modernpolitics_committeemember', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.CongressSessions'])),
            ('electedOfficial', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.ElectedOfficial'])),
            ('committee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Committee'])),
        ))
        db.send_create_signal('modernpolitics', ['CommitteeMember'])

        # Adding model 'Petition'
        db.create_table('modernpolitics_petition', (
            ('content_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Content'], unique=True, primary_key=True)),
            ('full_text', self.gf('django.db.models.fields.TextField')(max_length=10000)),
            ('finalized', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('modernpolitics', ['Petition'])

        # Adding M2M table for field signers on 'Petition'
        db.create_table('modernpolitics_petition_signers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('petition', models.ForeignKey(orm['modernpolitics.petition'], null=False)),
            ('userprofile', models.ForeignKey(orm['modernpolitics.userprofile'], null=False))
        ))
        db.create_unique('modernpolitics_petition_signers', ['petition_id', 'userprofile_id'])

        # Adding model 'Event'
        db.create_table('modernpolitics_event', (
            ('content_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Content'], unique=True, primary_key=True)),
            ('full_text', self.gf('django.db.models.fields.TextField')(max_length=10000)),
            ('datetime_of_event', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('modernpolitics', ['Event'])

        # Adding model 'News'
        db.create_table('modernpolitics_news', (
            ('content_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Content'], unique=True, primary_key=True)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('link_summary', self.gf('django.db.models.fields.TextField')(default='')),
            ('link_screenshot', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal('modernpolitics', ['News'])

        # Adding model 'UserPost'
        db.create_table('modernpolitics_userpost', (
            ('content_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Content'], unique=True, primary_key=True)),
            ('full_text', self.gf('django.db.models.fields.TextField')(max_length=10000)),
        ))
        db.send_create_signal('modernpolitics', ['UserPost'])

        # Adding model 'PhotoAlbum'
        db.create_table('modernpolitics_photoalbum', (
            ('content_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Content'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('modernpolitics', ['PhotoAlbum'])

        # Adding M2M table for field photos on 'PhotoAlbum'
        db.create_table('modernpolitics_photoalbum_photos', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('photoalbum', models.ForeignKey(orm['modernpolitics.photoalbum'], null=False)),
            ('userimage', models.ForeignKey(orm['modernpolitics.userimage'], null=False))
        ))
        db.create_unique('modernpolitics_photoalbum_photos', ['photoalbum_id', 'userimage_id'])

        # Adding model 'Comment'
        db.create_table('modernpolitics_comment', (
            ('content_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Content'], unique=True, primary_key=True)),
            ('root_content', self.gf('django.db.models.fields.related.ForeignKey')(related_name='root_content', to=orm['modernpolitics.Content'])),
            ('on_content', self.gf('django.db.models.fields.related.ForeignKey')(related_name='comments', to=orm['modernpolitics.Content'])),
            ('text', self.gf('django.db.models.fields.TextField')(max_length=1000)),
            ('creator_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('modernpolitics', ['Comment'])

        # Adding model 'Forum'
        db.create_table('modernpolitics_forum', (
            ('content_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Content'], unique=True, primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='parent', null=True, to=orm['modernpolitics.Content'])),
        ))
        db.send_create_signal('modernpolitics', ['Forum'])

        # Adding M2M table for field children on 'Forum'
        db.create_table('modernpolitics_forum_children', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('forum', models.ForeignKey(orm['modernpolitics.forum'], null=False)),
            ('content', models.ForeignKey(orm['modernpolitics.content'], null=False))
        ))
        db.create_unique('modernpolitics_forum_children', ['forum_id', 'content_id'])

        # Adding model 'LegislationStatus'
        db.create_table('modernpolitics_legislationstatus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status_text', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('where', self.gf('django.db.models.fields.CharField')(max_length=4, null=True)),
            ('result', self.gf('django.db.models.fields.CharField')(max_length=20, null=True)),
            ('how', self.gf('django.db.models.fields.CharField')(max_length=20, null=True)),
            ('roll', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal('modernpolitics', ['LegislationStatus'])

        # Adding model 'LegislationSubjects'
        db.create_table('modernpolitics_legislationsubjects', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('term_name', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal('modernpolitics', ['LegislationSubjects'])

        # Adding model 'Legislation'
        db.create_table('modernpolitics_legislation', (
            ('content_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Content'], unique=True, primary_key=True)),
            ('bill_session', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('bill_type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('bill_number', self.gf('django.db.models.fields.IntegerField')()),
            ('bill_updated', self.gf('django.db.models.fields.DateTimeField')()),
            ('state_datetime', self.gf('django.db.models.fields.DateField')()),
            ('state_text', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('bill_status', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.LegislationStatus'], unique=True)),
            ('introduced_datetime', self.gf('django.db.models.fields.DateField')()),
            ('sponsor', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sponsor_id', null=True, to=orm['modernpolitics.ElectedOfficial'])),
            ('bill_summary', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal('modernpolitics', ['Legislation'])

        # Adding M2M table for field bill_relation on 'Legislation'
        db.create_table('modernpolitics_legislation_bill_relation', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_legislation', models.ForeignKey(orm['modernpolitics.legislation'], null=False)),
            ('to_legislation', models.ForeignKey(orm['modernpolitics.legislation'], null=False))
        ))
        db.create_unique('modernpolitics_legislation_bill_relation', ['from_legislation_id', 'to_legislation_id'])

        # Adding M2M table for field subjects on 'Legislation'
        db.create_table('modernpolitics_legislation_subjects', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('legislation', models.ForeignKey(orm['modernpolitics.legislation'], null=False)),
            ('legislationsubjects', models.ForeignKey(orm['modernpolitics.legislationsubjects'], null=False))
        ))
        db.create_unique('modernpolitics_legislation_subjects', ['legislation_id', 'legislationsubjects_id'])

        # Adding model 'LegislationCosponsor'
        db.create_table('modernpolitics_legislationcosponsor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('legislation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Legislation'])),
            ('elected_official', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.ElectedOfficial'])),
            ('joined', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('modernpolitics', ['LegislationCosponsor'])

        # Adding model 'LegislationTitle'
        db.create_table('modernpolitics_legislationtitle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bill', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Legislation'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('title_type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('title_as', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('modernpolitics', ['LegislationTitle'])

        # Adding model 'LegislationAction'
        db.create_table('modernpolitics_legislationaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bill', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Legislation'])),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('refer_committee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Committee'], null=True)),
            ('text', self.gf('django.db.models.fields.TextField')(null=True)),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('modernpolitics', ['LegislationAction'])

        # Adding model 'LegislationCalendar'
        db.create_table('modernpolitics_legislationcalendar', (
            ('legislationaction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.LegislationAction'], unique=True, primary_key=True)),
            ('calendar', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('calendar_number', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('under', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
        ))
        db.send_create_signal('modernpolitics', ['LegislationCalendar'])

        # Adding model 'LegislationVote'
        db.create_table('modernpolitics_legislationvote', (
            ('legislationaction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.LegislationAction'], unique=True, primary_key=True)),
            ('how', self.gf('django.db.models.fields.CharField')(max_length=150, null=True)),
            ('vote_type', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('roll', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('where', self.gf('django.db.models.fields.CharField')(max_length=4, null=True)),
            ('result', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('suspension', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
        ))
        db.send_create_signal('modernpolitics', ['LegislationVote'])

        # Adding model 'LegislationToPresident'
        db.create_table('modernpolitics_legislationtopresident', (
            ('legislationaction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.LegislationAction'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('modernpolitics', ['LegislationToPresident'])

        # Adding model 'LegislationSigned'
        db.create_table('modernpolitics_legislationsigned', (
            ('legislationaction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.LegislationAction'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('modernpolitics', ['LegislationSigned'])

        # Adding model 'LegislationEnacted'
        db.create_table('modernpolitics_legislationenacted', (
            ('legislationaction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.LegislationAction'], unique=True, primary_key=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
        ))
        db.send_create_signal('modernpolitics', ['LegislationEnacted'])

        # Adding model 'LegislationRefLabel'
        db.create_table('modernpolitics_legislationreflabel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.LegislationAction'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('ref', self.gf('django.db.models.fields.CharField')(max_length=1000)),
        ))
        db.send_create_signal('modernpolitics', ['LegislationRefLabel'])

        # Adding model 'LegislationCommittee'
        db.create_table('modernpolitics_legislationcommittee', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('legislation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Legislation'])),
            ('committee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Committee'], null=True)),
            ('activity', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal('modernpolitics', ['LegislationCommittee'])

        # Adding model 'LegislationAmendment'
        db.create_table('modernpolitics_legislationamendment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('session', self.gf('django.db.models.fields.IntegerField')()),
            ('chamber', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('legislation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Legislation'], null=True)),
            ('status_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=400)),
            ('sponsor_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.ElectedOfficial'], null=True)),
            ('committee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Committee'], null=True)),
            ('offered_datetime', self.gf('django.db.models.fields.DateField')(null=True)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=50000)),
            ('purpose', self.gf('django.db.models.fields.TextField')(max_length=5000)),
            ('amends_sequence', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal('modernpolitics', ['LegislationAmendment'])

        # Adding model 'RollOption'
        db.create_table('modernpolitics_rolloption', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('modernpolitics', ['RollOption'])

        # Adding model 'CongressRoll'
        db.create_table('modernpolitics_congressroll', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('where', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.CongressSessions'])),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
            ('roll_number', self.gf('django.db.models.fields.IntegerField')()),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('updated', self.gf('django.db.models.fields.DateTimeField')()),
            ('aye', self.gf('django.db.models.fields.IntegerField')()),
            ('nay', self.gf('django.db.models.fields.IntegerField')()),
            ('nv', self.gf('django.db.models.fields.IntegerField')()),
            ('present', self.gf('django.db.models.fields.IntegerField')()),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('question', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('required', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('result', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('bill', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Legislation'], null=True)),
            ('amendment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.LegislationAmendment'], null=True)),
        ))
        db.send_create_signal('modernpolitics', ['CongressRoll'])

        # Adding M2M table for field options on 'CongressRoll'
        db.create_table('modernpolitics_congressroll_options', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('congressroll', models.ForeignKey(orm['modernpolitics.congressroll'], null=False)),
            ('rolloption', models.ForeignKey(orm['modernpolitics.rolloption'], null=False))
        ))
        db.create_unique('modernpolitics_congressroll_options', ['congressroll_id', 'rolloption_id'])

        # Adding model 'VotingRecord'
        db.create_table('modernpolitics_votingrecord', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('electedofficial', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.ElectedOfficial'])),
            ('roll', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.CongressRoll'])),
            ('bill', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Legislation'], null=True)),
            ('amendment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.LegislationAmendment'], null=True)),
            ('votekey', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('votevalue', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('modernpolitics', ['VotingRecord'])

        # Adding model 'Answer'
        db.create_table('modernpolitics_answer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('answer_text', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('modernpolitics', ['Answer'])

        # Adding model 'Question'
        db.create_table('modernpolitics_question', (
            ('content_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Content'], unique=True, primary_key=True)),
            ('question_text', self.gf('django.db.models.fields.TextField')(max_length=500)),
            ('question_type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('relevant_info', self.gf('django.db.models.fields.TextField')(max_length=1000, null=True, blank=True)),
            ('official', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('lg_weight', self.gf('django.db.models.fields.IntegerField')(default=5)),
        ))
        db.send_create_signal('modernpolitics', ['Question'])

        # Adding M2M table for field answers on 'Question'
        db.create_table('modernpolitics_question_answers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('question', models.ForeignKey(orm['modernpolitics.question'], null=False)),
            ('answer', models.ForeignKey(orm['modernpolitics.answer'], null=False))
        ))
        db.create_unique('modernpolitics_question_answers', ['question_id', 'answer_id'])

        # Adding model 'NextQuestion'
        db.create_table('modernpolitics_nextquestion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_question', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fquestion', to=orm['modernpolitics.Question'])),
            ('to_question', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tquestion', to=orm['modernpolitics.Question'])),
            ('answer_value', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('relevancy', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('modernpolitics', ['NextQuestion'])

        # Adding model 'Response'
        db.create_table('modernpolitics_response', (
            ('content_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Content'], unique=True, primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Question'])),
            ('answer_val', self.gf('django.db.models.fields.IntegerField')()),
            ('weight', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('answers', self.gf('lovegov.beta.modernpolitics.custom_fields.ListField')(default=[])),
        ))
        db.send_create_signal('modernpolitics', ['Response'])

        # Adding model 'UserResponse'
        db.create_table('modernpolitics_userresponse', (
            ('response_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Response'], unique=True, primary_key=True)),
            ('responder', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.UserProfile'])),
            ('explanation', self.gf('django.db.models.fields.TextField')(max_length=1000, blank=True)),
        ))
        db.send_create_signal('modernpolitics', ['UserResponse'])

        # Adding model 'Message'
        db.create_table('modernpolitics_message', (
            ('content_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Content'], unique=True, primary_key=True)),
            ('debater', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.UserProfile'])),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('modernpolitics', ['Message'])

        # Adding model 'Persistent'
        db.create_table('modernpolitics_persistent', (
            ('content_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Content'], unique=True, primary_key=True)),
            ('affirmative', self.gf('django.db.models.fields.related.ForeignKey')(related_name='negative', null=True, to=orm['modernpolitics.UserProfile'])),
            ('negative', self.gf('django.db.models.fields.related.ForeignKey')(related_name='affirmative', null=True, to=orm['modernpolitics.UserProfile'])),
            ('moderator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='themoderator', null=True, to=orm['modernpolitics.UserProfile'])),
            ('resolution', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('debate_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('debate_start_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('debate_finish_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('debate_expiration_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('turns_total', self.gf('django.db.models.fields.IntegerField')(default=6)),
            ('allotted_response_delta', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('allotted_debate_delta', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('allotted_expiration_delta', self.gf('django.db.models.fields.IntegerField')(default=10080)),
            ('votes_affirmative', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('votes_negative', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('turns_elapsed', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('turn_current', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('turn_lasttime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('winner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='thewinner', null=True, to=orm['modernpolitics.UserProfile'])),
            ('debate_finished', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('voting_finished', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('modernpolitics', ['Persistent'])

        # Adding M2M table for field statements on 'Persistent'
        db.create_table('modernpolitics_persistent_statements', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('persistent', models.ForeignKey(orm['modernpolitics.persistent'], null=False)),
            ('message', models.ForeignKey(orm['modernpolitics.message'], null=False))
        ))
        db.create_unique('modernpolitics_persistent_statements', ['persistent_id', 'message_id'])

        # Adding M2M table for field possible_users on 'Persistent'
        db.create_table('modernpolitics_persistent_possible_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('persistent', models.ForeignKey(orm['modernpolitics.persistent'], null=False)),
            ('userprofile', models.ForeignKey(orm['modernpolitics.userprofile'], null=False))
        ))
        db.create_unique('modernpolitics_persistent_possible_users', ['persistent_id', 'userprofile_id'])

        # Adding model 'WorldView'
        db.create_table('modernpolitics_worldview', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('modernpolitics', ['WorldView'])

        # Adding M2M table for field responses on 'WorldView'
        db.create_table('modernpolitics_worldview_responses', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('worldview', models.ForeignKey(orm['modernpolitics.worldview'], null=False)),
            ('response', models.ForeignKey(orm['modernpolitics.response'], null=False))
        ))
        db.create_unique('modernpolitics_worldview_responses', ['worldview_id', 'response_id'])

        # Adding model 'TopicComparison'
        db.create_table('modernpolitics_topiccomparison', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('topic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Topic'])),
            ('result', self.gf('django.db.models.fields.IntegerField')()),
            ('num_q', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('modernpolitics', ['TopicComparison'])

        # Adding model 'ViewComparison'
        db.create_table('modernpolitics_viewcomparison', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('viewA', self.gf('django.db.models.fields.related.ForeignKey')(related_name='viewa', to=orm['modernpolitics.WorldView'])),
            ('viewB', self.gf('django.db.models.fields.related.ForeignKey')(related_name='viewb', to=orm['modernpolitics.WorldView'])),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('result', self.gf('django.db.models.fields.IntegerField')()),
            ('num_q', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('modernpolitics', ['ViewComparison'])

        # Adding M2M table for field bytopic on 'ViewComparison'
        db.create_table('modernpolitics_viewcomparison_bytopic', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('viewcomparison', models.ForeignKey(orm['modernpolitics.viewcomparison'], null=False)),
            ('topiccomparison', models.ForeignKey(orm['modernpolitics.topiccomparison'], null=False))
        ))
        db.create_unique('modernpolitics_viewcomparison_bytopic', ['viewcomparison_id', 'topiccomparison_id'])

        # Adding model 'UserComparison'
        db.create_table('modernpolitics_usercomparison', (
            ('viewcomparison_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.ViewComparison'], unique=True, primary_key=True)),
            ('userA', self.gf('django.db.models.fields.related.ForeignKey')(related_name='a', to=orm['modernpolitics.UserProfile'])),
            ('userB', self.gf('django.db.models.fields.related.ForeignKey')(related_name='b', to=orm['modernpolitics.UserProfile'])),
        ))
        db.send_create_signal('modernpolitics', ['UserComparison'])

        # Adding model 'AggregateTuple'
        db.create_table('modernpolitics_aggregatetuple', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('answer_val', self.gf('django.db.models.fields.IntegerField')()),
            ('tally', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('modernpolitics', ['AggregateTuple'])

        # Adding model 'AggregateResponse'
        db.create_table('modernpolitics_aggregateresponse', (
            ('response_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Response'], unique=True, primary_key=True)),
            ('answer_avg', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=4, decimal_places=2)),
            ('total', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('modernpolitics', ['AggregateResponse'])

        # Adding M2M table for field users on 'AggregateResponse'
        db.create_table('modernpolitics_aggregateresponse_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('aggregateresponse', models.ForeignKey(orm['modernpolitics.aggregateresponse'], null=False)),
            ('userprofile', models.ForeignKey(orm['modernpolitics.userprofile'], null=False))
        ))
        db.create_unique('modernpolitics_aggregateresponse_users', ['aggregateresponse_id', 'userprofile_id'])

        # Adding M2M table for field responses on 'AggregateResponse'
        db.create_table('modernpolitics_aggregateresponse_responses', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('aggregateresponse', models.ForeignKey(orm['modernpolitics.aggregateresponse'], null=False)),
            ('aggregatetuple', models.ForeignKey(orm['modernpolitics.aggregatetuple'], null=False))
        ))
        db.create_unique('modernpolitics_aggregateresponse_responses', ['aggregateresponse_id', 'aggregatetuple_id'])

        # Adding model 'Group'
        db.create_table('modernpolitics_group', (
            ('content_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Content'], unique=True, primary_key=True)),
            ('full_text', self.gf('django.db.models.fields.TextField')(max_length=1000)),
            ('group_view', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.WorldView'])),
            ('group_privacy', self.gf('django.db.models.fields.CharField')(default='O', max_length=1)),
            ('group_type', self.gf('django.db.models.fields.CharField')(default='U', max_length=1)),
            ('democratic', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('system', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('modernpolitics', ['Group'])

        # Adding M2M table for field admins on 'Group'
        db.create_table('modernpolitics_group_admins', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('group', models.ForeignKey(orm['modernpolitics.group'], null=False)),
            ('userprofile', models.ForeignKey(orm['modernpolitics.userprofile'], null=False))
        ))
        db.create_unique('modernpolitics_group_admins', ['group_id', 'userprofile_id'])

        # Adding M2M table for field members on 'Group'
        db.create_table('modernpolitics_group_members', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('group', models.ForeignKey(orm['modernpolitics.group'], null=False)),
            ('userprofile', models.ForeignKey(orm['modernpolitics.userprofile'], null=False))
        ))
        db.create_unique('modernpolitics_group_members', ['group_id', 'userprofile_id'])

        # Adding M2M table for field group_content on 'Group'
        db.create_table('modernpolitics_group_group_content', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('group', models.ForeignKey(orm['modernpolitics.group'], null=False)),
            ('content', models.ForeignKey(orm['modernpolitics.content'], null=False))
        ))
        db.create_unique('modernpolitics_group_group_content', ['group_id', 'content_id'])

        # Adding M2M table for field group_newfeed on 'Group'
        db.create_table('modernpolitics_group_group_newfeed', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('group', models.ForeignKey(orm['modernpolitics.group'], null=False)),
            ('feeditem', models.ForeignKey(orm['modernpolitics.feeditem'], null=False))
        ))
        db.create_unique('modernpolitics_group_group_newfeed', ['group_id', 'feeditem_id'])

        # Adding M2M table for field group_hotfeed on 'Group'
        db.create_table('modernpolitics_group_group_hotfeed', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('group', models.ForeignKey(orm['modernpolitics.group'], null=False)),
            ('feeditem', models.ForeignKey(orm['modernpolitics.feeditem'], null=False))
        ))
        db.create_unique('modernpolitics_group_group_hotfeed', ['group_id', 'feeditem_id'])

        # Adding M2M table for field group_bestfeed on 'Group'
        db.create_table('modernpolitics_group_group_bestfeed', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('group', models.ForeignKey(orm['modernpolitics.group'], null=False)),
            ('feeditem', models.ForeignKey(orm['modernpolitics.feeditem'], null=False))
        ))
        db.create_unique('modernpolitics_group_group_bestfeed', ['group_id', 'feeditem_id'])

        # Adding model 'Motion'
        db.create_table('modernpolitics_motion', (
            ('content_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Content'], unique=True, primary_key=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Group'])),
            ('motion_type', self.gf('django.db.models.fields.CharField')(default='O', max_length=1)),
            ('full_text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('modernpolitics', ['Motion'])

        # Adding model 'Network'
        db.create_table('modernpolitics_network', (
            ('group_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Group'], unique=True, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('extension', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
        ))
        db.send_create_signal('modernpolitics', ['Network'])

        # Adding model 'UserGroup'
        db.create_table('modernpolitics_usergroup', (
            ('group_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Group'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('modernpolitics', ['UserGroup'])

        # Adding model 'WidgetAccess'
        db.create_table('modernpolitics_widgetaccess', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=500, null=True)),
            ('host', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('which', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('modernpolitics', ['WidgetAccess'])

        # Adding model 'PageAccess'
        db.create_table('modernpolitics_pageaccess', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.UserProfile'])),
            ('ipaddress', self.gf('django.db.models.fields.IPAddressField')(default='255.255.255.255', max_length=15, null=True)),
            ('page', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('action', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('left', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('duration', self.gf('django.db.models.fields.TimeField')(null=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('exit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('login', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('modernpolitics', ['PageAccess'])

        # Adding model 'UserIPAddress'
        db.create_table('modernpolitics_useripaddress', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.UserProfile'])),
            ('ipaddress', self.gf('django.db.models.fields.IPAddressField')(default='255.255.255.255', max_length=15)),
            ('locID', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('modernpolitics', ['UserIPAddress'])

        # Adding model 'Script'
        db.create_table('modernpolitics_script', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('command', self.gf('django.db.models.fields.CharField')(max_length=400)),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('modernpolitics', ['Script'])

        # Adding model 'SentEmail'
        db.create_table('modernpolitics_sentemail', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('from_email', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('to_email', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('modernpolitics', ['SentEmail'])

        # Adding model 'Feedback'
        db.create_table('modernpolitics_feedback', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.UserProfile'])),
            ('feedback', self.gf('django.db.models.fields.TextField')()),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('page', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('modernpolitics', ['Feedback'])

        # Adding model 'EmailList'
        db.create_table('modernpolitics_emaillist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('modernpolitics', ['EmailList'])

        # Adding model 'Bug'
        db.create_table('modernpolitics_bug', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.UserProfile'])),
            ('error', self.gf('django.db.models.fields.TextField')()),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('page', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('modernpolitics', ['Bug'])

        # Adding model 'ValidEmail'
        db.create_table('modernpolitics_validemail', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('modernpolitics', ['ValidEmail'])

        # Adding model 'ValidEmailExtension'
        db.create_table('modernpolitics_validemailextension', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('extension', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('modernpolitics', ['ValidEmailExtension'])

        # Adding model 'Relationship'
        db.create_table('modernpolitics_relationship', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('privacy', self.gf('django.db.models.fields.CharField')(default='PUB', max_length=3)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.UserProfile'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='frel', to=orm['modernpolitics.UserProfile'])),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('relationship_type', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))
        db.send_create_signal('modernpolitics', ['Relationship'])

        # Adding model 'UCRelationship'
        db.create_table('modernpolitics_ucrelationship', (
            ('relationship_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Relationship'], unique=True, primary_key=True)),
            ('content', self.gf('django.db.models.fields.related.ForeignKey')(related_name='trel', to=orm['modernpolitics.Content'])),
        ))
        db.send_create_signal('modernpolitics', ['UCRelationship'])

        # Adding model 'DebateVoted'
        db.create_table('modernpolitics_debatevoted', (
            ('ucrelationship_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.UCRelationship'], unique=True, primary_key=True)),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('modernpolitics', ['DebateVoted'])

        # Adding model 'MotionVoted'
        db.create_table('modernpolitics_motionvoted', (
            ('ucrelationship_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.UCRelationship'], unique=True, primary_key=True)),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('modernpolitics', ['MotionVoted'])

        # Adding model 'Voted'
        db.create_table('modernpolitics_voted', (
            ('ucrelationship_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.UCRelationship'], unique=True, primary_key=True)),
            ('value', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('modernpolitics', ['Voted'])

        # Adding model 'Created'
        db.create_table('modernpolitics_created', (
            ('ucrelationship_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.UCRelationship'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('modernpolitics', ['Created'])

        # Adding model 'Deleted'
        db.create_table('modernpolitics_deleted', (
            ('ucrelationship_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.UCRelationship'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('modernpolitics', ['Deleted'])

        # Adding model 'Commented'
        db.create_table('modernpolitics_commented', (
            ('ucrelationship_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.UCRelationship'], unique=True, primary_key=True)),
            ('comment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Comment'])),
        ))
        db.send_create_signal('modernpolitics', ['Commented'])

        # Adding model 'Edited'
        db.create_table('modernpolitics_edited', (
            ('ucrelationship_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.UCRelationship'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('modernpolitics', ['Edited'])

        # Adding model 'Shared'
        db.create_table('modernpolitics_shared', (
            ('ucrelationship_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.UCRelationship'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('modernpolitics', ['Shared'])

        # Adding M2M table for field share_users on 'Shared'
        db.create_table('modernpolitics_shared_share_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('shared', models.ForeignKey(orm['modernpolitics.shared'], null=False)),
            ('userprofile', models.ForeignKey(orm['modernpolitics.userprofile'], null=False))
        ))
        db.create_unique('modernpolitics_shared_share_users', ['shared_id', 'userprofile_id'])

        # Adding M2M table for field share_groups on 'Shared'
        db.create_table('modernpolitics_shared_share_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('shared', models.ForeignKey(orm['modernpolitics.shared'], null=False)),
            ('group', models.ForeignKey(orm['modernpolitics.group'], null=False))
        ))
        db.create_unique('modernpolitics_shared_share_groups', ['shared_id', 'group_id'])

        # Adding model 'Followed'
        db.create_table('modernpolitics_followed', (
            ('ucrelationship_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.UCRelationship'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('modernpolitics', ['Followed'])

        # Adding model 'Attending'
        db.create_table('modernpolitics_attending', (
            ('ucrelationship_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.UCRelationship'], unique=True, primary_key=True)),
            ('confirmed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('invited', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('requested', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('inviter', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('rejected', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('declined', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('choice', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('modernpolitics', ['Attending'])

        # Adding model 'GroupJoined'
        db.create_table('modernpolitics_groupjoined', (
            ('ucrelationship_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.UCRelationship'], unique=True, primary_key=True)),
            ('confirmed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('invited', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('requested', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('inviter', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('rejected', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('declined', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Group'])),
        ))
        db.send_create_signal('modernpolitics', ['GroupJoined'])

        # Adding model 'DebateJoined'
        db.create_table('modernpolitics_debatejoined', (
            ('ucrelationship_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.UCRelationship'], unique=True, primary_key=True)),
            ('confirmed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('invited', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('requested', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('inviter', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('rejected', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('declined', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('debate', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Persistent'])),
        ))
        db.send_create_signal('modernpolitics', ['DebateJoined'])

        # Adding model 'UURelationship'
        db.create_table('modernpolitics_uurelationship', (
            ('relationship_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Relationship'], unique=True, primary_key=True)),
            ('to_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tuser', to=orm['modernpolitics.UserProfile'])),
        ))
        db.send_create_signal('modernpolitics', ['UURelationship'])

        # Adding model 'UserFollow'
        db.create_table('modernpolitics_userfollow', (
            ('uurelationship_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.UURelationship'], unique=True, primary_key=True)),
            ('confirmed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('invited', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('requested', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('inviter', self.gf('django.db.models.fields.IntegerField')(default=-1)),
            ('rejected', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('declined', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('fb', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('modernpolitics', ['UserFollow'])

        # Adding model 'Linked'
        db.create_table('modernpolitics_linked', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_content', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fcontent', to=orm['modernpolitics.Content'])),
            ('to_content', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tcontent', to=orm['modernpolitics.Content'])),
            ('link_strength', self.gf('django.db.models.fields.IntegerField')()),
            ('link_bonus', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('association_strength', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('modernpolitics', ['Linked'])

        # Adding model 'MyContent'
        db.create_table('modernpolitics_mycontent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Content'])),
            ('rank', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('modernpolitics', ['MyContent'])

        # Adding model 'MyPeople'
        db.create_table('modernpolitics_mypeople', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.UserProfile'])),
            ('rank', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('modernpolitics', ['MyPeople'])

        # Adding model 'MyAction'
        db.create_table('modernpolitics_myaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Action'])),
            ('rank', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('modernpolitics', ['MyAction'])

        # Adding model 'TopicView'
        db.create_table('modernpolitics_topicview', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('privacy', self.gf('django.db.models.fields.CharField')(default='PUB', max_length=3)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.UserProfile'])),
            ('view', self.gf('django.db.models.fields.TextField')(max_length=10000, blank=True)),
            ('topic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Topic'])),
        ))
        db.send_create_signal('modernpolitics', ['TopicView'])

        # Adding model 'ProfilePage'
        db.create_table('modernpolitics_profilepage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.UserProfile'])),
            ('bio', self.gf('django.db.models.fields.TextField')(max_length=5000, blank=True)),
        ))
        db.send_create_signal('modernpolitics', ['ProfilePage'])

        # Adding M2M table for field my_views on 'ProfilePage'
        db.create_table('modernpolitics_profilepage_my_views', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('profilepage', models.ForeignKey(orm['modernpolitics.profilepage'], null=False)),
            ('topicview', models.ForeignKey(orm['modernpolitics.topicview'], null=False))
        ))
        db.create_unique('modernpolitics_profilepage_my_views', ['profilepage_id', 'topicview_id'])

        # Adding M2M table for field my_content on 'ProfilePage'
        db.create_table('modernpolitics_profilepage_my_content', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('profilepage', models.ForeignKey(orm['modernpolitics.profilepage'], null=False)),
            ('mycontent', models.ForeignKey(orm['modernpolitics.mycontent'], null=False))
        ))
        db.create_unique('modernpolitics_profilepage_my_content', ['profilepage_id', 'mycontent_id'])

        # Adding M2M table for field my_people on 'ProfilePage'
        db.create_table('modernpolitics_profilepage_my_people', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('profilepage', models.ForeignKey(orm['modernpolitics.profilepage'], null=False)),
            ('mypeople', models.ForeignKey(orm['modernpolitics.mypeople'], null=False))
        ))
        db.create_unique('modernpolitics_profilepage_my_people', ['profilepage_id', 'mypeople_id'])

        # Adding M2M table for field my_activity on 'ProfilePage'
        db.create_table('modernpolitics_profilepage_my_activity', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('profilepage', models.ForeignKey(orm['modernpolitics.profilepage'], null=False)),
            ('myaction', models.ForeignKey(orm['modernpolitics.myaction'], null=False))
        ))
        db.create_unique('modernpolitics_profilepage_my_activity', ['profilepage_id', 'myaction_id'])

        # Adding model 'US_State'
        db.create_table('modernpolitics_us_state', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('modernpolitics', ['US_State'])

        # Adding model 'US_Counties'
        db.create_table('modernpolitics_us_counties', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('state', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.US_State'], unique=True)),
        ))
        db.send_create_signal('modernpolitics', ['US_Counties'])

        # Adding model 'US_ConDistr'
        db.create_table('modernpolitics_us_condistr', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('state', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.US_State'], unique=True)),
        ))
        db.send_create_signal('modernpolitics', ['US_ConDistr'])

        # Adding model 'Debate'
        db.create_table('modernpolitics_debate', (
            ('content_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Content'], unique=True, primary_key=True)),
            ('moderator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='moderator', to=orm['modernpolitics.UserProfile'])),
            ('full_descript', self.gf('django.db.models.fields.TextField')(max_length=10000)),
            ('debate_when', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('modernpolitics', ['Debate'])

        # Adding model 'Debaters'
        db.create_table('modernpolitics_debaters', (
            ('ucrelationship_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.UCRelationship'], unique=True, primary_key=True)),
            ('side', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('modernpolitics', ['Debaters'])

        # Adding model 'DebateMessage'
        db.create_table('modernpolitics_debatemessage', (
            ('content_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Content'], unique=True, primary_key=True)),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Debate'])),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.UserProfile'])),
            ('message_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('debate_side', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=3000)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('modernpolitics', ['DebateMessage'])

        # Adding model 'LoveGov'
        db.create_table('modernpolitics_lovegov', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('default', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('average_votes', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('average_rating', self.gf('django.db.models.fields.IntegerField')(default=50)),
            ('lovegov_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='lovegovuser', null=True, to=orm['modernpolitics.UserProfile'])),
            ('lovegov_group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='anonuser', null=True, to=orm['modernpolitics.Group'])),
            ('anon_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.UserProfile'], null=True)),
            ('default_image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.UserImage'], null=True)),
            ('default_filter', self.gf('django.db.models.fields.related.ForeignKey')(related_name='defaultfilter', null=True, to=orm['modernpolitics.FilterSetting'])),
            ('best_filter', self.gf('django.db.models.fields.related.ForeignKey')(related_name='bestfilter', null=True, to=orm['modernpolitics.FilterSetting'])),
            ('new_filter', self.gf('django.db.models.fields.related.ForeignKey')(related_name='newfilter', null=True, to=orm['modernpolitics.FilterSetting'])),
            ('hot_filter', self.gf('django.db.models.fields.related.ForeignKey')(related_name='hotfilter', null=True, to=orm['modernpolitics.FilterSetting'])),
            ('worldview', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.WorldView'], null=True)),
        ))
        db.send_create_signal('modernpolitics', ['LoveGov'])

        # Adding model 'LoveGovSetting'
        db.create_table('modernpolitics_lovegovsetting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('default', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('setting', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('modernpolitics', ['LoveGovSetting'])

        # Adding model 'QuestionDiscussed'
        db.create_table('modernpolitics_questiondiscussed', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Question'])),
            ('num_comments', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('modernpolitics', ['QuestionDiscussed'])

        # Adding model 'Feed'
        db.create_table('modernpolitics_feed', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('modernpolitics', ['Feed'])

        # Adding M2M table for field items on 'Feed'
        db.create_table('modernpolitics_feed_items', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('feed', models.ForeignKey(orm['modernpolitics.feed'], null=False)),
            ('feeditem', models.ForeignKey(orm['modernpolitics.feeditem'], null=False))
        ))
        db.create_unique('modernpolitics_feed_items', ['feed_id', 'feeditem_id'])

        # Adding model 'qOrdered'
        db.create_table('modernpolitics_qordered', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Question'])),
            ('rank', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('modernpolitics', ['qOrdered'])

        # Adding model 'QuestionOrdering'
        db.create_table('modernpolitics_questionordering', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('alias', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('modernpolitics', ['QuestionOrdering'])

        # Adding M2M table for field questions on 'QuestionOrdering'
        db.create_table('modernpolitics_questionordering_questions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('questionordering', models.ForeignKey(orm['modernpolitics.questionordering'], null=False)),
            ('qordered', models.ForeignKey(orm['modernpolitics.qordered'], null=False))
        ))
        db.create_unique('modernpolitics_questionordering_questions', ['questionordering_id', 'qordered_id'])


    def backwards(self, orm):
        # Deleting model 'UserPhysicalAddress'
        db.delete_table('modernpolitics_userphysicaladdress')

        # Deleting model 'Topic'
        db.delete_table('modernpolitics_topic')

        # Deleting model 'Content'
        db.delete_table('modernpolitics_content')

        # Removing M2M table for field topics on 'Content'
        db.delete_table('modernpolitics_content_topics')

        # Deleting model 'UserImage'
        db.delete_table('modernpolitics_userimage')

        # Deleting model 'BasicInfo'
        db.delete_table('modernpolitics_basicinfo')

        # Deleting model 'Involved'
        db.delete_table('modernpolitics_involved')

        # Deleting model 'FeedItem'
        db.delete_table('modernpolitics_feeditem')

        # Deleting model 'DebateResult'
        db.delete_table('modernpolitics_debateresult')

        # Deleting model 'CustomNotificationSetting'
        db.delete_table('modernpolitics_customnotificationsetting')

        # Deleting model 'TopicWeight'
        db.delete_table('modernpolitics_topicweight')

        # Deleting model 'TypeWeight'
        db.delete_table('modernpolitics_typeweight')

        # Deleting model 'FilterSetting'
        db.delete_table('modernpolitics_filtersetting')

        # Removing M2M table for field topic_weights on 'FilterSetting'
        db.delete_table('modernpolitics_filtersetting_topic_weights')

        # Removing M2M table for field type_weights on 'FilterSetting'
        db.delete_table('modernpolitics_filtersetting_type_weights')

        # Deleting model 'RegisterCode'
        db.delete_table('modernpolitics_registercode')

        # Deleting model 'UserProfile'
        db.delete_table('modernpolitics_userprofile')

        # Removing M2M table for field debate_record on 'UserProfile'
        db.delete_table('modernpolitics_userprofile_debate_record')

        # Removing M2M table for field my_involvement on 'UserProfile'
        db.delete_table('modernpolitics_userprofile_my_involvement')

        # Removing M2M table for field my_history on 'UserProfile'
        db.delete_table('modernpolitics_userprofile_my_history')

        # Removing M2M table for field privileges on 'UserProfile'
        db.delete_table('modernpolitics_userprofile_privileges')

        # Removing M2M table for field my_feed on 'UserProfile'
        db.delete_table('modernpolitics_userprofile_my_feed')

        # Removing M2M table for field custom_notification_settings on 'UserProfile'
        db.delete_table('modernpolitics_userprofile_custom_notification_settings')

        # Deleting model 'UserPermission'
        db.delete_table('modernpolitics_userpermission')

        # Deleting model 'ControllingUser'
        db.delete_table('modernpolitics_controllinguser')

        # Deleting model 'Action'
        db.delete_table('modernpolitics_action')

        # Deleting model 'Notification'
        db.delete_table('modernpolitics_notification')

        # Removing M2M table for field users on 'Notification'
        db.delete_table('modernpolitics_notification_users')

        # Deleting model 'ElectedOfficial'
        db.delete_table('modernpolitics_electedofficial')

        # Deleting model 'Politician'
        db.delete_table('modernpolitics_politician')

        # Deleting model 'CongressSessions'
        db.delete_table('modernpolitics_congresssessions')

        # Removing M2M table for field people on 'CongressSessions'
        db.delete_table('modernpolitics_congresssessions_people')

        # Deleting model 'SelectMan'
        db.delete_table('modernpolitics_selectman')

        # Deleting model 'Senator'
        db.delete_table('modernpolitics_senator')

        # Deleting model 'Representative'
        db.delete_table('modernpolitics_representative')

        # Deleting model 'USPresident'
        db.delete_table('modernpolitics_uspresident')

        # Deleting model 'Committee'
        db.delete_table('modernpolitics_committee')

        # Deleting model 'CommitteeMember'
        db.delete_table('modernpolitics_committeemember')

        # Deleting model 'Petition'
        db.delete_table('modernpolitics_petition')

        # Removing M2M table for field signers on 'Petition'
        db.delete_table('modernpolitics_petition_signers')

        # Deleting model 'Event'
        db.delete_table('modernpolitics_event')

        # Deleting model 'News'
        db.delete_table('modernpolitics_news')

        # Deleting model 'UserPost'
        db.delete_table('modernpolitics_userpost')

        # Deleting model 'PhotoAlbum'
        db.delete_table('modernpolitics_photoalbum')

        # Removing M2M table for field photos on 'PhotoAlbum'
        db.delete_table('modernpolitics_photoalbum_photos')

        # Deleting model 'Comment'
        db.delete_table('modernpolitics_comment')

        # Deleting model 'Forum'
        db.delete_table('modernpolitics_forum')

        # Removing M2M table for field children on 'Forum'
        db.delete_table('modernpolitics_forum_children')

        # Deleting model 'LegislationStatus'
        db.delete_table('modernpolitics_legislationstatus')

        # Deleting model 'LegislationSubjects'
        db.delete_table('modernpolitics_legislationsubjects')

        # Deleting model 'Legislation'
        db.delete_table('modernpolitics_legislation')

        # Removing M2M table for field bill_relation on 'Legislation'
        db.delete_table('modernpolitics_legislation_bill_relation')

        # Removing M2M table for field subjects on 'Legislation'
        db.delete_table('modernpolitics_legislation_subjects')

        # Deleting model 'LegislationCosponsor'
        db.delete_table('modernpolitics_legislationcosponsor')

        # Deleting model 'LegislationTitle'
        db.delete_table('modernpolitics_legislationtitle')

        # Deleting model 'LegislationAction'
        db.delete_table('modernpolitics_legislationaction')

        # Deleting model 'LegislationCalendar'
        db.delete_table('modernpolitics_legislationcalendar')

        # Deleting model 'LegislationVote'
        db.delete_table('modernpolitics_legislationvote')

        # Deleting model 'LegislationToPresident'
        db.delete_table('modernpolitics_legislationtopresident')

        # Deleting model 'LegislationSigned'
        db.delete_table('modernpolitics_legislationsigned')

        # Deleting model 'LegislationEnacted'
        db.delete_table('modernpolitics_legislationenacted')

        # Deleting model 'LegislationRefLabel'
        db.delete_table('modernpolitics_legislationreflabel')

        # Deleting model 'LegislationCommittee'
        db.delete_table('modernpolitics_legislationcommittee')

        # Deleting model 'LegislationAmendment'
        db.delete_table('modernpolitics_legislationamendment')

        # Deleting model 'RollOption'
        db.delete_table('modernpolitics_rolloption')

        # Deleting model 'CongressRoll'
        db.delete_table('modernpolitics_congressroll')

        # Removing M2M table for field options on 'CongressRoll'
        db.delete_table('modernpolitics_congressroll_options')

        # Deleting model 'VotingRecord'
        db.delete_table('modernpolitics_votingrecord')

        # Deleting model 'Answer'
        db.delete_table('modernpolitics_answer')

        # Deleting model 'Question'
        db.delete_table('modernpolitics_question')

        # Removing M2M table for field answers on 'Question'
        db.delete_table('modernpolitics_question_answers')

        # Deleting model 'NextQuestion'
        db.delete_table('modernpolitics_nextquestion')

        # Deleting model 'Response'
        db.delete_table('modernpolitics_response')

        # Deleting model 'UserResponse'
        db.delete_table('modernpolitics_userresponse')

        # Deleting model 'Message'
        db.delete_table('modernpolitics_message')

        # Deleting model 'Persistent'
        db.delete_table('modernpolitics_persistent')

        # Removing M2M table for field statements on 'Persistent'
        db.delete_table('modernpolitics_persistent_statements')

        # Removing M2M table for field possible_users on 'Persistent'
        db.delete_table('modernpolitics_persistent_possible_users')

        # Deleting model 'WorldView'
        db.delete_table('modernpolitics_worldview')

        # Removing M2M table for field responses on 'WorldView'
        db.delete_table('modernpolitics_worldview_responses')

        # Deleting model 'TopicComparison'
        db.delete_table('modernpolitics_topiccomparison')

        # Deleting model 'ViewComparison'
        db.delete_table('modernpolitics_viewcomparison')

        # Removing M2M table for field bytopic on 'ViewComparison'
        db.delete_table('modernpolitics_viewcomparison_bytopic')

        # Deleting model 'UserComparison'
        db.delete_table('modernpolitics_usercomparison')

        # Deleting model 'AggregateTuple'
        db.delete_table('modernpolitics_aggregatetuple')

        # Deleting model 'AggregateResponse'
        db.delete_table('modernpolitics_aggregateresponse')

        # Removing M2M table for field users on 'AggregateResponse'
        db.delete_table('modernpolitics_aggregateresponse_users')

        # Removing M2M table for field responses on 'AggregateResponse'
        db.delete_table('modernpolitics_aggregateresponse_responses')

        # Deleting model 'Group'
        db.delete_table('modernpolitics_group')

        # Removing M2M table for field admins on 'Group'
        db.delete_table('modernpolitics_group_admins')

        # Removing M2M table for field members on 'Group'
        db.delete_table('modernpolitics_group_members')

        # Removing M2M table for field group_content on 'Group'
        db.delete_table('modernpolitics_group_group_content')

        # Removing M2M table for field group_newfeed on 'Group'
        db.delete_table('modernpolitics_group_group_newfeed')

        # Removing M2M table for field group_hotfeed on 'Group'
        db.delete_table('modernpolitics_group_group_hotfeed')

        # Removing M2M table for field group_bestfeed on 'Group'
        db.delete_table('modernpolitics_group_group_bestfeed')

        # Deleting model 'Motion'
        db.delete_table('modernpolitics_motion')

        # Deleting model 'Network'
        db.delete_table('modernpolitics_network')

        # Deleting model 'UserGroup'
        db.delete_table('modernpolitics_usergroup')

        # Deleting model 'WidgetAccess'
        db.delete_table('modernpolitics_widgetaccess')

        # Deleting model 'PageAccess'
        db.delete_table('modernpolitics_pageaccess')

        # Deleting model 'UserIPAddress'
        db.delete_table('modernpolitics_useripaddress')

        # Deleting model 'Script'
        db.delete_table('modernpolitics_script')

        # Deleting model 'SentEmail'
        db.delete_table('modernpolitics_sentemail')

        # Deleting model 'Feedback'
        db.delete_table('modernpolitics_feedback')

        # Deleting model 'EmailList'
        db.delete_table('modernpolitics_emaillist')

        # Deleting model 'Bug'
        db.delete_table('modernpolitics_bug')

        # Deleting model 'ValidEmail'
        db.delete_table('modernpolitics_validemail')

        # Deleting model 'ValidEmailExtension'
        db.delete_table('modernpolitics_validemailextension')

        # Deleting model 'Relationship'
        db.delete_table('modernpolitics_relationship')

        # Deleting model 'UCRelationship'
        db.delete_table('modernpolitics_ucrelationship')

        # Deleting model 'DebateVoted'
        db.delete_table('modernpolitics_debatevoted')

        # Deleting model 'MotionVoted'
        db.delete_table('modernpolitics_motionvoted')

        # Deleting model 'Voted'
        db.delete_table('modernpolitics_voted')

        # Deleting model 'Created'
        db.delete_table('modernpolitics_created')

        # Deleting model 'Deleted'
        db.delete_table('modernpolitics_deleted')

        # Deleting model 'Commented'
        db.delete_table('modernpolitics_commented')

        # Deleting model 'Edited'
        db.delete_table('modernpolitics_edited')

        # Deleting model 'Shared'
        db.delete_table('modernpolitics_shared')

        # Removing M2M table for field share_users on 'Shared'
        db.delete_table('modernpolitics_shared_share_users')

        # Removing M2M table for field share_groups on 'Shared'
        db.delete_table('modernpolitics_shared_share_groups')

        # Deleting model 'Followed'
        db.delete_table('modernpolitics_followed')

        # Deleting model 'Attending'
        db.delete_table('modernpolitics_attending')

        # Deleting model 'GroupJoined'
        db.delete_table('modernpolitics_groupjoined')

        # Deleting model 'DebateJoined'
        db.delete_table('modernpolitics_debatejoined')

        # Deleting model 'UURelationship'
        db.delete_table('modernpolitics_uurelationship')

        # Deleting model 'UserFollow'
        db.delete_table('modernpolitics_userfollow')

        # Deleting model 'Linked'
        db.delete_table('modernpolitics_linked')

        # Deleting model 'MyContent'
        db.delete_table('modernpolitics_mycontent')

        # Deleting model 'MyPeople'
        db.delete_table('modernpolitics_mypeople')

        # Deleting model 'MyAction'
        db.delete_table('modernpolitics_myaction')

        # Deleting model 'TopicView'
        db.delete_table('modernpolitics_topicview')

        # Deleting model 'ProfilePage'
        db.delete_table('modernpolitics_profilepage')

        # Removing M2M table for field my_views on 'ProfilePage'
        db.delete_table('modernpolitics_profilepage_my_views')

        # Removing M2M table for field my_content on 'ProfilePage'
        db.delete_table('modernpolitics_profilepage_my_content')

        # Removing M2M table for field my_people on 'ProfilePage'
        db.delete_table('modernpolitics_profilepage_my_people')

        # Removing M2M table for field my_activity on 'ProfilePage'
        db.delete_table('modernpolitics_profilepage_my_activity')

        # Deleting model 'US_State'
        db.delete_table('modernpolitics_us_state')

        # Deleting model 'US_Counties'
        db.delete_table('modernpolitics_us_counties')

        # Deleting model 'US_ConDistr'
        db.delete_table('modernpolitics_us_condistr')

        # Deleting model 'Debate'
        db.delete_table('modernpolitics_debate')

        # Deleting model 'Debaters'
        db.delete_table('modernpolitics_debaters')

        # Deleting model 'DebateMessage'
        db.delete_table('modernpolitics_debatemessage')

        # Deleting model 'LoveGov'
        db.delete_table('modernpolitics_lovegov')

        # Deleting model 'LoveGovSetting'
        db.delete_table('modernpolitics_lovegovsetting')

        # Deleting model 'QuestionDiscussed'
        db.delete_table('modernpolitics_questiondiscussed')

        # Deleting model 'Feed'
        db.delete_table('modernpolitics_feed')

        # Removing M2M table for field items on 'Feed'
        db.delete_table('modernpolitics_feed_items')

        # Deleting model 'qOrdered'
        db.delete_table('modernpolitics_qordered')

        # Deleting model 'QuestionOrdering'
        db.delete_table('modernpolitics_questionordering')

        # Removing M2M table for field questions on 'QuestionOrdering'
        db.delete_table('modernpolitics_questionordering_questions')


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
            'status': ('django.db.models.fields.IntegerField', [], {'default': '20'}),
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
            'my_connections': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
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