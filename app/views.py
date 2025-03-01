import os
from pathlib import Path
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.conf import settings
import whisper
from django.views.decorators.csrf import csrf_exempt

model = whisper.load_model(
    name=settings.WHISPER_MODELS['tiny.en'],  # BASE_DIR / 'models/tiny.en.pt',
    in_memory=True
)

@csrf_exempt
def transcribe(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No media file provided'}, status=400)

    try:
        media_file = request.FILES['file']
        temp_path = Path(settings.MEDIA_ROOT) / 'temp' / media_file.name
        temp_path.parent.mkdir(exist_ok=True)

        with open(temp_path, 'wb+') as destination:
            for chunk in media_file.chunks():
                destination.write(chunk)

        result = model.transcribe(str(temp_path))
        transcription = result['text']
        os.remove(temp_path)

        return JsonResponse({'transcription': transcription, 'status': 'success'})

    except Exception as e:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)

        return JsonResponse({'error': f'Transcription failed: {str(e)}', 'status': 'error'}, status=500)
