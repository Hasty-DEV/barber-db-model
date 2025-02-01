import psycopg2
from psycopg2 import sql

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "270619",
    "host": "localhost",
    "port": "5432",
    "options": "-c client_encoding=UTF8"
}

DATABASE_NAME = "barbershop"

def criar_banco():

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DATABASE_NAME,))
        existe = cur.fetchone()

        if not existe:
            cur.execute(f"CREATE DATABASE {DATABASE_NAME}")
            print(f"Banco de dados '{DATABASE_NAME}' criado com sucesso!")
        else:
            print(f"O banco de dados '{DATABASE_NAME}' já existe.")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao criar o banco de dados: {e}")

def criar_tabelas():
    """ Conecta ao banco e cria as tabelas """
    try:
        DB_CONFIG["dbname"] = "barbershop"
        print("Conectando ao banco de dados 'barbershop'...")

        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print('Criando a tabelas...')

        cur.execute("""
            DO $$ BEGIN
                CREATE TYPE user_type AS ENUM ('Cliente', 'Barbeiro');
            EXCEPTION WHEN duplicate_object THEN null; END $$;
        """)

        cur.execute("""
            DO $$ BEGIN
                CREATE TYPE payment_method AS ENUM ('Cartão', 'Pix', 'Dinheiro');
            EXCEPTION WHEN duplicate_object THEN null; END $$;
        """)

        cur.execute("""
            DO $$ BEGIN
                CREATE TYPE payment_status AS ENUM ('Pago', 'Pendente', 'Cancelado');
            EXCEPTION WHEN duplicate_object THEN null; END $$;
        """)

        cur.execute("""
            DO $$ BEGIN
                CREATE TYPE days_week AS ENUM ('Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sabado');
            EXCEPTION WHEN duplicate_object THEN null; END $$;
        """)

# Criar tabela de usuários
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                email VARCHAR(50) UNIQUE NOT NULL,
                phone VARCHAR(15),
                user_type user_type NOT NULL,
                password_hash TEXT NOT NULL
            );
        """)

# Criar tabela de serviços
        cur.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                name VARCHAR(12) NOT NULL,
                duration INT NOT NULL, -- Em minutos
                value DECIMAL(10,2) NOT NULL
            );
        """)

# Criar tabela de pagamentos
        cur.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                method payment_method NOT NULL,
                status payment_status DEFAULT 'Pendente',
                value DECIMAL(10,2) NOT NULL
            );
        """)

# Criar tabela de horários de atendimento
        cur.execute("""
            CREATE TABLE IF NOT EXISTS service_hours (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                week_day days_week NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL
            );
        """)

# Criar tabela de avaliações
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                grade INT CHECK (grade BETWEEN 1 AND 5),
                comment TEXT
            );
        """)

        conn.commit()
        cur.close()
        conn.close()

        print("Tabelas criadas com sucesso!")

    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")

criar_banco()
criar_tabelas()


def conectar():
    try:
        conn = psycopg2.connect(
            dbname="barbershop",
            user="postgres",
            password="270619",
            host="localhost",
            port="5432"
        )
        conn.set_client_encoding('UTF8')
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

def inserir_dados(tabela, colunas, valores):
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING id;").format(
                sql.Identifier(tabela),
                sql.SQL(", ").join(map(sql.Identifier, colunas)),
                sql.SQL(", ").join(sql.Placeholder() * len(valores))
            )
            cursor.execute(query, valores)
            conn.commit()
            novo_id = cursor.fetchone()[0]
            print(f"Registro inserido com sucesso! ID: {novo_id}")
            return novo_id
        except Exception as e:
            print(f"Erro ao inserir dados: {e}")
            conn.close()

def adicionar_usuario():
    name = input("Nome: ")
    email = input("Email: ")
    phone = input("Telefone: ")
    user_type = input("Tipo (Cliente/Barbeiro): ")
    password = input("Senha: ")

    return inserir_dados("users", ["name", "email", "phone", "user_type", "password_hash"],
                         [name, email, phone, user_type, password])

def adicionar_servico():
    name = input("Nome do Serviço: ")
    duration = int(input("Duração (minutos): "))
    value = float(input("Preço: "))

    return inserir_dados("services", ["name", "duracao", "value"], [name, duration, value])

def adicionar_pagamento():
    method = input("Método (Cartão/Pix/Dinheiro): ")
    status = input("Status (Pago/Pendente/Cancelado): ")
    value = float(input("Valor: "))

    return inserir_dados("payments", ["method", "status", "value"],
                         [method, status, value])

def adicionar_horario():
    week_day = input("Dia da semana: ")
    start_time = input("Hora de início (HH:MM): ")
    end_time = input("Hora de fim (HH:MM): ")

    return inserir_dados("service_hours", ["week_day", "start_time", "end_time"],
                         [week_day, start_time, end_time])

# Função para adicionar uma avaliação
def adicionar_avaliacao():
    grade = int(input("nota (1 a 5): "))
    comment = input("Comentário: ")

    return inserir_dados("reviews", ["grade", "comment"],
                         [grade, comment])

# Menu interativo
def menu():
    while True:
        print("\n1. Adicionar Usuário")
        print("2. Adicionar Serviço")
        print("3. Adicionar Pagamento")
        print("4. Adicionar Horário de Atendimento")
        print("5. Adicionar Avaliação")
        print("6. Sair")
        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            adicionar_usuario()
        elif escolha == "2":
            adicionar_servico()
        elif escolha == "3":
            adicionar_pagamento()
        elif escolha == "4":
            adicionar_horario()
        elif escolha == "5":
            adicionar_avaliacao()
        elif escolha == "6":
            print("Saindo...")
            break
        else:
            print("Opção inválida, tente novamente.")

# Executar o menu
if __name__ == "__main__":
    menu()