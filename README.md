# Müşteri Yaşam Boyu Değeri(CLTV) nedir?

-    Müşteri yaşam boyu değeri (CLTV), müşteri deneyimi programının bir parçası olarak izlenmesi gereken önemli istatistiklerden biridir. CLTV, yalnızca satın alma bazında değil, tüm ilişki genelinde bir müşterinin şirketiniz için ne kadar değerli olduğunun bir ölçümüdür.
-    CLTV, bir müşterinin tüm ilişkileri boyunca bir işletmeye verdiği toplam değerdir. Mevcut müşterileri elde tutmak, yenilerini kazanmaktan daha az maliyetli olduğu için önemli bir ölçümdür, bu nedenle mevcut müşterilerinizin değerini artırmak, büyümeyi sağlamak için harika bir yoldur.
-    CLV'yi bilmek, işletmelerin kar marjlarını korurken yeni müşteriler edinme ve mevcut müşterileri elde tutma stratejileri geliştirmelerine yardımcı olur.


## Customer Life Time Value Prediction by Using BG-NBD & Gamma-Gamma (BG-NBD ve Gamma-Gamma modelleri ile CLTV Tahmini)

Bu teknikleri kullanarak:
  -   Önümüzdeki dönemde hangi müşteri ne kadar alım yapacak? 
  -   Önümüzdeki dönemde en çok satın alma işlemini hangi ilk N müşterilerin yapması bekleniyor?
  -   Müşteri, işimiz için nasıl bir değer yaratacak?
  
gibi önemli değerlerin cevabını bulabiliriz.


*    BG-NBD Modeli, her müşterinin satın alma davranışlarının dağılımını modelleyecek ve her müşteri için beklenen işlem sayısını tahmin edecektir.

*    Gama-Gama Alt Modeli, beklenen ortalama kar dağılımını modelleyecek ve her müşteri için beklenen ortalama karı tahmin edecektir.

### BG-NBD Model

-   BG-NBD Modeli olarak bilinen Beta Geometrik / Negatif Binom Dağılımıdır. **Buy Till You Die** (Ölene Kadar Al) olarak da karşımıza çıkabilir. 
Bize bir sonraki dönemde koşullu beklenen işlem sayısını verir. 
    *   Bu model aşağıdaki sorulara cevap verebilir:
        -   Önümüzdeki hafta kaç işlem(Transaction) olacak? 
        -   Önümüzdeki 3 ayda kaç işlem olacak?
        -   Önümüzdeki 2 hafta içinde en çok satın alma işlemini hangi müşteriler yapacak?
        
Bu model, beklenen işlem sayısını tahmin etmek için olasılığı kullanarak 2 süreci modeller.
    -   Transaction Process (Buy)
    -   Dropout Process (Till You Die)   

### Gamma-Gamma Submodel
-   Bu modeli, her bir müşteri için ne kadar ortalama kâr elde edebileceğimizi tahmin etmek için kullanırız. Kitle için ortalama karı modelledikten sonra bize her müşteri için beklenen ortalama karı verir.

        -   Bir müşterinin parasal değeri (bir müşterinin işlem miktarlarının toplamı), işlem değerlerinin ortalaması etrafında rastgele dağıtılacaktır. 
        -   Ortalama bir işlem değeri müşteriler arasındaki dönemlerde değişebilir ancak bir müşteri için değişmez. 
        -   Ortalama işlem değeri, tüm müşteriler arasında gama olarak dağıtılacaktır.
