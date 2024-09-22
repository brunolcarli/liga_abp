<table align="center"><tr><td align="center" width="9999">

<img src="https://github.com/brunolcarli/liga_abp/blob/master/static/ABPLOGO.jpeg?raw=true" align="center" width="170" alt="Project icon">

# Liga ABP 

*Bot gerenciador da Liga organizada pela Arena de Batalhas Pokémon*

</td></tr>

</table>    

<div align="center">

> [![Version badge](https://img.shields.io/badge/version-1.0.1-silver.svg)]()



</div>

## Referências de comandos

Um guia de referência de comandos está disponível [aqui](https://github.com/brunolcarli/liga_abp/wiki/Modelos-de-dados)



## Desenvolvedores

### Clonando e executando o serviço

![Linux Badge](https://img.shields.io/badge/OS-Linux-black.svg)
![Apple badge](https://badgen.net/badge/OS/OSX/:color?icon=apple)


#### Execução em máquina local

Clone este projeto em um diretório da sua máquina, inicialize um novo amviente virtual python (`>= Python3.9`) e instale as dependências do serviço através do `make`:

Examplo com virtualevwrapper:

```
$ git clone https://github.com/brunolcarli/liga_abp.git
$ cd liga_abp/
$ mkvirtualenv liga_abp
$ (liga_abp) make install
```

Crie eum arquivo de variáveis de ambiente conforme o template disponibilizado em `config/environment/local_template` preenchendo os valores das variáveis com suas próprias configurações, informando corretamente o TOKEN (obtido no portal de desenvolvedores Discord na seção **aplicações**) e as variáveis que apontam para um banco de dados (MySQL/MariaDB)



> *you may need to create a user on database for this.*

```
export TOKEN=your_bot_token
export MYSQL_HOST=db_host
export MYSQL_PORT=db_port
export MYSQL_USER=db_username
export MYSQL_PASSWORD=db_password
export MYSQL_DATABASE=db_name
```

Exporte as variáveis

```
$ source config/environmnent/my_env_file
```

Adicione seu bot em um servidor discord e execute o serviço:


```
$ make local
```

## Docker

Instale o docker-compose com `pip`:

```
$ pip install docker-compose
```

Crie um novo arquivo chamado `docker` em `config/environment/` conforme o template disponibilizado no mesmo diretório, preenchendo os valores das variáveis (descrito na seção anterior).

Compile e execute o container utilizando o docker-compose:

```
$ docker-compose build
$ docker compose up
```

Nota: É necessário ter o schema e tabelas previamente criadas no banco de dados conforme o [modelo de estrutura de dados](https://github.com/brunolcarli/liga_abp/wiki/Modelos-de-dados)