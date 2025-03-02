import os
from pathlib import Path
from django.http import JsonResponse
from django.conf import settings
import whisper
from django.views.decorators.csrf import csrf_exempt

model = whisper.load_model(
    name=settings.WHISPER_MODELS['tiny.en'],  # BASE_DIR / 'models/tiny.en.pt',
    in_memory=True
)

def file_size(val, unit):
    if unit == 'KB':
        return val * 1024
    elif unit == 'MB':
        return val * 1024 * 1024
    elif unit == 'GB':
        return val * 1024 * 1024 * 1024
    return val


@csrf_exempt
def transcribe(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No media file provided'}, status=400)
    if request.FILES['file'].size > file_size(50, 'MB'):
        return JsonResponse({'error': 'File size limit exceeded'}, status=400)

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
