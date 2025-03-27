from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use('Agg')  # Usar backend no interactivo
import matplotlib.pyplot as plt
import re
import numpy as np
import os
import io
import base64
from datetime import datetime
import json
import traceback
 
from flask import Blueprint

normativa_bp = Blueprint('normativa', __name__, template_folder='../templates')
app = normativa_bp

#normativa_bp = Blueprint('normativa', __name__, template_folder='../templates')

# Ruta al Excel relativa a la raíz del proyecto
excel_path = os.path.join(os.path.dirname(__file__), '..', 'CdB_Normativa_Segmentada.xlsx')
df = pd.read_excel(excel_path)

@normativa_bp.route('/')
def mostrar_normativa():
    numeros_normas = sorted(df['Número'].dropna().astype(int).unique().tolist())

    return render_template(
        'normativa.html',
        numeros_normas=numeros_normas,
        etiquetas=etiquetas_unicas,
        temas=temas_unicos,
        subtemas=subtemas_unicos
    )



# Clase personalizada para manejar tipos de datos NumPy en JSON
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Timestamp):
            return obj.strftime('%d/%m/%Y')
        elif pd.isna(obj):
            return None
        return super(CustomJSONEncoder, self).default(obj)
 
# Configurar el codificador JSON personalizado
app.json_encoder = CustomJSONEncoder
 
# Variables globales
df_main = None  # DataFrame principal con normas
df_segmentacion = None  # DataFrame con segmentación mejorada
grafo_actual = None  # Grafo actual en memoria
etiquetas_unicas = []  # Lista de todas las etiquetas únicas
temas_unicos = []  # Lista de temas únicos
subtemas_unicos = []  # Lista de subtemas únicos
 
# Funciones auxiliares
def formatear_fecha(fecha):
    """
    Convierte cualquier tipo de fecha a formato string dd/mm/yyyy
    """
    if pd.isna(fecha):
        return "Fecha desconocida"
   
    try:
        if isinstance(fecha, np.datetime64):
            return pd.Timestamp(fecha).strftime('%d/%m/%Y')
        elif hasattr(fecha, 'strftime'):
            return fecha.strftime('%d/%m/%Y')
        else:
            # Intentar convertir a datetime si es un string
            return pd.to_datetime(fecha, errors='coerce', dayfirst=True).strftime('%d/%m/%Y')
    except:
        # Si falla la conversión, devolver el string original
        return str(fecha)
 
def extraer_numeros(valor):
    """Extrae números de una cadena que puede contener múltiples valores"""
    if pd.isna(valor):
        return []
    # Limpieza de caracteres especiales y separación por saltos de línea
    valor = re.sub(r'x000D\n', ' ', str(valor))
    # Extracción de números usando expresiones regulares
    numeros = re.findall(r'\b\d+\b', valor)
    return numeros
 
def extraer_fechas(valor):
    """Extrae fechas en formato dd/mm/yyyy de una cadena"""
    if pd.isna(valor):
        return []
    # Limpieza de caracteres especiales
    valor = re.sub(r'x000D\n', ' ', str(valor))
    # Extracción de fechas en formato dd/mm/yyyy
    fechas = re.findall(r'\d{2}/\d{2}/\d{4}', valor)
    return fechas
 
def extraer_info_historial(valor):
    """Extrae información detallada del historial de modificaciones"""
    if pd.isna(valor):
        return []
   
    modificaciones = []
    # Dividir por el separador '|'
    items = valor.split('|')
   
    for item in items:
        # Extraer tipo, número y fecha usando regex
        match = re.search(r'(NCG|OFC|CIR)\s+(\d+)\s+\((\d{2}/\d{2}/\d{4})', item)
        if match:
            tipo, num, fecha = match.groups()
            modificaciones.append((tipo, num, fecha))
   
    return modificaciones
 
def extraer_etiquetas(valor):
    """Extrae etiquetas separadas por comas"""
    if pd.isna(valor):
        return []
    # Dividir por coma y espacio
    etiquetas = [etiqueta.strip() for etiqueta in str(valor).split(',')]
    return [e for e in etiquetas if e]  # Filtrar etiquetas vacías
 
