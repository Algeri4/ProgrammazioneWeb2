from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Telefonata, Contrattotelefonico, Simattiva, Simdisattiva, Simnonattiva
from django.db import connection
from django.contrib import messages
from datetime import datetime
from django.http import JsonResponse
from datetime import date

def modifica_telefonata(request, id):
    telefonata = get_object_or_404(Telefonata.objects.select_related('effettuatada'), id=id)
    contratto = telefonata.effettuatada
    
    if request.method == 'POST':
        nuova_data = request.POST.get('data')
        nuova_ora = request.POST.get('ora')
        nuova_durata = request.POST.get('durata')
        nuovo_costo = request.POST.get('costo', 0)
        
        # Controllo: data non vuota
        if not nuova_data:
            messages.error(request, 'La data è obbligatoria.')
            return render(request, 'telefoni/modifica_telefonata.html', {'telefonata': telefonata})
        
        # 1. Data non nel futuro
        if nuova_data > str(date.today()):
            messages.error(request, 'La data della telefonata non può essere nel futuro.')
            return render(request, 'telefoni/modifica_telefonata.html', {'telefonata': telefonata})
        
        # 2. Data non antecedente all'attivazione del contratto
        if nuova_data < str(contratto.dataattivazione):
            messages.error(request, f'La data non può essere antecedente all\'attivazione del contratto ({contratto.dataattivazione}).')
            return render(request, 'telefoni/modifica_telefonata.html', {'telefonata': telefonata})
        
        # (Opzionale) Controllo SIM attiva/disattivata - se vuoi aggiungerlo, prendi spunto da insert_call.php
        
        # Aggiornamento campi
        telefonata.data = nuova_data
        telefonata.ora = nuova_ora
        telefonata.durata = nuova_durata
        if contratto.tipo == 'ricarica':
            telefonata.costo = float(nuovo_costo) if nuovo_costo else 0
        else:
            telefonata.costo = 0
        
        telefonata.save()
        
        messages.success(request, 'Telefonata modificata con successo.')
        return redirect('/telefonate/cerca/')
    
    context = {'telefonata': telefonata}
    return render(request, 'telefoni/modifica_telefonata.html', context)

def elimina_telefonata(request, id):
    telefonata = get_object_or_404(Telefonata, id=id)

    if request.method == 'POST':
        # Salva il numero per il redirect
        numero = telefonata.effettuatada
        telefonata.delete()
        return redirect('/telefonate/cerca/')

    context = {
        'telefonata': telefonata,
    }
    return render(request, 'telefoni/elimina_telefonata.html', context)


def cerca_telefonate(request):
    risultati = Telefonata.objects.select_related('effettuatada').all().order_by('-data', '-ora')

    query = request.GET.get('q', '')
    data_from = request.GET.get('data_from', '')
    data_to = request.GET.get('data_to', '')

    if query:
        risultati = risultati.filter(
            Q(effettuatada__numero__icontains=query) |
            Q(effettuatada__nominativo__icontains=query)
        )

    if data_from:
        risultati = risultati.filter(data__gte=data_from)
    if data_to:
        risultati = risultati.filter(data__lte=data_to)

    context = {
        'risultati': risultati,
        'query': query,
        'data_from': data_from,
        'data_to': data_to,
    }
    return render(request, 'telefoni/cerca_telefonate.html', context)


def inserisci_telefonata(request):
    if request.method == 'POST':
        numero = request.POST.get('numero')
        data = request.POST.get('data')
        ora = request.POST.get('ora')
        durata = request.POST.get('durata')
        costo = request.POST.get('costo', 0)

        try:
            contratto = Contrattotelefonico.objects.get(numero=numero)
        except Contrattotelefonico.DoesNotExist:
            messages.error(request, f'Il numero {numero} non esiste')
            return render(request, 'telefoni/inserisci_telefonata.html')

        nuova_telefonata = Telefonata(
            effettuatada=contratto,  # Ora passiamo l'oggetto, non la stringa!
            data=data,
            ora=ora,
            durata=durata,
            costo=costo if contratto.tipo == 'ricarica' else 0
        )
        nuova_telefonata.save()

        messages.success(request, f'Telefonata inserita con successo per {contratto.nominativo} ({numero})')
        return redirect('/telefonate/cerca/')

    return render(request, 'telefoni/inserisci_telefonata.html')

