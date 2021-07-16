create database LoremServer;
create user 'user'@'localhost' identified by '3325111';
grant all privileges on LoremServer.* to 'user'@'localhost';
flush privileges;

