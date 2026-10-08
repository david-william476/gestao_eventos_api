from sqlmodel import SQLModel, create_engine, Session

# Nome do arquivo de banco de dados local para testes do MVP
sqlite_file_name = "banco.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# O argumento connect_args={"check_same_thread": False} é necessário apenas para o SQLite
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})


def criar_banco_e_tabelas():
    # Importação correta e direta do modelo de dados
    from app.models.models import SQLModel
    SQLModel.metadata.create_all(engine)

def get_session():
    # Função geradora que fornece uma sessão de banco de dados para os endpoints da API
    with Session(engine) as session:
        yield session