# Cargar los datos al iniciar la aplicación
def cargar_datos():
    global df_main, df_segmentacion, etiquetas_unicas, temas_unicos, subtemas_unicos
    try:
        # Obtener el directorio actual
        dir_actual = os.path.dirname(os.path.abspath(__file__))
       
        dir_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_excel = os.path.abspath(os.path.join(dir_actual, '..', 'CdB_Normativa_Segmentada.xlsx'))

       
        # Verificar si el archivo existe
        if not os.path.isfile(ruta_excel):
            print(f"ERROR: El archivo no existe en la ruta: {ruta_excel}")
            print("Archivos en el directorio:")
            for archivo in os.listdir(dir_actual):
                print(f"  - {archivo}")
            return False, f"El archivo no existe en la ruta: {ruta_excel}"
       
        # Intentar cargar la hoja principal
        print(f"Intentando cargar la hoja principal del archivo: {ruta_excel}")
        df_main = pd.read_excel(ruta_excel, parse_dates=['Fecha'])
       
        # Intentar cargar la hoja de segmentación
        print(f"Intentando cargar la hoja de segmentación: {ruta_excel}")
        try:
            df_segmentacion = pd.read_excel(ruta_excel, sheet_name='Segmentacion Mejorada')
            print(f"Hoja de segmentación cargada. {len(df_segmentacion)} registros encontrados.")
            print(f"Columnas en segmentación: {df_segmentacion.columns.tolist()}")
           
            # Extraer etiquetas únicas, temas y subtemas
            if 'Etiquetas' in df_segmentacion.columns:
                todas_etiquetas = []
                for etiquetas_str in df_segmentacion['Etiquetas'].dropna():
                    todas_etiquetas.extend(extraer_etiquetas(etiquetas_str))
                etiquetas_unicas = sorted(list(set(todas_etiquetas)))
                print(f"Se encontraron {len(etiquetas_unicas)} etiquetas únicas")
           
            if 'Tema' in df_segmentacion.columns:
                temas_unicos = sorted(list(df_segmentacion['Tema'].dropna().unique()))
                print(f"Se encontraron {len(temas_unicos)} temas únicos")
           
            if 'Subtema' in df_segmentacion.columns:
                subtemas_unicos = sorted(list(df_segmentacion['Subtema'].dropna().unique()))
                print(f"Se encontraron {len(subtemas_unicos)} subtemas únicos")
           
        except Exception as e:
            print(f"Error al cargar la hoja de segmentación: {str(e)}")
            print("Continuando con la hoja principal solamente...")
            df_segmentacion = None
       
        # Convertir columnas numéricas a tipos Python estándar
        for col in df_main.select_dtypes(include=[np.number]).columns:
            df_main[col] = df_main[col].astype(float).fillna(0)
       
        # Verificar si se cargó correctamente
        if df_main is None or df_main.empty:
            print("ERROR: El DataFrame está vacío después de la carga")
            return False, "El DataFrame está vacío después de la carga"
       
        print(f"Datos cargados correctamente. {len(df_main)} registros encontrados.")
        print(f"Columnas en el DataFrame principal: {df_main.columns.tolist()}")
       
        return True, f"Datos cargados correctamente. {len(df_main)} registros encontrados."
    except Exception as e:
        error_msg = f"Error al cargar los datos: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return False, error_msg
 
# Función para obtener las etiquetas de una norma
def obtener_etiquetas_norma(tipo_norma, numero):
    global df_segmentacion
   
    if df_segmentacion is None:
        return []
   
    # Convertir a tipos básicos para comparación
    tipo_norma = str(tipo_norma)
    numero = int(numero) if isinstance(numero, (int, float)) or (isinstance(numero, str) and numero.isdigit()) else numero
   
    # Buscar en el DataFrame de segmentación
    filtro = (df_segmentacion['Tipo de Norma'] == tipo_norma) & (df_segmentacion['Número'] == numero)
    normas_filtradas = df_segmentacion[filtro]
   
    if len(normas_filtradas) == 0:
        return []
   
    # Obtener las etiquetas de la primera coincidencia
    etiquetas_str = normas_filtradas.iloc[0].get('Etiquetas', '')
   
    if pd.isna(etiquetas_str):
        return []
   
    return extraer_etiquetas(etiquetas_str)
 
# Función para obtener tema y subtema de una norma
def obtener_tema_subtema_norma(tipo_norma, numero):
    global df_segmentacion
   
    if df_segmentacion is None:
        return {'tema': '', 'subtema': ''}
   
    # Convertir a tipos básicos para comparación
    tipo_norma = str(tipo_norma)
    numero = int(numero) if isinstance(numero, (int, float)) or (isinstance(numero, str) and numero.isdigit()) else numero
   
    # Buscar en el DataFrame de segmentación
    filtro = (df_segmentacion['Tipo de Norma'] == tipo_norma) & (df_segmentacion['Número'] == numero)
    normas_filtradas = df_segmentacion[filtro]
   
    if len(normas_filtradas) == 0:
        return {'tema': '', 'subtema': ''}
   
    # Obtener tema y subtema
    tema = normas_filtradas.iloc[0].get('Tema', '')
    subtema = normas_filtradas.iloc[0].get('Subtema', '')
   
    if pd.isna(tema):
        tema = ''
   
    if pd.isna(subtema):
        subtema = ''
   
    return {'tema': str(tema), 'subtema': str(subtema)}
 
