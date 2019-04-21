/* script to create db tables */
create table bank
(
    bank_id integer PRIMARY KEY ,
    bank_name text
);

create table account_type
(
    account_type_id INTEGER PRIMARY KEY,
    DESCRIPTION text
);

create table account
(
    account_id integer PRIMARY KEY ,
    account_number integer not null,
    account_type_id integer,
    bank_id integer,
    first_balance real,
    first_balance_date date,
    FOREIGN KEY (bank_id) REFERENCES bank(bank_id),
    FOREIGN KEY (account_id) REFERENCES account_type(account_type_id)
);

create table card_type
(
    card_type_id INTEGER PRIMARY KEY,
    DESCRIPTION text
);

create table card
(
    card_id INTEGER PRIMARY KEY,
    card_number INTEGER not null UNIQUE ,
    account_id INTEGER,
    activated BOOLEAN,
    creadit_amount REAL,
    FOREIGN KEY (account_id) REFERENCES account(account_id)
);

create table transaction_type
(
    transaction_type_id INTEGER PRIMARY KEY,
    DESCRIPTION text
);

create table bank_category
(
    b_category_id INTEGER PRIMARY KEY,
    DESCRIPTION text
);

create table personal_category(
    p_category_id INTEGER PRIMARY KEY,
    DESCRIPTION text
);

create table transactions
(
    transaction_id INTEGER PRIMARY KEY,
    transaction_date date,
    post_date date,
    DESCRIPTION text,
    ref_number INTEGER,
    account_number INTEGER,
    amount real,
    b_category_id integer,
    p_category_id integer,
    FOREIGN KEY (account_number) REFERENCES card(card_number),
    FOREIGN KEY (b_category_id) REFERENCES bank_category(b_category_id),
    FOREIGN KEY (p_category_id) REFERENCES personal_category(p_category_id)
);