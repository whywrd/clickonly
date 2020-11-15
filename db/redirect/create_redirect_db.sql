CREATE TABLE redirects (
    id         char(36) PRIMARY KEY,
    ts         integer,
    location   varchar,
    history    varchar[]
);


CREATE TABLE location (
    id         SERIAL PRIMARY KEY,
    ts         integer,
    location   char(255),
    redirect   char(2000)
)
