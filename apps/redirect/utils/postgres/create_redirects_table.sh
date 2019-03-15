#!/bin/bash
su will -c 'psql redirect_usage'
CREATE TABLE redirects (
  id         char(36) PRIMARY KEY,
  ts         integer,
  location   varchar,
  history    varchar[]
);
