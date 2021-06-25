import 'dart:convert';

import 'package:diploma_project/session.dart';
import 'package:flutter/material.dart';

class Transaction {
  final String transactionDesc;
  final double amount;

  Transaction({this.transactionDesc, this.amount});

  factory Transaction.fromJson(Map<String, dynamic> json) {
    return Transaction(
      transactionDesc: json['description'],
      amount: double.parse(json['amount']),
    );
  }

  @override
  String toString() {
    return 'Transaction{transactionDesc: $transactionDesc, amount: $amount}';
  }
}

class TransactionDetailsWidget extends StatelessWidget {
  static const String _title = 'Transaction Details';

  @override
  Widget build(BuildContext context) {
    Map arguments = ModalRoute.of(context).settings.arguments as Map;

    if (arguments == null) {
      throw new Exception('Arguments not passed');
    }

    return Scaffold(
        appBar: AppBar(title: const Text(_title)),
        body: TransactionDetailsPage(arguments: arguments),
    );
  }
}

class TransactionDetailsPage extends StatefulWidget {
  final Map arguments;

  @override
  State<StatefulWidget> createState() =>
      TransactionDetailsPageState(arguments: arguments);

  TransactionDetailsPage({this.arguments});
}

class TransactionDetailsPageState extends State<TransactionDetailsPage> {
  final Map arguments;

  TransactionDetailsPageState({this.arguments});

  @override
  Widget build(BuildContext context) {
    return FutureBuilder(
      future: checkTransaction(arguments['data']),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.done) {
          return detailsWidget(context, snapshot.data);
        } else if (snapshot.hasError) {
          return Text(snapshot.error.toString());
        } else {
          return CircularProgressIndicator();
        }
      },
    );
  }

  Future checkTransaction(transactionId) async {
    print(transactionId);
    var response = await Session.get("/transactions/$transactionId");
    return response;
  }

  Widget detailsWidget(context, response) {
    if (response.statusCode == 200) {
      Transaction transaction = Transaction.fromJson(jsonDecode(response.body));
      return Container(
        child: Column(
          children: <Widget>[
            ListTile(
              title: Text('Amount: ${transaction.amount}'),
            ),
            Divider(
              height: 2.0,
            ),
            ListTile(
              title: Text('Description: ${transaction.transactionDesc}'),
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: <Widget>[
                RaisedButton(
                  child: Text("Accept"),
                  color: Colors.lightBlue,
                  textColor: Colors.white,
                  onPressed: () => {_accept(context)},
                )
              ],
            )
          ],
        ),
      );
    }
    return Text(response.body);
  }

  Future _accept(context) async {
    Session.headers["Content-Type"] = "application/json";
    print(Session.headers);
    var response = await Session.post("/transactions/accept",
        jsonEncode(<String, String>{'id': arguments['data']}));
    if (response.statusCode == 200) {
      Session.headers.remove('Content-Type');
      Navigator.pushReplacementNamed(context, '/account');
    } else {
      print('Error occurred');
      String em = response.body;
      print(em);
      Scaffold.of(context).showSnackBar(SnackBar(
        content: Text(em),
      ));
    }
  }
}
