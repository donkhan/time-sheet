DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS ts;
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  company  text,
  role text
);

insert into user values (1,"Kamil","a","AGNI","employee");
insert into user values (3,"Eial","a","AGNI","employee");
insert into user values (2,"Kaushik","a","AGNI","employer");

create table ts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date date,
    content text,
    user_id id,
    hours integer
);


