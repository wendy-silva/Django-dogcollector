CREATE DATABASE dogcollector;

CREATE USER dog_admin WITH PASSWORD 'password';

GRANT ALL PRIVILEGES ON DATABASE dogcollector TO dog_admin;