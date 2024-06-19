from django.db import models


class AbstractModel(models.Model):
    id = models.AutoField(primary_key=True)
    criado_em = models.DateTimeField(auto_now_add=True, db_comment="Data e hora da criação.")
    atualizado_em = models.DateTimeField(auto_now=True, db_comment="Data e hora da última alteração.")

    class Meta:
        abstract = True


# Create your models here.
class DBConnection(AbstractModel):
    class DbType(models.TextChoices):
        POSTGRESQL = "postgresql", "PostgreSQL"
        # MYSQL = "mysql", "MySQL"
        # MARIADB = "mariadb", "MariaDB"
        # SQLSERVER = "sqlserver", "SQL Server"
        # ORACLE = "oracle", "Oracle"
        # SQLITE = "sqlite", "SQLite"

    db_name = models.CharField(max_length=254, unique=True, verbose_name="Base de dados")
    db_user = models.CharField(max_length=254, verbose_name="Usuário")
    db_password = models.CharField(max_length=254, verbose_name="Senha")

    db_host = models.CharField(max_length=254, verbose_name="Host")
    db_port = models.IntegerField(default=5432, verbose_name="Porta")

    use_ssl = models.BooleanField(default=False, verbose_name="Usar SSL")

    db_type = models.CharField(
        choices=DbType.choices,
        default=DbType.POSTGRESQL,
        max_length=30,
        verbose_name="Selecione o tipo",
    )