def cerca_contratti(request):
    query = request.GET.get('q', '')
    risultati = []

    if query:
        # Cerca per numero o nominativo
        from django.db.models import Q
        risultati = Contrattotelefonico.objects.filter(
            Q(numero__icontains=query) |
            Q(nominativo__icontains=query)
        ).order_by('nominativo')

    context = {
        'risultati': risultati,
        'query': query,
    }
    return render(request, 'telefoni/cerca_contratti.html', context)


def cerca_sim(request):
    query = request.GET.get('q', '')
    risultati = []

    if query:
        from django.db.models import Q

        # Cerca SIM attive
        sim_attive = Simattiva.objects.filter(
            Q(codice__icontains=query) |
            Q(associataa__icontains=query)
        )

        # Cerca SIM disattivate
        sim_disattive = Simdisattiva.objects.filter(
            Q(codice__icontains=query) |
            Q(eraassociataa__icontains=query)
        )

        # Cerca SIM non attive
        sim_nonattive = Simnonattiva.objects.filter(
            codice__icontains=query
        )

        # Unisci i risultati
        for s in sim_attive:
            risultati.append({
                'codice': s.codice,
                'tipo': s.tiposim,
                'stato': 'Attiva',
                'telefono': s.associataa,
                'data_attivazione': s.dataattivazione,
                'data_disattivazione': None,
            })

        for s in sim_disattive:
            risultati.append({
                'codice': s.codice,
                'tipo': s.tiposim,
                'stato': 'Disattivata',
                'telefono': s.eraassociataa,
                'data_attivazione': s.dataattivazione,
                'data_disattivazione': s.datadisattivazione,
            })

        for s in sim_nonattive:
            risultati.append({
                'codice': s.codice,
                'tipo': s.tiposim,
                'stato': 'Non Attiva',
                'telefono': None,
                'data_attivazione': None,
                'data_disattivazione': None,
            })

    context = {
        'risultati': risultati,
        'query': query,
    }
    return render(request, 'telefoni/cerca_sim.html', context)


def autocomplete(request):
    term = request.GET.get('term', '')
    tipo = request.GET.get('tipo', 'telefonate')

    if len(term) < 1:
        return JsonResponse([], safe=False)

    risultati = []

    if tipo == 'telefonate' or tipo == 'contratti':
        # Cerca per numero o nominativo
        contratti = Contrattotelefonico.objects.filter(
            Q(numero__icontains=term) | Q(nominativo__icontains=term)
        )[:10]

        for c in contratti:
            risultati.append({
                'value': c.numero,
                'label': f"{c.numero} — {c.nominativo or 'Sconosciuto'}"
            })

    elif tipo == 'sim':
        # Cerca SIM per codice o telefono associato
        attive = Simattiva.objects.filter(
            Q(codice__icontains=term) | Q(associataa__icontains=term)
        )[:5]
        for s in attive:
            risultati.append({
                'value': s.codice,
                'label': f"{s.codice} — {s.associataa or 'non associata'} (Attiva)"
            })

        disattive = Simdisattiva.objects.filter(
            Q(codice__icontains=term) | Q(eraassociataa__icontains=term)
        )[:5]
        for s in disattive:
            risultati.append({
                'value': s.codice,
                'label': f"{s.codice} — {s.eraassociataa or 'non associata'} (Disattivata)"
            })

        nonattive = Simnonattiva.objects.filter(codice__icontains=term)[:5]
        for s in nonattive:
            risultati.append({
                'value': s.codice,
                'label': f"{s.codice} — Non Attiva"
            })

    elif tipo == 'insert':
        # Per inserimento telefonata: restituisce il numero
        contratti = Contrattotelefonico.objects.filter(
            Q(numero__icontains=term) | Q(nominativo__icontains=term)
        )[:10]

        for c in contratti:
            risultati.append({
                'value': c.numero,
                'label': f"{c.numero} — {c.nominativo or 'Sconosciuto'}"
            })

    return JsonResponse(risultati, safe=False)