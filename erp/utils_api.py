"""Utils for ERP views_api"""
from rest_framework import status
from rest_framework.response import Response


def handle_multiple_instances(self, request):
    """
    Handle multiple instances in one request.
    Returns:
    - Response: status 201, headers, and serializer data. 
    """
    # Create serializer for multiple instances
    serializer = self.get_serializer(data=request.data, many=True)
    # Check if they're valid
    serializer.is_valid(raise_exception=True)
    # Save instances
    self.perform_create(serializer)
    # Add headers 
    headers = self.get_success_headers(serializer.data)
    return Response(serializer.data, status=status.HTTP_201_CREATED,
        headers=headers)
 
def return_conflict_status(message):
    """
    When a RestrictedError is raised, return conflic_status.
    Parameters:
    - error: Restricted Error object.
    Returns:
    - response: Status 409 and error message.
    """
    return Response({
        "detail": str(message),
        "code": "restricted_error"
    }, status=status.HTTP_409_CONFLICT)

class SerializerMixin:
    def get_serializer(self, *args, **kwargs):
        # Add 'fields' to serializer init if picked SIDynamicSerilizer.
        fields = self.request.query_params.get("fields", None)
        if fields:
            kwargs['fields'] = fields.split(",")
        
        # Return an instance of the selected serializer class
        return self.get_serializer_class()(*args, **kwargs)

    def get_serializer_class(self):
        # Este método debe ser sobrescrito en la clase que lo hereda
        raise NotImplementedError("You must define get_serializer_class in the subclass.")
    