# Import bibliotecas
import pandas as pd
import win32com.client as win32
import pathlib


# Import base de dados
emails = pd.read_excel(r'database\Emails.xlsx')
vendas = pd.read_excel(r'database\Vendas.xlsx')
lojas = pd.read_csv(r'database\Lojas.csv', encoding='latin1', sep=';')

# Mesclando as tabelas de Lojas e Vendas
vendas = vendas.merge(lojas, on='ID Loja')
dicionario_lojas = {}
for loja in lojas['Loja']:
    dicionario_lojas[loja] = vendas.loc[vendas['Loja'] == loja, :]

# Definindo o dia do indicador //aqui está sendo chamado o ultimo dia registrado na base de dados
dia_indicador = vendas['Data'].max()

# Salvar a planilha na pasta arquivos_lojas
caminho_backup = pathlib.Path(r'arquivos_lojas')
arquivos_backup = caminho_backup.iterdir()

lista_nomes_backup = [arquivo.name for arquivo in arquivos_backup]

for loja in dicionario_lojas:
    if loja not in lista_nomes_backup:
        nova_pasta = caminho_backup / loja
        nova_pasta.mkdir()
    nome_arquivo = f'{dia_indicador.month}_{dia_indicador.day}_{loja}.xlsx'
    local_arquivo = caminho_backup / loja / nome_arquivo
    dicionario_lojas[loja].to_excel(local_arquivo)

# Definindo as metas
meta_fatu_dia = 1000
meta_fatu_ano = 1650000
meta_qtdeprodutos_dia = 4
meta_qtdeprodutos_ano = 120
meta_ticketmedio_dia = 500
meta_ticketmedio_ano = 500

# Automatizar o envio de e-mail para os gerentes de cada loja
for loja in dicionario_lojas:
    vendas_loja = dicionario_lojas[loja]
    vendas_loja_dia = vendas_loja.loc[vendas_loja['Data'] == dia_indicador, :]

    # faturamento
    fatu_ano = vendas_loja['Valor Final'].sum()
    fatu_dia = vendas_loja_dia['Valor Final'].sum()

    # diversidade de produtos
    qtde_produtos_ano = len(vendas_loja['Produto'].unique())
    qtde_produtos_dia = len(vendas_loja_dia['Produto'].unique())

    # ticket médio
    valor_venda = vendas_loja.groupby('Código Venda').sum()
    tick_ano = valor_venda['Valor Final'].mean()
    valor_venda_dia = vendas_loja_dia.groupby('Código Venda').sum()
    tick_dia = valor_venda_dia['Valor Final'].mean()

    # Enviar o e-mail
    outlook = win32.Dispatch('outlook.application')

    nome = emails.loc[emails['Loja'] == loja, 'Gerente'].values[0]
    mail = outlook.CreateItem(0)
    mail.To = emails.loc[emails['Loja'] == loja, 'E-mail'].values[0]
    mail.Subject = f'OnePage Dia {dia_indicador.day}/{dia_indicador.month} - Loja{loja}'


    if fatu_dia >= meta_fatu_dia:
        cor_fat_dia = 'green'
    else:
        cor_fat_dia = 'red'
    if fatu_ano >= meta_fatu_ano:
        cor_fat_ano = 'green'
    else:
        cor_fat_ano = 'red'


    if qtde_produtos_dia >= meta_qtdeprodutos_dia:
        cor_qtde_dia = 'green'
    else:
        cor_qtde_dia = 'red'
    if qtde_produtos_ano >= meta_qtdeprodutos_ano:
        cor_qtde_ano = 'green'
    else:
        cor_qtde_ano = 'red'


    if tick_dia >= meta_ticketmedio_dia:
        cor_tick_dia = 'green'
    else:
        cor_tick_dia = 'red'
    if tick_ano >= meta_ticketmedio_ano:
        cor_tick_ano = 'green'
    else:
        cor_tick_ano = 'red'