# Función para buscar normas por etiqueta, tema o subtema
def buscar_normas(criterio, valor):
    global df_main, df_segmentacion
   
    if df_segmentacion is None:
        return []
   
    resultados = []
   
    if criterio == 'etiqueta':
        # Buscar por etiqueta
        for _, row in df_segmentacion.iterrows():
            if pd.isna(row.get('Etiquetas', '')):
                continue
               
            etiquetas = extraer_etiquetas(row['Etiquetas'])
            if valor in etiquetas:
                # Buscar información adicional en df_main
                tipo_norma = row['Tipo de Norma']
                numero = row['Número']
               
                info_adicional = {}
                filtro_main = (df_main['Tipo de Norma'] == tipo_norma) & (df_main['Número'] == numero)
                normas_main = df_main[filtro_main]
               
                if len(normas_main) > 0:
                    main_row = normas_main.iloc[0]
                    info_adicional = {
                        'fecha': formatear_fecha(main_row.get('Fecha', '')),
                        'titulo': str(main_row.get('Título / Referencia', '')),
                        'resumen': str(main_row.get('Resumen', ''))[:200] + '...' if len(str(main_row.get('Resumen', ''))) > 200 else str(main_row.get('Resumen', '')),
                    }
               
                resultados.append({
                    'tipo': str(tipo_norma),
                    'numero': int(numero),
                    'tema': str(row.get('Tema', '')),
                    'subtema': str(row.get('Subtema', '')),
                    'etiquetas': etiquetas,
                    **info_adicional
                })
   
    elif criterio == 'tema':
        # Buscar por tema
        filtro = df_segmentacion['Tema'] == valor
        for _, row in df_segmentacion[filtro].iterrows():
            tipo_norma = row['Tipo de Norma']
            numero = row['Número']
           
            info_adicional = {}
            filtro_main = (df_main['Tipo de Norma'] == tipo_norma) & (df_main['Número'] == numero)
            normas_main = df_main[filtro_main]
           
            if len(normas_main) > 0:
                main_row = normas_main.iloc[0]
                info_adicional = {
                    'fecha': formatear_fecha(main_row.get('Fecha', '')),
                    'titulo': str(main_row.get('Título / Referencia', '')),
                    'resumen': str(main_row.get('Resumen', ''))[:200] + '...' if len(str(main_row.get('Resumen', ''))) > 200 else str(main_row.get('Resumen', '')),
                }
           
            etiquetas = []
            if not pd.isna(row.get('Etiquetas', '')):
                etiquetas = extraer_etiquetas(row['Etiquetas'])
           
            resultados.append({
                'tipo': str(tipo_norma),
                'numero': int(numero),
                'tema': str(row.get('Tema', '')),
                'subtema': str(row.get('Subtema', '')),
                'etiquetas': etiquetas,
                **info_adicional
            })
   
    elif criterio == 'subtema':
        # Buscar por subtema
        filtro = df_segmentacion['Subtema'] == valor
        for _, row in df_segmentacion[filtro].iterrows():
            tipo_norma = row['Tipo de Norma']
            numero = row['Número']
           
            info_adicional = {}
            filtro_main = (df_main['Tipo de Norma'] == tipo_norma) & (df_main['Número'] == numero)
            normas_main = df_main[filtro_main]
           
            if len(normas_main) > 0:
                main_row = normas_main.iloc[0]
                info_adicional = {
                    'fecha': formatear_fecha(main_row.get('Fecha', '')),
                    'titulo': str(main_row.get('Título / Referencia', '')),
                    'resumen': str(main_row.get('Resumen', ''))[:200] + '...' if len(str(main_row.get('Resumen', ''))) > 200 else str(main_row.get('Resumen', '')),
                }
           
            etiquetas = []
            if not pd.isna(row.get('Etiquetas', '')):
                etiquetas = extraer_etiquetas(row['Etiquetas'])
           
            resultados.append({
                'tipo': str(tipo_norma),
                'numero': int(numero),
                'tema': str(row.get('Tema', '')),
                'subtema': str(row.get('Subtema', '')),
                'etiquetas': etiquetas,
                **info_adicional
            })
   
    return resultados
 
