import random
import json
import matplotlib.pyplot as plt
import math
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

#G1 G7 katsayıları
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
print("3B BALİSTİK SİMÜLASYON TERMİNALİ v1.0")
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

    #yiv sorgulama
    yiv_varligi=input("silah yivli mi? evet/hayır").strip().lower()                                  
    if yiv_varligi!="evet" and yiv_varligi!="hayır":                          
        print("lütfen sadece evet ya da hayır yazınız")
    if yiv_varligi=="evet":
        helis_yonu=input("lütfen helis yönünü yazınız sağ/sol").strip().lower() 
        if helis_yonu!="sağ" and helis_yonu!="sol":
            print("lütfen sadece sağ ya da sol diyin")

        with open("mermilerim.json", "w", encoding="utf-8") as f:
            json.dump(mermi_kutuphanesi, f, indent=4)
    model_secimi=input("hangi balistik modeli kullanırsınız (G1/G7)")
    if model_secimi not in ["G1","G7"]:
        model_secimi="G7"
        print("geçersiz seçim varsayılan G7 kullanılıyor")
    current_bc = G1Bc if model_secimi == "G1" else G7Bc

    # --- ÇEVRE KOŞULLARI SÖZLÜĞÜ ---
    env = {
        "g": 9.80665,        # Yerçekimi
        "T": 2.0,           # Sıcaklık (C)
        "P_basinc": 1225.0, # Basınç (hPa/mbar)
        "N": 50.0,           # Nem (%)
        "enlem": 38.6,       # Enlem
        "pusula": 0,       # Atış yönü
        "rüzgar_dik": 0.0,
        "rüzgar_yan": -5,
        "namlu_yüksekligi": 1.5,
        "derece":1.0  #atış açısı
    }

    #Rk4 modeli için mermi verilerini paketledik
    bullet_data = {
    "m": m,
    "kalibre": kalibre,
    "bc": current_bc,
    "model": model_secimi,
    "Sg": Sg,
    "A_yan": A_yan
    }
    
    #dürbün sıfırlama talebine göre vektörlerin başlangıç durumunun hesaplanması 
    saglama=input("daha önce atış yaptınız mı evet/hayır").strip().lower()
    if saglama=="hayır":
        radyan_aci = math.radians(env["derece"])
        vx_ilk = v * math.cos(radyan_aci)
        vz_ilk = v * math.sin(radyan_aci)
        vy_ilk = env["rüzgar_yan"]  
    elif saglama=="evet":
        sifirlama=input("dürbünü sıfırlamak ister misiniz evet/hayır").strip().lower() 
        if sifirlama=="evet":
            dikey_MIL=float(input("dikeydeki düzeltme önerisini giriniz"))
            dikey_MIL_derece=dikey_MIL*0.0573

            yatay_MIL=float(input("yataydaki düzeltme önerisini giriniz (sayıyı sapmanın ters işaretlisi olarak girin)"))
            yatay_MIL_derece=yatay_MIL*0.0573
            sapma_yan_radyan = math.radians(yatay_MIL_derece)

            radyan_aci = math.radians(env["derece"]+dikey_MIL_derece)
            vx_ilk = v * math.cos(radyan_aci)
            vz_ilk = v * math.sin(radyan_aci)
            vy_ilk = env["rüzgar_yan"]+(vx_ilk * math.tan(sapma_yan_radyan))
        elif sifirlama=="hayır":
            radyan_aci = math.radians(env["derece"])
            vx_ilk = v * math.cos(radyan_aci)
            vz_ilk = v * math.sin(radyan_aci)
            vy_ilk = env["rüzgar_yan"]
    else:
        print("lütfen sadece evet ya da hayır diyin") 

    max_yükseklik=0+env["namlu_yüksekligi"]

    #Namludaki basınç (aerodinamik jump için lazım)
    psat_statik=6.1087*10**(7.5*(env["T"])/((env["T"])+237.3))
    pv_statik=psat_statik*(env["N"]*0.01)
    pd_statik=env["P_basinc"]-pv_statik
    p_namlu = ((pd_statik * 100) / (287.058 * (env["T"]+ 273.15))) + ((pv_statik * 100) / (461.495 * (env["T"] + 273.15)))
    uzaklik=0
    yükseklik=0+env["namlu_yüksekligi"]
    yatay_sapma=0

    #Aerodinamik jump
    if yiv_varligi=="evet":
        jump_hizi = (C_aj * p_namlu * (kalibre**3) * env["rüzgar_yan"] * v) / (m * Sg) 
        if helis_yonu=="sağ":
            vz_ilk+=jump_hizi   
        else:            
            vz_ilk-=jump_hizi
            
    state = np.array([0.0, 0.0, env["namlu_yüksekligi"], vx_ilk, vy_ilk, vz_ilk])    
    t = 0
    dt = 0.01 # Zaman adımı
    x_yolu, y_yolu, z_yolu = [], [], []


    def get_accelerations(state, env, bullet, t):
        x, y, z, vx, vy, vz = state
        v_anlik = math.sqrt(vx**2 + vy**2 + vz**2)
        if v_anlik < 0.1: return np.zeros(6)

        z0 = 0.015 
        z_ref = 2.0  
        v_wind_ref = env["rüzgar_yan"] 
        
        if z > z0:
            v_wind_anlik = v_wind_ref * (math.log(z / z0) / math.log(z_ref / z0))
        else:
            v_wind_anlik = 0.0

        v_rel_x = vx + env["rüzgar_dik"]
        v_rel_y = vy - v_wind_anlik
        v_rel_z = vz
        v_anlik_rel = math.sqrt(v_rel_x**2 + v_rel_y**2 + v_rel_z**2)
        
        #Nem faktörü içine katılmış ISA basınç hesaplama sistemi
        T_kelvin = (env['T'] + 273.15) - (0.0065 * z)
        T_anlik_C=env['T'] - (0.0065 * z)
        P_anlik = 101325 * (1 - 0.000022557 * z)**5.2559
        psat =6.1078 * 10**(7.5 * T_anlik_C / (T_anlik_C + 237.3))
        pv = psat * (env["N"]/ 100)
        pd_anlik = P_anlik - (pv*100)
        rho = ((pd_anlik ) / (287.05 * T_kelvin)) + ((pv * 100) / (461.5 * T_kelvin))

        #Mach ve Drag
        V_ses = math.sqrt(1.4 * 287.05 * T_kelvin)
        v_anlik = math.sqrt(vx**2 + vz**2 + vy**2)
        if v_anlik==0: v_anlik=0.0001
        M=v_anlik_rel/V_ses
        if M>1.5:
            cm_anlik=0.002
        elif 0.8<M<=1.5:
            cm_anlik= 0.002 + (0.015 - 0.002) * (1.5 - M) / (1.5 - 0.8)
        else:
            cm_anlik=0.015
        cd=calculate_drag_coefficient(M, current_bc, model=model_secimi)   
        A=math.pi*(bullet["kalibre"]/2)**2
        f_drag = 0.5 * rho * v_anlik_rel**2 * cd * A
        a_drag = f_drag / bullet['m']

        ax_drag = -(a_drag * (v_rel_x / v_anlik_rel))
        ay_drag = -(a_drag * (v_rel_y / v_anlik_rel))
        az_drag = -(a_drag * (v_rel_z / v_anlik_rel))

        #Coriolis hesaplamaları 
        omega = 7.2921e-5
        phi = math.radians(env['enlem'])
        theta = math.radians(env['pusula'])
        
        ax_cor = 2 * omega * (vy * math.cos(phi) * math.cos(theta) - vz * math.cos(phi) * math.sin(theta))
        ay_cor = 2 * omega * (vx * math.sin(phi) - vz * math.cos(phi) * math.cos(theta))
        az_cor = 2 * omega * vx * math.cos(phi) * math.sin(theta)

        #Spin drift hesabı 
        if yiv_varligi=="evet":
            a_spin_y = 0.05 * (bullet['Sg'] + 1.2) * t**0.83
        else:
            karaktersizlik_sapmasi=random.uniform(-0.001, 0.001)
            a_spin_y=(ay_drag+ay_cor+karaktersizlik_sapmasi)

        #Magnus hesabı (yive bağlı)
        if yiv_varligi=="evet":
            a_magnus_mag = (0.5 * rho * v_anlik_rel**2 * A * cm_anlik) / bullet['m']
            a_magnus_z =a_magnus_mag * (v_rel_y / v_anlik_rel)
            if helis_yonu == "sağ":
                az_magnus_final = a_magnus_z 
            else:
                az_magnus_final = -a_magnus_z 

        #Merminin yanal alanına bağlı rüzgar ivmesi    
        f_yanrüzgar = 0.5 * rho * (v_rel_y**2) * cd * bullet["A_yan"]
        a_yanrüzgar = (f_yanrüzgar / bullet['m']) * np.sign(v_rel_y)
        
        #Nihai bileşen hesabı
        dvx = ax_drag + ax_cor
        dvy = ay_drag + ay_cor+a_spin_y+a_yanrüzgar
        if yiv_varligi=="evet":
            dvz = az_drag + az_cor + az_magnus_final - env['g']
        else:
            dvz = az_drag + az_cor - env['g']


        return np.array([vx, vy, vz, dvx, dvy, dvz])

    print(f"\nAteşleniyor: {mermi_secimi}...")

    while state[2] >= 0:  # Mermi yere düşene kadar
        x_yolu.append(state[0])
        y_yolu.append(state[1])
        z_yolu.append(state[2])

        if state[2] > max_yükseklik:
            max_yükseklik = state[2]
    
        # RK4 Çekirdeği
        k1 = get_accelerations(state, env, bullet_data, t)
        k2 = get_accelerations(state + k1 * dt / 2, env, bullet_data, t + dt / 2)
        k3 = get_accelerations(state + k2 * dt / 2, env, bullet_data, t + dt / 2)
        k4 = get_accelerations(state + k3 * dt, env, bullet_data, t + dt)
    
        state = state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
        t += dt
    
        if state[0] > 10000: break # 10km güvenlik sınırı 
    
    
    v_son=math.sqrt(state[3]**2 + state[4]**2 + state[5]**2)
    enerji_joule=0.5*m*v_son**2
    print(f"\n---ATIŞ SONUÇLARI---")
    print(f"Maksimum Yükseklik (Yer Seviyesi): {max_yükseklik:.2f} m") 
    print(f"Havada Kalış Süresi: {t:.2f} s")
    print(f"Merminin Yere Çarpma Hızı: {v_son:.2f} m/s")
    print(f"Merminin Yere Çarpma Enerjisi: {enerji_joule:.2f} Joule")
    
    fig=plt.figure(figsize=(12,8))
    ax=fig.add_subplot(111, projection='3d')

    ax.plot(x_yolu, y_yolu, z_yolu, label='Mermi Yörüngesi', color='blue', linewidth=2)
    ax.scatter(0, 0, env["namlu_yüksekligi"], color='red', s=100, label='Atış Noktası')
    ax.plot([0, max(x_yolu)], [0, 0], [0, 0], color='black', linestyle='--', alpha=0.3, label='İdeal Hat')
    ax.set_title('3B Balistik Atış Simülasyonu')
    ax.set_xlabel('Menzil (X) - Metre')
    ax.set_ylabel('Yan Sapma (Y) - Metre')
    ax.set_zlabel('Yükseklik (Z) - Metre')
    ax.set_zlim(0,max(z_yolu)+5)
    x_son=x_yolu[-1]
    y_son=y_yolu[-1]
    z_son=z_yolu[-1]

    plt.legend()
    ax.scatter(x_son, y_son, z_son)
    f"X: {x_son:.1f}m"
    f"Y: {y_son:.1f}m"
    f"Z: {z_son:.1f}m"

    ax.text(x_son, y_son, z_son+5, f"X: {x_son:.1f}m \n Y: {y_son:.1f}m \n Z: {z_son:.1f}m")
    # =============================================================================
    # OPTİK DÜZELTME VE BİRİM DÖNÜŞÜMÜ (MIL to MOA)
    # -----------------------------------------------------------------------------
    # MIL (Miliradyan): 1/1000 radyan. 1000m'de 1m sapmaya denk gelir.
    # MOA (Minute of Angle): 1 derecenin 1/60'ı (1 ark-dakika). 
    #
    # İSPAT (Neden 3.438?):
    # 1 Tam Daire = 360 derece = 21,600 MOA (360 * 60)
    # 1 Tam Daire = 2 * PI radyan = 6,283.185 MIL (2 * PI * 1000)
    # Dönüşüm Katsayısı = 21,600 / 6,283.185 ≈ 3.437746... (Kısaca 3.438)
    # =============================================================================
    x_son = state[0]
    y_son = state[1]
    z_son = state[2]
    
    if x_son > 0:
        # 1. Dikey Düşüş (Elevation): 
        # Mermi namlu yüksekliğinden (örneğin 1.5m) çıkıp yere (0m) düştü.
        # Eğer hedef de namluyla aynı yükseklikteyse, mermi toplamda namlu yüksekliği kadar düşmüştür.
        dikey_fark_m = env["namlu_yüksekligi"] - z_son
        
        mil_dikey = (dikey_fark_m / x_son) * 1000
        moa_dikey = mil_dikey * 3.438
        
        # 2. Yatay Sapma (Windage):
        # Rüzgar ve Spin Drift mermiyi sağa (pozitif Y) ittiyse, dürbünü SOLA (negatif) çekmelisin.
        mil_yatay = (-y_son / x_son) * 1000
        moa_yatay = mil_yatay * 3.438

    print(f"\n--- DÜRBÜN AYARLARI (CLICK ADVICE) ---")
    print(f"Hedef Menzili: {x_son:.1f} m")
    print(f"Dikey (Elevation): {mil_dikey:.2f} MIL / {moa_dikey:.2f} MOA (YUKARI KLİK)")
    print(f"Yatay (Windage):   {abs(mil_yatay):.2f} MIL / {abs(moa_yatay):.2f} MOA " + ("SOLA" if y_son > 0 else "SAĞA"))
    ax.invert_yaxis()

    plt.show()

