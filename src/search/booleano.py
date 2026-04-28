import re
import json
from src.search.nlp import TextProcessor

class modeloBooleano:
    def __init__(self, remove_stopwords, normalization_method, language):
        self.termos_unicos= [] #lista ordenada de termos (linhas)
        self.documentos=[] #lista de documentos (colunas)
        self.matriz= [] #matriz termos-documentos

        self.remove_stopwords = remove_stopwords
        self.normalization_method =normalization_method
        self.language = language
        
        #menor valor -> maior prioridade
        self.prioridade={
            "(":0,
            ")":0,
            "NOT":1,
            "AND":2,
            "OR":3
        }

        self.nlp = TextProcessor()
    
    def construir_matriz(self, output_file):
        '''
        Constroi a matriz termo documento, esta corresponde a uma lista de listas, onde cada lista interna corresponde ao vetor
        de um termo único e indica se este existe num documento, 1, ou se não existe no documento, 0
        '''

        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                self.documentos = json.load(f)
        except FileNotFoundError:
            print(f"Erro: O ficheiro {output_file} não foi encontrado.")
            return

        ##############DEPOIS ALTERAR PARA USAR O NLP DIRETAMENTE####################################### 
        termos= set()
        docs_tokens=[]#ccada elemento da lista corresponde ao conjunto de tokens existente em cada documento

        for doc in self.documentos:
            #há campos tipos os autores que como tem varios sao listas, entao temos de os converter para string     
            conteudo_completo = []
            for valor in doc.values():
                if isinstance(valor, list):
                    conteudo_completo.append(" ".join(valor))
                else:
                    conteudo_completo.append(str(valor))

            texto_doc = " ".join(conteudo_completo).lower()
            tokens = self.nlp.process_text(
                texto_doc,
                language=self.language,
                remove_stopwords=self.remove_stopwords,
                normalization_method= self.normalization_method
            )

            token_set = set(tokens) #para a matriz precisamos do conjunto de tokens, tokens unicos
            docs_tokens.append(token_set)
            termos.update(token_set)
        
        self.termos_unicos= sorted(list(termos)) #termos na matriz ficam ordenados por ordem alfabetica

        num_docs= len(self.documentos)

        for termo in self.termos_unicos:
            #criamos uma linha cheia de zeros inicialmente para cada termo
            linha= [0] * num_docs
            
            for id_doc in range(num_docs):
                if termo in docs_tokens[id_doc]:
                    #Se o termo existe nesse documento o valor desse termo nesse documento passa de 0 para 1
                    linha[id_doc] = 1

            self.matriz.append(linha)

        print(f"Matriz termo-documento construída: {len(self.termos_unicos)} termos x {len(self.documentos)} documentos.")


