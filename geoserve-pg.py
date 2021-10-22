# -*- coding: utf-8 -*-
"""
Created on Thu Oct 21 11:33:27 2021

@author: younggis
"""

import os
from typing import Optional
import requests
import json


#geoserver服务器地址
GEOSERVER_URL='http://localhost:8090/geoserver'
#geoserver用户名
GEOSERVER_USERNAME='admin'
#geoserver密码
GEOSERVER_PASSWORD='geoserver'
#geoserver默认工作区
GEOSERVER_WORKSPACE='demo'
#geoserver默认存储空间
GEOSERVER_STORE='geo_data'

#postgresql地址
PG_HOST='localhost'
#postgresql端口
PG_PORT=5432
#postgresql数据库
PG_DB='postgis'
#postgresql实例schema
PG_SCHEMA='public'
#postgresql用户名
PG_USERNAME='postgres'
#postgresql密码
PG_PASSWORD='postgis'


class Geoserver:
    def __init__(
        self,
        service_url=GEOSERVER_URL,
        username=GEOSERVER_USERNAME,
        password=GEOSERVER_PASSWORD,
        workspace=GEOSERVER_WORKSPACE,
        store=GEOSERVER_STORE,
        host=PG_HOST,
        port=PG_PORT,
        db=PG_DB,
        schema=PG_SCHEMA,
        pg_user=PG_USERNAME,
        pg_password=PG_PASSWORD,
    ):
        self.service_url = service_url
        self.username = username
        self.password = password
        try:
            #不存在工作空间，立即创建
            if self.exist_workspace(workspace)==False:
                self.create_workspace(workspace)
            self.workspace = workspace
            
            #不存在存储空间，立即创建
            if self.exist_datastore(store)==False:
                self.create_featurestore(store_name=store, workspace=workspace, db=db, host=host, pg_user=pg_user, pg_password=pg_password)
            self.store = store
        
        except:
            print('init error!')
        
    def get_version(self):
        """
        Returns the version of the geoserver.
        """
        try:
            url = "{}/rest/about/version.json".format(self.service_url)
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_version error: ", e
    def get_status(self):
        """
        Returns the status of the geoserver.
        """
        try:
            url = "{}/rest/about/status.json".format(self.service_url)
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_status error: ", e
    def get_datastore(self, store_name: str, workspace: Optional[str] = None):
        """
        Return the data store in a given workspace.

        If workspace is not provided, it will take the default workspace
        curl -X GET http://localhost:8080/geoserver/rest/workspaces/demo/datastores -H  "accept: application/xml" -H  "content-type: application/json"
        """
        try:
            if workspace is None:
                workspace = "default"

            url = "{}/rest/workspaces/{}/datastores/{}".format(
                self.service_url, workspace, store_name
            )

            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_datastores error: {}".format(e)
    def get_datastores(self, workspace: Optional[str] = None):
        """
        List all data stores in a workspace.

        If workspace is not provided, it will listout all the datastores inside default workspace
        curl -X GET http://localhost:8080/geoserver/rest/workspaces/demo/datastores -H  "accept: application/xml" -H  "content-type: application/json"
        """
        try:
            if workspace is None:
                workspace = "default"

            url = "{}/rest/workspaces/{}/datastores.json".format(
                self.service_url, workspace
            )
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_datastores error: {}".format(e)
    def get_layer(self, layer_name: str, workspace: Optional[str] = None):
        """
        Returns the layer by layer name.
        """
        try:
            url = "{}/rest/layers/{}".format(self.service_url, layer_name)
            if workspace is not None:
                url = "{}/rest/workspaces/{}/layers/{}".format(
                    self.service_url, workspace, layer_name
                )

            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_layer error: {}".format(e)

    def get_layers(self, workspace: Optional[str] = None):
        """
        Get all the layers from geoserver
        If workspace is None, it will listout all the layers from geoserver
        """
        try:
            url = "{}/rest/layers".format(self.service_url)

            if workspace is not None:
                url = "{}/rest/workspaces/{}/layers".format(self.service_url, workspace)
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_layers error: {}".format(e)
    
    def get_layergroup(self, layer_name: str, workspace: Optional[str] = None):
        """
        Returns the layer group by layer group name.
        """
        try:
            url = "{}/rest/layergroups/{}".format(self.service_url, layer_name)
            if workspace is not None:
                url = "{}/rest/workspaces/{}/layergroups/{}".format(
                    self.service_url, workspace, layer_name
                )

            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_layer error: {}".format(e)
        
    def get_layergroups(self, workspace: Optional[str] = None):
        """
        Returns all the layer groups from geoserver.

        Notes
        -----
        If workspace is None, it will list all the layer groups from geoserver.
        """
        try:
            url = "{}/rest/layergroups".format(self.service_url)

            if workspace is not None:
                url = "{}/rest/workspaces/{}/layergroups".format(
                    self.service_url, workspace
                )
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_layers error: {}".format(e)
    
    def get_style(self, style_name, workspace: Optional[str] = None):
        """
        Returns the style by style name.
        """
        try:
            url = "{}/rest/styles/{}.json".format(self.service_url, style_name)
            if workspace is not None:
                url = "{}/rest/workspaces/{}/styles/{}.json".format(
                    self.service_url, workspace, style_name
                )

            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_style error: {}".format(e)

    def get_styles(self, workspace: Optional[str] = None):
        """
        Returns all loaded styles from geoserver.
        """
        try:
            url = "{}/rest/styles.json".format(self.service_url)

            if workspace is not None:
                url = "{}/rest/workspaces/{}/styles.json".format(
                    self.service_url, workspace
                )
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_styles error: {}".format(e)
    
    def get_default_workspace(self):
        """
        Returns the default workspace.
        """
        try:
            url = "{}/rest/workspaces/default".format(self.service_url)
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_default_workspace error: {}".format(e)

    def get_workspace(self, workspace):
        '''
        get name  workspace if exist
        Example: curl -v -u admin:admin -XGET -H "Accept: text/xml"  http://localhost:8080/geoserver/rest/workspaces/acme.xml
        '''
        try:
            payload = {'recurse': 'true'}
            url = '{0}/rest/workspaces/{1}.json'.format(
                self.service_url, workspace)
            r = requests.get(url, auth=(
                self.username, self.password), params=payload)
            if r.status_code == 200:
                return r.json()
            else:
                return None

        except Exception as e:
            return 'Error: {}'.format(e)

    def get_workspaces(self):
        """
        Returns all the workspaces.
        """
        try:
            url = "{}/rest/workspaces".format(self.service_url)
            r = requests.get(url, auth=(self.username, self.password))
            return r.json()

        except Exception as e:
            return "get_workspaces error: {}".format(e)
    
    def set_default_workspace(self, workspace: str):
        """
        Set the default workspace.
        """
        try:
            url = "{}/rest/workspaces/default".format(self.service_url)
            data = "<workspace><name>{}</name></workspace>".format(workspace)
            print(url, data)
            r = requests.put(
                url,
                data,
                auth=(self.username, self.password),
                headers={"content-type": "text/xml"},
            )

            if r.status_code == 200:
                return "Status code: {}, default workspace {} set!".format(
                    r.status_code, workspace
                )

        except Exception as e:
            return "reload error: {}".format(e)

    def create_workspace(self, workspace: str):
        """
        Create a new workspace in geoserver.

        The geoserver workspace url will be same as the name of the workspace.
        """
        try:
            url = "{}/rest/workspaces".format(self.service_url)
            data = "<workspace><name>{}</name></workspace>".format(workspace)
            headers = {"content-type": "text/xml"}
            r = requests.post(
                url, data, auth=(self.username, self.password), headers=headers
            )

            if r.status_code == 201:
                return "{} Workspace {} created!".format(r.status_code, workspace)

            if r.status_code == 401:
                raise Exception("The workspace already exist")

            else:
                raise Exception("The workspace can not be created")

        except Exception as e:
            return "Error: {}".format(e)

    def create_featurestore(
        self,
        store_name: str,
        workspace: Optional[str] = None,
        db: str = "postgres",
        host: str = "localhost",
        port: int = 5432,
        schema: str = "public",
        pg_user: str = "postgres",
        pg_password: str = "admin",
        overwrite: bool = False,

        expose_primary_keys: str = "false",
        description: Optional[str] = None,
        evictor_run_periodicity: Optional[int] = 300,
        max_open_prepared_statements: Optional[int] = 50,
        encode_functions: Optional[str] = "false",
        primary_key_metadata_table: Optional[str] = None,
        batch_insert_size: Optional[int] = 1,
        preparedstatements: Optional[str] = "false",
        loose_bbox: Optional[str] = "true",
        estimated_extends: Optional[str] = "true",
        fetch_size: Optional[int] = 1000,
        validate_connections: Optional[str] = "true",
        support_on_the_fly_geometry_simplification: Optional[str] = "true",
        connection_timeout: Optional[int] = 20,
        create_database: Optional[str] = "false",
        min_connections: Optional[int] = 1,
        max_connections: Optional[int] = 10,
        evictor_tests_per_run: Optional[int] = 3,
        test_while_idle: Optional[str] = "true",
        max_connection_idle_time: Optional[int] = 300
    ):
        """
        Create PostGIS store for connecting postgres with geoserver.

        Parameters
        ----------
        store_name : str
        workspace : str, optional
        db : str
        host : str
        port : int
        schema : str
        pg_user : str
        pg_password : str
        overwrite : bool

        expose_primary_keys: str
        description : str, optional
        evictor_run_periodicity : str
        max_open_prepared_statements : int
        encode_functions : str
        primary_key_metadata_table : str
        batch_insert_size : int
        preparedstatements : str
        loose_bbox : str
        estimated_extends : str
        fetch_size : int
        validate_connections : str
        support_on_the_fly_geometry_simplification : str
        connection_timeout : int
        create_database : str
        min_connections : int
        max_connections : int
        evictor_tests_per_run : int
        test_while_idle : str
        max_connection_idle_time : int


        Notes
        -----
        After creating feature store, you need to publish it. See the layer publish guidline here: https://geoserver-rest.readthedocs.io/en/latest/how_to_use.html#creating-and-publishing-featurestores-and-featurestore-layers 
        """

        url = "{}/rest/workspaces/{}/datastores".format(self.service_url, workspace)

        headers = {
            'content-type': 'text/xml'
        }

        database_connection = ("""
                <dataStore>
                <name>{0}</name>
                <description>{1}</description>
                <connectionParameters>
                <entry key="Expose primary keys">{2}</entry>
                <entry key="host">{3}</entry>
                <entry key="port">{4}</entry>
                <entry key="user">{5}</entry>
                <entry key="passwd">{6}</entry>
                <entry key="dbtype">postgis</entry>
                <entry key="schema">{7}</entry>
                <entry key="database">{8}</entry>
                <entry key="Evictor run periodicity">{9}</entry>
                <entry key="Max open prepared statements">{10}</entry>
                <entry key="encode functions">{11}</entry>
                <entry key="Primary key metadata table">{12}</entry>
                <entry key="Batch insert size">{13}</entry>
                <entry key="preparedStatements">{14}</entry>
                <entry key="Estimated extends">{15}</entry>
                <entry key="fetch size">{16}</entry>
                <entry key="validate connections">{17}</entry>
                <entry key="Support on the fly geometry simplification">{18}</entry>
                <entry key="Connection timeout">{19}</entry>
                <entry key="create Database">{20}</entry>
                <entry key="min connections">{21}</entry>
                <entry key="max connections">{22}</entry>
                <entry key="Evictor tests per run">{23}</entry>
                <entry key="Test while idle">{24}</entry>
                <entry key="Max connection idle time">{25}</entry>
                <entry key="Loose bbox">{26}</entry>
                </connectionParameters>              
                </dataStore>
                """.format(
                store_name, description, expose_primary_keys, host, port, pg_user, pg_password, schema, db,
                evictor_run_periodicity, max_open_prepared_statements, encode_functions, primary_key_metadata_table,
                batch_insert_size, preparedstatements, estimated_extends, fetch_size, validate_connections, 
                support_on_the_fly_geometry_simplification, connection_timeout, create_database, min_connections,
                max_connections, evictor_tests_per_run, test_while_idle, max_connection_idle_time, loose_bbox
                 )
        )

        r = None
        try:
            if overwrite:
                url = "{0}/rest/workspaces/{1}/datastores/{2}".format(
                    self.service_url, workspace, store_name)

                r = requests.put(url, data=database_connection, auth=(
                    self.username, self.password), headers=headers)

                if r.status_code not in [200, 201]:
                    return '{}: Datastore can not be updated. {}'.format(r.status_code, r.content)
            else:
                r = requests.post(url, data=database_connection, auth=(
                    self.username, self.password), headers=headers)

                if r.status_code not in [200, 201]:
                    return '{}: Data store can not be created! {}'.format(r.status_code, r.content)

        except Exception as e:
            return "Error: {}".format(e)
    
    def publish_featurestore(self, store_name: str, pg_table: str, workspace: Optional[str] = None):
        """

        Parameters
        ----------
        store_name : str
        pg_table : str
        workspace : str, optional

        Returns
        -------

        Notes
        -----
        Only user for postgis vector data
        input parameters: specify the name of the table in the postgis database to be published, specify the store,workspace name, and  the Geoserver user name, password and URL
        """
        if workspace is None:
            workspace = "default"

        url = "{}/rest/workspaces/{}/datastores/{}/featuretypes/".format(
            self.service_url, workspace, store_name)

        layer_xml = "<featureType><name>{}</name></featureType>".format(pg_table)
        headers = {"content-type": "text/xml"}

        try:
            r = requests.post(url, data=layer_xml, auth=(
                self.username, self.password), headers=headers)
            if r.status_code not in [200, 201]:
                return '{}: Data can not be published! {}'.format(r.status_code, r.content)

        except Exception as e:
            return "Error: {}".format(e)

    def edit_featuretype(self,
                        store_name: str,
                        workspace: Optional[str],
                        pg_table: str,
                        name: str,
                        title: str
                        ):
        """

        Parameters
        ----------
        store_name : str
        workspace : str, optional
        pg_table : str
        name : str
        title : str

        Returns
        -------

        Notes
        -----
        """

        if workspace is None:
            workspace = "default"

        url = "{}/rest/workspaces/{}/datastores/{}/featuretypes/{}.xml".format(
            self.service_url, workspace, store_name,pg_table)

        layer_xml = """<featureType>
                    <name>{}</name>
                    <title>{}</title>
                    </featureType>""".format(name,title)
        headers = {"content-type": "text/xml"}

        try:
            r = requests.put(url, data=layer_xml, auth=(
                self.username, self.password), headers=headers)
            if r.status_code not in [200, 201]:
                return '{}: Data has not been edited! {}'.format(r.status_code, r.content)

        except Exception as e:
            return "Error: {}".format(e)



    def publish_featurestore_sqlview(
        self,
        name: str,
        store_name: str,
        sql: str,
        key_column: str,
        geom_name: str = "geom",
        geom_type: str = "Geometry",
        workspace: Optional[str] = None,
        sql_parameter: Optional[list] = None
    ):
        """

        Parameters
        ----------
        name : str
        store_name : str
        sql : str
        key_column : str
        geom_name : str
        geom_type : str
        workspace : str, optional

        """
        if workspace is None:
            workspace = "default"
        
        parameter=''
        if sql_parameter is not None:
            for i in range(len(sql_parameter)):
                parameter+='<parameter>'
                parameter+='<name>'+sql_parameter[i]['name']+'</name>'
                parameter+='<defaultValue>'+sql_parameter[i]['defaultValue']+'</defaultValue>'
                parameter+='</parameter>'
        layer_xml = """<featureType>
        <name>{0}</name>
        <enabled>true</enabled>
        <namespace>
        <name>{5}</name>
        </namespace>
        <title>{0}</title>
        <srs>EPSG:4326</srs>
        <metadata>
        <entry key="JDBC_VIRTUAL_TABLE">
        <virtualTable>
        <name>{0}</name>
        <sql>{1}</sql>
        {6}
        <escapeSql>true</escapeSql>
        <keyColumn>{2}</keyColumn>
        <geometry>
        <name>{3}</name>
        <type>{4}</type>
        <srid>4326</srid>
        </geometry>
        </virtualTable>
        </entry>
        </metadata>
        </featureType>""".format(name, sql, key_column, geom_name, geom_type, workspace,str(parameter).encode("utf-8").decode("latin1"))

        url = "{0}/rest/workspaces/{1}/datastores/{2}/featuretypes".format(
            self.service_url, workspace, store_name)

        headers = {"content-type": "text/xml"}
        try:
            r = requests.post(url, data=layer_xml, auth=(self.username, self.password), headers=headers)
            if r.status_code not in [200, 201]:
                return '{}: Data can not be published! {}'.format(r.status_code, r.content)

        except Exception as e:
            print(e)
            return "Error: {}".format(e)
        
        
    def publish_layergroup(
        self,
        name: str,
        title: str,
        mode: Optional[str] = None,
        layer_list: Optional[list] = None,
        workspace: Optional[str] = None
    ):
        if mode is None:
            mode='SINGLE'
        publishables=[]
        styles=[]
        if layer_list is not None:
            for i in range(len(layer_list)):
                layer=self.get_layer(layer_list[i],workspace)
                publishables.append({
                    '@type': "layer",
                    'href': "{0}/rest/workspaces/{1}/layers/{2}.json".format(self.service_url,workspace, layer_list[i]),
                    'name': "{0}:{1}".format(workspace, layer_list[i])
                })
                styles.append(layer['layer']['defaultStyle'])
        else:
             return Exception('no layer to publish!')
        layergroup_json = {
            "layerGroup":{
                "name": name,
                "mode": mode,
                "title": title,
                "workspace": {
                    "name": workspace
                },
                "publishables": {
                    "published": publishables
                },
                "styles": {
                    "style": styles
                },
                "bounds": {
                    "minx": 0,
                    "maxx": 180,
                    "miny": 0,
                    "maxy": 90,
                    "crs": "EPSG:4326"
                }
            }
        }
        url = "{0}/rest/workspaces/{1}/layergroups".format(
            self.service_url, workspace)
        headers = {"content-type": "application/json"}
        try:
            r = requests.post(url, data=json.dumps(layergroup_json), auth=(
                self.username, self.password), headers=headers)
            if r.status_code not in [200, 201]:
                return '{}: Data can not be published! {}'.format(r.status_code, r.content)

        except Exception as e:
            return "Error: {}".format(e)
        
    
    def upload_style(
        self,
        path: str,
        name: Optional[str] = None,
        workspace: Optional[str] = None,
        sld_version: str = "1.0.0",
    ):
        """

        Parameters
        ----------
        path : str
        name : str, optional
        workspace : str, optional
        sld_version : str, optional

        Notes
        -----
        The name of the style file will be, sld_name:workspace
        This function will create the style file in a specified workspace.
        Inputs: path to the sld_file, workspace,
        """

        if name is None:
            name = os.path.basename(path)
            f = name.split(".")
            if len(f) > 0:
                name = f[0]

        headers = {"content-type": "text/xml"}

        url = "{}/rest/workspaces/{}/styles".format(self.service_url, workspace)

        sld_content_type = "application/vnd.ogc.sld+xml"
        if sld_version == "1.1.0" or sld_version == "1.1":
            sld_content_type = "application/vnd.ogc.se+xml"

        header_sld = {"content-type": sld_content_type}

        if workspace is None:
            # workspace = "default"
            url = "{}/rest/styles".format(self.service_url)

        style_xml = "<style><name>{}</name><filename>{}</filename></style>".format(
            name, name + ".sld"
        )

        r = None
        try:
            r = requests.post(url, data=style_xml, auth=(
                self.username, self.password), headers=headers)

            with open(path, 'rb') as f:
                r_sld = requests.put(url + '/' + name, data=f.read(), auth=(
                    self.username, self.password), headers=header_sld)
                if r_sld.status_code not in [200, 201]:
                    return '{}: Style file can not be uploaded! {}'.format(r.status_code, r.content)

            return r_sld.status_code

        except Exception as e:
            return "Error: {}".format(e)

    def get_featuretypes(self, workspace: str = None, store_name: str = None):
        """

        Parameters
        ----------
        workspace : str
        store_name : str

        """
        url = "{}/rest/workspaces/{}/datastores/{}/featuretypes.json".format(
            self.service_url, workspace, store_name
        )
        r = requests.get(url, auth=(self.username, self.password))
        r_dict = r.json()
        features = [i["name"] for i in r_dict["featureTypes"]["featureType"]]
        print("Status code: {}, Get feature type".format(r.status_code))

        return features

    def get_feature_attribute(
        self, feature_type_name: str, workspace: str, store_name: str
    ):
        """

        Parameters
        ----------
        feature_type_name : str
        workspace : str
        store_name : str

        """
        url = "{}/rest/workspaces/{}/datastores/{}/featuretypes/{}.json".format(
            self.service_url, workspace, store_name, feature_type_name
        )
        r = requests.get(url, auth=(self.username, self.password))
        r_dict = r.json()
        attribute = [
            i["name"] for i in r_dict["featureType"]["attributes"]["attribute"]
        ]
        print("Status code: {}, Get feature attribute".format(r.status_code))

        return attribute

    def get_featurestore(self, store_name: str, workspace: str):
        """

        Parameters
        ----------
        store_name : str
        workspace : str

        """
        url = "{}/rest/workspaces/{}/datastores/{}".format(
            self.service_url, workspace, store_name
        )
        r = requests.get(url, auth=(self.username, self.password))
        try:
            r_dict = r.json()
            return r_dict["dataStore"]

        except Exception as e:
            return "Error: {}".format(e)
    
    def publish_style(
        self,
        layer_name: str,
        style_name: str,
        workspace: str,
    ):
        """Publish a raster file to geoserver.

        Parameters
        ----------
        layer_name : str
        style_name : str
        workspace : str

        Notes
        -----
        The coverage store will be created automatically as the same name as the raster layer name.
        input parameters: the parameters connecting geoserver (user,password, url and workspace name),
        the path to the file and file_type indicating it is a geotiff, arcgrid or other raster type.

        """

        headers = {"content-type": "text/xml"}
        url = "{0}/rest/layers/{1}:{2}".format(self.service_url, workspace, layer_name)
        style_xml = (
            "<layer><defaultStyle><name>{}</name></defaultStyle></layer>".format(style_name))

        r = None
        try:
            r = requests.put(url, data=style_xml, auth=(
                self.username, self.password), headers=headers)

            return r.status_code

        except Exception as e:
            return "Error: {}".format(e)

    def delete_workspace(self, workspace: str):
        """

        Parameters
        ----------
        workspace : str

        """
        try:
            payload = {"recurse": "true"}
            url = "{}/rest/workspaces/{}".format(self.service_url, workspace)
            r = requests.delete(url, auth=(self.username, self.password), param=payload)

            if r.status_code == 200:
                return "Status code: {}, delete workspace".format(r.status_code)

            else:
                raise Exception("Error: {} {}".format(r.status_code, r.content))

        except Exception as e:
            return "Error: {}".format(e)

    def delete_layer(self, layer_name: str, workspace: Optional[str] = None):
        """

        Parameters
        ----------
        layer_name : str
        workspace : str, optional

        """
        try:
            payload = {"recurse": "true"}
            url = "{}/rest/workspaces/{}/layers/{}".format(
                self.service_url, workspace, layer_name
            )
            if workspace is None:
                url = "{}/rest/layers/{}".format(self.service_url, layer_name)

            r = requests.delete(
                url, auth=(self.username, self.password), params=payload
            )
            if r.status_code == 200:
                return "Status code: {}, delete layer".format(r.status_code)

            else:
                raise Exception("Error: {} {}".format(r.status_code, r.content))

        except Exception as e:
            return "Error: {}".format(e)

    def delete_featurestore(
        self, featurestore_name: str, workspace: Optional[str] = None
    ):
        """

        Parameters
        ----------
        featurestore_name : str
        workspace : str, optional

        """
        try:
            payload = {"recurse": "true"}
            url = "{}/rest/workspaces/{}/datastores/{}".format(
                self.service_url, workspace, featurestore_name
            )
            if workspace is None:
                url = "{}/rest/datastores/{}".format(
                    self.service_url, featurestore_name
                )
            r = requests.delete(
                url, auth=(self.username, self.password), params=payload
            )

            if r.status_code == 200:
                return "Status code: {}, delete featurestore".format(r.status_code)

            else:
                raise Exception("Error: {} {}".format(r.status_code, r.content))

        except Exception as e:
            return "Error: {}".format(e)
        
    def delete_style(self, style_name: str, workspace: Optional[str] = None):
        """

        Parameters
        ----------
        style_name : str
        workspace : str, optional
        """
        try:
            payload = {"recurse": "true"}
            url = "{}/rest/workspaces/{}/styles/{}".format(
                self.service_url, workspace, style_name
            )
            if workspace is None:
                url = "{}/rest/styles/{}".format(self.service_url, style_name)

            r = requests.delete(url, auth=(self.username, self.password), param=payload)

            if r.status_code == 200:
                return "Status code: {}, delete style".format(r.status_code)

            else:
                raise Exception("Error: {} {}".format(r.status_code, r.content))

        except Exception as e:
            return "Error: {}".format(e)
        
    def exist_layer(self, layer_name: str, workspace: Optional[str] = None):
        try:
            url = "{}/rest/layers/{}".format(self.service_url, layer_name)
            if workspace is not None:
                url = "{}/rest/workspaces/{}/layers/{}".format(
                    self.service_url, workspace, layer_name
                )
            r = requests.get(url, auth=(self.username, self.password))
            r.json()
            return True
        except:
            return False
        
    def exist_style(self, style_name: str, workspace: Optional[str] = None):
        try:
            url = "{}/rest/styles/{}.json".format(self.service_url, style_name)
            if workspace is not None:
                url = "{}/rest/workspaces/{}/styles/{}.json".format(
                    self.service_url, workspace, style_name
                )
            r = requests.get(url, auth=(self.username, self.password))
            r.json()
            return True
        except:
            return False
    
    def exist_layergroup(self, layer_name: str, workspace: Optional[str] = None):
        try:
            url = "{}/rest/layergroups/{}".format(self.service_url, layer_name)
            if workspace is not None:
                url = "{}/rest/workspaces/{}/layergroups/{}".format(
                    self.service_url, workspace, layer_name
                )

            r = requests.get(url, auth=(self.username, self.password))
            r.json()
            return True
        except:
            return False
        
    def exist_workspace(self, workspace):
        try:
            payload = {'recurse': 'true'}
            url = '{0}/rest/workspaces/{1}.json'.format(
                self.service_url, workspace)
            r = requests.get(url, auth=(
                self.username, self.password), params=payload)
            if r.status_code == 200:
                r.json()
                return True
            else:
                return False
        except:
            return False
    
    def exist_datastore(self, store_name: str, workspace: Optional[str] = None):
        try:
            if workspace is None:
                workspace = "default"

            url = "{}/rest/workspaces/{}/datastores/{}".format(
                self.service_url, workspace, store_name
            )

            r = requests.get(url, auth=(self.username, self.password))
            r.json()
            return True
        except:
            return False
        
if __name__ == '__main__':
    geoserver=Geoserver()
    #print(geoserver.publish_layergroup('py_layergroup','title',mode=None,layer_list=['famen_new','guanduan_new'],workspace='demo'))
    
    sql="select * from juminqu_0721 where city='%city%' and county='%county%'"
    sql_parameter=[{
        'name':'city',
        'defaultValue':'成都'
        },{
        'name':'county',
        'defaultValue':'锦江区'
        }]
    geoserver.publish_featurestore_sqlview(store_name='geo_data', name='oilsystem',key_column='id', sql=sql,workspace='demo',sql_parameter=sql_parameter)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    