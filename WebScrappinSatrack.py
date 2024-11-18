import ssl
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from selenium.webdriver.common.keys import Keys

def scrape_satrack():
    # Add SSL certificate verification bypass
    ssl._create_default_https_context = ssl._create_unverified_context

    # Configurar undetected-chromedriver con opciones básicas
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--ignore-ssl-errors")
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36')

    # Inicializar el driver
    driver = uc.Chrome(version_main=130, options=options)

    def print_element_info(element, name="Elemento"):
        """Imprime información detallada sobre un elemento web."""
        try:
            print(f"\n{name} información:")
            print(f"Texto: {element.text}")
            print(f"HTML: {element.get_attribute('outerHTML')}")
            print(f"Clases: {element.get_attribute('class')}")
            print(f"ID: {element.get_attribute('id')}")
            print(f"Visible: {element.is_displayed()}")
        except Exception as e:
            print(f"Error obteniendo información del {name}: {str(e)}")

    try:
        # Abrir la página de inicio de sesión de Satrack
        driver.get("https://login.satrack.com/login")
        time.sleep(5)

        # Intentar ingresar el usuario usando múltiples métodos
        driver.execute_script("""
            // Intentar encontrar el campo de usuario por diferentes atributos
            let usernameField = document.querySelector('input[placeholder="Usuario"], input[aria-label="Usuario"], input[name="Usuario"]') ||
                               document.querySelector('input[type="text"], input[type="email"]') ||
                               document.getElementsByTagName('input')[0];  // Primera entrada del formulario
            
            if (usernameField) {
                // Limpiar y enfocar el campo
                usernameField.focus();
                usernameField.value = '';
                
                // Establecer el valor y disparar eventos
                usernameField.value = 'martinespana@cargalibre.com.co';
                usernameField.dispatchEvent(new Event('input', { bubbles: true }));
                usernameField.dispatchEvent(new Event('change', { bubbles: true }));
                usernameField.dispatchEvent(new Event('blur', { bubbles: true }));
                
                // Simular escritura de teclado
                usernameField.dispatchEvent(new KeyboardEvent('keydown', { key: 'a' }));
                usernameField.dispatchEvent(new KeyboardEvent('keypress', { key: 'a' }));
                usernameField.dispatchEvent(new KeyboardEvent('keyup', { key: 'a' }));
            }
        """)
        print("Intento de ingreso de usuario mediante JavaScript")

        # Verificar si el valor se estableció correctamente
        username_value = driver.execute_script("""
            let field = document.querySelector('input[type="text"], input[type="email"]');
            return field ? field.value : '';
        """)
        print(f"Valor actual del campo usuario: {username_value}")

        time.sleep(2)

        # Usar JavaScript para la contraseña
        driver.execute_script("""
            let password = document.querySelector('input#password, input[name="password"], input[type="password"]');
            if (password) {
                password.value = '#3A3652e7';
                password.dispatchEvent(new Event('input', { bubbles: true }));
                password.dispatchEvent(new Event('change', { bubbles: true }));
            }
        """)
        print("Contraseña ingresada")

        time.sleep(2)  # Pequeña pausa

        # Hacer clic en el botón de inicio de sesión
        driver.execute_script("""
            let loginButton = document.querySelector('button[type="submit"], button.login-button, input[type="submit"]');
            if (loginButton) {
                loginButton.click();
            }
        """)
        print("Botón de inicio de sesión presionado")

        # Esperar a que se complete el login y redirija
        print("Esperando redirección después del login...")
        time.sleep(30)  # Aumentamos el tiempo de espera inicial

        print("Verificando URL actual...")
        current_url = driver.current_url
        print(f"URL actual: {current_url}")

        if "portal.satrack.com" in current_url:
            print("Redirección exitosa al portal")
            
            print("Esperando a que cargue la lista de vehículos...")
            time.sleep(45)

            print("Buscando vehículos...")

            # Lista de selectores a probar
            selectors = [
                "//div[contains(@class, 'vehicle-list')]//div[contains(@class, 'item')]",
                "//div[contains(@class, 'vehicle')]//div[contains(@class, 'plate')]",
                "//div[contains(@class, 'list')]//div[contains(@class, 'vehicle')]",
                "//div[contains(@class, 'vehicle-container')]//div[contains(@class, 'item')]",
                "//div[contains(@class, 'list')]//div[contains(@role, 'button')]",
                "//div[contains(@class, 'list')]//div[contains(@class, 'clickable')]"
            ]

            vehicle_elements = None

            # Probar cada selector
            for selector in selectors:
                try:
                    print(f"Intentando selector: {selector}")
                    # Esperar a que al menos un elemento sea visible
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    # Si llegamos aquí, encontramos elementos
                    vehicle_elements = driver.find_elements(By.XPATH, selector)
                    if vehicle_elements:
                        print(f"Encontrados {len(vehicle_elements)} elementos")
                        break
                except:
                    continue

            if not vehicle_elements:
                print("No se encontraron vehículos con los selectores principales")
                print("Intentando obtener estructura de la página...")
                
                # Obtener y mostrar la estructura básica de la página
                page_structure = driver.execute_script("""
                    return Array.from(document.querySelectorAll('div')).map(el => ({
                        class: el.className,
                        id: el.id,
                        text: el.textContent.slice(0, 50)
                    })).slice(0, 10);
                """)
                print("Estructura de la página:")
                for element in page_structure:
                    print(element)
                
                driver.save_screenshot("no_vehicles.png")
                raise Exception("No se pudieron encontrar los vehículos")

            print(f"\nSe encontraron {len(vehicle_elements)} vehículos")
            vehicles_info = []

            for index, vehicle in enumerate(vehicle_elements, 1):
                try:
                    vehicle_text = vehicle.text.strip()
                    if not vehicle_text or len(vehicle_text) < 3:
                        continue
                        
                    print(f"\nProcesando vehículo {index}: {vehicle_text}")
                    
                    # Hacer scroll hasta el elemento
                    driver.execute_script("arguments[0].scrollIntoView(true);", vehicle)
                    time.sleep(2)

                    # Intentar hacer clic
                    try:
                        vehicle.click()
                    except:
                        driver.execute_script("arguments[0].click();", vehicle)
                    
                    # Esperar a que el mapa se cargue
                    time.sleep(5)

                    # Intentar obtener información usando JavaScript
                    try:
                        # Obtener información del vehículo usando JavaScript
                        vehicle_info = driver.execute_script("""
                            // Función para buscar texto en elementos
                            function findTextInElements(selector) {
                                const elements = document.querySelectorAll(selector);
                                for (const el of elements) {
                                    if (el.offsetParent !== null) {  // Elemento visible
                                        const text = el.textContent.trim();
                                        if (text && text.length > 5) return text;
                                    }
                                }
                                return null;
                            }

                            // Buscar información en diferentes elementos
                            const locationInfo = {
                                // Buscar en elementos con clase específica
                                address: findTextInElements('.location-info, .address-info, .vehicle-location'),
                                
                                // Buscar en elementos del popup de Google Maps
                                mapInfo: findTextInElements('.gm-style-iw, .gm-style-iw-d'),
                                
                                // Buscar en cualquier elemento que contenga coordenadas
                                coords: findTextInElements('[class*="coord"], [class*="location"]'),
                                
                                // Buscar en elementos de dirección
                                street: findTextInElements('[class*="street"], [class*="address"]')
                            };

                            // Intentar obtener coordenadas del mapa
                            try {
                                const map = document.querySelector('#map');
                                if (map && map.__gm) {
                                    const center = map.__gm.get('center');
                                    locationInfo.mapCoords = `${center.lat()}, ${center.lng()}`;
                                }
                            } catch(e) {
                                console.error('Error getting map coordinates:', e);
                            }

                            return locationInfo;
                        """)

                        print("Información obtenida:", vehicle_info)

                        # Procesar la información obtenida
                        location = "No disponible"
                        coords = "No disponible"

                        if vehicle_info:
                            # Intentar obtener la ubicación de diferentes fuentes
                            location_sources = [
                                vehicle_info.get('address'),
                                vehicle_info.get('street'),
                                vehicle_info.get('mapInfo')
                            ]
                            
                            for source in location_sources:
                                if source and len(source.strip()) > 5:
                                    location = source.strip()
                                    break

                            # Intentar obtener coordenadas
                            coords = vehicle_info.get('mapCoords') or vehicle_info.get('coords') or "No disponible"

                        vehicles_info.append({
                            'plate': vehicle_text,
                            'location': location,
                            'coordinates': coords
                        })

                        print(f"Información encontrada para {vehicle_text}:")
                        print(f"Ubicación: {location}")
                        print(f"Coordenadas: {coords}")

                    except Exception as e:
                        print(f"Error obteniendo información: {str(e)}")
                        vehicles_info.append({
                            'plate': vehicle_text,
                            'location': "Error al obtener ubicación",
                            'coordinates': "No disponible"
                        })

                    # Pequeña pausa antes del siguiente vehículo
                    time.sleep(2)

                except Exception as e:
                    print(f"Error procesando vehículo: {str(e)}")
                    continue

            # Función para limpiar el texto de la ubicación
            def clean_location_text(text):
                if not text or text == "No disponible":
                    return "No disponible"
                
                # Eliminar textos comunes no deseados
                unwanted_texts = [
                    "more_vert",
                    "directions_car",
                    "filter_list",
                    "Ubicación no disponible",
                    "hace más de",
                    "En ruta con otra empresa",
                    "search refresh",
                    "Vehículos",
                    "Limpiar filtros",
                    "Estado",
                    "Viajes",
                    "Grupos",
                    "Búsqueda de vehículo avanzada"
                ]
                
                cleaned_text = text
                for unwanted in unwanted_texts:
                    cleaned_text = cleaned_text.replace(unwanted, "").strip()
                
                # Eliminar múltiples espacios
                cleaned_text = " ".join(cleaned_text.split())
                
                return cleaned_text if cleaned_text else "No disponible"

            # Función para limpiar coordenadas
            def clean_coordinates(coords):
                if not coords or coords == "No disponible":
                    return "No disponible"
                
                # Si encontramos un patrón de coordenadas (números con punto decimal), lo extraemos
                import re
                coord_pattern = r'(-?\d+\.\d+),\s*(-?\d+\.\d+)'
                match = re.search(coord_pattern, coords)
                if match:
                    return f"{match.group(1)}, {match.group(2)}"
                
                return "No disponible"

            # Reemplazar toda la sección de guardado en archivo por una estructura de datos
            report_data = None
            if vehicles_info:
                try:
                    # Crear diccionario con la información
                    report_data = {
                        'timestamp': time.strftime('%d/%m/%Y %H:%M:%S'),
                        'summary': {
                            'total_vehicles': len(vehicles_info),
                            'vehicles_with_location': sum(1 for v in vehicles_info if clean_location_text(v['location']) != "No disponible"),
                        },
                        'vehicles': []
                    }

                    # Agregar información detallada de cada vehículo
                    for vehicle in vehicles_info:
                        # Limpiar datos
                        location = clean_location_text(vehicle['location'])
                        coords = clean_coordinates(vehicle['coordinates'])
                        
                        vehicle_data = {
                            'plate': vehicle['plate'],
                            'location': location,
                            'coordinates': coords,
                            'status': 'located' if location != 'No disponible' else 'not_located'
                        }
                        report_data['vehicles'].append(vehicle_data)

                    # Mostrar resumen en consola
                    print("\nResumen de vehículos procesados:")
                    print(f"Total: {report_data['summary']['total_vehicles']}")
                    print(f"Con ubicación: {report_data['summary']['vehicles_with_location']}")
                    print(f"Sin ubicación: {report_data['summary']['total_vehicles'] - report_data['summary']['vehicles_with_location']}")
                    
                except Exception as e:
                    print(f"Error procesando datos: {str(e)}")
            else:
                print("No se encontró información de ningún vehículo")
            
            return report_data  # Este return está alineado con el if principal

        else:
            print("No se completó la redirección al portal correctamente")
            driver.save_screenshot("redirect_error.png")
            return None

    except Exception as e:
        print(f"Error general: {str(e)}")
        driver.save_screenshot("error_general.png")
        import traceback
        print(traceback.format_exc())
        return None

    finally:
        time.sleep(5)
        driver.quit()

# Ejecutar el script
if __name__ == "__main__":
    result = scrape_satrack()
    if result:
        print("\nDatos obtenidos exitosamente:")
        print(result)
