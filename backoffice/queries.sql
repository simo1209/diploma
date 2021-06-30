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
            UPDATE accounts SET balance = balance - new.amount;
        ELSIF new.seller_id IS NOT NULL THEN
            new.transaction_type_id = (SELECT id FROM transaction_type WHERE type = 'deposit');
            UPDATE accounts SET balance = balance + new.amount;
        end if;
        new.transaction_status_id = (SELECT id FROM transaction_status WHERE status = 'completed');
    END IF;
    IF new.status_update_time IS NULL THEN
        new.status_update_time = NOW();
    END IF;
    RETURN new;
END;
$$;

CREATE TRIGGER handle_payment_trigger
    BEFORE UPDATE
    ON transactions
    FOR EACH ROW
EXECUTE FUNCTION handle_payment();

CREATE OR REPLACE FUNCTION handle_payment() RETURNS TRIGGER
    LANGUAGE plpgsql
AS
$$
BEGIN
    IF is_payment(new.id) THEN
        IF new.buyer_id IS NOT NULL AND new.seller_id IS NOT NULL THEN
            UPDATE accounts SET balance = balance + new.amount WHERE accounts.id = new.seller_id;
            UPDATE accounts SET balance = balance - new.amount WHERE accounts.id = new.buyer_id;
        END IF;
        new.transaction_status_id = (SELECT id FROM transaction_status WHERE status = 'completed');
    END IF;
    new.status_update_time = NOW();
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

DROP FUNCTION transaction_history(account_id integer);

CREATE OR REPLACE FUNCTION transaction_history(account_id integer)
    RETURNS TABLE
            (
                date         TIMESTAMP,
                counterparty TEXT,
                description  TEXT,
                credit       NUMERIC,
                debit        NUMERIC,
                balance      NUMERIC
            )
AS
$$
BEGIN
    RETURN QUERY
        SELECT _date,
               _counterparty,
               _description,
               _credit,
               _debit,
               SUM(_amount) OVER ( ORDER BY _date ) as _balance
        FROM (SELECT t.status_update_time                                          AS _date,
                     COALESCE(b.first_name || ' ' || b.last_name, 'Cash Register') as _counterparty,
                     t.description                                                 as _description,
                     t.amount                                                      as _credit,
                     0                                                             as _debit,
                     t.amount                                                      as _amount
              FROM transactions t
                       LEFT JOIN accounts b on t.buyer_id = b.id
                       LEFT JOIN accounts s on t.seller_id = s.id
              WHERE t.seller_id = account_id
              UNION ALL
              SELECT t.status_update_time                                          AS _date,
                     COALESCE(s.first_name || ' ' || s.last_name, 'Cash Register') as _counterparty,
                     t.description                                                 as _description,
                     0                                                             as _credit,
                     t.amount                                                      AS _debit,
                     -t.amount                                                     as _amount
              FROM transactions t
                       LEFT JOIN accounts b on t.buyer_id = b.id
                       LEFT JOIN accounts s on t.seller_id = s.id
              WHERE t.buyer_id = account_id) ss
        ORDER BY _date;
END;
$$ LANGUAGE PLPGSQL;

DROP VIEW transaction_inquiry;
CREATE OR REPLACE VIEW transaction_inquiry AS
SELECT t.id,
       t.status_update_time::timestamp(0),
       t_s.status,
       t_t.type,
       t.amount,
       t.description,
       b.first_name || ' ' || b.last_name AS buyer_name,
       s.first_name || ' ' || s.last_name AS seller_name
FROM transactions t
         JOIN transaction_status t_s ON t.transaction_status_id = t_s.id
         JOIN transaction_type t_t ON t_t.id = t.transaction_type_id
         JOIN accounts b ON b.id = t.buyer_id
         JOIN accounts s ON s.id = t.seller_id;

