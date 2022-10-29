###############################################################
# RFM ile Müşteri Segmentasyonu (Customer Segmentation with RFM)
###############################################################

###############################################################
# 1. İş Problemi (Business Problem)
###############################################################

# Bir e-ticaret şirketi müşterilerini segmentlere ayırıp bu segmentlere göre
# pazarlama stratejileri belirlemek istiyor.

# Veri Seti Hikayesi
# https://archive.ics.uci.edu/ml/datasets/Online+Retail+II

# Online Retail II isimli veri seti İngiltere merkezli online bir satış mağazasının
# 01/12/2009 - 09/12/2011 tarihleri arasındaki satışlarını içeriyor.

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

###############################################################
# Gorev 1: Veriyi Anlama ve Hazırlama
###############################################################

import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)


#Adım 1: Online Retail II excelindeki 2010-2011 verisini okuyunuz. Oluşturduğunuz dataframe’in kopyasını oluşturunuz.
df_ = pd.read_excel("datasets/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()

#Adım 2: Veri setinin betimsel istatistiklerini inceleyiniz.
df.head()
df.shape
df.describe().T

#Adım3: Veri setinde eksik gözlem var mı? Varsa hangi değişkende kaç tane eksik gözlem vardır?
df.isnull().sum()

#Adım4: Eksik gözlemleri veri setinden çıkartınız. Çıkarma işleminde ‘inplace=True’ parametresini kullanınız.
df.dropna(inplace=True)

#Adım5: Eşsiz ürün sayısı kaçtır?
df["Description"].nunique()

Adım6: Hangi üründen kaçar tane vardır?
df["Description"].value_counts().head()

#Adım7: En çok sipariş edilen 5 ürünü çoktan aza doğru sıralayınız
df.groupby("Description").agg({"Quantity" : "sum"}).sort_values("Quantity", ascending=False).head(5)

df = df[(df['Quantity'] > 0)]

#Adım 8: Faturalardaki ‘C’ iptal edilen işlemleri göstermektedir. İptal edilen işlemleri veri setinden çıkartınız.
df = df[~df["Invoice"].str.contains("C", na=False)]

#Adım 9: Fatura başına elde edilen toplam kazancı ifade eden ‘TotalPrice’ adında bir değişken oluşturunuz.
df["TotalPrice"] = df["Quantity"] * df["Price"]

###############################################################
# Gorev 2: RFM Metriklerinin Hesaplanması
###############################################################

df["InvoiceDate"].max()
#recencydeğeri için bugünün tarihini (2011, 12, 11) olarak kabul ediniz.
today_date = dt.datetime(2011, 12, 11)
type(df["InvoiceDate"])

#Adım 1: Recency, Frequency ve Monetary tanımlarını yapınız.
#Recency: Sıcaklık, analiz tarihine göre müşterinin son alışverişi üzerinden geçen zaman
#Frequency: Müşterinin alışveriş sıklığı,toplam yaptığı alışveriş sayısı
#Monetary: Müşterinin alışverişlerinin toplam tutarı

#Adım 2: Müşteri özelinde Recency, Frequencyve Monetary metriklerini groupby, aggve lambda ile hesaplayınız.
df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})

#Adım 3: Hesapladığınız metrikleri rfmisimli bir değişkene atayınız.
rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})

rfm.head()

#Adım4: Oluşturduğunuz metriklerin isimlerini  recency, frequencyve monetaryolarak değiştiriniz.
rfm.columns = ["recency", "frequency", "monetary"]

rfm.describe().T

#rfm dataframe’ini oluşturduktan sonra veri setini "monetary>0" olacak şekilde filtreleyiniz.
rfm = rfm[rfm["monetary"] > 0]

###############################################################
# Gorev 3: RFM Skorlarının Oluşturulması ve Tek bir Değişkene Çevrilmesi
###############################################################

#Adım 1: Recency, Frequencyve Monetarymetriklerini qcutyardımı ile 1-5 arasında skorlara çeviriniz.
#Bu skorları recency_score, frequency_scoreve monetary_scoreolarak kaydediniz.
rfm["recency_score"] = pd.qcut(rfm["recency"], 5 , labels = [5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels = [1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm["monetary"], 5 , labels= [1, 2, 3, 4, 5])

rfm.head()

#Adım 2: recency_scoreve frequency_score’utek bir değişken olarak ifade ediniz ve RF_SCORE olarak kaydediniz.
rfm["RF_SCORE"] = (rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str))

###############################################################
# Gorev 4: RF Skorunun SegmentOlarak Tanımlanması
###############################################################

#Adım 1: Oluşturulan RF skorları için segmenttanımlamaları yapınız.
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

#Adım 2: Yukarıdaki seg_map yardımı ile skorları segmentlere çeviriniz.
rfm["segment"] = rfm["RF_SCORE"].replace(seg_map, regex=True)

rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])


###############################################################
# Gorev 4: Aksiyon Zamanı !
###############################################################

#Adım 1: Önemli gördüğünüz 3 segmenti seçiniz. Bu üç segmenti hem aksiyon kararları açısından hemde segmentlerin yapısı açısından(ortalama RFM değerleri) yorumlayınız.

rfm[rfm["segment"] == "cant_loose"].head()
rfm[rfm["segment"] == "cant_loose"].agg({"RF_SCORE": "median"})

rfm[rfm["segment"] == "champions"].head()
rfm[rfm["segment"] == "champions"].agg({"RF_SCORE": "median"})

rfm[rfm["segment"] == "loyal_customers"].head()
rfm[rfm["segment"] == "loyal_customers"].agg({"RF_SCORE": "median"})


#Adım2: "LoyalCustomers" sınıfına ait customerID'leri seçerek excel çıktısını alınız.

new_df = pd.DataFrame()
new_df["loyal_customers_id"] = rfm[rfm["segment"] == "loyal_customers"].index
new_df["loyal_customers_id"] = new_df["loyal_customers_id"].astype(int)

new_df.to_excel("loyal_customers.xlsx", sheet_name="loyal segment")