#=========== Resoluções de Querys ===============================================0

    def obter_linha_termo(self, termo):
        """ Devolve a linha (vetor) correspondente ao termo pesquisado, caso exista, senão o vetor é todo 0's"""
        termo= termo.lower()
        # de forma a ficar uniformizado, como aplicamos nlp aos termos dos documento, temos tambem de aplicar aos termos da query
        tokens= self.nlp.process_text(
            termo,
            language=self.language,
            remove_stopwords=self.remove_stopwords,
            normalization_method=self.normalization_method
        )

        if not tokens:
            return [0] * len(self.documentos) #por exemplo se for uma stopword e o utilizador pediu para remove-las vai devolver uma lista vazia
        
        termo_proc = tokens[0]
        
        if termo_proc in self.termos_unicos:
            indice_termo= self.termos_unicos.index(termo_proc)
            return self.matriz[indice_termo]
        return [0] * len(self.documentos)
    
    
    def operacao_and(self, linha_termo1, linha_termo2):
        '''
        Devolve uma lista com 0 e 1 que correspondem a se o termo existe em ambos os documentos
        '''
        return [a & b for a, b in zip(linha_termo1, linha_termo2)]
   
    ####################nao sei se na vdd isto esta a fazer grande coisa porque tem de comparar todos na mesma, mas tambem nao posso usar posting lists pois isso corresponde ao do indice invertido, so fiz isto pois era um dos requisitos
    def operacao_and_otimizado(self, lista_vetores):
        """Operação AND otimizada, para que sejam comparados primeiro os vetores dos termos que aparecem em menos documentos"""
        vetores_ordenados = sorted(lista_vetores, key= lambda x: sum(x)) #soma todos os 1 dos vetores fazendo com que termos que aparecem em menos documentos aparecam primeiro
        
        resultado = vetores_ordenados[0]
        for i in range(1, len(vetores_ordenados)):
            resultado = self.operacao_and(resultado, vetores_ordenados[i])
        return resultado
    
    
    def operacao_or(self, linha_termo1, linha_termo2):
        '''
        Devolve uma lista com 0 e 1 que correspondem a se existe um ou outro termo no doc
        '''
        return [a | b for a, b in zip(linha_termo1, linha_termo2)]
    
    def operacao_not(self, linha):
        """
        inverte os numeros da linha do termo
        """
        return [1 if x== 0 else 0 for x in linha]
    


    def avaliar_query(self, query): 
        """
        resolve a query respeitanda a hierarquia das operacoes logicas e lida com o AND implicito
        """
        query = query.replace("(", " ( ").replace(")", " ) ") #se houver parenteses vamos isola-los
        tokens_brutos = query.split()

        tokens=[]

        for i in range(len(tokens_brutos)):
            token_atual= tokens_brutos[i]
            tokens.append(token_atual)

            if i < len(tokens_brutos) -1:
                proximo = tokens_brutos[i+1]

                atual_e_termo = token_atual not in self.prioridade
                proximo_e_termo= proximo not in self.prioridade

                #Casos em que é um AND implicito, ou seja um espaco entre termos corresponde a um AND
                #termo termo
                #termo NOT termo
                #termo (termo)
                #) termo

                # Injeta "AND" se houver espaço entre: dois termos, termo e NOT, termo e '(', ou ')' e termo
                if atual_e_termo and proximo_e_termo:
                    tokens.append("AND")
                elif atual_e_termo and proximo == "NOT":
                    tokens.append("AND")
                elif atual_e_termo and proximo == "(":
                    tokens.append("AND")
                elif token_atual ==")" and proximo_e_termo:
                    tokens.append("AND")
                
        #funcionam como stacks, vamos buscar o ultimo inserido        
        operadores=[]
        vetores=[] #guarda resoltados parciais

        def resolver_ultimo():
            """
            Executa a última operação pendente na stack de operadores
            """
            if not operadores: 
                return None
            
            op = operadores.pop()
            if op == "NOT":
                val = vetores.pop()
                vetores.append(self.operacao_not(val))
            elif op =="AND":
                #agrupamos todos os AND adjacentes para otimizar o cálcula na funcao operacao_and_otimizado
                lista_para_and =[vetores.pop(), vetores.pop()]
                # Enquanto o próximo operador for AND, continuamos a tirar vetores para a mesma operação
                while operadores and operadores[-1]== "AND":
                    operadores.pop()
                    lista_para_and.append(vetores.pop())
                vetores.append(self.operacao_and_otimizado(lista_para_and))


            elif op== "OR":
                if len(vetores) >=2:
                    dir= vetores.pop()
                    esq=vetores.pop()
                    vetores.append(self.operacao_or(esq, dir))

        for token in tokens:
            if token == "(":
                operadores.append(token)
            elif token== ")":
                #resolve tudo o que esta dentro dos parêntese até encontrar o "(" correspondente e só depois é que o remove
                while operadores and operadores[-1] != "(":
                    resolver_ultimo()
                operadores.pop() #remove "("
            elif token in self.prioridade:
                #se o operador no fim da lista tiver uma prioridade maior (ou seja um numero inferior), resolvemo-lo primeiro
                while (operadores and operadores[-1] != "(" and self.prioridade[operadores[-1]]<= self.prioridade[token]):
                    resolver_ultimo() #se os que estao nas stacks sao de maior prioridade dos que os que ai vêm esses são resolvidos primeiro
                operadores.append(token)#só quando os de maior prioridade forem resolvidos e que esse é adicionada a lista de operadores

            else: #senao é um termo
                vetores.append(self.obter_linha_termo(token))
        
        while operadores:
            resolver_ultimo()
        
        return vetores[0]
    
    def executar_pesquisa(self, query):
        '''
        Executa a query e devolve os dois dos documentos encontrados (optamos por devolver o doi, pois este serve como um identificador único do documento)
        '''
        resultado_binario = self.avaliar_query(query)

        docs_res= []
        for i, bit in enumerate(resultado_binario):
            if bit ==1:
                docs_res.append(self.documentos[i].get('doi'))
        
        return docs_res
        
if __name__ == "__main__":
    remover_sw= input("Deseja remover Stop Words? (s/n)").lower() == 's'

    print("\nMétodo de Normalização:")
    print("1. Lematização (Mais preciso)")
    print("2. Stemming (Mais rápido)")
    print("3. Nenhum (Mantém palavras originais)")
    escolha_norm = input("Escolha (1/2/3): ")

    mapping = {'1': 'lemma', '2': 'stem', '3': None}
    metodo_norm = mapping.get(escolha_norm, None)

    idioma = input("Idioma (english/portuguese): ").lower()
    
    modelo = modeloBooleano(remove_stopwords= remover_sw, normalization_method=metodo_norm, language=idioma)
    caminho_scraper="../../scraper_results.json"
    modelo.construir_matriz(caminho_scraper)