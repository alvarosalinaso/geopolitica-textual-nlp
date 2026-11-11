# Guía de embebido editorial (Datawrapper / Flourish)

Archivos generados por `python -m src.export_editorial_data`. Todos son CSV UTF-8,
agregados (sin texto de discursos ni URLs) y de menos de 2 MB.

| Archivo | Herramienta | Tipo de gráfico | Clave de unión |
|---|---|---|---|
| `dw_mapa_regiones_chile.csv` | Datawrapper | Choropleth map → *Chile » Regions* | `iso_code` (ISO 3166-2, `CL-RM`) |
| `dw_mapa_comunas_chile.csv` | Datawrapper | Symbol map → *Chile » Comunas* | `cut_comuna` (CUT, 5 dígitos) |
| `dw_mapa_mundo_paises.csv` | Datawrapper | Choropleth map → *World* | `iso3` (ISO 3166-1 alfa-3) |
| `flourish_red_presidente_lugar.csv` | Flourish | Sankey chart (o Network graph) | `Source` → `Target` |
| `flourish_red_coocurrencia_lugares.csv` | Flourish | Network graph (o Chord / Arc diagram) | `Source` ↔ `Target` |

---

## 1. Mapa coroplético de regiones — Datawrapper

1. **New Map → Choropleth map** → busca *Chile » Regions (2018)*.
2. **Add your data → Import dataset** → sube `dw_mapa_regiones_chile.csv`.
3. **Match**: columna de unión `iso_code` ↔ *ISO-Code* del mapa.
4. **Values**: `menciones` (o `menciones_por_discurso` si quieres una tasa comparable).
5. **Visualize → Colors**: escala secuencial de un solo tono, 5 pasos, interpolación *natural breaks*. Las regiones con 0 quedan en el color más claro (no en gris de “sin dato”).
6. **Annotate → Tooltip**: título `{{ region }}`, cuerpo `{{ tooltip }}<br>Lugar más citado: {{ lugar_principal }}`.

| Rol | Columna |
|---|---|
| Geo (unión) | `iso_code` |
| Color | `menciones` |
| Tooltip | `region`, `tooltip`, `lugar_principal` |

## 2. Mapa de símbolos por comuna — Datawrapper

1. **New Map → Symbol map** → *Chile » Comunas*.
2. Importa `dw_mapa_comunas_chile.csv`. Si Datawrapper muestra `5101` en vez de `05101`, marca la columna `cut_comuna` como **texto** en *Check & Describe*.
3. **Match**: `cut_comuna` ↔ *CUT* / *Código comuna*.
4. **Symbol size**: `menciones` (escala por área, no por radio). **Symbol color**: `iso_region` (categórica) o un solo color.
5. **Tooltip**: `{{ tooltip }}`.

| Rol | Columna |
|---|---|
| Geo (unión) | `cut_comuna` |
| Tamaño | `menciones` |
| Color | `iso_region` (opcional) |
| Tooltip | `tooltip` |

## 3. Mapa mundial — Datawrapper

1. **New Map → Choropleth map** → *World*.
2. Importa `dw_mapa_mundo_paises.csv`. **Match**: `iso3` ↔ *ISO3*.
3. **Values**: `menciones`. Chile se excluye a propósito (autorreferencia que aplasta la escala); márcalo con una anotación de texto.
4. **Tooltip**: `{{ tooltip }}`.

| Rol | Columna |
|---|---|
| Geo (unión) | `iso3` |
| Color | `menciones` |
| Tooltip | `pais`, `tooltip` |

## 4. Red presidente → lugar — Flourish

1. **New visualisation → Sankey chart** (lectura editorial más clara) o **Network graph**.
2. **Data → Upload** `flourish_red_presidente_lugar.csv` en la hoja *Links*.
3. Asignación de columnas:

| Rol en Flourish | Columna |
|---|---|
| Source | `Source` (presidente) |
| Target | `Target` (lugar) |
| Value / Weight | `Value` |
| Color de nodo (hoja *Points*, opcional) | `target_group` (`Chile` / `Internacional`) |
| Orden de nodos | `source_first_year` (orden cronológico) |

4. **Preview**: limita a los 10–15 presidentes más recientes si el Sankey se satura.

## 5. Red de co-ocurrencia de lugares — Flourish

1. **New visualisation → Network graph** (alternativas: *Chord diagram*, *Arc diagram*).
2. Sube `flourish_red_coocurrencia_lugares.csv` en *Links*.

| Rol en Flourish | Columna |
|---|---|
| Source | `Source` |
| Target | `Target` |
| Link width / Value | `Weight` (nº de oraciones donde ambos lugares aparecen juntos) |

3. La red es no dirigida: desactiva las flechas (*Links → Arrows: none*).

---

## Código de inserción (portfolio-web o README)

Reemplaza `DW_ID` / `FLOURISH_ID` por el identificador publicado.

### Datawrapper (iframe responsivo + lazy loading)

```html
<figure style="margin:0 auto;max-width:860px;">
  <iframe
    title="Menciones geográficas en las Cuentas Públicas por región"
    aria-label="Mapa coroplético"
    src="https://datawrapper.dwcdn.net/DW_ID/1/"
    loading="lazy"
    scrolling="no"
    frameborder="0"
    style="width:0;min-width:100%!important;border:none;"
    height="560"
    data-external="1"></iframe>
  <figcaption style="font:0.8rem/1.4 system-ui,sans-serif;color:#666;">
    Fuente: discursos presidenciales (BCN). Elaboración propia, geopolitica-textual-nlp.
  </figcaption>
</figure>
<script type="text/javascript">!function(){"use strict";window.addEventListener("message",(function(a){if(void 0!==a.data["datawrapper-height"]){var e=document.querySelectorAll("iframe");for(var t in a.data["datawrapper-height"])for(var r,i=0;r=e[i];i++)if(r.contentWindow===a.source){var d=a.data["datawrapper-height"][t]+"px";r.style.height=d}}}))}();</script>
```

### Flourish (iframe responsivo + lazy loading)

```html
<div style="position:relative;width:100%;max-width:900px;margin:0 auto;aspect-ratio:16/10;">
  <iframe
    title="Red presidente → lugar"
    src="https://flo.uri.sh/visualisation/FLOURISH_ID/embed"
    loading="lazy"
    sandbox="allow-same-origin allow-forms allow-scripts allow-downloads allow-popups allow-popups-to-escape-sandbox allow-top-navigation-by-user-activation"
    style="position:absolute;inset:0;width:100%;height:100%;border:0;"></iframe>
</div>
```

### README de GitHub

GitHub no renderiza iframes: enlaza una captura estática al gráfico interactivo.

```markdown
[![Mapa de menciones por región](docs/img/mapa_regiones.png)](https://datawrapper.dwcdn.net/DW_ID/)
```
