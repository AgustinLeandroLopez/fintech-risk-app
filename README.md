# 📊 Analizador de Riesgo Fintech

Aplicación web desarrollada en Python con FastAPI que permite analizar la coherencia económica y fiscal de clientes a partir de un archivo CSV.

El sistema evalúa inconsistencias entre ingresos declarados, montos operados y categoría fiscal, generando un score de riesgo, un dictamen preliminar y observaciones justificadas.

---

## 🚀 Objetivo del proyecto

Simular un motor de análisis de riesgo utilizado en fintechs o entidades financieras para:

- Detectar inconsistencias fiscales
- Evaluar capacidad económica
- Clasificar clientes según nivel de riesgo
- Generar un dictamen preliminar automatizado

---

## 🛠️ Tecnologías utilizadas

- Python 3
- FastAPI
- Jinja2 (templates HTML)
- Uvicorn
- HTML + CSS

---

## 📂 Estructura del proyecto
# 📊 Analizador de Riesgo Fintech

Aplicación web desarrollada en Python con FastAPI que permite analizar la coherencia económica y fiscal de clientes a partir de un archivo CSV.

El sistema evalúa inconsistencias entre ingresos declarados, montos operados y categoría fiscal, generando un score de riesgo, un dictamen preliminar y observaciones justificadas.

---

## 🚀 Objetivo del proyecto

Simular un motor de análisis de riesgo utilizado en fintechs o entidades financieras para:

- Detectar inconsistencias fiscales
- Evaluar capacidad económica
- Clasificar clientes según nivel de riesgo
- Generar un dictamen preliminar automatizado

---

## 🛠️ Tecnologías utilizadas

- Python 3
- FastAPI
- Jinja2 (templates HTML)
- Uvicorn
- HTML + CSS

---

## 📂 Estructura del proyecto
fintech-risk-app/
│
├── main.py
├── clientes.csv
├── requirements.txt
│
├── services/
│ ├── parser.py
│ ├── rules.py
│ ├── scoring.py
│
├── data/
│ └── reglas_monotributo.json
│
├── templates/
│ ├── index.html
│ └── resultado.html
│
├── static/
│ └── styles.css


---

## ⚙️ Cómo ejecutar el proyecto

1. Clonar el repositorio:
git clone [<URL_DEL_REPO>](https://github.com/AgustinLeandroLopez/fintech-risk-app.git)
cd fintech-risk-app


2. Crear entorno virtual:
python -m venv venv


3. Activar entorno:

Windows:
venv\Scripts\activate


4. Instalar dependencias:
pip install -r requirements.txt


5. Ejecutar la aplicación:
uvicorn main:app --reload


6. Abrir en el navegador:
http://127.0.0.1:8000


---

## 📥 Formato del archivo CSV

El sistema recibe un archivo CSV con las siguientes columnas:
cuit,nombre,condicion_fiscal,categoria_monotributo,actividad,ingreso_declarado_mensual,monto_operado_mensual,monto_operado_anual

### Ejemplo:
20123456789,Juan Perez,MONOTRIBUTO,C,Servicios IT,450000,780000,9360000



---

## 🧠 Lógica de análisis

El sistema aplica reglas determinísticas para calcular el riesgo:

### 📌 Reglas implementadas

- Si el monto mensual supera 1.5x el ingreso declarado → +25 puntos
- Si el monto anual es inconsistente con ingresos → +25 puntos
- Si falta categoría de monotributo → +30 puntos
- Si el monto anual supera el límite de la categoría → +40 puntos

### 📊 Clasificación de riesgo

| Score | Nivel | Dictamen |
|------|------|---------|
| 0 - 29 | BAJO | Cumple |
| 30 - 59 | MEDIO | Cumple con observaciones |
| 60+ | ALTO | No cumple |

---

## 📊 Resultado del análisis

Para cada cliente el sistema genera:

- Score de riesgo
- Nivel (BAJO / MEDIO / ALTO)
- Dictamen:
  - Cumple
  - Cumple con observaciones
  - No cumple
- Observaciones explicativas

Además, la interfaz muestra:

- Tabla con resultados
- Colores por nivel de riesgo (verde, amarillo, rojo)
- Formato visual amigable tipo dashboard

---

## 🧪 Casos de prueba

El sistema contempla distintos escenarios:

- Cliente consistente (bajo riesgo)
- Inconsistencia leve (riesgo medio)
- Exceso de categoría monotributo (riesgo alto)
- Responsable inscripto (sin restricciones de categoría)

---

## 📌 Alcance del proyecto

Este sistema representa un modelo simplificado de análisis de riesgo y no reemplaza evaluaciones reales de organismos regulatorios.

---

## 🚀 Posibles mejoras futuras

- Integración con IA para generación de dictámenes explicativos
- Exportación a PDF / Excel
- Dashboard con métricas agregadas
- Validación contra datos reales de AFIP
- API externa de scoring

---

## 👨‍💻 Autor

Agustín López  
Proyecto académico – Fintech

