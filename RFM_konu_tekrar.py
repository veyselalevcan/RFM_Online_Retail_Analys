#Recency Frequency Monetary
#Yenilik- Sıklık - Money

#Customer Segmentation with RFM, satın alma alışkanlıklarına göre musterileri grupla.

###############################################################
# RFM ile Müşteri Segmentasyonu (Customer Segmentation with RFM)
###############################################################

# 1. İş Problemi (Business Problem)
# 2. Veriyi Anlama (Data Understanding)
# 3. Veri Hazırlama (Data Preparation)
# 4. RFM Metriklerinin Hesaplanması (Calculating RFM Metrics)
# 5. RFM Skorlarının Hesaplanması (Calculating RFM Scores)
# 6. RFM Segmentlerinin Oluşturulması ve Analiz Edilmesi (Creating & Analysing RFM Segments)
# 7. Tüm Sürecin Fonksiyonlaştırılması

###############################################################
# 1. İş Problemi (Business Problem)
###############################################################

# Bir e-ticaret şirketi müşterilerini segmentlere ayırıp bu segmentlere göre
# pazarlama stratejileri belirlemek istiyor.

###############################################################
# 2. Veriyi Anlama (Data Understanding)
###############################################################
import datetime as dt
import pandas as pd

pd.set_option('display.max_columns', None)
#pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

# Veri Seti Hikayesi
# https://archive.ics.uci.edu/ml/datasets/Online+Retail+II

# Online Retail II isimli veri seti İngiltere merkezli online bir satış mağazasının
# 01/12/2009 - 09/12/2011 tarihleri arasındaki satışlarını içeriyor.

df_ = pd.read_excel('CRM Analytics/online_retail_II.xlsx')
df = df_.copy()

# Değişkenler
#
# InvoiceNo: Fatura numarası. Her işleme yani faturaya ait eşsiz numara. C ile başlıyorsa iptal edilen işlem.
# StockCode: Ürün kodu. Her bir ürün için eşsiz numara.
# Description: Ürün ismi
# Quantity: Ürün adedi. Faturalardaki ürünlerden kaçar tane satıldığını ifade etmektedir.
# InvoiceDate: Fatura tarihi ve zamanı.
# UnitPrice: Ürün fiyatı (Sterlin cinsinden)
# CustomerID: Eşsiz müşteri numarası
# Country: Ülke ismi. Müşterinin yaşadığı ülke.

df.isnull().sum()
df['Description'].nunique()

df['Description'].value_counts()
df.groupby('Description').agg({'Quantity': 'sum'}).sort_values("Quantity", ascending=False).head()

df['Invoice'].nunique()

#Fatura Bazında Toplam Kazanç- TotalPrice:
df['TotalPrice'] = df['Quantity'] * df['Price']
df['TotalPrice'].head()

df.groupby('Invoice').agg({'TotalPrice': 'sum'}).head()

###############################################################
# 3. Veri Hazırlama (Data Preparation)
###############################################################
df.shape
df.isnull().sum()
df.describe().T

#Eksik değerleri sil
df.dropna(inplace=True)

# Invoice C ile başlıyorsa iptal edilen işlem. Bunların Dışındakileri gorelim:
# ~ ile değilini kontrol ederim.
df = df[~df['Invoice'].str.contains('C', na=False)]

df['Quantity'].sort_values().head()

#Eksi degerli faturaları filitreyelim
df = df[(df['Quantity'] > 0)]

###############################################################
# 4. RFM Metriklerinin Hesaplanması (Calculating RFM Metrics)
###############################################################

df['InvoiceDate'].max()

#Son işlem tarihinden iki sonrasına analiz günü olarak seçebilirim.
today_date = dt.datetime(2010, 12, 11)
type(today_date)

#Recency (Invoice Date), Frequency (Invoice), Monetary (TotalPRice)

rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})
# (today_date - InvoiceDate.max()).days gun cinsinden ifade et demek için .days yaptık
# Recency: her bir musterinin max tarihi;
# Frequency: her bir musterinin eşsiz fatura sayısı,
# Monetary: her bir musterinin totalprice toplamı

rfm.head()
rfm.columns = ['recency', 'frequency', 'monetary']
rfm.describe().T

