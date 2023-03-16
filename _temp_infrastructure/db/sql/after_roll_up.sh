#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "postgres" --dbname "postgres" <<-EOSQL

    /*
     * Установить схему для внесения изменений
     */
    SET search_path TO sch_developer_profile;

    /*
     * Добавить используемые роли
     */
    INSERT INTO roles (name, description, created_at, updated_at, id) values ('space-owner', 'Владелец пространства', now(), now(), (uuid_in(md5(random()::text || clock_timestamp()::text)::cstring))) ON CONFLICT DO NOTHING;
    INSERT INTO roles (name, description, created_at, updated_at, id) values ('admin', 'Администратор', now(), now(), (uuid_in(md5(random()::text || clock_timestamp()::text)::cstring))) ON CONFLICT DO NOTHING;
    INSERT INTO roles (name, description, created_at, updated_at, id) values ('developer', 'Разработчик', now(), now(), (uuid_in(md5(random()::text || clock_timestamp()::text)::cstring))) ON CONFLICT DO NOTHING;
    INSERT INTO roles (name, description, created_at, updated_at, id) values ('tester', 'Тестировщик', now(), now(), (uuid_in(md5(random()::text || clock_timestamp()::text)::cstring))) ON CONFLICT DO NOTHING;

    /*
     * Добавить используемые пермишены
     */
    INSERT INTO permissions (code, description, id) values ('space-read', '', (uuid_in(md5(random()::text || clock_timestamp()::text)::cstring))) ON CONFLICT DO NOTHING;
    INSERT INTO permissions (code, description, id) values ('space-write', '', (uuid_in(md5(random()::text || clock_timestamp()::text)::cstring))) ON CONFLICT DO NOTHING;
    INSERT INTO permissions (code, description, id) values ('space-delete', '', (uuid_in(md5(random()::text || clock_timestamp()::text)::cstring))) ON CONFLICT DO NOTHING;
    INSERT INTO permissions (code, description, id) values ('space-user-read', '', (uuid_in(md5(random()::text || clock_timestamp()::text)::cstring))) ON CONFLICT DO NOTHING;
    INSERT INTO permissions (code, description, id) values ('space-user-write', '', (uuid_in(md5(random()::text || clock_timestamp()::text)::cstring))) ON CONFLICT DO NOTHING;
    INSERT INTO permissions (code, description, id) values ('space-user-add', '', (uuid_in(md5(random()::text || clock_timestamp()::text)::cstring))) ON CONFLICT DO NOTHING;
    INSERT INTO permissions (code, description, id) values ('space-user-delete', '', (uuid_in(md5(random()::text || clock_timestamp()::text)::cstring))) ON CONFLICT DO NOTHING;
    INSERT INTO permissions (code, description, id) values ('component-read', '', (uuid_in(md5(random()::text || clock_timestamp()::text)::cstring))) ON CONFLICT DO NOTHING;
    INSERT INTO permissions (code, description, id) values ('component-create', '', (uuid_in(md5(random()::text || clock_timestamp()::text)::cstring))) ON CONFLICT DO NOTHING;
    INSERT INTO permissions (code, description, id) values ('component-delete', '', (uuid_in(md5(random()::text || clock_timestamp()::text)::cstring))) ON CONFLICT DO NOTHING;
    INSERT INTO permissions (code, description, id) values ('component-write', '', (uuid_in(md5(random()::text || clock_timestamp()::text)::cstring))) ON CONFLICT DO NOTHING;

    /*
     * Добавить связки роль --> пермишен
     */
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('space-owner')), (select id from permissions where code in ( 'space-read'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('space-owner')), (select id from permissions where code in ( 'space-write'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('space-owner')), (select id from permissions where code in ( 'space-delete'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('space-owner')), (select id from permissions where code in ( 'space-user-read'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('space-owner')), (select id from permissions where code in ( 'space-user-write'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('space-owner')), (select id from permissions where code in ( 'space-user-add'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('space-owner')), (select id from permissions where code in ( 'space-user-delete'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('space-owner')), (select id from permissions where code in ( 'component-read'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('space-owner')), (select id from permissions where code in ( 'component-create'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('space-owner')), (select id from permissions where code in ( 'component-delete'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('space-owner')), (select id from permissions where code in ( 'component-write'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('admin')), (select id from permissions where code in ( 'space-read'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('admin')), (select id from permissions where code in ( 'space-write'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('admin')), (select id from permissions where code in ( 'space-user-read'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('admin')), (select id from permissions where code in ( 'space-user-write'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('admin')), (select id from permissions where code in ( 'space-user-add'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('admin')), (select id from permissions where code in ( 'space-user-delete'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('admin')), (select id from permissions where code in ( 'component-read'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('admin')), (select id from permissions where code in ( 'component-create'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('admin')), (select id from permissions where code in ( 'component-delete'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('admin')), (select id from permissions where code in ( 'component-write'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('developer')), (select id from permissions where code in ('space-read'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('developer')), (select id from permissions where code in ('space-write'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('developer')), (select id from permissions where code in ('space-user-read'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('developer')), (select id from permissions where code in ('component-read'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('developer')), (select id from permissions where code in ('component-write'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('tester')), (select id from permissions where code in ('space-read'));
    INSERT INTO roles_permissions (role_id, permission_id) select (select id from roles where roles.name in ('tester')), (select id from permissions where code in ('component-read'));

EOSQL