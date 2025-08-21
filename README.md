# BlockVault-API

# 📦 Descrição
BlockVault-API é uma API focada no upload e download seguro de arquivos em um sistema centralizado, utilizando tecnologia blockchain para garantir a integridade e segurança dos dados. O sistema implementa um mecanismo de consenso PoA (Proof of Authority) para validar operações e registrar transações de forma imutável.

🚀 Funcionalidades principais
✅ Registro de arquivos na blockchain
✅ Upload e download seguro de arquivos
✅ Validação por meio de Proof of Authority (PoA)
✅ API RESTful com endpoints claros e documentados
✅ Armazenamento de registros em bancos de dados NoSQL e SQL
✅ Assinatura e verificação com chaves públicas e privadas

# 🛠️ Tecnologias utilizadas

Python 3.11: Linguagem de programação utilizada.
FastAPI: Framework para criação da API.
Uvicorn: Servidor ASGI para executar a aplicação.
MongoDB (NoSQL)
MySQL (SQL)
Criptografia / Hashing
Testes unitários com unittest

# ⚙️ Como instalar
Use o gerenciador de dependências pip para instalar os pacotes necessários.

Clone o repositório

git clone https://github.com/albertoh88/BlockVault-API.git

Crie e ative um ambiente virtual

python -m venv venv
.\Scripts\activate

Instale as dependências

pip install -r requirements.txt
Abra o arquivo .env e certifique-se de inserir seus dados de conexão com o banco de dados.
Substitua host, porta, nome do banco, usuário e senha pelas suas credenciais do MySQL e MongoDB.
O código para criar os bancos de dados MySQL e MongoDB está no diretório principal.

Para executar a aplicação, use o arquivo app.py. A API estará disponível em http://127.0.0.1:8000.

# 📌 Como usar
✅ O arquivo deve ser criptografado e enviado em formato binário.
✅ O token deve incluir a chave pública para assinar/verificar operações.

📥 1. Upload de arquivo (upload file)
Endpoint:
POST http://localhost:8000/uploadfile/

Como configurar no Postman:

Method: POST

Authorization:
→ Selecione “Bearer Token”
→ No campo do token, cole sua chave pública no formato JWT.

Body: → form-data
→ Key: file → Type: File → Selecione o arquivo criptografado (.bin, .enc, etc.)
→ Exemplo de arquivo: arquivo_criptografado.enc

Notas:
✔️ O arquivo deve estar previamente criptografado.
✔️ Será enviado em formato binário para o servidor.

🗑 2. Excluir arquivo (delete file)
Endpoint:
POST http://localhost:8000/deletefile/

Como configurar no Postman:

Method: POST

Authorization:
→ “Bearer Token” → Use sua chave pública JWT.

Headers:
→ Content-Type: application/json

Body: → raw → JSON

{
  "filename": "arquivo_criptografado.enc"
}
Notas:
✔️ Informe o nome exato do arquivo criptografado armazenado no servidor.

📂 3. Baixar arquivo (load file)
Endpoint:
POST http://localhost:8000/loadfile/

Como configurar no Postman:

Method: POST

Authorization:
→ “Bearer Token” → Use sua chave pública JWT.

Headers:
→ Content-Type: application/json

Body: → raw → JSON

{
  "filename": "arquivo_criptografado.enc"
}
Resposta:
✔️ O Postman fará o download do arquivo criptografado.
✔️ Lembre-se de salvá-lo manualmente a partir da aba “Body” no Postman, pois ele virá em formato binário.

⚠️ Resumo de requisitos importantes
🔒 Criptografia: Todos os arquivos devem estar previamente criptografados antes de serem enviados.
🔑 Token: O JWT enviado deve conter a chave pública utilizada para assinar/verificar.
📁 Formato: O arquivo deve ser enviado em binário (binary) no caso de upload.

# 💬 Contato
https://github.com/albertoh88

Notas adicionais
Documentação OpenAPI: O FastAPI gera automaticamente uma interface interativa da API acessível em http://127.0.0.1:8000/docs.
Não se esqueça de rodar o servidor com uvicorn app:app --reload se for usar o Uvicorn diretamente.

# 📃 Licença
Este projeto está sob a licença MIT. Consulte o arquivo [Licença MIT](https://opensource.org/licenses/MIT) para mais informações.
