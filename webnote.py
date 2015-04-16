import socket
import re
import json

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind(('0.0.0.0', 81))
s.listen(1)
while True:
    conn, addr = s.accept()
    print 'Connected by', addr
    data = ''

    while True:
        if '\r\n\r\n' in data:
            break
        new_data = conn.recv(1024)
        if not new_data:
            break
        data += new_data

    request_match = \
        re.match(r'^([^ ]+) ([^ ]+) ([^ ]+)\r\n(.*)$',
                 data,
                 re.DOTALL)

    if request_match is not None:
        method = request_match.group(1)
        resource = request_match.group(2)
        protocol = request_match.group(3)
        data = request_match.group(4)
    else:
        raise Exception('Cannot read request')

    request_headers = dict()
    while True:
        if data[:2] == '\r\n':
            data = data[2:]
            break
        field = re.match(r'^([^:]+): ([^\r]+)\r\n(.*)$', data, re.DOTALL)
        if field is not None:
            field_name = field.group(1)
            field_body = field.group(2)
            request_headers[field_name] = field_body
            data = field.group(3)
        else:
            raise Exception('Cannot read request header')

    print resource
    print request_headers

    response = ''

    response += 'HTTP/1.1 200 OK\r\n'

    with open('.notes') as note_file:
        note_dict = json.loads(note_file.read())
    if resource == '/notes':
        response += 'Content-Type: text/plain; charset=utf-8\r\n'
        response += '\r\n'
        for name in note_dict:
            response += '%s\n' % name
    elif resource == '/add_note':
        response += 'Content-Type: text/html; charset=utf-8\r\n'
        response += '\r\n'
        if method == 'GET':
            response += """
    <html>
            <head>
                    <meta http-equiv="content-type" content="text/h
    tml; charset=utf-8"/>
            </head>
            <body>
                <form action="add_note" method="POST">
                    Name: <input type="text" name="name"/>
                    <br/>
                    Content: <input type="text" name="content"/>
                    <br/>
                    <input type="submit" value="Add"/>
                </form>
            </body>
    </html>
            """
    else:
        response += 'Content-Type: text/plain; charset=utf-8\r\n'
        response += '\r\n'
        note_match = re.match('^/notes/([a-z]+)$', resource)
        if note_match is not None:
            response += note_dict[note_match.group(1)]
        else:
            response += 'Hello World!!!'

    conn.sendall(response)
    conn.close()
