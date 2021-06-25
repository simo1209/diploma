from time import perf_counter as pc
from backoffice import db
from backoffice.models import Account, Address
from statistics import mean


first_names = ['John', 'William', 'Frank', 'George', 'Harry', 'Joe', 'Lee', 'Jack', 'Alex', 'Norman']

lasT_names = ['John', 'William', 'Frank', 'George', 'Harry', 'Joe', 'Lee', 'Jack', 'Alex', 'Norman']

emails = {}

address = Address(
    'Street 1',
    'Street 2',
    'Sofia',
    'Bulgaria',
    1234
)
db.session.add(address)

account_creating = []
account_inserting = []

n = 500
for i in range(n):
    for last_name in lasT_names:
        last_name = last_name+'s'
        for first_name in first_names:
            # print('Creating account')
            start = pc()
            email = first_name.lower() + last_name.lower()
            if emails.get(email):
                emails[email]+=1
            else:
                emails[email]=1

            full_email = "{}{:03}@mail.com".format(email, emails[email])
            # print(full_email.format(email, emails[email]))

            account = Account(
                first_name=first_name,
                last_name=last_name,
                email=full_email,
                password=full_email,
                phone='0123456789',
                UCN='0123456789',
                address=address
            )
            end = pc()
            # print('Created account')
            # print(end - start)
            account_creating.append(end-start)
            # print('Inserting account')
            start = pc()
            db.session.add(account)
            db.session.commit()
            end = pc()
            # print('Inserted account')
            # print(end - start)
            account_inserting.append(end-start)
            # print(first_name, last_name)
    print(i,'/', n)


print('Total for creating {} accounts: '.format(n*100), sum(account_creating))
print('Mean for account creating: ',mean(account_creating))

print('Total for inserting {} accounts: '.format(n*100), sum(account_inserting))
print('Mean for account inserting: ',mean(account_inserting))

print('Total time: ', sum(account_creating) + sum(account_inserting))

# FIRST
# Total for creating 100 accounts:  21.914944199988895
# Mean for account creating:  0.21914944199988895
# Total for inserting 100 accounts:  1.0832933000019693
# Mean for account inserting:  0.010832933000019694
# Total time:  22.998237499990864

# SECOND
# Total for creating 100 accounts:  0.015137200000026496
# Mean for account creating:  0.00015137200000026497
# Total for inserting 100 accounts:  0.3626991999990423
# Mean for account inserting:  0.0036269919999904233
# Total time:  0.3778363999990688


# LAST
# Total for creating 50000 accounts:  6.339719899908232
# Mean for account creating:  0.00012679439799816465
# Total for inserting 50000 accounts:  155.86290329995973
# Mean for account inserting:  0.0031172580659991943
# Total time:  162.20262319986796