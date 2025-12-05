from fastapi import FastAPI, Query
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime
import psycopg2
import json

# ------------------------------------------------------------
# API initialization + GZIP compression
# ------------------------------------------------------------

app = FastAPI(
    title="GeoCetus API v2",
    description="REST API for accessing stranding datasets of cetaceans and sea turtles.",
    version="2.0",
    root_path="/gcapi"
)

# Enable gzip compression for JSON responses
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ------------------------------------------------------------
# CORS ENABLED HERE
# ------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # oppure metti domini specifici
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------
# Database configuration
# ------------------------------------------------------------

with open("config.json") as f:
    config = json.load(f)


def db_conn():
    """Open a new database connection using settings in config.json."""
    return psycopg2.connect(
        database=config["DB_NAME"],
        user=config["DB_USER"],
        password=config["DB_PASS"],
        host=config["DB_HOST"],
    )


# ------------------------------------------------------------
# Normalize table input (C/T → v_cetacei / v_tartarughe)
# ------------------------------------------------------------

def normalize_table(value: str) -> str:
    """
    Normalize table parameter:
    - 'C' or 'c' -> 'v_cetacei'
    - 'T' or 't' -> 'v_tartarughe'
    """
    v = value.strip().lower()
    if v == "c":
        return "v_cetacei"
    if v == "t":
        return "v_tartarughe"
    raise ValueError("Invalid table value. Use C (cetaceans) or T (turtles).")


# ------------------------------------------------------------
# GeoJSON conversion helper
# ------------------------------------------------------------

def rows_to_geojson(rows):
    features = []

    turtle_species = {"Caretta caretta", "Chelonia mydas", "Dermochelys coriacea"}

    cetacean_props = [
        "codice", "specie", "data_rilievo",
        "comune", "provincia", "regione",
        "latitudine", "longitudine",
        "sesso", "lunghezza", "condizioni",
        "targhetta", "targhetta_rilascio",
        "segnalatore", "rilevatore", "struttura_rilevatore"
    ]

    turtle_props = [
        "codice", "specie", "data_rilievo",
        "comune", "provincia", "regione",
        "latitudine", "longitudine",
        "sesso", "lunghezza", "tipo_lunghezza", "condizioni",
        "targhetta", "targhetta_rilascio",
        "segnalatore", "rilevatore", "struttura_rilevatore"
    ]

    for geometry_json, props in rows:

        # geometry_json è una stringa → convertirla in dict
        geometry = json.loads(geometry_json)

        # scegliere la lista di proprietà in base alla specie
        species = props.get("specie", "")
        props_list = turtle_props if species in turtle_species else cetacean_props

        # estrarre solo le proprietà richieste e in ordine
        properties = {k: props.get(k) for k in props_list}

        features.append({
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        })

    return {
        "type": "FeatureCollection",
        "count": len(features),
        "features": features
    }



# ------------------------------------------------------------
# Get valid species from lookup tables
# ------------------------------------------------------------

def get_species_mapping(table_norm: str):
    """
    Returns a mapping where both scientific and common names (normalized)
    map to the normalized scientific name.
    Example:
        'tartaruga comune'  -> 'caretta caretta'
        'caretta caretta'   -> 'caretta caretta'
    """
    lookup = "specie_cetacei" if table_norm == "v_cetacei" else "specie_tartarughe"

    conn = db_conn()
    cur = conn.cursor()
    cur.execute(f"SELECT nome_scientifico, nome_comune FROM {lookup};")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    mapping = {}

    for sci, com in rows:
        sci_norm = " ".join(sci.strip().lower().split())
        mapping[sci_norm] = sci_norm  # scientific → scientific

        if com:
            com_norm = " ".join(com.strip().lower().split())
            mapping[com_norm] = sci_norm  # common name → scientific

    return mapping


# ------------------------------------------------------------
# ENDPOINT — /v2/species
# ------------------------------------------------------------

