DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS ts;
DROP TABLE IF EXISTS company;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username varchar(200) NOT NULL,
  password varchar(200) NOT NULL,
  companyId  int,
  role varchar(200)
);
create table company (id int, name varchar(200), imgUrl varchar(200), url varchar(200));

insert into user values (1,"Kamil","a","employee",2);
insert into user values (2,"Kaushik","a","employer",2);
insert into user values (3,"Eial","a","employee",2);

insert into user values (4,"Kamil Khan","a","employee",1);
insert into user values (5,"Anwar","a","employee",1);
insert into user values (6,"Peer","a","employee",1);
insert into user values (7,"Ali","a","employer",1);

insert into company values (1, "Rizq Solutions", 'https://rizqsolutions.co.uk/wp-content/uploads/2022/09/cropped-Rizq-Logo-No-BG-e1663847241416-3.png',
                                'https://rizqsolutions.co.uk/');

insert into company values (2, "AGNI Technologies", 'https://agnitechnologies.com/wp-content/uploads/2022/03/PNG-logo.png',
                                'https://agnitechnologies.com/');

create table ts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date date,
    content text,
    user_id integer,
    hours integer,
    status integer,
    type text
);


