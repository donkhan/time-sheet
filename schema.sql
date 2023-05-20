DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS ts;
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username varchar(200) UNIQUE NOT NULL,
  password varchar(200) NOT NULL,
  company  varchar(200),
  role varchar(200)
);

insert into user values (1,"Kamil","a","AGNI","employee");
insert into user values (3,"Eial","a","AGNI","employee");
insert into user values (2,"Kaushik","a","AGNI","employer");

insert into user values (1,"Kamil","a","Rizq","employee");
insert into user values (3,"Anwar","a","Rizq","employee");
insert into user values (4,"Peer","a","Rizq","employee");
insert into user values (2,"Ali","a","Rizq","employer");


create table ts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date date,
    content text,
    user_id integer,
    hours integer,
    status integer,
    type text
);


