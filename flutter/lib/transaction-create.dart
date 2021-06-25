import 'package:diploma_project/session.dart';
import 'package:flutter/material.dart';

class TransactionCreate extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return TransactionCreatePage();
  }
}

class TransactionCreatePage extends StatefulWidget {
  TransactionCreatePage({Key key}) : super(key: key);

  @override
  TransactionCreatePageState createState() => TransactionCreatePageState();
}

class TransactionCreatePageState extends State<TransactionCreatePage> {
  final _formKey = GlobalKey<FormState>();
  static const String _title = 'Create Transaction';
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
      body: Form(
        key: _formKey,
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Text(
                "Create Transaction",
                style: TextStyle(fontSize: 33),
              ),
              Text(
                "Enter amount and description for the transaction. The app will generate a QR code you can share with others, to request the amount entered.",
                style: TextStyle(fontSize: 18, color: Colors.white12),
              ),
              TextFormField(
                controller: amountController,
                keyboardType: TextInputType.numberWithOptions(
                    signed: false, decimal: true),
                decoration: const InputDecoration(
                  hintText: 'Enter amount',
                ),
                validator: (value) {
                  if (value.isEmpty) {
                    return 'Please fill in the field';
                  }
                  if (double.parse(value) <= 0) {
                    return 'Please enter valid amount';
                  }
                  return null;
                },
              ),
              TextFormField(
                controller: descriptionController,
                keyboardType: TextInputType.multiline,
                decoration: const InputDecoration(
                  hintText: 'Enter description',
                ),
                validator: (value) {
                  if (value.isEmpty) {
                    return 'Please fill in the field';
                  }
                  return null;
                },
              ),
              Row(
                children: <Widget>[
                  Padding(
                      padding: const EdgeInsets.symmetric(
                          vertical: 16.0, horizontal: 8.0),
                      child: RaisedButton(
                        onPressed: () => _create(context),
                        child: Text('Create'),
                        color: Colors.lightBlue,
                        textColor: Colors.white,
                      )),
                  Visibility(
                    visible: errorMessage.isEmpty,
                    child: Text(errorMessage),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future _create(context) async {
    if (_formKey.currentState.validate()) {
      String amount = amountController.text;
      String description = descriptionController.text;

      var fields = {'amount': amount, 'description': description};

      var response = await Session.postForm('/transactions/create', fields);
      print(response.headers);
      print(response.statusCode);
      if (response.statusCode == 302) {
        String codeUrl = response.headers['location'];
        print(codeUrl);
        Navigator.push(
            context,
            MaterialPageRoute(
                builder: (context) => TransactionCode(
                      imgUrl: codeUrl,
                    )));
      } else if (response.statusCode == 400) {
        String em = await response.stream.bytesToString();
        setState(() {
          errorMessage = em;
        });
      }
    }
  }
}

class TransactionCode extends StatelessWidget {
  final String imgUrl;

  const TransactionCode({Key key, this.imgUrl}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(
          title: Text('Your QR code:'),
          actions: <Widget>[
            IconButton(
              icon: Icon(
                Icons.arrow_back_rounded,
                color: Colors.white,
              ),
              onPressed: () {
                Navigator.pushReplacementNamed(context, '/account');
              },
            )
          ],
        ),
        body: Center(
          child: Image.network(
            '$imgUrl',
          ),
        ),
      ),
    );
  }
}
