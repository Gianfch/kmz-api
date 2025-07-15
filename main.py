from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import zipfile, os, uuid
from lxml import etree
from pyproj import Transformer
from openpyxl import Workbook

app = FastAPI()
os.makedirs("output", exist_ok=True)
os.makedirs("temp", exist_ok=True)
app.mount("/files", StaticFiles(directory="output"), name="files")

transformer = Transformer.from_crs("EPSG:4326", "EPSG:32723", always_xy=True)

def decimal_to_dms(value, is_lat=True):
    direction = 'N' if value >= 0 else 'S' if is_lat else 'E' if value >= 0 else 'W'
    abs_val = abs(value)
    degrees = int(abs_val)
    minutes = int((abs_val - degrees) * 60)
    seconds = (abs_val - degrees - minutes/60) * 3600
    return f"{degrees}°{minutes}'{seconds:.2f}\"{direction}"

@app.post("/process-kmz")
async def process_kmz(file: UploadFile = File(...)):
    if not file.filename.endswith(".kmz"):
        raise HTTPException(status_code=400, detail="Arquivo deve ser .kmz")
    try:
        file_id = str(uuid.uuid4())
        zip_path = f"temp/{file_id}.zip"
        kml_path = f"temp/{file_id}.kml"
        with open(zip_path, "wb") as f:
            f.write(await file.read())
        with zipfile.ZipFile(zip_path, "r") as zf:
            kml_files = [f for f in zf.namelist() if f.endswith(".kml")]
            if not kml_files:
                raise HTTPException(status_code=400, detail="Nenhum .kml encontrado")
            zf.extract(kml_files[0], path="temp/")
            os.rename(f"temp/{kml_files[0]}", kml_path)
        tree = etree.parse(kml_path)
        ns = {"kml": "http://www.opengis.net/kml/2.2"}
        placemarks = tree.xpath("//kml:Placemark", namespaces=ns)
        data = []
        for p in placemarks:
            name_el = p.find("kml:name", namespaces=ns)
            coord_el = p.find(".//kml:coordinates", namespaces=ns)
            if coord_el is None:
                continue
            try:
                lon, lat, *_ = map(float, coord_el.text.strip().split(","))
            except:
                continue
            name = name_el.text.strip() if name_el is not None else ""
            lat_dms = decimal_to_dms(lat, is_lat=True)
            lon_dms = decimal_to_dms(lon, is_lat=False)
            easting, northing = transformer.transform(lon, lat)
            data.append([name, lat_dms, lon_dms, round(lat, 6), round(lon, 6), round(easting, 2), round(northing, 2)])
        if not data:
            raise HTTPException(status_code=400, detail="Nenhum ponto válido encontrado.")
        file_out = f"output/{file_id}.xlsx"
        wb = Workbook()
        ws = wb.active
        ws.append(["Nome", "Latitude (GMS)", "Longitude (GMS)", "Latitude (GD)", "Longitude (GD)", "Longitude E", "Latitude S"])
        for row in data:
            ws.append(row)
        wb.save(file_out)
        return JSONResponse({"downloadUrl": f"/files/{file_id}.xlsx"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar: {str(e)}")