# Función principal para crear el grafo
def crear_grafo_norma(df, numero_norma):
    """
    Crea un grafo de relaciones para una norma específica.
    """
    try:
        # Verificar que tenemos datos
        if df is None or df.empty:
            return None, "No hay datos cargados en el DataFrame"
           
        # Convertir a string para asegurar compatibilidad
        numero_norma = str(numero_norma)
       
        # Crear un grafo dirigido
        G = nx.DiGraph()
       
        # Verificar que el DataFrame contiene las columnas necesarias
        columnas_requeridas = [
            'Número', 'Tipo de Norma', 'Fecha',
            'Modifica a (numero)', 'Modifica a (fecha)',
            'Modificada por (numero)', 'Modificada por (fecha)',
            'Deroga a (numero)', 'Deroga a (fecha)',
            'Derogada por (numero)', 'Derogada por (fecha)',
            'Historial_Modificaciones'
        ]
       
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
        if columnas_faltantes:
            return None, f"Error: Faltan las siguientes columnas en el DataFrame: {', '.join(columnas_faltantes)}"
       
        # Buscar la norma en el dataframe
        try:
            norma_principal = df[df['Número'] == int(numero_norma)]
        except ValueError:
            return None, f"Error: El número de norma '{numero_norma}' no es válido."
       
        if len(norma_principal) == 0:
            return None, f"No se encontró ninguna norma con el número {numero_norma}"
       
        tipo_norma_principal = norma_principal['Tipo de Norma'].values[0]
        fecha_norma_principal = norma_principal['Fecha'].values[0]
       
        # Obtener título y resumen para la norma principal
        titulo_principal = norma_principal['Título / Referencia'].values[0] if 'Título / Referencia' in norma_principal.columns else "Sin título"
        resumen_principal = norma_principal['Resumen'].values[0] if 'Resumen' in norma_principal.columns else "Sin resumen"
       
        # Obtener etiquetas, tema y subtema
        etiquetas_principal = obtener_etiquetas_norma(tipo_norma_principal, numero_norma)
        tema_subtema = obtener_tema_subtema_norma(tipo_norma_principal, numero_norma)
       
        # Añadir el nodo principal
        fecha_str = formatear_fecha(fecha_norma_principal)
        etiqueta_principal = f"{tipo_norma_principal} {numero_norma}\n({fecha_str})"
        G.add_node(etiqueta_principal,
                  tipo='principal',
                  fecha=fecha_norma_principal,
                  titulo=titulo_principal,
                  resumen=resumen_principal,
                  numero=numero_norma,
                  etiquetas=etiquetas_principal,
                  tema=tema_subtema['tema'],
                  subtema=tema_subtema['subtema'])
       
        # 1. Procesamiento de "Modifica a"
        numeros_modifica = extraer_numeros(norma_principal['Modifica a (numero)'].values[0])
        fechas_modifica = extraer_fechas(norma_principal['Modifica a (fecha)'].values[0])
       
        for i, num in enumerate(numeros_modifica):
            fecha_raw = fechas_modifica[i] if i < len(fechas_modifica) else None
            fecha = formatear_fecha(fecha_raw)
           
            # Determinar el tipo de norma modificada
            norma_modificada = df[df['Número'] == int(num)]
            tipo_norma = "NCG"  # Por defecto
            titulo = "Sin título"
            resumen = "Sin resumen"
           
            if len(norma_modificada) > 0:
                tipo_norma = norma_modificada['Tipo de Norma'].values[0]
                if 'Título / Referencia' in norma_modificada.columns:
                    titulo = norma_modificada['Título / Referencia'].values[0]
                if 'Resumen' in norma_modificada.columns:
                    resumen = norma_modificada['Resumen'].values[0]
           
            # Obtener etiquetas, tema y subtema
            etiquetas = obtener_etiquetas_norma(tipo_norma, num)
            tema_subtema = obtener_tema_subtema_norma(tipo_norma, num)
           
            etiqueta = f"{tipo_norma} {num}\n({fecha})"
            G.add_node(etiqueta,
                      tipo='modificada',
                      fecha=fecha_raw,
                      titulo=titulo,
                      resumen=resumen,
                      numero=num,
                      etiquetas=etiquetas,
                      tema=tema_subtema['tema'],
                      subtema=tema_subtema['subtema'])
            G.add_edge(etiqueta_principal, etiqueta, tipo='modifica')
       
        # 2. Procesamiento de "Modificada por"
        # Si hay historial de modificaciones, usarlo para obtener más detalles
        if not pd.isna(norma_principal['Historial_Modificaciones'].values[0]):
            historial = extraer_info_historial(norma_principal['Historial_Modificaciones'].values[0])
           
            for tipo, num, fecha in historial:
                # Intentar obtener más información sobre esta norma
                norma_modificadora = df[df['Número'] == int(num)]
                titulo = "Sin título"
                resumen = "Sin resumen"
               
                if len(norma_modificadora) > 0:
                    if 'Título / Referencia' in norma_modificadora.columns:
                        titulo = norma_modificadora['Título / Referencia'].values[0]
                    if 'Resumen' in norma_modificadora.columns:
                        resumen = norma_modificadora['Resumen'].values[0]
               
                # Obtener etiquetas, tema y subtema
                etiquetas = obtener_etiquetas_norma(tipo, num)
                tema_subtema = obtener_tema_subtema_norma(tipo, num)
               
                etiqueta = f"{tipo} {num}\n({fecha})"
                G.add_node(etiqueta,
                          tipo='modificadora',
                          fecha=fecha,
                          titulo=titulo,
                          resumen=resumen,
                          numero=num,
                          etiquetas=etiquetas,
                          tema=tema_subtema['tema'],
                          subtema=tema_subtema['subtema'])
                G.add_edge(etiqueta, etiqueta_principal, tipo='modifica')
        else:
            # Usar los datos de "Modificada por" si no hay historial
            numeros_modificada_por = extraer_numeros(norma_principal['Modificada por (numero)'].values[0])
            fechas_modificada_por = extraer_fechas(norma_principal['Modificada por (fecha)'].values[0])
           
            for i, num in enumerate(numeros_modificada_por):
                fecha_raw = fechas_modificada_por[i] if i < len(fechas_modificada_por) else None
                fecha = formatear_fecha(fecha_raw)
               
                # Determinar el tipo de norma modificadora
                norma_modificadora = df[df['Número'] == int(num)]
                tipo_norma = "NCG"  # Por defecto
                titulo = "Sin título"
                resumen = "Sin resumen"
               
                if len(norma_modificadora) > 0:
                    tipo_norma = norma_modificadora['Tipo de Norma'].values[0]
                    if 'Título / Referencia' in norma_modificadora.columns:
                        titulo = norma_modificadora['Título / Referencia'].values[0]
                    if 'Resumen' in norma_modificadora.columns:
                        resumen = norma_modificadora['Resumen'].values[0]
               
                # Obtener etiquetas, tema y subtema
                etiquetas = obtener_etiquetas_norma(tipo_norma, num)
                tema_subtema = obtener_tema_subtema_norma(tipo_norma, num)
               
                etiqueta = f"{tipo_norma} {num}\n({fecha})"
                G.add_node(etiqueta,
                          tipo='modificadora',
                          fecha=fecha_raw,
                          titulo=titulo,
                          resumen=resumen,
                          numero=num,
                          etiquetas=etiquetas,
                          tema=tema_subtema['tema'],
                          subtema=tema_subtema['subtema'])
                G.add_edge(etiqueta, etiqueta_principal, tipo='modifica')
       
        # 3. Procesamiento de "Deroga a"
        numeros_deroga = extraer_numeros(norma_principal['Deroga a (numero)'].values[0])
        fechas_deroga = extraer_fechas(norma_principal['Deroga a (fecha)'].values[0])
       
        for i, num in enumerate(numeros_deroga):
            fecha_raw = fechas_deroga[i] if i < len(fechas_deroga) else None
            fecha = formatear_fecha(fecha_raw)
           
            # Determinar el tipo de norma derogada
            norma_derogada = df[df['Número'] == int(num)]
            tipo_norma = "NCG"  # Por defecto
            titulo = "Sin título"
            resumen = "Sin resumen"
           
            if len(norma_derogada) > 0:
                tipo_norma = norma_derogada['Tipo de Norma'].values[0]
                if 'Título / Referencia' in norma_derogada.columns:
                    titulo = norma_derogada['Título / Referencia'].values[0]
                if 'Resumen' in norma_derogada.columns:
                    resumen = norma_derogada['Resumen'].values[0]
           
            # Obtener etiquetas, tema y subtema
            etiquetas = obtener_etiquetas_norma(tipo_norma, num)
            tema_subtema = obtener_tema_subtema_norma(tipo_norma, num)
           
            etiqueta = f"{tipo_norma} {num}\n({fecha})"
            G.add_node(etiqueta,
                      tipo='derogada',
                      fecha=fecha_raw,
                      titulo=titulo,
                      resumen=resumen,
                      numero=num,
                      etiquetas=etiquetas,
                      tema=tema_subtema['tema'],
                      subtema=tema_subtema['subtema'])
            G.add_edge(etiqueta_principal, etiqueta, tipo='deroga')
       
        # 4. Procesamiento de "Derogada por"
        # Corregir el problema de "derogada por 0.0"
        derogada_por_numero = norma_principal['Derogada por (numero)'].values[0]
       
        # Verificar si el valor es válido (no es NaN y no es 0)
        if not pd.isna(derogada_por_numero) and derogada_por_numero != 0:
            num_derogada_por = derogada_por_numero
            fecha_derogada_por_raw = norma_principal['Derogada por (fecha)'].values[0]
            fecha_derogada_por = formatear_fecha(fecha_derogada_por_raw)
           
            # Determinar el tipo de norma derogadora
            norma_derogadora = df[df['Número'] == int(num_derogada_por)]
            tipo_norma = "NCG"  # Por defecto
            titulo = "Sin título"
            resumen = "Sin resumen"
           
            if len(norma_derogadora) > 0:
                tipo_norma = norma_derogadora['Tipo de Norma'].values[0]
                if 'Título / Referencia' in norma_derogadora.columns:
                    titulo = norma_derogadora['Título / Referencia'].values[0]
                if 'Resumen' in norma_derogadora.columns:
                    resumen = norma_derogadora['Resumen'].values[0]
           
            # Obtener etiquetas, tema y subtema
            etiquetas = obtener_etiquetas_norma(tipo_norma, num_derogada_por)
            tema_subtema = obtener_tema_subtema_norma(tipo_norma, num_derogada_por)
           
            etiqueta = f"{tipo_norma} {num_derogada_por}\n({fecha_derogada_por})"
            G.add_node(etiqueta,
                      tipo='derogadora',
                      fecha=fecha_derogada_por_raw,
                      titulo=titulo,
                      resumen=resumen,
                      numero=num_derogada_por,
                      etiquetas=etiquetas,
                      tema=tema_subtema['tema'],
                      subtema=tema_subtema['subtema'])
            G.add_edge(etiqueta, etiqueta_principal, tipo='deroga')
       
        # Determinar el estado de la norma correctamente
        if not pd.isna(derogada_por_numero) and derogada_por_numero != 0:
            estado = 'Derogada'
        else:
            # Verificar si hay otras indicaciones de vigencia
            if 'Vigencia' in norma_principal.columns and not pd.isna(norma_principal['Vigencia'].values[0]):
                estado = str(norma_principal['Vigencia'].values[0])
            else:
                estado = 'Vigente'
       
        # Obtener información resumida de la norma principal para devolver
        # Convertir valores a tipos Python estándar para asegurar la serialización JSON
        info_norma = {
            'tipo': str(tipo_norma_principal),
            'numero': str(numero_norma),
            'fecha': fecha_str,
            'titulo': str(titulo_principal),
            'resumen': str(resumen_principal),
            'num_modificaciones': int(norma_principal['Num_Modificaciones'].values[0]) if 'Num_Modificaciones' in norma_principal.columns else 0,
            'num_modifica': len(numeros_modifica),
            'num_deroga': len(numeros_deroga),
            'estado': estado,
            'etiquetas': etiquetas_principal,
            'tema': tema_subtema['tema'],
            'subtema': tema_subtema['subtema']
        }
       
        return G, info_norma
       
    except Exception as e:
        error_msg = f"Error al crear el grafo: {str(e)}"
        traceback.print_exc()
        return None, error_msg
 
