from django.shortcuts import render, redirect
from django.conf import settings
from django.core.paginator import Paginator
from django.contrib import messages
from .forms import MemberForm, WalletForm, TransactionForm
from .api_request import get_api, post_api, put_api, delete_api
from decimal import Decimal
import requests

BASE_URL = settings.BASE_URL

def home(request):
    return render(request, 'home.html')



def member_list(request):
    query = request.GET.get('q', '').strip()
    page_number = request.GET.get('page', 1)

    
    endpoint = "api/members/"
    api_response = get_api(BASE_URL, endpoint)

    if api_response.status_code == 200:
        members = api_response.json()
    else:
        members = []

    
    if query:
        query_lower = query.lower()
        members = [
            m for m in members
            if query_lower in m.get('full_name', '').lower()
            or query_lower in m.get('phone_number', '').lower()
            or query_lower in m.get('email', '').lower()
        ]

    
    paginator = Paginator(members, 5)
    records = paginator.get_page(page_number)

    
    return render(request, 'wallet_system_fe/member_list.html', {
        'records': records,
        'query': query,
    })


def member_create(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            data = {
                'member_id': form.cleaned_data['member_id'],
                'full_name': form.cleaned_data['full_name'],
                'phone_number': form.cleaned_data['phone_number'],
                'email': form.cleaned_data['email']
            }

           
            response = requests.post(f"{BASE_URL}/api/members/", json=data)

            if response.status_code in [200, 201]:
                return redirect('member_list')
            else:
                
                form.add_error(None, f"API Error: {response.text}")

    else:
       
        form = MemberForm(is_update=False)

    return render(request, 'wallet_system_fe/member_form.html', {'form': form})


def member_update(request, member_id):
    
    
    endpoint = f"api/members/{member_id}/"

    data = {}
    try:
        api_response = requests.get(f"{BASE_URL}{endpoint}")
        if api_response.status_code == 200:
            data = api_response.json()
        else:
            print(f"[DEBUG] Failed to fetch member data. Status: {api_response.status_code}")
    except requests.ConnectionError:
        print("[ERROR] Could not connect to API server while fetching member data.")

    if request.method == "POST":
        payload = {
            "full_name": request.POST.get("full_name"),
            "email": request.POST.get("email"),
            "phone_number": request.POST.get("phone_number"),
        }

        try:
            response = requests.put(f"{BASE_URL}{endpoint}", json=payload)
        except requests.ConnectionError:
            return render(
                request,
                "wallet_system_fe/member_form.html",
                {
                    "member": payload,
                    "error": "Connection error: Could not reach the API server.",
                },
            )

        if response.status_code in [200, 204]:
            return redirect("member_list")

        return render(
            request,
            "wallet_system_fe/member_form.html",
            {
                "member": payload,
                "error": f"Update failed: {response.text}",
            },
        )

    return render(
        request,
        "wallet_system_fe/member_form.html",
        {"member": data}
    )

def member_delete(request, member_id):
    endpoint = f"api/members/{member_id}/"  
    response = delete_api(BASE_URL, endpoint)

    if response.status_code in [200, 204]:
        messages.success(request, "Member deleted successfully!")
    else:
        messages.error(request, f"Failed to delete member (Status: {response.status_code})")

    return redirect('member_list')


def wallet_list(request):
    endpoint = "api/wallets/"
    api_response = get_api(BASE_URL, endpoint)
    wallets = api_response.json() if api_response.status_code == 200 else []

    search_query = request.GET.get('search', '').strip().lower()

    if search_query:
        wallets = [
            w for w in wallets
            if search_query in str(w.get('member_name', '')).lower()
            or search_query in str(w.get('member_id', '')).lower()
        ]

    paginator = Paginator(wallets, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'wallet_system_fe/wallet_list.html', {
        'records': page_obj,
        'search_query': search_query,
    })

def wallet_create(request):
    endpoint = "api/members/"
    api_response = get_api(BASE_URL, endpoint)
    members = api_response.json() if api_response.status_code == 200 else []

    if request.method == "POST":
        member_id = request.POST.get("member_id")
        initial_balance = request.POST.get("initial_balance", 0)

        try:
            initial_balance = float(initial_balance)
        except (ValueError, TypeError):
            initial_balance = 0.0

        data = {"member": member_id, "balance": initial_balance}

        print("Payload sent:", data)
        print("API URL:", f"{BASE_URL}api/wallets/")

        create_response = post_api(BASE_URL, "api/wallets/", data)

        if create_response.status_code in [200, 201]:
            messages.success(request, "Wallet created successfully!")
            return redirect("wallet_list")
        else:
            messages.error(request, f" Failed to create wallet: {create_response.text}")

    return render(request, "wallet_system_fe/wallet_create.html", {"members": members})

def wallet_deposit(request, member_id):
    if request.method == "POST":
        amount = request.POST.get('amount')
        description = request.POST.get('description', '')
        data = {'member_id': member_id, 'amount': amount, 'transaction_type': 'DEPOSIT', 'description': description}
        api_response = post_api(BASE_URL, "api/transactions/", data)
        if api_response.status_code in [200, 201]:
            return redirect('wallet_list')
        else:
            messages.error(request, f"Failed to deposit: {api_response.status_code}")
    return render(request, 'wallet_system_fe/wallet_deposit.html', {'member_id': member_id})


def wallet_withdraw(request, member_id):
    if request.method == "POST":
        amount = request.POST.get('amount')
        description = request.POST.get('description', '')
        data = {'member_id': member_id, 'amount': amount, 'transaction_type': 'WITHDRAW', 'description': description}
        api_response = post_api(BASE_URL, "api/transactions/", data)
        if api_response.status_code in [200, 201]:
            return redirect('wallet_list')
        else:
            messages.error(request, f"Failed to withdraw: {api_response.status_code}")
    return render(request, 'wallet_system_fe/wallet_withdraw.html', {'member_id': member_id})

def transaction_list(request):
    query = request.GET.get('q', '').strip().lower()
    page_number = request.GET.get('page', 1)

    endpoint = "api/transactions/"
    api_response = get_api(BASE_URL, endpoint)
    transactions = api_response.json() if api_response.status_code == 200 else []

    for t in transactions:
        t['sender'] = (
            t.get('member_one', {}).get('full_name')
            if isinstance(t.get('member_one'), dict)
            else t.get('member_one_name', '')
        )
        t['receiver'] = (
            t.get('member_two', {}).get('full_name')
            if isinstance(t.get('member_two'), dict)
            else t.get('member_two_name', '')
        )

    
    if query:
        transactions = [
            t for t in transactions
            if query in str(t.get('sender', '')).lower()
            or query in str(t.get('receiver', '')).lower()
            or query in str(t.get('transaction_type', '')).lower()
            or query in str(t.get('amount', '')).lower()
        ]

    
    paginator = Paginator(transactions, 5)
    records = paginator.get_page(page_number)

    
    return render(request, 'wallet_system_fe/transaction_list.html', {
        'records': records,
        'query': query,
    })



def transaction_create(request):
    endpoint = "api/members/"
    api_response = get_api(BASE_URL, endpoint)
    members = api_response.json() if api_response.status_code == 200 else []

    if request.method == "POST":
        member_one_id = request.POST.get("member_one")  
        member_two_id = request.POST.get("member_two")  
        amount = request.POST.get("amount", 0)
        description = request.POST.get("description", "")
        
        transaction_type = "transfer"

        data = {
            "member_one": member_one_id,
            "member_two": member_two_id or None,
            "amount": amount,
            "transaction_type": transaction_type,
            "description": description,
        }

        api_response = post_api(BASE_URL, "api/transactions/", data)
        if api_response.status_code == 201:
            return redirect("transaction_list")

    return render(request, "wallet_system_fe/transaction_form.html", {"members": members})