#monetary min değerinde 0 var bunu düzeltmeliyiz
rfm = rfm[rfm['monetary'] > 0]

#son durumda musteri sayımız? 4.312
rfm.shape

###############################################################
# 5. RFM Skorlarının Hesaplanması (Calculating RFM Scores)
###############################################################

rfm['recency_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])

#qcut- değişken ver bu değişkeni kaç yerden boleceğimi ve boldukten sonra labelleri belirt.
#kucukten buyuge bolup sıralar
#Recency değeri kucukse değerlidir. Son alışveriş tarihi az olan 1 çok olan 5 olacak

rfm['monetary_score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm['frequency_score'] = pd.qcut(rfm['frequency'], 5, labels=[1, 2, 3, 4, 5])

#frequency_score value error verdi. oluşturdugumuz aralıklarlada unique degerler olmadıgı için
#her aralıga benzer sayılar dustugu ıcın bolme yapamadı bu sebeple rank metodunu(rank(method='first')) kulllanacagız
#daha fazla aralıga aynı sayılar dusmus.

rfm['frequency_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])

#2 boyutlu RFM Score gorselinde R ve F degerlerini kullanıyoruz

rfm['RFM_SCORE'] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))
# astype(str) ile stringe çevirip iki stringi toplama ozelliğini kullandım.

rfm.describe().T

#Scoreları stringe cevirdiğim için describe a gelmedi.

rfm[rfm['RFM_SCORE'] == '55'] #Champion customers, en degerliler 457 kişi

rfm[rfm['RFM_SCORE'] == '14']

###############################################################
# 6. RFM Segmentlerinin Oluşturulması ve Analiz Edilmesi (Creating & Analysing RFM Segments)
###############################################################
# Regex (Regular Explanation)
# Regex temsil: 1. elemanında 5, ikinci elemanında 4 veya 5 gorursen 'CHAMPION' isimlendirmesi yap

# RFM isimlendirmesi
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

# veri setine segment değişkeni oluştur ve bu etiketleri ata

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)

# RFM_SCORE içindeki degerleri replace ile degistir.
# Bunu da seg_map te verdiğim key ve value degerleri ile yap

rfm.head()

# Metriklerle segmentlerin analizini yapalım: Ortalamalarını segmente göre inceleyelim
rfm[['segment', 'recency', 'frequency', 'monetary']].groupby('segment').agg(['mean', 'count'])

# Need Attentin sınıfını ilgili birime verelim bunlara ozel çalışma yapalım
rfm[rfm['segment'] == 'need_attention'].head()

# Bu musterilerin sadece ID lerini almak istersem:
rfm[rfm['segment'] == 'need_attention'].index

# Bu ID leri ilgili birime iletmek için to_csv metodunu kullanacağım. Once yeni bir dataframe oluşturuyorum
new_df = pd.DataFrame()

new_df['need_attention_customers_id'] = rfm[rfm['segment'] == 'need_attention'].index

# Float olan indeks degerlerini integere cevirip .00 lardan kurtulalım
new_df['need_attention_customers_id'] = new_df['need_attention_customers_id'].astype(int)

new_df.to_csv('need_attention_customers_id.csv')
rfm.to_csv('rfm.csv')

###############################################################
# 7. Tüm Sürecin Fonksiyonlaştırılması
###############################################################
def create_rfm(dataframe, csv=False):

    # VERIYI HAZIRLAMA
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]

    # RFM METRIKLERININ HESAPLANMASI
    today_date = dt.datetime(2011, 12, 11)
    rfm = dataframe.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                                                'Invoice': lambda num: num.nunique(),
                                                "TotalPrice": lambda price: price.sum()})
    rfm.columns = ['recency', 'frequency', "monetary"]
    rfm = rfm[(rfm['monetary'] > 0)]

    # RFM SKORLARININ HESAPLANMASI
    rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

    # cltv_df skorları kategorik değere dönüştürülüp df'e eklendi
    rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                        rfm['frequency_score'].astype(str))


    # SEGMENTLERIN ISIMLENDIRILMESI
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

    rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
    rfm = rfm[["recency", "frequency", "monetary", "segment"]]
    rfm.index = rfm.index.astype(int)

    if csv:
        rfm.to_csv("rfm.csv")

    return rfm

df = df_.copy()

create_rfm(df, csv=True)