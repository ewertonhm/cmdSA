# cmdSA
Um cliente cmd para o Sistema de Ativação

## Como usar:
- Para pesquisar um ou vários circuitos utilize:
`status -c circuitos separado por espaços`
exemplo:
`status -c BNU-0700A BQE-0644B`


## Como instalar e configurar:
### 1. Faça o download da release mais recente e extraia em uma pasta do seu computador.

### 2. Configure as variaveis de ambiente com o caminho da pasta do script:
1. Acesse o painel de controle
2. Acesse: Contas de Usuários > Contas de Usuário > Alterar as variáveis do meu ambiente.
3. Selecione a variável Path e click em Editar
4. Click em Novo e coloque o caminho da pasta em que se encontra o arquivo status.exe

### 3. Faça o download do chromedriver e salve na pasta c:\webdriver:
1. Faça o download da versão mais recente para windows em: [Chromedriver](https://chromedriver.chromium.org/downloads "Chromedriver")
2. Descompacte o arquivo chromedriver_win32.zip na pasta c:\webdriver.

### 4. Execute a primeira vez e configure o arquivo de credenciais:
1. abra uma janela do cmd e digite o comando:
`status -c firstrun`

2. O arquivo '.credentials.ini' vai ser criado na raiz do seu usuário (c:/Users/seu.nome/.credentials.ini), com o seguinte conteúdo:


    [credentials-sa]
    Login:usuario@redeunifique.com.br
    Senha:senha

- Nesse arquivo você deve preencher seu usuário do Sistema de Ativação (email), e a senha CRIPTOGRAFADA. 
- Para criptografar a senha, abra o cmd e digite:
`cripto`
E siga as instruções, exemplo:


    C:\Users\ewerton.marschalk>cripto
    Digite a senha:123456789
    Aqui está sua senha criptografada:
    Senha:09rMw1z+r5Xi4de9V6Gi3pKfBXtFENNQRQlvsAPTTUo=

------------


#### Links
- O cliente conta com links para o daloinfo no caso do pppoe, e para o cadastro do cliente no caso do código do cliente, porém os links são apenas exibidos usando terminais mais modernos, no windows 10 é possível utilizar o [Windows Terminal](https://www.microsoft.com/pt-br/p/windows-terminal/ "Windows Terminal"), que pode ser baixado e instalado pela Microsoft Store.
*OBS: No momento o script não funciona corretamente no PowerShell do Windows Terminal, que é o terminal padrão que ele abre ao ser executado, para contornar a situação, em configurações você pode alterar o "Perfil padrão" para Prompt de comando.*

------------




