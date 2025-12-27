import json
import base64
import boto3
import uuid

s3 = boto3.client("s3")

BUCKET_NAME = "velsync-ccd-uploads-jayanthiclaret"  

def lambda_handler(event, context):
    try:
        # Get content-type
        headers = event.get("headers", {})
        content_type = headers.get("content-type") or headers.get("Content-Type")

        if not content_type:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Content-Type missing"})
            }

        body = event["body"]

        # Decode body
        if event.get("isBase64Encoded"):
            body = base64.b64decode(body)

        # Extract boundary
        boundary = content_type.split("boundary=")[-1].encode()
        parts = body.split(boundary)

        for part in parts:
            if b'Content-Disposition' in part:
                header, file_data = part.split(b'\r\n\r\n', 1)
                file_data = file_data.rstrip(b'\r\n--')

                filename = f"{uuid.uuid4()}.png"

                s3.put_object(
                    Bucket=BUCKET_NAME,
                    Key=filename,
                    Body=file_data
                )

                return {
                    "statusCode": 200,
                    "body": json.dumps({
                        "message": "File uploaded successfully",
                        "filename": filename
                    })
                }

        return {
            "statusCode": 400,
            "body": json.dumps({"error": "File not found in request"})
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
