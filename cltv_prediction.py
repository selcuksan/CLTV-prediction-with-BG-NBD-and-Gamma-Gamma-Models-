import datetime as dt
import pandas as pd
from lifetimes import BetaGeoFitter
from lifetimes import GammaGammaFitter

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 500)
pd.set_option("display.float_format", lambda x: '% .2f' % x)


def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + (interquantile_range * 1.5)
    low_limit = quartile1 - (interquantile_range * 1.5)
    return low_limit, up_limit


def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    # dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit


"""Fatura: Fatura numarası. Bu numara 'C' ile başlıyorsa bu işlem iptal edilmiş demektir. 
Stok Kodu: Ürün kodu 
Açıklama: Ürün Adı 
Miktar: Satın alınan ürün adedi
FaturaTarihi: İşlem tarihi 
Fiyat: Birim fiyat 
Müşteri Kimliği: Benzersiz müşteri numarası 
Ülke: Müşterinin ülke adı
"""
df_ = pd.read_excel("CRM Analitiği/datasets/online_retail_II.xlsx")


def create_cltv_p(dataframe, month=3):
    #################
    # VERİ ÖN İŞLEME
    #################

    # Eksik verilerin silinmesi
    dataframe.dropna(inplace=True)

    # İptal edilmiş işlemlerin filtrelenmesi
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]

    # Price ve Quantity değişkenlerinin filtrelenmesi
    dataframe = dataframe[dataframe["Quantity"] > 0]
    dataframe = dataframe[dataframe["Price"] > 0]

    # Price ve Quantity değişkenlerindeki ayrık değerlerin baskılanması
    replace_with_thresholds(dataframe, "Quantity")
    replace_with_thresholds(dataframe, "Price")

    # Price ve Quantity değişkenlerinden totalPrice isimli yeni bir değişken oluşturulması
    dataframe["totalPrice"] = dataframe["Price"] * dataframe["Quantity"]

    # Analiz tarihinin belirlenmesi. Son sipariş tarihinden birkaç gün sonrasının seçilmesi mantıklı olabilir.
    today_date = dt.datetime(2011, 12, 11)

    # Çoklanmış Customer ID değişkeninin tekilleştirilmesi ve
    # Recency (İlk ve son satın alma arasındaki fark. Haftalık (her bir kullanıcı için),
    # T (şirketteki müşterinin yaşı. Haftalık (her bir kullanıcı için),
    # Frequency (toplam tekrar satın alma sayısı. Haftalık (sıklık>1)(her bir kullanıcı için),
    # Monetary (satın alma başına ortalama kazanç.Haftalık (her bir kullanıcı için) değişkenlerinin oluşturulması.
    cltv_df = dataframe.groupby(["Customer ID"]).agg({
        "InvoiceDate": [
            lambda x: (x.max() - x.min()).days,
            lambda x: (today_date - x.min()).days
        ],
        "Invoice": lambda x: x.nunique(),
        "totalPrice": lambda x: sum(x)

    })

    cltv_df.columns = ["recency", "T", "frequency", "monetary"]

    # Average Order Value (average_order_value = total_price / total_transaction)
    cltv_df["monetary"] = cltv_df["monetary"] / cltv_df["frequency"]

    # Birden fazla satın alma olmalı
    cltv_df = cltv_df[cltv_df["frequency"] > 1]

    # Her müşteri için haftalık değere ihtiyacımız var
    cltv_df["recency"] = cltv_df["recency"] / 7

    # Her müşteri için haftalık değere ihtiyacımız var
    cltv_df["T"] = cltv_df["T"] / 7

    """
    Yukarıdaki tabloda yer alan her bir müşteri için; 
    recency, T, Frequency ve Monetary değerleri hesaplanmıştır.
    """

    ############################
    # BG-NBD Modelinin Kurulması
    ############################

    bgf = BetaGeoFitter(penalizer_coef=0.001)

    bgf.fit(cltv_df["frequency"],
            cltv_df["recency"],
            cltv_df["T"])

    #################################################################
    # 1 Hafta içinde en çok satın alma beklenen 10 müşteri kimdir?
    #################################################################
    bgf.conditional_expected_number_of_purchases_up_to_time(1,
                                                            cltv_df["frequency"],
                                                            cltv_df["recency"],
                                                            cltv_df["T"]) \
        .sort_values(ascending=False)

    # conditional_expected_number_of_purchases_up_to_time() fonksiyonunun muadili.
    """cltv_df["expected_purch_1_week"] = bgf.predict(1,
                                                   cltv_df["frequency"],
                                                   cltv_df["recency"],
                                                   cltv_df["T"])"""

    #################################################################
    # 4 Hafta içinde en çok satın alma beklenen 10 müşteri kimdir?
    #################################################################
    bgf.predict(4,
                cltv_df["frequency"],
                cltv_df["recency"],
                cltv_df["T"]) \
        .sort_values(ascending=False).head()

    #################################################################
    # 1 Hafta içinde ne kadar satış işlemi beklenmektedir?
    #################################################################
    bgf.predict(1,
                cltv_df["frequency"],
                cltv_df["recency"],
                cltv_df["T"]).sum()

    #################################################################
    # 12 Hafta içinde en çok satın alma beklenen 10 müşteri kimdir?
    #################################################################
    bgf.predict(12,
                cltv_df["frequency"],
                cltv_df["recency"],
                cltv_df["T"]) \
        .sort_values(ascending=False).head(10)

    """Tahmin sonuçlarının değerlendirilmesi

    plot_period_transactions(bgf)
    plt.show()"""

    ##################################
    # GAMMA-GAMMA Modelinin Kurulması
    ##################################

    ggf = GammaGammaFitter(penalizer_coef=0.01)

    ggf.fit(cltv_df["frequency"], cltv_df["monetary"])

    cltv_df["expected_average_profit"] = ggf.conditional_expected_average_profit(
        cltv_df["frequency"], cltv_df["monetary"]
    )

    ###########################################################
    # En değerli olması beklenen ilk 10 müşteri kimdir?
    ###########################################################
    ggf.conditional_expected_average_profit(cltv_df['frequency'],
                                            cltv_df['monetary']) \
        .sort_values(ascending=False).head(10)

    ##################################
    # BG_NBD ve GAMMA-GAMMA ile CLTV HESAPLANMASI
    ##################################

    cltv = ggf.customer_lifetime_value(
        bgf, cltv_df["frequency"],
        cltv_df["recency"],
        cltv_df["T"],
        cltv_df["monetary"],
        time=month,  # 3 aylık
        freq="W",  # T'nin frekans bilgisi
        discount_rate=0.01
    )

    cltv = cltv.reset_index()

    cltv_final = cltv_df.merge(cltv, on="Customer ID", how="left")

    ##################################
    # CLTV'ye göre Segmentlerin oluşturulması
    ##################################

    cltv_final["segment"] = pd.qcut(cltv_final["clv"], 4, labels=["D", "C", "B", "A"])

    return cltv_final


df = df_.copy()

cltv_result = create_cltv_p(df)

cltv_result.groupby("segment").agg({
    "expected_average_profit": ["mean", "std"],
    "clv": ["mean", "std"]
})

# cltv_2.to_csv("cltv_prediction.csv")
