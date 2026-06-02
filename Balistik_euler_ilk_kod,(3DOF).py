import random
import json
import matplotlib.pyplot as plt
import math
from mpl_toolkits.mplot3d import Axes3D
#----------------------------------------------------------------------------------------------------------------------------------#
def calculate_drag_coefficient(mach, bc, model="G7"):     #bu bir komut bloğudur G1/7 değerlerini dinamik hesaplamamızı sağlıyor
    if model=="G1":
        if mach<0.8:
            cd_referans=0.20
        elif 0.8<=mach<1.2:
            cd_referans=0.20+(mach-0.8)*1.0  #hızlı artış drag rise
        else:
            cd_referans = 0.35 - (mach - 1.2) * 0.1 # Yavaş düşüş
    
    elif model=="G7":   
        if mach<0.9:
            cd_referans = 0.15
        elif 0.9<=mach<1.1:
            cd_referans = 0.15 + (mach - 0.9) * 1.5 # Daha dik artış
        else:
            cd_referans = 0.30 - (mach - 1.1) * 0.05 # Daha yavaş düşüş
    else:
        cd_referans = 0.20 # Varsayılan
    cd_anlik=cd_referans/bc
    return cd_anlik    
                           
print("-" * 57)
print("3B GELİŞMİŞ BALİSTİK SİMÜLASYON TERMİNALİ v1.0")
print("Hava Yoğunluğu, Coriolis, Eötvös ve Magnus Etkileri Aktif")
print("-" * 57)
try:
    mermi_kutuphanesi={
    "7.62_NTO":{"kalibre":7.62,
                "m":9.5,
                "A_yan": 150.0,
                "Sg": 1.5,
                "v": 850.0,
                "C_aj": 0.6,
                "G1Bc":0.390,
                "G7BC":0.190
                },
    "338_Lapua":{"kalibre": 8.58,
                 "m": 16.2,
                 "A_yan": 210.0,
                 "Sg": 1.4,
                 "v": 910.0,
                 "C_aj": 0.5,
                 "G1Bc":0.620,
                 "G7BC":0.315
                 }
    }
    
    try:
        with open("mermilerim.json", "r", encoding="utf-8") as f:
            mermi_kutuphanesi.update(json.load(f))
            print(" Kayıtlı mermiler dosyadan yüklendi.")
    except FileNotFoundError:
        print(" Kayıtlı mermi dosyası bulunamadı, varsayılanlar kullanılıyor.") 
    mermi_secimi=input("Lütfen kullandığınız mermiyi giriniz")   
    if mermi_secimi in mermi_kutuphanesi:
        veriler=mermi_kutuphanesi[mermi_secimi]
        kalibre=veriler["kalibre"]/1000
        m=veriler["m"]/1000                            
        A_yan=veriler["A_yan"]/1000000
        Sg=veriler["Sg"]
        v=veriler["v"]
        C_aj=veriler.get("C_aj",0.7)
        G1Bc = veriler.get("G1Bc", 0.400)
        G7Bc = veriler.get("G7BC", 0.200)
    else:
        k=float(input("lütfen merminizin kalibresini giriniz")) #mm
        kutle = float(input("lütfen merminin kütlesini giriniz")) # gram
        ayan = float(input("lütfen merminin yanal alanını giriniz")) # mm2
        stabili = float(input("lütfen Sg değerini giriniz"))
        hiz = float(input("lütfen ilk hızı giriniz")) #m/s
        caj = float(input("lütfen Aerodynamic Jump katsayısını (C_aj) giriniz"))
        g1bc = float(input("lütfen G1 BC değerini giriniz: "))
        g7bc = float(input("lütfen G7 BC değerini giriniz: "))
        mermi_kutuphanesi[mermi_secimi]={
            "kalibre":k,
            "m":kutle,
            "A_yan":ayan,
            "Sg":stabili,
            "v":hiz,
            "C_aj":caj,
            "G1Bc": g1bc, 
            "G7BC": g7bc
        }
        kalibre=k/1000
        m=kutle/1000
        A_yan = ayan / 1000000
        Sg = stabili
        v = hiz
        C_aj=caj
        G1Bc = g1bc
        G7Bc = g7bc
        with open("mermilerim.json", "w", encoding="utf-8") as f:
            json.dump(mermi_kutuphanesi, f, indent=4)
    model_secimi=input("hangi balistik modeli kullanırsınız (G1/G7)")
    if model_secimi not in ["G1","G7"]:
        model_secimi="G7"
        print("geçersiz seçim varsayılan G7 kullanılıyor")
    current_bc = G1Bc if model_secimi == "G1" else G7Bc

    g=float(input("lütfen yerçekimi ivmesini giriniz"))
    derece=float(input("lütfen sinüsün derecesini yazınız"))
    rüzgar_dik=float(input("lütfen dikine gelen rüzgar varsa belirtiniz"))
    rüzgar_yan=float(input("lütfen yandan gelen rüzgar varsa belirtiniz"))
    p_basinc=float(input("lütfen şu anki basınç değerini yazınız"))
    T=float(input("lütfen sıcaklığı celcius cinsinden giriniz"))
    N=float(input("lütfen nem yüzdesini giriniz"))
    enlem=float(input("lütefn enlemi giriniz"))
    pusula_acisi=float(input("lütfen pusula açısını yazınız"))
    namlu_yüksekligi=float(input("lütfen namlunun yere uzaklığını yazınız"))
    yiv_varligi=input("silah yivli mi? evet/hayır").strip().lower()                              
    if yiv_varligi!="evet" and yiv_varligi!="hayır":                          
        print("lütfen sadece evet ya da hayır yazınız")
    if yiv_varligi=="evet":
        helis_yonu=input("lütfen helis yönünü yazınız sağ/sol").strip().lower() 
        if helis_yonu!="sağ" and helis_yonu!="sol":
            print("lütfen sadece sağ ya da sol diyin")
      
    omega=7.2921*10**-5
    A=math.pi*((kalibre/2)**2)

    psat=6.1087*10**(7.5*(T)/((T)+237.3))
    pv=psat*(N*0.01)
    pd=p_basinc-pv
    p_namlu = ((pd * 100) / (287.058 * (T + 273.15))) + ((pv * 100) / (461.495 * (T + 273.15)))
    P_toplam=1013.25
    R_nemli=287.05 / (1 - (pv / P_toplam) * (1 - 287.05 / 461.495))
    p_deniz=((pd*100)/(287.058*(T+273.15)))+((pv*100)/(461.495*(T+273.15)))   
    radyan_aci=math.radians(derece)
    sinüs_degeri=math.sin(radyan_aci)
    cosinüs_degeri=math.cos(radyan_aci)     
    t=0
    max_yükseklik=0+namlu_yüksekligi
    x_koordinatlari=[]
    y_koordinatlari=[]
    z_koordinatlari=[]
    vx=v*cosinüs_degeri
    vz=v*sinüs_degeri
    vy=rüzgar_yan
    uzaklik=0
    yükseklik=0+namlu_yüksekligi
    yatay_sapma=0
    if yiv_varligi=="evet":
        jump_hizi = (C_aj * p_namlu * (kalibre**3) * rüzgar_yan * v) / (m * Sg)
        if helis_yonu=="sağ":
            vz+=jump_hizi   
        else:
             vz-=jump_hizi
             
    while yükseklik>=0:
        h_hesap=max(0,yükseklik)
        T_kelvin=(T + 273.15) - (0.0065 * h_hesap)
        P_anlik=101325 * (1 - 0.000022557 * h_hesap)**5.2559 
        T_anlik_C = T - (0.0065 * h_hesap)
        psat_dinamik = 6.1087 * 10**(7.5 * T_anlik_C / (T_anlik_C + 237.3))
        pv_dinamik = psat_dinamik * (N * 0.01)
        P_anlik_hPa = P_anlik / 100
        R_nemli_dinamik=287.05 / (1 - (pv_dinamik / P_anlik_hPa) * (1 - 287.05 / 461.495))
        p= P_anlik / (R_nemli_dinamik * T_kelvin)
        T_anlik = T - (0.0065 * h_hesap)
        V_ses = math.sqrt(1.4 * 287.05 * T_kelvin)
        v_anlik = math.sqrt(vx**2 + vz**2 + vy**2)
        if v_anlik==0: v_anlik=0.0001
        M=v_anlik/V_ses
        cd_anlik = calculate_drag_coefficient(M, current_bc, model=model_secimi)

        if M>1.5:
            cm_anlik=0.002
        elif 0.8<M<=1.5:
            cm_anlik= 0.002 + (0.015 - 0.002) * (1.5 - M) / (1.5 - 0.8)
        else:
            cm_anlik=0.015

        phi=math.radians(enlem)
        theta=math.radians(pusula_acisi)
        a_coriolis_y=2 * omega * (vx * math.sin(phi) - vz * math.cos(phi) * math.cos(theta))
        a_coriolis_z=2*omega*vx*math.cos(phi)*math.sin(theta)
        a_coriolis_x=2 * omega * (vy * math.cos(phi) * math.cos(theta) - vz * math.cos(phi) * math.sin(theta))
            
        fd=0.5*p*v_anlik**2*cd_anlik*A
        asürtünme=fd/m
        vx=vx-((asürtünme)*(vx/v_anlik)+a_coriolis_x)*0.01  #vx in olduğu yer
        v_bagil=rüzgar_yan-vy
        F_yan=0.5*p*(abs(v_bagil)*v_bagil)*cd_anlik*A_yan
        a_yan=F_yan/m
        if yiv_varligi=="evet":
            aspin_y=0.05*(Sg+1.2)*t**0.83
            vy=vy+(a_yan+a_coriolis_y+aspin_y)*0.01  #vy'nin olduğu yerler
        elif yiv_varligi=="hayır":
            karaktersizlik_sapmasi=random.uniform(-0.001, 0.001)
            vy=vy+(a_yan+a_coriolis_y+karaktersizlik_sapmasi)*0.01  #vy'nin olduğu yerler

        if yiv_varligi=="evet" and v_anlik>0.1:
            a_magnus_z=0.5*p*v_anlik**2*A*cm_anlik*(rüzgar_yan/v_anlik)/m
            if helis_yonu=="sol":
                vz=vz-(g + ((asürtünme) * (vz / v_anlik)) - a_coriolis_z + a_magnus_z) * 0.01
            else:
                vz=vz - (g + ((asürtünme) * (vz / v_anlik)) - a_coriolis_z - a_magnus_z) * 0.01           
        else:
            vz=vz-(g+((asürtünme)*(vz/v_anlik))-a_coriolis_z)*0.01 #vz'nin olduğu yer

        yükseklik+=(vz)*0.01
        uzaklik+=(vx+rüzgar_dik)*0.01
        yatay_sapma+=vy*0.01
        x_koordinatlari.append(uzaklik)
        y_koordinatlari.append(yatay_sapma)
        z_koordinatlari.append(yükseklik)
        if yükseklik>max_yükseklik:
            max_yükseklik=yükseklik
        t=t+0.01
        if yükseklik<0:
            break
    v_son=math.sqrt(vx**2+vy**2+vz**2)
    enerji_joule=0.5*m*v_son**2
    print(f"\n---ATIŞ SONUÇLARI---")
    print(f"Maksimum Yükseklik (Yer Seviyesi): {max_yükseklik:.2f} m") 
    print(f"Havada Kalış Süresi: {t:.2f} s")
    print(f"Merminin Yere Çarpma Hızı: {v_son:.2f} m/s")
    print(f"Merminin Yere Çarpma Enerjisi: {enerji_joule:.2f} Joule")
    
    fig=plt.figure(figsize=(12,8))
    ax=fig.add_subplot(111, projection='3d')

    ax.plot(x_koordinatlari, y_koordinatlari, z_koordinatlari, label='Mermi Yörüngesi', color='blue', linewidth=2)
    ax.scatter(0, 0, namlu_yüksekligi, color='red', s=100, label='Atış Noktası')
    ax.plot([0, max(x_koordinatlari)], [0, 0], [0, 0], color='black', linestyle='--', alpha=0.3, label='İdeal Hat')
    ax.set_title('3B Balistik Atış Simülasyonu')
    ax.set_xlabel('Menzil (X) - Metre')
    ax.set_ylabel('Yan Sapma (Y) - Metre')
    ax.set_zlabel('Yükseklik (Z) - Metre')
    ax.set_zlim(0,max(z_koordinatlari)+5)
    x_son=x_koordinatlari[-1]
    y_son=y_koordinatlari[-1]
    z_son=z_koordinatlari[-1]

    plt.legend()
    ax.scatter(x_son, y_son, z_son)
    f"X: {x_son:.1f}m"
    f"Y: {y_son:.1f}m"
    f"Z: {z_son:.1f}m"

    ax.text(x_son, y_son, z_son+5, f"X: {x_son:.1f}m \n Y: {y_son:.1f}m \n Z: {z_son:.1f}m")
    ax.invert_yaxis()
    plt.show()
except ValueError:
    print("lütfen sayı giriniz") 

    #PROJE: Balistik Atış Simülasyonu
    #PROJE SAHİBİNİN ADI SOYADI: Kıvanç Altıntopu
    #PROJE SAHİBİNİN BÖLÜMÜ: Makine Mühendisliği Hazırlık Öğrencisi
    #OKULUN ADI: Manisa Celal Bayar Üniversitesi Mühendislik ve Doğa Bilimlei Kampüsü
    #PROJENİN BİTİŞ TARİHİ: 24.02.2026
    
    #----------GÜNCELLEMELER----------#

    #Tarih:28.02.2026:
    # Mermi kütüphanesi eklerndi artık merminin gerekli değerlerini (yanal alanı.vb)
    #direk merminin türüne göre kütüphaneden seçiyor kütüphanede olamayan mermileri ise verileri ile birlikte kaydediyor
    
    #Tarih:2.03.2026:
    #Mermilerdeki G1 ve G7 katsayıları eklendi 
    #Atmosferdeki etkenler gerçek hayata daha yakın olacak şekil daha dinamikleştirildi 
