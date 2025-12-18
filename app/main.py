import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import httpx

app = FastAPI(title="EBook TTS MVP")

MN_API_KEY = os.getenv("MN_API_KEY")
MN_API_URL = "https://www.mnapi.com/v1/audio/speech"

@app.post("/tts")
async def text_to_speech(file: UploadFile = File(...)):
    # 1. 验证文件类型
    if file.content_type != "text/plain":
        raise HTTPException(400, "Only .txt files allowed")
    
    # 2. 读取文本并检查长度
    content = (await file.read()).decode("utf-8")
    if len(content) > 3500:
        raise HTTPException(400, "Text too long (max 3500 chars)")
    
    # 3. 调用 TTS API
    headers = {"Authorization": f"Bearer {MN_API_KEY}"}
    payload = {
        "model": "tts-1",
        "input": content,
        "voice": "alloy",
        "response_format": "mp3"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(MN_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        # 4. 生成临时文件名
        filename = f"output_{os.urandom(4).hex()}.mp3"
        with open(filename, "wb") as f:
            f.write(response.content)
        
        # 5. 返回音频文件
        return FileResponse(
            filename,
            media_type="audio/mpeg",
            filename=f"{file.filename}.mp3"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
