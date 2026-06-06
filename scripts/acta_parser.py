"""
Extrae ítems de actas del Consejo de Investigación (PDF) para cargar en Looker.

Tipos alineados al Sistema Consejo (Streamlit):
  - Proyecto de Investigación
  - Informe Final
  - Informe de Avance
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, replace
from pathlib import Path
from typing import List, Optional, Tuple

try:
    import pdfplumber
except ImportError:  # pragma: no cover
    pdfplumber = None

TIPO_PROYECTO = "Proyecto de Investigación"
TIPO_INFORME_FINAL = "Informe Final"
TIPO_INFORME_AVANCE = "Informe de Avance"

MESES = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}

JUNK_TITLE_PATTERNS = (
    r"^informes?\s+(finales?|de\s+avance|avance)",
    r"^presentaci[oó]n\s+de\s+(los\s+)?proyectos?",
    r"^proyectos?\s+picto",
    r"^enviar por mail",
    r"^lectura del acta",
    r"^resultados finales evaluaci",
    r"^categorizaci[oó]n extraordinaria",
    r"^convocatoria\s",
    r"^l[ií]neas prioritarias",
    r"^sigeva",
    r"^protocolo de actuaci",
    r"^directora?\b",
    r"^co\s*directora?",
    r"^codirectora?",
    r"^equipo de",
    r"^facultad de",
    r"^facultad ciencias",
    r"^escuela de",
    r"^instituto superior",
)

BULLET = r"[\uf0b7\u2022\u25cf•❖➢●\-]"

FACULTAD_START = r"(?:Facultad de|Facultad Ciencias|Facultad Don Bosco|Instituto Superior|Escuela de)"


def _is_junk_title(titulo: str) -> bool:
    t = _norm_key(titulo)
    if len(t) < 12:
        return True
    for pat in JUNK_TITLE_PATTERNS:
        if re.search(pat, t, re.I):
            return True
    return False


FACULTAD_TO_UNIDAD: List[Tuple[str, str]] = [
    (r"Filosof[ií]a y Humanidades", "FFyHSJ- Facultad de Filosofía y Humanidades"),
    (r"Don Bosco|Enolog[ií]a y Ciencias de la Alimentaci[oó]n", "FBOSCO- Facultad Don Bosco"),
    (r"Ciencias M[eé]dicas.*San Juan|Ciencias M[eé]dicas San Juan", "FCMSJ- Facultad de Ciencias Médicas San Juan"),
    (r"Ciencias M[eé]dicas.*San Luis", "FCMSL- Facultad de Ciencias Médicas Sede San Luis"),
    (r"Ciencias Veterinarias", "FCVSL- Facultad de Ciencias Veterinarias Sede San Luis"),
    (r"Derecho y Ciencias Sociales.*San Juan", "FDCSSJ- Facultad de Derecho y Ciencias Sociales Sede San Juan"),
    (r"Derecho y Ciencias Sociales.*San Luis", "FDCSSL- Facultad de Derecho y Ciencias Sociales Sede San Luis"),
    (r"Ciencias Econ[oó]micas.*San Juan", "FCEESJ- Facultad de Ciencias Económicas y Empresariales Sede San Juan"),
    (r"Ciencias Econ[oó]micas.*San Luis", "FCEESL- Facultad de Ciencias Económicas y Empresariales Sede San Luis"),
    (r"Educaci[oó]n", "FEDSJ- Facultad de Educación"),
    (r"Ciencias Qu[ií]micas", "FCQyTSJ- Facultad de Ciencias Químicas y Tecnológicas"),
    (r"Cultura Religiosa|ECRyPSJ", "ECRyPSJ- Escuela Cultura Religiosa y Pastoral"),
    (r"Escuela de Seguridad", "ESEGSJ- Escuela de Seguridad"),
    (r"Santa Mar[ií]a", "ISDSM- Instituto Universitario Santa María"),
    (r"San Buenaventura", "ISB- Instituto San Buenaventura"),
    (r"Vicerrectorad", "Vicerrectora de Formación"),
]


@dataclass
class ActaItem:
    numero_acta: str
    fecha_texto: str
    anio: str
    tipo: str
    titulo: str
    director: str
    unidad: str
    equipo: str
    fuente_pdf: str

    def dedup_key(self) -> str:
        return "|".join(
            [
                self.numero_acta,
                self.tipo,
                _norm_key(self.titulo),
            ]
        )


def _norm_key(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\s+", " ", s).strip().lower()
    s = re.sub(r"[^\w\s]", "", s)
    return s


def _fix_pdf_spacing(text: str) -> str:
    text = text or ""
    text = text.replace("\u00a0", " ")
    text = text.replace("\u201c", '"').replace("\u201d", '"').replace("\u2018", "'").replace("\u2019", "'")
    glued = [
        (r"tratan\s*los\s*siguientes", "Se tratan los siguientes temas:"),
        (r"Se\s*tratan\s*los\s*siguientes\s*temas", "Se tratan los siguientes temas:"),
        (r"Presentaci[oó]n\s*de\s*Proyectos?\s*DE\s*INVESTIGACI[ÓO]N", "Presentación de Proyectos de Investigación"),
        (r"Presentaci[oó]n\s*de\s*Proyectos?", "Presentación de Proyectos"),
        (r"Presentaci[oó]n\s*de\s*la", "Presentación de la"),
        (r"Informes?\s*Finales?", "Informes Finales"),
        (r"Informes?\s*de\s*Avance", "Informes de Avance"),
        (r"Informes?\s*Avance", "Informes de Avance"),
        (r"Informede\s*Avance", "Informes de Avance"),
        (r"Proyecto\s*:", "Proyecto:"),
        (r"Facultad\s*de", "Facultad de"),
        (r"Facultad\s*Ciencias", "Facultad Ciencias"),
        (r"Escuela\s*de", "Escuela de"),
        (r"Instituto\s*Superior", "Instituto Superior"),
        (r"Directora?\s*:", "Directora:"),
        (r"Co\s*Directora?", "Co Directora:"),
        (r"Equipo\s*de\s*Investigaci[oó]n", "Equipo de Investigación"),
        (r"Equipo\s*de\s*Trabajo", "Equipo de Trabajo"),
        (r"Siendo\s*las", "Siendo las"),
        (r"nohabiendo", "no habiendo"),
        (r"Lectura\s*del\s*acta", "Lectura del acta"),
        (r"Le[ií]da\s*el\s*acta", "Leída el acta"),
    ]
    for pat, repl in glued:
        text = re.sub(pat, repl, text, flags=re.IGNORECASE)
    text = re.sub(r"([a-záéíóúñ])([A-ZÁÉÍÓÚÑ])", r"\1 \2", text)
    text = re.sub(r"(\.)([A-ZÁÉÍÓÚÑ\"])", r"\1 \2", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _map_unidad(facultad_line: str) -> str:
    line = facultad_line.strip().rstrip(":")
    for pattern, unidad in FACULTAD_TO_UNIDAD:
        if re.search(pattern, line, re.IGNORECASE):
            return unidad
    line = re.sub(r"\s*–\s*Universidad Católica de Cuyo.*$", "", line, flags=re.I)
    line = re.sub(r"\s*-\s*Universidad Católica de Cuyo.*$", "", line, flags=re.I)
    return line[:120] if line else ""


def _parse_fecha(text: str) -> Tuple[str, str]:
    m = re.search(
        r"a los\s+(\d{1,2})\s+d[ií]as del mes de\s+(\w+)\s+de\s+((?:dos mil\s+)?[\wáéíóúñ]+)",
        text,
        re.IGNORECASE,
    )
    if not m:
        m = re.search(
            r"(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})",
            text,
            re.IGNORECASE,
        )
    if not m:
        return "", ""

    dia, mes_raw, anio_raw = m.group(1), m.group(2).lower(), m.group(3).lower().strip()
    anio = _year_from_token(anio_raw)
    if not anio:
        return "", ""
    mes_nombre = mes_raw.capitalize()
    fecha = f"{dia} de {mes_nombre} {anio}"
    return fecha, anio


def _year_from_token(token: str) -> str:
    token = (token or "").strip().lower()
    token = unicodedata.normalize("NFKD", token)
    token = "".join(c for c in token if not unicodedata.combining(c))
    if re.fullmatch(r"\d{4}", token):
        return token
    token = re.sub(r"\s+", " ", token)
    if token.startswith("dos mil "):
        rest = token.replace("dos mil ", "").strip()
        mapping = {
            "veintitres": "2023",
            "veintitrés": "2023",
            "veinticuatro": "2024",
            "veinticinco": "2025",
            "veintiseis": "2026",
            "veintiséis": "2026",
        }
        return mapping.get(rest, "")
    return ""


def _year_from_path(path: Path) -> str:
    for part in path.parts:
        if re.fullmatch(r"20\d{2}", part):
            return part
    return ""


def _parse_numero_acta(text: str) -> str:
    m = re.search(r"ACTA\s+N[º°o\.]*\s*(\d+)", text, re.IGNORECASE)
    return m.group(1) if m else ""


def _extract_body(text: str) -> str:
    start = re.search(r"siguientes\s*temas", text, re.I)
    if not start:
        return text
    body_start = start.end()
    tail = text[body_start:]

    end = re.search(r"no habiendo m[aá]s temas", tail, re.I)
    if end:
        return tail[: end.start()]

    # Cierre de reunión: "Siendo las HH:MM" al final (no el del encabezado).
    closes = list(re.finditer(r"Siendo las \d{1,2}[:.\s]", tail, re.I))
    if len(closes) >= 1:
        return tail[: closes[-1].start()]

    return tail


def _split_sections(body: str) -> List[Tuple[str, str]]:
    markers = [
        (TIPO_PROYECTO, r"Resultados\s+Finales\s+evaluaci[oó]n\s+de\s+Proyectos"),
        (TIPO_PROYECTO, r"Presentaci[oó]n\s+de\s+Proyectos?(?:\s+de\s+Investigaci[oó]n)?"),
        (TIPO_INFORME_FINAL, r"\d+\.\s*Informes?\s+Finales?(?!\s+de\s+Avance)|(?<!\w)Informes?\s+Finales?(?!\s+de\s+Avance)"),
        (TIPO_INFORME_AVANCE, r"\d+\.\s*Informes?\s+(?:de\s+)?Avance|(?<!\w)Informes?\s+(?:de\s+)?Avance"),
    ]
    hits: List[Tuple[int, str]] = []
    for tipo, pat in markers:
        for m in re.finditer(pat, body, re.IGNORECASE):
            hits.append((m.start(), tipo))
    hits.sort(key=lambda x: x[0])

    if not hits:
        return []

    out: List[Tuple[str, str]] = []
    for i, (start, tipo) in enumerate(hits):
        end = hits[i + 1][0] if i + 1 < len(hits) else len(body)
        out.append((tipo, body[start:end]))
    return out


def _parse_director_equipo(snippet: str) -> Tuple[str, str]:
    director = ""
    equipo = ""
    patterns = [
        r"(?:Directora?|Co-?directora?|Codirectora?)\s*(?:del Proyecto)?\s*:?\s*([^\.]+?)(?:\.|$)",
        r"Director\s+del\s+Proyecto\s*:?\s*([^\.]+?)(?:\.|$)",
    ]
    for pat in patterns:
        m = re.search(pat, snippet, re.IGNORECASE)
        if m:
            director = m.group(1).strip(" .")
            break
    m2 = re.search(
        r"(?:Equipo de Investigaci[oó]n|Equipo de Trabajo)\s*:?\s*(.+?)(?:\.|$)",
        snippet,
        re.IGNORECASE,
    )
    if m2:
        equipo = m2.group(1).strip(" .")
    return director[:120], equipo[:300]


def _append_row(rows: List[Tuple[str, str, str]], titulo: str, director: str, equipo: str) -> None:
    titulo = re.sub(r"\s+", " ", (titulo or "").strip()).strip('"\' ')
    if _is_junk_title(titulo):
        return
    if titulo.startswith(". ") or titulo.startswith("Director del"):
        return
    if any(_norm_key(t) == _norm_key(titulo) for t, _, _ in rows):
        return
    rows.append((titulo, director, equipo))


def _extract_diamond_blocks(block: str) -> List[Tuple[str, str, str]]:
    rows: List[Tuple[str, str, str]] = []
    for m in re.finditer(
        r"❖\s*(.+?)(?=❖|Facultad|Escuela|Instituto|\d+\.\s|$)",
        block,
        re.I | re.S,
    ):
        chunk = m.group(1).strip()
        titulo = re.split(r"\s*(?:➢|●|Directora|Co Directora|Equipo de)", chunk, maxsplit=1, flags=re.I)[0]
        titulo = titulo.strip('"\' .:')
        if _is_junk_title(titulo):
            continue
        director, equipo = _parse_director_equipo(chunk)
        _append_row(rows, titulo, director, equipo)
    return rows


def _extract_bullet_blocks(block: str) -> List[Tuple[str, str, str]]:
    rows: List[Tuple[str, str, str]] = []
    if "❖" in block:
        rows.extend(_extract_diamond_blocks(block))
    chunks = re.split(r"(?=[●•➢])", block)
    for chunk in chunks:
        chunk = re.sub(rf"^{BULLET}\s*", "", chunk.strip())
        if len(chunk) < 15 or chunk.startswith("❖"):
            continue
        titulo = re.split(r"\s*(?:Directora|Co Directora|Equipo de)", chunk, maxsplit=1, flags=re.I)[0]
        titulo = titulo.strip('"\' .:')
        if _is_junk_title(titulo):
            continue
        director, equipo = _parse_director_equipo(chunk)
        _append_row(rows, titulo, director, equipo)
    return rows


def _extract_pronis_table(block: str) -> List[Tuple[str, str, str]]:
    if not re.search(r"PRONIS|evaluaci[oó]n de Proyectos", block, re.I):
        return []
    rows: List[Tuple[str, str, str]] = []
    m = re.search(
        r"Director/a\s*(.+?)(?=\d+\.\s+Presentaci|\d+\.\s+Informes|\d+\.\s+CATEGOR|$)",
        block,
        re.I | re.S,
    )
    if not m:
        return rows
    content = m.group(1)
    parts = re.split(rf"(?={FACULTAD_START})", content)
    for part in parts:
        part = part.strip()
        if len(part) < 50:
            continue
        unidad_raw = re.match(
            r"(" + FACULTAD_START + r".{8,120}?)(?:\s+–|\s+-|\s+[A-ZÁÉÍÓÚÑ])",
            part,
            re.I | re.S,
        )
        unidad_line = unidad_raw.group(1) if unidad_raw else part[:80]
        rest = part[len(unidad_line) :].strip()
        rest = re.sub(r"^(?:Tecnológicas|Sociales|Económicas)\s*–\s*Universidad Católica de Cuyo\s*", "", rest, flags=re.I)
        # Director/a suele ser 2-4 palabras capitalizadas antes del siguiente "Facultad"
        dm = re.search(
            r"([A-ZÁÉÍÓÚ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚ][a-záéíóúñ]+){1,3})\s+(?:Católica de Cuyo|Facultad|Instituto|Escuela|\d+\.)",
            rest,
        )
        director = dm.group(1).strip() if dm else ""
        titulo = rest
        if director:
            titulo = rest[: dm.start()].strip()
        titulo = re.sub(r"\s+", " ", titulo)
        titulo = titulo.strip(" .,-")
        if len(titulo) < 20 or _is_junk_title(titulo):
            continue
        if re.search(r"Universidad Católica de Cuyo", titulo[:80], re.I):
            continue
        _append_row(rows, titulo, director, "")
    return rows


def _extract_proyecto_lines(block: str) -> List[Tuple[str, str, str]]:
    rows: List[Tuple[str, str, str]] = []

    rows.extend(_extract_pronis_table(block))

    for m in re.finditer(
        r'Proyecto\s*:\s*"([^"]+)"\s*\.?\s*(.*?)(?=Proyecto\s*:|Facultad|Escuela|$)',
        block,
        re.IGNORECASE | re.DOTALL,
    ):
        _append_row(rows, m.group(1), *_parse_director_equipo(m.group(2)))

    for m in re.finditer(
        rf"{BULLET}\s*\"([^\"]+)\"\.?\s*(.*?)(?={BULLET}\s*\"|Facultad|Escuela|\d+\.\s|$)",
        block,
        re.IGNORECASE | re.DOTALL,
    ):
        _append_row(rows, m.group(1), *_parse_director_equipo(m.group(2)))

    for m in re.finditer(
        rf"{BULLET}\s*([A-ZÁÉÍÓÚÑ0-9][^\"\.]{{10,220}}?)\"\.\s*(.*?)(?={BULLET}|Facultad|Escuela|\d+\.\s|$)",
        block,
        re.DOTALL,
    ):
        _append_row(rows, m.group(1), *_parse_director_equipo(m.group(2)))

    for m in re.finditer(r'"([^"]{12,220})"', block):
        titulo = m.group(1).strip()
        tail = block[m.end() : m.end() + 400]
        if re.search(r"Directora?|Director|Equipo", tail, re.I):
            _append_row(rows, titulo, *_parse_director_equipo(tail))

    rows.extend(_extract_bullet_blocks(block))

    if re.search(r"PICTO|SECITI", block, re.I):
        for m in re.finditer(
            r"\d+\.\s+(.{20,220}?)(?=\s*\d+\.\s+|Los Proyectos|se aprueban|$)", block, re.S
        ):
            titulo = m.group(1).strip().rstrip(".")
            if re.search(r"se aprueban|Consejo Superior", titulo, re.I):
                continue
            _append_row(rows, titulo, "", "")

    return rows


def _split_by_facultad(block: str) -> List[Tuple[str, str]]:
    pat = re.compile(
        rf"({FACULTAD_START}[^•❖➢●\d]{{0,120}}(?::|(?=\s*{BULLET}|\s*Facultad|\s*Escuela|\s*Instituto|\d+\.\s)))",
        re.IGNORECASE,
    )
    matches = list(pat.finditer(block))
    if not matches:
        return [("", block)]

    out: List[Tuple[str, str]] = []
    for i, m in enumerate(matches):
        unidad = _map_unidad(m.group(0))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(block)
        out.append((unidad, block[start:end]))
    return out


def _parse_section_block(
    tipo: str,
    block: str,
    numero_acta: str,
    fecha: str,
    anio: str,
    pdf_name: str,
) -> List[ActaItem]:
    if re.search(r"enviar por mail el informe final|PICTO 2019", block, re.I) and not re.search(
        r'Proyecto\s*:|"[^"]{12,}|❖|➢|●', block
    ):
        return []

    items: List[ActaItem] = []
    for unidad, sub in _split_by_facultad(block):
        if not unidad:
            m = re.search(rf"{FACULTAD_START}[^:•❖]{{0,100}}", block, re.I)
            if m:
                unidad = _map_unidad(m.group(0))
        for titulo, director, equipo in _extract_proyecto_lines(sub):
            items.append(
                ActaItem(
                    numero_acta=numero_acta,
                    fecha_texto=fecha,
                    anio=anio,
                    tipo=tipo,
                    titulo=titulo,
                    director=director,
                    unidad=unidad,
                    equipo=equipo,
                    fuente_pdf=pdf_name,
                )
            )

    if not items:
        for titulo, director, equipo in _extract_proyecto_lines(block):
            items.append(
                ActaItem(
                    numero_acta=numero_acta,
                    fecha_texto=fecha,
                    anio=anio,
                    tipo=tipo,
                    titulo=titulo,
                    director=director,
                    unidad="",
                    equipo=equipo,
                    fuente_pdf=pdf_name,
                )
            )
    return items


def extract_text_from_pdf(path: Path) -> str:
    if pdfplumber is None:
        raise RuntimeError("Instalá pdfplumber: pip install pdfplumber")
    with pdfplumber.open(path) as pdf:
        return "\n".join((p.extract_text() or "") for p in pdf.pages)


def parse_acta_text(text: str, pdf_name: str = "", year_hint: str = "") -> List[ActaItem]:
    text = _fix_pdf_spacing(text)
    numero = _parse_numero_acta(text)
    fecha, anio = _parse_fecha(text)
    if year_hint and not anio:
        anio = year_hint
    if not numero:
        return []

    body = _extract_body(text)
    items: List[ActaItem] = []
    for tipo, chunk in _split_sections(body):
        items.extend(_parse_section_block(tipo, chunk, numero, fecha, anio, pdf_name))

    if not items:
        # Actas sin encabezados de sección: buscar bloques por facultad con ítems.
        for unidad, sub in _split_by_facultad(body):
            for titulo, director, equipo in _extract_proyecto_lines(sub):
                tipo = TIPO_PROYECTO
                if re.search(r"informe final", titulo, re.I):
                    tipo = TIPO_INFORME_FINAL
                elif re.search(r"informe de avance|informe avance", titulo, re.I):
                    tipo = TIPO_INFORME_AVANCE
                items.append(
                    ActaItem(
                        numero_acta=numero,
                        fecha_texto=fecha,
                        anio=anio,
                        tipo=tipo,
                        titulo=titulo,
                        director=director,
                        unidad=unidad,
                        equipo=equipo,
                        fuente_pdf=pdf_name,
                    )
                )

    if year_hint:
        fixed: List[ActaItem] = []
        for it in items:
            if not it.anio:
                fixed.append(replace(it, anio=year_hint))
            else:
                fixed.append(it)
        items = fixed
    return items


def parse_acta_pdf(path: Path, year_hint: str = "") -> List[ActaItem]:
    hint = year_hint or _year_from_path(path)
    text = extract_text_from_pdf(path)
    return parse_acta_text(text, pdf_name=path.name, year_hint=hint)
