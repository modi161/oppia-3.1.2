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

"""Tests for the classroom page."""

from __future__ import absolute_import  # pylint: disable=import-only-modules
from __future__ import unicode_literals  # pylint: disable=import-only-modules

from constants import constants
from core.domain import config_domain
from core.domain import topic_domain
from core.domain import topic_fetchers
from core.domain import topic_services
from core.tests import test_utils
import feconf


class BaseClassroomControllerTests(test_utils.GenericTestBase):

    def setUp(self):
        """Completes the sign-up process for the various users."""
        super(BaseClassroomControllerTests, self).setUp()
        self.signup(self.NEW_USER_EMAIL, self.NEW_USER_USERNAME)
        self.user_id = self.get_user_id_from_email(self.NEW_USER_EMAIL)


class DefaultClassroomRedirectPageTests(BaseClassroomControllerTests):

    def test_redirect_to_default_classroom(self):
        response = self.get_html_response('/learn', expected_status_int=302)
        self.assertEqual(
            'http://localhost/learn/math', response.headers['location'])


class ClassroomPageTests(BaseClassroomControllerTests):

    def test_any_user_can_access_classroom_page(self):
        response = self.get_html_response('/learn/math')
        self.assertIn('<classroom-page></classroom-page>', response)


class ClassroomDataHandlerTests(BaseClassroomControllerTests):

    def test_get(self):
        self.signup(self.ADMIN_EMAIL, self.ADMIN_USERNAME)
        admin_id = self.get_user_id_from_email(self.ADMIN_EMAIL)
        self.set_admins([self.ADMIN_USERNAME])

        self.login(self.ADMIN_EMAIL, is_super_admin=True)
        topic_id_1 = topic_fetchers.get_new_topic_id()
        topic_id_2 = topic_fetchers.get_new_topic_id()
        private_topic = topic_domain.Topic.create_default_topic(
            topic_id_1, 'private_topic_name',
            'private-topic-name', 'description')
        topic_services.save_new_topic(admin_id, private_topic)
        public_topic = topic_domain.Topic.create_default_topic(
            topic_id_2, 'public_topic_name',
            'public-topic-name', 'description')
        public_topic.thumbnail_filename = 'Topic.svg'
        public_topic.thumbnail_bg_color = (
            constants.ALLOWED_THUMBNAIL_BG_COLORS['topic'][0])
        public_topic.subtopics = [
            topic_domain.Subtopic(
                1, 'Title', ['skill_id_1', 'skill_id_2', 'skill_id_3'],
                'image.svg',
                constants.ALLOWED_THUMBNAIL_BG_COLORS['subtopic'][0],
                'dummy-subtopic-three')]
        public_topic.next_subtopic_id = 2
        topic_services.save_new_topic(admin_id, public_topic)
        topic_services.publish_topic(topic_id_2, admin_id)

        csrf_token = self.get_new_csrf_token()
        new_config_value = [{
            'name': 'math',
            'topic_ids': [topic_id_1, topic_id_2],
            'course_details': 'Course details for classroom.',
            'topic_list_intro': 'Topics covered for classroom',
            'url_fragment': 'math',
        }]

        payload = {
            'action': 'save_config_properties',
            'new_config_property_values': {
                config_domain.CLASSROOM_PAGES_DATA.name: (
                    new_config_value),
            }
        }
        self.post_json('/adminhandler', payload, csrf_token=csrf_token)
        self.logout()

        json_response = self.get_json(
            '%s/%s' % (feconf.CLASSROOM_DATA_HANDLER, 'math'))
        public_topic_summary_dict = (
            topic_fetchers.get_topic_summary_by_id(topic_id_2).to_dict())
        public_topic_summary_dict['is_published'] = True
        private_topic_summary_dict = (
            topic_fetchers.get_topic_summary_by_id(topic_id_1).to_dict())
        private_topic_summary_dict['is_published'] = False

        expected_dict = {
            'name': 'math',
            'topic_summary_dicts': [
                private_topic_summary_dict, public_topic_summary_dict
            ],
            'course_details': 'Course details for classroom.',
            'topic_list_intro': 'Topics covered for classroom'
        }
        self.assertDictContainsSubset(expected_dict, json_response)

    def test_get_fails_for_invalid_classroom_name(self):
        self.get_json(
            '%s/%s' % (
                feconf.CLASSROOM_DATA_HANDLER, 'invalid_subject'),
            expected_status_int=404)


class ClassroomPromosStatusHandlerTests(BaseClassroomControllerTests):
    """Unit test for ClassroomPromosStatusHandler."""

    def test_get_request_returns_correct_status(self):
        self.set_config_property(
            config_domain.CLASSROOM_PROMOS_ARE_ENABLED, False)

        response = self.get_json('/classroom_promos_status_handler')
        self.assertEqual(
            response, {
                'classroom_promos_are_enabled': False
            })

        self.set_config_property(
            config_domain.CLASSROOM_PROMOS_ARE_ENABLED, True)
        response = self.get_json('/classroom_promos_status_handler')
        self.assertEqual(
            response, {
                'classroom_promos_are_enabled': True,
            })