import json
import tempfile

import psycopg2
import pygraphviz as pgv
from django.http import JsonResponse
from django.shortcuts import render

from core import forms


# Create your views here.
def home(request):
    if request.method == 'POST':
        form = forms.DBConnectionForm(request.POST)
        if form.is_valid():
            db_name = form.cleaned_data['db_name']
            db_user = form.cleaned_data['db_user']
            db_password = form.cleaned_data['db_password']
            db_host = form.cleaned_data['db_host']
            db_port = form.cleaned_data['db_port']
            use_ssl = form.cleaned_data['use_ssl']
            db_type = form.cleaned_data['db_type']

            db_config = {
                'dbname': db_name,
                'user': db_user,
                'password': db_password,
                'host': db_host,
                'port': db_port
            }

            if bool(use_ssl):
                db_config['sslmode'] = 'require'

            try:
                # Conectar ao banco de dados externo
                connection = psycopg2.connect(
                    **db_config
                )
                cursor = connection.cursor()

                # Obter as informações das tabelas e colunas
                cursor.execute("""
                            SELECT 
                                table_name, column_name, data_type, table_schema
                            FROM 
                                information_schema.columns
                            WHERE 
                                table_schema NOT IN ('pg_catalog','information_schema');
                        """)
                columns_info = cursor.fetchall()

                # Obter as informações das chaves primárias
                cursor.execute("""
                            SELECT 
                                kcu.table_name, kcu.column_name
                            FROM 
                                information_schema.table_constraints AS tc 
                                JOIN information_schema.key_column_usage AS kcu
                                  ON tc.constraint_name = kcu.constraint_name
                            WHERE 
                                tc.constraint_type = 'PRIMARY KEY'
                                AND tc.table_schema = 'public';
                        """)
                primary_keys = cursor.fetchall()

                # Criar o gráfico ER
                graph = pgv.AGraph(directed=True, strict=False)

                # Dicionário para armazenar os atributos de cada nó (tabela)
                node_attributes = {}

                # Adicionar nós (tabelas) ao gráfico e seus atributos (colunas)
                for table_name, column_name, data_type, table_schema in columns_info:
                    # Se o nó com a tabela ainda não existir
                    if table_name not in node_attributes:
                        # Adiciona no dicionário
                        node_attributes[table_name] = []

                    # Definir o nome do atributo (coluna)
                    attribute_label = f"{column_name}: {data_type}"

                    # se for primary key
                    if (table_name, column_name) in primary_keys:
                        # Adicionar a marcação (PK)
                        attribute_label += " (PK)"

                    # adicionar o atributo ao dicionário
                    node_attributes[table_name].append(attribute_label)

                # para cada nó no dicionário
                for table_name, attributes in node_attributes.items():
                    # concatena os atributos em uma string
                    node_label = f"{table_name} | " + " | ".join(attributes)
                    # adiciona o nó ao gráfico
                    graph.add_node(table_name, label=node_label, shape='record')

                # Adicionar arestas (relacionamentos de chaves estrangeiras)
                cursor.execute("""
                            SELECT 
                                tc.table_name AS source_table, kcu.column_name AS source_column, 
                                ccu.table_name AS target_table, ccu.column_name AS target_column
                            FROM 
                                information_schema.table_constraints AS tc 
                                JOIN information_schema.key_column_usage AS kcu
                                  ON tc.constraint_name = kcu.constraint_name
                                JOIN information_schema.constraint_column_usage AS ccu
                                  ON ccu.constraint_name = tc.constraint_name
                            WHERE 
                                tc.constraint_type = 'FOREIGN KEY'
                                AND tc.table_schema = 'public';
                        """)
                foreign_keys = cursor.fetchall()

                # para cada fk
                for fk in foreign_keys:
                    source_table, source_column, target_table, target_column = fk
                    graph.add_edge(source_table, target_table, label=f"{source_column} -> {target_column}")

                # Ajustar o layout do gráfico
                graph.graph_attr.update(size="10,10!", dpi="300", rankdir="LR", splines="true", nodesep="1.0",
                                        ranksep="2.0")
                graph.node_attr.update(fontsize="10", margin="0.1,0.1", width="2.5", height="0.5", shape="record")
                graph.edge_attr.update(fontsize="8")

                # Gerar o arquivo de imagem temporário
                with tempfile.NamedTemporaryFile(
                        suffix=".png",
                        delete=False,
                        dir="/tmp/media"
                ) as tmp_file:
                    graph.layout(prog='dot')
                    graph.draw(tmp_file.name, format='png')

                return render(
                    request,
                    'result.html',
                    {'image': tmp_file.name.split('/', maxsplit=2)[-1],
                     'conn_info': db_config,
                     'message': {'type': 'success', 'text': f'Diagrama de ER gerado com sucesso!'}}
                )
            except Exception as e:
                return render(
                    request,
                    'result.html',
                    {'error_message': f"Erro ao gerar o diagrama ER: {e}"}
                )
    else:
        form = forms.DBConnectionForm()

    return render(request, 'home.html', {'form': form})


def test_connection(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        db_host = data.get('db_host')
        db_port = data.get('db_port')
        db_name = data.get('db_name')
        db_user = data.get('db_user')
        db_password = data.get('db_password')
        use_ssl = data.get('use_ssl')

        try:
            connection = psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port,
                sslmode='require' if use_ssl else 'disable'
            )
            connection.close()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Método inválido.'})
