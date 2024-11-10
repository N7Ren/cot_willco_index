import pandas as pd

#'NAT GAS NYME', '023651',
#'BRAZILIAN REAL', '102741',

markets = pd.DataFrame({
    'contract_code': ['098662', '042601', '044601', '043602', '020601', 
                      '232741', '096742', '090741', '099741', '097741', '092741', '112741', '095741', '122741', '299741', '399741',
                      '088691', '084691', '075651', '076651', '067651', '002602', '073732', '083731', '005602', 
                      '124603', '209742', '13874A', '239742', '240741', '244042', 
                      '133741', '146021'],
    'contract_names':  ['USD INDEX', 'UST 2Y NOTE', 'UST 5Y NOTE', 'UST 10Y NOTE', 'UST BOND', 
                        'AUSTRALIAN DOLLAR', 'BRITISH POUND', 'CANADIAN DOLLAR', 'EURO FX', 'JAPANESE YEN', 'SWISS FRANC', 'NZ DOLLAR', 'MEXICAN PESO', 'SO AFRICAN RAND', 'EUR FX/GBP', 'EURO FX/JPY',
                        'GOLD', 'SILVER', 'PALLADIUM', 'PLATINUM', 'WTI-PHYSICAL', 'CORN', 'COCOA', 'COFFEE C', 'SOYBEANS',
                        'DJIA x $5', 'NASDAQ MINI', 'E-MINI S&P 500', 'RUSSELL E-MINI', 'NIKKEI STOCK AVERAGE', 'MSCI EM INDEX', 
                        'BITCOIN', 'ETHER CASH SETTLED']
})