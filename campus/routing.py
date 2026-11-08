import requests
from django.core.cache import cache
from django.http import JsonResponse

from .models import Building

# FOSSGIS-hosted OSRM with a real *walking* profile.
# (The generic router.project-osrm.org demo ignores the profile and always returns car routes.)
OSRM_FOOT_URL = 'https://routing.openstreetmap.de/routed-foot/route/v1/foot/'

# The OSRM / OSM usage policies ask for a User-Agent that identifies your app.
USER_AGENT = 'CampusConnect/1.0 (school project; Palawan State University)'

CACHE_SECONDS = 60 * 60 * 24   # same two buildings -> reuse the answer for a day


def campus_route(request):
    """GET /api/route/?from=<building_id>&to=<building_id> -> walking route between two buildings."""
    try:
        start = Building.objects.get(pk=request.GET.get('from'))
        end = Building.objects.get(pk=request.GET.get('to'))
    except (Building.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'error': 'Please choose two valid buildings.'}, status=400)

    if start.pk == end.pk:
        return JsonResponse({'error': 'Please choose two different buildings.'}, status=400)

    # OSRM wants longitude,latitude order
    coords = (
        f'{format(start.longitude, ".6f")},{format(start.latitude, ".6f")};'
        f'{format(end.longitude, ".6f")},{format(end.latitude, ".6f")}'
    )

    cache_key = 'route:' + coords
    result = cache.get(cache_key)

    if result is None:
        try:
            res = requests.get(
                OSRM_FOOT_URL + coords,
                params={'overview': 'full', 'geometries': 'geojson'},
                headers={'User-Agent': USER_AGENT},
                timeout=8,
            )
            res.raise_for_status()
            data = res.json()
        except (requests.RequestException, ValueError):
            return JsonResponse({'error': 'Routing service unavailable. Try again later.'}, status=502)

        if data.get('code') != 'Ok' or not data.get('routes'):
            return JsonResponse({'error': 'No walking route found between these buildings.'}, status=404)

        route = data['routes'][0]
        result = {
            'from': start.name,
            'to': end.name,
            'distance': round(route['distance']),   # meters
            'duration': round(route['duration']),   # seconds
            'geometry': route['geometry'],          # GeoJSON LineString
        }
        cache.set(cache_key, result, CACHE_SECONDS)

    return JsonResponse(result)