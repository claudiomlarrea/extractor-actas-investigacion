#!/usr/bin/env python3
"""
Sincroniza actas PDF del Consejo (Drive o carpeta local) → Google Sheet Hoja 2 (Looker).

Variables de entorno:
  GOOGLE_APPLICATION_CREDENTIALS   JSON cuenta de servicio
  CONSEJO_SHEET_ID                 default: 17MiyW17W7oLIwSCKjDXCoA85CwBkYqHYhDKblVN37c8
  CONSEJO_SHEET_TAB                default: Hoja 2
  ACTAS_DRIVE_FOLDER_ID            carpeta Drive ACTAS DE CONSEJO (recursiva)
  ACTAS_LOCAL_DIR                  alternativa: carpeta local con PDFs
  ACTAS_YEARS                      filtro opcional, ej. 2023,2024,2025
"""

from __future__ import annotations

import io
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

from acta_parser import ActaItem, parse_acta_pdf, parse_acta_text  # noqa: E402

SHEET_ID = os.environ.get("CONSEJO_SHEET_ID", "17MiyW17W7oLIwSCKjDXCoA85CwBkYqHYhDKblVN37c8").strip()
SHEET_TAB = os.environ.get("CONSEJO_SHEET_TAB", "Hoja 2").strip()
DRIVE_FOLDER_ID = os.environ.get("ACTAS_DRIVE_FOLDER_ID", "").strip()
DRIVE_FOLDER_IDS = [
    x.strip()
    for x in os.environ.get("ACTAS_DRIVE_FOLDER_IDS", "").split(",")
    if x.strip()
]
LOCAL_DIR = os.environ.get("ACTAS_LOCAL_DIR", "").strip()
# Si la carpeta raíz es «Secretaría de Investigación», solo entrar a esta subcarpeta.
ACTAS_SUBFOLDER = os.environ.get("ACTAS_DRIVE_SUBFOLDER", "Actas del Consejo").strip()
YEARS_FILTER = {
    y.strip()
    for y in os.environ.get("ACTAS_YEARS", "2023,2024,2025").split(",")
    if y.strip()
}
IMPORT_TAG = "Importación automática acta PDF"
REPLACE_IMPORT = os.environ.get("ACTAS_REPLACE_IMPORT", "").lower() in ("1", "true", "yes")

HEADERS = [
    "numero_acta",
    "FECHA",
    "AŃO",
    "TIPO",
    "TITULO",
    "DESCRIPCIÓN",
    "DIRECTOR",
    "CAT_DIRECTOR",
    "CODIRECTOR",
    "CAT_CODIRECTOR",
    "EQUIPO",
    "apellido_nombre_docente",
    "dni_docente",
    "UNIDAD ACADÉMICA",
    "RESOLUCION_CD",
    "RESOLUCION_CS",
    "INSTITUTO",
    "CATEDRA",
    "tipo de financiamiento",
    "Fuente de financiamiento",
    "Monto del financiamiento",
    "ALUMNOS",
    "PUNTAJE",
    "responsable_de_carga",
]


def item_to_row(item: ActaItem) -> List[str]:
    desc = f"Extraído de {item.fuente_pdf} (acta {item.numero_acta})."
    return [
        item.numero_acta,
        item.fecha_texto,
        item.anio,
        item.tipo,
        item.titulo,
        desc,
        item.director,
        "",
        "",
        "",
        item.equipo,
        "",
        "",
        item.unidad,
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        IMPORT_TAG,
    ]


def dedup_key_from_row(row: List[str]) -> str:
    acta = (row[0] or "").strip()
    tipo = (row[3] or "").strip().lower()
    titulo = (row[4] or "").strip().lower()
    titulo = " ".join(titulo.split())[:120]
    return f"{acta}|{tipo}|{titulo}"


def dedup_key_from_item(item: ActaItem) -> str:
    return item.dedup_key()


def get_credentials():
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if not creds_path or not Path(creds_path).is_file():
        raise SystemExit("Falta GOOGLE_APPLICATION_CREDENTIALS (JSON de cuenta de servicio).")
    from google.oauth2.service_account import Credentials

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    return Credentials.from_service_account_file(creds_path, scopes=scopes)


