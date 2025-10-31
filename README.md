# ⚽ Plataforma de Scouting — 5 Grandes Ligas Europeas

### Autor: **Daniel Carreño**  
**Máster en Python Avanzado — Sports Data Campus**  
🔗 [Ver aplicación en vivo](https://scouting-platform-5grandesligas.streamlit.app/)

---

## Descripción general

Esta aplicación es una plataforma interactiva desarrollada con **Streamlit**, diseñada para el **análisis y comparación de jugadores** de las cinco grandes ligas europeas (Premier League, LaLiga, Serie A, Bundesliga y Ligue 1).  
Su objetivo es facilitar el proceso de **scouting avanzado** mediante visualizaciones, métricas normalizadas y herramientas de seguimiento personalizadas.

---

## Características principales

- **Login y autenticación segura** mediante variables de entorno (`.env`) para un acceso controlado.  
- **Home Page** con tarjetas e hipervínculos que permiten acceder automáticamente a cada una de las pestañas de análisis de forma intuitiva.  
- **Dashboard central (Overview):** incluye gráficos de *Curva de madurez competitiva*, *Distribución táctica por liga*, *Explorador de métricas*, *Perfil medio por equipo* y *Evolución táctica temporal*.  
  Este módulo permite obtener una visión general del dataset y generar una **infografía resumen en formato PDF** al final de la página.  
- **Ranking y análisis por posición:** permite filtrar y generar el **TOP N jugadores** en función de una o varias métricas ponderadas, construyendo perfiles adaptables a distintos esquemas de juego.  
  Incluye opción para descargar los resultados en formato **CSV**.  
- **Comparador de jugadores (Radar Chart):** posibilita la comparación de **2 o 3 jugadores** según métricas seleccionadas o preajustes definidos por rol/posición.  
  Presenta un radar con fortalezas y debilidades, una tabla resumen de métricas y percentiles, además de permitir la descarga del radar en formato **PNG**.  
- **Módulo de jugadores similares:** busca jugadores con perfiles parecidos basándose en una o varias métricas simultáneas (con ponderaciones).  
  Ofrece un resumen final de fortalezas, debilidades y percentiles dentro de la liga, con descarga disponible en formato **CSV**.  
- **Shortlist interactiva:** permite crear listas personalizadas de jugadores de interés, clasificándolos por categorías (*observados*, *seguimiento*, *candidatos* o *no procede*).  
  Cada lista puede descargarse en formato **CSV**.  
- **Barra lateral dinámica:** disponible en todas las páginas, facilita la navegación y el filtrado por **liga, temporada, equipo, edad, minutos jugados y rol táctico** (delantero, volante, mediocentro, lateral, central o portero).  
- **Despliegue completo en Streamlit Cloud** para acceso público desde cualquier dispositivo.

---

## Estructura del proyecto

📦 proyecto-scouting
┣ 📂 .streamlit/
┣ 📂 data/
┃ ┣ 📂 processed/
┃ ┗ 📜 sample_datos.csv
┣ 📂 notebooks/
┃ ┣ 📂 data/
┃ ┃ ┗ 📜 sample_datos.csv
┃ ┗ 📜 ETL-5grandesligas.ipynb
┣ 📂 pages/
┃ ┣ 1_Overview.py
┃ ┣ 2_Ranking.py
┃ ┣ 3_Comparador.py
┃ ┣ 4_Similares.py
┃ ┗ 5_Shortlist.py
┣ 📂 utils/
┃ ┣ data_loader.py
┃ ┣ filters.py
┃ ┗ metrics.py
┣ 📂 venv/
┣ 📜 .env
┣ 📜 app.py
┣ 📜 iniciar_app.bat
┣ 📜 requirements.txt
┗ 📜 README.md

---

## Tecnologías utilizadas

- **Python 3.11** — Lenguaje principal del proyecto, utilizado para el procesamiento, análisis y visualización de datos.  
- **Streamlit** — Framework para la creación de aplicaciones web interactivas basadas en Python.  
- **Pandas** — Manipulación y análisis estructurado de datos en formato tabular (DataFrames).  
- **NumPy** — Soporte para operaciones matemáticas y manejo eficiente de arreglos numéricos.  
- **Plotly Express / Graph Objects** — Creación de gráficos interactivos y personalizados para el análisis visual de datos.  
- **Matplotlib** — Soporte adicional para visualizaciones estáticas complementarias.  
- **Seaborn** — Extensión de Matplotlib para visualizaciones estadísticas con alto nivel estético.  
- **OpenPyXL** — Lectura y escritura de archivos Excel (.xlsx).  
- **Streamlit-AgGrid** — Integración de tablas interactivas con filtrado, orden y selección dinámica.  
- **Kaleido** — Exportación de gráficos de Plotly a formatos de imagen (.png, .pdf) de alta resolución.  
- **Scikit-learn** — Librería de machine learning utilizada para la normalización y cálculo de métricas estadísticas.  
- **Statsmodels** — Análisis estadístico avanzado y modelado de series temporales.  
- **PyArrow** — Lectura y escritura optimizada de archivos en formato Parquet.  
- **FastParquet** — Alternativa eficiente para manejo de archivos Parquet en grandes volúmenes de datos.  
- **Kaggle** — Fuente de datos y recursos para el análisis y validación de datasets deportivos.  
- **Python-dotenv** — Manejo seguro de variables de entorno (.env) para autenticación y configuración.  
- **ReportLab** — Generación de reportes en PDF con diseño personalizado.  

---

## Variables de entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes credenciales:

USERNAME=admin
PASSWORD=admin


Estas variables son requeridas para acceder al panel principal de la aplicación y asegurar un control básico de acceso.

---

## Ejecución local

### 1. Clonar el repositorio

git clone https://github.com/DanielCarreno95/scouting-hub-5grandesligas.git
cd proyecto-scouting

### 2. Instala dependencias:

pip install -r requirements.txt

### 3. Ejecuta la aplicación:

streamlit run app.py

### 4. Accede desde tu navegador a http://localhost:8501

## Despliegue en Streamlit Cloud
La aplicación se encuentra desplegada en:

https://scouting-platform-5grandesligas.streamlit.app/

Este despliegue permite acceder a la plataforma desde cualquier dispositivo sin necesidad de instalación local.

---

## Capturas y ejemplo de visualización

- **Comparador de jugadores:** Radar Chart multi-jugador con normalización 0–100, ideal para observar diferencias de rendimiento por rol o posición.  
- **Shortlist interactiva:** Lista editable de seguimiento que permite clasificar jugadores por estado de observación y exportar los resultados en formato CSV.  
- **Dashboard (Overview):** Panel de control principal que centraliza la exploración de métricas, evolución táctica y distribución competitiva.  

---

## Conclusión

Este proyecto representa una integración avanzada entre **análisis de datos deportivos**, **visualización interactiva** , **Integración y automatización de datos con APIS** y **desarrollo web con Python**.  
La aplicación ofrece una herramienta funcional, escalable y visualmente clara para el **scouting profesional de jugadores** en las cinco grandes ligas europeas.  

A través de módulos especializados, la plataforma permite realizar un **análisis integral del rendimiento individual y colectivo**, apoyado en métricas estandarizadas, comparativas dinámicas y visualizaciones intuitivas.  

El trabajo destaca por su enfoque en la **automatización, eficiencia del análisis y capacidad de personalización**, aspectos esenciales para un entorno profesional de análisis de rendimiento deportivo.  
Además, la incorporación de un **sistema de autenticación, exportación PDF e integración de herramientas interactivas** refuerza su valor aplicado dentro de la analítica moderna en el deporte.  

En conjunto, este proyecto constituye una **plataforma sólida, moderna y funcional**, alineada con las exigencias reales de los **departamentos de scouting y análisis de rendimiento** en el fútbol profesional.
