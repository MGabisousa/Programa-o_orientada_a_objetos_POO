#%%
from wget import download
from requests import get
from datetime import datetime
from zipfile import ZipFile
from os import path, remove
import numpy as np
import pandas as pd
import os

#%%
class ExtractDTB:
    " Extrair dados da divisão territorial do Brasil a partir do IBGE "
    
    print( 'Inicializando o processo de extração...' )

    def __init__(self, urlname, destdir):
        self.urlname = urlname
        self.destdir = destdir

    def __log__(self, msg):
        data = datetime.now().strftime('%d-%m-%Y %Hh%Mm%Ss')
        print(f'--->> {data} INFO {msg.upper()}...')

    def download(self):

        self.__log__( 'Verificando se a URL está ativa' )

        response = get(self.urlname, timeout=600, stream=True)

        if response.ok:
            self.__log__( 'Baixando os dados' )
            download(self.urlname, self.destdir)

    def uncompress(self, string = "MUNICIPIO.xls"):
        " Descomprimir dados baixados da DTB "

        self.__log__( 'Verificando arquivo compactado' )

        nome_arquivo = path.basename(self.urlname)
        
        if 'zip' in nome_arquivo:
            with ZipFile(f'{self.destdir}/{nome_arquivo}', 'r') as zip:
                zip.printdir()
                lista_zip= zip.filelist

        print(lista_zip)

        xls_zip = [i.filename for i in lista_zip if string in i.filename][0]

        self.__log__( f'Descompactando o arquivo: {xls_zip}' )

        with ZipFile(f'{self.destdir}/{nome_arquivo}', 'r') as zip:
            zip.extract(xls_zip, path = self.destdir)

        return f'{self.destdir}/{nome_arquivo}'

    def ziprm(self):
        " Remoção do arquivo ZIP "
        arquivo_local = self.uncompress()

        if path.exists(arquivo_local):
            self.__log__( f'Removendo o arquivo: {arquivo_local}' )
            remove(arquivo_local)


# Diretórios
urlname = 'https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/divisao_territorial/2022/DTB_2022.zip'

destdir = 'C:/Users/gabri/OneDrive/Documentos/poo p1'

# Instanciando o processo de extração da DTB
extract = ExtractDTB(urlname, destdir)

# Download
extract.download()

# Uncompress
extract.uncompress()

# Gestão de arquivos baixados
extract.ziprm()
#########################################################################################################################################


# %%
'''................................................ '''
 
class TransformDTB:
    '''Essa classe tem como definição fazer é pegar o arquivo baixado e transformar em um DataFrame e deixá-lo com os parâmetros pedidos.

'''
    print('Transformando em DataFrame........')
    
    def __init__(self, tab_municipio):
        self.tab_municipio = pd.read_excel(tab_municipio, header=6, names=['UF', 'Nome_UF', 'Região_Geográfica_Intermediária',
           'Nome_Região_Geográfica_Intermediária', 'Região_Geográfica_Imediata',
           'Nome_Região_Geográfica_Imediata', 'Mesorregião_Geográfica',
           'Nome_Mesorregião', 'Microrregião_Geográfica', 'Nome_Microrregião',
           'Município', 'Código_Município_Completo', 'Nome_Município'])
        self.tab_municipio = self.tab_municipio.fillna(0) #substituindo os nan por 0
    
    def filtrar_nordeste(self):                                                              # filtrando nordeste 
        nordeste = input("Quer escolher a região nordeste ? Sim/NÃO : ")
        if nordeste.lower() == 'Sim' or 'sim':
            self.tab_municipio = self.tab_municipio[self.tab_municipio['UF'].between(21, 29)]
    
    def ver(self, n):
        return self.tab_municipio.head(n)
    
    def contar_municipios_por_estado(self):
        contagem = self.tab_municipio.groupby('Nome_UF')    ['Nome_Município'].nunique()
        return contagem



tab_municipio= 'C:/Users/gabri/OneDrive/Documentos/poo p1/RELATORIO_DTB_BRASIL_MUNICIPIO.xls'

transform_dtb = TransformDTB(tab_municipio)

# Filtrando Nordeste
transform_dtb.filtrar_nordeste()

# Exibindo os 10 primeiros.
print(transform_dtb.ver(10))

# Contando o número de municípios por estado
contagem_municipios = transform_dtb.contar_municipios_por_estado()
print(f'A quantidade de municípios é : {contagem_municipios}')

#/////////////////////////////////////////////////////////////////////


# %%

class LoadDTB:
    '''Essa classe pega o  DataFrame e pede onde você quer salvar ele e em que tipo de arquivo você deseja ter esse  DataFrame salvo.'''
    
    def __init__(self, tab_municipio):
        self.tab_municipio = tab_municipio
        
    def salve_arquivo(self, content):
        diretorio = input("Digite o diretório de destino: ")
        nome_arquivo = input("Digite o nome do arquivo: ")
        
        tipo = input('Escolha o tipo de arquivo que você quer - CSV, EXCEL ou JSON: ')
        
        print(f'O tipo de arquivo que foi escolhido foi:{tipo}')
        
        destino = f"{diretorio}/{nome_arquivo}"  #se não for windows tem que trocar / por \.
        
        print('O arquivo vai ser salvo no seguinte diretório :{destino}')
        
        if tipo == 'CSV' or 'csv':
            destino = f"{destino}.csv" 
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            with open(destino, 'w') as file:
                file.write(content)
            self.tab_municipio.to_csv(destino, index=False)
            
        elif tipo == 'EXCEL' or 'excel':
            destino = f"{destino}.xlsx"
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            self.tab_municipio.to_excel(destino, index=False)
            
        elif tipo == 'JSON' or 'json':
            destino = f"{destino}.json"
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            with open(destino, 'w') as file:
                file.write(content)
            self.tab_municipio.to_json(destino, orient='records')
                                       
        else:
            print("Tipo de arquivo não listado .")
            return
        
        print(f"Arquivo salvo em: {destino}")

#transformando a tabela .
loader = LoadDTB(transform_dtb.tab_municipio)

# salvando o arquivo .
loader.salve_arquivo('content')



# %%
