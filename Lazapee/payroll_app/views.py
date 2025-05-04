from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee, Payslip, Account

# Account management methods
def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            account = Account.objects.get(username=username)
            if account.check_password(password):
                request.session['account_id'] = account.pk  # request session instead of global id
                return redirect('homepage')
            else:
                return render(request, 'payroll_app/login.html', {'error': 'Invalid password'})
        except Account.DoesNotExist:
            return render(request, 'payroll_app/login.html', {'error': 'Account does not exist'})
    else:
        return render(request, 'payroll_app/login.html')
    
def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if Account.objects.filter(username=username).exists():
            return render(request, 'payroll_app/signup.html', {'error': 'Account already exists'})
        else:
            Account.objects.create(username=username, password=password)
            return redirect('login')
    else:
        return render(request, 'payroll_app/signup.html')
    
def manage_account(request, pk):
    session_id = request.session.get('account_id')
    if session_id != int(pk):
        return redirect('login')

    account = get_object_or_404(Account, pk=pk)

    if request.method == "POST" and request.POST.get("delete_account") == "true":
        account.delete()
        request.session.flush()  # properly log out
        return redirect("login")

    return render(request, 'payroll_app/manage_account.html', {'account': account})

def change_password(request, pk):
    session_id = request.session.get('account_id')
    if session_id != int(pk):
        return redirect('login')

    try:
        account = Account.objects.get(pk=pk)
    except Account.DoesNotExist:
        return redirect('login')

    if request.method == "POST":
        current_password = request.POST.get('password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

    # FIX PART WHERE WHEN OPENED IT SAYS CURRENT PASSWORD IS INCORRECT KAAGAD
    
        if current_password != account.password:
            return render(request, 'payroll_app/change_password.html', {'error': 'Current password is incorrect', 'account': account})

        if current_password == new_password:
            return render(request, 'payroll_app/change_password.html', {'error': 'Please change current password', 'account': account})

        if new_password != confirm_password:
            return render(request, 'payroll_app/change_password.html', {'error': 'New passwords do not match', 'account': account})

        account.set_password(new_password)
        return render(request, 'payroll_app/manage_account.html', {'success': 'Password changed successfully', 'account': account})
    else:
        return render(request, 'payroll_app/change_password.html', {'account': account})

def logout(request):
    request.session.flush()  # logout
    return redirect('login')

# misc
def homepage(request):
    account_id = request.session.get('account_id')

    if account_id:
        try:
            account = get_object_or_404(Account, pk=account_id)
            employee = Employee.objects.all()
            return render(request, 'payroll_app/homepage.html', 
                          {'employee': employee, 'account': account})
        except Account.DoesNotExist:
            return redirect('login')
    else:
        return redirect('login')
    
def new_employee(request):
    account_id = request.session.get('account_id')

    if account_id:
        if request.method == "POST":
            name = request.POST.get("name")
            id_number = request.POST.get("id_number")
            rate = request.POST.get("rate")
            allowance = request.POST.get("allowance")

            # Check if all required fields are entered
            if not all([name, id_number, rate]):
                return render(request, 'payroll_app/new_employee.html', {'error': 'Enter required fields'})

            # Validate number fields
            try:
                id_number = int(id_number)
                rate = float(rate)
                allowance = float(allowance) if allowance else 0

            except ValueError:
                return render(request, 'payroll_app/new_employee.html', {'error': 'Invalid input'})
            
            # 6 digit id number
            if len(str(id_number)) != 6:
                    return render(request, 'payroll_app/new_employee.html', {'error': 'ID must be 6 digits'})
            
            # Name cannot contain numbers
            if any(char.isdigit() for char in name):
                return render(request, 'payroll_app/new_employee.html', {'error': 'Name cannot contain numbers'})
            
            # rate cannot be negative or 0
            if rate <= 0:
                return render(request, 'payroll_app/new_employee.html', {'error': 'Insert valid rate'})
            
            # Allowance cannot be negative
            if allowance < 0:
                return render(request, 'payroll_app/new_employee.html', {'error': 'Insert valid allowance'})

            # Avoiding duplicate id numbers
            if Employee.objects.filter(id_number=id_number).exists():
                return render(request, 'payroll_app/new_employee.html', {'error': f'ID {id_number} already exists'})

            # Create employee
            Employee.objects.create(
                name=name,
                id_number=id_number,
                rate=rate,
                allowance=allowance
            )
            # Redirect after successful creation
            return render(request, 'payroll_app/new_employee.html', {'success' : 'Employee added successfully'})
        return render(request, 'payroll_app/new_employee.html')
    else:
        return redirect('login')
    
def delete_employee(request, pk):
    account_id = request.session.get('account_id')
    if account_id:
        employee = get_object_or_404(Employee, id_number=pk)
        employee.delete()
        return redirect('homepage')
    
    else:
        return redirect('login')

def update_employee(request, pk):
    account_id = request.session.get('account_id')
    if account_id:
        employee = get_object_or_404(Employee, id_number=pk)

        if request.method == "POST":
            name = request.POST.get("name")
            id_number = request.POST.get("id_number")
            rate = request.POST.get("rate")
            allowance = request.POST.get("allowance")

            # Check if all required fields are entered
            if not all([name, id_number, rate]):
                return render(request, 'payroll_app/update_employee.html', {'error': 'Enter required fields', 'employee': employee})

            # Validate number fields
            try:
                id_number = int(id_number)
                rate = float(rate)
                allowance = float(allowance) if allowance else 0

            except ValueError:
                return render(request, 'payroll_app/update_employee.html', {'error': 'Invalid input', 'employee': employee})
            
            # 6 digit id number
            if len(str(id_number)) != 6:
                    return render(request, 'payroll_app/update_employee.html', {'error': 'ID must be 6 digits', 'employee': employee})
            
            # Name cannot contain numbers
            if any(char.isdigit() for char in name):
                return render(request, 'payroll_app/update_employee.html', {'error': 'Name cannot contain numbers', 'employee': employee})
            
            # rate cannot be negative or 0
            if rate <= 0:
                return render(request, 'payroll_app/update_employee.html', {'error': 'Insert valid rate', 'employee': employee})
            
            # Allowance cannot be negative
            if allowance < 0:
                return render(request, 'payroll_app/update_employee.html', {'error': 'Insert valid allowance', 'employee': employee})

            # Avoiding duplicate id numbers
            if Employee.objects.filter(id_number=id_number).exclude(pk=pk).exists():
                return render(request, 'payroll_app/update_employee.html', {'error': f'ID {id_number} already exists', 'employee': employee})

            # Update employee
            employee.name = name
            employee.id_number = id_number
            employee.rate = rate
            employee.allowance = allowance
            employee.save()

            # Redirect after successful update
            return redirect('homepage')
        
        return render(request, 'payroll_app/update_employee.html', {'employee': employee})
    else:
        return redirect('login')
    
def ot_update(request, pk):
    account_id = request.session.get('account_id')
    if account_id:
        account = get_object_or_404(Account, pk=account_id)
        employee = get_object_or_404(Employee, id_number=pk)

        if request.method == "POST":
            ot_hours = float(request.POST.get("ot_hours"))
            employee.overtime_pay += (employee.rate / 160) * 1.5 * ot_hours
            employee.save()
            return redirect('homepage')
        else:
            employee_list = Employee.objects.all()
            return render(request, 'payroll_app/homepage.html', {
                'employee': employee_list,
                'account': account
            })
    else:
        return redirect('login')