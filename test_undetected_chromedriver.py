import undetected_chromedriver as uc

options = uc.ChromeOptions()
options.add_argument("--headless")  # Opcional: ejecución sin interfaz gráfica
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# Forzar el uso del chromedriver manual
driver = uc.Chrome(driver_executable_path="/usr/local/bin/chromedriver", options=options)
driver.get("https://www.google.com")
print("Título de la página:", driver.title)
driver.quit()
