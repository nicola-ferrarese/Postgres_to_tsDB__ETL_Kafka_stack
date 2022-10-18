import time
from datetime import datetime, timezone

from envsensor.models import env_measure, env_measure_30min, EnvSerializer
import psycopg2
from django.http import JsonResponse
from rest_framework import status, viewsets
from rest_framework.response import Response

class API_ViewSet(viewsets.ViewSet):
    def GetMeasures(self,request,device, pk=None):
        for x in request.query_params:
            print(x + " : " + str(request.query_params[x]))
        Date_start  = datetime.strptime(request.query_params['startInterval'], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc)
        Date_finish = datetime.strptime(request.query_params['endInterval'], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc)

        result = env_measure_30min.objects.filter(time__gte=Date_start,
                                                  time__lte=Date_finish)
        return JsonResponse(EnvSerializer(result, many=True).data, safe=False)

        #return Response(status=status.HTTP_400_BAD_REQUEST)