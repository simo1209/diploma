import 'package:flutter/material.dart';
import 'dart:convert';

import 'package:diploma_project/session.dart';


class Transaction {
  final String transactionDesc;
  final double amount;

  Transaction({this.transactionDesc, this.amount});

  factory Transaction.fromJson(Map<String, dynamic> json) {
    return Transaction(
      transactionDesc: json['transaction_desc'],
      amount: json['amount'],
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
    Map arguments = ModalRoute
        .of(context)
        .settings
        .arguments as Map;

    if (arguments == null) {
      throw new Exception('Arguments not passed');
    }

    return MaterialApp(
      title: _title,
      home: Scaffold(
        appBar: AppBar(title: const Text(_title)),
        body: TransactionDetailsPage(arguments: arguments),
      ),
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
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: <Widget>[
                Text('Description'),
                Text('Amount')
              ],
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: <Widget>[
                Text(transaction.transactionDesc),
                Text(transaction.amount.toString())
              ],
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: <Widget>[
                RaisedButton(
                  child: Text("Accept"),
                  color: Colors.lightBlue,
                  textColor: Colors.white,
                  onPressed: () {
                    print('Accepting transaction');
                  },
                )
              ],
            )
          ],
        ),
      );
    }
    return Text(response.body);
  }

}