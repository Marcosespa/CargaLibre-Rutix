import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import joblib
import random

# =======================
# 1. Cargar y Limpiar los Datos
# =======================
# Cargar el archivo CSV
data = pd.read_csv(
    '/Users/marcosrodrigo/Desktop/Rutix Final/CargaLibre-Rutix/ARCHIVOS/tarifas_historicas.csv',
    delimiter=';',  # Especificar delimitador
    encoding='ISO-8859-1'
)

# Limpieza de caracteres especiales en la columna tipo_vehiculo
data['tipo_vehiculo'] = data['tipo_vehiculo'].str.replace(r'\x96', '', regex=True)
print("Tipos de vehículo después de limpieza:", data['tipo_vehiculo'].unique())

# =======================
# 2. Generar Datos Simulados (Opcional)
# =======================
simulated_data = []
for _ in range(100):  # Generar 100 registros simulados
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
# 3. Preparar las Variables Predictoras y Objetivo
# =======================
# Variables predictoras y objetivo
X = pd.get_dummies(data[['distancia_km', 'tipo_vehiculo', 'peajes', 'clima', 'trafico']], drop_first=True)
y = data['tarifa']

# Normalizar variables numéricas
scaler = StandardScaler()
X[['distancia_km', 'peajes']] = scaler.fit_transform(X[['distancia_km', 'peajes']])

# Guardar el escalador para uso futuro
joblib.dump(scaler, 'scaler.pkl')

# Dividir en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# =======================
# 4. Entrenar el Modelo (Regresión Lineal)
# =======================
linear_model = LinearRegression()
linear_model.fit(X_train, y_train)

# Predicciones y evaluación con Regresión Lineal
linear_predictions = linear_model.predict(X_test)
rmse_linear = mean_squared_error(y_test, linear_predictions, squared=False)
mae_linear = mean_absolute_error(y_test, linear_predictions)

print("=== Regresión Lineal ===")
print("Error Cuadrático Medio (RMSE):", rmse_linear)
print("Error Absoluto Medio (MAE):", mae_linear)
print("R² del modelo:", linear_model.score(X_test, y_test))

# =======================
# 5. Entrenar el Modelo (Random Forest)
# =======================
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Predicciones y evaluación con Random Forest
rf_predictions = rf_model.predict(X_test)
rmse_rf = mean_squared_error(y_test, rf_predictions, squared=False)
mae_rf = mean_absolute_error(y_test, rf_predictions)

print("\n=== Random Forest ===")
print("Error Cuadrático Medio (RMSE):", rmse_rf)
print("Error Absoluto Medio (MAE):", mae_rf)
print("R² del modelo:", rf_model.score(X_test, y_test))

# =======================
# 6. Validación Cruzada
# =======================
cv_scores = cross_val_score(rf_model, X, y, cv=5, scoring='neg_mean_squared_error')
rmse_cv = [(-score) ** 0.5 for score in cv_scores]
print("\n=== Validación Cruzada (Random Forest) ===")
print("RMSE por partición:", rmse_cv)
print("RMSE promedio:", sum(rmse_cv) / len(rmse_cv))

# =======================
# 7. Guardar los Modelos
# =======================
joblib.dump(linear_model, 'linear_model_tarifas.pkl')
joblib.dump(rf_model, 'rf_model_tarifas.pkl')

# =======================
# 8. Probar el Modelo con Datos Nuevos
# =======================
nuevos_datos = pd.DataFrame({
    'distancia_km': [500],
    'tipo_vehiculo': ['Grande'],
    'peajes': [30000],
    'clima': ['Soleado'],
    'trafico': ['Moderado']
})

# Codificar y normalizar los datos nuevos
nuevos_datos = pd.get_dummies(nuevos_datos, columns=['tipo_vehiculo', 'clima', 'trafico'], drop_first=True)
for col in X.columns:
    if col not in nuevos_datos.columns:
        nuevos_datos[col] = 0
nuevos_datos[['distancia_km', 'peajes']] = scaler.transform(nuevos_datos[['distancia_km', 'peajes']])

# Predecir con ambos modelos
linear_pred_new = linear_model.predict(nuevos_datos)
rf_pred_new = rf_model.predict(nuevos_datos)

print("\n=== Predicciones para Nuevos Datos ===")
print("Predicción (Regresión Lineal):", linear_pred_new[0])
print("Predicción (Random Forest):", rf_pred_new[0])
