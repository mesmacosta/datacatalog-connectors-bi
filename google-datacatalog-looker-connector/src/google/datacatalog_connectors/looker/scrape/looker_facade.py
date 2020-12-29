#!/usr/bin/python
#
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from functools import lru_cache
import logging

from looker_sdk import client, error


class LookerFacade:
    """Wraps Looker's API calls."""

    def __init__(self, looker_credentials_file):
        self.__sdk = client.setup(looker_credentials_file)

    def get_child_folders(self, parent_folder_id, fields=None):
        folders = self.__sdk.folder_children(folder_id=parent_folder_id,
                                             fields=fields)

        logging.info('%s folders found:', len(folders))
        for folder in folders:
            logging.info('%s/%s [%s]', parent_folder.name, folder.name,
                         folder.id)

        return folders

    @lru_cache(maxsize=128)
    def get_connection(self, connection_name):
        connection = self.__sdk.connection(connection_name=connection_name)
        self.__log_single_object_scrape_result(connection)
        return connection

    def get_dashboard(self, dashboard_id):
        dashboard = self.__sdk.dashboard(dashboard_id=dashboard_id)
        self.__log_single_object_scrape_result(dashboard)
        return dashboard

    def get_folder(self, folder_id, fields=None):
        folder = self.__sdk.folder(folder_id=folder_id, fields=fields)
        self.__log_single_object_scrape_result(folder)
        return folder

    def get_look(self, look_id):
        look = self.__sdk.look(look_id=look_id)
        self.__log_single_object_scrape_result(look)
        return look

    @lru_cache(maxsize=1024)
    def get_lookml_model_explore(self, model_name, explore_name):
        explore = self.__sdk.lookml_model_explore(lookml_model_name=model_name,
                                                  explore_name=explore_name)
        self.__log_single_object_scrape_result(explore)
        return explore

    @lru_cache(maxsize=1024)
    def get_query(self, query_id):
        query = self.__sdk.query(query_id=query_id)
        self.__log_single_object_scrape_result(query)
        return query

    @lru_cache(maxsize=1024)
    def get_query_result(self, query_id, result_format='sql'):
        query_result = self.__sdk.run_query(query_id=query_id, result_format=result_format)
        self.__log_single_object_scrape_result(query_result)
        return query_result

    def search_dashboards(self, fields=None):
        dashboards = self.__sdk.search_dashboards(fields=fields)

        logging.info('%s dashboards found:', len(dashboards))
        for dashboard in dashboards:
            logging.info('%s [%s]', dashboard.title, dashboard.id)

        return dashboards

    def search_dashboards_by_id(self, space_id, fields=None):
        dashboards = self.__sdk.search_dashboards(
            space_id=space_id, fields=fields)

        logging.info('%s dashboards found:', len(dashboards))
        for dashboard in dashboards:
            logging.info('%s [%s]', dashboard.title, dashboard.id)

        return dashboards

    def search_folders(self, fields=None):
        folders = self.__sdk.search_folders(fields=fields)

        logging.info('%s folders found:', len(folders))
        for folder in folders:
            logging.info('%s [%s]', folder.name, folder.id)

        return folders

    def search_looks(self, fields=None):
        looks = self.__sdk.search_looks(fields=fields)

        logging.info('%s looks found:', len(looks))
        for look in looks:
            logging.info('%s [%s]', look.title, look.id)

        return looks

    def search_looks_by_id(self, space_id, fields=None):
        looks = self.__sdk.search_looks(space_id=space_id,
                                        fields=fields)

        logging.info('%s looks found:', len(looks))
        for look in looks:
            logging.info('%s [%s]', look.title, look.id)

        return looks

    def search_top_level_folders(self, fields=None):
        folders = self.__sdk.search_folders(fields=fields,
                                            parent_id='IS NULL')

        logging.info('%s folders found:', len(folders))
        for folder in folders:
            logging.info('/%s [%s]', folder.name, folder.id)

        return folders

    @classmethod
    def __log_single_object_scrape_result(cls, the_object):
        logging.info('Found!' if the_object else 'NOT found!')
