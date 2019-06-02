#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#    
#    This file is a part of Metrix++ Tool.
#    

import sqlite3
import re
import os.path
import logging
import itertools 
import shutil
import traceback

class Database(object):
    
    last_used_id = 0
    version = "1.0"
    
    class TableData(object):
        def __init__(self, table_id, name, support_regions):
            self.id = table_id
            self.name = name
            self.support_regions = support_regions
    
    class ColumnData(object):
        def __init__(self, column_id, name, sql_type, non_zero):
            self.id = column_id
            self.name = name
            self.sql_type = sql_type
            self.non_zero = non_zero

    class TagData(object):
        def __init__(self, tag_id, name):
            self.id = tag_id
            self.name = name

    class PropertyData(object):
        def __init__(self, property_id, name, value):
            self.id = property_id
            self.name = name
            self.value = value

    class FileData(object):
        def __init__(self, file_id, path, checksum):
            self.id = file_id
            self.path = path
            self.checksum = checksum

    class RegionData(object):
        def __init__(self, file_id, region_id, name, begin, end, line_begin, line_end, cursor, group, checksum):
            self.file_id = file_id
            self.region_id = region_id
            self.name = name
            self.begin = begin
            self.end = end
            self.line_begin = line_begin
            self.line_end = line_end
            self.cursor = cursor
            self.group = group
            self.checksum = checksum

    class MarkerData(object):
        def __init__(self, file_id, begin, end, group):
            self.file_id = file_id
            self.begin = begin
            self.end = end
            self.group = group

    def __init__(self):
        self.read_only = False
        self.conn = None
        self.dirs = None
        self.is_cloned = False
        
        self.last_used_id += 1
        self.id = self.last_used_id
        self._tables_cache = None
    
    def __del__(self):
        if self.conn != None:
            if self.is_cloned == True:
                logging.debug("Cleaning up database file")
                self.InternalCleanUpUtils().clean_up_not_confirmed(self)
            logging.debug("Committing database file")
            self.conn.commit()
    
    class InternalCleanUpUtils(object):
        
        def clean_up_not_confirmed(self, db_loader):
            sql = "DELETE FROM __info__ WHERE (confirmed = 0)"
            db_loader.log(sql)
            db_loader.conn.execute(sql)
            sql = "DELETE FROM __tags__ WHERE (confirmed = 0)"
            db_loader.log(sql)
            db_loader.conn.execute(sql)

            sql = "SELECT * FROM __tables__ WHERE (confirmed = 0)"
            db_loader.log(sql)
            for table in db_loader.conn.execute(sql).fetchall():
                sql = "DELETE FROM __columns__ WHERE table_id = '" + str(table['id']) + "'"
                db_loader.log(sql)
                db_loader.conn.execute(sql)
                sql = "DELETE FROM __tables__ WHERE id = '" + str(table['id']) + "'"
                db_loader.log(sql)
                db_loader.conn.execute(sql)
                self._tables_cache = None # reset cache when a list of tables is modified
                sql = "DROP TABLE '" + table['name'] + "'"
                db_loader.log(sql)
                db_loader.conn.execute(sql)

            sql = "SELECT __columns__.name AS column_name, __tables__.name AS table_name, __columns__.id AS column_id FROM __columns__, __tables__ WHERE (__columns__.confirmed = 0 AND __columns__.table_id = __tables__.id)"
            db_loader.log(sql)
            for column in db_loader.conn.execute(sql).fetchall():
                logging.info("New database file inherits useless column: '" + column['table_name'] + "'.'" + column['column_name'] + "'")
                sql = "DELETE FROM __columns__ WHERE id = '" + str(column['column_id']) + "'"
                db_loader.log(sql)
                db_loader.conn.execute(sql)
                sql = "UPDATE '" + column['table_name'] + "' SET '" + column['column_name'] + "' = NULL"
                # TODO bug here: collect with column, recollect without, recollect with again
                # it will be impossible to create the column in the table
                db_loader.log(sql)
                db_loader.conn.execute(sql)
            
            self.clean_up_file(db_loader)

        def clean_up_file(self, db_loader, file_id = None):
            # this function is called on every updated file, so cache table names
            if db_loader._tables_cache == None:
                db_loader._tables_cache = []
                sql = "SELECT * FROM __tables__"
                db_loader.log(sql)
                for table in db_loader.conn.execute(sql).fetchall():
                    db_loader._tables_cache.append(table['name'])

            for table_name in itertools.chain(db_loader._tables_cache, ['__regions__', '__markers__']):
                sql = ""
                if file_id == None:
                    sql = "DELETE FROM '" + table_name + "' WHERE file_id IN (SELECT __files__.id FROM __files__ WHERE __files__.confirmed = 0)"
                else:
                    sql = "DELETE FROM '" + table_name + "' WHERE (file_id = " + str(file_id) + ")"
                db_loader.log(sql)
                db_loader.conn.execute(sql)
            
            
    class InternalPathUtils(object):
        
        def iterate_heads(self, path):
            dirs = []
            head = os.path.dirname(path)
            last_head = None # to process Windows drives
            while (head != "" and last_head != head):
                dirs.append(os.path.basename(head))
                last_head = head
                head = os.path.dirname(head)
            dirs.reverse()
            for each in dirs:
                yield each
                
        def normalize_path(self, path):
            if path == None:
                return None
            path =re.sub(r'''[\\]''', "/", path)
            if len(path) > 0 and path[len(path) - 1] == '/':
                return path[:-1]
            return path 
        
        def update_dirs(self, db_loader, path = None):
            if db_loader.dirs == None:
                if path == None:
                    db_loader.dirs = {} # initial construction
                else:
                    return # avoid useless cache updates 
            elif path == None:
                return # avoid multiple initial constructions
            
            path = self.normalize_path(path)
            rows = None
            if path == None:
                sql = "SELECT * FROM __files__"
                db_loader.log(sql)
                rows = db_loader.conn.execute(sql).fetchall()
            else:
                rows = [{"path": path}]
            for row in rows:
                cur_head = db_loader.dirs
                for dir_name in self.iterate_heads(row["path"]):
                    if dir_name not in list(cur_head.keys()):
                        cur_head[dir_name] = {}
                    cur_head = cur_head[dir_name]
                cur_head[os.path.basename(row["path"])] = None


    def create(self, file_name, clone_from = None):
        if clone_from != None:
            self.is_cloned = True
            logging.debug("Cloning database file: " + clone_from)
            shutil.copy2(clone_from, file_name)
            logging.debug("Connecting database file: " + file_name)
            self.conn = sqlite3.connect(file_name, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.read_only = False
            
            sql = "UPDATE __tables__ SET confirmed = 0"
            self.log(sql)
            self.conn.execute(sql)
            self._tables_cache = None # reset cache when a list of tables is modified
            sql = "UPDATE __columns__ SET confirmed = 0"
            self.log(sql)
            self.conn.execute(sql)
            sql = "UPDATE __tags__ SET confirmed = 0"
            self.log(sql)
            self.conn.execute(sql)
            sql = "UPDATE __files__ SET confirmed = 0"
            self.log(sql)
            self.conn.execute(sql)
                
        else:
            self.connect(file_name)
        
    def connect(self, file_name, read_only = False):
        logging.debug("Connecting database file: " + file_name)
        self.conn = sqlite3.connect(file_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.read_only = read_only
        if self.read_only == False:
            try:
                sql = "CREATE TABLE __info__ (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, property text NOT NULL, value text, confirmed integer NOT NULL, UNIQUE (property) ON CONFLICT REPLACE)"
                self.log(sql)
                self.conn.execute(sql)
                sql = "INSERT INTO __info__ (property, value, confirmed) VALUES ('version', '" + self.version + "', 1)"
                self.log(sql)
                self.conn.execute(sql)
                sql = "CREATE TABLE __tables__ (id integer NOT NULL PRIMARY KEY, name text NOT NULL, version text NOT NULL, support_regions integer NOT NULL, confirmed integer NOT NULL, UNIQUE (name))"
                self.log(sql)
                self.conn.execute(sql)
                self._tables_cache = None # reset cache when a list of tables is modified
                sql = "CREATE TABLE __columns__ (id integer NOT NULL PRIMARY KEY, name text NOT NULL, type text NOT NULL, table_id integer NOT_NULL, non_zero integer NOT NULL, confirmed integer NOT NULL, UNIQUE (name, table_id))"
                self.log(sql)
                self.conn.execute(sql)
                sql = "CREATE TABLE __tags__ (id integer NOT NULL PRIMARY KEY, name text NOT NULL UNIQUE, confirmed integer NOT NULL)"
                self.log(sql)
                self.conn.execute(sql)
                sql = "CREATE TABLE __files__ (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, path text NOT NULL, checksum integer NOT NULL, tag1 integer, tag2 integer, tag3 integer, confirmed integer NOT NULL, UNIQUE(path))"
                self.log(sql)
                self.conn.execute(sql)
                sql = "CREATE TABLE __regions__ (file_id integer NOT NULL, region_id integer NOT NULL, name text NOT NULL, begin integer NOT NULL, end integer NOT NULL, line_begin integer NOT NULL, line_end integer NOT NULL, cursor integer NOT NULL, group_id integer NOT NULL, checksum integer NOT NULL, PRIMARY KEY (file_id, region_id))"
                self.log(sql)
                self.conn.execute(sql)
                sql = "CREATE TABLE __markers__ (id integer NOT NULL PRIMARY KEY, file_id integer NOT NULL, begin integer NOT NULL, end integer NOT NULL, group_id integer NOT NULL)"
                self.log(sql)
                self.conn.execute(sql)
            except sqlite3.OperationalError as e:
                logging.debug("sqlite3.OperationalError: " + str(e))
                
    def set_property(self, property_name, value):
        ret_val = None
        sql = "SELECT * FROM __info__ WHERE (property = '" + property_name + "')"
        self.log(sql)
        result = self.conn.execute(sql).fetchall()
        if len(result) != 0:
            ret_val = result[0]['value']

        sql = "INSERT INTO __info__ (property, value, confirmed) VALUES ('" + property_name + "', '" + value + "', 1)"
        self.log(sql)
        self.conn.execute(sql)
        return ret_val
        
    def get_property(self, property_name):
        ret_val = None
        sql = "SELECT * FROM __info__ WHERE (property = '" + property_name + "' AND confirmed = 1)"
        self.log(sql)
        result = self.conn.execute(sql).fetchall()
        if len(result) != 0:
            ret_val = result[0]['value']
        return ret_val

    def iterate_properties(self):
        sql = "SELECT * FROM __info__ WHERE (confirmed = 1)"
        self.log(sql)
        for each in self.conn.execute(sql).fetchall():
            yield self.PropertyData(each['id'], each['property'], each['value'])

    def create_table(self, table_name, support_regions = False, version='1.0'):
        assert(self.read_only == False)

        self._tables_cache = None # reset cache when a list of tables is modified
        
        sql = "SELECT * FROM __tables__ WHERE (name = '" + table_name + "'AND confirmed == 0)"
        self.log(sql)
        result = self.conn.execute(sql).fetchall()
        if len(result) != 0:
            if result[0]['version'] != version:
                # in case of changes in version, drop existing table data
                sql = "DELETE FROM __columns__ WHERE table_id = '" + str(result[0]['id']) + "'"
                self.log(sql)
                self.conn.execute(sql)
                sql = "DELETE FROM __tables__ WHERE id = '" + str(result[0]['id']) + "'"
                self.log(sql)
                self.conn.execute(sql)
                sql = "DROP TABLE '" + result[0]['name'] + "'"
                self.log(sql)
                self.conn.execute(sql)
            else:                
                sql = "UPDATE __tables__ SET confirmed = 1 WHERE (name = '" + table_name + "')"
                self.log(sql)
                self.conn.execute(sql)
                return False      
        
        sql = "CREATE TABLE '" + table_name + "' (file_id integer NOT NULL PRIMARY KEY)"
        if support_regions == True:
            sql = str("CREATE TABLE '" + table_name + "' (file_id integer NOT NULL, region_id integer NOT NULL, "
                      + "PRIMARY KEY (file_id, region_id))")
            
        self.log(sql)
        self.conn.execute(sql)
        sql = "INSERT INTO __tables__ (name, version, support_regions, confirmed) VALUES ('" + table_name + "', '" + version + "', '" + str(int(support_regions)) + "', 1)"
        self.log(sql)
        self.conn.execute(sql)
        return True

    def iterate_tables(self):
        sql = "SELECT * FROM __tables__ WHERE (confirmed = 1)"
        self.log(sql)
        result = self.conn.execute(sql).fetchall()
        for row in result:
            yield self.TableData(int(row["id"]), str(row["name"]), bool(row["support_regions"]))
            
    def check_table(self, table_name):
        sql = "SELECT * FROM __tables__ WHERE (name = '" + table_name + "' AND confirmed = 1)"
        self.log(sql)
        result = self.conn.execute(sql).fetchall()
        if len(result) == 0:
            return False
        return True

    def create_column(self, table_name, column_name, column_type, non_zero=False):
        assert(self.read_only == False)
        if column_type == None:
            logging.debug("Skipping column '" + column_name + "' creation for table '" + table_name + "'")
            return
        
        sql = "SELECT id FROM __tables__ WHERE (name = '" + table_name + "')"
        self.log(sql)
        table_id = next(self.conn.execute(sql))['id']

        sql = "SELECT * FROM __columns__ WHERE (table_id = '" + str(table_id) + "' AND name = '" + column_name + "' AND confirmed == 0)"
        self.log(sql)
        result = self.conn.execute(sql).fetchall()
        if len(result) != 0:
            # Major changes in columns should result in step up of table version,
            # which causes drop the table in case of database reuse
            assert(result[0]['type'] == column_type)
            assert(result[0]['non_zero'] == non_zero)
            sql = "UPDATE __columns__ SET confirmed = 1 WHERE (table_id = '" + str(table_id) + "' AND name = '" + column_name + "')"
            self.log(sql)
            self.conn.execute(sql)
            return False       
        
        sql = "ALTER TABLE '" + table_name + "' ADD COLUMN '" + column_name + "' " + column_type
        self.log(sql)
        self.conn.execute(sql)
        sql = "SELECT id FROM __tables__ WHERE (name = '" + table_name + "')"
        self.log(sql)
        table_id = next(self.conn.execute(sql))['id']
        sql = "INSERT INTO __columns__ (name, type, table_id, non_zero, confirmed) VALUES ('" + column_name + "', '" + column_type + "', '" + str(table_id) + "', '" + str(int(non_zero)) + "', 1)"
        self.log(sql)
        self.conn.execute(sql)
        return True        

    def iterate_columns(self, table_name):
        sql = "SELECT id FROM __tables__ WHERE (name = '" + table_name + "')"
        self.log(sql)
        table_id = next(self.conn.execute(sql))['id']
        sql = "SELECT * FROM __columns__ WHERE (table_id = '" + str(table_id) + "' AND confirmed = 1)"
        self.log(sql)
        result = self.conn.execute(sql).fetchall()
        for row in result:
            yield self.ColumnData(int(row["id"]), str(row["name"]), str(row["type"]), bool(row["non_zero"]))

    def check_column(self, table_name, column_name):
        sql = "SELECT id FROM __tables__ WHERE (name = '" + table_name + "')"
        self.log(sql)
        table_id = next(self.conn.execute(sql))['id']
        sql = "SELECT * FROM __columns__ WHERE (table_id = '" + str(table_id) + "' AND name = '" + column_name + "' AND confirmed = 1)"
        self.log(sql)
        result = self.conn.execute(sql).fetchall()
        if len(result) == 0:
            return False
        return True
    
    def create_tag(self, tag_name):
        assert(self.read_only == False)
        
        sql = "SELECT * FROM __tags__ WHERE (name = '" + tag_name + "' AND confirmed == 0)"
        self.log(sql)
        result = self.conn.execute(sql).fetchall()
        if len(result) != 0:
            sql = "UPDATE __tags__ SET confirmed = 1 WHERE (name = '" + tag_name + "')"
            self.log(sql)
            self.conn.execute(sql)
            return        
        
        sql = "INSERT INTO __tags__ (name, confirmed) VALUES ('" + tag_name + "', 1)"
        self.log(sql)
        self.conn.execute(sql)        

    def iterate_tags(self):
        sql = "SELECT * FROM __tags__ WHERE (confirmed = 1)"
        self.log(sql)
        result = self.conn.execute(sql).fetchall()
        for row in result:
            yield self.TagData(int(row["id"]), str(row["name"]))

    def check_tag(self, tag_name):
        sql = "SELECT * FROM __tags__ WHERE (name = '" + tag_name + "' AND confirmed = 1)"
        self.log(sql)
        result = self.conn.execute(sql).fetchall()
        if len(result) == 0:
            return False
        return True

    # TODO activate usage of tags
    def create_file(self, path, checksum):
        assert(self.read_only == False)
        path = self.InternalPathUtils().normalize_path(path)

        if self.is_cloned == True:
            sql = "SELECT * FROM __files__ WHERE (path = '" + path + "')"
            self.log(sql)
            result = self.conn.execute(sql).fetchall()
            if len(result) != 0:
                if result[0]['checksum'] == checksum:
                    old_id = result[0]['id']
                    sql = "UPDATE __files__ SET confirmed = 1 WHERE (id = " + str(old_id) +")"
                    self.log(sql)
                    self.conn.execute(sql)
                    return (old_id, False)
                else:
                    self.InternalCleanUpUtils().clean_up_file(self, result[0]['id'])
        
        sql = "INSERT OR REPLACE INTO __files__ (path, checksum, confirmed) VALUES (?, ?, 1)"
        column_data = [path, checksum]
        self.log(sql + " /with arguments: " + str(column_data))
        cur = self.conn.cursor()
        cur.execute(sql, column_data)
        self.InternalPathUtils().update_dirs(self, path=path)
        return (cur.lastrowid, True)
    
    def iterate_dircontent(self, path, include_subdirs = True, include_subfiles = True):
        self.InternalPathUtils().update_dirs(self)
        path = self.InternalPathUtils().normalize_path(path)
        cur_head = self.dirs
        valid = True
        if path != "":
            for head in self.InternalPathUtils().iterate_heads(path):
                if head not in list(cur_head.keys()):
                    # non existing directory
                    valid = False
                else:
                    cur_head = cur_head[head]
            basename = os.path.basename(path)
            if basename not in list(cur_head.keys()) or cur_head[basename] == None:
                # do not exist or points to the file
                valid = False
            else:
                cur_head = cur_head[basename]
        if valid == True:
            for elem in list(cur_head.keys()):
                if include_subdirs == True and cur_head[elem] != None:
                    yield elem
                if include_subfiles == True and cur_head[elem] == None:
                    yield elem

    def check_file(self, path):
        return self.get_file(path) != None

    def check_dir(self, path):
        for each in self.iterate_dircontent(path):
            each = each # used
            return True # there is at least one item
        return False

    def get_file(self, path):
        path = self.InternalPathUtils().normalize_path(path)
        result = self.select_rows("__files__", filters = [("path", "=", path), ("confirmed", "=", 1)])
        if len(result) == 0:
            return None
        assert(len(result) == 1)
        return self.FileData(result[0]['id'], result[0]['path'], result[0]['checksum'])

    def iterate_files(self, path_like = None):
        for row in self.select_rows('__files__', path_like=path_like, filters=[('confirmed','=','1')]): 
            yield self.FileData(row['id'], row['path'], row['checksum'])

    def create_region(self, file_id, region_id, name, begin, end, line_begin, line_end, cursor, group, checksum):
        assert(self.read_only == False)
        sql = "INSERT OR REPLACE INTO __regions__ (file_id, region_id, name, begin, end, line_begin, line_end, cursor, group_id, checksum) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        column_data = [file_id, region_id, name, begin, end, line_begin, line_end, cursor, group, checksum]
        self.log(sql + " /with arguments: " + str(column_data))
        cur = self.conn.cursor()
        cur.execute(sql, column_data)
        return cur.lastrowid
    
    def get_region(self, file_id, region_id):
        result = self.select_rows("__regions__", filters = [("file_id", "=", file_id), ("region_id", "=", region_id)])
        if len(result) == 0:
            return None
        return self.RegionData(result[0]['file_id'],
                               result[0]['region_id'],
                               result[0]['name'],
                               result[0]['begin'],
                               result[0]['end'],
                               result[0]['line_begin'],
                               result[0]['line_end'],
                               result[0]['cursor'],
                               result[0]['group_id'],
                               result[0]['checksum'])

    def iterate_regions(self, file_id):
        for each in self.select_rows("__regions__", filters = [("file_id", "=", file_id)]):
            yield self.RegionData(each['file_id'],
                                  each['region_id'],
                                  each['name'],
                                  each['begin'],
                                  each['end'],
                                  each['line_begin'],
                                  each['line_end'],
                                  each['cursor'],
                                  each['group_id'],
                                  each['checksum'])
    
    def create_marker(self, file_id, begin, end, group):
        assert(self.read_only == False)
        sql = "INSERT OR REPLACE INTO __markers__ (file_id, begin, end, group_id) VALUES (?, ?, ?, ?)"
        column_data = [file_id, begin, end, group]
        self.log(sql + " /with arguments: " + str(column_data))
        cur = self.conn.cursor()
        cur.execute(sql, column_data)
        return cur.lastrowid
    
    def iterate_markers(self, file_id):
        for each in self.select_rows("__markers__", filters = [("file_id", "=", file_id)]):
            yield self.MarkerData(each['file_id'],
                                  each['begin'],
                                  each['end'],
                                  each['group_id'])

    def add_row(self, table_name, file_id, region_id, array_data):
        assert(self.read_only == False)
        column_names = "'file_id'"
        column_values = "?"
        column_data = [file_id]
        if region_id != None:
            column_names += ", 'region_id'"
            column_values += ", ?"
            column_data.append(region_id)
        useful_data = 0
        for each in array_data:
            column_names +=  ", '" + each[0] + "'"
            column_values += ", ?"
            column_data.append(each[1])
            useful_data += 1
        if useful_data == 0:
            return
        sql = "INSERT OR REPLACE INTO '" + table_name + "' (" + column_names + ") VALUES (" + column_values + ")"
        self.log(sql + " /with arguments: " + str(column_data))
        cur = self.conn.cursor()
        cur.execute(sql, column_data)
        return cur.lastrowid

    def select_rows(self, table_name, path_like = None, column_names = [], filters = [], order_by = None, limit_by = None):
        safe_column_names = []
        for each in column_names:
            safe_column_names.append("'" + each + "'")
        return self.select_rows_unsafe(table_name, path_like = path_like,
                                       column_names = safe_column_names, filters = filters,
                                       order_by = order_by, limit_by = limit_by)

    def select_rows_unsafe(self, table_name, path_like = None, column_names = [], filters = [], 
                           group_by = None, order_by = None, limit_by = None):
        path_like = self.InternalPathUtils().normalize_path(path_like)
        if self.conn == None:
            return []

        table_stmt = "'" + table_name + "'"

        what_stmt = ", ".join(column_names)
        if len(what_stmt) == 0:
            what_stmt = "*"
        elif path_like != None and table_name != '__files__' and group_by == None:
            what_stmt += ", '__files__'.'path', '__files__'.'id'"
        inner_stmt = ""
        if path_like != None and table_name != '__files__':
            inner_stmt = " INNER JOIN '__files__' ON '__files__'.'id' = '" + table_name + "'.'file_id' "

        where_stmt = " "
        values = ()
        if len(filters) != 0:
            if filters[0][1] == 'IN':
                where_stmt = " WHERE (`" + filters[0][0] + "` " + filters[0][1] + " " + filters[0][2]
            else:    
                where_stmt = " WHERE (`" + filters[0][0] + "` " + filters[0][1] + " ?"
                values = (filters[0][2],)
            for each in filters[1:]:
                if each[1] == 'IN':
                    where_stmt += " AND `" + each[0] + "` " + each[1] + " " + each[2]
                else:
                    where_stmt += " AND `" + each[0] + "` " + each[1] + " ?"
                    values += (each[2], )
            if path_like != None:
                where_stmt += " AND '__files__'.'path' LIKE ?"
                values += (path_like, )
            where_stmt += ")"
        elif path_like != None:
            where_stmt = " WHERE '__files__'.'path' LIKE ?"
            values += (path_like, )
        
        group_stmt = ""
        if group_by != None:
            group_stmt = " GROUP BY (`" + group_by + "`)"

        order_stmt = ""
        if order_by != None:
            if order_by.startswith("-"):
                order_stmt = " ORDER BY (`" + order_by[1:] + "`) DESC "
            else:
                order_stmt = " ORDER BY (`" + order_by + "`) "

        limit_stmt = ""
        if limit_by != None:
            limit_stmt = " LIMIT " + str(limit_by)

        sql = "SELECT " + what_stmt + " FROM " + table_stmt + inner_stmt + where_stmt + group_stmt + order_stmt + limit_stmt
        self.log(sql + " /with arguments: " + str(values))
        return self.conn.execute(sql, values).fetchall()

    def get_row(self, table_name, file_id, region_id):
        selected = self.get_rows(table_name, file_id, region_id)
        # assures that only one row in database
        # if assertion happens, caller's intention is not right, use get_rows instead    
        assert(len(selected) == 0 or len(selected) == 1)
        if len(selected) == 0:
            return None
        return selected[0]

    def get_rows(self, table_name, file_id, region_id):
        filters = [("file_id", '=', file_id)]
        if region_id != None:
            filters.append(("region_id", '=', region_id))
        return self.select_rows(table_name, filters=filters)
    
    def aggregate_rows(self, table_name, path_like = None, column_names = None, filters = []):
        
        if column_names == None:
            column_names = []
            for column in self.iterate_columns(table_name):
                column_names.append(column.name)
                
        if len(column_names) == 0:
            # it is possible that a table does not have meanfull columns
            return {} 
        
        total_column_names = []
        for column_name in column_names:
            for func in ['max', 'min', 'avg', 'total', 'count']:
                total_column_names.append(func + "('" + table_name + "'.'" + column_name + "') AS " + "'" + column_name + "_" + func + "'")
             
        data = self.select_rows_unsafe(table_name, path_like = path_like, column_names = total_column_names, filters = filters)
        assert(len(data) == 1)
        result = {}
        for column_name in column_names:
            result[column_name] = {}
            for func in ['max', 'min', 'avg', 'total', 'count']:
                result[column_name][func] = data[0][column_name + "_" + func]
        return result
    
    def count_rows(self, table_name, path_like = None, group_by_column = None, filters = []):
        
        count_column_names = None
        
        if group_by_column != None:
            for column in self.iterate_columns(table_name):
                if group_by_column == column.name:
                    count_column_names = ["`" + group_by_column + "`", "COUNT(`" + group_by_column + "`)"]
                    break
        else:
            count_column_names = ["COUNT(*)"]
            
        if count_column_names == None:
            return []
             
        data = self.select_rows_unsafe(table_name, path_like = path_like, column_names = count_column_names,
                                       filters = filters, group_by = group_by_column)
        return data

    def log(self, sql):
        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
            pass
            logging.debug("[" + str(self.id) + "] Executing query: " + sql)
            traceback.print_stack()
        
