-- $Id$

create table webcams (
       webcam_idx int primary key,
       shortname varchar,
       url varchar,
       directory varchar,
       enabled boolean default 't'
);

create sequence webcam_ids;

create table images (
       image_idx int primary key,
       webcam_idx int references webcams,
       servertime timestamp with time zone,
       lastmodified timestamp with time zone,
       filename varchar,
       red_mean float,
       green_mean float,
       blue_mean float,
       red_stddev float,
       green_stddev float,
       blue_stddev float,
       num_colours int,
       signature varchar
);

create sequence image_ids;
create index images_by_signature on images using btree (signature);

create table locations (
       location_idx int primary key,
       longitude float,
       latitude float
);

create sequence location_ids;

create table days (
       location_idx int references locations,
       daynumber int,
       sunrise timestamp with time zone, -- probably can be NULL, I think
       sunset timestamp with time zone --  likewise
);