def generar_imagen_grafo(G, info_norma):
    """
    Genera una imagen del grafo y la devuelve como datos base64
    """
    if G is None or len(G.nodes()) == 0:
        return None, "No hay relaciones para visualizar."
   
    # Crear una figura
    plt.figure(figsize=(12, 9))
   
    # Posicionamiento del grafo
    pos = nx.spring_layout(G, k=0.5, iterations=50)
   
    # Definir colores según el tipo de nodo
    colores = {
        'principal': 'gold',
        'modificada': 'lightblue',
        'modificadora': 'lightgreen',
        'derogada': 'salmon',
        'derogadora': 'red'
    }
   
    # Asignar colores a los nodos
    node_colors = [colores[G.nodes[node]['tipo']] for node in G.nodes()]
   
    # Definir estilos de borde según el tipo de relación
    edge_styles = []
    edge_colors = []
    for u, v, data in G.edges(data=True):
        if data.get('tipo') == 'modifica':
            edge_styles.append('solid')
            edge_colors.append('green')
        elif data.get('tipo') == 'deroga':
            edge_styles.append('dashed')
            edge_colors.append('red')
        else:
            edge_styles.append('solid')
            edge_colors.append('blue')
   
    # Dibujar nodos
    nx.draw_networkx_nodes(G, pos, node_size=2000, node_color=node_colors, alpha=0.8)
   
    # Dibujar bordes
    for i, (u, v, data) in enumerate(G.edges(data=True)):
        edge_color = edge_colors[i]
        style = edge_styles[i]
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], width=2,
                            alpha=0.7, edge_color=edge_color, style=style,
                            connectionstyle='arc3,rad=0.1', arrowsize=15)
   
    # Dibujar etiquetas
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')
   
    # Crear leyenda para los tipos de nodos
    leyenda_nodos = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=tipo)
                    for tipo, color in colores.items()]
   
    # Crear leyenda para los tipos de relaciones
    leyenda_relaciones = [
        plt.Line2D([0], [0], color='green', lw=2, label='Modifica'),
        plt.Line2D([0], [0], color='red', lw=2, label='Deroga')
    ]
   
    # Añadir leyendas
    plt.legend(handles=leyenda_nodos + leyenda_relaciones, loc='upper left',
              title='Tipos de nodos y relaciones')
   
    plt.title(f"Grafo de relaciones para {info_norma['tipo']} {info_norma['numero']}")
    plt.axis('off')
    plt.tight_layout()
   
    # Guardar la figura en un buffer
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100)
    img_buffer.seek(0)
    plt.close()
   
    # Codificar la imagen en base64
    img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
   
    return img_base64
 
