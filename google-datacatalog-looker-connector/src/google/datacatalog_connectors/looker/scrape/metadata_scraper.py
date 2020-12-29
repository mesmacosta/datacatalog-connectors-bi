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

from looker_sdk import error

from google.datacatalog_connectors.looker.scrape import \
    looker_facade


class MetadataScraper:
    __DASHBOARD_FIELDS = 'id,title,created_at,description,space,hidden,' \
                         'user_id,view_count,favorite_count,' \
                         'last_accessed_at,last_viewed_at,deleted,' \
                         'deleted_at,deleter_id,dashboard_elements'
    __FOLDER_FIELDS = 'id,name,parent_id,child_count,creator_id'
    __LOOK_FIELDS = 'id,title,created_at,updated_at,description,space,' \
                    'public,user_id,last_updater_id,query_id,url,short_url,' \
                    'public_url,excel_file_url,google_spreadsheet_formula,' \
                    'view_count,favorite_count,last_accessed_at,' \
                    'last_viewed_at,deleted,deleter_id'

    def __init__(self, looker_credentials_file):
        self.__looker_facade = looker_facade.LookerFacade(
            looker_credentials_file)

    def scrape_dashboard(self, dashboard_id):
        self.__log_scrape_start('Scraping dashboard by id: %s...',
                                dashboard_id)

        try:
            dashboard = self.__looker_facade.get_dashboard(dashboard_id=dashboard_id)
        except error.SDKError as e:
            logging.info('API call failed...')
            logging.info(e)
            raise

        return dashboard

    def scrape_all_dashboards(self):
        self.__log_scrape_start('Scraping all dashboards...')

        # The all_dashboards method response does not include all fields the
        # connector actually needs, so search_dashboards is used here.
        #
        # Please notice "lookml" dashboards are not included in
        # search_dashboards response and need a special handling.
        return self.__looker_facade.search_dashboards(
            fields=self.__DASHBOARD_FIELDS)

    def scrape_dashboards_from_folder(self, folder):
        self.__log_scrape_start('Scraping "%s" folder dashboards...',
                                folder.name)
        dashboards = self.__looker_facade.search_dashboards_by_id(
            space_id=folder.id, fields=self.__DASHBOARD_FIELDS)

        logging.info('%s dashboards found:', len(dashboards))
        for dashboard in dashboards:
            logging.info('%s [%s]', dashboard.title, dashboard.id)

        return dashboards

    def scrape_folder(self, folder_id):
        self.__log_scrape_start('Scraping folder by id: %s...', folder_id)
        return self.__looker_facade.get_folder(
            folder_id=folder_id,
            fields=f'{self.__FOLDER_FIELDS},dashboards,looks')

    def scrape_all_folders(self):
        self.__log_scrape_start('Scraping all folders...')

        # The all_folders method response does not include all fields the
        # connector actually needs, so search_folders is used here.
        #
        # Also, empty folders are not included in all_folders response.
        return self.__looker_facade.search_folders(fields=self.__FOLDER_FIELDS)

    def scrape_top_level_folders(self):
        self.__log_scrape_start('Scraping top-level folders...')
        return self.__looker_facade.search_top_level_folders(fields=self.__FOLDER_FIELDS)

    def scrape_child_folders(self, parent_folder):
        self.__log_scrape_start('Scraping "%s" children...',
                                parent_folder.name)
        return self.__looker_facade.get_child_folders(
            parent_folder_id=parent_folder.id,
            fields=self.__FOLDER_FIELDS)

    def scrape_look(self, look_id):
        self.__log_scrape_start('Scraping look by id: %s...', look_id)
        return self.__looker_facade.get_look(look_id=look_id)

    def scrape_all_looks(self):
        self.__log_scrape_start('Scraping all looks...')

        # The all_looks method response does not include all fields the
        # connector actually needs, so search_looks is used here.
        return self.__looker_facade.search_looks(fields=self.__LOOK_FIELDS)

    def scrape_looks_from_folder(self, folder):
        self.__log_scrape_start('Scraping "%s" folder looks...', folder.name)
        return self.__looker_facade.search_looks_by_id(space_id=folder.id,
                                                       fields=self.__LOOK_FIELDS)

    @lru_cache(maxsize=1024)
    def scrape_query(self, query_id):
        self.__log_scrape_start('Scraping query by id: %s...', query_id)
        return self.__looker_facade.get_query(query_id=query_id)

    @lru_cache(maxsize=1024)
    def scrape_query_generated_sql(self, query_id):
        self.__log_scrape_start('Scraping generated SQL by query id: %s...',
                                query_id)
        return self.__looker_facade.get_query_result(query_id=query_id)

    @lru_cache(maxsize=1024)
    def scrape_lookml_model_explore(self, model_name, explore_name):
        self.__log_scrape_start(
            'Scraping LookML model explore by name: %s/%s...', model_name,
            explore_name)

        try:
            model = self.__looker_facade.get_lookml_model_explore(
                model_name=model_name, explore_name=explore_name)
        except error.SDKError as e:
            logging.info('API call failed...')
            logging.info(e)
            raise

        return model

    def scrape_connection(self, connection_name):
        self.__log_scrape_start('Scraping connection by name: %s...',
                                connection_name)
        return self.__looker_facade.get_connection(connection_name=connection_name)

    @classmethod
    def __log_scrape_start(cls, message, *args):
        logging.info('')
        logging.info(message, *args)
        logging.info('-------------------------------------------------')

