# cmdSA
Um cliente cmd para o Sistema de Ativação
![Screenshot](screenshot.png)

## Como usar:
### Para verificar o status de um ou vários circuitos utilize:
```
status -c circuitos separado por espaços
```
exemplo:
```
status -c BNU-0700A BQE-0644B
````


### Para verificar o status de um ou vários circuitos, com a exibição separada por Caixa de Atendimento, utilize:
```
status -ca circuitos separado por espaços
```
exemplo:
```
status -ca BNU-0700A
````
*OBS: essa consulta é um pouco mais demorada que a consulta normal ao status dos circuitos, e para ser realizada, vai necessitar de acesso a tela de 
Gerenciamento de Portas FTTH no ERP, caso seu usuário no ERP não tenha acesso a essa tela, o comando não vai funcionar.*


### Para pesquisar o status de um ou vários clientes utilize:
```
status -p login
```
exemplo:
```
status -p 519171
```


### para pesquisar o status de um login e do seu circuito, utilize:
```
status -c pppoe -p login
```
exemplo:
```
status -c pppoe -p 519171
```



## Como instalar e configurar:
### 1. Faça o download da [release](https://github.com/ewertonhm/cmdSA/releases) mais recente e extraia em uma pasta do seu computador.

### 2. Configure as variaveis de ambiente com o caminho da pasta do script:
1. Acesse o painel de controle
2. Acesse: Contas de Usuários > Contas de Usuário > Alterar as variáveis do meu ambiente.
3. Selecione a variável Path e click em Editar
4. Click em Novo e coloque o caminho da pasta em que se encontra o arquivo status.exe

### 3. Abra o prompt de comando e digita 'status' e siga as instruções. 


```

------------


#### Links
- O cliente conta com links para o daloinfo no caso do pppoe, e para o cadastro do cliente no caso do código do cliente, porém os links são apenas exibidos usando terminais mais modernos, no windows 10 é possível utilizar o [Windows Terminal](https://www.microsoft.com/pt-br/p/windows-terminal/ "Windows Terminal"), que pode ser baixado e instalado pela Microsoft Store.
*OBS: No momento o script não funciona corretamente no PowerShell do Windows Terminal, que é o terminal padrão que ele abre ao ser executado, para contornar a situação, em configurações você pode alterar o "Perfil padrão" para Prompt de comando.*

------------