@app.get(
    "/v2/species",
    summary="List species",
    description="Return available species (scientific and common names) for cetaceans or turtles.",
)
def list_species(
    table: str = Query(..., description="C = cetaceans, T = sea turtles"),
):
    try:
        table_norm = normalize_table(table)
    except ValueError as e:
        return {"error": str(e)}

    lookup = "specie_cetacei" if table_norm == "v_cetacei" else "specie_tartarughe"

    conn = db_conn()
    cur = conn.cursor()
    cur.execute(
        f"""
        SELECT
            sid,
            TRIM(nome_scientifico) AS scientific_name,
            TRIM(nome_comune)      AS common_name
        FROM {lookup}
        ORDER BY nome_scientifico;
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return {
        "count": len(rows),
        "species": [
            {
                "sid": sid,
                "scientific_name": sci,
                "common_name": com,
            }
            for sid, sci, com in rows
        ],
    }


# ------------------------------------------------------------
# ENDPOINT — /v2/regions
# ------------------------------------------------------------

@app.get(
    "/v2/regions",
    summary="List Italian regions in dataset",
)
def list_regions():
    conn = db_conn()
    cur = conn.cursor()
    cur.execute("SELECT cod_istat, nome FROM regioni ORDER BY nome;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return {
        "count": len(rows),
        "regions": [{"cod_istat": cod, "name": nome} for cod, nome in rows],
    }


# ------------------------------------------------------------
# ENDPOINT — /v2/records
# ------------------------------------------------------------

@app.get(
    "/v2/records",
    summary="Extract stranding records",
    description=(
        "Returns cetacean or sea turtle stranding events.\n\n"
        "Filters available:\n"
        "- table: C (cetaceans) or T (turtles)\n"
        "- period: YYYY-MM-DD/YYYY-MM-DD\n"
        "- species: comma-separated list of species (scientific or common names)\n"
        "- region: comma-separated list of regions\n"
        "- bbox: xmin,ymin,xmax,ymax (WGS84)\n"
        "- limit: max number of returned records"
    ),
)
def get_records(
    table: str = Query(..., description="C = cetaceans, T = sea turtles"),
    period: Optional[str] = Query(
        None, description="Date range: YYYY-MM-DD/YYYY-MM-DD"
    ),
    species: Optional[str] = Query(
        None, description="Comma-separated species list"
    ),
    region: Optional[str] = Query(
        None, description="Comma-separated region list"
    ),
    bbox: Optional[str] = Query(
        None, description="Bounding box: xmin,ymin,xmax,ymax (WGS84)"
    ),
    limit: Optional[int] = Query(
        None, description="Limit number of returned records"
    ),
):
    try:
        table_norm = normalize_table(table)
    except ValueError as e:
        return {"error": str(e)}

    filters = []
    params = []

    # --------------------------------------------------------
    # Period filter
    # --------------------------------------------------------
    if period:
    try:
        d1, d2 = period.split("/")
        # Usa direttamente le stringhe, lascia a Postgres il cast
        filters.append("data_rilievo::date BETWEEN %s::date AND %s::date")
        params.extend([d1, d2])
    except Exception:
        return {
            "error": "Invalid period format. Use YYYY-MM-DD/YYYY-MM-DD."
        }


    # --------------------------------------------------------
    # Species filter (accepts scientific + common names)
    # --------------------------------------------------------
    if species:
        # Raw values as provided in the URL
        requested_raw = [s.strip() for s in species.split(",") if s.strip()]

        # Normalize: lowercase + collapse spaces
        requested_norm = [" ".join(s.lower().split()) for s in requested_raw]

        # Load species mapping (common/scientific -> scientific)
        mapping = get_species_mapping(table_norm)

        # Validate inputs: must all exist in the mapping
        invalid = [s for s in requested_norm if s not in mapping]
        if invalid:
            return {
                "error": "Invalid species value(s).",
                "invalid_species": invalid
            }

        # Convert all user input into scientific names
        scientific_targets = [mapping[s] for s in requested_norm]

        # Build the SQL clause
        clause_parts = ["LOWER(TRIM(specie)) = %s"] * len(scientific_targets)
        species_clause = "(" + " OR ".join(clause_parts) + ")"

        filters.append(species_clause)
        params.extend(scientific_targets)

    # --------------------------------------------------------
    # Region filter
    # --------------------------------------------------------
    if region:
        regions = [r.strip() for r in region.split(",") if r.strip()]
        if regions:
            region_clause_parts = ["regione ILIKE %s"] * len(regions)
            region_clause = "(" + " OR ".join(region_clause_parts) + ")"
            filters.append(region_clause)
            params.extend([f"%{r}%" for r in regions])

    # --------------------------------------------------------
    # BBOX filter
    # --------------------------------------------------------
    if bbox:
        try:
            minx, miny, maxx, maxy = map(float, bbox.split(","))
            filters.append("the_geom && ST_MakeEnvelope(%s, %s, %s, %s, 4326)")
            params.extend([minx, miny, maxx, maxy])
        except Exception:
            return {
                "error": "Invalid bbox format. Use xmin,ymin,xmax,ymax."
            }

    # --------------------------------------------------------
    # WHERE and LIMIT clauses
    # --------------------------------------------------------
    where_sql = ""
    if filters:
        where_sql = "WHERE " + " AND ".join(filters)

    limit_clause = f"LIMIT {limit}" if limit else ""

    # --------------------------------------------------------
    # Final SQL query
    # --------------------------------------------------------
    query = f"""
        SELECT
            ST_AsGeoJSON(the_geom::geometry, 6, 1),
            (to_jsonb(t) - 'the_geom') AS props
        FROM (
            SELECT *
            FROM {table_norm}
            {where_sql}
            ORDER BY data_rilievo DESC
            {limit_clause}
        ) AS t;
    """

    try:
        conn = db_conn()
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        # Log to console and return error as JSON
        print("SQL ERROR:", e)
        return {"error": str(e)}

    return rows_to_geojson(rows)


