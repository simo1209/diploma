import 'dart:convert';

import 'package:diploma_project/account.dart';
import 'package:diploma_project/history.dart';
import 'package:diploma_project/session.dart';
import 'package:diploma_project/transaction-create.dart';
import 'package:diploma_project/transaction-details.dart';
import 'package:flutter/material.dart';

void main() {
  runApp(Login());
}

class Login extends StatelessWidget {
  static const String _title = 'Login';

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: _title,
      home: Scaffold(
        appBar: AppBar(title: const Text(_title)),
        body: LoginPage(),
      ),
      routes: <String, WidgetBuilder>{
        '/account': (_) => new AccountWidget(),
        '/signUp': (_) => new SignUp(),
        '/transactionDetails': (_) => new TransactionDetailsWidget(),
        '/transactionCreate': (_) => new TransactionCreatePage(),
        '/history': (_) => new TransactionHistory()
      },
    );
  }
}

class LoginPage extends StatefulWidget {
  LoginPage({Key key}) : super(key: key);

  @override
  _LoginPageState createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _formKey = GlobalKey<FormState>();

  final emailController = TextEditingController();
  final passwordController = TextEditingController();

  @override
  void dispose() {
    emailController.dispose();
    passwordController.dispose();

    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Text(
              "Login",
              style: TextStyle(fontSize: 33),
            ),
            TextFormField(
              controller: emailController,
              keyboardType: TextInputType.emailAddress,
              decoration: const InputDecoration(
                hintText: 'Enter your email',
              ),
              validator: (value) {
                if (value.isEmpty) {
                  return 'Please fill in the field';
                }
                return null;
              },
            ),
            TextFormField(
              controller: passwordController,
              obscureText: true,
              decoration: const InputDecoration(
                hintText: 'Enter your password',
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
                    onPressed: () => _login(context),
                    child: Text('Sign In'),
                    color: Colors.lightBlue,
                    textColor: Colors.white,
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(
                      vertical: 16.0, horizontal: 8.0),
                  child: RaisedButton(
                    onPressed: () {
                      Navigator.of(context).pushNamed('/signUp');
                    },
                    child: Text('Sign Up'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Future _login(context) async {
    if (_formKey.currentState.validate()) {
      String email = emailController.text;
      String password = passwordController.text;

      try {
        var response = await Session.login(email, password);

        print(response);
        if (response.statusCode == 200) {
          Session.updateCookie(response);
          Navigator.of(context).pushReplacementNamed('/account');
        } else {
          print('Error occurred');
          String em = await response.stream.bytesToString();
          Map<String, dynamic> error = jsonDecode(em);
          print(error);
          Scaffold.of(context).showSnackBar(SnackBar(
            content: Text(error['description']),
          ));
        }
      } on Exception catch (_) {
        Scaffold.of(context).showSnackBar(SnackBar(
          content: Text("Couldn't connect to server"),
        ));
      }
    }
  }
}

class SignUp extends StatelessWidget {
  static const String _title = 'SignUp';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text(_title)),
      body: SignUpPage(),
    );
  }
}

class SignUpPage extends StatefulWidget {
  SignUpPage({Key key}) : super(key: key);

  @override
  _SignUpPageState createState() => _SignUpPageState();
}

class _SignUpPageState extends State<SignUpPage> {
  final _formKey = GlobalKey<FormState>();

  final emailController = TextEditingController();
  final passwordController = TextEditingController();
  final confirmController = TextEditingController();
  final firstNameController = TextEditingController();
  final lastNameController = TextEditingController();
  final phoneController = TextEditingController();
  final ucnController = TextEditingController();
  final countryController = TextEditingController();
  final cityController = TextEditingController();
  final address1Controller = TextEditingController();
  final address2Controller = TextEditingController();
  final postalCodeController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: <Widget>[
              Text(
                "SignUp",
                style: TextStyle(fontSize: 33),
              ),
              TextFormField(
                controller: firstNameController,
                decoration: const InputDecoration(
                  hintText: 'Enter your first name',
                ),
                validator: (value) {
                  if (value.isEmpty) {
                    return 'Please fill in the field';
                  }
                  return null;
                },
              ),
              TextFormField(
                controller: lastNameController,
                decoration: const InputDecoration(
                  hintText: 'Enter your last name',
                ),
                validator: (value) {
                  if (value.isEmpty) {
                    return 'Please fill in the field';
                  }
                  return null;
                },
              ),
              TextFormField(
                controller: emailController,
                keyboardType: TextInputType.emailAddress,
                decoration: const InputDecoration(
                  hintText: 'Enter your email',
                ),
                validator: (value) {
                  if (value.isEmpty) {
                    return 'Please fill in the field';
                  }

                  if (value.length < 6 || value.length > 40) {
                    return 'Invalid length';
                  }

                  return null;
                },
              ),
              TextFormField(
                controller: passwordController,
                obscureText: true,
                decoration: const InputDecoration(
                  hintText: 'Enter your password',
                ),
                validator: (value) {
                  if (value.isEmpty) {
                    return 'Please fill in the field';
                  }

                  if (value.length < 6 || value.length > 40) {
                    return 'Invalid length';
                  }

                  return null;
                },
              ),
              TextFormField(
                controller: confirmController,
                obscureText: true,
                decoration: const InputDecoration(
                  hintText: 'Confirm your password',
                ),
                validator: (value) {
                  if (value.isEmpty) {
                    return 'Please fill in the field';
                  }
                  if (value.compareTo(passwordController.text) != 0) {
                    return 'Passwords must match';
                  }

                  if (value.length < 6 || value.length > 40) {
                    return 'Invalid length';
                  }

                  return null;
                },
              ),
              TextFormField(
                controller: phoneController,
                decoration: const InputDecoration(
                  hintText: 'Enter your phone number',
                ),
                validator: (value) {
                  if (value.isEmpty) {
                    return 'Please fill in the field';
                  }

                  RegExp regExp = new RegExp(r'08[789]\d{7}');
                  if (!regExp.hasMatch(value) && value.length != 10) {
                    return 'Please enter valid phone number';
                  }

                  return null;
                },
              ),
              TextFormField(
                controller: ucnController,
                decoration: const InputDecoration(
                  hintText: 'Enter your UCN',
                ),
                validator: (value) {
                  if (value.isEmpty) {
                    return 'Please fill in the field';
                  }
                  RegExp regExp = new RegExp(r'\d{10}');
                  if (!regExp.hasMatch(value) && value.length != 10) {
                    return 'Please enter valid UCN';
                  }
                  return null;
                },
              ),
              TextFormField(
                controller: countryController,
                decoration: const InputDecoration(
                  hintText: 'Select country',
                ),
                validator: (value) {
                  if (value.isEmpty) {
                    return 'Please fill in the field';
                  }
                  return null;
                },
              ),
              TextFormField(
                controller: cityController,
                decoration: const InputDecoration(
                  hintText: 'Select city',
                ),
                validator: (value) {
                  if (value.isEmpty) {
                    return 'Please fill in the field';
                  }
                  return null;
                },
              ),
              TextFormField(
                controller: address1Controller,
                decoration: const InputDecoration(
                  hintText: 'Enter your address (Street 1)',
                ),
                validator: (value) {
                  if (value.isEmpty) {
                    return 'Please fill in the field';
                  }
                  return null;
                },
              ),
              TextFormField(
                controller: address2Controller,
                decoration: const InputDecoration(
                  hintText: 'Enter your address (Street 2)',
                ),
                validator: (value) {
                  return null;
                },
              ),
              TextFormField(
                controller: postalCodeController,
                decoration: const InputDecoration(
                  hintText: 'Enter your postal code',
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
                      onPressed: () => _signup(context),
                      child: Text('Sign Up'),
                      color: Colors.lightBlue,
                      textColor: Colors.white,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future _signup(context) async {
    if (_formKey.currentState.validate()) {
      var fields = {
        'email': emailController.text,
        'password': passwordController.text,
        'confirm': confirmController.text,
        'first_name': firstNameController.text,
        'last_name': lastNameController.text,
        'phone': phoneController.text,
        'UCN': ucnController.text,
        'country': countryController.text,
        'city': cityController.text,
        'address1': address1Controller.text,
        'address2': address2Controller.text,
        'postal_code': postalCodeController.text,
      };
      try {
        var response = await Session.register(fields);

        if (response.statusCode == 201) {
          Session.updateCookie(response);
          Navigator.of(context).pushReplacementNamed('/account');
        } else {
          print('Error occurred');
          String em = await response.stream.bytesToString();
          Map<String, dynamic> error = jsonDecode(em);
          Scaffold.of(context).showSnackBar(SnackBar(
            content: Text(error['description']),
          ));
        }
      } on Exception catch (_) {
        Scaffold.of(context).showSnackBar(SnackBar(
          content: Text("Couldn't connect to server"),
        ));
      }
    }
  }
}
