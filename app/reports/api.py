from fastapi import APIRouter, Depends, HTTPException
import pandas as pd

from app.database import SessionLocal, get_db
from app.user.models import Email


report_router = APIRouter()


@report_router.get("/read_csv_from_url")
async def read_csv_from_url(request_data: dict,db: SessionLocal = Depends(get_db)):
    language = request_data.get("language")
    try:
        # Replace the Google Sheets URL with the export link to a CSV file
        csv_url = "https://docs.google.com/spreadsheets/d/11-a-pSwwMYSYjfHzIRL6IbXQBvM0RJ8PCXZdbeZqb-g/export?format=csv&id=11-a-pSwwMYSYjfHzIRL6IbXQBvM0RJ8PCXZdbeZqb-g&gid=0"

        # Read the CSV file from the provided URL using pandas
        df = pd.read_csv(csv_url)

        # Map "data" to columns in DataFrame
        result = []
        for item in request_data["data"]:
            filtered_df = df[
                (df['Question Pair'] == item.get("pair")) &
                (df['Response 1'] == item.get("response1")) &
                (df['Response 2'] == item.get("response2"))
            ]
            filtered_data = filtered_df['English Text'].iloc[0] if language == 'en' else filtered_df['Japanese Text'].iloc[0]
            result.append({"skill": item.get("pair_name"),
                          "quotes": f"{filtered_data}"})

        
        
        user_data = db.query(Email).filter(id == request_data.get("user_id")).first()
        print(user_data.__dict__,'rtyui')
        feedback = {
            "user": {
                "name": "[prema]",
                "app_name": "Querly"
            },
            "questionnaire_results": result,
            "closing_message": "Remember, these suggestions are tailored to your self-assessment and are meant to guide your continuous development as an entrepreneur. We encourage you to revisit the questionnaire periodically to track your progress and refine your skills further.",
            "team_message": "Best regards, Querly Team"
        }
        return {"success": True, "result": feedback}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to map data to columns: {str(e)}")
