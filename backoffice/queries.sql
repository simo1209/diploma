CREATE OR REPLACE FUNCTION is_payment(transaction_id integer) RETURNS BOOLEAN AS
$$
BEGIN
    RETURN EXISTS(SELECT transaction_type_id
                  FROM transactions
                           JOIN transaction_type ON transactions.transaction_type_id = transaction_type.id
                  WHERE transactions.id = transaction_id
                    AND transaction_type.type = 'payment');
END
$$
    LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS handle_funds_transfer_trigger ON transactions;

CREATE TRIGGER handle_funds_transfer_trigger
    BEFORE INSERT
    ON transactions
    FOR EACH ROW
EXECUTE FUNCTION handle_funds_transfer();

CREATE OR REPLACE FUNCTION handle_funds_transfer() RETURNS TRIGGER
    LANGUAGE plpgsql
AS
$$
BEGIN
    IF NOT is_payment(new.id) THEN
        IF new.buyer_id IS NOT NULL THEN
            new.transaction_type_id = (SELECT id FROM transaction_type WHERE type = 'withdraw');
            UPDATE accounts SET balance = balance - new.amount WHERE id = new.buyer_id;
        ELSIF new.seller_id IS NOT NULL THEN
            new.transaction_type_id = (SELECT id FROM transaction_type WHERE type = 'deposit');
            UPDATE accounts SET balance = balance + new.amount WHERE id = new.seller_id;
        END IF;
        new.transaction_status_id = (SELECT id FROM transaction_status WHERE status = 'completed');
    END IF;
    IF new.status_update_time IS NULL THEN
        new.status_update_time = NOW();
    END IF;
    RETURN new;
END;
$$;

DROP TRIGGER IF EXISTS handle_payment_trigger ON transactions;

CREATE TRIGGER handle_payment_trigger
    BEFORE UPDATE
    ON transactions
    FOR EACH ROW
EXECUTE FUNCTION handle_payment_update();

CREATE OR REPLACE FUNCTION handle_payment_update() RETURNS TRIGGER
    LANGUAGE plpgsql
AS
$$
BEGIN
    IF is_payment(new.id) THEN
        IF new.buyer_id IS NOT NULL AND new.seller_id IS NOT NULL THEN
            IF new.status_update_time IS NULL THEN
                new.status_update_time = NOW();
            END IF;

            UPDATE accounts SET balance = balance + new.amount WHERE accounts.id = new.seller_id;
            UPDATE accounts SET balance = balance - new.amount WHERE accounts.id = new.buyer_id;
            new.transaction_status_id = (SELECT id FROM transaction_status WHERE status = 'completed');

        END IF;
    END IF;

    RETURN new;
END;
$$;


CREATE OR REPLACE FUNCTION is_completed(transaction_id integer) RETURNS BOOLEAN AS
$$
BEGIN
    RETURN EXISTS(SELECT transaction_type_id
                  FROM transactions
                           JOIN transaction_status ON transactions.transaction_status_id = transaction_status.id
                  WHERE transactions.id = transaction_id
                    AND transaction_status.status = 'completed');
END
$$
    LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS transaction_history(account_id integer);


DROP VIEW transaction_history;

DROP VIEW IF EXISTS transaction_inquiry;


CREATE OR REPLACE VIEW transaction_inquiry AS
SELECT t.id,
       t.creation_time::timestamp(0),
       t_s.status,
       t_t.type,
       t.amount,
       t.description,
       b.first_name AS buyer_first_name,
       b.last_name  AS buyer_last_name,
       s.first_name AS seller_first_name,
       s.last_name  AS seller_last_name
FROM transactions t
         JOIN transaction_status t_s ON t.transaction_status_id = t_s.id
         JOIN transaction_type t_t ON t_t.id = t.transaction_type_id
         JOIN accounts b ON b.id = t.buyer_id
         JOIN accounts s ON s.id = t.seller_id;


SELECT _date,
       _counterparty_first_name,
       _counterparty_last_name,
       _description,
       _credit,
       _debit,
       SUM(_amount) OVER ( ORDER BY _date ) AS _balance
FROM (SELECT t.creation_time AS _date,
             b.first_name    AS _counterparty_first_name,
             b.last_name     AS _counterparty_last_name,
             t.description   AS _description,
             t.amount        AS _credit,
             0               AS _debit,
             t.amount        AS _amount
      FROM transactions t
               LEFT JOIN accounts b ON t.buyer_id = b.id
               LEFT JOIN accounts s ON t.seller_id = s.id
      WHERE t.seller_id = 9
      UNION ALL
      SELECT t.creation_time AS _date,
             s.first_name    AS _counterparty_first_name,
             s.last_name     AS _counterparty_last_name,
             t.description   AS _description,
             0               AS _credit,
             t.amount        AS _debit,
             -t.amount       AS _amount
      FROM transactions t
               LEFT JOIN accounts b ON t.buyer_id = b.id
               LEFT JOIN accounts s ON t.seller_id = s.id
      WHERE t.buyer_id = 9) th ORDER BY _date;
