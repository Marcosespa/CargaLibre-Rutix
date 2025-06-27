import ssl
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, WebDriverException

def clean_location_text(text):
    if not text or text == "No disponible":
        return "No disponible"
    unwanted_texts = [
        "more_vert", "directions_car", "filter_list", "Ubicación no disponible",
        "hace más de", "En ruta con otra empresa", "search refresh", "Vehículos",
        "Limpiar filtros", "Estado", "Viajes", "Grupos", "Búsqueda de vehículo avanzada"
    ]
    cleaned_text = text
    for unwanted in unwanted_texts:
        cleaned_text = cleaned_text.replace(unwanted, "").strip()
    cleaned_text = " ".join(cleaned_text.split())
    return cleaned_text if cleaned_text else "No disponible"

def split_coordinates(coords):
    if not coords or coords == 'No disponible':
        return '', ''
    coords_clean = coords.replace(' ', '').strip()
    if ',' in coords_clean:
        lat, lon = coords_clean.split(',', 1)
    elif ';' in coords_clean:
        lat, lon = coords_clean.split(';', 1)
    else:
        return '', ''
    try:
        float(lat)
        float(lon)
        return lat.strip(), lon.strip()
    except ValueError:
        return '', ''

def scrape_satrack_optimizado(username, password):
    """
    Versión optimizada del scraping de Satrack con tiempos reducidos y mejor manejo de errores
    """
    # Configurar SSL
    ssl._create_default_https_context = ssl._create_unverified_context

    # Configurar Chrome con opciones optimizadas
    options = uc.ChromeOptions()
    options.add_argument("--headless")  # Ejecutar sin interfaz gráfica (más rápido)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-images")  # No cargar imágenes (más rápido)
    options.add_argument("--disable-javascript")  # Deshabilitar JS si no es necesario
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36')
    
    # Configuraciones de rendimiento
    prefs = {
        "profile.default_content_setting_values": {
            "images": 2,  # No cargar imágenes
            "plugins": 2,  # No cargar plugins
            "popups": 2,   # Bloquear popups
            "geolocation": 2,  # Bloquear geolocalización
            "notifications": 2,  # Bloquear notificaciones
            "media_stream": 2,  # Bloquear media stream
        }
    }
    options.add_experimental_option("prefs", prefs)
    
    driver = None
    try:
        # Inicializar driver con timeouts más agresivos
        driver = uc.Chrome(options=options)
        driver.set_page_load_timeout(30)  # Reducido de 60 a 30
        driver.set_script_timeout(30)     # Reducido de 60 a 30
        
        print(f"🌐 Iniciando sesión para: {username}")
        
        # Navegar a la página de login
        driver.get("https://login.satrack.com/login")
        time.sleep(2)  # Reducido de 5 a 2
        
        # Login optimizado
        try:
            # Usuario
            user_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'txt_login_username'))
            )
            user_input.clear()
            user_input.send_keys(username)
            time.sleep(0.5)  # Reducido de 1 a 0.5
            
            # Contraseña
            password_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'txt_login_password'))
            )
            password_input.clear()
            password_input.send_keys(password)
            time.sleep(0.5)  # Reducido de 1 a 0.5
            
            # Login
            driver.execute_script("""
                let loginButton = document.querySelector('button[type="submit"], button.login-button, input[type="submit"]');
                if (loginButton) {
                    loginButton.click();
                }
            """)
            
            # Verificar login exitoso (timeout reducido)
            try:
                error_message = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((
                        By.XPATH, 
                        "//div[contains(text(), 'incorrec') or contains(text(), 'inválid') or contains(text(), 'error')]"
                    ))
                )
                print(f"❌ Error de login para {username}")
                return None
            except TimeoutException:
                print(f"✅ Login exitoso para {username}")
            
            # Esperar redirección (reducido significativamente)
            time.sleep(10)  # Reducido de 30 a 10
            
            current_url = driver.current_url
            if "portal.satrack.com" not in current_url:
                print(f"❌ No se redirigió al portal para {username}")
                return None
            
            # Esperar carga de vehículos (reducido)
            time.sleep(15)  # Reducido de 45 a 15
            
            # Obtener vehículos de manera optimizada
            vehicles_info = obtener_vehiculos_optimizado(driver)
            
            if vehicles_info:
                return {
                    'timestamp': time.strftime('%d/%m/%Y %H:%M:%S'),
                    'summary': {
                        'total_vehicles': len(vehicles_info),
                        'vehicles_with_location': sum(1 for v in vehicles_info if v['location'] != "No disponible"),
                    },
                    'vehicles': vehicles_info
                }
            else:
                print(f"⚠️  No se encontraron vehículos para {username}")
                return None
                
        except TimeoutException as e:
            print(f"⏰ Timeout en login para {username}: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ Error en login para {username}: {str(e)}")
            return None
            
    except Exception as e:
        print(f"❌ Error general para {username}: {str(e)}")
        return None
        
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def obtener_vehiculos_optimizado(driver):
    """
    Obtiene la información de vehículos de manera optimizada
    """
    try:
        # Selectores optimizados (menos selectores, más específicos)
        selectors = [
            "//div[contains(@class, 'vehicle-list')]//div[contains(@class, 'item')]",
            "//div[contains(@class, 'vehicle')]//div[contains(@class, 'plate')]",
            "//div[contains(@class, 'list')]//div[contains(@class, 'vehicle')]"
        ]
        
        vehicle_elements = None
        
        # Probar selectores rápidamente
        for selector in selectors:
            try:
                WebDriverWait(driver, 5).until(  # Reducido de 10 a 5
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                vehicle_elements = driver.find_elements(By.XPATH, selector)
                if vehicle_elements:
                    break
            except:
                continue
        
        if not vehicle_elements:
            print("⚠️  No se encontraron vehículos")
            return []
        
        print(f"🚗 Encontrados {len(vehicle_elements)} vehículos")
        vehicles_info = []
        
        # Procesar vehículos de manera más rápida
        for index, vehicle in enumerate(vehicle_elements[:20], 1):  # Limitar a 20 vehículos máximo
            try:
                vehicle_text = vehicle.text.strip()
                if not vehicle_text or len(vehicle_text) < 3:
                    continue
                
                # Hacer clic rápido
                driver.execute_script("arguments[0].click();", vehicle)
                time.sleep(1)
                
                # Extraer ubicación del popup si existe
                location = "No disponible"
                try:
                    popup = driver.find_element(By.CSS_SELECTOR, ".gm-style-iw")
                    popup_text = popup.text.strip()
                    location = clean_location_text(popup_text)
                except Exception:
                    pass
                
                # Buscar coordenadas en el DOM
                coords = "No disponible"
                try:
                    coords = driver.execute_script("""
                        const elements = document.querySelectorAll('*');
                        for (const el of elements) {
                            if (el.offsetParent !== null) {
                                const text = el.textContent;
                                const coordPattern = /Lat\\/Long:\\s*([-]?\\d+\\.\\d+),\\s*([-]?\\d+\\.\\d+)/i;
                                const match = text.match(coordPattern);
                                if (match) {
                                    return `${match[1]}, ${match[2]}`;
                                }
                            }
                        }
                        return 'No disponible';
                    """)
                except Exception:
                    pass
                lat, lon = split_coordinates(coords)
                vehicle_info = {
                    'plate': vehicle_text,
                    'location': location,
                    'coordinates': coords,
                    'lat': lat,
                    'lon': lon
                }
                
                vehicles_info.append(vehicle_info)
                
                # Pausa mínima entre vehículos
                time.sleep(0.5)  # Reducido de 2 a 0.5
                
            except Exception as e:
                continue
        
        return vehicles_info
        
    except Exception as e:
        print(f"❌ Error obteniendo vehículos: {str(e)}")
        return []

# Función de compatibilidad
def scrape_satrack(username, password):
    """Wrapper para mantener compatibilidad con el código existente"""
    return scrape_satrack_optimizado(username, password)

if __name__ == "__main__":
    # Prueba rápida
    username = "motocargasas"
    password = "JU@nse0914"
    
    print("🚀 Iniciando prueba de scraping optimizado...")
    result = scrape_satrack_optimizado(username, password)
    
    if result:
        print("\n✅ Datos obtenidos exitosamente:")
        print(f"Total vehículos: {result['summary']['total_vehicles']}")
        print(f"Con ubicación: {result['summary']['vehicles_with_location']}")
    else:
        print("❌ No se pudieron obtener datos") 