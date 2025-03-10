# Copyright 2018 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for core.domain.takeout_service."""

from __future__ import absolute_import  # pylint: disable=import-only-modules
from __future__ import unicode_literals  # pylint: disable=import-only-modules

import datetime
import json

from constants import constants
from core.domain import exp_domain
from core.domain import exp_services
from core.domain import feedback_services
from core.domain import rights_domain
from core.domain import takeout_domain
from core.domain import takeout_service
from core.domain import topic_domain
from core.platform import models
from core.tests import test_utils
import feconf
import python_utils
import utils

(
    app_feedback_report_models, auth_models, base_models, blog_models,
    collection_models, config_models, email_models, exploration_models,
    feedback_models, improvements_models, question_models, skill_models,
    story_models, subtopic_models, suggestion_models, topic_models, user_models
) = models.Registry.import_models([
    models.NAMES.app_feedback_report, models.NAMES.auth,
    models.NAMES.base_model, models.NAMES.blog, models.NAMES.collection,
    models.NAMES.config, models.NAMES.email, models.NAMES.exploration,
    models.NAMES.feedback, models.NAMES.improvements, models.NAMES.question,
    models.NAMES.skill, models.NAMES.story, models.NAMES.subtopic,
    models.NAMES.suggestion, models.NAMES.topic, models.NAMES.user
])


class TakeoutServiceProfileUserUnitTests(test_utils.GenericTestBase):
    """Tests for the takeout service for profile user."""

    USER_ID_1 = 'user_1'
    PROFILE_ID_1 = 'profile_1'
    USER_1_ROLE = feconf.ROLE_ID_ADMIN
    PROFILE_1_ROLE = feconf.ROLE_ID_LEARNER
    USER_1_EMAIL = 'user1@example.com'
    GENERIC_USERNAME = 'user'
    GENERIC_DATE = datetime.datetime(2019, 5, 20)
    GENERIC_EPOCH = utils.get_time_in_millisecs(GENERIC_DATE)
    GENERIC_IMAGE_URL = 'www.example.com/example.png'
    GENERIC_USER_BIO = 'I am a user of Oppia!'
    GENERIC_SUBJECT_INTERESTS = ['Math', 'Science']
    GENERIC_LANGUAGE_CODES = ['en', 'es']
    GENERIC_DISPLAY_ALIAS = 'display_alias'
    GENERIC_DISPLAY_ALIAS_2 = 'display_alias2'
    EXPLORATION_IDS = ['exp_1']
    EXPLORATION_IDS_2 = ['exp_2']
    COLLECTION_IDS = ['23', '42', '4']
    COLLECTION_IDS_2 = ['32', '44', '6']
    STORY_IDS = ['12', '22', '32']
    STORY_IDS_2 = ['42', '52', '62']
    TOPIC_IDS = ['11', '21', '31']
    TOPIC_IDS_2 = ['41', '51', '61']
    SKILL_ID_1 = 'skill_id_1'
    SKILL_ID_2 = 'skill_id_2'
    SKILL_ID_3 = 'skill_id_3'
    DEGREE_OF_MASTERY = 0.5
    DEGREE_OF_MASTERY_2 = 0.6
    EXP_VERSION = 1
    STATE_NAME = 'state_name'
    STORY_ID_1 = 'story_id_1'
    COMPLETED_NODE_IDS_1 = ['node_id_1', 'node_id_2']

    def set_up_non_trivial(self):
        """Set up all models for use in testing.
        1) Simulates skill mastery of user_1 and profile_1.
        2) Simulates completion of some activities of user_1 and profile_1.
        3) Simulates incomplete status of some activities.
        4) Populates ExpUserLastPlaythroughModel of user.
        5) Creates user LearnerPlaylsts.
        6) Simulates collection progress of user.
        7) Simulates story progress of user.
        8) Creates new collection rights.
        9) Simulates a general suggestion.
        10) Creates new exploration rights.
        11) Populates user settings.
        """
        # Setup for UserSkillModel.
        user_models.UserSkillMasteryModel(
            id=user_models.UserSkillMasteryModel.construct_model_id(
                self.USER_ID_1, self.SKILL_ID_3),
            user_id=self.USER_ID_1,
            skill_id=self.SKILL_ID_3,
            degree_of_mastery=self.DEGREE_OF_MASTERY_2).put()
        user_models.UserSkillMasteryModel(
            id=user_models.UserSkillMasteryModel.construct_model_id(
                self.PROFILE_ID_1, self.SKILL_ID_1),
            user_id=self.PROFILE_ID_1,
            skill_id=self.SKILL_ID_1,
            degree_of_mastery=self.DEGREE_OF_MASTERY).put()

        # Setup for CompletedActivitiesModel.
        user_models.CompletedActivitiesModel(
            id=self.USER_ID_1,
            exploration_ids=self.EXPLORATION_IDS_2,
            collection_ids=self.COLLECTION_IDS_2,
            story_ids=self.STORY_IDS_2,
            learnt_topic_ids=self.TOPIC_IDS_2).put()
        user_models.CompletedActivitiesModel(
            id=self.PROFILE_ID_1,
            exploration_ids=self.EXPLORATION_IDS,
            collection_ids=self.COLLECTION_IDS,
            story_ids=self.STORY_IDS,
            learnt_topic_ids=self.TOPIC_IDS).put()

        # Setup for IncompleteACtivitiesModel.
        user_models.IncompleteActivitiesModel(
            id=self.PROFILE_ID_1,
            exploration_ids=self.EXPLORATION_IDS,
            collection_ids=self.COLLECTION_IDS,
            story_ids=self.STORY_IDS_2,
            partially_learnt_topic_ids=self.TOPIC_IDS).put()

        # Setup for ExpUserLastPlaythroughModel.
        user_models.ExpUserLastPlaythroughModel(
            id='%s.%s' % (self.PROFILE_ID_1, self.EXPLORATION_IDS[0]),
            user_id=self.PROFILE_ID_1, exploration_id=self.EXPLORATION_IDS[0],
            last_played_exp_version=self.EXP_VERSION,
            last_played_state_name=self.STATE_NAME).put()

        # Setup for LearnerPlaylistModel.
        user_models.LearnerPlaylistModel(
            id=self.PROFILE_ID_1,
            exploration_ids=self.EXPLORATION_IDS,
            collection_ids=self.COLLECTION_IDS).put()

        # Setup for CollectionProgressModel.
        user_models.CollectionProgressModel(
            id='%s.%s' % (self.PROFILE_ID_1, self.COLLECTION_IDS[0]),
            user_id=self.PROFILE_ID_1,
            collection_id=self.COLLECTION_IDS[0],
            completed_explorations=self.EXPLORATION_IDS).put()

        # Setup for StoryProgressModel.
        user_models.StoryProgressModel(
            id='%s.%s' % (self.PROFILE_ID_1, self.STORY_ID_1),
            user_id=self.PROFILE_ID_1,
            story_id=self.STORY_ID_1,
            completed_node_ids=self.COMPLETED_NODE_IDS_1).put()

        # Setup for UserSettingsModel.
        user_models.UserSettingsModel(
            id=self.USER_ID_1,
            email=self.USER_1_EMAIL,
            role=self.USER_1_ROLE,
            username=self.GENERIC_USERNAME,
            normalized_username=self.GENERIC_USERNAME,
            last_agreed_to_terms=self.GENERIC_DATE,
            last_started_state_editor_tutorial=self.GENERIC_DATE,
            last_started_state_translation_tutorial=self.GENERIC_DATE,
            last_logged_in=self.GENERIC_DATE,
            last_created_an_exploration=self.GENERIC_DATE,
            last_edited_an_exploration=self.GENERIC_DATE,
            profile_picture_data_url=self.GENERIC_IMAGE_URL,
            default_dashboard='learner', creator_dashboard_display_pref='card',
            user_bio=self.GENERIC_USER_BIO,
            subject_interests=self.GENERIC_SUBJECT_INTERESTS,
            first_contribution_msec=1,
            preferred_language_codes=self.GENERIC_LANGUAGE_CODES,
            preferred_site_language_code=self.GENERIC_LANGUAGE_CODES[0],
            preferred_audio_language_code=self.GENERIC_LANGUAGE_CODES[0],
            display_alias=self.GENERIC_DISPLAY_ALIAS
        ).put()
        user_models.UserSettingsModel(
            id=self.PROFILE_ID_1,
            email=self.USER_1_EMAIL,
            role=self.PROFILE_1_ROLE,
            username=None,
            normalized_username=None,
            last_agreed_to_terms=self.GENERIC_DATE,
            last_started_state_editor_tutorial=None,
            last_started_state_translation_tutorial=None,
            last_logged_in=self.GENERIC_DATE,
            last_created_an_exploration=None,
            last_edited_an_exploration=None,
            profile_picture_data_url=None,
            default_dashboard='learner', creator_dashboard_display_pref='card',
            user_bio=self.GENERIC_USER_BIO,
            subject_interests=self.GENERIC_SUBJECT_INTERESTS,
            first_contribution_msec=None,
            preferred_language_codes=self.GENERIC_LANGUAGE_CODES,
            preferred_site_language_code=self.GENERIC_LANGUAGE_CODES[0],
            preferred_audio_language_code=self.GENERIC_LANGUAGE_CODES[0],
            display_alias=self.GENERIC_DISPLAY_ALIAS_2
        ).put()

    def set_up_trivial(self):
        """Setup for trivial test of export_data functionality."""
        user_models.UserSettingsModel(
            id=self.USER_ID_1,
            email=self.USER_1_EMAIL,
            role=self.USER_1_ROLE
        ).put()
        user_models.UserSettingsModel(
            id=self.PROFILE_ID_1,
            email=self.USER_1_EMAIL,
            role=self.PROFILE_1_ROLE
        ).put()

    def test_export_data_for_profile_user_trivial_raises_error(self):
        """Trivial test of export_data functionality."""

        self.set_up_trivial()
        error_msg = 'Takeout for profile users is not yet supported.'
        with self.assertRaisesRegexp(NotImplementedError, error_msg):
            takeout_service.export_data_for_user(self.PROFILE_ID_1)

    def test_export_data_for_profile_user_nontrivial_raises_error(self):
        """Nontrivial test of export_data functionality."""

        self.set_up_non_trivial()
        error_msg = 'Takeout for profile users is not yet supported.'
        with self.assertRaisesRegexp(NotImplementedError, error_msg):
            takeout_service.export_data_for_user(self.PROFILE_ID_1)


