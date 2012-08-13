# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'LegislationEnacted'
        db.delete_table('modernpolitics_legislationenacted')

        # Deleting model 'CommitteeMember'
        db.delete_table('modernpolitics_committeemember')

        # Deleting model 'VotingRecord'
        db.delete_table('modernpolitics_votingrecord')

        # Deleting model 'Legislation'
        db.delete_table('modernpolitics_legislation')

        # Removing M2M table for field bill_relation on 'Legislation'
        db.delete_table('modernpolitics_legislation_bill_relation')

        # Removing M2M table for field subjects on 'Legislation'
        db.delete_table('modernpolitics_legislation_subjects')

        # Deleting model 'LegislationVote'
        db.delete_table('modernpolitics_legislationvote')

        # Deleting model 'LegislationRefLabel'
        db.delete_table('modernpolitics_legislationreflabel')

        # Deleting model 'LegislationStatus'
        db.delete_table('modernpolitics_legislationstatus')

        # Deleting model 'CongressRoll'
        db.delete_table('modernpolitics_congressroll')

        # Removing M2M table for field options on 'CongressRoll'
        db.delete_table('modernpolitics_congressroll_options')

        # Deleting model 'LegislationCosponsor'
        db.delete_table('modernpolitics_legislationcosponsor')

        # Deleting model 'ProfilePage'
        db.delete_table('modernpolitics_profilepage')

        # Removing M2M table for field my_content on 'ProfilePage'
        db.delete_table('modernpolitics_profilepage_my_content')

        # Removing M2M table for field my_people on 'ProfilePage'
        db.delete_table('modernpolitics_profilepage_my_people')

        # Removing M2M table for field my_activity on 'ProfilePage'
        db.delete_table('modernpolitics_profilepage_my_activity')

        # Removing M2M table for field my_views on 'ProfilePage'
        db.delete_table('modernpolitics_profilepage_my_views')

        # Deleting model 'USPresident'
        db.delete_table('modernpolitics_uspresident')

        # Deleting model 'LegislationCommittee'
        db.delete_table('modernpolitics_legislationcommittee')

        # Deleting model 'LegislationSubjects'
        db.delete_table('modernpolitics_legislationsubjects')

        # Deleting model 'RollOption'
        db.delete_table('modernpolitics_rolloption')

        # Deleting model 'LegislationSigned'
        db.delete_table('modernpolitics_legislationsigned')

        # Deleting model 'SelectMan'
        db.delete_table('modernpolitics_selectman')

        # Deleting model 'LegislationTitle'
        db.delete_table('modernpolitics_legislationtitle')

        # Deleting model 'Senator'
        db.delete_table('modernpolitics_senator')

        # Deleting model 'Committee'
        db.delete_table('modernpolitics_committee')

        # Deleting model 'Representative'
        db.delete_table('modernpolitics_representative')

        # Deleting model 'LegislationAmendment'
        db.delete_table('modernpolitics_legislationamendment')

        # Deleting model 'ElectedOfficial'
        db.delete_table('modernpolitics_electedofficial')

        # Deleting model 'LegislationToPresident'
        db.delete_table('modernpolitics_legislationtopresident')

        # Deleting model 'LegislationCalendar'
        db.delete_table('modernpolitics_legislationcalendar')

        # Deleting model 'CongressSessions'
        db.delete_table('modernpolitics_congresssessions')

        # Removing M2M table for field people on 'CongressSessions'
        db.delete_table('modernpolitics_congresssessions_people')

        # Deleting model 'Politician'
        db.delete_table('modernpolitics_politician')

        # Deleting model 'LegislationAction'
        db.delete_table('modernpolitics_legislationaction')

        # Adding model 'OfficeTag'
        db.create_table('modernpolitics_officetag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('modernpolitics', ['OfficeTag'])

        # Adding model 'Office'
        db.create_table('modernpolitics_office', (
            ('content_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Content'], unique=True, primary_key=True)),
            ('governmental', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('modernpolitics', ['Office'])

        # Adding M2M table for field tags on 'Office'
        db.create_table('modernpolitics_office_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('office', models.ForeignKey(orm['modernpolitics.office'], null=False)),
            ('officetag', models.ForeignKey(orm['modernpolitics.officetag'], null=False))
        ))
        db.create_unique('modernpolitics_office_tags', ['office_id', 'officetag_id'])


        # Changing field 'Motion.expiration_date'
        db.alter_column('modernpolitics_motion', 'expiration_date', self.gf('django.db.models.fields.DateTimeField')())
        # Deleting field 'UserProfile.user_type'
        db.delete_column('modernpolitics_userprofile', 'user_type')

        # Deleting field 'UserProfile.type'
        db.delete_column('modernpolitics_userprofile', 'type')

        # Adding field 'UserProfile.ghost'
        db.add_column('modernpolitics_userprofile', 'ghost',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'UserProfile.politician'
        db.add_column('modernpolitics_userprofile', 'politician',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'UserProfile.elected_official'
        db.add_column('modernpolitics_userprofile', 'elected_official',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'UserProfile.num_supporters'
        db.add_column('modernpolitics_userprofile', 'num_supporters',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'UserProfile.govtrack_id'
        db.add_column('modernpolitics_userprofile', 'govtrack_id',
                      self.gf('django.db.models.fields.IntegerField')(default=-1),
                      keep_default=False)

        # Adding M2M table for field supporters on 'UserProfile'
        db.create_table('modernpolitics_userprofile_supporters', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_userprofile', models.ForeignKey(orm['modernpolitics.userprofile'], null=False)),
            ('to_userprofile', models.ForeignKey(orm['modernpolitics.userprofile'], null=False))
        ))
        db.create_unique('modernpolitics_userprofile_supporters', ['from_userprofile_id', 'to_userprofile_id'])

        # Adding field 'GroupJoined.ever_member'
        db.add_column('modernpolitics_groupjoined', 'ever_member',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'LegislationEnacted'
        db.create_table('modernpolitics_legislationenacted', (
            ('state', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('legislationaction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.LegislationAction'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('modernpolitics', ['LegislationEnacted'])

        # Adding model 'CommitteeMember'
        db.create_table('modernpolitics_committeemember', (
            ('electedOfficial', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.ElectedOfficial'])),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.CongressSessions'])),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('committee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Committee'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('modernpolitics', ['CommitteeMember'])

        # Adding model 'VotingRecord'
        db.create_table('modernpolitics_votingrecord', (
            ('amendment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.LegislationAmendment'], null=True)),
            ('votevalue', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('votekey', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('bill', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Legislation'], null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('electedofficial', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.ElectedOfficial'])),
            ('roll', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.CongressRoll'])),
        ))
        db.send_create_signal('modernpolitics', ['VotingRecord'])

        # Adding model 'Legislation'
        db.create_table('modernpolitics_legislation', (
            ('bill_status', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.LegislationStatus'], unique=True)),
            ('introduced_datetime', self.gf('django.db.models.fields.DateField')()),
            ('bill_summary', self.gf('django.db.models.fields.TextField')(null=True)),
            ('bill_type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('bill_session', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('sponsor', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sponsor_id', null=True, to=orm['modernpolitics.ElectedOfficial'])),
            ('bill_updated', self.gf('django.db.models.fields.DateTimeField')()),
            ('state_datetime', self.gf('django.db.models.fields.DateField')()),
            ('bill_number', self.gf('django.db.models.fields.IntegerField')()),
            ('content_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Content'], unique=True, primary_key=True)),
            ('state_text', self.gf('django.db.models.fields.CharField')(max_length=500)),
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

        # Adding model 'LegislationVote'
        db.create_table('modernpolitics_legislationvote', (
            ('how', self.gf('django.db.models.fields.CharField')(max_length=150, null=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('result', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('suspension', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('vote_type', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('legislationaction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.LegislationAction'], unique=True, primary_key=True)),
            ('where', self.gf('django.db.models.fields.CharField')(max_length=4, null=True)),
            ('roll', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal('modernpolitics', ['LegislationVote'])

        # Adding model 'LegislationRefLabel'
        db.create_table('modernpolitics_legislationreflabel', (
            ('action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.LegislationAction'])),
            ('ref', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=1000)),
        ))
        db.send_create_signal('modernpolitics', ['LegislationRefLabel'])

        # Adding model 'LegislationStatus'
        db.create_table('modernpolitics_legislationstatus', (
            ('how', self.gf('django.db.models.fields.CharField')(max_length=20, null=True)),
            ('result', self.gf('django.db.models.fields.CharField')(max_length=20, null=True)),
            ('roll', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('status_text', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('where', self.gf('django.db.models.fields.CharField')(max_length=4, null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('modernpolitics', ['LegislationStatus'])

        # Adding model 'CongressRoll'
        db.create_table('modernpolitics_congressroll', (
            ('amendment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.LegislationAmendment'], null=True)),
            ('bill', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Legislation'], null=True)),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.CongressSessions'])),
            ('result', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('aye', self.gf('django.db.models.fields.IntegerField')()),
            ('question', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('nay', self.gf('django.db.models.fields.IntegerField')()),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('nv', self.gf('django.db.models.fields.IntegerField')()),
            ('updated', self.gf('django.db.models.fields.DateTimeField')()),
            ('present', self.gf('django.db.models.fields.IntegerField')()),
            ('required', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('roll_number', self.gf('django.db.models.fields.IntegerField')()),
            ('where', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('modernpolitics', ['CongressRoll'])

        # Adding M2M table for field options on 'CongressRoll'
        db.create_table('modernpolitics_congressroll_options', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('congressroll', models.ForeignKey(orm['modernpolitics.congressroll'], null=False)),
            ('rolloption', models.ForeignKey(orm['modernpolitics.rolloption'], null=False))
        ))
        db.create_unique('modernpolitics_congressroll_options', ['congressroll_id', 'rolloption_id'])

        # Adding model 'LegislationCosponsor'
        db.create_table('modernpolitics_legislationcosponsor', (
            ('legislation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Legislation'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('elected_official', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.ElectedOfficial'])),
            ('joined', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('modernpolitics', ['LegislationCosponsor'])

        # Adding model 'ProfilePage'
        db.create_table('modernpolitics_profilepage', (
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.UserProfile'])),
            ('bio', self.gf('django.db.models.fields.TextField')(max_length=5000, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('modernpolitics', ['ProfilePage'])

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

        # Adding M2M table for field my_views on 'ProfilePage'
        db.create_table('modernpolitics_profilepage_my_views', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('profilepage', models.ForeignKey(orm['modernpolitics.profilepage'], null=False)),
            ('topicview', models.ForeignKey(orm['modernpolitics.topicview'], null=False))
        ))
        db.create_unique('modernpolitics_profilepage_my_views', ['profilepage_id', 'topicview_id'])

        # Adding model 'USPresident'
        db.create_table('modernpolitics_uspresident', (
            ('electedofficial_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.ElectedOfficial'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('modernpolitics', ['USPresident'])

        # Adding model 'LegislationCommittee'
        db.create_table('modernpolitics_legislationcommittee', (
            ('legislation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Legislation'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('committee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Committee'], null=True)),
            ('activity', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal('modernpolitics', ['LegislationCommittee'])

        # Adding model 'LegislationSubjects'
        db.create_table('modernpolitics_legislationsubjects', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('term_name', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal('modernpolitics', ['LegislationSubjects'])

        # Adding model 'RollOption'
        db.create_table('modernpolitics_rolloption', (
            ('text', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('modernpolitics', ['RollOption'])

        # Adding model 'LegislationSigned'
        db.create_table('modernpolitics_legislationsigned', (
            ('legislationaction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.LegislationAction'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('modernpolitics', ['LegislationSigned'])

        # Adding model 'SelectMan'
        db.create_table('modernpolitics_selectman', (
            ('electedofficial_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.ElectedOfficial'], unique=True, primary_key=True)),
            ('represents', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal('modernpolitics', ['SelectMan'])

        # Adding model 'LegislationTitle'
        db.create_table('modernpolitics_legislationtitle', (
            ('title_as', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('bill', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Legislation'])),
            ('title_type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('modernpolitics', ['LegislationTitle'])

        # Adding model 'Senator'
        db.create_table('modernpolitics_senator', (
            ('classNum', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('electedofficial_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.ElectedOfficial'], unique=True, primary_key=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2, null=True)),
        ))
        db.send_create_signal('modernpolitics', ['Senator'])

        # Adding model 'Committee'
        db.create_table('modernpolitics_committee', (
            ('code', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Committee'], null=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('modernpolitics', ['Committee'])

        # Adding model 'Representative'
        db.create_table('modernpolitics_representative', (
            ('electedofficial_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.ElectedOfficial'], unique=True, primary_key=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2, null=True)),
            ('district', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal('modernpolitics', ['Representative'])

        # Adding model 'LegislationAmendment'
        db.create_table('modernpolitics_legislationamendment', (
            ('status', self.gf('django.db.models.fields.CharField')(max_length=400)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=50000)),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('offered_datetime', self.gf('django.db.models.fields.DateField')(null=True)),
            ('session', self.gf('django.db.models.fields.IntegerField')()),
            ('purpose', self.gf('django.db.models.fields.TextField')(max_length=5000)),
            ('committee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Committee'], null=True)),
            ('sponsor_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.ElectedOfficial'], null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('amends_sequence', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('legislation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Legislation'], null=True)),
            ('chamber', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal('modernpolitics', ['LegislationAmendment'])

        # Adding model 'ElectedOfficial'
        db.create_table('modernpolitics_electedofficial', (
            ('govtrack_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('os_id', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('youtube_id', self.gf('django.db.models.fields.CharField')(max_length=150, null=True)),
            ('official_name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('bioguide_id', self.gf('django.db.models.fields.CharField')(max_length=50, null=True)),
            ('metavid_id', self.gf('django.db.models.fields.CharField')(max_length=150, null=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1, null=True)),
            ('twitter_id', self.gf('django.db.models.fields.CharField')(max_length=150, null=True)),
            ('politician_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.Politician'], unique=True, primary_key=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('pvs_id', self.gf('django.db.models.fields.IntegerField')(null=True)),
        ))
        db.send_create_signal('modernpolitics', ['ElectedOfficial'])

        # Adding model 'LegislationToPresident'
        db.create_table('modernpolitics_legislationtopresident', (
            ('legislationaction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.LegislationAction'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('modernpolitics', ['LegislationToPresident'])

        # Adding model 'LegislationCalendar'
        db.create_table('modernpolitics_legislationcalendar', (
            ('calendar_number', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('calendar', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('legislationaction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.LegislationAction'], unique=True, primary_key=True)),
            ('under', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
        ))
        db.send_create_signal('modernpolitics', ['LegislationCalendar'])

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

        # Adding model 'Politician'
        db.create_table('modernpolitics_politician', (
            ('num_messages', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('office_seeking', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('num_supporters', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('userprofile_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['modernpolitics.UserProfile'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('modernpolitics', ['Politician'])

        # Adding model 'LegislationAction'
        db.create_table('modernpolitics_legislationaction', (
            ('text', self.gf('django.db.models.fields.TextField')(null=True)),
            ('bill', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Legislation'])),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')()),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('refer_committee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['modernpolitics.Committee'], null=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('modernpolitics', ['LegislationAction'])

        # Deleting model 'OfficeTag'
        db.delete_table('modernpolitics_officetag')

        # Deleting model 'Office'
        db.delete_table('modernpolitics_office')

        # Removing M2M table for field tags on 'Office'
        db.delete_table('modernpolitics_office_tags')


        # Changing field 'Motion.expiration_date'
        db.alter_column('modernpolitics_motion', 'expiration_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))
        # Adding field 'UserProfile.user_type'
        db.add_column('modernpolitics_userprofile', 'user_type',
                      self.gf('django.db.models.fields.CharField')(default='G', max_length=1),
                      keep_default=False)

        # Adding field 'UserProfile.type'
        db.add_column('modernpolitics_userprofile', 'type',
                      self.gf('django.db.models.fields.CharField')(default='U', max_length=1),
                      keep_default=False)

        # Deleting field 'UserProfile.ghost'
        db.delete_column('modernpolitics_userprofile', 'ghost')

        # Deleting field 'UserProfile.politician'
        db.delete_column('modernpolitics_userprofile', 'politician')

        # Deleting field 'UserProfile.elected_official'
        db.delete_column('modernpolitics_userprofile', 'elected_official')

        # Deleting field 'UserProfile.num_supporters'
        db.delete_column('modernpolitics_userprofile', 'num_supporters')

        # Deleting field 'UserProfile.govtrack_id'
        db.delete_column('modernpolitics_userprofile', 'govtrack_id')

        # Removing M2M table for field supporters on 'UserProfile'
        db.delete_table('modernpolitics_userprofile_supporters')

        # Deleting field 'GroupJoined.ever_member'
        db.delete_column('modernpolitics_groupjoined', 'ever_member')


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
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['modernpolitics.UserProfile']"}),
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
        'modernpolitics.comment': {
            'Meta': {'object_name': 'Comment', '_ormbases': ['modernpolitics.Content']},
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'creator_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'on_content': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': "orm['modernpolitics.Content']"}),
            'root_content': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'root_content'", 'to': "orm['modernpolitics.Content']"}),
            'text': ('django.db.models.fields.TextField', [], {'max_length': '10000'})
        },
        'modernpolitics.commented': {
            'Meta': {'object_name': 'Commented', '_ormbases': ['modernpolitics.UCRelationship']},
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Comment']"}),
            'ucrelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UCRelationship']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.content': {
            'Meta': {'object_name': 'Content'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'alias': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '1000'}),
            'calculated_view': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.WorldView']", 'null': 'True', 'blank': 'True'}),
            'content_privacy': ('django.db.models.fields.CharField', [], {'default': "'O'", 'max_length': '1'}),
            'created_when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['modernpolitics.UserProfile']"}),
            'downvotes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_calc': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'in_feed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'in_search': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
        'modernpolitics.created': {
            'Meta': {'object_name': 'Created', '_ormbases': ['modernpolitics.UCRelationship']},
            'ucrelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UCRelationship']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.customnotificationsetting': {
            'Meta': {'object_name': 'CustomNotificationSetting'},
            'alerts': ('lovegov.modernpolitics.custom_fields.ListField', [], {}),
            'content': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Content']", 'null': 'True'}),
            'email': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']", 'null': 'True'})
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
        'modernpolitics.debateresult': {
            'Meta': {'object_name': 'DebateResult'},
            'debate': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '1'})
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
        'modernpolitics.discussion': {
            'Meta': {'object_name': 'Discussion', '_ormbases': ['modernpolitics.Content']},
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.edited': {
            'Meta': {'object_name': 'Edited', '_ormbases': ['modernpolitics.UCRelationship']},
            'ucrelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UCRelationship']", 'unique': 'True', 'primary_key': 'True'})
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
            'hot_window': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'similarity': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'topic_weights': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.TopicWeight']", 'symmetrical': 'False'}),
            'type_weights': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.TypeWeight']", 'symmetrical': 'False'})
        },
        'modernpolitics.followed': {
            'Meta': {'object_name': 'Followed', '_ormbases': ['modernpolitics.UCRelationship']},
            'ucrelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UCRelationship']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.group': {
            'Meta': {'object_name': 'Group', '_ormbases': ['modernpolitics.Content']},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'admin'", 'symmetrical': 'False', 'to': "orm['modernpolitics.UserProfile']"}),
            'agreement_threshold': ('django.db.models.fields.IntegerField', [], {'default': '50'}),
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'democratic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'full_text': ('django.db.models.fields.TextField', [], {'max_length': '1000'}),
            'government_type': ('django.db.models.fields.CharField', [], {'default': "'traditional'", 'max_length': '30'}),
            'group_content': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'ongroup'", 'symmetrical': 'False', 'to': "orm['modernpolitics.Content']"}),
            'group_privacy': ('django.db.models.fields.CharField', [], {'default': "'O'", 'max_length': '1'}),
            'group_type': ('django.db.models.fields.CharField', [], {'default': "'S'", 'max_length': '1'}),
            'group_view': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.WorldView']"}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'member'", 'symmetrical': 'False', 'to': "orm['modernpolitics.UserProfile']"}),
            'motion_expiration': ('django.db.models.fields.IntegerField', [], {'default': '7'}),
            'num_members': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'participation_threshold': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'system': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'modernpolitics.groupjoined': {
            'Meta': {'object_name': 'GroupJoined', '_ormbases': ['modernpolitics.UCRelationship']},
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'declined': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ever_member': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
        'modernpolitics.messaged': {
            'Meta': {'object_name': 'Messaged', '_ormbases': ['modernpolitics.UURelationship']},
            'message': ('django.db.models.fields.TextField', [], {}),
            'uurelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UURelationship']", 'unique': 'True', 'primary_key': 'True'})
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'network_type': ('django.db.models.fields.CharField', [], {'default': "'D'", 'max_length': '1'})
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
            'anon_users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'anonymous_notify_agg_users'", 'symmetrical': 'False', 'to': "orm['modernpolitics.UserProfile']"}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['modernpolitics.UserProfile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ignored': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modifier': ('django.db.models.fields.CharField', [], {'default': "'D'", 'max_length': '1'}),
            'notify_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notifywho'", 'to': "orm['modernpolitics.UserProfile']"}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'PUB'", 'max_length': '3'}),
            'recent_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'mostrecentuser'", 'null': 'True', 'to': "orm['modernpolitics.UserProfile']"}),
            'tally': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'trig_content': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'trigcontent'", 'null': 'True', 'to': "orm['modernpolitics.Content']"}),
            'trig_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'griguser'", 'null': 'True', 'to': "orm['modernpolitics.UserProfile']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'notifyagg'", 'symmetrical': 'False', 'to': "orm['modernpolitics.UserProfile']"}),
            'verbose': ('django.db.models.fields.TextField', [], {}),
            'viewed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'modernpolitics.office': {
            'Meta': {'object_name': 'Office', '_ormbases': ['modernpolitics.Content']},
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'governmental': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'tag_offices'", 'symmetrical': 'False', 'to': "orm['modernpolitics.OfficeTag']"})
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
            'current': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'finalized': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'full_text': ('django.db.models.fields.TextField', [], {'max_length': '10000'}),
            'goal': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'p_level': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'signers': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'petitions'", 'symmetrical': 'False', 'to': "orm['modernpolitics.UserProfile']"})
        },
        'modernpolitics.photoalbum': {
            'Meta': {'object_name': 'PhotoAlbum', '_ormbases': ['modernpolitics.Content']},
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'photos': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.UserImage']", 'symmetrical': 'False'})
        },
        'modernpolitics.physicaladdress': {
            'Meta': {'object_name': 'PhysicalAddress'},
            'address_string': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True'}),
            'district': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '30', 'decimal_places': '15'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '30', 'decimal_places': '15'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'})
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
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['modernpolitics.UserProfile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'PUB'", 'max_length': '3'}),
            'relationship_type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'frel'", 'to': "orm['modernpolitics.UserProfile']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
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
            'answer_val': ('django.db.models.fields.IntegerField', [], {}),
            'answers': ('lovegov.modernpolitics.custom_fields.ListField', [], {'default': '[]'}),
            'content_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Content']", 'unique': 'True', 'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Question']"}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '5'})
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
        'modernpolitics.simplefilter': {
            'Meta': {'object_name': 'SimpleFilter'},
            'created_when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']", 'null': 'True'}),
            'display': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '1'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.Group']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'levels': ('lovegov.modernpolitics.custom_fields.ListField', [], {'default': '[]'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.PhysicalAddress']", 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '200'}),
            'ranking': ('django.db.models.fields.CharField', [], {'default': "'H'", 'max_length': '1'}),
            'submissions_only': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'topics': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.Topic']", 'symmetrical': 'False'}),
            'types': ('lovegov.modernpolitics.custom_fields.ListField', [], {})
        },
        'modernpolitics.supported': {
            'Meta': {'object_name': 'Supported', '_ormbases': ['modernpolitics.UURelationship']},
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'uurelationship_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.UURelationship']", 'unique': 'True', 'primary_key': 'True'})
        },
        'modernpolitics.topic': {
            'Meta': {'object_name': 'Topic'},
            'alias': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '30'}),
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
            'num_q': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'result': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.Topic']"})
        },
        'modernpolitics.topicview': {
            'Meta': {'object_name': 'TopicView'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['modernpolitics.UserProfile']"}),
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
        'modernpolitics.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'about_me': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'access_token': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'address': ('lovegov.modernpolitics.custom_fields.ListField', [], {'default': '[]'}),
            'alias': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'anonymous': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.AnonID']", 'symmetrical': 'False'}),
            'bio': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'blog_url': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'confirmation_link': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content_notification_setting': ('lovegov.modernpolitics.custom_fields.ListField', [], {}),
            'created_when': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'custom_notification_settings': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.CustomNotificationSetting']", 'symmetrical': 'False'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'debate_record': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.DebateResult']", 'symmetrical': 'False'}),
            'developer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'dob': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'elected_official': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'email_notification_setting': ('lovegov.modernpolitics.custom_fields.ListField', [], {}),
            'ethnicity': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'evolve': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'facebook_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'facebook_profile_url': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'fb_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'filter_setting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.FilterSetting']", 'null': 'True'}),
            'first_login': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'follow_me': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'follow_me'", 'null': 'True', 'to': "orm['modernpolitics.Group']"}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'ghost': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'govtrack_id': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'i_follow': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'i_follow'", 'null': 'True', 'to': "orm['modernpolitics.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invite_message': ('django.db.models.fields.CharField', [], {'default': '"LoveGov Alpha is now up and running! We would really appreciate it if you logged in and test run the features of our site. Please keep in mind that Alpha only contains a portion of the functionality intended for the Brown/RISD beta, so you will see us regularly adding new features over the next month. If you encounter any problems while using our siteor just want to send us comments then please don\'t hesitate to contact us - we want to hear your opinions!"', 'max_length': '10000', 'blank': 'True'}),
            'invite_subject': ('django.db.models.fields.CharField', [], {'default': "'Welcome to LoveGov Alpha'", 'max_length': '1000', 'blank': 'True'}),
            'last_answered': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'last_page_access': ('django.db.models.fields.IntegerField', [], {'default': '-1', 'null': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.PhysicalAddress']", 'null': 'True'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'my_feed': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'newfeed'", 'symmetrical': 'False', 'to': "orm['modernpolitics.FeedItem']"}),
            'my_filters': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.SimpleFilter']", 'symmetrical': 'False'}),
            'my_history': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'history'", 'symmetrical': 'False', 'to': "orm['modernpolitics.Content']"}),
            'my_involvement': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['modernpolitics.Involved']", 'symmetrical': 'False'}),
            'networks': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'networks'", 'symmetrical': 'False', 'to': "orm['modernpolitics.Network']"}),
            'nick_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'num_articles': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_petitions': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_supporters': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parties': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'parties'", 'symmetrical': 'False', 'to': "orm['modernpolitics.Party']"}),
            'party': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'political_role': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'politician': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'private_follow': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'privileges': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'priv'", 'symmetrical': 'False', 'to': "orm['modernpolitics.Content']"}),
            'profile_image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserImage']", 'null': 'True'}),
            'raw_data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'registration_code': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.RegisterCode']", 'null': 'True'}),
            'religion': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'supporters': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'supportees'", 'symmetrical': 'False', 'to': "orm['modernpolitics.UserProfile']"}),
            'twitter_screen_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'twitter_user_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
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
        'modernpolitics.userresponse': {
            'Meta': {'object_name': 'UserResponse', '_ormbases': ['modernpolitics.Response']},
            'explanation': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'blank': 'True'}),
            'responder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['modernpolitics.UserProfile']"}),
            'response_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['modernpolitics.Response']", 'unique': 'True', 'primary_key': 'True'})
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