except ValueError:
    print("lütfen sayı giriniz")
except Exception as e:
    print(f"\nSistemsel Hata: {e}")
 


    #PROJE: Balistik Atış Simülasyonu
    #PROJE SAHİBİNİN ADI SOYADI: Kıvanç Altıntopu
    #PROJE SAHİBİNİN BÖLÜMÜ: Makine Mühendisliği Hazırlık Öğrencisi
    #OKULUN ADI: Manisa Celal Bayar Üniversitesi Mühendislik ve Doğa Bilimlei Kampüsü
    #PROJENİN BİTİŞ TARİHİ: 24.02.2026
    
    #----------GÜNCELLEMELER----------#

    #Tarih:28.02.2026:
    # * Mermi kütüphanesi eklerndi artık merminin gerekli değerlerini (yanal alanı.vb)
    #direk merminin türüne göre kütüphaneden seçiyor kütüphanede olamayan mermileri ise verileri ile birlikte kaydediyor
    
    #Tarih:02.03.2026:
    # * Mermilerdeki G1 ve G7 katsayıları eklendi 
    # * Atmosferdeki etkenler gerçek hayata daha yakın olacak şekil daha dinamikleştirildi

    #Tarih:06.03.2026:
    # * Kullanıcıdan alınması gereken değerler input yerine sözlük yapısı olarak alınacak şekilde ayarlandı 
    #böylece artık değerleri girmek daha kolay hale gelecek
    # * Balistik atış simülasyonu RK4 sistemine göre en baştan ayarlandı böylece artık daha keskin sonuçlar alınabiliyor.

    #Tarih:08.03.2026
    #*Dürbün sıfırlama talebine göre vektörlerin başlangıç durumunun hesaplanması bu ayarlalarla birlikte aynı verilerle atılan
    #ikinci atış 0 veya diğerki duruma göre 0'a çok daha yakın sapma yapıyor