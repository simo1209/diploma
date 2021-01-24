import 'package:http/http.dart' as http;

class Session {
  static Map<String, String> headers = {};
  static final String host = "http://192.168.0.101:5001";

  static Future<http.StreamedResponse> login(email, password) async {
    var uri = Uri.parse('$host/login');

    var request = http.MultipartRequest('POST', uri);
    request.fields['email'] = email;
    request.fields['password'] = password;

    return request.send();
  }

  static Future<http.StreamedResponse> register(Map<String, String> fields) {
    var uri = Uri.parse('$host/register');

    var request = http.MultipartRequest('POST', uri);
    fields.forEach((key, value) {
      request.fields[key] = value;
    });

    return request.send();
  }

  static Future<http.StreamedResponse> postForm(String url, Map<String, String> fields) {
    var uri = Uri.parse('$host$url');
    print(uri);

    var request = http.MultipartRequest('POST', uri);
    fields.forEach((key, value) {
      request.fields[key] = value;
    });
    request.headers['cookie'] = headers['cookie'];

    return request.send();
  }

  static Future<http.Response> get(String url) async {
    print(headers);
    http.Response response = await http.get('$host$url', headers: headers);
    print(response.statusCode);
    updateCookie(response);
    return response;
  }

  static Future<http.Response> post(String url, dynamic data) async {
    print('$host$url');
    print(data);
    print(headers);
    http.Response response =
        await http.post('$host$url', body: data, headers: headers);
    updateCookie(response);
    return response;
  }

  static void updateCookie(response) {
    String rawCookie = response.headers['set-cookie'];
    if (rawCookie != null) {
      int index = rawCookie.indexOf(';');
      headers['cookie'] =
          (index == -1) ? rawCookie : rawCookie.substring(0, index);
    }
  }
}