def obtener_info_detallada_norma(G, numero_norma):
    """
    Obtiene información detallada sobre una norma específica del grafo.
    """
    # Convertir a string para asegurar compatibilidad
    numero_norma = str(numero_norma)
   
    # Buscar el nodo que coincide con el número de norma
    nodo_encontrado = None
    for node, attrs in G.nodes(data=True):
        if str(attrs.get('numero')) == numero_norma:
            nodo_encontrado = node
            break
   
    if nodo_encontrado is None:
        return {
            'error': f"No se encontró ninguna norma con el número {numero_norma} en el grafo actual."
        }
   
    # Obtener atributos del nodo
    attrs = G.nodes[nodo_encontrado]
    tipo = attrs.get('tipo', 'desconocido')
    titulo = attrs.get('titulo', 'Sin título disponible')
    resumen = attrs.get('resumen', 'Sin resumen disponible')
    fecha = attrs.get('fecha', 'Fecha desconocida')
    etiquetas = attrs.get('etiquetas', [])
    tema = attrs.get('tema', '')
    subtema = attrs.get('subtema', '')
   
    if hasattr(fecha, 'strftime'):
        fecha = fecha.strftime('%d/%m/%Y')
    elif isinstance(fecha, np.datetime64):
        fecha = pd.Timestamp(fecha).strftime('%d/%m/%Y')
   
    # Obtener relaciones
    relaciones_salientes = []
    for u, v, data in G.out_edges(nodo_encontrado, data=True):
        relacion = data.get('tipo', 'relacionada con')
        nodo_destino = G.nodes[v]
        relaciones_salientes.append({
            'tipo': str(relacion),
            'etiqueta': str(v),
            'numero': str(nodo_destino.get('numero', '')),
            'titulo': str(nodo_destino.get('titulo', 'Sin título'))
        })
   
    relaciones_entrantes = []
    for u, v, data in G.in_edges(nodo_encontrado, data=True):
        relacion = data.get('tipo', 'relacionada con')
        nodo_origen = G.nodes[u]
        relaciones_entrantes.append({
            'tipo': str(relacion),
            'etiqueta': str(u),
            'numero': str(nodo_origen.get('numero', '')),
            'titulo': str(nodo_origen.get('titulo', 'Sin título'))
        })
   
    return {
        'etiqueta': str(nodo_encontrado),
        'tipo': str(tipo),
        'numero': str(attrs.get('numero', '')),
        'fecha': str(fecha),
        'titulo': str(titulo),
        'resumen': str(resumen),
        'etiquetas': etiquetas,
        'tema': str(tema),
        'subtema': str(subtema),
        'relaciones_salientes': relaciones_salientes,
        'relaciones_entrantes': relaciones_entrantes
    }
 
