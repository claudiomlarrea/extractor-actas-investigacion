#!/usr/bin/env python3
"""Comprueba acceso de la cuenta de servicio a planilla y carpetas Drive."""
import json
import os
import sys

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

CREDS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
FOLDERS = [
    x.strip()
    for x in os.environ.get("ACTAS_DRIVE_FOLDER_ID", "").split(",")
    if x.strip()
]
FOLDERS += [
    x.strip()
    for x in os.environ.get("ACTAS_DRIVE_FOLDER_IDS", "").split(",")
    if x.strip()
]
SHEET_ID = os.environ.get("CONSEJO_SHEET_ID", "17MiyW17W7oLIwSCKjDXCoA85CwBkYqHYhDKblVN37c8")


def main() -> int:
    if not CREDS or not os.path.isfile(CREDS):
        print("Definí GOOGLE_APPLICATION_CREDENTIALS apuntando al JSON de la cuenta de servicio.")
        return 1

    with open(CREDS, encoding="utf-8") as f:
        sa = json.load(f)
    email = sa.get("client_email", "?")
    print(f"Cuenta de servicio: {email}\n")

    creds = Credentials.from_service_account_file(
        CREDS,
        scopes=[
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/spreadsheets.readonly",
        ],
    )
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)

    try:
        meta = drive.files().get(fileId=SHEET_ID, fields="id,name", supportsAllDrives=True).execute()
        print(f"✓ Planilla accesible: «{meta.get('name')}»")
    except HttpError as exc:
        print(f"✗ Planilla NO accesible ({exc.resp.status}). Compartila con {email}")

    if not FOLDERS:
        print("\nSin ACTAS_DRIVE_FOLDER_ID. Ejemplo:")
        print("  ACTAS_DRIVE_FOLDER_ID=1abc... python3 scripts/verify_drive_access.py")
        return 0

    print()
    ok = 0
    for fid in FOLDERS:
        try:
            meta = drive.files().get(
                fileId=fid, fields="id,name,driveId", supportsAllDrives=True
            ).execute()
            where = "unidad compartida" if meta.get("driveId") else "Mi unidad / compartido"
            print(f"✓ Carpeta OK: «{meta.get('name')}» ({fid}) — {where}")
            ok += 1
        except HttpError as exc:
            print(f"✗ Carpeta NO accesible: {fid} (HTTP {exc.resp.status})")
            print(f"  → Compartir con {email} como Lector")

    print(f"\nCarpetas accesibles: {ok}/{len(FOLDERS)}")
    if ok == 0:
        print(
            "\nSi ya compartiste y sigue fallando:\n"
            "  1) Abrí Compartir y verificá que aparezca looker-sync@...\n"
            "  2) Si está en una Unidad compartida, agregá la cuenta a la unidad entera\n"
            "  3) Pedí a TI que permita compartir con cuentas de servicio externas"
        )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
