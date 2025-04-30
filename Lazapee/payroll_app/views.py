from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee, Payslip, Account

id = 0

# Account management methods
def login(request):
    global id
    id = 0  # reset on every login attempt
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            account = Account.objects.get(username=username)
            if account.check_password(password):
                id = account.pk
                return redirect('homepage')
            else:
                return render(request, 'payroll_app/login.html', {'error': 'Invalid password'})
        except Account.DoesNotExist:
            return render(request, 'payroll_app/login.html', {'error': 'Account does not exist'})
    else:
        return render(request, 'payroll_app/login.html')
    
def signup(request):
    global id
    id = 0
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if Account.objects.filter(username=username).exists():
            return render(request, 'payroll_app/signup.html', {'error': 'Account already exists'})
        else:
            Account.objects.create(username=username, password=password)
            return render(request, 'payroll_app/login.html', {'success': 'Account created successfully'})
    else:
        return render(request, 'payroll_app/signup.html')
    
def manage_account(request, pk):
    global id
    if int(pk) != id:
        return redirect('login')  # Force logout if pk doesn't match current session
    
    account = get_object_or_404(Account, pk=pk)

    if request.method == "POST" and request.POST.get("delete_account") == "true":
        account.delete()
        id = 0
        return redirect("login")
    
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
        
        account.set_password(new_password)

        return render(request, 'payroll_app/manage_account.html', {'success': 'Password changed successfully', 'account': account})
    else:
        return render(request, 'payroll_app/change_password.html', {'account': account})

# misc

def homepage(request):
    global id  # call account pk
    employee = Employee.objects.all()

    if id != 0:  # long as account pk = nonzero
        try:
            account = get_object_or_404(Account, pk=id)
            return render(request, 'payroll_app/homepage.html', 
                          {'employee': employee, 'account': account, 'id': id})
        except:
            return redirect('login')
    else:
        return redirect('login')