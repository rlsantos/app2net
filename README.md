# app2net

# Tutorial
## Instalação

1. clone o repositório: `git clone https://github.com/rlsantos/app2net`. 
2. Instale as dependências: `pip install -r requirements.txt`

A forma mais simples de executar o ecossistema, com todas a  infraestrutura virtual necessária, é através de Docker. 
Para executá-lo, levantando todos os componentes, basta executar o comando `docker-compose up`, que irá criar e 
configurar os seguintes serviços:

| Container     |Porta|Função                                                                 |
|---------------|-----|-----------------------------------------------------------------------|
|db             |5432 |Banco de Dados PostgreSQL                                              |
|app2net_core   |8000 |Servidor excutando o componente App2net core                           |
|repo           |3333 |Repositório com NetApps                                                |
|node-p4 (1 e 2)|5555 |Nós com suporte à P4, Simple Switch <br> (Driver já instalado)         |
|node-openflow  |5555 |Nó com suporte à Openflow, Controlador Ryu <br> (Driver já instalado)  | 

Caso não possa executar o ambiente com Docker, pode-se também instalar manualmente os componentes necessários. Nesse 
caso, recomenda-se utilizar máquinas virtuais para os nós. Atente-se para a necessidade de instalar e executar os 
drivers nos nós de rede.

Após a instalação, execute os seguintes comandos, para finalizar o processo de instalação e salvar as informações 
necessárias no banco de dados:

```bash
$ cd app2net_core
$ python3 manage.py migrate
$ python3 manage.py loaddata fixture.json
```

## Uso
ToDo