# Ruta para verificar el estado de carga de datos
@app.route('/estado')
def estado():
    global df_main, df_segmentacion
    if df_main is not None and not df_main.empty:
        info = {
            'estado': 'OK',
            'mensaje': f'Datos cargados correctamente. {len(df_main)} registros encontrados.',
            'columnas': [str(col) for col in df_main.columns.tolist()]
        }
       
        if df_segmentacion is not None and not df_segmentacion.empty:
            info['segmentacion'] = {
                'registros': len(df_segmentacion),
                'columnas': [str(col) for col in df_segmentacion.columns.tolist()],
                'temas': len(temas_unicos),
                'subtemas': len(subtemas_unicos),
                'etiquetas': len(etiquetas_unicas)
            }
       
        return jsonify(info)
    else:
        # Intentar cargar los datos nuevamente
        success, message = cargar_datos()
        if success:
            info = {
                'estado': 'OK',
                'mensaje': message,
                'columnas': [str(col) for col in df_main.columns.tolist()]
            }
           
            if df_segmentacion is not None and not df_segmentacion.empty:
                info['segmentacion'] = {
                    'registros': len(df_segmentacion),
                    'columnas': [str(col) for col in df_segmentacion.columns.tolist()],
                    'temas': len(temas_unicos),
                    'subtemas': len(subtemas_unicos),
                    'etiquetas': len(etiquetas_unicas)
                }
           
            return jsonify(info)
        else:
            return jsonify({
                'estado': 'ERROR',
                'mensaje': message
            })
 
