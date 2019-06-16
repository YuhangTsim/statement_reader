INSERT INTO transactions (trans_type_id, transaction_date, post_date, DESCRIPTION, ref_number, account_number, amount)
SELECT
	tt.transaction_type_id,
	rt.transaction_date,
	rt.post_date,
	rt.DESCRIPTION,
	rt.ref_number,
	rt.account_number,
	rt.amount
FROM
	staging_transactions rt
	JOIN transaction_type tt ON rt.trans_type = tt.DESCRIPTION;

INSERT INTO transaction_description (DESCRIPTION)
SELECT 
    DISTINCT DESCRIPTION
FROM
	staging_transactions
WHERE
	DESCRIPTION NOT in(
		SELECT DESCRIPTION FROM transaction_description);

DELETE FROM staging_transactions;