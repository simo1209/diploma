import 'dart:convert';

import 'package:diploma_project/session.dart';

import 'package:flutter/material.dart';
import 'package:http/http.dart';
import 'package:qrscan/qrscan.dart' as scanner;


class Account {
  final String firstName;
  final String lastName;
  final String email;
  final double balance;

  Account({this.firstName, this.lastName, this.email, this.balance});

  factory Account.fromJson(Map<String, dynamic> json) {
    return Account(
      firstName: json['first_name'],
      lastName: json['last_name'],
      email: json['email'],
      balance: double.parse(json['balance']),
    );
  }

  @override
  String toString() {
    return 'Account{firstName: $firstName, lastName: $lastName, email: $email, balance: $balance}';
  }
}

class AccountWidget extends StatelessWidget {
  static const String _title = 'Your Account';

  @override
  Widget build(BuildContext context) {
      return Scaffold(
        appBar: AppBar(title: const Text(_title)),
        body: AccountPage(),
    );
  }
}

class AccountPage extends StatefulWidget {
  @override
  State<StatefulWidget> createState() => AccountPageState();
}

class AccountPageState extends State<AccountPage> {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        FutureBuilder(
          future: getAccountInformation(),
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.done) {
              return accountDetailsWidget(context, snapshot.data);
            } else if (snapshot.hasError) {
              return Text(snapshot.error.toString());
            } else {
              return CircularProgressIndicator();
            }
          },
        ),
        Column(
          children: [
            RaisedButton(
              child: Text('Scan Code', style: TextStyle(fontSize: 24)),
              onPressed: _scan,
              color: Colors.lightBlue,
              textColor: Colors.white,
            ),
            RaisedButton(
              child: Text('Create Code', style: TextStyle(fontSize: 24)),
              onPressed: (){
                Navigator.of(context).pushNamed('/transactionCreate');
              },
            ),
            RaisedButton(
              child: Text('Log Out', style: TextStyle(fontSize: 24)),
              onPressed: () => _logout(context),
            ),
          ],
        )
      ],
    );
  }

  Future _logout(context) async {

    var response = await Session.get('/logout');

    if (response.statusCode == 200){
      Session.headers.remove('cookie');
      Navigator.popUntil(context, ModalRoute.withName('/'));
    }
  }

  Future getAccountInformation() async {
    var response = await Session.get("/account");
    return response;
  }

  Widget accountDetailsWidget(BuildContext context, Response data) {
    if (data.statusCode == 200) {
      Account account = Account.fromJson(jsonDecode(data.body));
      return Column(
        children: <Widget>[
          ListTile(
            title: Text('${account.firstName} ${account.lastName}'),
          ),
          Divider(
            height: 2.0,
          ),
          ListTile(
            title: Text('Email: ${account.email}'),
          ),
          Divider(
            height: 2.0,
          ),
          ListTile(
            title: Text('Balance: ${account.balance}'),
          ),
          Divider(
            height: 2.0,
          ),
        ],
      );
    }
    return Text(data.body);
  }

  Future _scan() async {
    print('Scanning');
    String data = await scanner.scan(); // Read the QR encoded string
    print('Scanned');
    print(data);
    if (data.indexOf('QRPayment:') == -1){
      throw Exception('QR Code is not recognized');
    }
    var id = data.substring(10);
    print(id);
    Navigator.of(context).pushNamed('/transactionDetails', arguments: {'data': id});
  }
}