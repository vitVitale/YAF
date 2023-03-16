--liquibase formatted sql

--changeset Vitaly V:5
insert into person (firstname, lastname, state, username) values ('Elena', 'Truehanovich', 'Y', 'mouse_1');
insert into person (firstname, lastname, state, username) values ('Vitaly', 'Vasilyuk', 'Y', 'mouse_2');
