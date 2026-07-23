from django.utils.deprecation import MiddlewareMixin
from .utils import log_action

class AuditLogMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # We only log modifications (POST, PUT, DELETE) by authenticated users on administrative or custom manager routes
        if hasattr(request, 'user') and request.user and request.user.is_authenticated:
            if request.method in ['POST', 'PUT', 'DELETE']:
                path = request.path
                
                # Exclude native django admin logs (which has its own log entry) to avoid duplication
                # Custom paths like accounts, certificates, core, audit_logs will be logged here
                is_custom_admin_path = any(x in path for x in ['/certificates/', '/accounts/', '/departments/', '/courses/', '/students/'])
                
                if is_custom_admin_path:
                    # Ignore double logs for standard auth views if any
                    if 'login' in path or 'logout' in path:
                        return response
                        
                    description = f"User performed {request.method} request on path {path}."
                    
                    # Capture request POST parameters key list (masking values for security)
                    if request.POST:
                        keys = list(request.POST.keys())
                        if 'csrfmiddlewaretoken' in keys:
                            keys.remove('csrfmiddlewaretoken')
                        if 'password' in keys:
                            keys = [k for k in keys if 'password' not in k]  # Security filter
                        if keys:
                            description += f" Post Parameters: {', '.join(keys)}"
                            
                    log_action(
                        user=request.user,
                        action=f"AUDIT_{request.method}",
                        description=description,
                        request=request
                    )
        return response
