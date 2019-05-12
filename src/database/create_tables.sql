/* script to create db tables */
DROP table if exists transactions;
DROP table if exists personal_category;
DROP table if exists bank_category;
DROP table if exists transaction_type;
DROP table if exists card;
DROP table if exists card_type;
DROP table if exists account;
DROP table if exists account_type;
DROP table if exists bank;

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
    card_type_id INTEGER,
    card_number INTEGER not null UNIQUE ,
    account_id INTEGER,
    activated BOOLEAN,
    creadit_amount REAL,
    FOREIGN KEY (account_id) REFERENCES account(account_id),
    FOREIGN KEY (card_type_id) REFERENCES card_type(card_type_id)
);

create table transaction_type
(
    transaction_type_id INTEGER PRIMARY KEY,
    bank_id INTEGER,
    DESCRIPTION text,
    FOREIGN KEY (bank_id) REFERENCES bank(bank_id)
);

-- table for category definition from bank
create table bank_category
(
    b_category_id INTEGER PRIMARY KEY,
    bank_id INTEGER,
    DESCRIPTION text
);

-- table for personal category definition
create table personal_category(
    p_category_id INTEGER PRIMARY KEY,
    DESCRIPTION text,
    COMMENT text
);

create table transactions
(
    transaction_id INTEGER PRIMARY KEY,
    trans_type_id INTEGER ,
    transaction_date date,
    post_date date,
    DESCRIPTION text,
    ref_number INTEGER,
    account_number INTEGER,
    amount real,
    b_category_id integer,
    p_category_id integer,
    overwrite_p_category_id integer,
    FOREIGN KEY (account_number) REFERENCES card(card_number),
    FOREIGN KEY (b_category_id) REFERENCES bank_category(b_category_id),
    FOREIGN KEY (p_category_id) REFERENCES personal_category(p_category_id),
    FOREIGN KEY (overwrite_p_category_id) REFERENCES personal_category(p_category_id),
    FOREIGN KEY (trans_type_id) REFERENCES transaction_type(transaction_type_id)
);