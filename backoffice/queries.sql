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

        ELSIF new.seller_id IS NOT NULL THEN
            new.transaction_type_id = (SELECT id FROM transaction_type WHERE type = 'deposit');

        end if;
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

SELECT is_payment(50229);

CREATE OR REPLACE FUNCTION transaction_history(account_id integer)
    RETURNS TABLE
            (
                date         TIMESTAMP,
                counterparty TEXT,
                description  TEXT,
                debit        NUMERIC,
                credit       NUMERIC,
                balance      NUMERIC
            )
AS
$$
BEGIN
    RETURN QUERY
        SELECT t.creation_time                        AS date,
               CONCAT(s.first_name, ' ', s.last_name) AS counterparty,
               t.description                          AS description,
               t.amount                               AS debit,
               NULL                                   AS credit,
               b.balance - t.amount                   AS balance
        FROM transactions AS t
                 LEFT JOIN accounts b on t.buyer_id = b.id
                 LEFT JOIN accounts s on t.seller_id = s.id
        WHERE t.buyer_id = account_id
        UNION ALL
        SELECT t.creation_time                        AS date,
               CONCAT(b.first_name, ' ', b.last_name) AS counterparty,
               t.description                          AS description,
               NULL                                   AS debit,
               t.amount                               AS credit,
               s.balance + t.amount                   AS balance

        FROM transactions AS t
                 LEFT JOIN accounts b on t.buyer_id = b.id
                 LEFT JOIN accounts s on t.seller_id = s.id
        WHERE t.seller_id = account_id;
END;
$$ LANGUAGE PLPGSQL;


CREATE TABLE transactions_history
(
    date         TIMESTAMP,
    counterparty TEXT,
    description  TEXT,
    debit        NUMERIC,
    credit       NUMERIC,
    balance      NUMERIC,
    user_id      INTEGER
);