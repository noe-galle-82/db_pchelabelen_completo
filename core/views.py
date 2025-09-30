from django.shortcuts import render
from django.http import HttpResponse # <-- ¡NECESITAS ESTA IMPORTACIÓN!

# En core/views.py

def me(request):
    """
    Vista simple que devuelve un mensaje de texto.
    """
    # Lógica de tu vista (ej. obtener datos del usuario, etc.)
    # ...
    
    # Devuelve una respuesta HTTP simple
    return HttpResponse("Hola, esta es la vista 'me'") 
    
# Si quisieras renderizar un template (la forma más común):
# return render(request, 'core/perfil.html', {'contexto': 'valor'})