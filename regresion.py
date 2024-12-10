import pandas as pd
import random
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# =======================
# 1. Cargar y Limpiar los Datos
# =======================
data = pd.read_csv(
    '/Users/marcosrodrigo/Desktop/Rutix Final/CargaLibre-Rutix/ARCHIVOS/tarifas_historicas.csv',
    delimiter=';',  # Delimitador
    encoding='ISO-8859-1'
)

# Limpiar caracteres especiales
data['tipo_vehiculo'] = data['tipo_vehiculo'].str.replace(r'\x96', '', regex=True)
print("Tipos de vehículo disponibles después de limpieza:", data['tipo_vehiculo'].unique())

# =======================
# 2. Simular Más Datos (Opcional)
# =======================
simulated_data = []
for _ in range(100):  # Generar datos simulados
    simulated_data.append({
        'distancia_km': random.randint(50, 600),
        'tipo_vehiculo': random.choice(['Pequeo', 'Grande', 'Mediano']),
        'peajes': random.randint(10000, 50000),
        'clima': random.choice(['Soleado', 'Lluvioso', 'Nublado']),
        'trafico': random.choice(['Fluido', 'Moderado', 'Pesado']),
        'tarifa': random.randint(200000, 800000)
    })
simulated_df = pd.DataFrame(simulated_data)
data = pd.concat([data, simulated_df], ignore_index=True)

# =======================
# 3. Preprocesamiento
# =======================
X = pd.get_dummies(data[['distancia_km', 'tipo_vehiculo', 'peajes', 'clima', 'trafico']], drop_first=True)
y = data['tarifa']

scaler = StandardScaler()
X[['distancia_km', 'peajes']] = scaler.fit_transform(X[['distancia_km', 'peajes']])
joblib.dump(scaler, 'scaler.pkl')  # Guardar el escalador

# =======================
# 4. Dividir los Datos
# =======================
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# =======================
# 5. Entrenar el Modelo
# =======================
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# =======================
# 6. Evaluar el Modelo
# =======================
predictions = rf_model.predict(X_test)
rmse = mean_squared_error(y_test, predictions, squared=False)
r2 = rf_model.score(X_test, y_test)
print("Random Forest - RMSE:", rmse)
print("Random Forest - R²:", r2)

# Visualizar Importancia de Características
feature_importances = rf_model.feature_importances_
for feature, importance in zip(X.columns, feature_importances):
    print(f"{feature}: {importance}")

# Guardar el modelo
joblib.dump(rf_model, 'modelo_tarifas_rf.pkl')

# =======================
# 7. Probar el Modelo con Nuevos Datos
# =======================
nuevos_datos = [
    {'distancia_km': 500, 'tipo_vehiculo': 'Pequeo', 'peajes': 30000, 'clima': 'Soleado', 'trafico': 'Fluido'},
    {'distancia_km': 500, 'tipo_vehiculo': 'Grande', 'peajes': 30000, 'clima': 'Soleado', 'trafico': 'Fluido'},
    {'distancia_km': 500, 'tipo_vehiculo': 'Mediano', 'peajes': 30000, 'clima': 'Soleado', 'trafico': 'Fluido'}
]
nuevos_datos_df = pd.DataFrame(nuevos_datos)
nuevos_datos_df = pd.get_dummies(nuevos_datos_df, columns=['tipo_vehiculo', 'clima', 'trafico'], drop_first=True)
for col in X.columns:
    if col not in nuevos_datos_df.columns:
        nuevos_datos_df[col] = 0
scaler = joblib.load('scaler.pkl')
nuevos_datos_df[['distancia_km', 'peajes']] = scaler.transform(nuevos_datos_df[['distancia_km', 'peajes']])
modelo_cargado = joblib.load('modelo_tarifas_rf.pkl')
tarifas_predichas = modelo_cargado.predict(nuevos_datos_df)
for tipo, tarifa in zip(nuevos_datos, tarifas_predichas):
    print(f"Tarifa para tipo de vehículo {tipo['tipo_vehiculo']}: {tarifa}")

# =======================
# 8. Visualización
# =======================
sns.scatterplot(data=data, x='distancia_km', y='tarifa', hue='tipo_vehiculo')
plt.title("Relación entre distancia y tarifa por tipo de vehículo")
plt.xlabel("Distancia (km)")
plt.ylabel("Tarifa (COP)")
plt.show()
