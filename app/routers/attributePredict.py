from fastapi import APIRouter, File, UploadFile, HTTPException
from app.utils.preprocess_image import preprocess_image
from app.models import predict_attributes
from app.utils.database import execute_insert
from fastapi.responses import JSONResponse
from datetime import datetime

router = APIRouter()

@router.post("/")
async def attributePredict(file: UploadFile = File(...)):
    """Endpoint to predict fashion attributes from an image."""
    try:
        # Validate file type
        if not file.filename.endswith(('png', 'jpg', 'jpeg', 'HEIC')):
            raise HTTPException(status_code=400, detail="Invalid file type. Supported types: png, jpg, jpeg, heic.")

        # Read file and preprocess
        file_bytes = await file.read()
        image_url, processed_image = preprocess_image(file_bytes)

        # Predict attributes using the model
        predictions = predict_attributes(processed_image)

        # Insert predictions into the wardrobe table
        insert_query = """
            INSERT INTO wadrobe (imageUrl, gender, masterCategory, subCategory, articleType, season, usagetype, purchaseDate, price)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            image_url,
            predictions.get("gender"),
            predictions.get("masterCategory"),
            predictions.get("subCategory"),
            predictions.get("articleType"),
            predictions.get("season"),
            predictions.get("usage"),
            datetime.now().strftime('%Y-%m-%d'),
            None  # Assuming price is not available during prediction
        )
        execute_insert(insert_query, params)

        return JSONResponse(content={"predictions": predictions, "imageUrl": image_url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
