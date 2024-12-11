# copy of views.py
import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def cheese_recommendations(request):
    """
    API endpoint to get cheese recommendations from the JavaScript backend.
    Accepts user preferences as JSON input.
    """

    if request.method == "POST":
        try:
            # Parsing user preferences
            preferences = json.loads(request.body)

            # Call the Node.js script with user preferences
            result = subprocess.run(
                ['node', 'CheeseAI.js', json.dumps(preferences)],  # Node.js command with preferences
                capture_output=True,
                text=True,
                check=True,
            )

            # Parsing the JSON output
            recommendations = json.loads(result.stdout)

            # Recommendations as a JSON response
            return JsonResponse({'recommendations': recommendations}, status=200)

        except subprocess.CalledProcessError as e:
            # Handles script errors
            return JsonResponse({'error': e.stderr}, status=500)
        except json.JSONDecodeError:
            # Handles invalid JSON in request or in response
            return JsonResponse({'error': 'Invalid JSON input or output.'}, status=400)

    # Returning an error for non-POST requests
    return JsonResponse({'error': 'Invalid request method. Use POST.'}, status=405)
