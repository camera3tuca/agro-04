"""
Base de Dados do Agronegócio
Mapeamento completo de ativos do setor
"""

class AgroDatabase:
    """Base de dados completa do setor de agronegócio"""
    
    def __init__(self):
        self.data = self._initialize_database()
    
    def _initialize_database(self):
        """Inicializa base de ativos do agronegócio"""
        
        database = {
            # AÇÕES BRASILEIRAS - Agronegócio
            'acoes_br': {
                # Proteína Animal
                'BEEF3': {'name': 'Minerva', 'sector': 'Frigorífico', 'subsector': 'Proteína Bovina'},
                'MRFG3': {'name': 'Marfrig', 'sector': 'Frigorífico', 'subsector': 'Proteína Bovina'},
                'JBSS3': {'name': 'JBS', 'sector': 'Frigorífico', 'subsector': 'Proteína Animal'},
                'BRFS3': {'name': 'BRF', 'sector': 'Frigorífico', 'subsector': 'Aves e Suínos'},
                
                # Alimentos e Bebidas
                'ABEV3': {'name': 'Ambev', 'sector': 'Bebidas', 'subsector': 'Cervejas'},
                'MDIA3': {'name': 'M.Dias Branco', 'sector': 'Alimentos', 'subsector': 'Massas e Biscoitos'},
                
                # Insumos Agrícolas
                'SMTO3': {'name': 'São Martinho', 'sector': 'Açúcar e Etanol', 'subsector': 'Bioenergia'},
                'SOJA3': {'name': 'Boa Safra', 'sector': 'Insumos', 'subsector': 'Sementes'},
                
                # Trading e Logística
                'RAIZ4': {'name': 'Raízen', 'sector': 'Bioenergia', 'subsector': 'Etanol'},
                'CSAN3': {'name': 'Cosan', 'sector': 'Bioenergia', 'subsector': 'Açúcar e Etanol'},
                
                # Papel e Celulose
                'SUZB3': {'name': 'Suzano', 'sector': 'Papel e Celulose', 'subsector': 'Celulose'},
                'KLBN11': {'name': 'Klabin', 'sector': 'Papel e Celulose', 'subsector': 'Papel'},
                
                # Terras e Agricultura
                'SLCE3': {'name': 'SLC Agrícola', 'sector': 'Agricultura', 'subsector': 'Grãos'},
                'AGRO3': {'name': 'BrasilAgro', 'sector': 'Agricultura', 'subsector': 'Terras Agrícolas'},
            },
            
            # BDRs - Agronegócio Internacional
            'bdrs': {
                # Equipamentos Agrícolas
                'D1EE34': {'name': 'Deere & Company', 'sector': 'Equipamentos', 'subsector': 'Maquinário Agrícola', 'us_ticker': 'DE'},
                'A1GC34': {'name': 'AGCO Corp', 'sector': 'Equipamentos', 'subsector': 'Maquinário Agrícola', 'us_ticker': 'AGCO'},
                
                # Trading e Processamento
                'A1DM34': {'name': 'Archer Daniels', 'sector': 'Trading', 'subsector': 'Commodities Agrícolas', 'us_ticker': 'ADM'},
                'B1UN34': {'name': 'Bunge', 'sector': 'Trading', 'subsector': 'Commodities Agrícolas', 'us_ticker': 'BG'},
                
                # Fertilizantes
                'M1OS34': {'name': 'Mosaic', 'sector': 'Insumos', 'subsector': 'Fertilizantes', 'us_ticker': 'MOS'},
                'N1TR34': {'name': 'Nutrien', 'sector': 'Insumos', 'subsector': 'Fertilizantes', 'us_ticker': 'NTR'},
                'C1F34': {'name': 'CF Industries', 'sector': 'Insumos', 'subsector': 'Fertilizantes', 'us_ticker': 'CF'},
                
                # Biotecnologia Agrícola
                'C1TX34': {'name': 'Corteva', 'sector': 'Insumos', 'subsector': 'Sementes e Defensivos', 'us_ticker': 'CTVA'},
            },
            
            # ETFs - Agronegócio
            'etfs': {
                'FOOD11': {'name': 'ETF Agronegócio', 'sector': 'ETF', 'subsector': 'Agronegócio BR'},
            },
            
            # Commodities para Correlação
            'commodities': {
                'ZC=F': {'name': 'Milho Futuro', 'sector': 'Commodity', 'subsector': 'Grãos'},
                'ZS=F': {'name': 'Soja Futuro', 'sector': 'Commodity', 'subsector': 'Grãos'},
                'ZW=F': {'name': 'Trigo Futuro', 'sector': 'Commodity', 'subsector': 'Grãos'},
                'LE=F': {'name': 'Gado Futuro', 'sector': 'Commodity', 'subsector': 'Proteína'},
                'SB=F': {'name': 'Açúcar Futuro', 'sector': 'Commodity', 'subsector': 'Açúcar'},
            }
        }
        
        return database
    
    def get_all_tickers(self):
        """Retorna todos os tickers para monitoramento"""
        tickers = []
        for category in ['acoes_br', 'bdrs', 'etfs']:
            tickers.extend(list(self.data[category].keys()))
        return tickers
    
    def get_ticker_info(self, ticker):
        """Retorna informações de um ticker específico"""
        for category in self.data.values():
            if ticker in category:
                return category[ticker]
        return None
    
    def get_by_sector(self, sector):
        """Retorna tickers por setor"""
        result = []
        for category in ['acoes_br', 'bdrs', 'etfs']:
            for ticker, info in self.data[category].items():
                if info['sector'] == sector:
                    result.append((ticker, info))
        return result