# Rutas de la aplicación
@app.route('/')
def index():
    global df_main, df_segmentacion, temas_unicos, subtemas_unicos, etiquetas_unicas
   
    # Si los datos no están cargados, intentar cargarlos
    if df_main is None:
        success, message = cargar_datos()
        error = None if success else message
    else:
        error = None
   
    # Obtener todos los números de normas disponibles si los datos están cargados
    numeros_normas = []
    if df_main is not None and not df_main.empty:
        numeros_normas = sorted(df_main['Número'].astype(int).tolist())
   
    tiene_segmentacion = df_segmentacion is not None and not df_segmentacion.empty
    print("Etiquetas:", etiquetas_unicas)

    return render_template('index.html',
                          numeros_normas=numeros_normas,
                          error=error,
                          tiene_segmentacion=tiene_segmentacion,
                          temas=temas_unicos,
                          subtemas=subtemas_unicos,
                          etiquetas=etiquetas_unicas)
 
@app.route('/grafo', methods=['POST'])
def generar_grafo():
    global df_main, grafo_actual
   
    # Verificar si los datos están cargados
    if df_main is None or df_main.empty:
        success, message = cargar_datos()
        if not success:
            return jsonify({'error': message})
   
    numero_norma = request.form.get('numero_norma')
    if not numero_norma:
        return jsonify({'error': 'Debes proporcionar un número de norma'})
   
    G, info = crear_grafo_norma(df_main, numero_norma)
   
    if isinstance(info, str):  # Si es un mensaje de error
        return jsonify({'error': info})
   
    img_base64 = generar_imagen_grafo(G, info)
   
    # Guardar el grafo para futuras consultas
    grafo_actual = G
   
    return jsonify({
        'imagen': img_base64,
        'info': info
    })
 
@app.route('/detalles_norma/<numero_norma>', methods=['GET'])
def detalles_norma(numero_norma):
    global grafo_actual
   
    if 'grafo_actual' not in globals() or grafo_actual is None:
        return jsonify({'error': 'No hay un grafo cargado actualmente'})
   
    info_detallada = obtener_info_detallada_norma(grafo_actual, numero_norma)
    return jsonify(info_detallada)
 
@app.route('/buscar/<criterio>/<valor>', methods=['GET'])
def buscar(criterio, valor):
    """
    Busca normas según el criterio (etiqueta, tema, subtema) y valor especificados.
    """
    global df_main, df_segmentacion
   
    if df_segmentacion is None:
        return jsonify({'error': 'No se ha cargado la información de segmentación'})
   
    if criterio not in ['etiqueta', 'tema', 'subtema']:
        return jsonify({'error': 'Criterio de búsqueda no válido'})
   
    resultados = buscar_normas(criterio, valor)
   
    return jsonify({
        'criterio': criterio,
        'valor': valor,
        'resultados': resultados,
        'total': len(resultados)
    })
 
@app.route('/etiquetas', methods=['GET'])
def obtener_etiquetas():
    """
    Devuelve la lista de todas las etiquetas disponibles.
    """
    global etiquetas_unicas
   
    return jsonify({
        'etiquetas': etiquetas_unicas,
        'total': len(etiquetas_unicas)
    })
 
@app.route('/temas', methods=['GET'])
def obtener_temas():
    """
    Devuelve la lista de todos los temas disponibles.
    """
    global temas_unicos
   
    return jsonify({
        'temas': temas_unicos,
        'total': len(temas_unicos)
    })
 
@app.route('/subtemas', methods=['GET'])
def obtener_subtemas():
    """
    Devuelve la lista de todos los subtemas disponibles.
    """
    global subtemas_unicos
   
    return jsonify({
        'subtemas': subtemas_unicos,
        'total': len(subtemas_unicos)
    })
 
@app.route('/subtemas_por_tema/<tema>', methods=['GET'])
def obtener_subtemas_por_tema(tema):
    """
    Devuelve los subtemas asociados a un tema específico.
    """
    global df_segmentacion
   
    if df_segmentacion is None:
        return jsonify({'error': 'No se ha cargado la información de segmentación'})
   
    subtemas = df_segmentacion[df_segmentacion['Tema'] == tema]['Subtema'].dropna().unique()
    subtemas = [str(s) for s in subtemas]
   
    return jsonify({
        'tema': tema,
        'subtemas': sorted(subtemas),
        'total': len(subtemas)
    })
 
# Inicializar los datos al inicio
print("Iniciando carga de datos...")
success, message = cargar_datos()
print(message)
 

