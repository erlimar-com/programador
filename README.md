Projeto Programador
===================

Este é o código utilizado para demonstrar o que é possível fazer
quando se é um programador.

É também o site que explica o projeto em http://programador.erlimar.com
além da API por tráz do utilitário de linha de comando `programador` que
o próprio site ensina a instalar e usar.

## Notas de desenvolvimento

Para implantar o site em um servidor [NGINX](http://nginx.org) faça:

1. Crie um diretório para conter as configurações:
```sh
$ mkdir /opt/programador
```

2. Crie o arquivo de configuração do NGINX `/opt/programador/uwsgi.site`:
```config
server {
    listen 80;
    listen [::]:80;
    server_name programador.erlimar.com;
    location / {
        include uwsgi_params;
        uwsgi_pass unix:/opt/programador/uwsgi.sock;
    }
}
```

3. Faça o link do arquivo criado no diretório do NGINX:
```sh
$ ln -s /opt/programador/uwsgi.site /etc/nginx/sites-enabled/programador.erlimar.com
```

4. Instale o módulo de servidor com o pip localmente:
```sh
$ pip3 install ./servidor
```

5. Instale o uWSGI com pip:
```sh
$ pip3 install uwsgi
```

6. Crie o arquivo de inicialização do uWSGI:
```ini
[uwsgi]
module = programador_servidor:app
socket = /opt/programador/uwsgi.sock
chmod-socket = 666
master = true
die-on-term = true
```

7. Crie o arquivo de definição do serviço SystemD `/opt/programador/wsgi.service`:
```ini
[Unit]
Description=uWSGI instance to serve ProgramadorServidor
After=network.target

[Service]
ExecStart=uwsgi --ini /opt/programador/uwsgi.ini

[Install]
WantedBy=multi-user.target
```

8. Faça o link do arquivo criado no diretório do SystemD:
```sh
$ ln -s /opt/programador/uwsgi.service /etc/systemd/system/programador-servidor.service
```

9. Inicie-o:
```sh
$ systemctl start programador-servidor
```

10. Reinicie o NGINX:
```sh
$ systemctl stop nginx
$ systemctl start nginx
```
