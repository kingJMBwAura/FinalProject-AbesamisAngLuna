from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee, Payslip, Account

id = 0

# Account management methods
def login(request):
    global id
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            account = Account.objects.get(username=username)
            if account.getPassword() == password:
                # sets id to the pk of the account in use
                id = account.pk
                return redirect('view_supplier')
            else:
                return render(request, 'payroll_app/login.html', {'error': 'Invalid login'})
        except Account.DoesNotExist:
            return render(request, 'payroll_app/login.html', {'error': 'Invalid login'})
        
    else:
        return render(request, 'payroll_app/login.html')
    
def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if Account.objects.filter(username=username).exists():
            return render(request, 'payroll_app/signup.html', {'error': 'Account already exists'})
        
        else:
            account = Account.objects.create(username=username, password=password)
            account.save()
            return render(request, 'payroll_app/login.html', {'success': 'Account created successfully', 'account':account,'id':id})
        
    else:
        return render(request, 'payroll_app/signup.html')
    
def manage_account(request, pk):
    try:
        account = Account.objects.get(pk=pk)
    # send user back if account does not exist
    except Account.DoesNotExist:
        return redirect('login')
    
    if request.method == "POST" and request.POST.get("delete_account") == "true":
        account.delete()
        return redirect("login")
    
    else:
        return render(request, 'payroll_app/manage_account.html', {'account': account})

def change_password(request, pk):
    try:
        account = Account.objects.get(pk=pk)
    # send user back if account does not exist
    except Account.DoesNotExist:
        return redirect('login')
    if request.method == "POST":
        current_password = request.POST.get('password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if current_password is None:
            return render(request, 'payroll_app/change_password.html', {'account': account})
        
        if current_password != account.password:
            return render(request, 'payroll_app/change_password.html', {'error': 'Current password is incorrect', 'account': account})
        
        if current_password == new_password:
            return render(request, 'payroll_appp/change_password.html', {'error': 'Please change current password', 'account': account})
        
        if new_password != confirm_password:
            return render(request, 'payroll_app/change_password.html', {'error': 'New passwords do not match', 'account': account})
        
        account.password = new_password
        account.save()

        return render(request, 'payroll_app/manage_account.html', {'success': 'Password changed successfully', 'account': account})
    else:
        return render(request, 'payroll_app/change_password.html', {'account': account})

# misc

def homepage(request):
    global id  # call account pk
    employee = Employee.objects.all()

    if id != 0:  # long as account pk = nonzero
        account = get_object_or_404(Account, pk=id)
        return render(request, 'payroll_app/homepage.html', {'employee': employee, 'account': account, 'id': id})
    else:
        return render(request, 'payroll_app/homepage.html', {'employee': employee, 'id': id})