# Definindo o corpo do e-mail
    mail.HTMLBody = f'''
    <p>Bom dia, {nome}.</p>

    <p>O resultado de ontem <strong>({dia_indicador.day}/{dia_indicador.month})</strong> da <strong>Loja {loja}</strong> foi:</p>

    <table>
      <tr>
        <th>Indicador</th>
        <th>Valor Dia</th>
        <th>Meta Dia</th>
        <th>Cenário Dia</th>
      </tr>
      <tr>
        <td>Faturamento</td>
        <td style="text-align: center">R${fatu_dia:,.2f}</td>
        <td style="text-align: center">R${meta_fatu_dia:,.2f}</td>
        <td style="text-align: center"><font color="{cor_fat_dia}">◙</font></td>
      </tr>
      <tr>
        <td>Diversidade de Produto</td>
        <td style="text-align: center">{qtde_produtos_dia}</td>
        <td style="text-align: center">{meta_qtdeprodutos_dia}</td>
        <td style="text-align: center"><font color="{cor_qtde_dia}">◙</font></td>
      </tr>
      <tr>
        <td>Ticket Médio</td>
        <td style="text-align: center">R${tick_dia:,.2f}</td>
        <td style="text-align: center">R${meta_ticketmedio_dia:,.2f}</td>
        <td style="text-align: center"><font color="{cor_tick_dia}">◙</font></td>
      </tr>
    </table>
    <br>
    <table>
      <tr>
        <th>Indicador</th>
        <th>Valor Ano</th>
        <th>Meta Ano</th>
        <th>Cenário Ano</th>
      </tr>
      <tr>
        <td>Faturamento</td>
        <td style="text-align: center">R${fatu_ano:,.2f}</td>
        <td style="text-align: center">R${meta_fatu_ano:,.2f}</td>
        <td style="text-align: center"><font color="{cor_fat_ano}">◙</font></td>
      </tr>
      <tr>
        <td>Diversidade de Produto</td>
        <td style="text-align: center">{qtde_produtos_ano}</td>
        <td style="text-align: center">{meta_qtdeprodutos_ano}</td>
        <td style="text-align: center"><font color="{cor_qtde_ano}">◙</font></td>
      </tr>
      <tr>
        <td>Ticket Médio</td>
        <td style="text-align: center">R${tick_ano:,.2f}</td>
        <td style="text-align: center">R${meta_ticketmedio_ano:,.2f}</td>
        <td style="text-align: center"><font color="{cor_tick_ano}">◙</font></td>
      </tr>
    </table>

    <p>Segue em anexo a planilha com todos os dados para ánalise.</p>
    <p>Qualquer dúvida estou à disposição.</p>
    <p>Att., Giannini</p>
    '''

    # Anexos (pode colocar quantos quiser):
    attachment = pathlib.Path.cwd() / caminho_backup / loja / f'{dia_indicador.month}_{dia_indicador.day}_{loja}.xlsx'
    mail.Attachments.Add(str(attachment))
    mail.Send()


# Criar um ranking para a diretoria
faturamento_lojas = vendas.groupby('Loja')[['Loja', 'Valor Final']].sum()
faturamento_lojas_ano = faturamento_lojas.sort_values(by='Valor Final', ascending=False)

nome_arquivo = f'{dia_indicador.month}_{dia_indicador.day}_Ranking Anual.xlsx'
faturamento_lojas_ano.to_excel(r'arquivos_lojas\{}'.format(nome_arquivo))

vendas_dia = vendas.loc[vendas['Data']==dia_indicador, :]
faturamento_lojas_dia = vendas_dia.groupby('Loja')[['Loja', 'Valor Final']].sum()
faturamento_lojas_dia = faturamento_lojas_dia.sort_values(by='Valor Final', ascending=False)

nome_arquivo = '{}_{}_Ranking Dia.xlsx'.format(dia_indicador.month, dia_indicador.day)
faturamento_lojas_dia.to_excel(r'arquivos_lojas\{}'.format(nome_arquivo))


# Enviar e-mail para a diretoria
outlook = win32.Dispatch('outlook.application')

mail = outlook.CreateItem(0)
mail.To = emails.loc[emails['Loja']=='Diretoria', 'E-mail'].values[0]
mail.Subject = f'Ranking Dia {dia_indicador.day}/{dia_indicador.month}'
mail.Body = f'''
Prezados, bom dia.

Melhor loja do Dia em faturamento: Loja {faturamento_lojas_dia.index[0]} com Faturamento R${faturamento_lojas_dia.iloc[0, 0]:,.2f}
Pior loja do Dia em faturamento: Loja {faturamento_lojas_dia.index[-1]} com Faturamento R${faturamento_lojas_dia.iloc[-1, 0]:,.2f}

Melhor loja do Ano em faturamento: Loja {faturamento_lojas_ano.index[0]} com Faturamento R${faturamento_lojas_ano.iloc[0, 0]:,.2f}
Pior loja do Ano em faturamento: Loja {faturamento_lojas_ano.index[0]} com Faturamento R${faturamento_lojas_ano.iloc[-1, 0]:,.2f}

Segue em anexo os rankings do ano e do dia de todas as lojas.

Qualquer dúvida estou à disposição.

Att., Giannini.
'''

attachment  = pathlib.Path.cwd() / caminho_backup / f'{dia_indicador.month}_{dia_indicador.day}_Ranking Anual.xlsx'
mail.Attachments.Add(str(attachment))
attachment  = pathlib.Path.cwd() / caminho_backup / f'{dia_indicador.month}_{dia_indicador.day}_Ranking Dia.xlsx'
mail.Attachments.Add(str(attachment))

mail.Send()
