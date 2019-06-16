-- insert default setting into db after init

INSERT INTO bank (bank_id, bank_name) values (?, ?);
INSERT INTO account_type (account_type_id, DESCRIPTION) values (?, ?);
INSERT INTO card_type (card_type_id, DESCRIPTION) values (?, ?);
INSERT INTO transaction_type (transaction_type_id, DESCRIPTION) values (?, ?);

-- insert personal setting into db after init
INSERT INTO personal_category (p_category_id, DESCRIPTION, COMMENT) values (?, ?, ?);