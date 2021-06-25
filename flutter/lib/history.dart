import 'dart:convert';

import 'package:diploma_project/session.dart';
import 'package:flutter/material.dart';

class HistoryRow {
  final double debit;
  final double credit;
  final String description;
  final String date;
  final String counterparty;

  HistoryRow({this.debit, this.credit, this.description, this.date, this.counterparty});

  factory HistoryRow.fromJson(Map<String, dynamic> json) {
    return HistoryRow(
        debit: json['debit']!=null?double.parse(json['debit']):null,
        credit: json['credit']!=null?double.parse(json['credit']):null,
        description: json['description'],
        date: json['date'],
        counterparty: json['counterparty']);
  }
}

class TransactionHistory extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return TransactionHistoryPage();
  }
}

class TransactionHistoryPage extends StatefulWidget {
  TransactionHistoryPage({Key key}) : super(key: key);

  @override
  TransactionHistoryPageState createState() => TransactionHistoryPageState();
}

class TransactionHistoryPageState extends State<TransactionHistoryPage> {
  static const String _title = 'Transaction History';
  String errorMessage = '';

  final amountController = TextEditingController();
  final descriptionController = TextEditingController();

  @override
  void dispose() {
    amountController.dispose();
    descriptionController.dispose();

    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(title: const Text(_title)),
        body: FutureBuilder(
          future: loadHistory(),
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.done && snapshot.hasData){
              var historyJson = jsonDecode(snapshot.data.body);
              var history = List<HistoryRow>();
              historyJson.forEach((row) {
                history.add(HistoryRow.fromJson(row));
              });
              return ListView.builder(
                itemCount: history.length,
                itemBuilder: (context, index) {
                  var transaction = history[index];
                  return Card(
                    child: ListTile(
                      title: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text("${transaction.credit!=null?'-':'+'}${transaction.credit!=null?transaction.credit:transaction.debit}",),
                          Text("${transaction.date}")
                        ],
                      ),
                      subtitle: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text("${transaction.counterparty}"),
                          Text("${transaction.description}")
                        ],
                      )
                    ),
                  );
                },
              );
            }else if (snapshot.hasError){
              Scaffold.of(context).showSnackBar(SnackBar(
                content: Text("Couldn't connect to server"),
              ));
              return new Text(snapshot.error.toString());
            }
            return CircularProgressIndicator();
          },
        ));
  }

  loadHistory() async {
    var response = await Session.get('/accounts/account/transactions');
    return response;
  }
}