def existing_keys_from_sheet(ws) -> Set[str]:
    rows = ws.get_all_values()
    if len(rows) < 2:
        return set()
    keys = set()
    for row in rows[1:]:
        padded = row + [""] * (len(HEADERS) - len(row))
        keys.add(dedup_key_from_row(padded))
    return keys


def list_pdfs_from_drive(creds, folder_id: str) -> List[Tuple[str, bytes, str]]:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    from googleapiclient.errors import HttpError

    drive = build("drive", "v3", credentials=creds, cache_discovery=False)
    try:
        meta = (
            drive.files()
            .get(fileId=folder_id, fields="id,name", supportsAllDrives=True)
            .execute()
        )
        print(f"Drive: carpeta «{meta.get('name', folder_id)}» ({folder_id})", file=sys.stderr)
    except HttpError as exc:
        if exc.resp.status == 404:
            raise RuntimeError(
                f"Carpeta no encontrada o sin acceso: {folder_id}. "
                "Compartila con looker-sync@uccuyo-looker-sync.iam.gserviceaccount.com "
                "y verificá el ID en la URL (.../folders/ID)."
            ) from exc
        raise

    out: List[Tuple[str, bytes, str]] = []
    download_count = 0

    def walk(fid: str, path_prefix: str = "") -> None:
        nonlocal download_count
        if path_prefix:
            print(f"  Carpeta: {path_prefix.rstrip('/')}", file=sys.stderr, flush=True)
        page_token = None
        while True:
            resp = (
                drive.files()
                .list(
                    q=f"'{fid}' in parents and trashed=false",
                    fields="nextPageToken, files(id, name, mimeType)",
                    pageToken=page_token,
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                )
                .execute()
            )
            for f in resp.get("files", []):
                name = f.get("name", "")
                mime = f.get("mimeType", "")
                fid_child = f["id"]
                if mime == "application/vnd.google-apps.folder":
                    if path_prefix == "" and ACTAS_SUBFOLDER:
                        nl = name.lower()
                        sub = ACTAS_SUBFOLDER.lower()
                        is_actas = sub in nl or ("actas" in nl and "consejo" in nl)
                        is_year = name.isdigit() and name in YEARS_FILTER
                        if not is_actas and not is_year:
                            continue
                    if YEARS_FILTER and not any(y in name for y in YEARS_FILTER):
                        # Subcarpetas por año: 2023, 2024, 2025
                        if name.isdigit() and name not in YEARS_FILTER:
                            continue
                    walk(fid_child, f"{path_prefix}{name}/")
                elif mime == "application/pdf" or name.lower().endswith(".pdf"):
                    if "acta" not in name.lower():
                        continue
                    if YEARS_FILTER and path_prefix:
                        if not any(y in path_prefix for y in YEARS_FILTER):
                            continue
                    download_count += 1
                    label = f"{path_prefix}{name}" if path_prefix else name
                    print(f"  Descargando ({download_count}): {label}", file=sys.stderr, flush=True)
                    buf = io.BytesIO()
                    request = drive.files().get_media(fileId=fid_child, supportsAllDrives=True)
                    downloader = MediaIoBaseDownload(buf, request)
                    done = False
                    while not done:
                        _, done = downloader.next_chunk()
                    out.append((f"{path_prefix}{name}" if path_prefix else name, buf.getvalue()))
            page_token = resp.get("nextPageToken")
            if not page_token:
                break

    walk(folder_id)
    return out


def _path_matches_year_filter(rel: str) -> bool:
    if not YEARS_FILTER:
        return True
    parts = rel.replace("\\", "/").split("/")
    year_parts = [p for p in parts if re.fullmatch(r"20\d{2}", p)]
    if not year_parts:
        return True  # PDFs sueltos (prueba local) no se filtran por año
    return any(y in rel for y in YEARS_FILTER)


def list_pdfs_local(root: Path) -> List[Tuple[str, bytes, str]]:
    out: List[Tuple[str, bytes, str]] = []
    for path in sorted(root.rglob("*.pdf")):
        if "acta" not in path.name.lower():
            continue
        rel = str(path.relative_to(root))
        if not _path_matches_year_filter(rel):
            continue
        out.append((path.name, path.read_bytes(), rel))
    return out