class TakeoutServiceFullUserUnitTests(test_utils.GenericTestBase):
    """Tests for the takeout service for full user."""

    USER_ID_1 = 'user_1'
    PROFILE_ID_1 = 'profile_1'
    THREAD_ID_1 = 'thread_id_1'
    THREAD_ID_2 = 'thread_id_2'
    BLOG_POST_ID_1 = 'blog_post_id_1'
    BLOG_POST_ID_2 = 'blog_post_id_2'
    TOPIC_ID_1 = 'topic_id_1'
    TOPIC_ID_2 = 'topic_id_2'
    USER_1_ROLE = feconf.ROLE_ID_ADMIN
    PROFILE_1_ROLE = feconf.ROLE_ID_LEARNER
    USER_1_EMAIL = 'user1@example.com'
    GENERIC_USERNAME = 'user'
    GENERIC_PIN = '12345'
    GENERIC_DATE = datetime.datetime(2019, 5, 20)
    GENERIC_EPOCH = utils.get_time_in_millisecs(GENERIC_DATE)
    GENERIC_IMAGE_URL = 'www.example.com/example.png'
    GENERIC_USER_BIO = 'I am a user of Oppia!'
    GENERIC_SUBJECT_INTERESTS = ['Math', 'Science']
    GENERIC_LANGUAGE_CODES = ['en', 'es']
    GENERIC_DISPLAY_ALIAS = 'display_alias'
    GENERIC_DISPLAY_ALIAS_2 = 'display_alias2'
    USER_1_IMPACT_SCORE = 0.87
    USER_1_TOTAL_PLAYS = 33
    USER_1_AVERAGE_RATINGS = 4.37
    USER_1_NUM_RATINGS = 22
    USER_1_WEEKLY_CREATOR_STATS_LIST = [
        {
            ('2019-05-21'): {
                'average_ratings': 4.00,
                'total_plays': 5
            }
        },
        {
            ('2019-05-28'): {
                'average_ratings': 4.95,
                'total_plays': 10
            }
        }
    ]
    EXPLORATION_IDS = ['exp_1']
    EXPLORATION_IDS_2 = ['exp_2']
    STORY_IDS = ['12', '22', '32']
    STORY_IDS_2 = ['42', '52', '62']
    TOPIC_IDS = ['11', '21', '31']
    TOPIC_IDS_2 = ['41', '51', '61']
    CREATOR_IDS = ['4', '8', '16']
    CREATOR_USERNAMES = ['username4', 'username8', 'username16']
    COLLECTION_IDS = ['23', '42', '4']
    COLLECTION_IDS_2 = ['32', '44', '6']
    GENERAL_FEEDBACK_THREAD_IDS = ['42', '4', '8']
    MESSAGE_IDS_READ_BY_USER = [0, 1]
    SKILL_ID_1 = 'skill_id_1'
    SKILL_ID_2 = 'skill_id_2'
    SKILL_ID_3 = 'skill_id_3'
    DEGREE_OF_MASTERY = 0.5
    DEGREE_OF_MASTERY_2 = 0.6
    EXP_VERSION = 1
    STATE_NAME = 'state_name'
    STORY_ID_1 = 'story_id_1'
    STORY_ID_2 = 'story_id_2'
    COMPLETED_NODE_IDS_1 = ['node_id_1', 'node_id_2']
    COMPLETED_NODE_IDS_2 = ['node_id_3', 'node_id_4']
    THREAD_ENTITY_TYPE = feconf.ENTITY_TYPE_EXPLORATION
    THREAD_ENTITY_ID = 'exp_id_2'
    THREAD_STATUS = 'open'
    THREAD_SUBJECT = 'dummy subject'
    THREAD_HAS_SUGGESTION = True
    THREAD_SUMMARY = 'This is a great summary.'
    THREAD_MESSAGE_COUNT = 0
    MESSAGE_TEXT = 'Export test text.'
    MESSAGE_RECEIEVED_VIA_EMAIL = False
    CHANGE_CMD = {}
    SCORE_CATEGORY_1 = 'category_1'
    SCORE_CATEGORY_2 = 'category_2'
    SCORE_CATEGORY = (
        suggestion_models.SCORE_TYPE_TRANSLATION +
        suggestion_models.SCORE_CATEGORY_DELIMITER + 'English')
    GENERIC_MODEL_ID = 'model-id-1'
    COMMIT_TYPE = 'create'
    COMMIT_MESSAGE = 'This is a commit.'
    COMMIT_CMDS = [
        {'cmd': 'some_command'},
        {'cmd2': 'another_command'}
    ]
    PLATFORM_ANDROID = 'android'
    # Timestamp in sec since epoch for Mar 7 2021 21:17:16 UTC.
    REPORT_SUBMITTED_TIMESTAMP = datetime.datetime.fromtimestamp(1615151836)
    # Timestamp in sec since epoch for Mar 19 2021 17:10:36 UTC.
    TICKET_CREATION_TIMESTAMP = datetime.datetime.fromtimestamp(1616173836)
    TICKET_ID = '%s.%s.%s' % (
        'random_hash', TICKET_CREATION_TIMESTAMP.second, '16CharString1234')
    REPORT_TYPE_SUGGESTION = 'suggestion'
    CATEGORY_OTHER = 'other'
    PLATFORM_VERSION = '0.1-alpha-abcdef1234'
    DEVICE_COUNTRY_LOCALE_CODE_INDIA = 'in'
    ANDROID_DEVICE_MODEL = 'Pixel 4a'
    ANDROID_SDK_VERSION = 28
    ENTRY_POINT_NAVIGATION_DRAWER = 'navigation_drawer'
    TEXT_LANGUAGE_CODE_ENGLISH = 'en'
    AUDIO_LANGUAGE_CODE_ENGLISH = 'en'
    ANDROID_REPORT_INFO = {
        'user_feedback_other_text_input': 'add an admin',
        'event_logs': ['event1', 'event2'],
        'logcat_logs': ['logcat1', 'logcat2'],
        'package_version_code': 1,
        'language_locale_code': 'en',
        'entry_point_info': {
            'entry_point_name': 'crash',
        },
        'text_size': 'MEDIUM_TEXT_SIZE',
        'download_and_update_only_on_wifi': True,
        'automatically_update_topics': False,
        'is_admin': False
    }
    ANDROID_REPORT_INFO_SCHEMA_VERSION = 1
    SUGGESTION_LANGUAGE_CODE = 'en'
    SUBMITTED_TRANSLATIONS_COUNT = 2
    SUBMITTED_TRANSLATION_WORD_COUNT = 100
    ACCEPTED_TRANSLATIONS_COUNT = 1
    ACCEPTED_TRANSLATIONS_WITHOUT_REVIEWER_EDITS_COUNT = 0
    ACCEPTED_TRANSLATION_WORD_COUNT = 50
    REJECTED_TRANSLATIONS_COUNT = 0
    REJECTED_TRANSLATION_WORD_COUNT = 0
    # Timestamp dates in sec since epoch for Mar 19 2021 UTC.
    CONTRIBUTION_DATES = [
        datetime.date.fromtimestamp(1616173836),
        datetime.date.fromtimestamp(1616173837)
    ]

    def set_up_non_trivial(self):
        """Set up all models for use in testing.
        1) Simulates the creation of a user, user_1, and their stats model.
        2) Simulates skill mastery of user_1 with two skills.
        3) Simulates subscriptions to threads, activities, and collections.
        4) Simulates creation and edit of an exploration by user_1.
        5) Creates an ExplorationUserDataModel.
        6) Simulates completion of some activities.
        7) Simulates incomplete status of some activities.
        8) Creates user LearnerGoals.
        9) Populates ExpUserLastPlaythroughModel of user.
        10) Creates user LearnerPlaylsts.
        11) Simulates collection progress of user.
        12) Simulates story progress of user.
        13) Creates new collection rights.
        14) Simulates a general suggestion.
        15) Creates new exploration rights.
        16) Populates user settings.
        17) Creates two reply-to ids for feedback.
        18) Creates a task closed by the user.
        19) Simulates user_1 scrubbing a report.
        20) Creates new BlogPostModel and BlogPostRightsModel.
        21) Creates a TranslationContributionStatsModel.
        """
        # Setup for UserStatsModel.
        user_models.UserStatsModel(
            id=self.USER_ID_1,
            impact_score=self.USER_1_IMPACT_SCORE,
            total_plays=self.USER_1_TOTAL_PLAYS,
            average_ratings=self.USER_1_AVERAGE_RATINGS,
            num_ratings=self.USER_1_NUM_RATINGS,
            weekly_creator_stats_list=self.USER_1_WEEKLY_CREATOR_STATS_LIST
        ).put()

        # Setup for UserSkillModel.
        user_models.UserSkillMasteryModel(
            id=user_models.UserSkillMasteryModel.construct_model_id(
                self.USER_ID_1, self.SKILL_ID_1),
            user_id=self.USER_ID_1,
            skill_id=self.SKILL_ID_1,
            degree_of_mastery=self.DEGREE_OF_MASTERY).put()
        user_models.UserSkillMasteryModel(
            id=user_models.UserSkillMasteryModel.construct_model_id(
                self.USER_ID_1, self.SKILL_ID_2),
            user_id=self.USER_ID_1,
            skill_id=self.SKILL_ID_2,
            degree_of_mastery=self.DEGREE_OF_MASTERY).put()
        user_models.UserSkillMasteryModel(
            id=user_models.UserSkillMasteryModel.construct_model_id(
                self.PROFILE_ID_1, self.SKILL_ID_3),
            user_id=self.PROFILE_ID_1,
            skill_id=self.SKILL_ID_3,
            degree_of_mastery=self.DEGREE_OF_MASTERY_2).put()

        # Setup for UserSubscriptionsModel.
        for creator_id in self.CREATOR_IDS:
            user_models.UserSettingsModel(
                id=creator_id,
                username='username' + creator_id,
                email=creator_id + '@example.com'
            ).put()

        user_models.UserSubscriptionsModel(
            id=self.USER_ID_1, creator_ids=self.CREATOR_IDS,
            collection_ids=self.COLLECTION_IDS,
            exploration_ids=self.EXPLORATION_IDS,
            general_feedback_thread_ids=self.GENERAL_FEEDBACK_THREAD_IDS,
            last_checked=self.GENERIC_DATE).put()

        # Setup for UserContributionsModel.
        self.save_new_valid_exploration(
            self.EXPLORATION_IDS[0], self.USER_ID_1, end_state_name='End')

        exp_services.update_exploration(
            self.USER_ID_1, self.EXPLORATION_IDS[0],
            [exp_domain.ExplorationChange({
                'cmd': 'edit_exploration_property',
                'property_name': 'objective',
                'new_value': 'the objective'
            })], 'Test edit')

        # Setup for ExplorationUserDataModel.
        user_models.ExplorationUserDataModel(
            id='%s.%s' % (self.USER_ID_1, self.EXPLORATION_IDS[0]),
            user_id=self.USER_ID_1,
            exploration_id=self.EXPLORATION_IDS[0], rating=2,
            rated_on=self.GENERIC_DATE,
            draft_change_list={'new_content': {}},
            draft_change_list_last_updated=self.GENERIC_DATE,
            draft_change_list_exp_version=3,
            draft_change_list_id=1).put()

        # Setup for CompletedActivitiesModel.
        user_models.CompletedActivitiesModel(
            id=self.USER_ID_1,
            exploration_ids=self.EXPLORATION_IDS,
            collection_ids=self.COLLECTION_IDS,
            story_ids=self.STORY_IDS,
            learnt_topic_ids=self.TOPIC_IDS).put()
        user_models.CompletedActivitiesModel(
            id=self.PROFILE_ID_1,
            exploration_ids=self.EXPLORATION_IDS_2,
            collection_ids=self.COLLECTION_IDS_2,
            story_ids=self.STORY_IDS_2,
            learnt_topic_ids=self.TOPIC_IDS_2).put()

        # Setup for IncompleteACtivitiesModel.
        user_models.IncompleteActivitiesModel(
            id=self.USER_ID_1,
            exploration_ids=self.EXPLORATION_IDS,
            collection_ids=self.COLLECTION_IDS,
            story_ids=self.STORY_IDS,
            partially_learnt_topic_ids=self.TOPIC_IDS).put()

        # Setup for ExpUserLastPlaythroughModel.
        user_models.ExpUserLastPlaythroughModel(
            id='%s.%s' % (self.USER_ID_1, self.EXPLORATION_IDS[0]),
            user_id=self.USER_ID_1, exploration_id=self.EXPLORATION_IDS[0],
            last_played_exp_version=self.EXP_VERSION,
            last_played_state_name=self.STATE_NAME).put()

        # Setup for LearnerPlaylistModel.
        user_models.LearnerPlaylistModel(
            id=self.USER_ID_1,
            exploration_ids=self.EXPLORATION_IDS,
            collection_ids=self.COLLECTION_IDS).put()
        user_models.LearnerPlaylistModel(
            id=self.PROFILE_ID_1,
            exploration_ids=self.EXPLORATION_IDS_2,
            collection_ids=self.COLLECTION_IDS_2).put()

        # Setup for CollectionProgressModel.
        user_models.CollectionProgressModel(
            id='%s.%s' % (self.USER_ID_1, self.COLLECTION_IDS[0]),
            user_id=self.USER_ID_1,
            collection_id=self.COLLECTION_IDS[0],
            completed_explorations=self.EXPLORATION_IDS).put()
        user_models.CollectionProgressModel(
            id='%s.%s' % (self.PROFILE_ID_1, self.COLLECTION_IDS_2[0]),
            user_id=self.PROFILE_ID_1,
            collection_id=self.COLLECTION_IDS_2[0],
            completed_explorations=self.EXPLORATION_IDS_2).put()

        # Setup for StoryProgressModel.
        user_models.StoryProgressModel(
            id='%s.%s' % (self.USER_ID_1, self.STORY_ID_1),
            user_id=self.USER_ID_1,
            story_id=self.STORY_ID_1,
            completed_node_ids=self.COMPLETED_NODE_IDS_1).put()
        user_models.StoryProgressModel(
            id='%s.%s' % (self.PROFILE_ID_1, self.STORY_ID_2),
            user_id=self.PROFILE_ID_1,
            story_id=self.STORY_ID_2,
            completed_node_ids=self.COMPLETED_NODE_IDS_2).put()

        # Setup for CollectionRightsModel.
        collection_models.CollectionRightsModel(
            id=self.COLLECTION_IDS[0],
            owner_ids=[self.USER_ID_1],
            editor_ids=[self.USER_ID_1],
            voice_artist_ids=[self.USER_ID_1],
            viewer_ids=[self.USER_ID_1],
            community_owned=False,
            status=constants.ACTIVITY_STATUS_PUBLIC,
            viewable_if_private=False,
            first_published_msec=0.0
        ).save(
            'cid', 'Created new collection right',
            [{'cmd': rights_domain.CMD_CREATE_NEW}])

        # Setup for GeneralSuggestionModel.
        suggestion_models.GeneralSuggestionModel.create(
            feconf.SUGGESTION_TYPE_EDIT_STATE_CONTENT,
            feconf.ENTITY_TYPE_EXPLORATION,
            self.EXPLORATION_IDS[0], 1,
            suggestion_models.STATUS_IN_REVIEW, self.USER_ID_1,
            'reviewer_1', self.CHANGE_CMD, self.SCORE_CATEGORY,
            'exploration.exp1.thread_1', None)

        # Setup for TopicRightsModel.
        topic_models.TopicRightsModel(
            id=self.TOPIC_ID_1,
            manager_ids=[self.USER_ID_1],
            topic_is_published=True
        ).commit(
            'committer_id',
            'New topic rights',
            [{'cmd': topic_domain.CMD_CREATE_NEW}])
        topic_models.TopicRightsModel(
            id=self.TOPIC_ID_2,
            manager_ids=[self.USER_ID_1],
            topic_is_published=True
        ).commit(
            'committer_id',
            'New topic rights',
            [{'cmd': topic_domain.CMD_CREATE_NEW}])

        # Setup for ExplorationRightsModel.
        exploration_models.ExplorationRightsModel(
            id=self.EXPLORATION_IDS[0],
            owner_ids=[self.USER_ID_1],
            editor_ids=[self.USER_ID_1],
            voice_artist_ids=[self.USER_ID_1],
            viewer_ids=[self.USER_ID_1],
            community_owned=False,
            status=constants.ACTIVITY_STATUS_PUBLIC,
            viewable_if_private=False,
            first_published_msec=0.0
        ).save(
            'cid', 'Created new exploration right',
            [{'cmd': rights_domain.CMD_CREATE_NEW}])

        # Setup for UserSettingsModel.
        user_models.UserSettingsModel(
            id=self.USER_ID_1,
            email=self.USER_1_EMAIL,
            role=self.USER_1_ROLE,
            username=self.GENERIC_USERNAME,
            normalized_username=self.GENERIC_USERNAME,
            last_agreed_to_terms=self.GENERIC_DATE,
            last_started_state_editor_tutorial=self.GENERIC_DATE,
            last_started_state_translation_tutorial=self.GENERIC_DATE,
            last_logged_in=self.GENERIC_DATE,
            last_created_an_exploration=self.GENERIC_DATE,
            last_edited_an_exploration=self.GENERIC_DATE,
            profile_picture_data_url=self.GENERIC_IMAGE_URL,
            default_dashboard='learner', creator_dashboard_display_pref='card',
            user_bio=self.GENERIC_USER_BIO,
            subject_interests=self.GENERIC_SUBJECT_INTERESTS,
            first_contribution_msec=1,
            preferred_language_codes=self.GENERIC_LANGUAGE_CODES,
            preferred_site_language_code=self.GENERIC_LANGUAGE_CODES[0],
            preferred_audio_language_code=self.GENERIC_LANGUAGE_CODES[0],
            display_alias=self.GENERIC_DISPLAY_ALIAS,
            pin=self.GENERIC_PIN
        ).put()
        user_models.UserSettingsModel(
            id=self.PROFILE_ID_1,
            email=self.USER_1_EMAIL,
            role=self.PROFILE_1_ROLE,
            username=None,
            normalized_username=None,
            last_agreed_to_terms=self.GENERIC_DATE,
            last_started_state_editor_tutorial=None,
            last_started_state_translation_tutorial=None,
            last_logged_in=self.GENERIC_DATE,
            last_created_an_exploration=None,
            last_edited_an_exploration=None,
            profile_picture_data_url=None,
            default_dashboard='learner', creator_dashboard_display_pref='card',
            user_bio=self.GENERIC_USER_BIO,
            subject_interests=self.GENERIC_SUBJECT_INTERESTS,
            first_contribution_msec=None,
            preferred_language_codes=self.GENERIC_LANGUAGE_CODES,
            preferred_site_language_code=self.GENERIC_LANGUAGE_CODES[0],
            preferred_audio_language_code=self.GENERIC_LANGUAGE_CODES[0],
            display_alias=self.GENERIC_DISPLAY_ALIAS_2
        ).put()

        suggestion_models.GeneralVoiceoverApplicationModel(
            id='application_1_id',
            target_type='exploration',
            target_id='exp_id',
            status=suggestion_models.STATUS_IN_REVIEW,
            author_id=self.USER_ID_1,
            final_reviewer_id='reviewer_id',
            language_code=self.SUGGESTION_LANGUAGE_CODE,
            filename='application_audio.mp3',
            content='<p>Some content</p>',
            rejection_message=None).put()

        suggestion_models.GeneralVoiceoverApplicationModel(
            id='application_2_id',
            target_type='exploration',
            target_id='exp_id',
            status=suggestion_models.STATUS_IN_REVIEW,
            author_id=self.USER_ID_1,
            final_reviewer_id=None,
            language_code=self.SUGGESTION_LANGUAGE_CODE,
            filename='application_audio.mp3',
            content='<p>Some content</p>',
            rejection_message=None).put()

        suggestion_models.TranslationContributionStatsModel.create(
            language_code=self.SUGGESTION_LANGUAGE_CODE,
            contributor_user_id=self.USER_ID_1,
            topic_id=self.TOPIC_ID_1,
            submitted_translations_count=self.SUBMITTED_TRANSLATIONS_COUNT,
            submitted_translation_word_count=(
                self.SUBMITTED_TRANSLATION_WORD_COUNT),
            accepted_translations_count=self.ACCEPTED_TRANSLATIONS_COUNT,
            accepted_translations_without_reviewer_edits_count=(
                self.ACCEPTED_TRANSLATIONS_WITHOUT_REVIEWER_EDITS_COUNT),
            accepted_translation_word_count=(
                self.ACCEPTED_TRANSLATION_WORD_COUNT),
            rejected_translations_count=self.REJECTED_TRANSLATIONS_COUNT,
            rejected_translation_word_count=(
                self.REJECTED_TRANSLATION_WORD_COUNT),
            contribution_dates=self.CONTRIBUTION_DATES
        )

        user_models.UserContributionRightsModel(
            id=self.USER_ID_1,
            can_review_translation_for_language_codes=['hi', 'en'],
            can_review_voiceover_for_language_codes=['hi'],
            can_review_questions=True).put()

        user_models.UserContributionProficiencyModel(
            id='%s.%s' % (self.SCORE_CATEGORY_1, self.USER_ID_1),
            user_id=self.USER_ID_1,
            score_category=self.SCORE_CATEGORY_1,
            score=1.5,
            onboarding_email_sent=False
        ).put()
        user_models.UserContributionProficiencyModel(
            id='%s.%s' % (self.SCORE_CATEGORY_2, self.USER_ID_1),
            user_id=self.USER_ID_1,
            score_category=self.SCORE_CATEGORY_2,
            score=2,
            onboarding_email_sent=False
        ).put()

        collection_models.CollectionRightsSnapshotMetadataModel(
            id=self.GENERIC_MODEL_ID, committer_id=self.USER_ID_1,
            commit_type=self.COMMIT_TYPE, commit_message=self.COMMIT_MESSAGE,
            commit_cmds=self.COMMIT_CMDS
        ).put()

        collection_models.CollectionSnapshotMetadataModel(
            id=self.GENERIC_MODEL_ID, committer_id=self.USER_ID_1,
            commit_type=self.COMMIT_TYPE, commit_message=self.COMMIT_MESSAGE,
            commit_cmds=self.COMMIT_CMDS
        ).put()

        skill_models.SkillSnapshotMetadataModel(
            id=self.GENERIC_MODEL_ID, committer_id=self.USER_ID_1,
            commit_type=self.COMMIT_TYPE, commit_message=self.COMMIT_MESSAGE,
            commit_cmds=self.COMMIT_CMDS
        ).put()
        subtopic_models.SubtopicPageSnapshotMetadataModel(
            id=self.GENERIC_MODEL_ID, committer_id=self.USER_ID_1,
            commit_type=self.COMMIT_TYPE, commit_message=self.COMMIT_MESSAGE,
            commit_cmds=self.COMMIT_CMDS
        ).put()

        topic_models.TopicRightsSnapshotMetadataModel(
            id=self.GENERIC_MODEL_ID, committer_id=self.USER_ID_1,
            commit_type=self.COMMIT_TYPE, commit_message=self.COMMIT_MESSAGE,
            commit_cmds=self.COMMIT_CMDS
        ).put()

        topic_models.TopicSnapshotMetadataModel(
            id=self.GENERIC_MODEL_ID, committer_id=self.USER_ID_1,
            commit_type=self.COMMIT_TYPE, commit_message=self.COMMIT_MESSAGE,
            commit_cmds=self.COMMIT_CMDS
        ).put()

        story_models.StorySnapshotMetadataModel(
            id=self.GENERIC_MODEL_ID, committer_id=self.USER_ID_1,
            commit_type=self.COMMIT_TYPE, commit_message=self.COMMIT_MESSAGE,
            commit_cmds=self.COMMIT_CMDS
        ).put()

        question_models.QuestionSnapshotMetadataModel(
            id=self.GENERIC_MODEL_ID, committer_id=self.USER_ID_1,
            commit_type=self.COMMIT_TYPE, commit_message=self.COMMIT_MESSAGE,
            commit_cmds=self.COMMIT_CMDS
        ).put()

        config_models.ConfigPropertySnapshotMetadataModel(
            id=self.GENERIC_MODEL_ID, committer_id=self.USER_ID_1,
            commit_type=self.COMMIT_TYPE, commit_message=self.COMMIT_MESSAGE,
            commit_cmds=self.COMMIT_CMDS
        ).put()

        exploration_models.ExplorationRightsSnapshotMetadataModel(
            id=self.GENERIC_MODEL_ID, committer_id=self.USER_ID_1,
            commit_type=self.COMMIT_TYPE, commit_message=self.COMMIT_MESSAGE,
            commit_cmds=self.COMMIT_CMDS
        ).put()

        improvements_models.TaskEntryModel(
            id=self.GENERIC_MODEL_ID,
            composite_entity_id=self.GENERIC_MODEL_ID,
            entity_type=improvements_models.TASK_ENTITY_TYPE_EXPLORATION,
            entity_id=self.GENERIC_MODEL_ID,
            entity_version=1,
            task_type=improvements_models.TASK_TYPE_HIGH_BOUNCE_RATE,
            target_type=improvements_models.TASK_TARGET_TYPE_STATE,
            target_id=self.GENERIC_MODEL_ID,
            status=improvements_models.TASK_STATUS_OPEN,
            resolver_id=self.USER_ID_1
        ).put()

        config_models.PlatformParameterSnapshotMetadataModel(
            id=self.GENERIC_MODEL_ID, committer_id=self.USER_ID_1,
            commit_type=self.COMMIT_TYPE, commit_message=self.COMMIT_MESSAGE,
            commit_cmds=self.COMMIT_CMDS
        ).put()

        user_models.UserEmailPreferencesModel(
            id=self.USER_ID_1,
            site_updates=False,
            editor_role_notifications=False,
            feedback_message_notifications=False,
            subscription_notifications=False
        ).put()
        auth_models.UserAuthDetailsModel(
            id=self.USER_ID_1,
            parent_user_id=self.PROFILE_ID_1
        ).put()

        # Set-up for AppFeedbackReportModel scrubbed by user.
        report_id = '%s.%s.%s' % (
            self.PLATFORM_ANDROID, self.REPORT_SUBMITTED_TIMESTAMP.second,
            'randomInteger123')
        app_feedback_report_models.AppFeedbackReportModel(
            id=report_id,
            platform=self.PLATFORM_ANDROID,
            scrubbed_by=None,
            ticket_id='%s.%s.%s' % (
                'random_hash', self.TICKET_CREATION_TIMESTAMP.second,
                '16CharString1234'),
            submitted_on=self.REPORT_SUBMITTED_TIMESTAMP,
            report_type=self.REPORT_TYPE_SUGGESTION,
            category=self.CATEGORY_OTHER,
            platform_version=self.PLATFORM_VERSION,
            android_device_country_locale_code=(
                self.DEVICE_COUNTRY_LOCALE_CODE_INDIA),
            android_device_model=self.ANDROID_DEVICE_MODEL,
            android_sdk_version=self.ANDROID_SDK_VERSION,
            entry_point=self.ENTRY_POINT_NAVIGATION_DRAWER,
            text_language_code=self.TEXT_LANGUAGE_CODE_ENGLISH,
            audio_language_code=self.AUDIO_LANGUAGE_CODE_ENGLISH,
            android_report_info=self.ANDROID_REPORT_INFO,
            android_report_info_schema_version=(
                self.ANDROID_REPORT_INFO_SCHEMA_VERSION)
        ).put()
        report_entity = (
            app_feedback_report_models.AppFeedbackReportModel.get_by_id(
                report_id))
        report_entity.scrubbed_by = self.USER_ID_1
        report_entity.update_timestamps()
        report_entity.put()

        # Set-up for the BlogPostModel.
        blog_post_model = blog_models.BlogPostModel(
            id=self.BLOG_POST_ID_1,
            author_id=self.USER_ID_1,
            content='content sample',
            title='sample title',
            published_on=datetime.datetime.utcnow(),
            url_fragment='sample-url-fragment',
            tags=['tag', 'one'],
            thumbnail_filename='thumbnail'
        )
        blog_post_model.update_timestamps()
        blog_post_model.put()

        blog_post_rights_for_post_1 = blog_models.BlogPostRightsModel(
            id=self.BLOG_POST_ID_1,
            editor_ids=[self.USER_ID_1],
            blog_post_is_published=True,
        )

        blog_post_rights_for_post_1.update_timestamps()
        blog_post_rights_for_post_1.put()

        blog_post_rights_for_post_2 = blog_models.BlogPostRightsModel(
            id=self.BLOG_POST_ID_2,
            editor_ids=[self.USER_ID_1],
            blog_post_is_published=False,
        )

        blog_post_rights_for_post_2.update_timestamps()
        blog_post_rights_for_post_2.put()

    def set_up_trivial(self):
        """Setup for trivial test of export_data functionality."""
        user_models.UserSettingsModel(
            id=self.USER_ID_1,
            email=self.USER_1_EMAIL,
            role=self.USER_1_ROLE
        ).put()
        user_models.UserSettingsModel(
            id=self.PROFILE_ID_1,
            email=self.USER_1_EMAIL,
            role=self.PROFILE_1_ROLE
        ).put()
        user_models.UserSubscriptionsModel(id=self.USER_ID_1).put()

    def test_export_nonexistent_full_user_raises_error(self):
        """Setup for nonexistent user test of export_data functionality."""
        with self.assertRaisesRegexp(
            user_models.UserSettingsModel.EntityNotFoundError,
            'Entity for class UserSettingsModel with id fake_user_id '
            'not found'):
            takeout_service.export_data_for_user('fake_user_id')

    def test_export_data_for_full_user_trivial_is_correct(self):
        """Trivial test of export_data functionality."""
        self.set_up_trivial()
        self.maxDiff = None
        # Generate expected output.
        app_feedback_report = {}
        collection_progress_data = {}
        collection_rights_data = {
            'editable_collection_ids': [],
            'owned_collection_ids': [],
            'viewable_collection_ids': [],
            'voiced_collection_ids': []
        }
        completed_activities_data = {}
        contribution_data = {}
        exploration_rights_data = {
            'editable_exploration_ids': [],
            'owned_exploration_ids': [],
            'viewable_exploration_ids': [],
            'voiced_exploration_ids': []
        }
        exploration_data = {}
        general_feedback_message_data = {}
        general_feedback_thread_data = {}
        general_feedback_thread_user_data = {}
        general_suggestion_data = {}
        last_playthrough_data = {}
        learner_playlist_data = {}
        incomplete_activities_data = {}
        user_settings_data = {
            'email': 'user1@example.com',
            'role': feconf.ROLE_ID_ADMIN,
            'username': None,
            'normalized_username': None,
            'last_agreed_to_terms_msec': None,
            'last_started_state_editor_tutorial_msec': None,
            'last_started_state_translation_tutorial_msec': None,
            'last_logged_in_msec': None,
            'last_edited_an_exploration_msec': None,
            'last_created_an_exploration_msec': None,
            'profile_picture_filename': None,
            'default_dashboard': 'learner',
            'creator_dashboard_display_pref': 'card',
            'user_bio': None,
            'subject_interests': [],
            'first_contribution_msec': None,
            'preferred_language_codes': [],
            'preferred_site_language_code': None,
            'preferred_audio_language_code': None,
            'display_alias': None,
        }
        skill_data = {}
        stats_data = {}
        story_progress_data = {}
        subscriptions_data = {
            'exploration_ids': [],
            'collection_ids': [],
            'creator_usernames': [],
            'general_feedback_thread_ids': [],
            'last_checked_msec': None
        }
        task_entry_data = {
            'task_ids_resolved_by_user': [],
            'issue_descriptions': [],
            'resolution_msecs': [],
            'statuses': []
        }
        topic_rights_data = {
            'managed_topic_ids': []
        }

        expected_voiceover_application_data = {}
        expected_contrib_proficiency_data = {}
        expected_contribution_rights_data = {}
        expected_collection_rights_sm = {}
        expected_collection_sm = {}
        expected_skill_sm = {}
        expected_subtopic_page_sm = {}
        expected_topic_rights_sm = {}
        expected_topic_sm = {}
        expected_translation_contribution_stats = {}
        expected_story_sm = {}
        expected_question_sm = {}
        expected_config_property_sm = {}
        expected_exploration_rights_sm = {}
        expected_exploration_sm = {}
        expected_platform_parameter_sm = {}
        expected_user_auth_details = {}
        expected_user_email_preferences = {}
        expected_blog_post_data = {}
        expected_blog_post_rights = {
            'editable_blog_post_ids': []
        }

        expected_user_data = {
            'app_feedback_report': app_feedback_report,
            'blog_post': expected_blog_post_data,
            'blog_post_rights': expected_blog_post_rights,
            'user_stats': stats_data,
            'user_settings': user_settings_data,
            'user_subscriptions': subscriptions_data,
            'user_skill_mastery': skill_data,
            'user_contributions': contribution_data,
            'exploration_user_data': exploration_data,
            'completed_activities': completed_activities_data,
            'incomplete_activities': incomplete_activities_data,
            'exp_user_last_playthrough': last_playthrough_data,
            'learner_playlist': learner_playlist_data,
            'task_entry': task_entry_data,
            'topic_rights': topic_rights_data,
            'collection_progress': collection_progress_data,
            'story_progress': story_progress_data,
            'general_feedback_thread': general_feedback_thread_data,
            'general_feedback_thread_user':
                general_feedback_thread_user_data,
            'general_feedback_message': general_feedback_message_data,
            'collection_rights': collection_rights_data,
            'general_suggestion': general_suggestion_data,
            'exploration_rights': exploration_rights_data,
            'general_voiceover_application':
                expected_voiceover_application_data,
            'user_contribution_proficiency': expected_contrib_proficiency_data,
            'user_contribution_rights': expected_contribution_rights_data,
            'collection_rights_snapshot_metadata':
                expected_collection_rights_sm,
            'collection_snapshot_metadata':
                expected_collection_sm,
            'skill_snapshot_metadata':
                expected_skill_sm,
            'subtopic_page_snapshot_metadata':
                expected_subtopic_page_sm,
            'topic_rights_snapshot_metadata':
                expected_topic_rights_sm,
            'topic_snapshot_metadata': expected_topic_sm,
            'translation_contribution_stats':
                expected_translation_contribution_stats,
            'story_snapshot_metadata': expected_story_sm,
            'question_snapshot_metadata': expected_question_sm,
            'config_property_snapshot_metadata':
                expected_config_property_sm,
            'exploration_rights_snapshot_metadata':
                expected_exploration_rights_sm,
            'exploration_snapshot_metadata': expected_exploration_sm,
            'platform_parameter_snapshot_metadata':
                expected_platform_parameter_sm,
            'user_auth_details': expected_user_auth_details,
            'user_email_preferences': expected_user_email_preferences
        }

        # Perform export and compare.
        user_takeout_object = takeout_service.export_data_for_user(
            self.USER_ID_1)
        observed_data = user_takeout_object.user_data
        observed_images = user_takeout_object.user_images
        self.assertEqual(expected_user_data, observed_data)
        observed_json = json.dumps(observed_data)
        expected_json = json.dumps(expected_user_data)
        self.assertEqual(json.loads(expected_json), json.loads(observed_json))
        expected_images = []
        self.assertEqual(expected_images, observed_images)

    def test_exports_have_single_takeout_dict_key(self):
        """Test to ensure that all export policies that specify a key for the
        Takeout dict are also models that specify this policy are type
        MULTIPLE_INSTANCES_PER_USER.
        """
        self.set_up_non_trivial()

        # We set up the feedback_thread_model here so that we can easily
        # access it when computing the expected data later.
        feedback_thread_model = feedback_models.GeneralFeedbackThreadModel(
            entity_type=self.THREAD_ENTITY_TYPE,
            entity_id=self.THREAD_ENTITY_ID,
            original_author_id=self.USER_ID_1,
            status=self.THREAD_STATUS,
            subject=self.THREAD_SUBJECT,
            has_suggestion=self.THREAD_HAS_SUGGESTION,
            summary=self.THREAD_SUMMARY,
            message_count=self.THREAD_MESSAGE_COUNT
        )
        feedback_thread_model.put()

        thread_id = feedback_services.create_thread(
            self.THREAD_ENTITY_TYPE,
            self.THREAD_ENTITY_ID,
            self.USER_ID_1,
            self.THREAD_SUBJECT,
            self.MESSAGE_TEXT
        )
        feedback_services.create_message(
            thread_id,
            self.USER_ID_1,
            self.THREAD_STATUS,
            self.THREAD_SUBJECT,
            self.MESSAGE_TEXT
        )

        # Retrieve all models for export.
        all_models = [
            clazz
            for clazz in test_utils.get_storage_model_classes()
            if (not clazz.__name__ in
                test_utils.BASE_MODEL_CLASSES_WITHOUT_DATA_POLICIES)
        ]

        for model in all_models:
            export_method = model.get_model_association_to_user()
            export_policy = model.get_export_policy()
            num_takeout_keys = 0
            for field_export_policy in export_policy.values():
                if (field_export_policy ==
                        base_models
                        .EXPORT_POLICY
                        .EXPORTED_AS_KEY_FOR_TAKEOUT_DICT):
                    num_takeout_keys += 1

            if (export_method ==
                    base_models.MODEL_ASSOCIATION_TO_USER
                    .MULTIPLE_INSTANCES_PER_USER):
                # If the id is used as a Takeout key, then we should not
                # have any fields exported as the key for the Takeout.
                self.assertEqual(
                    num_takeout_keys,
                    0 if model.ID_IS_USED_AS_TAKEOUT_KEY else 1)
            else:
                self.assertEqual(num_takeout_keys, 0)

    def test_exports_follow_export_policies(self):
        """Test to ensure that all fields that should be exported
        per the export policy are exported, and exported in the proper format.
        """
        self.set_up_non_trivial()

        # We set up the feedback_thread_model here so that we can easily
        # access it when computing the expected data later.
        feedback_thread_model = feedback_models.GeneralFeedbackThreadModel(
            entity_type=self.THREAD_ENTITY_TYPE,
            entity_id=self.THREAD_ENTITY_ID,
            original_author_id=self.USER_ID_1,
            status=self.THREAD_STATUS,
            subject=self.THREAD_SUBJECT,
            has_suggestion=self.THREAD_HAS_SUGGESTION,
            summary=self.THREAD_SUMMARY,
            message_count=self.THREAD_MESSAGE_COUNT
        )
        feedback_thread_model.put()

        thread_id = feedback_services.create_thread(
            self.THREAD_ENTITY_TYPE,
            self.THREAD_ENTITY_ID,
            self.USER_ID_1,
            self.THREAD_SUBJECT,
            self.MESSAGE_TEXT
        )
        feedback_services.create_message(
            thread_id,
            self.USER_ID_1,
            self.THREAD_STATUS,
            self.THREAD_SUBJECT,
            self.MESSAGE_TEXT
        )

        # Retrieve all models for export.
        all_models = [
            clazz
            for clazz in test_utils.get_storage_model_classes()
            if (not clazz.__name__ in
                test_utils.BASE_MODEL_CLASSES_WITHOUT_DATA_POLICIES)
        ]

        # Iterate over models and test export policies.
        for model in all_models:
            export_method = model.get_model_association_to_user()
            export_policy = model.get_export_policy()
            renamed_export_keys = model.get_field_names_for_takeout()
            exported_field_names = []
            field_used_as_key_for_takeout_dict = None
            for field_name in model._properties: # pylint: disable=protected-access
                if (export_policy[field_name] ==
                        base_models.EXPORT_POLICY.EXPORTED):
                    if field_name in renamed_export_keys:
                        exported_field_names.append(
                            renamed_export_keys[field_name]
                        )
                    else:
                        exported_field_names.append(field_name)
                elif (export_policy[field_name] ==
                      base_models
                      .EXPORT_POLICY.EXPORTED_AS_KEY_FOR_TAKEOUT_DICT):
                    field_used_as_key_for_takeout_dict = field_name

            if (export_method ==
                    base_models
                    .MODEL_ASSOCIATION_TO_USER.NOT_CORRESPONDING_TO_USER):
                self.assertEqual(len(exported_field_names), 0)
            elif (export_method ==
                  base_models.MODEL_ASSOCIATION_TO_USER.ONE_INSTANCE_PER_USER):
                exported_data = model.export_data(self.USER_ID_1)
                self.assertEqual(
                    sorted([
                        python_utils.UNICODE(key)
                        for key in exported_data.keys()]),
                    sorted(exported_field_names)
                )
            elif (export_method ==
                  base_models
                  .MODEL_ASSOCIATION_TO_USER
                  .ONE_INSTANCE_SHARED_ACROSS_USERS):
                self.assertIsNotNone(
                    model.get_field_name_mapping_to_takeout_keys)
                exported_data = model.export_data(self.USER_ID_1)
                field_mapping = model.get_field_name_mapping_to_takeout_keys()
                self.assertEqual(
                    sorted(exported_field_names),
                    sorted(field_mapping.keys())
                )
                self.assertEqual(
                    sorted(exported_data.keys()),
                    sorted(field_mapping.values())
                )
            elif (export_method ==
                  base_models
                  .MODEL_ASSOCIATION_TO_USER.MULTIPLE_INSTANCES_PER_USER):
                exported_data = model.export_data(self.USER_ID_1)
                for model_id in exported_data.keys():
                    # If we are using a field as a Takeout key.
                    if field_used_as_key_for_takeout_dict:
                        # Ensure that we export the field.
                        self.assertEqual(
                            model_id,
                            getattr(
                                model,
                                field_used_as_key_for_takeout_dict)
                        )
                    self.assertEqual(
                        sorted([
                            python_utils.UNICODE(key)
                            for key in exported_data[model_id].keys()]),
                        sorted(exported_field_names)
                    )

    def test_export_data_for_full_user_nontrivial_is_correct(self):
        """Nontrivial test of export_data functionality."""
        self.set_up_non_trivial()
        # We set up the feedback_thread_model here so that we can easily
        # access it when computing the expected data later.
        feedback_thread_model = feedback_models.GeneralFeedbackThreadModel(
            entity_type=self.THREAD_ENTITY_TYPE,
            entity_id=self.THREAD_ENTITY_ID,
            original_author_id=self.USER_ID_1,
            status=self.THREAD_STATUS,
            subject=self.THREAD_SUBJECT,
            has_suggestion=self.THREAD_HAS_SUGGESTION,
            summary=self.THREAD_SUMMARY,
            message_count=self.THREAD_MESSAGE_COUNT
        )
        feedback_thread_model.update_timestamps()
        feedback_thread_model.put()

        blog_post_model = blog_models.BlogPostModel(
            id=self.BLOG_POST_ID_1,
            author_id=self.USER_ID_1,
            content='content sample',
            title='sample title',
            published_on=datetime.datetime.utcnow(),
            url_fragment='sample-url-fragment',
            tags=['tag', 'one'],
            thumbnail_filename='thumbnail'
        )
        blog_post_model.update_timestamps()
        blog_post_model.put()

        expected_stats_data = {
            'impact_score': self.USER_1_IMPACT_SCORE,
            'total_plays': self.USER_1_TOTAL_PLAYS,
            'average_ratings': self.USER_1_AVERAGE_RATINGS,
            'num_ratings': self.USER_1_NUM_RATINGS,
            'weekly_creator_stats_list': self.USER_1_WEEKLY_CREATOR_STATS_LIST
        }
        expected_user_skill_data = {
            self.SKILL_ID_1: self.DEGREE_OF_MASTERY,
            self.SKILL_ID_2: self.DEGREE_OF_MASTERY
        }
        expected_contribution_data = {
            'created_exploration_ids': [self.EXPLORATION_IDS[0]],
            'edited_exploration_ids': [self.EXPLORATION_IDS[0]]
        }
        expected_exploration_data = {
            self.EXPLORATION_IDS[0]: {
                'rating': 2,
                'rated_on_msec': self.GENERIC_EPOCH,
                'draft_change_list': {'new_content': {}},
                'draft_change_list_last_updated_msec': self.GENERIC_EPOCH,
                'draft_change_list_exp_version': 3,
                'draft_change_list_id': 1,
                'mute_suggestion_notifications': (
                    feconf.DEFAULT_SUGGESTION_NOTIFICATIONS_MUTED_PREFERENCE),
                'mute_feedback_notifications': (
                    feconf.DEFAULT_SUGGESTION_NOTIFICATIONS_MUTED_PREFERENCE)
            }
        }
        expected_completed_activities_data = {
            'completed_exploration_ids': self.EXPLORATION_IDS,
            'completed_collection_ids': self.COLLECTION_IDS,
            'completed_story_ids': self.STORY_IDS,
            'learnt_topic_ids': self.TOPIC_IDS
        }
        expected_incomplete_activities_data = {
            'incomplete_exploration_ids': self.EXPLORATION_IDS,
            'incomplete_collection_ids': self.COLLECTION_IDS,
            'incomplete_story_ids': self.STORY_IDS,
            'partially_learnt_topic_ids': self.TOPIC_IDS
        }
        expected_last_playthrough_data = {
            self.EXPLORATION_IDS[0]: {
                'exp_version': self.EXP_VERSION,
                'state_name': self.STATE_NAME
            }
        }
        expected_learner_playlist_data = {
            'playlist_exploration_ids': self.EXPLORATION_IDS,
            'playlist_collection_ids': self.COLLECTION_IDS
        }
        expected_collection_progress_data = {
            self.COLLECTION_IDS[0]: self.EXPLORATION_IDS
        }
        expected_story_progress_data = {
            self.STORY_ID_1: self.COMPLETED_NODE_IDS_1
        }
        thread_id = feedback_services.create_thread(
            self.THREAD_ENTITY_TYPE,
            self.THREAD_ENTITY_ID,
            self.USER_ID_1,
            self.THREAD_SUBJECT,
            self.MESSAGE_TEXT
        )
        feedback_services.create_message(
            thread_id,
            self.USER_ID_1,
            self.THREAD_STATUS,
            self.THREAD_SUBJECT,
            self.MESSAGE_TEXT
        )
        expected_general_feedback_thread_data = {
            feedback_thread_model.id: {
                'entity_type': self.THREAD_ENTITY_TYPE,
                'entity_id': self.THREAD_ENTITY_ID,
                'status': self.THREAD_STATUS,
                'subject': self.THREAD_SUBJECT,
                'has_suggestion': self.THREAD_HAS_SUGGESTION,
                'summary': self.THREAD_SUMMARY,
                'message_count': self.THREAD_MESSAGE_COUNT,
                'last_updated_msec': utils.get_time_in_millisecs(
                    feedback_thread_model.last_updated)
            },
            thread_id: {
                'entity_type': self.THREAD_ENTITY_TYPE,
                'entity_id': self.THREAD_ENTITY_ID,
                'status': self.THREAD_STATUS,
                'subject': self.THREAD_SUBJECT,
                'has_suggestion': False,
                'summary': None,
                'message_count': 2,
                'last_updated_msec': utils.get_time_in_millisecs(
                    feedback_models.
                    GeneralFeedbackThreadModel.
                    get_by_id(thread_id).last_updated)
            }
        }
        expected_general_feedback_thread_user_data = {
            thread_id: {
                'message_ids_read_by_user': self.MESSAGE_IDS_READ_BY_USER
            }
        }
        expected_general_feedback_message_data = {
            thread_id + '.0': {
                'thread_id': thread_id,
                'message_id': 0,
                'updated_status': self.THREAD_STATUS,
                'updated_subject': self.THREAD_SUBJECT,
                'text': self.MESSAGE_TEXT,
                'received_via_email': self.MESSAGE_RECEIEVED_VIA_EMAIL
            },
            thread_id + '.1': {
                'thread_id': thread_id,
                'message_id': 1,
                'updated_status': self.THREAD_STATUS,
                'updated_subject': self.THREAD_SUBJECT,
                'text': self.MESSAGE_TEXT,
                'received_via_email': self.MESSAGE_RECEIEVED_VIA_EMAIL
            }
        }
        expected_collection_rights_data = {
            'owned_collection_ids': (
                [self.COLLECTION_IDS[0]]),
            'editable_collection_ids': (
                [self.COLLECTION_IDS[0]]),
            'voiced_collection_ids': (
                [self.COLLECTION_IDS[0]]),
            'viewable_collection_ids': [self.COLLECTION_IDS[0]]
        }
        expected_general_suggestion_data = {
            'exploration.exp1.thread_1': {
                'suggestion_type': (
                    feconf.SUGGESTION_TYPE_EDIT_STATE_CONTENT),
                'target_type': feconf.ENTITY_TYPE_EXPLORATION,
                'target_id': self.EXPLORATION_IDS[0],
                'target_version_at_submission': 1,
                'status': suggestion_models.STATUS_IN_REVIEW,
                'change_cmd': self.CHANGE_CMD
            }
        }
        expected_exploration_rights_data = {
            'owned_exploration_ids': (
                [self.EXPLORATION_IDS[0]]),
            'editable_exploration_ids': (
                [self.EXPLORATION_IDS[0]]),
            'voiced_exploration_ids': (
                [self.EXPLORATION_IDS[0]]),
            'viewable_exploration_ids': [self.EXPLORATION_IDS[0]]
        }
        expected_user_settings_data = {
            'email': self.USER_1_EMAIL,
            'role': feconf.ROLE_ID_ADMIN,
            'username': self.GENERIC_USERNAME,
            'normalized_username': self.GENERIC_USERNAME,
            'last_agreed_to_terms_msec': self.GENERIC_EPOCH,
            'last_started_state_editor_tutorial_msec': self.GENERIC_EPOCH,
            'last_started_state_translation_tutorial_msec': self.GENERIC_EPOCH,
            'last_logged_in_msec': self.GENERIC_EPOCH,
            'last_edited_an_exploration_msec': self.GENERIC_EPOCH,
            'last_created_an_exploration_msec': self.GENERIC_EPOCH,
            'profile_picture_filename': 'user_settings_profile_picture.png',
            'default_dashboard': 'learner',
            'creator_dashboard_display_pref': 'card',
            'user_bio': self.GENERIC_USER_BIO,
            'subject_interests': self.GENERIC_SUBJECT_INTERESTS,
            'first_contribution_msec': 1,
            'preferred_language_codes': self.GENERIC_LANGUAGE_CODES,
            'preferred_site_language_code': self.GENERIC_LANGUAGE_CODES[0],
            'preferred_audio_language_code': self.GENERIC_LANGUAGE_CODES[0],
            'display_alias': self.GENERIC_DISPLAY_ALIAS,
        }

        expected_subscriptions_data = {
            'creator_usernames': self.CREATOR_USERNAMES,
            'collection_ids': self.COLLECTION_IDS,
            'exploration_ids': self.EXPLORATION_IDS,
            'general_feedback_thread_ids': self.GENERAL_FEEDBACK_THREAD_IDS +
                                           [thread_id],
            'last_checked_msec': self.GENERIC_EPOCH
        }

        expected_task_entry_data = {
            'task_ids_resolved_by_user': [self.GENERIC_MODEL_ID]
        }
        expected_topic_data = {
            'managed_topic_ids': [self.TOPIC_ID_1, self.TOPIC_ID_2]
        }

        expected_voiceover_application_data = {
            'application_1_id': {
                'target_type': 'exploration',
                'target_id': 'exp_id',
                'status': 'review',
                'language_code': 'en',
                'filename': 'application_audio.mp3',
                'content': '<p>Some content</p>',
                'rejection_message': None
            },
            'application_2_id': {
                'target_type': 'exploration',
                'target_id': 'exp_id',
                'status': 'review',
                'language_code': 'en',
                'filename': 'application_audio.mp3',
                'content': '<p>Some content</p>',
                'rejection_message': None
            }
        }

        expected_contribution_rights_data = {
            'can_review_translation_for_language_codes': ['hi', 'en'],
            'can_review_voiceover_for_language_codes': ['hi'],
            'can_review_questions': True
        }

        expected_contrib_proficiency_data = {
            self.SCORE_CATEGORY_1: {
                'onboarding_email_sent': False,
                'score': 1.5
            },
            self.SCORE_CATEGORY_2: {
                'onboarding_email_sent': False,
                'score': 2
            }
        }
        expected_collection_rights_sm = {
            self.GENERIC_MODEL_ID: {
                'commit_type': self.COMMIT_TYPE,
                'commit_message': self.COMMIT_MESSAGE,
            }
        }
        expected_collection_sm = {
            self.GENERIC_MODEL_ID: {
                'commit_type': self.COMMIT_TYPE,
                'commit_message': self.COMMIT_MESSAGE,
            }
        }

        expected_skill_sm = {
            self.GENERIC_MODEL_ID: {
                'commit_type': self.COMMIT_TYPE,
                'commit_message': self.COMMIT_MESSAGE,
            }
        }
        expected_subtopic_page_sm = {
            self.GENERIC_MODEL_ID: {
                'commit_type': self.COMMIT_TYPE,
                'commit_message': self.COMMIT_MESSAGE,
            }
        }
        expected_topic_rights_sm = {
            self.GENERIC_MODEL_ID: {
                'commit_type': self.COMMIT_TYPE,
                'commit_message': self.COMMIT_MESSAGE,
            }
        }
        expected_topic_sm = {
            self.GENERIC_MODEL_ID: {
                'commit_type': self.COMMIT_TYPE,
                'commit_message': self.COMMIT_MESSAGE,
            }
        }

        expected_story_sm = {
            self.GENERIC_MODEL_ID: {
                'commit_type': self.COMMIT_TYPE,
                'commit_message': self.COMMIT_MESSAGE,
            }
        }
        expected_question_sm = {
            self.GENERIC_MODEL_ID: {
                'commit_type': self.COMMIT_TYPE,
                'commit_message': self.COMMIT_MESSAGE,
            }
        }
        expected_config_property_sm = {
            self.GENERIC_MODEL_ID: {
                'commit_type': self.COMMIT_TYPE,
                'commit_message': self.COMMIT_MESSAGE,
            }
        }

        expected_exploration_rights_sm = {
            self.GENERIC_MODEL_ID: {
                'commit_type': self.COMMIT_TYPE,
                'commit_message': self.COMMIT_MESSAGE,
            }
        }

        expected_exploration_sm = {
            'exp_1-1': {
                'commit_type': 'create',
                'commit_message':
                    'New exploration created with title \'A title\'.'
            },
            'exp_1-2': {
                'commit_type': 'edit',
                'commit_message': 'Test edit'
            }
        }

        expected_platform_parameter_sm = {
            self.GENERIC_MODEL_ID: {
                'commit_type': self.COMMIT_TYPE,
                'commit_message': self.COMMIT_MESSAGE,
            }
        }
        expected_user_email_preferences = {}
        expected_user_auth_details = {}
        expected_app_feedback_report = {
            '%s.%s.%s' % (
                self.PLATFORM_ANDROID, self.REPORT_SUBMITTED_TIMESTAMP.second,
                'randomInteger123'): {
                    'scrubbed_by': self.USER_ID_1,
                    'platform': self.PLATFORM_ANDROID,
                    'ticket_id': self.TICKET_ID,
                    'submitted_on': self.REPORT_SUBMITTED_TIMESTAMP.isoformat(),
                    'report_type': self.REPORT_TYPE_SUGGESTION,
                    'category': self.CATEGORY_OTHER,
                    'platform_version': self.PLATFORM_VERSION}}
        expected_blog_post_data = {
            'content': 'content sample',
            'title': 'sample title',
            'published_on': utils.get_time_in_millisecs(
                blog_post_model.published_on),
            'url_fragment': 'sample-url-fragment',
            'tags': ['tag', 'one'],
            'thumbnail_filename': 'thumbnail'
        }
        expected_blog_post_rights = {
            'editable_blog_post_ids': [
                self.BLOG_POST_ID_1,
                self.BLOG_POST_ID_2
            ],
        }
        expected_translation_contribution_stats_data = {
            '%s.%s.%s' % (
                self.SUGGESTION_LANGUAGE_CODE, self.USER_ID_1,
                self.TOPIC_ID_1): {
                    'language_code': self.SUGGESTION_LANGUAGE_CODE,
                    'topic_id': self.TOPIC_ID_1,
                    'submitted_translations_count': (
                        self.SUBMITTED_TRANSLATIONS_COUNT),
                    'submitted_translation_word_count': (
                        self.SUBMITTED_TRANSLATION_WORD_COUNT),
                    'accepted_translations_count': (
                        self.ACCEPTED_TRANSLATIONS_COUNT),
                    'accepted_translations_without_reviewer_edits_count': (
                        self
                        .ACCEPTED_TRANSLATIONS_WITHOUT_REVIEWER_EDITS_COUNT),
                    'accepted_translation_word_count': (
                        self.ACCEPTED_TRANSLATION_WORD_COUNT),
                    'rejected_translations_count': (
                        self.REJECTED_TRANSLATIONS_COUNT),
                    'rejected_translation_word_count': (
                        self.REJECTED_TRANSLATION_WORD_COUNT),
                    'contribution_dates': [
                        date.isoformat() for date in self.CONTRIBUTION_DATES]
                }
        }
        expected_user_data = {
            'user_stats': expected_stats_data,
            'user_settings': expected_user_settings_data,
            'user_subscriptions': expected_subscriptions_data,
            'user_skill_mastery': expected_user_skill_data,
            'user_contributions': expected_contribution_data,
            'exploration_user_data': expected_exploration_data,
            'completed_activities': expected_completed_activities_data,
            'incomplete_activities': expected_incomplete_activities_data,
            'exp_user_last_playthrough': expected_last_playthrough_data,
            'learner_playlist': expected_learner_playlist_data,
            'task_entry': expected_task_entry_data,
            'topic_rights': expected_topic_data,
            'collection_progress': expected_collection_progress_data,
            'story_progress': expected_story_progress_data,
            'general_feedback_thread':
                expected_general_feedback_thread_data,
            'general_feedback_thread_user':
                expected_general_feedback_thread_user_data,
            'general_feedback_message':
                expected_general_feedback_message_data,
            'collection_rights':
                expected_collection_rights_data,
            'general_suggestion': expected_general_suggestion_data,
            'exploration_rights': expected_exploration_rights_data,
            'general_voiceover_application':
                expected_voiceover_application_data,
            'user_contribution_proficiency': expected_contrib_proficiency_data,
            'user_contribution_rights': expected_contribution_rights_data,
            'collection_rights_snapshot_metadata':
                expected_collection_rights_sm,
            'collection_snapshot_metadata':
                expected_collection_sm,
            'skill_snapshot_metadata':
                expected_skill_sm,
            'subtopic_page_snapshot_metadata':
                expected_subtopic_page_sm,
            'topic_rights_snapshot_metadata':
                expected_topic_rights_sm,
            'topic_snapshot_metadata': expected_topic_sm,
            'translation_contribution_stats':
                expected_translation_contribution_stats_data,
            'story_snapshot_metadata': expected_story_sm,
            'question_snapshot_metadata': expected_question_sm,
            'config_property_snapshot_metadata':
                expected_config_property_sm,
            'exploration_rights_snapshot_metadata':
                expected_exploration_rights_sm,
            'exploration_snapshot_metadata': expected_exploration_sm,
            'platform_parameter_snapshot_metadata':
                expected_platform_parameter_sm,
            'user_email_preferences': expected_user_email_preferences,
            'user_auth_details': expected_user_auth_details,
            'app_feedback_report': expected_app_feedback_report,
            'blog_post': expected_blog_post_data,
            'blog_post_rights': expected_blog_post_rights
        }

        user_takeout_object = takeout_service.export_data_for_user(
            self.USER_ID_1)
        observed_data = user_takeout_object.user_data
        observed_images = user_takeout_object.user_images
        self.assertItemsEqual(observed_data, expected_user_data)
        observed_json = json.dumps(observed_data)
        expected_json = json.dumps(expected_user_data)
        self.assertItemsEqual(
            json.loads(observed_json), json.loads(expected_json))
        expected_images = [
            takeout_domain.TakeoutImage(
                self.GENERIC_IMAGE_URL, 'user_settings_profile_picture.png')
        ]
        self.assertEqual(len(expected_images), len(observed_images))
        for i, _ in enumerate(expected_images):
            self.assertEqual(
                expected_images[i].b64_image_data,
                observed_images[i].b64_image_data
            )
            self.assertEqual(
                expected_images[i].image_export_path,
                observed_images[i].image_export_path
            )

    def test_export_for_full_user_does_not_export_profile_data(self):
        """Test that exporting data for a full user does not export
        data for any profile user, atleast for the models that were
        populated for the profile user.
        """
        self.set_up_non_trivial()
        profile_user_settings_data = {
            'email': self.USER_1_EMAIL,
            'role': self.PROFILE_1_ROLE,
            'username': None,
            'normalized_username': None,
            'last_agreed_to_terms_msec': self.GENERIC_DATE,
            'last_started_state_editor_tutorial_msec': None,
            'last_started_state_translation_tutorial': None,
            'last_logged_in_msec': self.GENERIC_DATE,
            'last_created_an_exploration': None,
            'last_edited_an_exploration': None,
            'profile_picture_data_url': None,
            'default_dashboard': 'learner',
            'creator_dashboard_display_pref': 'card',
            'user_bio': self.GENERIC_USER_BIO,
            'subject_interests': self.GENERIC_SUBJECT_INTERESTS,
            'first_contribution_msec': None,
            'preferred_language_codes': self.GENERIC_LANGUAGE_CODES,
            'preferred_site_language_code': self.GENERIC_LANGUAGE_CODES[0],
            'preferred_audio_language_code': self.GENERIC_LANGUAGE_CODES[0],
            'display_alias': self.GENERIC_DISPLAY_ALIAS_2
        }
        user_skill_data = {
            self.SKILL_ID_3: self.DEGREE_OF_MASTERY_2
        }
        completed_activities_data = {
            'completed_exploration_ids': self.EXPLORATION_IDS_2,
            'completed_collection_ids': self.COLLECTION_IDS_2,
            'completed_story_ids': self.STORY_IDS,
            'learnt_topic_ids': self.TOPIC_IDS
        }
        incomplete_activities_data = {}
        last_playthrough_data = {}
        learner_playlist_data = {
            'playlist_exploration_ids': self.EXPLORATION_IDS_2,
            'playlist_collection_ids': self.COLLECTION_IDS_2
        }
        collection_progress_data = {
            self.COLLECTION_IDS_2[0]: self.EXPLORATION_IDS_2
        }
        story_progress_data = {
            self.STORY_ID_2: self.COMPLETED_NODE_IDS_2
        }
        profile_user_data = {
            'user_settings': profile_user_settings_data,
            'user_skill_mastery': user_skill_data,
            'completed_activities': completed_activities_data,
            'incomplete_activities': incomplete_activities_data,
            'exp_user_last_playthrough': last_playthrough_data,
            'learner_playlist': learner_playlist_data,
            'collection_progress': collection_progress_data,
            'story_progress': story_progress_data,
        }

        user_takeout_object = takeout_service.export_data_for_user(
            self.USER_ID_1)
        observed_data = user_takeout_object.user_data
        for key, value in profile_user_data.items():
            self.assertNotEqual(value, observed_data[key])
