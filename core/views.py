from django.shortcuts import render, redirect
from core.models import Evento
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http.response import Http404, JsonResponse
from datetime import datetime, timedelta
from django.contrib.auth.models import User

def handler404(request, exception):
    return render(request, '404.html')

def login_user(request):
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('/')

def submit_login(request):
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        usuario = authenticate(username=username, password=password)
        if usuario is not None:
            login(request, usuario)
            return redirect('/')
        else:
            messages.error(request, "Usuario ou Senha Inválidos")
    return redirect('/')

@login_required(login_url='/login/')
def lista_eventos(request):
    usuario = request.user
    data_atual = datetime.now() -timedelta(hours=1)
    evento = Evento.objects.filter(usuario = usuario, data_evento__gt = data_atual)
    dados = {'eventos':evento}
    return render(request, 'agenda.html', dados)

@login_required(login_url='/login/')
def lista_eventos_historico(request):
    usuario = request.user
    data_atual = datetime.now()
    evento = Evento.objects.filter(usuario=usuario, data_evento__lt=data_atual)
    dados = {'eventos':evento}
    return render(request, 'historico.html', dados)

@login_required(login_url='/login/')
def evento(request):
    id_evento = request.GET.get('id')
    dados = {}
    if id_evento:
        try:
            dados['evento'] = Evento.objects.get(id=id_evento)
        except Exception:
            raise Http404()
    return render(request, 'evento.html', dados)

@login_required(login_url='/login/')
def submit_evento(request):
    if request.POST:
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao')
        data_evento = request.POST.get('data_evento')
        local = request.POST.get('local')
        usuario = request.user
        id_evento = request.POST.get('id_evento')
        if id_evento and Evento.objects.get(id=id_evento).usuario == usuario:
            Evento.objects.filter(id=id_evento).update(titulo=titulo,
                              descricao=descricao,
                              data_evento=data_evento,
                              local=local)
        
        else:
            Evento.objects.create(titulo=titulo,
                              descricao=descricao,
                              data_evento=data_evento,
                              local=local,
                              usuario=usuario)
    return redirect('/')

@login_required(login_url='/login/')
def delete_evento(request, id_evento):
    usuario = request.user
    try:
        evento = Evento.objects.get(id=id_evento)
    except Exception:
        raise Http404()
    
    if usuario == evento.usuario:
        evento.delete()
    else:
        raise Http404()
    return redirect('/')

def json_lista_evento(request, id_usuario):
    usuario = User.objects.get(id=id_usuario)
    evento = Evento.objects.filter(usuario = usuario).values('id', 'titulo')
    return JsonResponse(list(evento), safe=False)