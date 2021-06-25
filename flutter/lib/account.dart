import 'dart:convert';

import 'package:diploma_project/session.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart';
import 'package:permission_handler/permission_handler.dart';
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
    bool isScreenWide =
        MediaQuery.of(context).size.width >= MediaQuery.of(context).size.height;

    return Column(
      children: [
        FutureBuilder(
          future: getAccountInformation(),
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.done && snapshot.hasData) {
              return accountDetailsWidget(context, snapshot.data);
            } else if (snapshot.hasError) {
              return Text(snapshot.error.toString());
            } else {
              return CircularProgressIndicator();
            }
          },
        ),
        Flex(
          direction: isScreenWide ? Axis.horizontal : Axis.vertical,
          children: [
            RaisedButton(
              child: Text('Scan Code', style: TextStyle(fontSize: 24)),
              onPressed: _scan,
              color: Colors.lightBlue,
              textColor: Colors.white,
            ),
            RaisedButton(
              child: Text('Create Code', style: TextStyle(fontSize: 24)),
              onPressed: () {
                Navigator.of(context).pushNamed('/transactionCreate');
              },
            ),
            RaisedButton(
              child: Text('Log Out', style: TextStyle(fontSize: 24)),
              onPressed: () => _logout(context),
            ),
            RaisedButton(
              child: Text('Transaction History', style: TextStyle(fontSize: 24)),
              onPressed: () {
                Navigator.of(context).pushNamed('/history');
              },
            )
          ],
        )
      ],
    );
  }

  Future _logout(context) async {
    try {
      var response = await Session.get('/logout');

      if (response.statusCode == 302 || response.statusCode == 200) {
        Session.headers.remove('cookie');
        Navigator.pushReplacementNamed(context, '/');
      }
    } on Exception catch (_) {
      Scaffold.of(context).showSnackBar(SnackBar(
        content: Text("Couldn't connect to server"),
      ));
    }
  }

  Future getAccountInformation() async {
    try {
      var response = await Session.get("/accounts/account");
      return response;
    } on Exception catch (_) {
      Scaffold.of(context).showSnackBar(SnackBar(
        content: Text("Couldn't connect to server"),
      ));
    }
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
    Map<Permission, PermissionStatus> statuses = await [
      Permission.camera,
      Permission.storage,
    ].request();

    if (statuses[Permission.camera].isGranted &&
        statuses[Permission.storage].isGranted) {
      print('Scanning');
      String data = await scanner.scan(); // Read the QR encoded string
      print('Scanned');
      print(data);
      if (data.indexOf('QRPayment:') == -1) {
        Scaffold.of(context).showSnackBar(SnackBar(
          content: Text("QR Code is not recognized"),
        ));
      }
      var id = data.substring(10);
      print(id);
      Navigator.of(context)
          .pushNamed('/transactionDetails', arguments: {'data': id});
    } else {
      Scaffold.of(context).showSnackBar(SnackBar(
        content: Text("Please grant permission"),
      ));
    }
  }
}