def _year_hint_from_rel(rel: str) -> str:
    for part in rel.replace("\\", "/").split("/"):
        if re.fullmatch(r"20\d{2}", part):
            return part
    return ""


def parse_all_pdfs(pdf_list: Iterable[Tuple[str, bytes, str]]) -> List[ActaItem]:
    items: List[ActaItem] = []
    pdf_list = list(pdf_list)
    total = len(pdf_list)
    for i, (name, data, rel) in enumerate(pdf_list, start=1):
        print(f"  Parseando ({i}/{total}): {rel or name}", file=sys.stderr, flush=True)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(data)
            tmp_path = Path(tmp.name)
        try:
            items.extend(parse_acta_pdf(tmp_path, year_hint=_year_hint_from_rel(rel)))
        except Exception as exc:
            print(f"⚠ Error parseando {name}: {exc}", file=sys.stderr)
        finally:
            tmp_path.unlink(missing_ok=True)
    return items


def remove_import_rows(ws) -> int:
    rows = ws.get_all_values()
    if len(rows) < 2:
        return 0
    resp_idx = HEADERS.index("responsable_de_carga")
    header = rows[0]
    kept = [header]
    removed = 0
    for row in rows[1:]:
        padded = row + [""] * max(0, len(HEADERS) - len(row))
        if padded[resp_idx].strip() == IMPORT_TAG:
            removed += 1
            continue
        kept.append(padded[: max(len(header), len(HEADERS))])
    if removed:
        print(f"  Eliminando {removed} filas de importación previa...", file=sys.stderr, flush=True)
        ws.clear()
        ws.update(values=kept, range_name="A1")
    return removed


def push_items(items: List[ActaItem]) -> int:
    import gspread

    creds = get_credentials()
    gc = gspread.authorize(creds)
    ws = gc.open_by_key(SHEET_ID).worksheet(SHEET_TAB)

    if REPLACE_IMPORT:
        remove_import_rows(ws)

    existing = existing_keys_from_sheet(ws)
    to_add: List[List[str]] = []
    for item in items:
        key = dedup_key_from_item(item)
        if key in existing:
            continue
        existing.add(key)
        to_add.append(item_to_row(item))

    if to_add:
        print(f"  Subiendo {len(to_add)} filas a la planilla...", file=sys.stderr, flush=True)
        ws.append_rows(to_add, value_input_option="USER_ENTERED")
    return len(to_add)


def main() -> int:
    creds = get_credentials()
    pdf_list: List[Tuple[str, bytes, str]] = []

    if LOCAL_DIR:
        root = Path(LOCAL_DIR)
        if not root.is_dir():
            raise SystemExit(f"ACTAS_LOCAL_DIR no existe: {root}")
        pdf_list = list_pdfs_local(root)
        print(f"PDFs locales: {len(pdf_list)}", file=sys.stderr)
    elif DRIVE_FOLDER_IDS or DRIVE_FOLDER_ID:
        folder_ids = DRIVE_FOLDER_IDS or [DRIVE_FOLDER_ID]
        seen_names = set()
        for fid in folder_ids:
            try:
                for name, data, rel in list_pdfs_from_drive(creds, fid):
                    if name not in seen_names:
                        seen_names.add(name)
                        pdf_list.append((name, data, rel))
            except Exception as exc:
                print(f"⚠ Carpeta {fid}: {exc}", file=sys.stderr)
        print(f"PDFs en Drive: {len(pdf_list)}", file=sys.stderr)
    else:
        raise SystemExit(
            "Definí ACTAS_DRIVE_FOLDER_ID (una carpeta) o ACTAS_DRIVE_FOLDER_IDS (varias, separadas por coma).\n"
            "El ID sale de la URL de Drive: .../folders/ESTE_ES_EL_ID"
        )

    items = parse_all_pdfs(pdf_list)
    print(f"Ítems extraídos: {len(items)}", file=sys.stderr)
    added = push_items(items)
    print(f"Planilla «{SHEET_TAB}»: +{added} filas nuevas (total extraído: {len(items)}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
